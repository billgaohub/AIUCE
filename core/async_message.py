"""
核心模块：异步消息总线
Async Layer Communication Message Bus
支持异步订阅和发布的消息总线实现

设计原则：
- 同步方法保持向后兼容
- 异步方法以 async_ 前缀区分
- 支持混合模式（同步订阅者 + 异步订阅者）
"""

from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional, Awaitable, Union
from datetime import datetime
from enum import Enum
import uuid
import json
import asyncio
from concurrent.futures import ThreadPoolExecutor

# 导入同步版本作为基类
try:
    from .message import Message, LayerLevel
except ImportError:
    from message import Message, LayerLevel


# 异步回调类型
AsyncCallback = Callable[[Message], Awaitable[None]]
SyncCallback = Callable[[Message], None]
AnyCallback = Union[SyncCallback, AsyncCallback]


class AsyncMessageBus:
    """
    异步消息总线 - 十一层架构的异步神经网络

    特性：
    1. 支持同步和异步订阅者混合
    2. 并发投递消息到多个层级
    3. 异步钩子机制
    4. 线程池执行同步回调
    """

    def __init__(self, max_history: int = 1000, executor_workers: int = 4):
        # 同步订阅者
        self._sync_subscribers: Dict[str, List[SyncCallback]] = {}
        # 异步订阅者
        self._async_subscribers: Dict[str, List[AsyncCallback]] = {}
        # 消息历史
        self._history: List[Message] = []
        self._max_history = max_history
        # 消息钩子
        self._sync_hooks: Dict[str, List[SyncCallback]] = {}
        self._async_hooks: Dict[str, List[AsyncCallback]] = {}
        # 统计
        self._stats = {
            "published": 0,
            "delivered": 0,
            "broadcasts": 0,
            "async_delivered": 0,
            "sync_delivered": 0,
        }
        # 线程池（用于执行同步回调）
        self._executor = ThreadPoolExecutor(max_workers=executor_workers)

    # ── 订阅管理 ────────────────────────────────────────────────

    def subscribe(self, layer: str, callback: SyncCallback):
        """订阅某层级的消息（同步版本，向后兼容）"""
        if layer not in self._sync_subscribers:
            self._sync_subscribers[layer] = []
        self._sync_subscribers[layer].append(callback)

    def async_subscribe(self, layer: str, callback: AsyncCallback):
        """订阅某层级的消息（异步版本）"""
        if layer not in self._async_subscribers:
            self._async_subscribers[layer] = []
        self._async_subscribers[layer].append(callback)

    def unsubscribe(self, layer: str, callback: AnyCallback):
        """取消订阅"""
        if layer in self._sync_subscribers and callback in self._sync_subscribers[layer]:
            self._sync_subscribers[layer].remove(callback)
        if layer in self._async_subscribers and callback in self._async_subscribers[layer]:
            self._async_subscribers[layer].remove(callback)

    def add_hook(self, msg_type: str, callback: SyncCallback):
        """添加消息钩子（同步版本）"""
        if msg_type not in self._sync_hooks:
            self._sync_hooks[msg_type] = []
        self._sync_hooks[msg_type].append(callback)

    def async_add_hook(self, msg_type: str, callback: AsyncCallback):
        """添加消息钩子（异步版本）"""
        if msg_type not in self._async_hooks:
            self._async_hooks[msg_type] = []
        self._async_hooks[msg_type].append(callback)

    # ── 消息发布 ────────────────────────────────────────────────

    def publish(self, message: Message):
        """发布消息（同步版本，向后兼容）"""
        # 运行异步版本的事件循环
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # 已有事件循环运行中，创建任务
                asyncio.create_task(self.async_publish(message))
            else:
                # 无事件循环，运行一次
                loop.run_until_complete(self.async_publish(message))
        except RuntimeError:
            # 无事件循环，创建新的
            asyncio.run(self.async_publish(message))

    async def async_publish(self, message: Message):
        """
        异步发布消息到目标层级

        并发投递策略：
        1. 异步订阅者通过 asyncio.gather 并发执行
        2. 同步订阅者通过线程池执行，避免阻塞
        """
        message.add_trace(message.source_layer)
        self._history.append(message)
        self._stats["published"] += 1

        # 裁剪历史
        if len(self._history) > self._max_history:
            self._history = self._history[-self._max_history:]

        # 执行钩子
        await self._execute_hooks(message)

        # 路由消息
        if message.target_layer:
            # 单播
            await self._deliver_to(message, message.target_layer)
        else:
            # 广播
            self._stats["broadcasts"] += 1
            await self._broadcast(message)

    async def _execute_hooks(self, message: Message):
        """执行消息钩子"""
        tasks = []

        # 异步钩子
        if message.type in self._async_hooks:
            for hook in self._async_hooks[message.type]:
                tasks.append(hook(message))

        # 同步钩子（在线程池中执行）
        if message.type in self._sync_hooks:
            for hook in self._sync_hooks[message.type]:
                tasks.append(asyncio.get_event_loop().run_in_executor(
                    self._executor, hook, message
                ))

        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)

    async def _deliver_to(self, message: Message, target: str):
        """投递消息到指定层级"""
        tasks = []

        # 异步订阅者
        if target in self._async_subscribers:
            for callback in self._async_subscribers[target]:
                tasks.append(self._safe_async_call(callback, message, target))

        # 同步订阅者
        if target in self._sync_subscribers:
            for callback in self._sync_subscribers[target]:
                tasks.append(self._safe_sync_call(callback, message, target))

        if tasks:
            results = await asyncio.gather(*tasks, return_exceptions=True)
            self._stats["delivered"] += sum(1 for r in results if r is True)

    async def _broadcast(self, message: Message):
        """广播消息到所有层级"""
        tasks = []

        for layer in set(list(self._async_subscribers.keys()) + list(self._sync_subscribers.keys())):
            if layer == message.source_layer:
                continue

            # 异步订阅者
            if layer in self._async_subscribers:
                for callback in self._async_subscribers[layer]:
                    tasks.append(self._safe_async_call(callback, message, layer))

            # 同步订阅者
            if layer in self._sync_subscribers:
                for callback in self._sync_subscribers[layer]:
                    tasks.append(self._safe_sync_call(callback, message, layer))

        if tasks:
            results = await asyncio.gather(*tasks, return_exceptions=True)
            self._stats["delivered"] += sum(1 for r in results if r is True)

    async def _safe_async_call(self, callback: AsyncCallback, message: Message, layer: str) -> bool:
        """安全调用异步回调"""
        try:
            await callback(message)
            self._stats["async_delivered"] += 1
            return True
        except Exception as e:
            print(f"  [异步消息总线] 投递失败 {layer}: {e}")
            return False

    async def _safe_sync_call(self, callback: SyncCallback, message: Message, layer: str) -> bool:
        """安全调用同步回调（在线程池中执行）"""
        try:
            await asyncio.get_event_loop().run_in_executor(
                self._executor, callback, message
            )
            self._stats["sync_delivered"] += 1
            return True
        except Exception as e:
            print(f"  [异步消息总线] 投递失败 {layer}: {e}")
            return False

    # ── 便捷方法 ────────────────────────────────────────────────

    def send(
        self,
        source: str,
        target: str,
        msg_type: str,
        payload: dict = None,
        priority: int = 0
    ) -> Message:
        """快捷发送：构造并发送消息（同步版本）"""
        msg = Message(
            source_layer=source,
            target_layer=target,
            type=msg_type,
            payload=payload or {},
            priority=priority
        )
        self.publish(msg)
        return msg

    async def async_send(
        self,
        source: str,
        target: str,
        msg_type: str,
        payload: dict = None,
        priority: int = 0
    ) -> Message:
        """快捷发送：构造并发送消息（异步版本）"""
        msg = Message(
            source_layer=source,
            target_layer=target,
            type=msg_type,
            payload=payload or {},
            priority=priority
        )
        await self.async_publish(msg)
        return msg

    def broadcast(self, source: str, msg_type: str, payload: dict = None) -> Message:
        """广播消息（同步版本）"""
        msg = Message(
            source_layer=source,
            target_layer="",
            type=msg_type,
            payload=payload or {}
        )
        self.publish(msg)
        return msg

    async def async_broadcast(self, source: str, msg_type: str, payload: dict = None) -> Message:
        """广播消息（异步版本）"""
        msg = Message(
            source_layer=source,
            target_layer="",
            type=msg_type,
            payload=payload or {}
        )
        await self.async_publish(msg)
        return msg

    # ── 查询方法 ────────────────────────────────────────────────

    def get_history(
        self,
        layer: str = None,
        msg_type: str = None,
        limit: int = 100
    ) -> List[dict]:
        """获取消息历史"""
        history = self._history[-limit:]
        result = []
        for msg in history:
            if layer and msg.source_layer != layer and msg.target_layer != layer:
                continue
            if msg_type and msg.type != msg_type:
                continue
            result.append(msg.to_dict())
        return result

    def get_trace(self, msg_id: str) -> List[str]:
        """获取消息追踪链"""
        for msg in reversed(self._history):
            if msg.id == msg_id:
                return msg.trace
        return []

    def clear_history(self):
        """清空历史"""
        self._history = []

    def stats(self) -> dict:
        """获取总线统计"""
        return {
            **self._stats,
            "sync_subscribers": {layer: len(cbs) for layer, cbs in self._sync_subscribers.items()},
            "async_subscribers": {layer: len(cbs) for layer, cbs in self._async_subscribers.items()},
            "sync_hooks": list(self._sync_hooks.keys()),
            "async_hooks": list(self._async_hooks.keys()),
            "history_size": len(self._history),
        }

    def shutdown(self):
        """关闭消息总线"""
        self._executor.shutdown(wait=True)


# ── 导出 ──────────────────────────────────────────────────────────

__all__ = [
    "AsyncMessageBus",
    "Message",
    "LayerLevel",
    "AsyncCallback",
    "SyncCallback",
    "AnyCallback",
]

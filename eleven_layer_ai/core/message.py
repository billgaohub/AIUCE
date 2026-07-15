"""
核心模块：消息总线
Layer Communication Message Bus
十一层架构的神经网络
"""

from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional
from datetime import datetime
from enum import Enum
import uuid
import json


class LayerLevel(str, Enum):
    """十一层层级枚举"""
    L0 = "L0"    # 意志层
    L1 = "L1"    # 身份层
    L2 = "L2"    # 感知层
    L3 = "L3"    # 推理层
    L4 = "L4"    # 记忆层
    L5 = "L5"    # 决策层
    L6 = "L6"    # 经验层
    L7 = "L7"    # 演化层
    L8 = "L8"    # 接口层
    L9 = "L9"    # 代理层
    L10 = "L10"  # 沙盒层

    @property
    def official(self) -> str:
        """获取驻守名臣"""
        officials = {
            "L0": "秦始皇", "L1": "诸葛亮", "L2": "魏征",
            "L3": "张良",   "L4": "司马迁", "L5": "包拯",
            "L6": "曾国藩", "L7": "商鞅",   "L8": "张骞",
            "L9": "韩信",   "L10": "庄子",
        }
        return officials.get(self.value, "")

    @property
    def department(self) -> str:
        """获取核心部门"""
        depts = {
            "L0": "御书房", "L1": "宗人府", "L2": "都察院",
            "L3": "军机处", "L4": "翰林院", "L5": "大理寺",
            "L6": "吏部",   "L7": "中书省", "L8": "礼部",
            "L9": "锦衣卫", "L10": "钦天监",
        }
        return depts.get(self.value, "")


@dataclass
class Message:
    """
    层间统一消息格式

    所有层级之间传递的消息格式统一，确保可追溯性。
    消息链 trace 记录了消息经过的所有层级。
    """
    # 基础字段
    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())

    # 路由信息
    source_layer: str = ""    # 来源层级
    target_layer: str = ""    # 目标层级（空=广播）

    # 消息类型
    type: str = ""            # observe, reason, decide, execute, veto, review...

    # 消息内容
    payload: Dict[str, Any] = field(default_factory=dict)

    # 优先级
    priority: int = 0         # 0=normal, 1=high, 2=critical

    # 消息链追踪
    trace: List[str] = field(default_factory=list)

    def add_trace(self, layer: str, note: str = ""):
        """添加追踪记录"""
        entry = f"[{self.timestamp}] {layer}"
        if note:
            entry += f" → {note}"
        self.trace.append(entry)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "timestamp": self.timestamp,
            "source": self.source_layer,
            "target": self.target_layer,
            "type": self.type,
            "priority": self.priority,
            "trace": self.trace,
            "payload_keys": list(self.payload.keys()),
        }

    def __repr__(self) -> str:
        return (f"<Message {self.id} {self.source_layer}→{self.target_layer or 'BROADCAST'}"
                f" type={self.type} priority={self.priority}>")


class MessageBus:
    """
    消息总线 - 十一层架构的神经网络

    负责：
    1. 层间消息路由（单播/广播）
    2. 消息订阅/发布
    3. 消息链追踪
    4. 历史记录
    """

    def __init__(self, max_history: int = 1000):
        self._subscribers: Dict[str, List[Callable]] = {}
        self._history: List[Message] = []
        self._max_history = max_history
        self._hooks: Dict[str, List[Callable]] = {}  # 消息钩子
        self._stats = {"published": 0, "delivered": 0, "broadcasts": 0}

    # ── Subscription ──────────────────────────────────────────────

    def subscribe(self, layer: str, callback: Callable[[Message], None]):
        """订阅某层级的消息"""
        if layer not in self._subscribers:
            self._subscribers[layer] = []
        self._subscribers[layer].append(callback)

    def unsubscribe(self, layer: str, callback: Callable[[Message], None]):
        """取消订阅"""
        if layer in self._subscribers:
            self._subscribers[layer].remove(callback)

    def add_hook(self, msg_type: str, callback: Callable[[Message], None]):
        """添加消息钩子（所有该类型的消息都会触发）"""
        if msg_type not in self._hooks:
            self._hooks[msg_type] = []
        self._hooks[msg_type].append(callback)

    # ── Publishing ────────────────────────────────────────────────

    def publish(self, message: Message):
        """发布消息到目标层级"""
        message.add_trace(message.source_layer)
        self._history.append(message)
        self._stats["published"] += 1

        # 裁剪历史
        if len(self._history) > self._max_history:
            self._history = self._history[-self._max_history:]

        # 执行钩子
        if message.type in self._hooks:
            for hook in self._hooks[message.type]:
                hook(message)

        # 路由
        if message.target_layer:
            # 单播
            self._stats["delivered"] += self._deliver_to(message, message.target_layer)
        else:
            # 广播
            self._stats["broadcasts"] += 1
            for layer, callbacks in self._subscribers.items():
                if layer != message.source_layer:
                    for cb in callbacks:
                        self._stats["delivered"] += 1
                        cb(message)

    def _deliver_to(self, message: Message, target: str) -> int:
        """投递消息到指定层级"""
        if target not in self._subscribers:
            return 0
        count = 0
        for callback in self._subscribers[target]:
            try:
                callback(message)
                count += 1
            except Exception as e:
                print(f"  [消息总线] 投递失败 {target}: {e}")
        return count

    # ── Convenience Methods ───────────────────────────────────────

    def send(
        self,
        source: str,
        target: str,
        msg_type: str,
        payload: dict = None,
        priority: int = 0
    ) -> Message:
        """快捷发送：构造并发送消息"""
        msg = Message(
            source_layer=source,
            target_layer=target,
            type=msg_type,
            payload=payload or {},
            priority=priority
        )
        self.publish(msg)
        return msg

    def broadcast(self, source: str, msg_type: str, payload: dict = None) -> Message:
        """广播消息"""
        msg = Message(
            source_layer=source,
            target_layer="",
            type=msg_type,
            payload=payload or {}
        )
        self.publish(msg)
        return msg

    # ── Query ─────────────────────────────────────────────────────

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
            "subscribers": {layer: len(cbs) for layer, cbs in self._subscribers.items()},
            "hooks": list(self._hooks.keys()),
            "history_size": len(self._history),
        }


# ── Convenience Layer Imports ──────────────────────────────────────

# 导出 LayerLevel 别名，供其他模块使用
__all__ = ["Message", "MessageBus", "LayerLevel"]

"""
Channel Manager - 统一通道管理器
管理所有 IM 入口，统一消息路由
"""

from __future__ import annotations

import asyncio
import logging
from typing import Any, Callable, Dict, List, Optional
from datetime import datetime

from .base import ChannelAdapter, ChannelMessage, ChannelType
from .feishu import FeishuAdapter
from .telegram import TelegramAdapter

logger = logging.getLogger(__name__)


class ChannelManager:
    """统一通道管理器"""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.channels: Dict[ChannelType, ChannelAdapter] = {}
        self.handlers: Dict[ChannelType, List[Callable]] = {}
        self._locks: Dict[ChannelType, asyncio.Lock] = {}
        self._initialized = False

    async def initialize(self, config: Optional[Dict[str, Any]] = None) -> None:
        """初始化所有通道"""
        if self._initialized:
            return

        config = config or self.config

        # 飞书
        feishu_cfg = config.get("feishu", {})
        if feishu_cfg.get("enabled"):
            self.register(ChannelType.FEISHU, FeishuAdapter(feishu_cfg))
            logger.info("✅ 飞书通道已注册")

        # Telegram
        telegram_cfg = config.get("telegram", {})
        if telegram_cfg.get("enabled"):
            self.register(ChannelType.TELEGRAM, TelegramAdapter(telegram_cfg))
            logger.info("✅ Telegram 通道已注册")

        self._initialized = True

    def register(
        self,
        channel_type: ChannelType,
        adapter: ChannelAdapter
    ) -> None:
        """注册通道"""
        self.channels[channel_type] = adapter
        self.handlers[channel_type] = []
        self._locks[channel_type] = asyncio.Lock()

    def register_handler(
        self,
        channel_type: ChannelType,
        handler: Callable[[ChannelMessage], Any]
    ) -> None:
        """注册消息处理器"""
        if channel_type not in self.handlers:
            self.handlers[channel_type] = []
        self.handlers[channel_type].append(handler)

    async def handle_message(
        self,
        channel_type: ChannelType,
        raw: Dict[str, Any]
    ) -> Optional[List[Any]]:
        """处理收到的消息"""
        if channel_type not in self.channels:
            logger.warning(f"未注册的通道: {channel_type}")
            return None

        adapter = self.channels[channel_type]
        message = await adapter.parse_message(raw)

        # 忽略空消息和心跳
        if not message.content or message.content.startswith("/ping"):
            return None

        results = []
        for handler in self.handlers.get(channel_type, []):
            try:
                result = await handler(message)
                results.append(result)
            except Exception as e:
                logger.error(f"处理消息失败: {e}")

        return results if results else None

    async def send(
        self,
        channel_type: ChannelType,
        message: str,
        chat_id: str,
        **kwargs
    ) -> bool:
        """通过指定通道发送消息"""
        if channel_type not in self.channels:
            logger.warning(f"未注册的通道: {channel_type}")
            return False

        adapter = self.channels[channel_type]
        return await adapter.send_message(message, chat_id, **kwargs)

    async def broadcast(
        self,
        message: str,
        exclude: Optional[List[ChannelType]] = None
    ) -> Dict[ChannelType, bool]:
        """广播消息到所有通道"""
        exclude = exclude or []
        results = {}

        for ch_type, adapter in self.channels.items():
            if ch_type in exclude:
                continue
            try:
                # 广播时使用配置的默认 chat_id
                default_chat = self.config.get(ch_type.value, {}).get("default_chat_id", "")
                if default_chat:
                    result = await adapter.send_message(message, default_chat)
                    results[ch_type] = result
            except Exception as e:
                logger.error(f"广播到 {ch_type} 失败: {e}")
                results[ch_type] = False

        return results

    def list_channels(self) -> List[Dict[str, Any]]:
        """列出所有已注册的通道"""
        return [
            {
                "type": ch_type.value,
                "enabled": adapter.enabled,
                "healthy": asyncio.run(adapter.health_check()),
            }
            for ch_type, adapter in self.channels.items()
        ]

    def get_adapter(self, channel_type: ChannelType) -> Optional[ChannelAdapter]:
        """获取指定通道适配器"""
        return self.channels.get(channel_type)

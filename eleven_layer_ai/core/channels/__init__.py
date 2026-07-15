"""
AIUCE 多入口通道模块
支持飞书、Telegram 等 IM 平台接入

架构:
- ChannelAdapter: 基础适配器接口
- FeishuAdapter: 飞书适配器
- TelegramAdapter: Telegram 适配器
- ChannelManager: 统一管理器
"""

from .base import ChannelAdapter, ChannelMessage, ChannelType
from .feishu import FeishuAdapter
from .telegram import TelegramAdapter
from .manager import ChannelManager

__all__ = [
    "ChannelAdapter",
    "ChannelMessage",
    "ChannelType",
    "FeishuAdapter",
    "TelegramAdapter",
    "ChannelManager",
]

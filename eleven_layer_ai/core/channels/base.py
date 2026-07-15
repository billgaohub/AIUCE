"""
Channel Base - 通道基础接口
定义统一的消息格式和适配器接口
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, Optional
import uuid


class ChannelType(Enum):
    """支持的通道类型"""
    FEISHU = "feishu"
    TELEGRAM = "telegram"
    WEBHOOK = "webhook"
    API = "api"


@dataclass
class ChannelMessage:
    """统一消息格式"""
    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    channel: ChannelType = ChannelType.API
    user_id: str = ""
    chat_id: str = ""
    content: str = ""
    raw: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_system_input(self) -> Dict[str, Any]:
        """转换为系统输入格式"""
        return {
            "channel": self.channel.value,
            "user_id": self.user_id,
            "chat_id": self.chat_id,
            "content": self.content,
            "raw": self.raw,
            "timestamp": self.timestamp.isoformat(),
            "metadata": self.metadata,
        }


class ChannelAdapter(ABC):
    """通道适配器基类"""

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.enabled = config.get("enabled", True)
        self.name = self.__class__.__name__.replace("Adapter", "").lower()

    @abstractmethod
    async def send_message(self, message: str, chat_id: str, **kwargs) -> bool:
        """发送消息到通道"""
        pass

    @abstractmethod
    async def parse_message(self, raw: Dict[str, Any]) -> ChannelMessage:
        """解析原始消息为统一格式"""
        pass

    @abstractmethod
    async def setup_webhook(self, webhook_url: str) -> bool:
        """设置 Webhook"""
        pass

    async def health_check(self) -> bool:
        """健康检查"""
        return self.enabled

    def format_response(self, text: str) -> str:
        """格式化响应消息"""
        return text.strip()

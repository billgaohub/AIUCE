"""
Telegram Adapter - Telegram 通道适配器
支持 Telegram Bot 消息接收和发送
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional
import httpx
import json

from .base import ChannelAdapter, ChannelMessage, ChannelType


class TelegramAdapter(ChannelAdapter):
    """Telegram 适配器"""

    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.bot_token = config.get("bot_token", "")
        self.api_base = f"https://api.telegram.org/bot{self.bot_token}"
        self.parse_mode = config.get("parse_mode", "Markdown")
        self.proxy_url = config.get("proxy_url", "")
        self.allow_groups = config.get("allow_groups", True)

    async def send_message(
        self,
        message: str,
        chat_id: str,
        reply_to: Optional[str] = None,
        keyboard: Optional[List[List[Dict]]] = None,
        **kwargs
    ) -> bool:
        """发送消息到 Telegram"""
        payload = {
            "chat_id": chat_id,
            "text": message,
            "parse_mode": self.parse_mode,
        }
        if reply_to:
            payload["reply_to_message_id"] = reply_to
        if keyboard:
            payload["reply_markup"] = json.dumps({"inline_keyboard": keyboard})

        try:
            async with httpx.AsyncClient() as client:
                resp = await client.post(
                    f"{self.api_base}/sendMessage",
                    json=payload,
                    timeout=15.0,
                )
                return resp.json().get("ok", False)
        except Exception:
            return False

    async def parse_message(self, raw: Dict[str, Any]) -> ChannelMessage:
        """解析 Telegram Update"""
        message = raw.get("message", raw.get("edited_message", {}))
        callback_query = raw.get("callback_query", {})

        if callback_query:
            message = callback_query.get("message", {})
            content = callback_query.get("data", "")
            user_id = str(callback_query.get("from", {}).get("id", ""))
        else:
            # 处理文本、图片、命令等
            content = (
                message.get("text") or
                message.get("caption", "") or
                ""
            )
            # 处理命令
            if message.get("entities"):
                for entity in message["entities"]:
                    if entity.get("type") == "bot_command":
                        content = "/" + content
                        break
            user_id = str(message.get("from", {}).get("id", ""))

        chat = message.get("chat", {})
        return ChannelMessage(
            channel=ChannelType.TELEGRAM,
            user_id=user_id,
            chat_id=str(chat.get("id", "")),
            content=content.strip(),
            raw=raw,
            metadata={
                "message_id": str(message.get("message_id", "")),
                "chat_type": chat.get("type", "private"),
                "is_group": chat.get("type") in ("group", "supergroup"),
                "callback_query_id": callback_query.get("id", ""),
            }
        )

    async def setup_webhook(self, webhook_url: str) -> bool:
        """设置 Webhook"""
        try:
            async with httpx.AsyncClient() as client:
                resp = await client.post(
                    f"{self.api_base}/setWebhook",
                    json={"url": webhook_url},
                    timeout=15.0,
                )
                result = resp.json()
                return result.get("ok", False)
        except Exception:
            return False

    async def get_me(self) -> Optional[Dict[str, Any]]:
        """获取 Bot 信息"""
        try:
            async with httpx.AsyncClient() as client:
                resp = await client.get(f"{self.api_base}/getMe", timeout=10.0)
                return resp.json().get("result")
        except Exception:
            return None

    async def answer_callback_query(
        self,
        callback_query_id: str,
        text: Optional[str] = None
    ) -> bool:
        """回应回调查询（按钮点击）"""
        payload = {"callback_query_id": callback_query_id}
        if text:
            payload["text"] = text

        try:
            async with httpx.AsyncClient() as client:
                resp = await client.post(
                    f"{self.api_base}/answerCallbackQuery",
                    json=payload,
                    timeout=10.0,
                )
                return resp.json().get("ok", False)
        except Exception:
            return False

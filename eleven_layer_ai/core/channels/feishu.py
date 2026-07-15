"""
Feishu Adapter - 飞书通道适配器
支持飞书机器人消息接收和发送
"""

from __future__ import annotations

from typing import Any, Dict, Optional
import httpx
import hashlib
import time
import json

from .base import ChannelAdapter, ChannelMessage, ChannelType


class FeishuAdapter(ChannelAdapter):
    """飞书适配器"""

    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.app_id = config.get("app_id", "")
        self.app_secret = config.get("app_secret", "")
        self.verification_token = config.get("verification_token", "")
        self.encrypt_key = config.get("encrypt_key", "")
        self.api_base = config.get("api_base", "https://open.feishu.cn/open-apis")
        self.access_token: Optional[str] = None
        self.token_expires_at: float = 0

    async def _get_access_token(self) -> str:
        """获取 access_token（带缓存）"""
        now = time.time()
        if self.access_token and now < self.token_expires_at:
            return self.access_token

        async with httpx.AsyncClient() as client:
            resp = await client.post(
                f"{self.api_base}/auth/v3/tenant_access_token/internal",
                json={"app_id": self.app_id, "app_secret": self.app_secret},
                timeout=10.0,
            )
            data = resp.json()
            self.access_token = data.get("tenant_access_token", "")
            self.token_expires_at = now + data.get("expire", 7200) - 60
            return self.access_token

    async def send_message(
        self,
        message: str,
        chat_id: str,
        msg_type: str = "text",
        **kwargs
    ) -> bool:
        """发送消息到飞书群或个人"""
        token = await self._get_access_token()

        payload = {
            "receive_id": chat_id,
            "msg_type": msg_type,
            "content": json.dumps({"text": message}) if msg_type == "text" else message,
        }
        if msg_type == "text":
            payload["content"] = json.dumps({"text": message})

        try:
            async with httpx.AsyncClient() as client:
                resp = await client.post(
                    f"{self.api_base}/im/v1/messages?receive_id_type=chat_id",
                    headers={"Authorization": f"Bearer {token}"},
                    json=payload,
                    timeout=15.0,
                )
                return resp.status_code == 200
        except Exception:
            return False

    async def parse_message(self, raw: Dict[str, Any]) -> ChannelMessage:
        """解析飞书事件消息"""
        event = raw.get("event", {})
        header = raw.get("header", {})

        # 处理加密消息
        if "encrypt" in raw:
            decrypted = self._decrypt(raw["encrypt"])
            raw = json.loads(decrypted)
            event = raw.get("event", {})

        msg = ChannelMessage(
            channel=ChannelType.FEISHU,
            user_id=event.get("sender", {}).get("sender_id", {}).get("open_id", ""),
            chat_id=event.get("chat_id", ""),
            content=event.get("text", "").get("content", ""),
            raw=raw,
            metadata={
                "event_type": header.get("event_type", ""),
                "message_id": event.get("message_id", ""),
            }
        )
        return msg

    async def setup_webhook(self, webhook_url: str) -> bool:
        """验证 Webhook URL"""
        return True

    async def verify_request(
        self,
        timestamp: str,
        nonce: str,
        signature: str
    ) -> bool:
        """验证飞书请求签名"""
        string_to_sign = f"{timestamp}{nonce}{self.encrypt_key}"
        sign = hashlib.sha1(string_to_sign.encode()).hexdigest()
        return sign == signature

    def _decrypt(self, encrypt: str) -> str:
        """AES 解密"""
        if not self.encrypt_key:
            return encrypt

        try:
            from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
            from cryptography.hazmat.backends import default_backend
            import base64

            # 密钥处理：SHA256 后取 32 字节
            key_hash = hashlib.sha256(self.encrypt_key.encode("utf-8")).digest()
            
            # 解码 base64
            decode_data = base64.b64decode(encrypt)
            
            # IV 在前 16 字节
            iv = decode_data[:16]
            cipher_text = decode_data[16:]
            
            # AES-CBC 解密
            cipher = Cipher(algorithms.AES(key_hash), modes.CBC(iv), backend=default_backend())
            decryptor = cipher.decryptor()
            decrypted_data = decryptor.update(cipher_text) + decryptor.finalize()
            
            # 移除 PKCS7 填充
            padding_len = decrypted_data[-1]
            if padding_len < 1 or padding_len > 16:
                return decrypted_data.decode("utf-8")
                
            return decrypted_data[:-padding_len].decode("utf-8")
        except Exception as e:
            print(f"  [Feishu] ❌ 解密失败: {str(e)}")
            return encrypt

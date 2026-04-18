# 多入口通道

AIUCE 通过统一通道层支持多 IM 平台接入，所有消息统一为 `ChannelMessage` 格式，由 `ChannelManager` 集中路由。

## 架构

```
User (飞书/Telegram/其他)
    ↓
Webhook → /webhook/feishu  或  /webhook/telegram
    ↓
ChannelManager (统一管理器)
    ↓
Handler (AIUCE 核心处理)
    ↓
ChannelAdapter.send_message() → 用户回复
```

## 支持的平台

### 飞书

**功能**：
- 接收群聊/私聊消息
- 发送文本消息
- Webhook 事件验证签名
- AES 消息解密（预留）

**配置**：
```bash
export FEISHU_APP_ID=cli_xxxxxxxxxxxxxxxx
# SECRET=<removed for security>
export FEISHU_VERIFICATION_TOKEN=xxxxxxxxxxxxxxxx
```

**Webhook 设置**：
飞书开放平台 → 企业自建应用 → 消息事件 → 添加请求地址：
```
https://your-domain.com/webhook/feishu
```

### Telegram

**功能**：
- 接收私信/群组消息
- 支持 Inline Keyboard（回调查询）
- Bot 命令处理
- 群组/私聊区分

**配置**：
```bash
export TELEGRAM_BOT_TOKEN=123456789:ABCdefGHIjklMNOpqrsTUVwxyz
```

**Webhook 设置**：
```bash
curl -X POST https://api.telegram.org/bot<TOKEN>/setWebhook \
  -d '{"url": "https://your-domain.com/webhook/telegram"}'
```

## API 端点

### `GET /channels`

列出所有已注册的通道状态：

```json
{
  "channels": [
    { "type": "feishu", "enabled": true, "healthy": true },
    { "type": "telegram", "enabled": true, "healthy": true }
  ]
}
```

### `POST /channels/broadcast`

广播消息到所有通道：

```json
POST /channels/broadcast
{
  "message": "系统通知内容"
}
```

### `POST /webhook/feishu`

接收飞书事件推送，请求体示例：

```json
{
  "schema": "2.0",
  "header": {
    "event_type": "im.message.receive_v1",
    "token": "xxx"
  },
  "event": {
    "sender": { "sender_id": { "open_id": "ou_xxx" } },
    "chat_id": "oc_xxx",
    "message_id": "om_xxx",
    "text": { "content": "用户输入" }
  }
}
```

### `POST /webhook/telegram`

接收 Telegram Update，核心字段：

```json
{
  "update_id": 123456789,
  "message": {
    "chat": { "id": 123456789, "type": "private" },
    "from": { "id": 123456789 },
    "text": "用户输入"
  }
}
```

## 代码示例

### 发送消息

```python
from core.channels import ChannelManager, ChannelType

manager = ChannelManager()
await manager.initialize({
    "feishu": {
        "enabled": True,
        "app_id": "cli_xxx",
        "app_secret": "xxx",
    }
})

# 发送消息
await manager.send(
    ChannelType.FEISHU,
    "这是回复内容",
    chat_id="oc_xxxxxxxx"
)
```

### 注册消息处理器

```python
async def handle(message: ChannelMessage):
    result = await system.process(message.content)
    return result

manager.register_handler(ChannelType.TELEGRAM, handle)
```

## 扩展新通道

继承 `ChannelAdapter` 即可：

```python
from core.channels.base import ChannelAdapter, ChannelMessage, ChannelType

class MyChannelAdapter(ChannelAdapter):
    def __init__(self, config):
        super().__init__(config)

    async def send_message(self, message: str, chat_id: str, **kwargs) -> bool:
        # 实现发送逻辑
        pass

    async def parse_message(self, raw: Dict) -> ChannelMessage:
        # 实现消息解析
        pass

    async def setup_webhook(self, webhook_url: str) -> bool:
        # 实现 Webhook 设置
        pass

# 注册
manager.register(ChannelType.WEBHOOK, MyChannelAdapter(config))
```

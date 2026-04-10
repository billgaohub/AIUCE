# AI Reference
# API 参考文档 v1.1.0

> **版本**: 1.1.0 (安全加固版)
> **更新日期**: 2026-04-08

## 概述

AIUCE API v1.1.0 新增安全特性：
- ✅ API Key 认证 (`X-API-Key` Header)
- ✅ Rate Limiting (默认 100 req/min)
- ✅ 异常脱敏处理
- ✅ 请求 ID 追踪

---

## 认证

### API Key 认证

所有 API 请求（除 `/health` 外）需要携带 `X-API-Key` Header：

```bash
curl -H "X-API-Key: your-api-key" http://localhost:8000/status
```

### 环境变量配置

```bash
# 设置 API Keys（逗号分隔多个）
export AIUCE_API_KEYS="key1,key2,key3"

# 是否启用认证（开发模式可关闭）
export AIUCE_AUTH_ENABLED="true"

# Rate Limit 配置
export AIUCE_RATE_LIMIT="100"  # 每分钟最大请求数

# CORS 配置
export AIUCE_CORS_ORIGINS="*"  # 允许的来源
```

### 本地开发模式

未配置 `AIUCE_API_KEYS` 时，API 允许本地访问（无需认证）。

---

## 端点列表

| 方法 | 端点 | 认证 | 说明 |
|------|------|------|------|
| GET | `/` | ❌ | 根路径，重定向到 Web 界面 |
| GET | `/health` | ❌ | 健康检查 |
| GET | `/status` | ✅ | 获取系统状态 |
| POST | `/chat` | ✅ | 对话接口（完整响应） |
| POST | `/chat/simple` | ✅ | 简单对话（仅文本） |
| GET | `/constitution` | ✅ | 获取宪法条款 |
| POST | `/memory` | ✅ | 存储记忆 |
| GET | `/memory` | ✅ | 检索记忆 |
| GET | `/audit` | ✅ | 获取审计日志 |
| POST | `/review` | ✅ | 执行每日复盘 |
| POST | `/evolve` | ✅ | 触发系统演化 |

---

## 详细 API

### GET /health

健康检查端点，无需认证。

**响应**:
```json
{
  "status": "healthy",
  "timestamp": "2026-04-08T12:00:00",
  "version": "1.1.0"
}
```

---

### GET /status

获取系统状态。

**响应**:
```json
{
  "version": "1.1.0",
  "build_date": "2026-04-08",
  "layers": {
    "L0_constitution": 6,
    "L1_identity": "AI助手",
    "L2_perception": "active",
    "L3_reasoning": "active",
    "L4_memory": 0,
    "L5_decision": 0,
    "L6_experience": 0,
    "L7_evolution": 0,
    "L8_interface": 4,
    "L9_agent": 0,
    "L10_sandbox": 0
  },
  "message_bus": {
    "total_messages": 0,
    "subscriptions": 0
  },
  "audit": {
    "total_decisions": 0,
    "total_vetos": 0
  }
}
```

---

### POST /chat

完整对话接口。

**请求体**:
```json
{
  "message": "你好",
  "context": {}  // 可选
}
```

**响应**:
```json
{
  "response": "你好！我是基于十一层架构的 AI 助手...",
  "status": "success",
  "layers_involved": ["L0", "L1", "L2", "L3", "L5", "L8"],
  "audit_id": "audit_xxx",
  "vetoed": false,
  "veto_reason": null,
  "timing": {
    "L0_constitution_ms": 1,
    "L1_identity_ms": 0,
    "total_ms": 150
  },
  "request_id": "abc12345"
}
```

---

### POST /chat/simple

简单对话接口，仅返回文本响应。

**请求体**:
```json
{
  "message": "你好"
}
```

**响应**:
```json
{
  "response": "你好！我是 AI 助手..."
}
```

---

### GET /constitution

获取宪法条款列表。

**响应**:
```json
{
  "title": "十一层架构最高宪法",
  "created": "2026-04-08T12:00:00",
  "clauses": [
    {
      "id": "SOVEREIGNTY-1",
      "title": "最高主权不可侵犯",
      "content": "系统主权归用户所有，AI不得自授权限",
      "severity": 3,
      "enabled": true
    }
  ]
}
```

---

### POST /memory

存储记忆。

**请求体**:
```json
{
  "content": "今天学习了 AIUCE 架构",
  "category": "event",
  "importance": 0.8
}
```

**响应**:
```json
{
  "memory_id": "mem_xxx",
  "status": "success"
}
```

---

### GET /memory

检索记忆。

**参数**:
- `query` (required): 搜索关键词
- `limit` (optional): 返回数量，默认 10

**响应**:
```json
{
  "memories": [
    {
      "id": "mem_xxx",
      "content": "今天学习了 AIUCE 架构",
      "category": "event",
      "importance": 0.8,
      "timestamp": 1712553600
    }
  ]
}
```

---

### GET /audit

获取审计日志。

**参数**:
- `limit` (optional): 返回数量，默认 100

**响应**:
```json
{
  "logs": [
    {
      "id": "audit_xxx",
      "input": "用户输入...",
      "decision": {...},
      "timestamp": "2026-04-08T12:00:00"
    }
  ]
}
```

---

### POST /review

执行每日复盘。

**响应**:
```json
{
  "anomalies": [],
  "success_patterns": [],
  "review_date": "2026-04-08"
}
```

---

### POST /evolve

触发系统演化。

**参数**:
- `rule_id` (optional): 要演化的规则 ID

**响应**:
```json
{
  "evolved": false,
  "reason": "No evolution needed"
}
```

---

## 错误响应

### 401 Unauthorized

```json
{
  "detail": "Invalid or missing API key"
}
```

### 429 Too Many Requests

```json
{
  "detail": "Rate limit exceeded. Max 100 requests per 60s"
}
```

### 500 Internal Server Error

```json
{
  "error": "Internal server error",
  "request_id": "abc12345",
  "timestamp": "2026-04-08T12:00:00",
  "detail": "An error occurred. Check server logs for details."
}
```

---

## Python SDK 使用示例

```python
import httpx

class AIUCEClient:
    def __init__(self, base_url: str, api_key: str = None):
        self.base_url = base_url
        self.api_key = api_key
        self.headers = {"X-API-Key": api_key} if api_key else {}
    
    def chat(self, message: str) -> dict:
        response = httpx.post(
            f"{self.base_url}/chat",
            json={"message": message},
            headers=self.headers
        )
        return response.json()
    
    def get_status(self) -> dict:
        response = httpx.get(
            f"{self.base_url}/status",
            headers=self.headers
        )
        return response.json()
    
    def health_check(self) -> dict:
        response = httpx.get(f"{self.base_url}/health")
        return response.json()


# 使用示例
client = AIUCEClient("http://localhost:8000", api_key="your-key")
print(client.chat("你好"))
```

---

## cURL 示例

```bash
# 健康检查
curl http://localhost:8000/health

# 获取状态（需要认证）
curl -H "X-API-Key: your-key" http://localhost:8000/status

# 对话
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your-key" \
  -d '{"message": "你好"}'

# 存储记忆
curl -X POST http://localhost:8000/memory \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your-key" \
  -d '{"content": "测试记忆", "importance": 0.5}'
```

---

## 各层 API（内部使用）

### L0: Constitution (意志层)

```python
class Constitution:
    def is_constitutional(self, input: str, context: Dict) -> bool
    def add_clause(self, clause: ConstitutionClause)
    def remove_clause(self, clause_id: str)
    def export_constitution(self) -> Dict
```

### L1: IdentityLayer (身份层)

```python
class IdentityLayer:
    def check_boundary(self, input: str) -> Dict
    def update_profile(self, profile: IdentityProfile)
    def get_profile(self) -> IdentityProfile
```

### L2: PerceptionLayer (感知层)

```python
class PerceptionLayer:
    def observe(self, user_input: str) -> Dict
    def add_source(self, name: str, source: DataSource)
    def refresh(self)
```

### L3: ReasoningLayer (推理层)

```python
class ReasoningLayer:
    def reason(self, user_input: str, perception: Dict, memories: List) -> Dict
    def register_model(self, name: str, model: MindModel)
    def unregister_model(self, name: str)
```

### L4: MemoryLayer (记忆层)

```python
class MemoryLayer:
    def store(self, content: str, category: str, importance: float) -> str
    def retrieve(self, query: str, limit: int = 10) -> List[Dict]
    def delete(self, memory_id: str) -> bool
    def stats(self) -> Dict
```

### L5: DecisionLayer (决策层)

```python
class DecisionLayer:
    def adjudicate(self, input: str, reasoning: Dict, memories: List) -> Dict
    def get_decision(self, decision_id: str) -> Dict
    def list_decisions(self, limit: int = 100) -> List[Dict]
```

### L6: ExperienceLayer (经验层)

```python
class ExperienceLayer:
    def review(self, input: str, decision: Dict, response: str, result: Dict) -> Dict
    def daily_review(self) -> Dict
    def get_patterns(self) -> List[Dict]
```

### L7: EvolutionLayer (演化层)

```python
class EvolutionLayer:
    def check_evolution_needed(self) -> Dict
    def propose_evolution(self, change: EvolutionChange) -> str
    def approve_evolution(self, rule_id: str) -> bool
    def execute_evolution(self, rule_id: str) -> Dict
```

### L8: InterfaceLayer (接口层)

```python
class InterfaceLayer:
    def call_model(self, prompt: str, context: List, reasoning: Dict) -> ModelResponse
    def register_provider(self, name: str, provider: ModelProvider)
    def set_default_provider(self, name: str)
```

### L9: AgentLayer (代理层)

```python
class AgentLayer:
    def execute(self, decision: Dict, model_response: ModelResponse) -> Dict
    def register_tool(self, name: str, tool: Tool)
    def list_tools(self) -> List[str]
```

### L10: SandboxLayer (沙盒层)

```python
class SandboxLayer:
    def simulate(self, decision: Dict, reasoning: Dict) -> Dict
    def run_scenario(self, scenario: SimulationScenario) -> SimulationResult
    def get_simulation_history(self) -> List[Dict]
```

---

## 类型定义

### Message

```python
@dataclass
class Message:
    id: str
    source: str
    target: str
    msg_type: str
    payload: Dict
    timestamp: float
    priority: int = 0
```

### ModelResponse

```python
@dataclass
class ModelResponse:
    content: str
    success: bool
    error: Optional[str]
    latency_ms: float
    provider: str
    tokens_used: Optional[int]
```

### MemoryEntry

```python
@dataclass
class MemoryEntry:
    id: str
    content: str
    category: str
    importance: float
    timestamp: float
    embedding: Optional[List[float]]
    metadata: Dict
```

---

## 工具函数

### gen_id() -> str

生成唯一ID。

### gen_timestamp() -> float

生成当前时间戳。

### detect_intent(text: str) -> List[str]

检测文本意图。

### assess_risk(text: str) -> float

评估风险分数 (0-1)。

### semantic_search(query: str, documents: List[str], top_k: int = 5) -> List[Tuple[int, float]]

语义搜索。

### Timer

```python
with Timer("operation_name") as timer:
    # 执行操作
    pass
print(f"耗时: {timer.elapsed_ms()}ms")
```

---

## 多入口通道 API

### GET /channels

列出所有已注册的 IM 通道状态。

**响应示例**：
```json
{
  "channels": [
    { "type": "feishu", "enabled": true, "healthy": true },
    { "type": "telegram", "enabled": false, "healthy": false }
  ]
}
```

### POST /channels/broadcast

广播消息到所有已启用的通道。

**请求参数**：
| 参数 | 类型 | 说明 |
|------|------|------|
| message | string | 广播内容 |

**响应示例**：
```json
{
  "results": {
    "feishu": true,
    "telegram": false
  }
}
```

### POST /webhook/feishu

飞书事件 Webhook 接收端点。由飞书开放平台推送事件。

**飞书事件格式**：
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
    "text": { "content": "用户输入内容" }
  }
}
```

### POST /webhook/telegram

Telegram Bot Webhook 接收端点。

**Telegram Update 格式**：
```json
{
  "update_id": 123456789,
  "message": {
    "chat": { "id": 123456789, "type": "private" },
    "from": { "id": 123456789, "is_bot": false },
    "message_id": 1,
    "text": "用户输入"
  }
}
```

## 通道配置

通过环境变量配置各通道：

| 环境变量 | 说明 | 必需 |
|----------|------|------|
| `FEISHU_APP_ID` | 飞书应用 ID | 飞书启用时 |
| `FEISHU_APP_SECRET` | 飞书应用密钥 | 飞书启用时 |
| `FEISHU_VERIFICATION_TOKEN` | 飞书验证 Token | 飞书启用时 |
| `TELEGRAM_BOT_TOKEN` | Telegram Bot Token | Telegram 启用时 |

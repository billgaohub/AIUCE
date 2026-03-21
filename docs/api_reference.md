# API Reference
# API 参考文档

## ElevenLayerSystem

主系统类，协调所有十一层。

### 构造函数

```python
ElevenLayerSystem(config: Dict[str, Any] = None)
```

参数：
- `config`: 配置字典，可选

### 方法

#### run(user_input: str) -> Dict[str, Any]

执行完整的十一层处理流程。

参数：
- `user_input`: 用户输入字符串

返回：
```python
{
    "status": "success",           # 状态
    "layers_involved": ["L2", ...], # 参与的层级
    "response": "...",             # 响应内容
    "audit_id": "...",             # 审计ID
    "vetoed": False,               # 是否被否决
    "veto_reason": None,           # 否决原因
    "veto_layer": None,            # 否决层级
    "timing": {...}                # 时间统计
}
```

#### chat(user_input: str) -> str

快捷对话接口，只返回文本响应。

参数：
- `user_input`: 用户输入字符串

返回：
- 响应文本字符串

#### get_status() -> Dict[str, Any]

获取系统状态。

返回：
```python
{
    "version": "1.0.0",
    "build_date": "2026-03-20",
    "layers": {
        "L0_constitution": 5,
        "L1_identity": "AI助手",
        ...
    },
    "message_bus": {...},
    "audit": {...}
}
```

#### get_audit_log(limit: int = 100) -> List[Dict]

获取审计日志。

参数：
- `limit`: 返回的最大条目数

返回：
- 审计日志条目列表

#### daily_review() -> Dict[str, Any]

执行每日复盘。

返回：
```python
{
    "anomalies": [...],       # 发现的异常
    "success_patterns": [...], # 成功模式
    "review_date": "..."
}
```

#### evolve(rule_id: str = None) -> Dict[str, Any]

触发系统演化。

参数：
- `rule_id`: 要演化的规则ID，可选

返回：
- 演化结果

#### memory_stats() -> Dict[str, Any]

获取记忆统计。

返回：
- 记忆层统计信息

#### export_constitution() -> Dict[str, Any]

导出宪法全文。

返回：
- 宪法条款列表

---

## 各层 API

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

## 消息总线 API

```python
class MessageBus:
    def send(self, source: str, target: str, msg_type: str, payload: Dict)
    def broadcast(self, msg_type: str, payload: Dict)
    def subscribe(self, msg_type: str, handler: Callable)
    def unsubscribe(self, msg_type: str, handler: Callable)
    def stats(self) -> Dict
```

---

## 审计日志 API

```python
class AuditLog:
    def log_decision(self, input: str, decision: Dict, reasoning: Dict) -> str
    def log_veto(self, layer: str, input: str, reason: str)
    def log_execution(self, decision_id: str, result: Dict)
    def get_logs(self, limit: int = 100) -> List[Dict]
    def get_stats(self) -> Dict
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

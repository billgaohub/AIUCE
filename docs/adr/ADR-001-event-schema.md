# ADR-001: Event Schema v1.0 定义

**ADR**: ADR-001
**标题**: 事件架构 - 四类核心事件定义
**状态**: 已批准
**提出日期**: 2026-05-09
**作者**: AIUCE Transformation

---

## 1. 背景

当前 AIUCE 系统的事件流散落各处，缺乏统一的事件 Schema 定义。现有 `core/neural_bus.py` 实现了事件存储，但事件类型过于繁多（60+ 种），无法从事件重建状态。

## 2. 决策

采用受限的 4 类核心事件架构。

## 3. 事件定义

### 3.1 UserIntentEvent - 用户意图事件

```yaml
event_type: user_intent
fields:
  - user_id: string
  - intent: string
  - raw_input: string
  - channel: string
```

### 3.2 AgentActionEvent - Agent 行为事件

```yaml
event_type: agent_action
fields:
  - agent_id: string
  - action_type: enum
  - target: string
  - params: object
  - risk_level: enum
```

### 3.3 StateMutationEvent - 状态变更事件

```yaml
event_type: state_mutation
fields:
  - path: string
  - before: any
  - after: any
  - causation_id: string
```

### 3.4 GovernanceEvent - 治理事件

```yaml
event_type: governance
fields:
  - policy_id: string
  - decision: enum
  - reason: string
  - severity: enum
```

## 4. 约束

- v1.0 严格限制 4 类事件
- 禁止直接 set_state()
- 事件必须可回放、可验证

## 5. 状态

| 日期 | 状态 | 说明 |
|------|------|------|
| 2026-05-09 | 已批准 | 初始版本 |

## 6. 实现

- `core/state_daemon.py` - 单一事实源实现
- `core/policy_engine.py` - 动态授权引擎
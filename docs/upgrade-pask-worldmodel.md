# AIUCE 升级计划：PASK + World Model 范式融合

> 基于 arXiv:2604.08000 (PASK), arXiv:2602.00785 (World Model Intermediary), arXiv:2603.19312 (LeWorldModel)

## Phase 1: 主动能力升级 (1-2月)

### 1.1 L2/L3 增强：流式意图检测 (IntentFlow)

**目标**：从被动响应升级为主动意图检测

**实现**：
- 新增 `IntentFlow` 类：流式上下文监控，检测潜在需求
- L2 感知层增加 `detect_latent_needs()` 方法
- L3 推理层增加 `streaming_reason()` 方法

**文件**：
- `repo/core/intent_flow.py` (新建)
- `repo/l2_perception.py` (修改)
- `repo/l3_reasoning.py` (修改)

### 1.2 L4 增强：Hybrid Memory 分层

**目标**：记忆分层建模，支持主动推理

**实现**：
- Workspace Memory：当前会话工作记忆
- User Memory：用户长期偏好/历史
- Global Memory：系统级知识

**文件**：
- `repo/core/hybrid_memory.py` (新建)
- `repo/l4_memory.py` (修改)

### 1.3 L10 探索：轻量世界模型架构

**目标**：为影子宇宙引入数据驱动的世界模型

**实现**：
- World Model 接口定义 (T^, R^, G^)
- Surprise 检测机制
- 成本模型

**文件**：
- `repo/core/world_model.py` (新建)
- `repo/l10_sandbox.py` (修改)

---

## Phase 2: 自进化能力 (2-4月)

### 2.1 L6/L7 联动：双过程反思机制

**目标**：Fast Process (System 1) + Slow Process (System 2)

**实现**：
- Fast: L3 快速直觉推理
- Slow: L6/L7 深度反思 + 规则演化
- 闭环：反思结果反馈到 L3

### 2.2 记忆压缩：Surprise 检测

**目标**：基于物理异常检测的记忆遗忘

**实现**：
- Surprise 分数计算
- 低 surprise 记忆压缩/遗忘
- 高 surprise 记忆保留

### 2.3 任务分布学习 G^

**目标**：从真实交互日志学习任务分布

**实现**：
- 交互日志收集
- 任务分布建模
- OOD 任务生成

---

## Phase 3: 主权与边缘 (4-6月)

### 3.1 L0/L1 主权保护层

**目标**：数据本地化保障

**实现**：
- 本地数据存储强制
- 外部数据传输审计
- 隐私边界检查

### 3.2 L9 资产托管抽象

**目标**：支持持有资产和执行交易

**实现**：
- 账户抽象接口
- 交易签名/验证
- 资产余额追踪

### 3.3 去中心化沙盒验证

**目标**：无中心化依赖的沙盒

**实现**：
- 本地验证网络
- 共识机制模拟
- 交易回滚测试

---

## 参考论文

1. PASK: arXiv:2604.08000 - DD-MM-PAS 主动代理范式
2. World Models as Intermediary: arXiv:2602.00785 - 世界模型中间层
3. LeWorldModel: arXiv:2603.19312 - 稳定端到端 JEPA
4. Agentic DeAI: 2026 AI Security Report - 去中心化主权 Agent

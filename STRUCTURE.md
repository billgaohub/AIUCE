# AIUCE - Project Structure
# 项目结构说明（已重组为 eleven_layer_ai/ 包）

> 2026-07-15 起，所有源码已移入 `eleven_layer_ai/` 包：根模块 + `core/` 子包。
> 运行方式：`python -m eleven_layer_ai.api` / `python -m eleven_layer_ai.demo`；
> 导入方式：`from eleven_layer_ai import create_system`；测试：`pytest tests/`。

```
eleven_layer_ai/                      # 顶层包（导入名即 eleven_layer_ai）
│
├── __init__.py                      # 包初始化，导出主要类（仅导出 Tier-A 集成层）
├── config.yaml                      # 配置文件
├── system.py                        # 主系统入口 - ElevenLayerSystem（协调全部 11 层）
├── utils.py                         # 工具函数（ID生成、风险评分、语义搜索等）
├── cli.py                           # 命令行接口（entry point: eleven-layer）
├── api.py                           # FastAPI 服务
├── demo.py                          # 演示脚本
│
├── l1_identity.py                   # L1 身份层（Tier-A 集成层，见下）
├── l2_perception.py                 # L2 感知层
├── l3_reasoning.py                  # L3 推理层
├── l4_memory.py                     # L4 记忆层
├── l5_decision.py                   # L5 决策层
├── l6_experience.py                 # L6 经验层
├── l7_evolution.py                  # L7 演化层
├── l8_interface.py                  # L8 接口层
├── l9_agent.py                      # L9 代理层
├── l10_sandbox.py                   # L10 沙盒层
│
├── core/                            # 核心子包
│   ├── __init__.py
│   ├── constants.py                 # 常量（Layer, MsgType, RiskLevel 等）
│   ├── types.py                     # 类型定义（Message, ModelResponse, ...）
│   ├── message.py                   # 消息总线
│   ├── constitution.py              # L0 宪法引擎（被 Tier-A L0 入口封装）
│   ├── audit.py                     # 审计日志（路径已改为可移植，见下）
│   ├── l0_sovereignty_gateway.py    # L0 主权网关（Tier-B 增强）
│   ├── l0_semantic_gateway.py       # L0 语义网关（Tier-B 增强）
│   ├── l1_identity_brain.py         # L1 增强：IdentityBrain + MECEWing
│   ├── l2_reality_sensor.py         # L2 增强：RealitySensor 多模态
│   ├── l2_document_ingestor.py      # L2 增强：文档摄取
│   ├── l3_cognitive_orchestrator.py # L3 增强：认知编排
│   ├── l4_palace_memory.py          # L4 增强：宫殿记忆
│   ├── l4_code_understanding.py     # L4 增强：代码理解
│   ├── l5_audit.py                  # L5 增强：三域审计
│   ├── l6_experience.py             # L6 增强：经验引擎
│   ├── l7_evolution_engine.py       # L7 增强：演化引擎
│   ├── l8_interface.py              # L8 增强：多模型路由
│   ├── l9_tool_harness.py           # L9 增强：工具编排（锦衣卫令牌系统）
│   ├── l9_agent.py                  # L9 增强：Agent 实现
│   └── ...（其余核心支撑模块）
│
├── tests/                           # 测试（不在安装包内）
│   ├── test_system.py               # 系统级测试（驱动 ElevenLayerSystem）
│   ├── test_layers.py               # Tier-A 各层单元测试
│   ├── test_integration.py          # 集成测试
│   ├── test_phase1.py ~ phase3.py   # Tier-B 增强层测试
│
├── examples/                        # 示例
├── docs/                            # 文档
└── benchmarks/                      # 性能测试
```

## ⚠️ 两层架构说明（重要，避免误判为“重复代码”）

本项目**刻意采用两层设计**，不是未经整理的重复实现：

| 层级 | 文件位置 | 角色 | 被谁使用 |
|------|---------|------|---------|
| **Tier-A 集成层**（稳定 API） | `eleven_layer_ai/l1_identity.py` … `l10_sandbox.py`、`system.py` | 生产运行时使用的、接口稳定的层实现；`__init__.py` 只导出这一层 | `ElevenLayerSystem`（`system.py`）——即默认运行路径 |
| **Tier-B 增强层**（独立/实验） | `eleven_layer_ai/core/lN_*_*.py`（如 `l1_identity_brain.py`、`l2_reality_sensor.py`、`l4_palace_memory.py`、`l7_evolution_engine.py`、`l9_tool_harness.py`…） | 功能更完整/实验性的“增强版”实现 | 仅由 `tests/test_phase1.py`–`test_phase3.py` 直接驱动，**未接入默认 `ElevenLayerSystem`** |

- 各 Tier-A 层文件头部 docstring 中以“增强版: core/xxx.py”注明其对应的 Tier-B 模块，便于溯源。
- 两层**不是简单副本**：Tier-B 模块类名/职责通常与 Tier-A 不同（如 `IdentityBrain` vs `IdentityLayer`、`RealitySensor` vs `PerceptionLayer`），属“互补增强”而非“待合并重复”。
- **收敛建议**：是否将 Tier-B 增强能力并入默认运行路径，是一个架构决策，应在下一代项目 **SONUV / AIOBR** 中统一规划，而非在即将归档的遗留仓库里做破坏性合并。

## 文件职责（Tier-A 运行时路径）

| 文件 | 层级 | 名臣 | 职责 |
|------|------|------|------|
| `core/constitution.py` | L0 | 秦始皇 | 宪法引擎，一票否决权（被 Tier-A L0 入口封装） |
| `l1_identity.py` | L1 | 诸葛亮 | 人设边界检查 |
| `l2_perception.py` | L2 | 魏征 | 现实对账，意图识别 |
| `l3_reasoning.py` | L3 | 张良 | 多路径推演 |
| `l4_memory.py` | L4 | 司马迁 | 语义索引，史料编纂 |
| `l5_decision.py` | L5 | 包拯 | 决策存证，审计落槌 |
| `l6_experience.py` | L6 | 曾国藩 | 复盘机制，模式固化 |
| `l7_evolution.py` | L7 | 商鞅 | 内核重构，变法执行 |
| `l8_interface.py` | L8 | 张骞 | 算力外交，模型调用 |
| `l9_agent.py` | L9 | 韩信 | 跨设备执行，工具调度 |
| `l10_sandbox.py` | L10 | 庄子 | 影子宇宙，模拟推演 |

## 配置与路径（已修复）

- `eleven_layer_ai/core/audit.py` 的审计日志路径已从硬编码本机绝对路径改为 `~/.aiuce/audit_log.json`（可通过 `config["storage_path"]` 覆盖）。
- `eleven_layer_ai/core/l0_semantic_gateway.py` 的 `SOUL.md` 查找候选已移除本机路径，改为基于包根/工作目录/用户主目录的可移植候选。

## 快速导航

- **开始使用**：`pip install -e .`，然后 `python -m eleven_layer_ai.demo`
- **启动 API**：`python -m eleven_layer_ai.api`
- **运行测试**：`pytest tests/`
- **了解架构**：`docs/architecture.md`
- **查看 API**：`docs/api_reference.md`

## 扩展开发

- 扩展 Tier-A 运行时层：编辑 `eleven_layer_ai/lN_*.py`。
- 实验 Tier-B 增强能力：编辑 `eleven_layer_ai/core/lN_*_*.py`，并通过 `tests/test_phaseN.py` 验证。
- 修改宪法条款（L0）：编辑 `config.yaml` 的 `constitution` 段，或运行时调用 `constitution.add_clause()`。

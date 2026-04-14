# AIUCE System 🏯

[![CI](https://github.com/billgaohub/AIUCE/actions/workflows/ci.yml/badge.svg)](https://github.com/billgaohub/AIUCE/actions)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.14](https://img.shields.io/badge/python-3.14-blue.svg)](https://www.python.org/downloads/)
[![Tests](https://img.shields.io/badge/tests-33%20passing-44cc44.svg)](#-tests)
[![Layers](https://img.shields.io/badge/layers-9%2F10%20active-7b2d8b.svg)](#-architecture)

> **AIUCE** = **A**I System + **U**niverse + **C**onstitution + **E**volution
>
> Personal AI Infrastructure with Layered Governance

AIUCE 是 Personal AI Infrastructure 的微缩密码，由四个核心哲学缩写映射十一层架构：
**A** 对应 L0-L10 全层感知与推理，**U** 对应 L10 影子宇宙（蒙特卡洛/A/B测试），
**C** 对应 L0 最高宪法（一票否决），**E** 对应 L7 渐进式变法（内核重构）。

---

## 命名释义

### 🤖 A — AI System (十一层架构人工智能)

具备分层治理、制衡机制与记忆能力的有机体。从感知、推理、决策到物理执行的完整多体协同。

**对应层级**: L0–L10 全架构

### 🌌 U — Universe (影子宇宙)

L10 沙盒层（庄子/钦天监）：在虚拟「影子宇宙」中通过蒙特卡洛模拟和 A/B 测试，模拟百万次失败，在现实中坍缩出一条可行路径。

### ⚖️ C — Constitution (最高宪法)

L0 意志层（秦始皇/御书房）：系统的最高权力中心，对一切偏离主权意志的指令行使「一票否决权」。

### 🔄 E — Evolution (渐进式演化)

L7 演化层（商鞅/中书省）：通过反馈循环，一旦经验层证明旧逻辑过时，便在物理层面重构内核代码，实现真正的自动变法。

---

## 🏛️ 十一层架构

| 层 | 架构层 | 名臣 | 部门 | 核心模块 | 来源 | 状态 |
|----|--------|------|------|----------|------|------|
| **L0** | 意志层 | 秦始皇 | 御书房 | `l0_sovereignty_gateway.py` | agent-sovereignty-rules | ✅ |
| **L0** | 语义层 | 魏征 | 都察院 | `l0_semantic_gateway.py` | hermes-agent | ✅ |
| **L1** | 身份层 | 诸葛亮 | 宗人府 | `l1_identity_brain.py` | gbrain | ✅ |
| **L2** | 感知层 | 张良 | 军机处 | `l2_document_ingestor.py` | markitdown | ✅ |
| **L3** | 推理层 | 张良 | 军机处 | `l3_cognitive_orchestrator.py` | teonu-worldmodel + deer-flow | ✅ |
| **L4** | 记忆层 | 司马迁 | 翰林院 | `l4_palace_memory.py` | mempalace | ✅ |
| **L4** | 记忆层 | 司马迁 | 翰林院 | `l4_code_understanding.py` | graphify | ✅ |
| **L5** | 决策层 | 包拯 | 大理寺 | `l5_audit.py` | ai-governance-framework | ✅ |
| **L6** | 经验层 | 曾国藩 | 吏部 | — | — | ⬜ 待 Phase 4 |
| **L7** | 演化层 | 商鞅 | 中书省 | `l7_evolution_engine.py` | OpenSpace | ✅ |
| **L8** | 接口层 | 张骞 | 礼部 | `l8_interface.py` | — | ✅ |
| **L9** | 代理层 | 韩信 | 锦衣卫 | `l9_tool_harness.py` | CLI-Anything + ipipq | ✅ |
| **L10** | 沙盒层 | 庄子 | 钦天监 | `l10_sandbox.py` | — | ✅ |

**进度**: 9/10 层核心模块已实现（L6 经验层待 Phase 4）

---

## 🧠 Phase 1–3 深度融合成果

基于「理念移植 > 代码复用」原则，从 5 个 billgaohub 项目和 5 个外部开源项目中提取核心理念，重构为 AIUCE 原生组件。

### 融合来源一览

| 模块 | 来源 | 核心理念 |
|------|------|---------|
| L0 SovereigntyGateway | agent-sovereignty-rules | P1-P7 宪法 + 关键词否决 |
| L0 SemanticGateway | hermes-agent | 语义置信度 + 合规网关 |
| L1 IdentityBrain | gbrain | MECE 实体目录 + Brain-first 查询 |
| L2 DocumentIngestor | markitdown | 万物转 Markdown + 双轨输出 |
| L3 CognitiveOrchestrator | teonu-worldmodel + deer-flow | 三层认知控制 + DAG 任务规划 |
| L4 PalaceMemory | mempalace | Raw Verbatim + 记忆宫殿 + 96.6% 检索率 |
| L4 CodeUnderstanding | graphify | AST 零 LLM + Leiden 社区检测 |
| L5 DecisionAudit | ai-governance-framework | 三域评分 + 哈希链 |
| L7 EvolutionEngine | OpenSpace | GDPVal 基准 + Skill 自演化 |
| L9 ToolHarness | CLI-Anything + ipipq | 合宪性注册 + 智能路由 |

详细报告：[docs/reports/aiuce-billgaohub-fusion-20260414.md](docs/reports/aiuce-billgaohub-fusion-20260414.md)

---

## ✅ 测试

```
tests/
├── test_layers.py      # 原有（引用旧类名，待清理）
├── test_system.py      # 原有（引用旧类名，待清理）
├── test_phase1.py      # L0/L3/L5/L9 模块测试 ✅
└── test_phase2.py      # L1/L2/L4/L7 模块测试 ✅
```

**运行测试**:

```bash
# 激活虚拟环境
source .venv/bin/activate

# 运行所有测试
.venv/bin/python3 -m pytest tests/ -v

# 仅运行 Phase 1-2（33 passing）
.venv/bin/python3 -m pytest tests/test_phase1.py tests/test_phase2.py -v
```

**测试结果**: `33 passed` — 覆盖 L0–L9 所有新融合模块

---

## 🛠️ 快速开始

```bash
# 克隆
git clone https://github.com/billgaohub/AIUCE.git
cd AIUCE

# 激活虚拟环境（Python 3.14）
source .venv/bin/activate

# 运行测试
python3 -m pytest tests/test_phase1.py tests/test_phase2.py -v
```

**初始化记忆目录**:

```python
from core.l1_identity_brain import IdentityBrain
from core.l4_palace_memory import PalaceMemory

brain = IdentityBrain()   # ~/.aiuce/brain/
palace = PalaceMemory()  # ~/.aiuce/palace/
```

**执行认知任务**:

```python
from core.l3_cognitive_orchestrator import CognitiveOrchestrator

oc = CognitiveOrchestrator()
dag = oc.plan("明天下雨准备备选方案")
result = oc.execute(dag)
```

**审计决策**:

```python
from core.l5_audit import DecisionAudit, AuditEntry, DecisionType

audit = DecisionAudit()
entry = AuditEntry(
    entry_id="task-001",
    session_id="session-x",
    layer="L3",
    timestamp="2026-04-14T12:00:00",
    decision_type="action",
    intent="测试意图",
    reasoning="测试推理",
    output="测试输出",
    sovereignty_passed=True,
)
audit.log(entry)
```

---

## 📡 多入口通道

| 平台 | 状态 | 能力 |
|------|------|------|
| 飞书 | ✅ 支持 | 消息收发、Webhook 接收 |
| Telegram | ✅ 支持 | Bot 消息、回调查询、Webhook |
| Webhook | ✅ 支持 | 自定义 HTTP 回调 |

配置见 [docs/channels.md](docs/channels.md)。

---

## 🔧 技术规格

- **Python**: 3.14
- **核心依赖**: pydantic 2.12.5
- **可选依赖**: markitdown（文档转换）、ChromaDB（向量检索）、faster-whisper（音视频转录）
- **虚拟环境**: `.venv/`（已配置）
- **测试框架**: pytest（33 passing）

---

## 📚 文档

| 文档 | 内容 |
|------|------|
| [fusion-phase2-3-20260414](docs/reports/aiuce-billgaohub-fusion-phase2-3-20260414.md) | Phase 2-3 融合完整报告 |
| [aiuce-billgaohub-fusion-20260414](docs/reports/aiuce-billgaohub-fusion-20260414.md) | Phase 1 融合完整报告 |
| [github-ecosystem-analysis-20260414](docs/reports/github-ecosystem-analysis-20260414.md) | 外部生态分析 |
| [architecture](docs/architecture.md) | 十一层架构详解 |
| [integration](docs/integration.md) | 开源集成指南 |

---

## 🚀 社区项目

| 项目 | 状态 | 说明 |
|------|------|------|
| [AIUCE](https://github.com/billgaohub/AIUCE) | ✅ Active | Personal AI Infrastructure（主仓库） |
| [IPIPQ](https://github.com/billgaohub/ipipq) | ✅ Active | AI 文件自动整理工具 |
| [smart-file-router](https://github.com/billgaohub/smart-file-router) | ✅ Active | 智能文件分类引擎（已融合至 L9） |

---

## 架构哲学

> "治大国若烹小鲜" — 老子

AIUCE 借鉴中国古代官僚治理智慧：

- **分层**让复杂系统可控（L1–L10 各司其职）
- **制衡**让权力不被滥用（L0 否决权）
- **审计**让决策可追溯（L5 哈希链）
- **演化**让系统持续改进（L7 GDPVal 自演化）

---

## 许可证

MIT License — 详见 [LICENSE](LICENSE)

---

**AIUCE** — Personal AI Infrastructure with Layered Governance  
🏯 治大国若烹小鲜

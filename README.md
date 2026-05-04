# AIUCE System 🏯

[![CI](https://github.com/billgaohub/AIUCE/actions/workflows/ci.yml/badge.svg)](https://github.com/billgaohub/AIUCE/actions)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.14](https://img.shields.io/badge/python-3.14-blue.svg)](https://www.python.org/downloads/)
[![Tests](https://img.shields.io/badge/tests-33%20passing-44cc44.svg)](#-tests)
[![Layers](https://img.shields.io/badge/layers-10%2F10%20active-44cc44.svg)](#-architecture)

> **AIUCE** = **A**I System + **U**niverse + **C**onstitution + **E**volution
>
> Personal AI Infrastructure with Layered Governance

AIUCE is the distilled essence of **Personal AI Infrastructure**, with four core philosophies embedded in an eleven-layer architecture. **A** maps to L0-L10 full-spectrum perception and reasoning. **U** maps to L10's Shadow Universe (Monte Carlo / A/B testing). **C** maps to L0's Supreme Constitution (one-vote veto). **E** maps to L7's gradual evolution (kernel refactoring).

---

## 🎯 Why AIUCE?

### The Problem with AI Today

| Problem | Impact |
|---------|--------|
| ❌ **Black Box** | You cannot understand why AI made a decision |
| ❌ **Unpredictable** | AI evolves in unexpected directions |
| ❌ **No Veto Power** | You cannot stop AI from doing harmful things |
| ❌ **No Memory** | AI forgets context across sessions |
| ❌ **No Accountability** | You cannot trace who made what decision |

### The AIUCE Solution

| Solution | Layer |
|----------|-------|
| ✅ **Constitutional Veto** | L0 — Supreme Constitution with one-vote veto |
| ✅ **Controlled Evolution** | L7 — Conservative but continuous improvement |
| ✅ **Full Audit Trail** | L5 — Every decision is logged and traceable |
| ✅ **Semantic Memory** | L4 — Persistent knowledge across sessions |
| ✅ **11-Layer Governance** | L0–L10 — Checks and balances at every level |

---

## 🏛️ The 11-Layer Architecture

AIUCE implements a unique governance structure inspired by ancient Chinese bureaucratic wisdom:

```
┌─────────────────────────────────────────────────────────────────┐
│  L0  WILL          "Qin Shi Huang"  Emperor's Study            │
│     Sovereignty Gateway + Semantic Gateway                       │
├─────────────────────────────────────────────────────────────────┤
│  L1  IDENTITY       "Zhuge Liang"   Ministry of Rites           │
│     Brain-first entity registry, MECE taxonomy                  │
├─────────────────────────────────────────────────────────────────┤
│  L2  PERCEPTION     "Zhang Liang"   Grand Council              │
│     Multi-format document ingestion, Markdown pipeline           │
├─────────────────────────────────────────────────────────────────┤
│  L3  REASONING      "Zhang Liang"   Grand Council              │
│     Three-level cognitive control + DAG task planning           │
├─────────────────────────────────────────────────────────────────┤
│  L4  MEMORY         "Sima Qian"     Hanlin Academy             │
│     Palace Memory + Code Understanding (AST + Leiden)           │
├─────────────────────────────────────────────────────────────────┤
│  L5  DECISION       "Bao Zheng"     Supreme Court              │
│     Three-domain scoring + hash chain audit                      │
├─────────────────────────────────────────────────────────────────┤
│  L6  EXPERIENCE     "Zeng Guofan"   Ministry of Personnel      │
│     Daily review, pattern recognition, experience accumulation   │
├─────────────────────────────────────────────────────────────────┤
│  L7  EVOLUTION      "Shang Yang"    Secretariat               │
│     GDPVal benchmark + Skill self-evolution                      │
├─────────────────────────────────────────────────────────────────┤
│  L8  INTERFACE      "Zhang Qian"    Ministry of Foreign Affairs│
│     Multi-provider API gateway (OpenAI / Claude / Qwen / DeepSeek)│
├─────────────────────────────────────────────────────────────────┤
│  L9  AGENT          "Han Xin"       Imperial Guard             │
│     Constitutional tool registry + intelligent routing           │
├─────────────────────────────────────────────────────────────────┤
│  L10 SANDBOX        "Zhuangzi"      Astronomical Bureau        │
│     Shadow Universe simulation, Monte Carlo testing              │
└─────────────────────────────────────────────────────────────────┘
```

### Layer Detail

| Layer | Name | Minister | Core Module | Origin | Status |
|-------|------|---------|-----------|--------|--------|
| **L0** | Will | Qin Shi Huang | `l0_sovereignty_gateway.py` | agent-sovereignty-rules | ✅ |
| **L0** | Semantic | Wei Zheng | `l0_semantic_gateway.py` | hermes-agent | ✅ |
| **L0** | Sovereignty | — | `core/sovereignty.py` | PASK Phase 3 | ✅ |
| **L1** | Identity | Zhuge Liang | `l1_identity_brain.py` | gbrain | ✅ |
| **L2** | Perception | Zhang Liang | `l2_document_ingestor.py` | markitdown | ✅ |
| **L2** | IntentFlow | — | `core/intent_flow.py` | PASK DD | ✅ |
| **L3** | Reasoning | Zhang Liang | `l3_cognitive_orchestrator.py` | teonu-worldmodel + deer-flow | ✅ |
| **L4** | Memory | Sima Qian | `l4_palace_memory.py` | mempalace | ✅ |
| **L4** | HybridMemory | — | `core/hybrid_memory.py` | PASK MM | ✅ |
| **L4** | CodeUnderstanding | Sima Qian | `l4_code_understanding.py` | graphify | ✅ |
| **L5** | Decision | Bao Zheng | `l5_audit.py` | ai-governance-framework | ✅ |
| **L6** | Experience | Zeng Guofan | `l6_experience.py` | — | ✅ |
| **L6** | DualProcess | — | `core/dual_process.py` | PASK Phase 2 | ✅ |
| **L7** | Evolution | Shang Yang | `l7_evolution_engine.py` | OpenSpace | ✅ |
| **L8** | Interface | Zhang Qian | `l8_interface.py` | — | ✅ |
| **L9** | Agent | Han Xin | `l9_tool_harness.py` | CLI-Anything + ipipq | ✅ |
| **L9** | AssetCustody | — | `core/asset_custody.py` | PASK Phase 3 | ✅ |
| **L10** | Sandbox | Zhuangzi | `l10_sandbox.py` | — | ✅ |
| **L10** | WorldModel | — | `core/world_model.py` | PASK Phase 1 | ✅ |

**Progress**: 10/10 core layer modules implemented + 6 PASK upgrade modules (**L6 Experience layer completed**)

---

## 🔬 Phase 1–3 Fusion Results

Based on the principle of **"Concept Transfer > Code Reuse"**, we extracted core philosophies from 5 billgaohub projects and 5 external open-source projects, reconstructing them as native AIUCE components.

### Fusion Sources

| Module | Origin | Core Concept |
|--------|--------|-------------|
| L0 SovereigntyGateway | agent-sovereignty-rules | P1-P7 Constitution + Keyword Veto |
| L0 SemanticGateway | hermes-agent | Semantic confidence + Compliance gateway |
| L1 IdentityBrain | gbrain | MECE entity directory + Brain-first query |
| L2 DocumentIngestor | markitdown | Universal Markdown conversion + dual export |
| L3 CognitiveOrchestrator | teonu-worldmodel + deer-flow | Three-level cognitive control + DAG planning |
| L4 PalaceMemory | mempalace | Raw Verbatim + Memory Palace + 96.6% retrieval rate |
| L4 CodeUnderstanding | graphify | AST zero-LLM + Leiden community detection |
| L5 DecisionAudit | ai-governance-framework | Three-domain scoring + hash chain |
| L7 EvolutionEngine | OpenSpace | GDPVal benchmark + Skill self-evolution |
| L9 ToolHarness | CLI-Anything + ipipq | Constitutional registry + intelligent routing |

Full reports:
- [docs/reports/aiuce-billgaohub-fusion-20260414.md](docs/reports/aiuce-billgaohub-fusion-20260414.md) — Phase 1
- [docs/reports/aiuce-billgaohub-fusion-phase2-3-20260414.md](docs/reports/aiuce-billgaohub-fusion-phase2-3-20260414.md) — Phase 2–3

---

## 🚀 PASK + World Model Upgrade (2026)

Inspired by recent research, AIUCE has been upgraded with **proactive agent capabilities** and **world model simulation**.

### Research Basis

| Paper | arXiv | Key Contribution |
|-------|-------|-----------------|
| **PASK** | [2604.08000](https://arxiv.org/abs/2604.08000) | DD-MM-PAS proactive agent paradigm |
| **World Models as Intermediary** | [2602.00785](https://arxiv.org/abs/2602.00785) | T^/R^/G^ world model components |
| **LeWorldModel** | [2603.19312](https://arxiv.org/abs/2603.19312) | Stable end-to-end JEPA + Surprise detection |

### New Core Modules

| Module | File | Description |
|--------|------|-------------|
| **IntentFlow** | `core/intent_flow.py` | Streaming intent detection, latent needs inference |
| **HybridMemory** | `core/hybrid_memory.py` | Workspace/User/Global three-tier memory |
| **WorldModel** | `core/world_model.py` | T^ (dynamics), R^ (reward), G^ (task distribution), Surprise detection |
| **DualProcess** | `core/dual_process.py` | System 1 (Fast) + System 2 (Slow) reflection |
| **Sovereignty** | `core/sovereignty.py` | Data localization, transfer audit, privacy boundary |
| **AssetCustody** | `core/asset_custody.py` | Account abstraction, transaction management |

### Upgrade Highlights

| Layer | Before | After |
|-------|--------|-------|
| **L2 Perception** | Passive intent detection (keywords) | **Streaming IntentFlow** - detects latent needs from context |
| **L3 Reasoning** | Multi-path reasoning (one-shot) | **Streaming reasoning** + HybridMemory integration |
| **L4 Memory** | Flat semantic index | **Three-tier Hybrid** - Workspace/User/Global |
| **L6 Experience** | Daily review, pattern recognition | **Dual Process** - System 1 (fast) + System 2 (slow) |
| **L7 Evolution** | Rule evolution | **L6/L7 linkage** - proposals from deep reflection |
| **L9 Agent** | Tool execution | **Asset Custody** - account/tranaction abstraction |
| **L10 Sandbox** | Monte Carlo simulation | **World Model** - T^/R^/G^ + Surprise detection |

Full upgrade plan: [docs/upgrade-pask-worldmodel.md](docs/upgrade-pask-worldmodel.md)

---

## 🚀 Quick Start

```bash
# Clone
git clone https://github.com/billgaohub/AIUCE.git
cd AIUCE

# Activate virtual environment (Python 3.14)
source .venv/bin/activate

# Run tests
python3 -m pytest tests/test_phase1.py tests/test_phase2.py -v
```

**Initialize memory directories**:

```python
from core.l1_identity_brain import IdentityBrain
from core.l4_palace_memory import PalaceMemory

brain = IdentityBrain()    # ~/.aiuce/brain/
palace = PalaceMemory()   # ~/.aiuce/palace/
```

**Execute cognitive tasks**:

```python
from core.l3_cognitive_orchestrator import CognitiveOrchestrator

oc = CognitiveOrchestrator()
dag = oc.plan("Prepare backup plans if it rains tomorrow")
result = oc.execute(dag)
```

**Audit decisions**:

```python
from core.l5_audit import DecisionAudit, AuditEntry, DecisionType

audit = DecisionAudit()
entry = AuditEntry(
    entry_id="task-001",
    session_id="session-x",
    layer="L3",
    timestamp="2026-04-14T12:00:00",
    decision_type="action",
    intent="Test intent",
    reasoning="Test reasoning",
    output="Test output",
    sovereignty_passed=True,
)
audit.log(entry)
```

---

## ✅ Tests

```
tests/
├── test_phase1.py     # L0/L3/L5/L9 module tests ✅
└── test_phase2.py     # L1/L2/L4/L7 module tests ✅
```

**Run all tests**:

```bash
source .venv/bin/activate
python3 -m pytest tests/test_phase1.py tests/test_phase2.py -v
```

**Result**: `33 passed` — covers all L0–L9 fusion modules

---

## 📡 Multi-Channel Support

| Platform | Status | Capability |
|----------|--------|------------|
| Feishu | ✅ Supported | Send/receive messages, webhook |
| Telegram | ✅ Supported | Bot messages, callback queries, webhook |
| Webhook | ✅ Supported | Custom HTTP callbacks |

See [docs/channels.md](docs/channels.md).

---

## 🔧 Technical Specs

- **Python**: 3.14
- **Core dependencies**: pydantic 2.12.5
- **Optional**: markitdown (doc conversion), ChromaDB (vector search), faster-whisper (audio/video)
- **Virtual environment**: `.venv/` (pre-configured)
- **Test framework**: pytest (33 passing)

---

## 🌐 Multi-Model Support (L8)

| Provider | Model | Status |
|----------|-------|--------|
| OpenAI | GPT-4o / GPT-4o-mini | ✅ |
| Anthropic | Claude 3.5 Sonnet | ✅ |
| Alibaba | Qwen-Plus / Qwen2.5 | ✅ |
| DeepSeek | DeepSeek-Chat | ✅ |
| Local | Ollama (Llama3) | ✅ |
| Local | MLX (Qwen2.5-7B) | ✅ |

---

## 📖 Documentation

| Document | Description |
|----------|-------------|
| [fusion-report-phase1](docs/reports/aiuce-billgaohub-fusion-20260414.md) | Phase 1 fusion report |
| [fusion-report-phase2-3](docs/reports/aiuce-billgaohub-fusion-phase2-3-20260414.md) | Phase 2–3 fusion report |
| [architecture](docs/architecture.md) | 11-layer architecture deep dive |
| [integration](docs/integration.md) | Open-source integration guide |
| [channels](docs/channels.md) | Multi-channel configuration |

---

## 🤝 Related Projects

| Project | Status | Note |
|---------|--------|------|
| [AIUCE](https://github.com/billgaohub/AIUCE) | ✅ Active | Main repo — Personal AI Infrastructure |
| [IPIPQ](https://github.com/billgaohub/ipipq) | ✅ Active | AI file auto-organizer |
| [smart-file-router](https://github.com/billgaohub/smart-file-router) | ✅ Active | Intelligent file classifier (integrated into L9) |

---

## 📜 Architecture Philosophy

> "Governing a large country is like cooking a small fish" — Lao Tzu

AIUCE applies ancient governance wisdom to modern AI:

- **Layered governance** keeps complex systems controllable (L1–L10, each with a role)
- **Checks and balances** prevent any layer from dominating (L0 veto)
- **Audit trails** make every decision traceable (L5 hash chain)
- **Controlled evolution** enables continuous improvement (L7 GDPVal)

---

## 🔐 Security Features

- **API Key Authentication**: All endpoints require `X-API-Key` header
- **Rate Limiting**: 100 req/min (configurable)
- **Execution Sandbox (L9)**: Command whitelist, dangerous pattern detection, timeout limits
- **Risk Classification**: LOW / MEDIUM / HIGH / CRITICAL

---

## 📄 License

MIT License — see [LICENSE](LICENSE)

---

**AIUCE** — Personal AI Infrastructure with Layered Governance  
🏯 *治大国若烹小鲜 · Governing a large country is like cooking a small fish*

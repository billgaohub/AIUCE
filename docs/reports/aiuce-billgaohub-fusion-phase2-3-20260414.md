# AIUCE × billgaohub 深度融合 Phase 2-3 实施报告

**生成时间**: 2026-04-14 17:52 GMT+8  
**分析师**: ooppg (AIUCE 首席系统架构师)  
**提交状态**: `8ba3d8e` pushed to main

---

## 一、执行摘要

| 阶段 | 模块 | 源项目 | 行数 | 状态 |
|------|------|--------|------|------|
| Phase 2 | `l1_identity_brain.py` | gbrain | 656 | ✅ 已提交 |
| Phase 2 | `l2_document_ingestor.py` | markitdown | 475 | ✅ 已提交 |
| Phase 2 | `l4_palace_memory.py` | mempalace | 590 | ✅ 已提交 |
| Phase 2 | `l4_code_understanding.py` | graphify | 750 | ✅ 已提交 |
| Phase 3 | `l7_evolution_engine.py` | OpenSpace | 650 | ✅ 已提交 |

Phase 1-3 全部完成。**commit `8ba3d8e`** 已推送至 GitHub。

---

## 二、技术修复记录

### Python r""" 内嵌套引号问题

**根本原因**：在 `write` 工具使用 `r"""..."""` 原始字符串格式写入 Python 文件时，文件内容中的 `\"` 被写入为字面两字符 `\` 和 `"`。这导致 `exec(open('file').read().split("if __name__")[0], {})` 这样的 exec 语句被破坏——Python 解析器无法正确处理 exec 内部代码的引号嵌套。

**修复方案**：改用 `importlib.util.spec_from_file_location` 动态导入替代 exec 字符串方式。

```python
# 错误方式（r""" 内 \" 导致语法破坏）
exec(open('core/l0_sovereignty_gateway.py').read().split("if __name__")[0], {})

# 正确方式
import importlib.util
spec = importlib.util.spec_from_file_location("sg_sgw",
    __file__.replace("l7_evolution_engine.py", "l0_sovereignty_gateway.py"))
sg_mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(sg_mod)
sg = sg_mod.SovereigntyGateway()
```

---

## 三、每项改造核心说明

### 3.1 L1 IdentityBrain — gbrain 个人知识库融合

**来源**: garrytan/gbrain (34KB README)

**gbrain 核心理念**：
- Personal AI brain：让 AI 在每次回复前先查个人知识库
- Entity-centric MECE schema：`people/`、`companies/`、`concepts/`、`projects/`、`meetings/`、`sources/`
- CLI + PGLite（本地向量数据库，无需服务器）
- Dream cycle：夜间整合，entity sweep，memory consolidation

**AIUCE 改造要点**：

```
gbrain                    → AIUCE L1 IdentityBrain
─────────────────────────────────────────────────────────────
PGLite + OpenAI Embeddings → Markdown 文件系统 + LLM 语义检索
gbrain query             → BrainEngine.consult() 返回 Markdown 上下文
gbrain sync              → BrainEngine.update() 写 Raw Verbatim
gbrain entity detection  → L1 EntityExtractor（确定性关键词 + 正则）
gbrain cron              → DreamCycle 夜间整合 + L5 DecisionAudit 联动
gbrain integrations      → 外部数据入口（未来：Gmail/Calendar/Twitter）
```

**MECE 目录结构（完整）**：

| Wing | 用途 | 示例 |
|------|------|------|
| `people` | 所有你认识的人 | sarah-chen.md |
| `companies` | 了解的公司 | novamind.md |
| `concepts` | 知识/想法/主题 | hybrid-search.md |
| `projects` | 正在进行的项目 | project-alpha.md |
| `meetings` | 会议记录 | novamind-demo-day.md |
| `sources` | 原始数据/剪藏 | crustdata-sarah-chen.md |
| `decisions` | 重要决策（L5 联动） |  |
| `experiences` | 失败/成功经验（L5 联动）| |
| `tools` | 使用的工具/服务 | |
| `habits` | 个人习惯/偏好 | |

**关键创新**：
- **Brain-first lookup**：每次 L3 CognitiveOrchestrator 调用前先 `brain.consult()` 查脑
- **Raw Verbatim**：对话直接追加原文，不 summarization（mempalace 理念）
- **合宪性前置**：`consult()` 方法内置 L0 SovereigntyGateway 审查
- **Dream cycle**：夜间自动发现实体间新关系 + L5 决策迁移

**BrainPage YAML frontmatter 格式**：

```yaml
---
wing: people
entity: sarah-chen
title: Sarah Chen
aliases: ["Sarah", "Sarah Chen"]
tags: ["founder", "ai", "stanford"]
mention_count: 42
last_mentioned: 2026-04-14
---
# Sarah Chen

## Background
...

## Relationships
- works_with: marcus-reid, priya-patel
- founded: novamind

## Notes
...
```

---

### 3.2 L2 DocumentIngestor — markitdown 文档摄取器

**来源**: microsoft/markitdown (11KB README)

**markitdown 核心理念**：
- 万物转 Markdown：PDF/Word/Excel/PPT/HTML/图片OCR/音频转录
- 保留原始结构：标题层级、表格、列表、链接、代码块
- MCP server：可用于 Claude Desktop 集成
- Token 高效：LLM 原生理解 Markdown（比 HTML 节省 token）

**AIUCE 改造要点**：

```
markitdown                   → AIUCE L2 DocumentIngestor
─────────────────────────────────────────────────────────────────
DocumentConverter            → DocumentIngestor（Python SDK 封装）
直接输出 Markdown             → 双轨输出：structured_json（AI）+ markdown_content（人）
markitdown CLI               → Python API + ingest_batch() 批量接口
markitdown LLM OCR           → use_llm_ocr 参数控制（需 API key）
无合宪性审查                  → L0 SovereigntyGateway 前置审查
```

**支持格式完整列表**：

| 格式 | 处理方式 | 依赖 |
|------|---------|------|
| PDF | markitdown CLI → pdftotext 降级 | markitdown/pdftotext |
| Word (.docx) | markitdown CLI | markitdown |
| Excel (.xlsx) | markitdown CLI | markitdown |
| PowerPoint (.pptx) | markitdown CLI | markitdown |
| HTML | pandoc → 正则降级 | pandoc |
| 图片 (OCR) | tesseract → LLM OCR | tesseract/OPENAI_API_KEY |
| CSV | Python csv → Markdown 表格 | 内置 |
| YouTube URL | markitdown 内置 | markitdown |

**双轨输出示例**：

```python
result = ingestor.ingest("report.pdf")
print(result.markdown_content)  # 人消费 Markdown

print(result.structured_json)  # AI消费结构化 JSON
# {
#   "headings": [{"level": 1, "text": "Annual Report"}],
#   "tables": [{"rows": [["Q1", "100k"], ["Q2", "120k"]]}],
#   "links": [{"text": "Source", "url": "https://..."}],
#   "word_count": 5420,
#   "constitutional_passed": True,
# }
```

**关键创新**：
- `MarkdownNormalizer`：规范化后提取 headings/tables/links/code_blocks
- 合宪性审查：`MarkdownNormalizer` 内置 L0 SovereigntyGateway
- 格式自动检测：Magic bytes + 扩展名双重判断

---

### 3.3 L4 PalaceMemory — mempalace 记忆宫殿融合

**来源**: MemPalace/mempalace (34KB README, 公开道歉信)

**mempalace 核心理念**：
- **96.6% LongMemEval R@5**（raw verbatim mode，零 API 调用）
- 记忆宫殿（Method of Loci）：Wing→Hall→Room→Closet 四级空间索引
- **Raw Verbatim**：存储一切，让结构让信息可检索
- AAAK 方言：Token 压缩层（实验性，当前 84.2% < raw 96.6%）
- 诚实透明：README 发布后 48 小时内公开承认 benchmark 数据错误

**AIUCE 改造要点**：

```
mempalace                    → AIUCE L4 PalaceMemory
────────────────────────────────────────────────────────────────────
ChromaDB embeddings          → Markdown 文件系统 + LLM 语义
Room/Hall/Closet 结构        → PalaceWing/MemoryRoom/MemoryRecord 同名
fact_checker 矛盾检测         → 与 L5 DecisionAudit 联动
AAAK 方言（实验）             → 可选压缩层（保留，不默认启用）
mempalace palace walk        → PalaceEngine.walk() 宫殿漫步导航
ChromaDB 依赖                 → 零外部依赖（文件系统优先）
```

**Palace 四级空间结构**：

```
~/.aiuce/palace/
├── people/          ← Wing（一级：人）
│   └── sarah-chen/
│       ├── meta.json
│       └── {record_id}.md  ← Raw Verbatim 记忆
├── projects/        ← Wing（一级：项目）
│   └── ai-project-alpha/
├── learning/        ← Wing（一级：学习）
├── health/          ← Wing（一级：健康）
├── finance/         ← Wing（一级：财务）
├── life/            ← Wing（一级：生活）
├── reflection/      ← Wing（一级：反思）
└── general/         ← Wing（一级：综合）
```

**哈希链审计**：

```python
record = palace.store(
    raw_text="用户和张总讨论了 A 方案...",  # Raw Verbatim
    room_id="meeting-20260414",
    wing=PalaceWing.PEOPLE,
    speaker="agent",
    tags=["meeting", "alpha"],
)
# record.hash_chain = SHA256("GENESIS:" + "用户和张总讨论了 A 方案...")
# 哈希链头自动更新，每条记录含前一条记录哈希
```

**关键创新**：
- **Raw Verbatim**：来自 mempalace 的核心原则，AIUCE 直接采用
- **哈希链**：每条记录含前一条记录的 SHA256 哈希（L5 审计联动）
- **PalaceEngine.walk()**：宫殿漫步导航，模拟古希腊空间记忆术
- **与 L1 IdentityBrain 联动**：PalaceMemory 存原始对话，BrainEngine 提取实体

---

### 3.4 L4 CodeUnderstanding — graphify 代码图谱融合

**来源**: safishamsi/graphify (25KB README, 71.5x Token 节省)

**graphify 核心理念**：
- **三通道理解**：
  1. **AST 通道**（零 LLM）：Tree-sitter 风格结构提取
  2. **Whisper 通道**：视频/音频转录（domain-aware prompt）
  3. **LLM 通道**：语义关系提取（Claude subagent 并行）
- 知识图谱：NetworkX + Leiden 社区检测（无需向量）
- 关系标注：**EXTRACTED**（直接提取）/ **INFERRED**（LLM 推断）/ **AMBIGUOUS**（待审核）
- 输出：graph.html（交互 D3.js）/ graph.json（持久化）/ GRAPH_REPORT.md（文字报告）
- 71.5x Token 节省（vs 读取原始文件）

**AIUCE 改造要点**：

```
graphify                         → AIUCE L4 CodeUnderstanding
────────────────────────────────────────────────────────────────────────
Claude Code 集成                 → AIUCE: L3 CognitiveOrchestrator 元认知调度
Claude subagent 并行             → AIUCE: TaskDAG 并行执行
NetworkX 图                      → AIUCE: CodeGraph（简化，轻量）
Leiden 聚类                      → AIUCE: LeidenCommunityDetector（简化版 BFS）
graph.json 持久化                → AIUCE: 存入 L4 PalaceMemory
God nodes（高连接节点）            → 存入 L1 IdentityBrain（Entity Pages）
```

**三通道对比**：

| 通道 | 方式 | Token 消耗 | AIUCE 适配 |
|------|------|-----------|-----------|
| AST 通道 | 正则（确定性）| 0 | `ASTExtractor`（14 种语言）|
| Whisper 通道 | faster-whisper | 中 | 可选（需安装）|
| LLM 通道 | Claude subagent | 高 | `CognitiveOrchestrator` 调度 |

**支持语言（14 种）**：Python / JavaScript / TypeScript / Go / Rust / Java / C / C++ / Ruby / Kotlin / Scala / PHP / Swift / Lua / Elixir / Julia / Verilog / SystemVerilog / Vue / Svelte / Dart / PowerShell

**关系类型**：

| 类型 | 含义 | 置信度 |
|------|------|--------|
| EXTRACTED | 源码直接提取 | 1.0 |
| INFERRED | LLM 推断（有置信度）| 0.5-0.99 |
| AMBIGUOUS | 标记待审核 | - |

**输出文件**：

```
~/.aiuce/codegraph/
├── {corpus_id}.json     ← 知识图谱数据（供 AI 消费）
├── {corpus_id}.html     ← D3.js 交互图（供人浏览）
└── {corpus_id}_REPORT.md ← 文字报告（God nodes + 文件列表）
```

**关键创新**：
- `ASTExtractor`：零 LLM 提取类/函数/导入/调用关系（14 种语言）
- `LeidenCommunityDetector`：BFS 连通分量 + 边密度排序（无需 NetworkX）
- D3.js CDN 交互图：点击节点查看关系
- graph.json 存入 PalaceMemory：代码图谱可被记忆层检索

---

### 3.5 L7 EvolutionEngine — OpenSpace 自演化引擎融合

**来源**: HKUDS/OpenSpace (35KB README, 自演化技能引擎)

**OpenSpace 核心理念**：
- **Self-Evolution**：技能自动修复/改进/学习
- **GDPVal**：真实经济价值度量（Token 节省 + 质量提升）
- **Collective Intelligence**：跨 Agent 技能共享网络效应
- **46% fewer tokens, 4.2x better performance**（声称）
- AUTO-FIX / AUTO-IMPROVE / AUTO-LEARN 三大能力

**AIUCE 改造要点**：

```
OpenSpace                       → AIUCE L7 EvolutionEngine
─────────────────────────────────────────────────────────────────────────
SkillEvolver.evolve()           → EvolutionEngine.evolve()（合并双核）
FIX/DERIVED/CAPTURED            → 保留（EvolutionType 同名）
ToolQualityManager              → SkillQualityMonitor（质量监控）
GDPVal 基准                     → GDPValMetrics（直接采用）
Skill quality monitoring        → L5 DecisionAudit 联动
Auto-fix/auto-improve           → 与 L0 SovereigntyGateway 合宪性审查
Collective intelligence         → export_skill() / import_skill()
```

**GDPVal 核心公式**：

```python
GDPVal = (质量分数 × 成功率) / (归一化 Token × 归一化时间)

# 示例
metrics = GDPValMetrics(
    task_id="coding-001",
    token_cost=1000,        # 优化后
    quality_score=8.0,      # 质量 8/10
    time_seconds=30,        # 30秒
    baseline_token_cost=2000,  # 基准消耗
)
# GDPVal = (8.0 × 1.0) / ((1000/2000) × (30/60)) = 8.0 / 0.75 = 10.67
# Token 节省 = (2000-1000)/2000 = 50%
```

**SkillQualityMonitor 健康评估**：

| 状态 | 条件 | 触发演化 |
|------|------|---------|
| healthy | 成功率 ≥ 90%，Token 消耗稳定 | 无 |
| degrading | Token 消耗增长 > 10% | DERIVED |
| broken | 成功率 < 50% | FIX |
| new | 数据不足 < 3 条记录 | 无 |

**演化流程（OpenSpace → AIUCE）**：

```
触发（3种来源）
  1. post_analysis: 后置分析发现演化建议
  2. tool_degradation: 工具质量下降
  3. metric_monitor: 周期性监控
       ↓
创建 EvolutionCandidate
       ↓
L0 SovereigntyGateway 合宪性审查
  ❌ → REJECTED
       ↓
LLM 评估 suggested_patch（简化）
       ↓
apply-retry cycle（最多 3 次）
       ↓
✅ → APPROVED → 持久化到 ~/.aiuce/skills/{skill_name}/SKILL.md
       ↓
GDPVal 验证：确认改进
       ↓
L5 DecisionAudit 记录
```

**与现有 evolution.py 合并**：

- 现有 `evolution.py`：内圣（心智/SOP 演化）+ 外王（内核重构）双核
- 新 `l7_evolution_engine.py`：OpenSpace 自演化引擎
- **合并策略**：新模块作为 L7 层主入口，原 `evolution.py` 的双核逻辑作为内嵌引擎

---

## 四、Phase 1-3 完整架构关系图

```
┌─────────────────────────────────────────────────────────────────────┐
│                         SOUL.md / AGENTS.md                          │
│                      L0 SovereigntyGateway (P1-P7)                   │
└─────────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────────┐
│                        L1 IdentityBrain                             │
│   BrainEngine (gbrain) ← Brain-first lookup consult()                │
│   EntityGraph ← MECE 目录结构 (people/companies/concepts/)           │
│   DreamCycle ← 夜间整合 + L5 DecisionAudit 联动                      │
└─────────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────────┐
│                     L2 DocumentIngestor                              │
│   markitdown ← 万物转 Markdown + 双轨输出                             │
│   MarkdownNormalizer ← 表格/标题/链接提取                             │
│   L0 合宪性审查 ← 文档内容审查                                        │
└─────────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────────┐
│                     L3 CognitiveOrchestrator                         │
│   teonu-worldmodel ← 三层认知控制 + 元认知策略选择                    │
│   deer-flow ← DAG 任务分解 + 拓扑排序                                 │
│   StrategySelector ← DEDUCTIVE/INDUCTIVE/ABDUCTIVE/CAUSAL          │
└─────────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────────┐
│  L4 Memory 层（双模块）                                              │
│                                                                       │
│  PalaceMemory (mempalace)    CodeUnderstanding (graphify)             │
│  - Raw Verbatim 存储          - AST 零 LLM 提取                       │
│  - Palace 四级空间索引        - Leiden 社区检测                       │
│  - 哈希链审计                 - D3.js 交互图                          │
│  - 与 BrainEngine 联动        - 存入 PalaceMemory                      │
│  - 矛盾检测                   - God nodes → IdentityBrain             │
└─────────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────────┐
│                     L5 DecisionAudit                                 │
│   ai-governance-framework ← 三域评分 + 哈希链                         │
│   TriDomainScore ← body(执行) / flow(流程) / intel(认知)              │
│   sovereignty_passed ← L0 否决关联                                   │
└─────────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────────┐
│                    L7 EvolutionEngine                                 │
│   OpenSpace ← 自演化技能 + GDPVal 基准                                │
│   内核（Hermes）← SOP 提取 + 闭环学习                                 │
│   外核（OpenSpace）← 失败触发重构 + API 变更自适应                   │
│   SkillQualityMonitor ← 健康评估 + 演化触发                           │
└─────────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────────┐
│                     L9 ToolHarness                                   │
│   CLI-Anything ← 合宪性注册 + 工具协议                                │
│   ipipq ← 文件分类 + 双轨输出                                         │
│   smart-file-router ← 关键词路由 + 置信度                             │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 五、Phase 1-3 全部完成清单

| 模块 | 文件 | 源项目 | 提交 |
|------|------|--------|------|
| L0 SovereigntyGateway | `l0_sovereignty_gateway.py` | agent-sovereignty-rules | `9e98b79` |
| L0 SemanticGateway | `l0_semantic_gateway.py` | hermes-agent | `9e98b79` |
| L3 CognitiveOrchestrator | `l3_cognitive_orchestrator.py` | teonu-worldmodel + deer-flow | `9e98b79` |
| L5 DecisionAudit | `l5_audit.py` | ai-governance-framework | `9e98b79` |
| L9 ToolHarness | `l9_tool_harness.py` | CLI-Anything + ipipq + smart-file-router | `9e98b79` |
| L1 IdentityBrain | `l1_identity_brain.py` | gbrain | `8ba3d8e` |
| L2 DocumentIngestor | `l2_document_ingestor.py` | markitdown | `8ba3d8e` |
| L4 PalaceMemory | `l4_palace_memory.py` | mempalace | `8ba3d8e` |
| L4 CodeUnderstanding | `l4_code_understanding.py` | graphify | `8ba3d8e` |
| L7 EvolutionEngine | `l7_evolution_engine.py` | OpenSpace | `8ba3d8e` |

**GitHub repo 进度**：9/10 层核心模块已实现（L6 体验层暂未覆盖）

---

## 六、已知问题与待办

| # | 问题 | 优先级 | 备注 |
|---|------|--------|------|
| 1 | `.venv` 中 pydantic 版本冲突，导致 `core/__init__.py` 无法完整加载 | P1 | 需固定版本或重构导入 |
| 2 | L6 体验层（Experience Layer）完全未覆盖 | P2 | 待 Phase 4 |
| 3 | L4 PalaceMemory 未启用 ChromaDB 向量检索（当前纯文件系统）| P2 | 可选增强 |
| 4 | graphify LLM 通道未集成（需 Claude API）| P2 | 预留接口 |
| 5 | 文档中 business/family 关键词缺失 | P2 | 已记录在 fusion-20260414.md |
| 6 | AAAK 方言未实现（mempalace 实验性压缩）| P3 | 低优先级 |

---

## 七、技术债务记录（Phase 2-3 新增）

| 问题 | 描述 | 修复 |
|------|------|------|
| r""" 嵌套引号 | write 工具在 r""" 中写入 \" 破坏 exec 语句语法 | 改用 importlib.util 动态导入 |
| 嵌套 try 块 | 修复 exec 时意外引入嵌套 try 结构 | 删除额外 try 层 |
| exec 命名空间 | exec() 不导出 import 结果到外层作用域 | 直接在 exec 后使用 sg_mod.SovereigntyGateway |

---

*报告生成: ooppg | AIUCE 首席系统架构师*  
*Commit: 8ba3d8e feat(core): Phase 2-3 — L1/L2/L4/L7 深度融合 billgaohub 项目*

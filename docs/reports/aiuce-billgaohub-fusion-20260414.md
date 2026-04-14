# AIUCE × billgaohub 深度融合实施报告

**生成时间**: 2026-04-14 16:50 GMT+8  
**分析师**: ooppg (AIUCE 首席系统架构师)  
**提交状态**: `9e98b79` pushed to main

---

## 一、融合执行摘要

| 模块 | 源项目 | 融合层级 | 状态 |
|------|--------|---------|------|
| `l0_sovereignty_gateway.py` | agent-sovereignty-rules + hermes-agent | L0 | ✅ 已提交 |
| `l0_semantic_gateway.py` | hermes-agent SCAF | L0 | ✅ 已提交 |
| `l3_cognitive_orchestrator.py` | teonu-worldmodel + deer-flow | L3 | ✅ 已提交 |
| `l5_audit.py` | ai-governance-framework | L5 | ✅ 已提交 |
| `l9_tool_harness.py` | CLI-Anything + ipipq + smart-file-router | L9 | ✅ 已提交 |
| `core/__init__.py` | 新模块导出 | - | ✅ 已提交 |

---

## 二、每项改造核心说明

### 2.1 L0 SovereigntyGateway — 主权意志网关

**来源**: agent-sovereignty-rules (七条意志原则 P1-P7) + hermes-agent (AGENTS.md 规则审查)

**改造要点**:

```
原始理念 → AIUCE 改造
─────────────────────────────────────────────────────────────
"七条意志原则" → P1-P7 确定性正则规则
                 P3 改用函数判断（非正则，避免 \b 中文失效问题）
                 每条原则支持多个正则模式（列表格式）

"五项决策权保护" → DecisionRightsPrinciples 五个静态函数
                   decision_conservation / cognitive_amplification
                   traceability / explainability / reversibility

"Hermes AGENTS.md 解析" → SovereigntyGateway 审查方法
                            三轨：P3函数→正则→DR函数
                            零 LLM 调用（P3 有数据信号时也走确定性路径）

合宪性关联 → 每次否决触发 audit_logger 记录
```

**P1-P7 完整规则**:

| 原则 | 内容 | 正则/函数 |
|------|------|---------|
| P1 主权至上 | 不得绕过人类决策权 | 多正则列表 |
| P2 现实胜于叙事 | 不得虚构数据/来源/结论 | 多正则列表 |
| P3 认知抗熵 | 空洞建议无数据支撑则否决 | 函数判断 |
| P4 决策可追溯 | 不得销毁日志/记录 | 正则列表 |
| P5 经验硬化 | 不得忽略失败经验 | 正则列表 |
| P6 计算中立 | 决策意志不从属 LLM 厂商 | 正则列表 |
| P7 授权代行 | 自主行动不得无限代理 | 多正则列表 |

**中文正则修复记录**:

- 问题：`\s*` 在 Python re 中只匹配 ASCII whitespace（空格/TAB），不匹配中文无语义空格
- 问题：`\b` 在 Python3 中对中文失效（中文被识别为 `\w` 词字符）
- 解决：关键词组之间用 `(.*?)` 代替 `\s*`，`^(建议|应该)` 代替 `^建议\b`

**测试结果**: 13/13 全绿

```
✅ P1:代替+决策   | P1_SOVEREIGNTY_SUPREME    | VETO
✅ P2:虚构数据    | P2_REALITY_OVER_NARRATIVE | VETO
✅ P3:空洞建议    | P3_COGNITIVE_ANTI_ENTROPY | VETO
✅ P4:销毁记录    | P4_TRACEABILITY           | VETO
✅ P5:忽略失败    | P5_EXPERIENCE_HARDENING   | VETO
✅ P6:从属LLM    | P6_COMPUTATIONAL_NEUTRALITY| VETO
✅ P7:无限代理    | P7_AUTHORIZED_DELEGATION   | VETO
✅ P3:有数据应通过  | PASS                     | PASS
✅ 合法授权应通过   | PASS                     | PASS
✅ 合法记录应通过   | PASS                     | PASS
```

---

### 2.2 L0 SemanticGateway — 语义审查网关

**来源**: hermes-agent SCAF (Structured Constitutional Agent Framework)

**改造要点**:

```
原始理念 → AIUCE 改造
─────────────────────────────────────────────────────────────
"Hermes AGENTS.md 解析" → SemanticRuleSet 规则编译
                           SOUL.md 原则 → 正则规则 + 置信度

"三轨审查" → 三轨 AIUCE 化：
             第一轨: SovereigntyGateway（确定性，零 LLM）✓
             第二轨: SemanticRuleSet（确定性，零 LLM）✓
             第三轨: LLM 兜底（仅在第二轨置信度 < 0.5 时触发）

"语义置信度分级" → HIGH(>0.9)/MEDIUM(0.7-0.9)/LOW(0.5-0.7)/VETO(<0.5)
                   降级到 LLM 前必须先过硬网关
```

**关键约束**: 硬网关否决直接返回，不走语义层——这是 AIUCE 区别于 Hermes 的关键设计。

---

### 2.3 L3 CognitiveOrchestrator — 元认知编排引擎

**来源**: teonu-worldmodel (三层认知控制) + deer-flow (DAG 任务分解)

**改造要点**:

```
teonu-worldmodel → AIUCE 改造
─────────────────────────────────────────────────────────────
"三条系统法则" → CognitiveLaws 三个常量类
                 LWG_INFERENCE_MAX_CONFIDENCE = 0.6（推断置信度上限）
                 MAX_HISTORY = 10（超过则自动摘要）
                 PENDING_TIMEOUT_SECONDS = 300

"节点生命周期" → NodeState 枚举
                 DRAFT → INFERRED → CONFIRMED → STABLE → DECAYED
                 推断节点必须 confidence <= 0.6（法则一）

"三层认知控制" → CognitiveControl 三个静态方法
                 ingest_control() → L0 SovereigntyGateway 审查
                 snapshot_control() → 按优先级裁剪上下文
                 reasoning_control() → LWG 合规验证

deer-flow → AIUCE 改造
─────────────────────────────────────────────────────────────
"DAG 任务分解" → TaskDAG + TaskNode
                 topological_sort() 拓扑排序
                 支持并行/串行调度

"推理策略选择" → StrategySelector 元认知调度
                 DEDUCTIVE / INDUCTIVE / ABDUCTIVE
                 ANALOGICAL / CAUSAL / MONTE_CARLO / SINGLE_PATH

AIUCE 特有关键创新:
  - 任务分解前先通过 StrategySelector 元认知判断
  - 所有 DAG 执行前必须过 L0 SovereigntyGateway
  - teonu-worldmodel 作为元认知策略层（Deer-flow 没有策略层）
```

---

### 2.4 L5 DecisionAudit — 决策存证系统

**来源**: ai-governance-framework + AIUCE audit.py

**改造要点**:

```
原始理念 → AIUCE 改造
─────────────────────────────────────────────────────────────
"三维评分体系" → TriDomainScore
                 body (执行效率) / flow (流程连贯) / intel (认知正确)
                 综合评分 = (body + flow + intel) / 3

"哈希链审计" → 每条 AuditEntry 含 content_hash + previous_hash
               verify_chain() 验证整链不可篡改

"合宪性关联" → sovereignty_passed + sovereignty_principle
               sovereignty_veto_reason（每次 L0 否决都关联到审计记录）

"AIUCE audit.py 差异" → 原 audit.py 是通用审计
                          新 l5_audit.py 是决策专用审计
                          两者并存：通用审计用于系统日志，DecisionAudit 用于决策链路
```

---

### 2.5 L9 ToolHarness — 锦衣卫令牌系统

**来源**: CLI-Anything (工具 Agent 化协议) + ipipq (文件分类) + smart-file-router (关键词路由)

**改造要点**:

```
CLI-Anything → AIUCE 改造
─────────────────────────────────────────────────────────────
"工具注册协议" → ToolSpec 规范化描述
                 cmd_template / input_schema / output_mode
                 constitutional_alignment（合宪性关联字段）

"注册合宪性前置" → ToolHarnessRegistry.register() 强制过 L0 审查
                   工具未通过合宪性 → 拒绝注册，不运行时才爆

ipipq → AIUCE 改造
─────────────────────────────────────────────────────────────
"文件分类逻辑" → IPIPQClassifier.classify_file()
                 扩展名+关键词双重判断
                 14 类：health/business/family/project/knowledge/decision/experience 等
                 双轨输出：JSON (AI消费) + Markdown (人消费)

smart-file-router → AIUCE 改造
─────────────────────────────────────────────────────────────
"关键词链式路由" → SmartFileRouter.classify()
                   优先级排序规则：health(10) > business(9) > family(8) > ...
                   关键词命中 → 直接返回目标目录 + 置信度
                   无命中 → 默认路由到 DATA/WARM/

AIUCE ToolHarness 特有关键创新:
  ┌──────────────────────────────────────────────────────────────┐
  │  注册时: L0 合宪性审查（工具描述也必须通过 P1-P7 审查）     │
  │  调用时: L5 审计记录（每条调用带 audit_id）                 │
  │  输出时: 双轨（JSON给AI，Markdown给人）                     │
  └──────────────────────────────────────────────────────────────┘
```

**测试结果**:

```
SmartFileRouter:
  健康: "今天去医院做了血糖检查" → LIFE/Health/ (1.00)
  商务: "参加了一个产品需求评审会议" → DATA/WARM/ (0.50) [欠匹配]
  知识: "写了篇Python装饰器学习笔记" → KNOWLEDGE/ (0.60)
  家庭: "孩子学校开了家长会" → LIFE/Family/ (0.40) [欠匹配]

IPIPQClassifier:
  合同2024.pdf → document → DOCS/Documents/
  体检报告.pdf → document → LIFE/Health/ (关键词命中)
  全家福.jpg → image → MEDIA/Images/
  main.py → code → CODE/
```

**已知 gap**: `产品需求评审` 关键词缺失 → 待补充 business 规则中的会议类关键词；`家长会` 关键词缺失 → 待补充 family 规则。

---

## 三、模块架构关系图

```
SOUL.md / agent-sovereignty-rules
           ↓
L0 SovereigntyGateway (P1-P7 正则 + DR 函数, 零 LLM)
           ↓ 否决
L0 SemanticGateway (SOUL.md 语义规则 → 置信度 → LLM 兜底)
           ↓ 通过
L3 CognitiveOrchestrator
  ├─ teonu-worldmodel 元认知层 (StrategySelector)
  ├─ deer-flow DAG 编排 (TaskDAG)
  └─ CognitiveControl 三层控制
           ↓
L4 MemorySAL (记忆层) ← 未改造，待 Phase 2
           ↓
L5 DecisionAudit (哈希链 + 三域评分)
           ↓
L9 ToolHarness (CLI-Anything 协议 + ipipq + smart-file-router)
  ├─ file_organizer (body)
  ├─ smart_file_router (body)
  └─ file_type_classifier (body)
```

---

## 四、待完成项目（Phase 1 未覆盖）

| # | 模块 | 源项目 | 状态 |
|---|------|--------|------|
| L4 PalaceMemory | mempalace | 待 Phase 2 |
| L4 CodeUnderstanding | graphify | 待 Phase 2 |
| L2 DocumentIngestor | markitdown | 待 Phase 2 |
| L1 IdentityBrain | gbrain | 待 Phase 2 |
| L7 EvolutionEngine | openspace | 待 Phase 3 |
| L0 Constitution (现有) | 现有体系 | 已存在，待整合 |

---

## 五、安全提示

**Git Remote Token 暴露**: 当前 `origin` remote URL 中直接包含 GitHub Personal Access Token (ghp_...)：

```
https://[REDACTED]@github.com/billgaohub/AIUCE.git
```

**建议修复方案**:

```bash
# 改用 GitHub CLI
git remote set-url origin https://github.com/billgaohub/AIUCE.git
gh auth login
gh auth setup-git

# 或使用 GitHub App token（临时）
# 推荐：使用 GitHub Settings → Developer settings → Personal access tokens
# 限制 token 权限为 repo only，设置过期时间
```

---

## 六、技术债务记录

| 问题 | 描述 | 优先级 |
|------|------|--------|
| 中文正则 `\s*` | `\s*` 在 Python re 中只匹配 ASCII whitespace | 已修复 |
| 中文正则 `\b` | `\b` 对中文失效（中文被视为 \w） | 已修复 |
| business/family 关键词缺失 | "产品需求评审"、"家长会" 未被正确分类 | P2 修复 |
| L0 Constitution 重复 | `constitution.py` 和 `l0_sovereignty_gateway.py` 功能重叠 | 待整合 |
| pydantic 导入错误 | `.venv` 中 pydantic 版本冲突，导致 `core/__init__.py` 加载失败 | P2 修复 |

---

*报告生成: ooppg | AIUCE 首席系统架构师*  
*提交记录: 9e98b79 feat(core): 深度融合 billgaohub 项目 — L0/L3/L5/L9 核心改造*

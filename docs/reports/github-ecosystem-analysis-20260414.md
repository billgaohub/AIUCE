# AIUCE 开源生态深度改造融合报告

**生成时间**: 2026-04-14 16:35 GMT+8  
**分析师**: ooppg (AIUCE 首席系统架构师)  
**核心原则**: 不套用，不嵌入，只提取理念，改写为 AIUCE 原生组件  
**数据来源**: GitHub API (live) + 源码分析

---

## 一、改造哲学框架

"深度适配"意味着三层拆解：

1. **理念层** — 这个项目解决什么根本问题？AIUCE 的等价问题是什么？
2. **机制层** — 它用了什么机制来实现？AIUCE 的架构能否用同样机制但不同实现？
3. **代码层** — 哪些模块需要重写？哪些可以直接移植？

---

## 二、逐项深度改造方案

---

### 2.1 Hermes Agent → AIUCE L0 "司马迁手记"语义审计引擎

**原始项目**: NousResearch/hermes-agent ★80842  
**原始定位**: 自演进 Agent，AGENTS.md 规则，技能自创，跨会话记忆

#### 2.1.1 理念拆解

Hermes 的核心不是"又一个 Agent"，而是**"用文件约束 AI 行为"**这一元问题：
- 写入 AGENTS.md = 写入宪法
- AI 读取 AGENTS.md = 合宪性审查
- 技能自创 = 从经验中抽取 SOP，写回 AGENTS.md

这与 AIUCE L0 的设计哲学**完全同构**：AIUCE 用代码写硬网关 + 软网关做合宪检查，Hermes 用 Markdown 文件做规则约束 + LLM 解读。

**AIUCE 改造方向**：不是把 Hermes 接入 L0，而是将 **Hermes 的"文件规则→Agent行为约束"机制移植为 AIUCE 的 L0 语义网关层**，用 AIUCE 的 SOUL.md / IDENTITY.md / AGENTS.md 替代 Hermes 的规则格式。

#### 2.1.2 具体改造

```
现有: constitution.py 的软网关依赖 LLM 概率判断
改造: 提取 Hermes 的 AGENTS.md 解析器 + LLM 双轨审查逻辑
      → 重写为 L0/SemanticGateway 类，读 SOUL.md / agent-sovereignty-rules 原文
```

**伪代码改造**:

```python
# L0/semantic_gateway.py（重写自 Hermes SCAF 机制）
class SemanticGateway:
    """
    改造自 Hermes Agent 的 AGENTS.md 规则审查机制。
    不依赖 Hermes 本身，只提取其核心理念：
    "用人类可读文件约束 AI 行为，并在执行中持续校验"
    """

    def __init__(self, soul_path: str, sovereignty_rules_path: str):
        # 读取 AIUCE 原生文件作为语义约束源
        self.rules = self._load_sovereignty_rules(sovereignty_rules_path)
        self.principles = self._load_soul_principles(soul_path)

    def audit(self, intent: str) -> VetoResult:
        # 第一轨: 确定性关键词匹配（硬网关逻辑，零 LLM 调用）
        hard_match = self._keyword_veto(intent)
        if hard_match:
            return hard_match  # 立即否决，不调用 LLM

        # 第二轨: 语义层合宪性检查（改造自 Hermes 意图审查）
        constitutional = self._hermes_style_semantic_check(
            intent,
            rules=self.rules,      # agent-sovereignty-rules 五原则注入
            soul=self.principles   # SOUL.md 语义注入
        )

        # 第三轨: LLM 概率判断（仅在第二轨不确定时触发）
        if constitutional.confidence < 0.8:
            return self._llm_judgment(intent)  # 兜底调用
        return constitutional
```

**改造要点**:
- 不引入 hermes-agent 依赖包，只学习其"AGENTS.md → 行为约束"机制
- `agent-sovereignty-rules` 的五项原则（守恒、放大、可追溯、可解释、可反转）作为语义审查规则注入源
- 零 LLM 调用的硬网关优先，减少 token 消耗

#### 2.1.3 billgaohub 协同改造

`agent-sovereignty-rules` 的五项原则不应只存在于文档，而应成为 SemanticGateway 的确定性校验规则：

```python
# AIUCE L0 层内置的五项决策权原则（直接来自 agent-sovereignty-rules）
SOVEREIGNTY_RULES = {
    "decision_conservation": r"(转移|外包|放弃)\s*(决策|决定权)",  # 不能转移决策权
    "cognitive_amplification": r"(放大|增强|提升)\s*(认知|判断力)",  # 只放大，不替代
    "traceability": r"(不留痕迹|销毁|删除)\s*(记录|日志|审计)",     # 所有决策可追溯
    "explainability": r"(无需解释|不解释|黑箱)",                     # 决策可解释
    "reversibility": r"(不可逆|无法撤回)",                          # 输出可反转
}
```

---

### 2.2 MemPalace → AIUCE L4 "翰林院藏书阁"记忆体系

**原始项目**: MemPalace/mempalace ★45195  
**原始定位**: 记忆宫殿空间索引，Raw verbatim 存储，Wing/Hall/Room 三级结构

#### 2.2.1 理念拆解

MemPalace 的核心创新不是"用了 ChromaDB"，而是**两个反共识的设计决策**：
1. **不摘要，只存储原文** — 其他系统让 LLM 决定什么是重要的，结果损失了上下文；MemPalace 直接存原始对话
2. **空间结构而非平面索引** — "记忆宫殿"的三级空间（wing=对象、hall=类型、room=主题）比向量搜索更能捕捉语义层级

**AIUCE 改造方向**：将"记忆宫殿"的空间索引理念嫁接于 AIUCE L4 的 `memory_sal.py`，用 AIUCE 的 Layer/Category 体系替代 MemPalace 的 Wing/Hall/Room 命名，同时保留 Raw verbatim 原则。

#### 2.2.2 具体改造

```
现有: memory_sal.py 用 DAG 压缩 + FTS5 检索
改造: 新增 PalaceMemoryEngine，Raw verbatim 优先 + 三级空间索引
      Wing → AIUCE Layer（L0-L10）
      Hall → MemoryCategory（Body/Flow/Intel）
      Room → 语义簇（具体主题）
```

**改造要点**: 不是用 MemPalace 替换 L4，而是将 L4 记忆层改造为双引擎架构：

```python
# L4/memory_sal.py 新增（改造自 MemPalace 理念）

class PalaceMemoryEngine:
    """
    改造自 MemPalace 的记忆宫殿理念。
    核心理念移植：
    1. Raw verbatim 存储（不做摘要，不烧 LLM）
    2. 三级空间索引替代平面向量检索
    3. 用 AIUCE 的 Layer/Category 体系替代 Wing/Hall/Room 命名

    AIUCE 适配：
    - Wing  → Layer 层级（L0意志...L10沙盒）
    - Hall  → Body/Flow/Intel 三域
    - Room  → 语义主题簇
    """

    def __init__(self, vector_store=None):
        self.raw_storage = RawVerbatimStore()  # 改造自 MemPalace: 不摘要
        self.spatial_index = SpatialIndex()       # 改造自: 空间索引而非纯向量
        self.layer_map = LAYER_TO_DOMAIN_MAP      # AIUCE 特有的层级映射

    def memorize(self, entry: MemoryEntry) -> MemoryID:
        # 第一步: Raw verbatim 存入（100%保留，无损失）
        raw_id = self.raw_storage.store(entry.content)

        # 第二步: 空间索引（改造自 MemPalace 的 Wing/Hall/Room）
        # Wing = 本次交互涉及的 AIUCE 层级（L0-L10）
        # Hall = 三域分类（Body=工具执行/Flow=流程/I=认知）
        # Room = 语义簇（自动聚类）
        spatial_id = self.spatial_index.place(
            raw_id=raw_id,
            wing=self._detect_layer(entry),       # AIUCE 层检测
            hall=self._detect_domain(entry),       # 三域分类
            room=self._semantic_cluster(entry)     # 语义主题
        )
        return spatial_id

    def recall(self, query: str, layers: List[Layer]) -> List[MemoryEntry]:
        # 空间感知识索：沿着 Layer 层级向上遍历
        results = []
        for layer in layers:
            results += self.spatial_index.query(layer=layer, query=query)
        return self._rank_by_recency_and_relevance(results)
```

**改造要点**:
- 不引入 mempalace 依赖，只用 ChromaDB 做向量存储（AIUCE 原生依赖）
- 核心改造：**去掉摘要层**，直接 Raw verbatim，节省 LLM token
- 空间索引的"导航感"：AIUCE 用户可沿 L0→L10 层级"参观"记忆，而非平面搜索

---

### 2.3 OpenSpace → AIUCE L6/L7 "商鞅变法"自演化引擎

**原始项目**: HKUDS/OpenSpace ★5164  
**原始定位**: One command 演化所有 Agent，GDPVal 基准，AUTO-FIX，技能自提取

#### 2.3.1 理念拆解

OpenSpace 的核心不是"一个演化工具"，而是**"把成功操作轨迹变成可复用技能"**：
- 完成任务后，提取操作轨迹（SOP）
- 给 SOP 打分（GDPVal）
- 不好用 → AUTO-FIX 自动修改 SOP
- 好用 → 固化为技能，进入技能库

这与 AIUCE L6（经验层/复盘）和 L7（演化层/内核变法）的设计**高度同构**，只是实现路径不同。

**AIUCE 改造方向**：将 OpenSpace 的"轨迹→SOP→评分→AUTO-FIX"闭环，重写为 AIUCE L6/L7 的内环/外环演化逻辑，用 `evolution.py` 的双核架构承接。

#### 2.3.2 具体改造

```
现有: evolution.py 的内环/外环设计为空壳，缺少具体算法
改造: 引入 OpenSpace 的"轨迹提取→SOP生成→GDPVal评分→AUTO-FIX"四步闭环
```

**改造要点**:

```python
# L7/evolution_engine.py（改造自 OpenSpace 机制）

class EvolutionEngine:
    """
    改造自 OpenSpace 的自演化机制。
    核心理念移植：
    1. 轨迹提取：从 L9 执行日志中提取操作序列
    2. SOP 生成：将轨迹抽象为可复用步骤
    3. GDPVal 评分：用 AIUCE 的 Body/Flow/Intel 三域评估
    4. AUTO-FIX：失败时自动改写 SOP

    AIUCE 特有改造：
    - 引入 teonu-worldmodel 的元认知层作为"演化方向判断"
    - L6 内环处理心智演化（用户偏好学习）
    - L7 外环处理物理演化（API 变更/规则重构）
    """

    def on_task_complete(self, execution_log: ExecutionLog):
        # 第一步: 轨迹提取（改造自 OpenSpace 的 skill extraction）
        trajectory = self._extract_trajectory(execution_log)

        # 第二步: SOP 生成（改造自 OpenSpace 的 skill authoring）
        sop = self._author_sop(trajectory)  # LLM 抽象化

        # 第三步: GDPVal 评分（改造为 AIUCE 三域评分）
        score = self._aiuce_score(sop,
            body=self._measure_body_quality(execution_log),    # 执行效率
            flow=self._measure_flow_quality(execution_log),    # 流程连贯性
            intel=self._measure_intel_quality(execution_log)    # 认知正确性
        )

        # 第四步: 分支处理
        if score < THRESHOLD:
            self._auto_fix(sop, execution_log)  # AUTO-FIX（改造自 OpenSpace）
        else:
            self._promote_to_skill(sop)           # 固化进 skill library

    def _auto_fix(self, sop: SOP, failure_log: ExecutionLog):
        """
        改造自 OpenSpace 的 AUTO-FIX 机制。
        不同于 OpenSpace 的通用修复：AIUCE 的 AUTO-FIX 受 L0 宪法约束，
        每次修复尝试都必须通过合宪性网关审查，防止"为了修bug而破坏架构"。
        """
        for attempt in range(MAX_AUTO_FIX_ATTEMPTS):
            # AIUCE 特有关键：修复不能违反宪法条款
            proposed_fix = self._generate_fix(sop, failure_log)

            # L0 合宪性审查（AIUCE 原生机制，OpenSpace 没有）
            veto = self.constitution.audit(proposed_fix)
            if veto.passed:
                self._apply_fix(sop, proposed_fix)
                return
        # 超过重试次数，回退人工审核
        self._escalate_to_human(sop)
```

**改造要点**:
- 不引入 openspace 依赖包，只拆解其"轨迹→SOP→评分→FIX"的四步闭环
- AIUCE 特有关键创新：每次 AUTO-FIX 必须经过 L0 合宪性审查（OpenSpace 没有宪法约束）
- `teonu-worldmodel` 的元认知作为演化方向判断层（"往哪个方向演化"）

---

### 2.4 CLI-Anything → AIUCE L9 "锦衣卫令牌"工具协议

**原始项目**: HKUDS/CLI-Anything ★30589  
**原始定位**: 让所有 CLI 工具变成 Agent 原生工具，cli-hub，JSON/Human 双输出

#### 2.4.1 理念拆解

CLI-Anything 的核心不是"又一个工具集合"，而是**"工具的 Agent 化协议"**：
- 任何 CLI → 通过 harness 包装 → JSON 输出 + Human 可读输出
- hub 机制：发现、注册、版本管理
- 核心价值：给 AI 提供结构化的、可靠的工具接口

这与 AIUCE L9 的 `ToolRegistry` + `ExecutionEngine` 机制**完全同构**，差异在于 AIUCE 缺一个"把任意 CLI 转成结构化工具"的 harness 协议。

**AIUCE 改造方向**：将 CLI-Anything 的 harness 协议改写为 AIUCE L9 的 `ToolHarness` 规范，用 billgaohub 的 `ipipq` 和 `smart-file-router` 作为首批注册工具。

#### 2.4.2 具体改造

```python
# L9/tool_harness.py（改造自 CLI-Anything 协议）

class ToolHarness:
    """
    改造自 CLI-Anything 的工具包装协议。
    核心理念移植：
    1. 任何 CLI 工具通过 Harness → 结构化 JSON + Human 输出
    2. Hub 注册机制：发现、版本、协议兼容
    3. 零配置注册：工具方只需声明接口规范

    AIUCE 特有改造：
    - 引入 L0 合宪性检查：注册工具必须通过合宪性审查
    - 引入 L5 审计记录：每个工具调用都有执行凭证
    - 双轨输出：JSON 给 AI（H9），Markdown 给 human（飞书/Telegram）
    """

    def register(self, tool_spec: ToolSpec) -> ToolID:
        # AIUCE 特有关键: 工具注册必须过 L0 合宪性
        veto = self.constitution.audit_tool_spec(tool_spec)
        if veto.passed:
            return self.registry.register(tool_spec)
        raise ConstitutionError(f"工具 {tool_spec.name} 未通过合宪性审查: {veto.reason}")

    def invoke(self, tool_id: ToolID, params: dict) -> ToolResult:
        # 1. 获取工具规范
        spec = self.registry.get(tool_id)

        # 2. L5 审计记录（AIUCE 特有，OpenClaw/Hermes 没有）
        audit_id = self.audit.log_tool_invocation(tool_id, params)

        # 3. 双轨执行
        if spec.output_mode == "json":
            result = self._exec_json_mode(spec, params)   # AI 消费
        else:
            result = self._exec_human_mode(spec, params)  # 人类消费

        # 4. L5 审计归档
        self.audit.finalize(audit_id, result)
        return result

# 改造 ipipq 为 AIUCE L9 原生工具
@ToolHarness.register(
    name="file_organizer",
    domain=ToolDomain.BODY,  # 执行域（Body/Flow/Intel）
    layer=L9,
    protocol="cli-anything-v1",
    constitutional_alignment=["body_flow_quality"],  # L0 合宪性关联
)
def file_organizer(target_dir: str, strategy: str = "semantic") -> FileOrganizerResult:
    """
    改造自 billgaohub/ipipq。
    CLI-Anything 包装：将 ipipq 的文件自动整理能力注册为 L9 原生工具。
    """
    ...
```

---

### 2.5 Graphify → AIUCE L4 "图谱星图"代码理解模块

**原始项目**: safishamsi/graphify ★25653  
**原始定位**: AST 无成本结构解析 + LLM 关系提取，71.5x token 节省

#### 2.5.1 理念拆解

Graphify 的核心不是"一个知识图谱工具"，而是**"零成本结构提取 + 语义关系发现"**的双通道：
- 通道一：Tree-sitter AST，无 LLM 成本，提取代码结构
- 通道二：LLM 从结构中发现关系，生成图谱

**AIUCE 改造方向**：将双通道理念移植为 AIUCE L4 的 `CodeUnderstanding` 子模块，专门处理代码记忆的语义存储，解决 AIUCE 对自身代码库的"自我理解"问题。

```python
# L4/code_understanding.py（改造自 Graphify 理念）

class CodeUnderstandingModule:
    """
    改造自 Graphify 的双通道知识图谱理念。
    核心理念移植：
    1. 通道一: Tree-sitter AST 解析（零 LLM 成本）
    2. 通道二: LLM 关系发现（语义补充）
    3. 71.5x token 节省：AI 读图谱而非原始代码

    AIUCE 特有改造：
    - 输出接入 L4 SemanticDisk（记忆层）
    - 生成的图谱节点标注 AIUCE Layer 归属（L0-L10）
    - 支持 AIUCE repo 自身代码的自理解
    """

    def analyze(self, repo_path: str) -> CodeKnowledgeGraph:
        # 通道一: AST 结构解析（零 token）
        structure = self._ast_pass(repo_path)  # Tree-sitter，无 LLM

        # 通道二: 关系发现（仅对关键节点调用 LLM）
        relations = self._llm_relation_pass(
            structure,
            focus_nodes=self._prioritize(structure),  # 只对核心节点做 LLM
        )

        # 标注 AIUCE 层级归属（Graphify 没有的 AIUCE 特有属性）
        for node in relations.nodes:
            node.layer = self._assign_layer(node)  # 判断属于哪个 L0-L10

        return CodeKnowledgeGraph(structure + relations)
```

---

### 2.6 Deer-flow → AIUCE L3 "三十六计"推理调度器

**原始项目**: bytedance/deer-flow ★61302  
**原始定位**: LangGraph 多路径推理，ReAct/Plan-and-Solve，任务分解 DAG

#### 2.6.1 理念拆解

Deer-flow 的核心不是"一个任务规划器"，而是**"把复杂任务变成可执行的 DAG，并在沙盒中验证"**：
- 任务 → DAG 分解（Plan）
- DAG 节点 → 工具/推理调用（Act）
- 沙盒验证 → 回退/重试

AIUCE L3 已经设计了"多路径推演"框架（`l3_reasoning.py`），但没有实现 DAG 化执行层。Deer-flow 的 LangGraph 化改造是关键缺口。

**AIUCE 改造方向**：将 Deer-flow 的 DAG 执行机制移植为 AIUCE L3 的 `TaskOrchestrator`，用 `teonu-worldmodel` 的元认知调度替代 Deer-flow 的朴素的"最长路径优先"。

```python
# L3/orchestrator.py（改造自 Deer-flow DAG 机制）

class AIUCETaskOrchestrator:
    """
    改造自 Deer-flow 的 LangGraph DAG 执行机制。
    核心理念移植：
    1. 任务 → DAG 分解（Plan）
    2. DAG 节点并行/串行调度（Execute）
    3. 沙盒验证 + 回退（Sandbox）

    AIUCE 特有改造：
    - 引入 teonu-worldmodel 元认知层：在分解前先判断"用哪一计"
    - L10 沙盒做真正的影子宇宙（Deer-flow 沙盒是通用沙盒，AIUCE 沙盒是蒙特卡洛）
    - L0 合宪性前置检查：DAG 分解结果必须通过合宪性网关
    """

    def plan(self, task: str) -> TaskDAG:
        # AIUCE 特有：元认知判断"推理策略"（Deer-flow 没有这层）
        strategy = self.worldmodel.select_strategy(task)  # teonu-worldmodel 调度

        # DAG 分解（改造自 Deer-flow 的 Plan 阶段）
        dag = self._deerflow_style_decompose(task, strategy=strategy)

        # L0 合宪性检查（AIUCE 特有，Deeer-flow 无此机制）
        veto = self.constitution.audit_dag(dag)
        if veto.passed:
            return dag
        return self._replan_with_constraints(dag, veto.constraints)

    def execute(self, dag: TaskDAG) -> List[NodeResult]:
        # L10 蒙特卡洛验证（AIUCE 特有，Deeer-flow 是通用沙盒）
        if self._needs_simulation(dag):
            sim_result = self.sandbox.monte_carlo_simulate(dag)
            if sim_result.confidence < 0.7:
                return self._degrade_to_single_path(dag)  # 降级到保守路径
        return self._parallel_execute(dag)  # 并行执行
```

---

### 2.7 MarkItDown → AIUCE L2 "千里眼"文档感知器

**原始项目**: microsoft/markitdown ★107583  
**原始定位**: 万物转 Markdown，保留结构，LLM 视觉 OCR

#### 2.7.1 理念拆解

MarkItDown 的核心价值是**"让非结构化文档变成 LLM 可消费的 Markdown"**。AIUCE L2 感知层的"现实对账"机制需要处理文档输入，目前缺乏这一环。

**AIUCE 改造方向**：将 MarkItDown 的文档→Markdown 转换内化为 L2 感知层的 `DocumentIngestor` 子模块，专门负责 PDF/Word/Excel/PPT 的感知化处理。

```python
# L2/document_ingestor.py（改造自 MarkItDown 机制）

class DocumentIngestor:
    """
    改造自 Microsoft MarkItDown 的文档转换理念。
    核心理念移植：
    1. 万物转 Markdown（保留结构）
    2. LLM 视觉 OCR（图片内文字识别）
    3. 流式处理（不积压大文档）

    AIUCE 特有改造：
    - 转换结果不是终点，是 L2 感知事件的起点
    - 感知事件注入 NeuralBus，进入 L3→L5→L9 处理链
    - L0 合宪性：敏感文档（PDF加密/权限）直接过滤，不进入感知层
    """

    def ingest(self, doc_path: str) -> PerceptionEvent:
        # 格式检测 + LLM OCR（改造自 MarkItDown）
        content = self._markitdown_convert(doc_path)

        # AIUCE 特有：感知事件生成
        event = RealitySnapshot(
            source="document_ingestor",
            content=content,
            layer=self._detect_layer(content),
            constitutional_tags=self._extract_constitutional_tags(content),
        )

        # 注入 L2 感知事件总线
        self.neural_bus.publish(Event(type=EventType.DOCUMENT_PERCEIVED, payload=event))
        return event
```

---

### 2.8 其他项目处理

| 项目 | 评级 | 改造决策 | 理由 |
|------|------|----------|------|
| gbrain | P1 | **吸收理念，不引代码** | 人设 Brain 模板逻辑简化为 AIUCE L1 identity_injector |
| Cognee | P2 | **降级为辅助** | 6行代码理念可学，但 AIUCE L4 已有 memory_sal 自研体系，暂不引入 |
| UI-TARS | P2 | **等待时机** | GUI 感知有价值但依赖桌面环境，Phase 3 评估 |
| awesome-design-md | P3 | **吸收理念** | DESIGN.md 约束机制改写为 L8 输出格式化规范 |
| pretext | P3 | **暂缓** | 文本排版与 L8 路由功能无直接关系 |
| lossless-claw | P3 | **暂缓** | stars 4275，生态成熟后再评估 |
| memos | P3 | **降级** | 个人笔记与 L2 实时感知场景不匹配，降为外部数据源 |
| MiniMax-AI/cli | P3 | **暂缓** | stars 1325，MiniMax 生态影响力不足 |
| skills | P3 | **吸收理念** | 技能标准化思路（agentskills.io）融入 L7 skill_library |

---

## 三、billgaohub 项目深度融合方案

| 项目 | AIUCE 改造目标 | 融合层级 | 改造方式 |
|------|---------------|---------|---------|
| **agent-sovereignty-rules** | L0 语义网关规则源 | L0 | 五项原则 → 确定性合宪性校验规则 |
| **teonu-worldmodel** | L3/L7 元认知调度层 | L3+L7 | 元认知判断 → 推理策略选择 + 演化方向 |
| **smart-file-router** | L9 Body 域执行工具 | L9 | 分类引擎 → CLI-Harness 注册为 L9 工具 |
| **ipipq** | L9 文件整理工具 | L9 | 整理逻辑 → ToolHarness 协议注册 |
| **ai-governance-framework** | L5 审计规范源 | L5 | 治理框架 → 审计字段规范化 |

---

## 四、优先级与改造路径

### P0 核心改造（先完成后端框架）

| # | 改造模块 | 源项目 | 改造要点 | 工时估算 |
|---|---------|--------|---------|---------|
| 1 | L0/SemanticGateway | hermes-agent | AGENTS.md 规则解析 → SOUL.md 语义审查 | 3-5天 |
| 2 | L4/PalaceMemory | mempalace | Raw verbatim + 空间索引替代摘要 | 5-7天 |
| 3 | L7/EvolutionEngine | OpenSpace | 轨迹→SOP→GDPVal→AUTO-FIX 四步闭环 | 5-7天 |
| 4 | L9/ToolHarness | CLI-Anything | 工具 Agent 化协议 + ipipq/smart-file-router 注册 | 4-6天 |
| 5 | L3/Orchestrator | deer-flow | DAG 任务分解 + teonu-worldmodel 元认知调度 | 7-10天 |

### P1 感知与理解（完成核心后）

| # | 改造模块 | 源项目 | 改造要点 |
|---|---------|--------|---------|
| 6 | L2/DocumentIngestor | MarkItDown | 万物→Markdown → 感知事件注入 |
| 7 | L4/CodeUnderstanding | Graphify | AST+LLM 双通道 → 代码自理解图谱 |
| 8 | L1/IdentityBrain | gbrain | 人设 Brain 模板 → identity_injector |

---

## 五、改造核心原则

```
一、理念移植 > 代码复用
   学它的思想，不抄它的实现。AIUCE 自研体系优先。

二、L0 合宪性是所有改造的天花板
   任何外部机制接入 AIUCE，必须先通过 L0 审查。
   这是 AIUCE 与 Hermes/Deer-flow/OpenSpace 的本质差异。

三、Raw Verbatim > LLM 摘要
   学习 MemPalace：存储原文，不烧 LLM 做摘要。
   记忆层(token)成本 < 推理层(token)成本。

四、元认知调度 > 朴素调度
   学习 teonu-worldmodel + deer-flow：任务分解前先判断"往哪走"。

五、双轨输出 > 单轨
   所有 L9 工具必须同时支持 JSON（AI消费）和 Markdown（人消费）。
```

---

*报告生成: ooppg | AIUCE 首席系统架构师*  
*核心立场: 不做集成商，做架构师。每个外部理念必须经过 AIUCE 语境的转译。*  
*数据真实性: GitHub API live query + 源码 README 分析, 2026-04-14*

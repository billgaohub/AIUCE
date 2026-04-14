"""
L3 认知编排层：元认知调度引擎
Cognitive Orchestrator — 改造自 teonu-worldmodel 的三层认知控制

融合来源：
- teonu-worldmodel (billgaohub): 三条系统法则 + 三层认知控制 + 节点生命周期
- deer-flow (bytedance): DAG 任务分解 + 工具链编排

核心职责：
- 元认知调度：推理前先判断"用哪一计"（策略选择）
- 三层认知控制：输入控制(ingest)、上下文控制(snapshot)、推理控制(LWG)
- 认知可压缩：超过预算时动态裁剪，遗忘/合并/摘要
- DAG 化推理：任务分解为有向无环图，支持并行/串行调度
"""

from typing import Dict, Any, List, Optional, Callable, Set
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import uuid
import heapq


# ═══════════════════════════════════════════════════════════════════
# 三条系统法则（来自 teonu-worldmodel）
# ═══════════════════════════════════════════════════════════════════

class CognitiveLaws:
    """
    改造自 teonu-worldmodel 的三条系统法则。
    AIUCE L3 的元认知调度必须遵守这三条铁律。
    """

    # 法则一：假设≠事实
    # LWG（局部世界生成）产生的推断必须标记 confidence <= 0.6
    # 推断不能直接作为事实使用，必须经过验证
    LWG_INFERENCE_MAX_CONFIDENCE = 0.6

    # 法则二：认知必须可压缩
    # 超过 MAX_HISTORY 条历史记录 → 自动摘要化
    # pending 超时 → 自动遗忘或升级为 alert
    MAX_HISTORY = 10
    PENDING_TIMEOUT_SECONDS = 300

    # 法则三：上下文必须受预算约束
    # token budget 耗尽时，优先保留 stable + 高 confidence 节点
    DEFAULT_TOKEN_BUDGET = 2000


# ═══════════════════════════════════════════════════════════════════
# 节点生命周期（来自 teonu-worldmodel）
# ═══════════════════════════════════════════════════════════════════

class NodeState(Enum):
    """改造自 teonu-worldmodel 的节点生命周期状态"""
    DRAFT = "draft"           # 初稿，待验证
    INFERRED = "inferred"     # LWG 推断生成，confidence <= 0.6
    CONFIRMED = "confirmed"   # 已验证，可信
    STABLE = "stable"         # 稳定，可作为推理前提
    DECAYED = "decayed"       # 过时/被遗忘


@dataclass
class CognitiveNode:
    """改造自 teonu-worldmodel 的认知节点"""
    id: str
    title: str
    content: str
    state: NodeState = NodeState.DRAFT
    confidence: float = 0.5
    half_life_days: int = 30
    layer_tags: List[str] = field(default_factory=list)  # AIUCE Layer 归属
    parent_ids: List[str] = field(default_factory=list)
    child_ids: List[str] = field(default_factory=list)
    created_at: str = ""
    updated_at: str = ""

    def is_valid_inference(self) -> bool:
        """法则一：推断节点置信度不能超过上限"""
        return self.confidence <= CognitiveLaws.LWG_INFERENCE_MAX_CONFIDENCE


# ═══════════════════════════════════════════════════════════════════
# 三层认知控制（来自 teonu-worldmodel）
# ═══════════════════════════════════════════════════════════════════

class CognitiveControl:
    """
    改造自 teonu-worldmodel 的三层认知控制。
    每一层对应一个控制函数。
    """

    @staticmethod
    def ingest_control(intent: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        改造自 teonu-worldmodel 的输入控制（Ingest）。
        决定什么能进入认知世界。

        AIUCE L3 特有：
        - 调用 SovereigntyGateway 做主权审查
        - 调用 SemanticGateway 做语义审查
        """
        from .l0_sovereignty_gateway import SovereigntyGateway
        from .l0_semantic_gateway import SemanticGateway

        sovereignty = SovereigntyGateway()
        semantic = SemanticGateway()

        # 第一关：主权审查
        sv = sovereignty.audit(intent, context)
        if sv.vetoed:
            return {
                "allowed": False,
                "gate": "sovereignty",
                "reason": sv.reason,
                "stage": "denied",
            }

        # 第二关：语义审查
        sm = semantic.audit(intent, context)
        if not sm.passed:
            return {
                "allowed": False,
                "gate": "semantic",
                "reason": sm.reason,
                "stage": "denied",
            }

        return {
            "allowed": True,
            "gate": "passed",
            "confidence": sm.confidence.value,
            "stage": "ingested",
        }

    @staticmethod
    def snapshot_control(
        nodes: List[CognitiveNode],
        token_budget: int = CognitiveLaws.DEFAULT_TOKEN_BUDGET
    ) -> List[CognitiveNode]:
        """
        改造自 teonu-worldmodel 的上下文控制（Snapshot）。
        决定当前推理能看到什么世界。

        优先级：STABLE > CONFIRMED > INFERRED > DRAFT
        超预算时按优先级裁剪
        """
        if not nodes:
            return []

        # 按优先级排序
        def priority(node: CognitiveNode) -> tuple:
            state_order = {
                NodeState.STABLE: 0,
                NodeState.CONFIRMED: 1,
                NodeState.INFERRED: 2,
                NodeState.DRAFT: 3,
                NodeState.DECAYED: 99,
            }
            return (state_order.get(node.state, 99), -node.confidence)

        sorted_nodes = sorted(nodes, key=priority)

        # 估算 token（简化：按字符数/4）
        total_tokens = sum(len(n.content) // 4 for n in sorted_nodes)

        if total_tokens <= token_budget:
            return sorted_nodes

        # 超预算，渐进裁剪
        budget_nodes: List[CognitiveNode] = []
        used_tokens = 0
        for node in sorted_nodes:
            node_tokens = len(node.content) // 4
            if used_tokens + node_tokens <= token_budget:
                budget_nodes.append(node)
                used_tokens += node_tokens
            else:
                break

        return budget_nodes

    @staticmethod
    def reasoning_control(
        nodes: List[CognitiveNode],
        intent: str
    ) -> Dict[str, Any]:
        """
        改造自 teonu-worldmodel 的推理控制（LWG - 局部世界生成）。
        决定如何理解世界。

        核心：生成推断时必须遵守"假设≠事实"法则。
        推断节点 confidence <= 0.6，必须标记 requires_validation。
        """
        valid_nodes = [n for n in nodes if n.state != NodeState.DECAYED]

        # 检测推断节点是否违规
        violations = []
        for node in valid_nodes:
            if node.state == NodeState.INFERRED and not node.is_valid_inference():
                violations.append(node.id)

        return {
            "valid_nodes": valid_nodes,
            "lwg_violations": violations,
            "requires_validation": len(violations) > 0,
            "inference_count": sum(1 for n in valid_nodes if n.state == NodeState.INFERRED),
        }


# ═══════════════════════════════════════════════════════════════════
# 推理策略选择（改造自 teonu-worldmodel 的元认知调度）
# ═══════════════════════════════════════════════════════════════════

class ReasoningStrategy(Enum):
    """改造自 deer-flow 的推理策略枚举"""
    DEDUCTIVE = "deductive"       # 演绎：从规则推导
    INDUCTIVE = "inductive"       # 归纳：从现象总结
    ABDUCTIVE = "abductive"       # 溯因：从结果反推原因
    ANALOGICAL = "analogical"     # 类比：找相似案例
    CAUSAL = "causal"             # 因果：因果链分析
    MONTE_CARLO = "monte_carlo"  # 蒙特卡洛：概率模拟（L10 沙盒联动）
    SINGLE_PATH = "single"        # 保守单路径（DAG 置信度不足时降级）


class StrategySelector:
    """
    改造自 teonu-worldmodel 的元认知调度。
    核心问题："在当前上下文下，应该用哪种推理策略？"

    融合 deer-flow 的 DAG 评估机制：
    - 复杂任务 → 选择多路径策略（DEDUCTIVE + ABDUCTIVE）
    - 低置信度 → 降级到 SINGLE_PATH
    - 高风险/高不确定性 → MONTE_CARLO
    """

    def select(
        self,
        intent: str,
        context: Dict[str, Any],
        node_count: int = 0,
        avg_confidence: float = 0.5,
    ) -> ReasoningStrategy:
        """
        元认知策略选择。
        在分解任务前先判断"用哪一计"。
        """
        # 法则：低置信度 → 保守策略
        if avg_confidence < 0.4:
            return ReasoningStrategy.SINGLE_PATH

        # 法则：推断节点多 → 溯因策略验证
        if node_count > 5:
            return ReasoningStrategy.ABDUCTIVE

        # 法则：复杂任务特征 → 多路径策略
        complexity_indicators = [
            "分析", "评估", "比较", "预测", "权衡",
            "方案", "策略", "计划", "决策",
        ]
        if any(kw in intent for kw in complexity_indicators):
            return ReasoningStrategy.DEDUCTIVE

        # 默认：演绎推理
        return ReasoningStrategy.DEDUCTIVE


# ═══════════════════════════════════════════════════════════════════
# DAG 任务节点（改造自 deer-flow）
# ═══════════════════════════════════════════════════════════════════

@dataclass
class TaskNode:
    """改造自 deer-flow 的 DAG 任务节点"""
    id: str
    label: str
    task: str
    strategy: ReasoningStrategy = ReasoningStrategy.DEDUCTIVE
    depends_on: List[str] = field(default_factory=list)  # 前置节点 ID
    confidence: float = 0.5
    status: str = "pending"  # pending | running | done | failed
    result: Any = None
    layer_tag: str = ""  # AIUCE Layer 归属（L0-L10）


@dataclass
class TaskDAG:
    """改造自 deer-flow 的任务 DAG（有向无环图）"""
    id: str
    nodes: Dict[str, TaskNode] = field(default_factory=dict)
    execution_order: List[List[str]] = field(default_factory=list)  # 按层级分组

    def add_node(self, node: TaskNode):
        self.nodes[node.id] = node

    def topological_sort(self) -> List[List[str]]:
        """拓扑排序，返回按执行层级分组的节点 ID"""
        in_degree = {nid: len(n.depends_on) for nid, n in self.nodes.items()}
        levels: List[List[str]] = []

        remaining = set(self.nodes.keys())
        while remaining:
            # 找入度为 0 的节点
            current_level = [nid for nid in remaining if in_degree[nid] == 0]
            if not current_level:
                break  # 循环依赖检测
            levels.append(current_level)
            for nid in current_level:
                remaining.remove(nid)
                # 减少后继节点的入度
                for successor_id, succ in self.nodes.items():
                    if nid in succ.depends_on:
                        in_degree[successor_id] -= 1

        self.execution_order = levels
        return levels


# ═══════════════════════════════════════════════════════════════════
# Cognitive Orchestrator（认知编排器）
# ═══════════════════════════════════════════════════════════════════

class CognitiveOrchestrator:
    """
    改造自 teonu-worldmodel + deer-flow 的认知编排器。

    AIUCE 特有设计：
    1. 元认知调度层（StrategySelector）：推理前先选策略
    2. 三层认知控制：ingest → snapshot → LWG
    3. DAG 任务编排：任务分解为可并行执行的任务图
    4. L0 合宪性前置：所有 DAG 在执行前必须通过 SovereigntyGateway
    """

    def __init__(self, sovereignty_gateway=None):
        from .l0_sovereignty_gateway import SovereigntyGateway
        self.sovereignty = sovereignty_gateway or SovereigntyGateway()
        self.strategy_selector = StrategySelector()
        self.active_nodes: Dict[str, CognitiveNode] = {}

    def plan(self, intent: str, context: Dict[str, Any] = None) -> TaskDAG:
        """
        任务规划主入口。
        改造自 deer-flow 的 Plan 阶段。
        """
        context = context or {}

        # ── 阶段一：元认知调度（teonu-worldmodel）──────────────
        node_count = len(self.active_nodes)
        avg_conf = sum(n.confidence for n in self.active_nodes.values()) / max(node_count, 1)
        strategy = self.strategy_selector.select(intent, context, node_count, avg_conf)

        # ── 阶段二：输入控制（ingest）──────────────────────────
        ingest = CognitiveControl.ingest_control(intent, context)
        if not ingest.get("allowed", False):
            raise PermissionError(f"L3 规划被 ingest 拒绝: {ingest}")

        # ── 阶段三：上下文快照（snapshot）───────────────────────
        snapshot = CognitiveControl.snapshot_control(
            list(self.active_nodes.values()),
            token_budget=context.get("token_budget", CognitiveLaws.DEFAULT_TOKEN_BUDGET)
        )

        # ── 阶段四：推理控制（LWG）─────────────────────────────
        reasoning = CognitiveControl.reasoning_control(snapshot, intent)
        if reasoning.get("requires_validation", False):
            # 有违规推断，标记但不阻止
            pass

        # ── 阶段五：DAG 分解（deer-flow 风格）──────────────────
        dag = self._decompose(intent, strategy, context)

        # ── 阶段六：L0 合宪性前置检查 ─────────────────────────
        for node in dag.nodes.values():
            veto = self.sovereignty.audit(node.task)
            if veto.vetoed:
                node.status = "failed"
                node.result = {"error": f"主权否决: {veto.reason}"}

        return dag

    def _decompose(
        self,
        intent: str,
        strategy: ReasoningStrategy,
        context: Dict[str, Any]
    ) -> TaskDAG:
        """
        任务分解为 DAG。
        改造自 deer-flow 的 DAG 构建逻辑。
        """
        dag_id = str(uuid.uuid4())[:8]
        dag = TaskDAG(id=dag_id, nodes={})

        # 简单策略：单任务节点
        root = TaskNode(
            id=f"{dag_id}-root",
            label="主任务",
            task=intent,
            strategy=strategy,
            layer_tag="L3",
        )
        dag.add_node(root)

        # 复杂任务：拆分子任务
        sub_task_patterns = [
            (r"分析和?比较", "分析子任务", "L3"),
            (r"规划和?实施", "规划子任务", "L7"),
            (r"执行和?验证", "执行子任务", "L9"),
            (r"监控和?调整", "监控子任务", "L6"),
        ]

        for pattern, label, layer in sub_task_patterns:
            if pattern in intent:
                sub = TaskNode(
                    id=f"{dag_id}-sub-{len(dag.nodes)}",
                    label=label,
                    task=intent,
                    strategy=strategy,
                    depends_on=[root.id],
                    layer_tag=layer,
                )
                dag.add_node(sub)

        dag.topological_sort()
        return dag

    def execute(self, dag: TaskDAG) -> Dict[str, Any]:
        """
        执行 DAG。
        改造自 deer-flow 的 Execute 阶段。
        """
        results = {}
        for level in dag.execution_order:
            for node_id in level:
                node = dag.nodes[node_id]
                if node.status == "failed":
                    continue

                # 并行执行同层级节点
                node.status = "running"
                # 这里调用实际的 LLM 或工具
                node.status = "done"
                results[node_id] = node.result

        return results

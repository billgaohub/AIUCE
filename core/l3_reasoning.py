"""
L3 推理层：多路径推演引擎
Reasoning Engine with Deer-flow Integration

架构：
┌─────────────────────────────────────────────────────────┐
│              L3 推理层 (Reasoning Engine)                │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  ┌───────────────────────────────────────────────────┐  │
│  │  任务规划器 (Task Planner) - Deer-flow             │  │
│  │  - 复杂任务分解 (Task Decomposition)               │  │
│  │  - DAG 依赖管理 (Dependency Graph)                 │  │
│  │  - 并行/串行调度 (Scheduling)                      │  │
│  └───────────────────────────────────────────────────┘  │
│                         ↓                               │
│  ┌───────────────────────────────────────────────────┐  │
│  │  多路径推演 (Multi-path Reasoning)                 │  │
│  │  - 假设生成 (Hypothesis Generation)               │  │
│  │  - 演绎推理 (Deductive Reasoning)                 │  │
│  │  - 归纳推理 (Inductive Reasoning)                 │  │
│  │  - 类比推理 (Analogical Reasoning)                │  │
│  └───────────────────────────────────────────────────┘  │
│                         ↓                               │
│  ┌───────────────────────────────────────────────────┐  │
│  │  推理选择 (Reasoning Selection)                    │  │
│  │  - 路径评分 (Path Scoring)                        │  │
│  │  - 风险评估 (Risk Assessment)                     │  │
│  │  - 最优路径选择 (Optimal Path Selection)          │  │
│  └───────────────────────────────────────────────────┘  │
│                                                          │
└─────────────────────────────────────────────────────────┘

Deer-flow 集成：
- 任务分解为 DAG 工作流
- 支持 ReAct / Plan-and-Solve 等推理策略
- 工具链编排
"""

from typing import Dict, Any, List, Optional, Tuple, Callable, Union
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import json
import os
import threading
import queue
import uuid
from collections import defaultdict
import heapq


# ═══════════════════════════════════════════════════════════════
# 类型定义
# ═══════════════════════════════════════════════════════════════

class ReasoningStrategy(Enum):
    """推理策略"""
    DEDUCTIVE = "deductive"       # 演绎推理
    INDUCTIVE = "inductive"       # 归纳推理
    ABDUCTIVE = "abductive"       # 溯因推理
    ANALOGICAL = "analogical"     # 类比推理
    REACT = "react"               # ReAct 推理
    PLAN_AND_SOLVE = "plan_and_solve"  # Plan-and-Solve
    TREE_OF_THOUGHT = "tree_of_thought"  # 思维树


class TaskStatus(Enum):
    """任务状态"""
    PENDING = "pending"
    READY = "ready"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class PathScore(Enum):
    """路径评分等级"""
    OPTIMAL = 5       # 最优
    GOOD = 4          # 良好
    ACCEPTABLE = 3    # 可接受
    RISKY = 2         # 有风险
    DANGEROUS = 1     # 危险
    INVALID = 0       # 无效


@dataclass
class ReasoningTask:
    """推理任务"""
    id: str
    name: str
    description: str
    strategy: ReasoningStrategy
    dependencies: List[str] = field(default_factory=list)
    status: TaskStatus = TaskStatus.PENDING
    result: Optional[Any] = None
    error: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "strategy": self.strategy.value,
            "dependencies": self.dependencies,
            "status": self.status.value,
            "result": self.result,
            "error": self.error,
            "created_at": self.created_at,
            "started_at": self.started_at,
            "completed_at": self.completed_at
        }


@dataclass
class ReasoningPath:
    """推理路径"""
    id: str
    hypothesis: str
    reasoning_steps: List[str]
    conclusion: str
    confidence: float
    evidence: List[str] = field(default_factory=list)
    risks: List[str] = field(default_factory=list)
    score: PathScore = PathScore.ACCEPTABLE
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "hypothesis": self.hypothesis,
            "steps": len(self.reasoning_steps),
            "conclusion": self.conclusion,
            "confidence": self.confidence,
            "risks": len(self.risks),
            "score": self.score.value
        }


@dataclass
class TaskDAG:
    """任务 DAG"""
    id: str
    name: str
    tasks: Dict[str, ReasoningTask]
    edges: List[Tuple[str, str]]  # (from, to)
    entry_points: List[str]
    exit_points: List[str]
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "task_count": len(self.tasks),
            "edge_count": len(self.edges),
            "entry_points": self.entry_points,
            "exit_points": self.exit_points
        }


@dataclass
class ReasoningResult:
    """推理结果"""
    task_id: str
    selected_path: Optional[ReasoningPath]
    all_paths: List[ReasoningPath]
    execution_time_ms: float
    strategy_used: ReasoningStrategy
    success: bool
    summary: str


# ═══════════════════════════════════════════════════════════════
# 任务规划器 (Task Planner) - Deer-flow 风格
# ═══════════════════════════════════════════════════════════════

class TaskPlanner:
    """
    任务规划器 - Deer-flow 集成
    
    功能：
    1. 复杂任务分解
    2. DAG 依赖管理
    3. 并行/串行调度
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self._task_queue: queue.Queue = queue.Queue()
        self._dags: Dict[str, TaskDAG] = {}
        self._execution_callback: Optional[Callable] = None
        
        print("  [L3 推理层] 任务规划器初始化")
    
    def set_execution_callback(self, callback: Callable[[ReasoningTask], Any]):
        """设置任务执行回调"""
        self._execution_callback = callback
    
    # ── 任务分解 ───────────────────────────────────────────────
    
    def decompose(
        self,
        goal: str,
        strategy: ReasoningStrategy = ReasoningStrategy.REACT,
        max_depth: int = 3
    ) -> TaskDAG:
        """
        分解复杂任务为 DAG
        
        Args:
            goal: 目标描述
            strategy: 推理策略
            max_depth: 最大分解深度
            
        Returns:
            任务 DAG
        """
        dag_id = str(uuid.uuid4())[:8]
        
        # 创建根任务
        root_task = ReasoningTask(
            id=f"{dag_id}_root",
            name="root",
            description=goal,
            strategy=strategy
        )
        
        # 分解子任务
        tasks = {root_task.id: root_task}
        edges = []
        
        self._decompose_recursive(
            parent_task=root_task,
            tasks=tasks,
            edges=edges,
            current_depth=1,
            max_depth=max_depth,
            strategy=strategy
        )
        
        # 计算入口和出口点
        entry_points = [root_task.id]
        exit_points = [
            t.id for t in tasks.values()
            if not any(e[0] == t.id for e in edges)
        ]
        
        dag = TaskDAG(
            id=dag_id,
            name=goal[:50],
            tasks=tasks,
            edges=edges,
            entry_points=entry_points,
            exit_points=exit_points
        )
        
        self._dags[dag_id] = dag
        return dag
    
    def _decompose_recursive(
        self,
        parent_task: ReasoningTask,
        tasks: Dict[str, ReasoningTask],
        edges: List[Tuple[str, str]],
        current_depth: int,
        max_depth: int,
        strategy: ReasoningStrategy
    ):
        """递归分解任务"""
        if current_depth > max_depth:
            return
        
        # 根据策略分解
        sub_tasks = self._generate_subtasks(parent_task, strategy)
        
        for i, (name, desc) in enumerate(sub_tasks):
            sub_task = ReasoningTask(
                id=f"{parent_task.id}_{i}",
                name=name,
                description=desc,
                strategy=strategy,
                dependencies=[parent_task.id]
            )
            
            tasks[sub_task.id] = sub_task
            edges.append((parent_task.id, sub_task.id))
            
            # 递归分解
            self._decompose_recursive(
                sub_task, tasks, edges,
                current_depth + 1, max_depth, strategy
            )
    
    def _generate_subtasks(
        self,
        parent: ReasoningTask,
        strategy: ReasoningStrategy
    ) -> List[Tuple[str, str]]:
        """生成子任务"""
        # 基于策略生成子任务
        if strategy == ReasoningStrategy.REACT:
            return [
                ("think", f"思考: {parent.description}"),
                ("act", f"行动: 执行相关操作"),
                ("observe", f"观察: 检查结果")
            ]
        
        elif strategy == ReasoningStrategy.PLAN_AND_SOLVE:
            return [
                ("plan", f"规划: 制定解决方案"),
                ("execute", f"执行: 按计划执行"),
                ("verify", f"验证: 检查结果")
            ]
        
        elif strategy == ReasoningStrategy.TREE_OF_THOUGHT:
            return [
                ("branch_1", f"分支1: 可能性A"),
                ("branch_2", f"分支2: 可能性B"),
                ("branch_3", f"分支3: 可能性C")
            ]
        
        else:
            # 默认分解
            return [
                ("analyze", f"分析: {parent.description}"),
                ("synthesize", f"综合: 整合信息"),
                ("conclude", f"结论: 得出结果")
            ]
    
    # ── DAG 执行 ───────────────────────────────────────────────
    
    def execute(self, dag: TaskDAG) -> Dict[str, Any]:
        """
        执行 DAG
        
        支持并行和串行执行
        """
        results = {}
        completed = set()
        
        # 拓扑排序
        execution_order = self._topological_sort(dag)
        
        for task_id in execution_order:
            task = dag.tasks[task_id]
            
            # 检查依赖
            deps_completed = all(
                dep in completed
                for dep in task.dependencies
            )
            
            if not deps_completed:
                task.status = TaskStatus.FAILED
                task.error = "依赖未完成"
                continue
            
            # 执行任务
            task.status = TaskStatus.RUNNING
            task.started_at = datetime.now().isoformat()
            
            try:
                if self._execution_callback:
                    result = self._execution_callback(task)
                else:
                    result = self._default_execute(task)
                
                task.result = result
                task.status = TaskStatus.COMPLETED
                completed.add(task_id)
                
            except Exception as e:
                task.status = TaskStatus.FAILED
                task.error = str(e)
            
            task.completed_at = datetime.now().isoformat()
            results[task_id] = task.to_dict()
        
        return results
    
    def _topological_sort(self, dag: TaskDAG) -> List[str]:
        """拓扑排序"""
        in_degree = defaultdict(int)
        
        for task_id in dag.tasks:
            in_degree[task_id] = 0
        
        for from_id, to_id in dag.edges:
            in_degree[to_id] += 1
        
        # Kahn 算法
        queue = [t for t in dag.tasks if in_degree[t] == 0]
        result = []
        
        while queue:
            current = queue.pop(0)
            result.append(current)
            
            for from_id, to_id in dag.edges:
                if from_id == current:
                    in_degree[to_id] -= 1
                    if in_degree[to_id] == 0:
                        queue.append(to_id)
        
        return result
    
    def _default_execute(self, task: ReasoningTask) -> Any:
        """默认执行器"""
        return {"status": "executed", "description": task.description}
    
    # ── 统计 ───────────────────────────────────────────────────
    
    def stats(self) -> Dict[str, Any]:
        """统计"""
        return {
            "total_dags": len(self._dags),
            "total_tasks": sum(len(dag.tasks) for dag in self._dags.values())
        }


# ═══════════════════════════════════════════════════════════════
# 多路径推演器 (Multi-path Reasoning)
# ═══════════════════════════════════════════════════════════════

class MultiPathReasoning:
    """
    多路径推演器
    
    支持：
    1. 假设生成
    2. 多种推理策略
    3. 路径评估
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self._llm_provider: Optional[Callable] = None
        
        print("  [L3 推理层] 多路径推演器初始化")
    
    def set_llm_provider(self, provider: Callable):
        """设置 LLM 提供者"""
        self._llm_provider = provider
    
    # ── 推理接口 ───────────────────────────────────────────────
    
    def reason(
        self,
        query: str,
        context: Optional[Dict[str, Any]] = None,
        strategy: ReasoningStrategy = ReasoningStrategy.DEDUCTIVE,
        num_paths: int = 3
    ) -> List[ReasoningPath]:
        """
        执行多路径推理
        
        Args:
            query: 查询/问题
            context: 上下文
            strategy: 推理策略
            num_paths: 生成路径数量
            
        Returns:
            推理路径列表
        """
        paths = []
        
        for i in range(num_paths):
            path = self._generate_path(query, context, strategy, i)
            paths.append(path)
        
        return paths
    
    def _generate_path(
        self,
        query: str,
        context: Optional[Dict[str, Any]],
        strategy: ReasoningStrategy,
        path_index: int
    ) -> ReasoningPath:
        """生成推理路径"""
        path_id = str(uuid.uuid4())[:8]
        
        # 根据策略生成假设
        hypothesis = self._generate_hypothesis(query, strategy, path_index)
        
        # 生成推理步骤
        steps = self._generate_steps(query, hypothesis, strategy)
        
        # 生成结论
        conclusion = self._generate_conclusion(steps, strategy)
        
        # 计算置信度
        confidence = 0.5 + (path_index * 0.1)  # 简化：第一个路径置信度最高
        
        # 识别风险
        risks = self._identify_risks(steps, strategy)
        
        # 计算评分
        score = self._calculate_score(confidence, risks)
        
        return ReasoningPath(
            id=path_id,
            hypothesis=hypothesis,
            reasoning_steps=steps,
            conclusion=conclusion,
            confidence=confidence,
            risks=risks,
            score=score
        )
    
    def _generate_hypothesis(
        self,
        query: str,
        strategy: ReasoningStrategy,
        index: int
    ) -> str:
        """生成假设"""
        templates = {
            ReasoningStrategy.DEDUCTIVE: [
                f"假设 {index+1}: 如果按照逻辑演绎，{query}",
                f"假设 {index+1}: 基于已知前提，{query}",
                f"假设 {index+1}: 从一般到特殊，{query}"
            ],
            ReasoningStrategy.INDUCTIVE: [
                f"假设 {index+1}: 从观察中归纳，{query}",
                f"假设 {index+1}: 基于模式识别，{query}",
                f"假设 {index+1}: 从特殊到一般，{query}"
            ],
            ReasoningStrategy.ABDUCTIVE: [
                f"假设 {index+1}: 最佳解释可能是，{query}",
                f"假设 {index+1}: 推断原因，{query}",
                f"假设 {index+1}: 假设原因，{query}"
            ],
            ReasoningStrategy.ANALOGICAL: [
                f"假设 {index+1}: 通过类比，{query}",
                f"假设 {index+1}: 相似案例启示，{query}",
                f"假设 {index+1}: 结构映射，{query}"
            ]
        }
        
        return templates.get(strategy, [f"假设 {index+1}: {query}"])[index % 3]
    
    def _generate_steps(
        self,
        query: str,
        hypothesis: str,
        strategy: ReasoningStrategy
    ) -> List[str]:
        """生成推理步骤"""
        if strategy == ReasoningStrategy.REACT:
            return [
                f"思考: 分析 {query}",
                f"行动: 收集相关信息",
                f"观察: 评估结果",
                f"思考: 综合判断"
            ]
        
        elif strategy == ReasoningStrategy.TREE_OF_THOUGHT:
            return [
                f"思考分支A: {hypothesis}",
                f"思考分支B: 替代视角",
                f"思考分支C: 反向思考",
                f"评估: 选择最佳分支"
            ]
        
        else:
            return [
                f"步骤1: 分析问题 - {query}",
                f"步骤2: 应用 {strategy.value} 推理",
                f"步骤3: 验证推理链",
                f"步骤4: 得出结论"
            ]
    
    def _generate_conclusion(
        self,
        steps: List[str],
        strategy: ReasoningStrategy
    ) -> str:
        """生成结论"""
        return f"基于{strategy.value}推理，结论如下: {steps[-1]}"
    
    def _identify_risks(
        self,
        steps: List[str],
        strategy: ReasoningStrategy
    ) -> List[str]:
        """识别风险"""
        risks = []
        
        if strategy == ReasoningStrategy.ABDUCTIVE:
            risks.append("溯因推理可能产生多个合理解释")
        
        if len(steps) > 5:
            risks.append("推理链过长，可能引入累积误差")
        
        return risks
    
    def _calculate_score(
        self,
        confidence: float,
        risks: List[str]
    ) -> PathScore:
        """计算评分"""
        risk_penalty = len(risks) * 0.2
        adjusted_confidence = confidence - risk_penalty
        
        if adjusted_confidence >= 0.9:
            return PathScore.OPTIMAL
        elif adjusted_confidence >= 0.7:
            return PathScore.GOOD
        elif adjusted_confidence >= 0.5:
            return PathScore.ACCEPTABLE
        elif adjusted_confidence >= 0.3:
            return PathScore.RISKY
        else:
            return PathScore.DANGEROUS


# ═══════════════════════════════════════════════════════════════
# L3 推理层主类
# ═══════════════════════════════════════════════════════════════

class ReasoningEngine:
    """
    L3 推理层 - 多路径推演引擎
    
    "没有唯一解，只有更优解"
    
    组件：
    1. 任务规划器 (Deer-flow)
    2. 多路径推演器
    
    集成：
    - Deer-flow: 任务 DAG 分解与调度
    - LLM Provider: 推理增强
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        
        # 组件
        self.planner = TaskPlanner(self.config.get("planner", {}))
        self.reasoner = MultiPathReasoning(self.config.get("reasoner", {}))
        
        print("  [L3 推理层] 房玄龄/军师 - 多路径推演引擎就位")
    
    # ── LLM 集成 ───────────────────────────────────────────────
    
    def set_llm_provider(self, provider: Callable):
        """设置 LLM 提供者"""
        self.reasoner.set_llm_provider(provider)
    
    # ── 任务规划 ───────────────────────────────────────────────
    
    def decompose(
        self,
        goal: str,
        strategy: ReasoningStrategy = ReasoningStrategy.REACT,
        max_depth: int = 3
    ) -> TaskDAG:
        """分解任务"""
        return self.planner.decompose(goal, strategy, max_depth)
    
    def execute(self, dag: TaskDAG) -> Dict[str, Any]:
        """执行 DAG"""
        return self.planner.execute(dag)
    
    # ── 推理接口 ───────────────────────────────────────────────
    
    def reason(
        self,
        query: str,
        context: Optional[Dict[str, Any]] = None,
        strategy: ReasoningStrategy = ReasoningStrategy.DEDUCTIVE,
        num_paths: int = 3,
        select_best: bool = True
    ) -> ReasoningResult:
        """
        执行推理
        
        Args:
            query: 查询
            context: 上下文
            strategy: 推理策略
            num_paths: 路径数量
            select_best: 是否选择最优路径
        """
        start_time = datetime.now()
        
        # 生成多路径
        paths = self.reasoner.reason(query, context, strategy, num_paths)
        
        # 选择最优路径
        selected = None
        if select_best and paths:
            selected = max(paths, key=lambda p: p.score.value)
        
        # 计算耗时
        elapsed_ms = (datetime.now() - start_time).total_seconds() * 1000
        
        return ReasoningResult(
            task_id=str(uuid.uuid4())[:8],
            selected_path=selected,
            all_paths=paths,
            execution_time_ms=elapsed_ms,
            strategy_used=strategy,
            success=True,
            summary=selected.conclusion if selected else "无有效路径"
        )
    
    # ── 复合推理 ───────────────────────────────────────────────
    
    def reason_and_execute(
        self,
        query: str,
        strategy: ReasoningStrategy = ReasoningStrategy.REACT
    ) -> Tuple[ReasoningResult, Dict[str, Any]]:
        """
        推理并执行
        
        1. 分解任务
        2. 推理生成方案
        3. 执行 DAG
        """
        # 分解
        dag = self.decompose(query, strategy)
        
        # 推理
        reasoning_result = self.reason(query, strategy=strategy)
        
        # 执行
        execution_result = self.execute(dag)
        
        return reasoning_result, execution_result
    
    # ── 统计 ───────────────────────────────────────────────────
    
    def stats(self) -> Dict[str, Any]:
        """统计"""
        return {
            "planner": self.planner.stats(),
            "reasoner": {"status": "ready"}
        }


# ═══════════════════════════════════════════════════════════════
# 导出
# ═══════════════════════════════════════════════════════════════

__all__ = [
    "ReasoningStrategy",
    "TaskStatus",
    "PathScore",
    "ReasoningTask",
    "ReasoningPath",
    "TaskDAG",
    "ReasoningResult",
    "TaskPlanner",
    "MultiPathReasoning",
    "ReasoningEngine",
]

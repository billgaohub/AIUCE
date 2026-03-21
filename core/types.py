"""
Shared Type Definitions for Eleven-Layer Architecture
十一层架构共享类型定义

所有层级共用的数据结构和类型别名。
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Union
from datetime import datetime
from enum import Enum


# ─── Enums ───────────────────────────────────────────────────────

class LayerLevel(str, Enum):
    """层级枚举"""
    L0 = "L0"
    L1 = "L1"
    L2 = "L2"
    L3 = "L3"
    L4 = "L4"
    L5 = "L5"
    L6 = "L6"
    L7 = "L7"
    L8 = "L8"
    L9 = "L9"
    L10 = "L10"


class RiskLevel(str, Enum):
    LOW      = "low"
    MEDIUM   = "medium"
    HIGH     = "high"
    CRITICAL = "critical"


class MemoryCategory(str, Enum):
    EVENT      = "event"
    KNOWLEDGE  = "knowledge"
    PREFERENCE = "preference"
    FACT       = "fact"
    DECISION   = "decision"
    PATTERN    = "pattern"
    HEALTH     = "health"
    FINANCE    = "finance"
    WORK       = "work"
    PERSONAL   = "personal"


class DecisionStatus(str, Enum):
    PENDING       = "pending"
    APPROVED      = "approved"
    REJECTED      = "rejected"
    VETOED        = "vetoed"
    SANDBOX_REJECTED = "sandbox_rejected"
    SUCCESS       = "success"
    FAILURE       = "failure"


class OutcomeType(str, Enum):
    SUCCESS          = "success"
    PARTIAL          = "partial"
    FAILURE          = "failure"
    BLOCKED          = "blocked"
    REJECTED_SANDBOX = "rejected_sandbox"


# ─── Core Data Classes ───────────────────────────────────────────

@dataclass
class RealityMetric:
    """现实指标"""
    name: str
    value: Any
    unit: str = ""
    timestamp: str = ""
    source: str = ""
    expected: str = ""   # 期望值（用于对比）
    abnormal: bool = False
    severity: int = 0    # 0=正常, 1=轻微, 2=中等, 3=严重


@dataclass
class ReasoningPath:
    """推理路径"""
    path_id: str
    description: str
    likelihood: float = 0.5   # 0-1
    consequences: List[str] = field(default_factory=list)
    pros: List[str] = field(default_factory=list)
    cons: List[str] = field(default_factory=list)
    final_score: float = 0.0
    risk_factors: List[str] = field(default_factory=list)
    estimated_cost: float = 0.0    # 预估成本
    estimated_time: str = ""        # 预估时间


@dataclass
class MindModel:
    """心智模型（25个）"""
    model_id: str
    name: str
    description: str
    perspective: str       # 视角描述
    questions: List[str]   # 该模型会问的问题
    enabled: bool = True


@dataclass
class MemoryEntry:
    """记忆条目"""
    id: str
    content: str
    timestamp: str
    category: str
    tags: List[str] = field(default_factory=list)
    importance: float = 0.5    # 0-1
    access_count: int = 0
    last_accessed: str = ""
    embedding: List[float] = field(default_factory=list)  # 向量化表示
    source: str = ""            # 来源
    linked_memory_ids: List[str] = field(default_factory=list)  # 关联记忆


@dataclass
class DecisionRecord:
    """决策记录"""
    id: str
    timestamp: str
    input: str
    reasoning_summary: str
    decision: str
    confidence: float
    approved: bool
    audit_hash: str
    risk_level: str = "low"
    requires_action: bool = False
    requires_confirmation: bool = False


@dataclass
class ReviewRecord:
    """复盘记录"""
    id: str
    timestamp: str
    original_decision: str
    outcome: str           # success, partial, failure, blocked
    deviation: float       # 偏离度 0-1
    lessons: List[str]
    patterns: List[str]
    user_satisfaction: float = 0.0  # 用户满意度 0-1


@dataclass
class SuccessPattern:
    """成功模式"""
    pattern_id: str
    description: str
    success_count: int = 0
    failure_count: int = 0
    last_validated: str = ""
    solidification: float = 0.0    # 0-1, 越高越稳定
    trigger_conditions: List[str] = field(default_factory=list)


@dataclass
class EvolutionRule:
    """演化规则"""
    rule_id: str
    description: str
    trigger_condition: str
    target_layer: str
    old_logic: str
    new_logic: str
    evidence: List[str] = field(default_factory=list)
    approved: bool = False
    executed: bool = False
    executed_at: str = ""
    rollback_available: bool = True


@dataclass
class MutationRecord:
    """变异记录"""
    mutation_id: str
    timestamp: str
    target: str        # 变异目标
    before: str        # 变异前
    after: str          # 变异后
    reason: str
    success: bool
    rollback_to: str = ""


@dataclass
class ModelProvider:
    """模型提供商"""
    provider_id: str
    name: str
    endpoint: str
    api_key_env: str
    model_name: str
    capability: List[str]
    cost_per_1k: float = 0.0
    latency_ms: int = 1000
    available: bool = True
    max_tokens: int = 4096
    context_window: int = 128000


@dataclass
class ModelResponse:
    """模型响应"""
    provider: str
    model: str
    content: str
    tokens_used: int = 0
    latency_ms: int = 0
    timestamp: str = ""
    success: bool = True
    error: str = ""
    finish_reason: str = ""


@dataclass
class Tool:
    """工具定义"""
    tool_id: str
    name: str
    description: str
    category: str
    permissions: List[str] = field(default_factory=list)
    enabled: bool = True
    parameters: Dict[str, Any] = field(default_factory=dict)
    examples: List[str] = field(default_factory=list)


@dataclass
class ExecutionResult:
    """执行结果"""
    execution_id: str
    tool_id: str
    success: bool
    output: Any = None
    error: str = ""
    duration_ms: int = 0
    timestamp: str = ""


@dataclass
class SimulationScenario:
    """模拟场景"""
    scenario_id: str
    description: str
    variables: Dict[str, Any]
    constraints: List[str]
    iterations: int
    success_criteria: str
    time_horizon: str = ""     # 模拟时间跨度


@dataclass
class SimulationResult:
    """模拟结果"""
    scenario_id: str
    total_runs: int
    success_count: int
    success_rate: float
    best_outcome: Dict[str, Any] = field(default_factory=dict)
    worst_outcome: Dict[str, Any] = field(default_factory=dict)
    insights: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    confidence: float = 0.0


@dataclass
class ConstitutionClause:
    """宪法条款"""
    id: str
    title: str
    content: str
    keywords: List[str]
    severity: int           # 1=警告, 2=拒绝, 3=一票否决
    enabled: bool = True
    created_at: str = ""
    last_triggered: str = ""


@dataclass
class AuditEntry:
    """审计条目"""
    id: str
    timestamp: str
    type: str                # decision, veto, execution, sandbox
    layer: str               # 涉及的层级
    user_input: str
    summary: str
    details: Dict[str, Any] = field(default_factory=dict)
    layers_involved: List[str] = field(default_factory=list)


@dataclass
class SystemConfig:
    """系统配置"""
    # L0 意志层
    constitution_enabled: bool = True
    veto_threshold: int = 3

    # L1 身份层
    identity_profile: Dict[str, Any] = field(default_factory=dict)
    boundary_enforcement: bool = True

    # L2 感知层
    data_sources: Dict[str, Any] = field(default_factory=dict)
    perception_depth: str = "full"   # quick, partial, full

    # L3 推理层
    active_models: List[str] = field(default_factory=list)
    reasoning_depth: int = 3
    max_paths: int = 5

    # L4 记忆层
    memory_max: int = 10000
    vector_enabled: bool = False
    embedding_model: str = "default"

    # L5 决策层
    risk_thresholds: Dict[str, float] = field(default_factory=dict)
    require_explicit_approval: bool = False

    # L6 经验层
    deviation_threshold: float = 0.3
    auto_review: bool = True

    # L7 演化层
    evolution_enabled: bool = True
    failure_threshold: int = 3

    # L8 接口层
    default_provider: str = "qwen"
    fallback_providers: List[str] = field(default_factory=list)
    mock_mode: bool = True

    # L9 执行层
    tools_enabled: bool = True
    safe_mode: bool = True

    # L10 沙盒层
    sandbox_enabled: bool = True
    sandbox_safe_threshold: float = 0.7
    max_iterations: int = 10000


# ─── Result Types (统一返回格式) ─────────────────────────────────

@dataclass
class LayerResult:
    """层级处理结果（统一格式）"""
    success: bool
    data: Any = None
    error: str = ""
    warnings: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class SystemRunResult:
    """系统运行结果（统一格式）"""
    status: str
    layers_involved: List[str] = field(default_factory=list)
    response: Any = None
    audit_id: str = ""
    vetoed: bool = False
    veto_reason: str = ""
    veto_layer: str = ""
    execution_result: Dict[str, Any] = field(default_factory=dict)
    evolution_result: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)


# ─── Re-exports for convenience ───────────────────────────────────

__all__ = [
    # Enums
    "LayerLevel",
    "RiskLevel",
    "MemoryCategory",
    "DecisionStatus",
    "OutcomeType",
    # Data Classes
    "RealityMetric",
    "ReasoningPath",
    "MindModel",
    "MemoryEntry",
    "DecisionRecord",
    "ReviewRecord",
    "SuccessPattern",
    "EvolutionRule",
    "MutationRecord",
    "ModelProvider",
    "ModelResponse",
    "Tool",
    "ExecutionResult",
    "SimulationScenario",
    "SimulationResult",
    "ConstitutionClause",
    "AuditEntry",
    "SystemConfig",
    # Result Types
    "LayerResult",
    "SystemRunResult",
]

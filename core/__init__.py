"""
Core 模块初始化
导出常量、类型、消息总线、宪法引擎、审计日志
"""

from .constants import (
    Layer, LAYER_OFFICIALS, MsgType, RiskLevel, RISK_THRESHOLDS,
    DecisionStatus, MemoryCategory, DataSourceType, ProviderID,
    ToolCategory, SYSTEM_PROMPT_TEMPLATE, PATHS,
    MAX_MEMORY_ENTRIES, MAX_HISTORY_MESSAGES, MAX_SANDBOX_ITERATIONS,
    MAX_MIND_MODELS, DEFAULT_CONTEXT_LIMIT,
)

# 类型定义（简化导入，避免循环依赖）
from .types import (
    LayerID, MessageType, DecisionStatus as DecisionStatusType,
    RiskLevel as RiskLevelType,
)

from .message import Message, MessageBus, LayerLevel as MsgLayerLevel
from .async_message import AsyncMessageBus, AsyncCallback, SyncCallback, AnyCallback

# 双重网关宪法
from .constitution import (
    GateType, VetoLevel,
    ConstitutionClause as DualClause,
    VetoResult, HardGateway, SoftGateway,
    Constitution as DualConstitution,
)

# 分级存储抽象层
from .memory_sal import (
    MemoryTier, ArchiveStatus,
    MemoryCategory as MemoryCategoryEnum,
    EmbeddingProvider, MemoryEntry as MemoryEntrySAL,
    KnowledgeNode, MemoryQuery, MemorySearchResult,
    WorkingMemory, SemanticDisk, MemoryLayer as MemoryLayerSAL,
)

# 神经总线
from .neural_bus import (
    EventType, Event, EventSubscription,
    EventStore, EventQueue, NeuralBus,
)

# 双核演化引擎
from .evolution import (
    EvolutionMode, EvolutionStatus, EvolutionTrigger,
    SuccessPattern as EvolutionPattern,
    EvolutionRule as EvolutionRuleType,
    MutationRecord as MutationRecordType,
    InnerEvolution, OuterEvolution, DualCoreEvolution,
)

# L2 感知层
from .l2_reality_sensor import (
    PerceptionType, DataQuality, DriftLevel,
    PerceptionEvent, RealitySnapshot, TruthClaim, DriftReport,
    MultimodalPerception, RealityDataPipeline, TruthReconciliation,
    RealitySensor,
)

# L3 推理层
from .l3_reasoning import (
    ReasoningStrategy, TaskStatus, PathScore,
    ReasoningTask, ReasoningPath, TaskDAG, ReasoningResult,
    TaskPlanner, MultiPathReasoning, ReasoningEngine,
)

# L9 代理层
from .l9_agent import (
    ToolCategory as AgentToolCategory,
    ExecutionStatus, RiskLevel as AgentRiskLevel,
    Tool, ExecutionRequest, ExecutionResult, UIAction,
    ToolRegistry, ExecutionEngine, AgentLayer,
)

from .audit import AuditLog

# ── 融合模块（billgaohub 项目深度改造）──────────────────────────────

# L0 合宪性层：主权意志网关（改造自 agent-sovereignty-rules + hermes-agent）
from .l0_sovereignty_gateway import (
    SovereigntyPrinciples,
    DecisionRightsPrinciples,
    SovereigntyVeto,
    SovereigntyGateway,
)

# L0 语义层：意图审查网关（改造自 hermes-agent SCAF 机制）
from .l0_semantic_gateway import (
    SemanticConfidence,
    SemanticAuditResult,
    SemanticRuleSet,
    SemanticGateway,
)

# L3 认知编排层：元认知调度引擎（改造自 teonu-worldmodel + deer-flow）
from .l3_cognitive_orchestrator import (
    CognitiveLaws,
    NodeState,
    CognitiveNode,
    CognitiveControl,
    ReasoningStrategy,
    StrategySelector,
    TaskNode,
    TaskDAG,
    CognitiveOrchestrator,
)

# L5 审计层：决策存证系统（改造自 ai-governance-framework）
from .l5_audit import (
    TriDomainScore,
    DecisionType,
    AuditEntry,
    DecisionAudit,
)

# L9 工具注册层：锦衣卫令牌系统（改造自 CLI-Anything + ipipq + smart-file-router）
from .l9_tool_harness import (
    ToolDomain,
    ToolSpec,
    ToolInvocation,
    IPIPQClassifier,
    SmartFileRouter,
    ToolHarnessRegistry,
)

__all__ = [
    # constants
    "Layer", "LAYER_OFFICIALS", "MsgType", "RiskLevel", "RISK_THRESHOLDS",
    "DecisionStatus", "MemoryCategory", "DataSourceType", "ProviderID",
    "ToolCategory", "SYSTEM_PROMPT_TEMPLATE", "PATHS",
    "MAX_MEMORY_ENTRIES", "MAX_HISTORY_MESSAGES", "MAX_SANDBOX_ITERATIONS",
    "MAX_MIND_MODELS", "DEFAULT_CONTEXT_LIMIT",
    # types
    "LayerID", "MessageType", "DecisionStatusType", "RiskLevelType",
    # core components
    "Message", "MessageBus", "AsyncMessageBus", 
    "AsyncCallback", "SyncCallback", "AnyCallback",
    # 双重网关
    "GateType", "VetoLevel", "DualClause", "VetoResult",
    "HardGateway", "SoftGateway", "DualConstitution",
    # 分级存储
    "MemoryTier", "ArchiveStatus", "MemoryCategoryEnum",
    "EmbeddingProvider", "MemoryEntrySAL", "KnowledgeNode",
    "MemoryQuery", "MemorySearchResult",
    "WorkingMemory", "SemanticDisk", "MemoryLayerSAL",
    # 神经总线
    "EventType", "Event", "EventSubscription",
    "EventStore", "EventQueue", "NeuralBus",
    # 双核演化
    "EvolutionMode", "EvolutionStatus", "EvolutionTrigger",
    "EvolutionPattern", "EvolutionRuleType", "MutationRecordType",
    "InnerEvolution", "OuterEvolution", "DualCoreEvolution",
    # L2 感知层
    "PerceptionType", "DataQuality", "DriftLevel",
    "PerceptionEvent", "RealitySnapshot", "TruthClaim", "DriftReport",
    "MultimodalPerception", "RealityDataPipeline", "TruthReconciliation",
    "RealitySensor",
    # L3 推理层
    "ReasoningStrategy", "TaskStatus", "PathScore",
    "ReasoningTask", "ReasoningPath", "TaskDAG", "ReasoningResult",
    "TaskPlanner", "MultiPathReasoning", "ReasoningEngine",
    # L9 代理层
    "AgentToolCategory", "ExecutionStatus", "AgentRiskLevel",
    "Tool", "ExecutionRequest", "ExecutionResult", "UIAction",
    "ToolRegistry", "ExecutionEngine", "AgentLayer",
    # 审计
    "AuditLog",
    # L0 合宪性层
    "SovereigntyPrinciples", "DecisionRightsPrinciples", "SovereigntyVeto", "SovereigntyGateway",
    # L0 语义层
    "SemanticConfidence", "SemanticAuditResult", "SemanticRuleSet", "SemanticGateway",
    # L3 认知编排层
    "CognitiveLaws", "NodeState", "CognitiveNode", "CognitiveControl",
    "ReasoningStrategy", "StrategySelector", "TaskNode", "TaskDAG", "CognitiveOrchestrator",
    # L5 审计层
    "TriDomainScore", "DecisionType", "AuditEntry", "DecisionAudit",
    # L9 工具注册层
    "ToolDomain", "ToolSpec", "ToolInvocation", "IPIPQClassifier", "SmartFileRouter", "ToolHarnessRegistry",
]

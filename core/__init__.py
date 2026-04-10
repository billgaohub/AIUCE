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

from .types import (
    LayerLevel, RiskLevel as RiskLevelEnum, MemoryCategory as MemCatEnum,
    DecisionStatus as DecisionStatusEnum, OutcomeType,
    RealityMetric, ReasoningPath, MindModel,
    MemoryEntry, DecisionRecord, ReviewRecord, SuccessPattern,
    EvolutionRule, MutationRecord,
    ModelProvider, ModelResponse,
    Tool, ExecutionResult,
    SimulationScenario, SimulationResult,
    ConstitutionClause, AuditEntry, SystemConfig,
    LayerResult, SystemRunResult,
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

from .audit import AuditLog

__all__ = [
    # constants
    "Layer", "LAYER_OFFICIALS", "MsgType", "RiskLevel", "RISK_THRESHOLDS",
    "DecisionStatus", "MemoryCategory", "DataSourceType", "ProviderID",
    "ToolCategory", "SYSTEM_PROMPT_TEMPLATE", "PATHS",
    "MAX_MEMORY_ENTRIES", "MAX_HISTORY_MESSAGES", "MAX_SANDBOX_ITERATIONS",
    "MAX_MIND_MODELS", "DEFAULT_CONTEXT_LIMIT",
    # types
    "LayerLevel", "RiskLevelEnum", "MemCatEnum", "DecisionStatusEnum", "OutcomeType",
    "RealityMetric", "ReasoningPath", "MindModel",
    "MemoryEntry", "DecisionRecord", "ReviewRecord", "SuccessPattern",
    "EvolutionRule", "MutationRecord",
    "ModelProvider", "ModelResponse",
    "Tool", "ExecutionResult",
    "SimulationScenario", "SimulationResult",
    "ConstitutionClause", "AuditEntry", "SystemConfig",
    "LayerResult", "SystemRunResult",
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
    # 审计
    "AuditLog",
]

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
from .constitution import Constitution
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
    "Message", "MessageBus", "Constitution", "AuditLog",
]

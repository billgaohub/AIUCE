"""
Eleven-Layer AI System
十一层架构 AI 系统

基于「十一层架构.md」构建，每层职责明确，层间通信规范。

架构层次：
L0  意志层 - 秦始皇/御书房   - 最高宪法，一票否决权
L1  身份层 - 诸葛亮/宗人府   - 人设管家，防止越权
L2  感知层 - 魏征/都察院    - 现实对账，只说真话
L3  推理层 - 张良/军机处    - 多路径推演，决策后果分析
L4  记忆层 - 司马迁/翰林院   - 全域语义索引，史料编纂
L5  决策层 - 包拯/大理寺    - 决策存证，审计日志
L6  经验层 - 曾国藩/吏部    - 复盘机制，偏离度扫描
L7  演化层 - 商鞅/中书省    - 内核重构，物理层面变法
L8  接口层 - 张骞/礼部      - 外事协议，算力外交
L9  代理层 - 韩信/锦衣卫    - 跨设备执行，物理工具调度
L10 沙盒层 - 庄子/钦天监    - 影子宇宙，模拟推演

层级实现说明：
- 根目录 lX_*.py: system.py 集成版本（接口稳定）
- core/lX_*.py:    增强版本（独立使用，功能更完整）
- 详见各文件头部注释
"""

# Core
from .core.message import Message, MessageBus, LayerLevel
from .core.constitution import Constitution, ConstitutionClause
from .core.audit import AuditLog
from .core.constants import (
    Layer, LAYER_OFFICIALS, MsgType, RiskLevel, RISK_THRESHOLDS,
    DecisionStatus, MemoryCategory, SYSTEM_PROMPT_TEMPLATE, PATHS,
)
from .core.types import (
    LayerLevel as CoreLayerLevel,
    MindModel, MemoryEntry, ReasoningPath,
    ModelProvider, ModelResponse,
    Tool, ExecutionResult,
    SimulationScenario, SimulationResult,
    LayerResult, SystemRunResult,
)
from .utils import (
    gen_id, gen_timestamp,
    truncate, extract_chinese_keywords, detect_intent,
    assess_risk, get_risk_level,
    simple_embedding, cosine_similarity, semantic_search,
    Timer, retry,
    format_layer_chain, format_score, format_duration,
    ensure_dir, safe_read_json, safe_write_json,
)

# Layers
from .l1_identity import IdentityLayer
from .l2_perception import PerceptionLayer
from .l3_reasoning import ReasoningLayer
from .l4_memory import MemoryLayer
from .l5_decision import DecisionLayer
from .l6_experience import ExperienceLayer
from .l7_evolution import EvolutionLayer
from .l8_interface import InterfaceLayer
from .l9_agent import AgentLayer
from .l10_sandbox import SandboxLayer

# Main System
from .system import ElevenLayerSystem, create_system

__all__ = [
    # Core
    "Message", "MessageBus", "LayerLevel", "Constitution", "AuditLog",
    # Constants
    "Layer", "LAYER_OFFICIALS", "MsgType", "RiskLevel", "RISK_THRESHOLDS",
    "DecisionStatus", "MemoryCategory", "SYSTEM_PROMPT_TEMPLATE", "PATHS",
    # Types
    "CoreLayerLevel", "MindModel", "MemoryEntry", "ReasoningPath",
    "ModelProvider", "ModelResponse",
    "Tool", "ExecutionResult",
    "SimulationScenario", "SimulationResult",
    "LayerResult", "SystemRunResult",
    # Utils
    "gen_id", "gen_timestamp",
    "truncate", "extract_chinese_keywords", "detect_intent",
    "assess_risk", "get_risk_level",
    "simple_embedding", "cosine_similarity", "semantic_search",
    "Timer", "retry",
    "format_layer_chain", "format_score", "format_duration",
    "ensure_dir", "safe_read_json", "safe_write_json",
    # Layers
    "IdentityLayer",
    "PerceptionLayer",
    "ReasoningLayer",
    "MemoryLayer",
    "DecisionLayer",
    "ExperienceLayer",
    "EvolutionLayer",
    "InterfaceLayer",
    "AgentLayer",
    "SandboxLayer",
    # System
    "ElevenLayerSystem",
    "create_system",
]

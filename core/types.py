"""
AIUCE Core Types - Type Annotations
AIUCE 核心类型定义

提供完整的类型注解支持
"""

from typing import (
    Any,
    Dict,
    List,
    Optional,
    Union,
    Callable,
    TypeVar,
    Generic,
    Awaitable,
)
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime
from pydantic import BaseModel, Field


# ═══════════════════════════════════════════════════════════════
# 基础类型
# ═══════════════════════════════════════════════════════════════

T = TypeVar("T")


class LayerID(Enum):
    """层级标识"""
    L0_WILL = 0
    L1_IDENTITY = 1
    L2_PERCEPTION = 2
    L3_REASONING = 3
    L4_MEMORY = 4
    L5_DECISION = 5
    L6_EXPERIENCE = 6
    L7_EVOLUTION = 7
    L8_INTERFACE = 8
    L9_AGENT = 9
    L10_SANDBOX = 10


class MessageType(Enum):
    """消息类型"""
    QUERY = "query"
    RESPONSE = "response"
    VETO = "veto"
    ERROR = "error"
    AUDIT = "audit"
    EVOLUTION = "evolution"


class DecisionStatus(Enum):
    """决策状态"""
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    VETOED = "vetoed"
    EXECUTED = "executed"


class RiskLevel(Enum):
    """风险等级"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


# ═══════════════════════════════════════════════════════════════
# 消息与事件
# ═══════════════════════════════════════════════════════════════

@dataclass
class Message:
    """层间消息"""
    source: LayerID
    target: LayerID
    msg_type: MessageType
    payload: Dict[str, Any]
    timestamp: datetime = field(default_factory=datetime.now)
    trace_id: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "source": self.source.value,
            "target": self.target.value,
            "msg_type": self.msg_type.value,
            "payload": self.payload,
            "timestamp": self.timestamp.isoformat(),
            "trace_id": self.trace_id,
        }


@dataclass
class Event:
    """事件溯源事件"""
    event_id: str
    event_type: str
    layer: LayerID
    data: Dict[str, Any]
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_json(self) -> str:
        """序列化为 JSON"""
        import json
        return json.dumps({
            "event_id": self.event_id,
            "event_type": self.event_type,
            "layer": self.layer.value,
            "data": self.data,
            "timestamp": self.timestamp.isoformat(),
            "metadata": self.metadata,
        })


# ═══════════════════════════════════════════════════════════════
# 层级结果
# ═══════════════════════════════════════════════════════════════

@dataclass
class LayerResult:
    """层级处理结果"""
    success: bool
    layer: LayerID
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    vetoed: bool = False
    veto_reason: Optional[str] = None
    audit_id: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


# ═══════════════════════════════════════════════════════════════
# 记忆系统
# ═══════════════════════════════════════════════════════════════

@dataclass
class MemoryNode:
    """记忆节点（DAG 结构）"""
    node_id: str
    content: str
    embedding: Optional[List[float]] = None
    parent_ids: List[str] = field(default_factory=list)
    child_ids: List[str] = field(default_factory=list)
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)
    source: str = "internal"  # internal / external
    
    def is_internal(self) -> bool:
        """是否为内部记忆"""
        return self.source == "internal"
    
    def is_external(self) -> bool:
        """是否为外部输入"""
        return self.source == "external"


@dataclass
class MemoryQuery:
    """记忆查询"""
    query: str
    top_k: int = 10
    filters: Dict[str, Any] = field(default_factory=dict)
    include_external: bool = False


@dataclass
class MemorySearchResult:
    """记忆搜索结果"""
    nodes: List[MemoryNode]
    scores: List[float]
    query: str
    total: int


# ═══════════════════════════════════════════════════════════════
# 决策系统
# ═══════════════════════════════════════════════════════════════

@dataclass
class Decision:
    """决策记录"""
    decision_id: str
    input: str
    reasoning: Dict[str, Any]
    decision: str
    status: DecisionStatus
    risk_level: RiskLevel
    timestamp: datetime = field(default_factory=datetime.now)
    layers_involved: List[LayerID] = field(default_factory=list)
    context: Dict[str, Any] = field(default_factory=dict)
    
    def to_audit_record(self) -> Dict[str, Any]:
        """转换为审计记录"""
        return {
            "decision_id": self.decision_id,
            "input": self.input,
            "decision": self.decision,
            "status": self.status.value,
            "risk_level": self.risk_level.value,
            "timestamp": self.timestamp.isoformat(),
            "layers": [l.value for l in self.layers_involved],
            "context_hash": hash(str(self.context)),
        }


# ═══════════════════════════════════════════════════════════════
# API Models (Pydantic)
# ═══════════════════════════════════════════════════════════════

class QueryRequest(BaseModel):
    """查询请求"""
    query: str = Field(..., min_length=1, max_length=10000)
    context: Optional[Dict[str, Any]] = None
    user_id: Optional[str] = None
    trace_id: Optional[str] = None


class QueryResponse(BaseModel):
    """查询响应"""
    status: str
    response: Optional[str] = None
    layers_involved: List[str] = []
    audit_id: Optional[str] = None
    vetoed: bool = False
    veto_reason: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


class HealthResponse(BaseModel):
    """健康检查响应"""
    status: str
    version: str
    uptime_seconds: float
    layers_status: Dict[str, bool]


class LayerStatusResponse(BaseModel):
    """层级状态响应"""
    layer_id: int
    layer_name: str
    status: str
    last_activity: Optional[datetime] = None
    metrics: Dict[str, Any] = Field(default_factory=dict)


# ═══════════════════════════════════════════════════════════════
# 回调类型
# ═══════════════════════════════════════════════════════════════

# 同步回调
SyncCallback = Callable[[Message], LayerResult]

# 异步回调
AsyncCallback = Callable[[Message], Awaitable[LayerResult]]

# 事件处理器
EventHandler = Callable[[Event], None]

# 演化回调
EvolutionCallback = Callable[[Dict[str, Any]], Dict[str, Any]]


# ═══════════════════════════════════════════════════════════════
# 泛型容器
# ═══════════════════════════════════════════════════════════════

@dataclass
class Result(Generic[T]):
    """通用结果包装"""
    success: bool
    value: Optional[T] = None
    error: Optional[str] = None
    
    @classmethod
    def ok(cls, value: T) -> "Result[T]":
        """成功结果"""
        return cls(success=True, value=value)
    
    @classmethod
    def err(cls, error: str) -> "Result[T]":
        """失败结果"""
        return cls(success=False, error=error)
    
    def is_ok(self) -> bool:
        return self.success
    
    def is_err(self) -> bool:
        return not self.success
    
    def unwrap(self) -> T:
        """获取值（失败时抛出异常）"""
        if not self.success:
            raise ValueError(f"Unwrap error: {self.error}")
        return self.value
    
    def unwrap_or(self, default: T) -> T:
        """获取值或默认值"""
        return self.value if self.success else default

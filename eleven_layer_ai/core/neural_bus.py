"""
AIUCE-Node 神经总线：事件溯源引擎
Event Sourcing Neural Bus

架构：
┌─────────────────────────────────────────────────────────┐
│              AIUCE-Node 神经总线                         │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  ┌───────────────────────────────────────────────────┐  │
│  │  事件队列 (Event Queue)                            │  │
│  │  - SQLite Queue / Redis Stream                    │  │
│  │  - 不可变事件 (Immutable Event)                    │  │
│  │  - 支持回放 (Replay)                              │  │
│  └───────────────────────────────────────────────────┘  │
│                         ↓                               │
│  ┌───────────────────────────────────────────────────┐  │
│  │  事件分发器 (Event Dispatcher)                     │  │
│  │  - 订阅/发布模式                                   │  │
│  │  - 层级路由                                        │  │
│  │  - 异步投递                                        │  │
│  └───────────────────────────────────────────────────┘  │
│                         ↓                               │
│  ┌───────────────────────────────────────────────────┐  │
│  │  事件存储 (Event Store)                            │  │
│  │  - 审计日志 (L5 大理寺)                            │  │
│  │  - 决策存证哈希                                    │  │
│  │  - 黑匣子数据                                      │  │
│  └───────────────────────────────────────────────────┘  │
│                                                          │
└─────────────────────────────────────────────────────────┘

设计原则：
1. 放弃简单的 JSON RPC 同步调用
2. 改用轻量级事件队列
3. 每次感知/推理/拦截均作为不可变事件发布
4. 强制所有 Payload 采用结构化 Agent-first JSON
"""

from typing import Dict, Any, List, Optional, Callable, Union
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import json
import os
import sqlite3
import threading
import queue
import hashlib
from collections import defaultdict
import uuid
from dataclasses import asdict, is_dataclass


def _default_json_serializer(obj):
    """自定义 JSON 序列化：支持 dataclass 和常见类型"""
    if is_dataclass(obj) and not isinstance(obj, type):
        return asdict(obj)
    if hasattr(obj, 'to_dict'):
        return obj.to_dict()
    if hasattr(obj, '__dict__'):
        return obj.__dict__
    return str(obj)


# ═══════════════════════════════════════════════════════════════
# 类型定义
# ═══════════════════════════════════════════════════════════════

class EventType(Enum):
    """事件类型"""
    # L0 意志层
    VETO = "veto"
    CONSTITUTION_CHECK = "constitution_check"
    
    # L1 身份层
    IDENTITY_CHECK = "identity_check"
    PERSONA_UPDATE = "persona_update"
    
    # L2 感知层
    PERCEPTION_CAPTURE = "perception_capture"
    REALITY_DATA = "reality_data"
    
    # L3 推理层
    REASONING_START = "reasoning_start"
    REASONING_RESULT = "reasoning_result"
    
    # L4 记忆层
    MEMORY_STORE = "memory_store"
    MEMORY_RETRIEVE = "memory_retrieve"
    MEMORY_ARCHIVE = "memory_archive"
    
    # L5 决策层
    DECISION_MADE = "decision_made"
    DECISION_REJECTED = "decision_rejected"
    
    # L6 经验层
    REVIEW_COMPLETE = "review_complete"
    PATTERN_DETECTED = "pattern_detected"
    
    # L7 演化层
    EVOLUTION_TRIGGERED = "evolution_triggered"
    EVOLUTION_COMPLETE = "evolution_complete"
    
    # L8 接口层
    MODEL_CALL = "model_call"
    MODEL_RESPONSE = "model_response"
    
    # L9 代理层
    EXECUTION_START = "execution_start"
    EXECUTION_RESULT = "execution_result"
    
    # L10 沙盒层
    SIMULATION_START = "simulation_start"
    SIMULATION_RESULT = "simulation_result"
    
    # 系统
    SYSTEM_ERROR = "system_error"
    SYSTEM_HEARTBEAT = "system_heartbeat"


@dataclass
class Event:
    """事件"""
    id: str
    type: EventType
    source: str  # 层级 ID (L0, L1, ..., L10)
    target: Optional[str]  # 目标层级（空=广播）
    payload: Dict[str, Any]
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    correlation_id: Optional[str] = None  # 关联 ID（同一请求的事件共享）
    causation_id: Optional[str] = None  # 因果 ID（导致此事件的事件）
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "id": self.id,
            "type": self.type.value,
            "source": self.source,
            "target": self.target,
            "payload": self.payload,
            "timestamp": self.timestamp,
            "correlation_id": self.correlation_id,
            "causation_id": self.causation_id,
            "metadata": self.metadata
        }
    
    def compute_hash(self) -> str:
        """计算事件哈希（用于审计）"""
        data = f"{self.id}{self.type.value}{self.source}{json.dumps(self.payload, sort_keys=True, default=_default_json_serializer)}"
        return hashlib.sha256(data.encode()).hexdigest()[:16]


@dataclass
class EventSubscription:
    """事件订阅"""
    subscriber_id: str
    event_types: List[EventType]
    callback: Callable[[Event], None]
    filter_fn: Optional[Callable[[Event], bool]] = None


# ═══════════════════════════════════════════════════════════════
# 事件存储 (Event Store)
# ═══════════════════════════════════════════════════════════════

class EventStore:
    """
    事件存储
    
    特性：
    1. 不可变事件（Append-only）
    2. 支持回放（Replay）
    3. 决策存证哈希
    4. 黑匣子数据
    """
    
    def __init__(self, storage_path: str = None):
        default_path = os.path.expanduser("~/.aiuce/events.db")
        self.storage_path = storage_path or default_path
        
        self._init_storage()
    
    def _init_storage(self):
        """初始化存储"""
        os.makedirs(os.path.dirname(self.storage_path), exist_ok=True)
        
        with sqlite3.connect(self.storage_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS events (
                    id TEXT PRIMARY KEY,
                    type TEXT NOT NULL,
                    source TEXT,
                    target TEXT,
                    payload TEXT,
                    timestamp TEXT,
                    correlation_id TEXT,
                    causation_id TEXT,
                    event_hash TEXT,
                    metadata TEXT
                )
            """)
            
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_events_type ON events(type)
            """)
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_events_source ON events(source)
            """)
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_events_correlation ON events(correlation_id)
            """)
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_events_timestamp ON events(timestamp)
            """)
            
            conn.commit()
    
    def append(self, event: Event) -> str:
        """追加事件（自动处理非 JSON 可序列化对象）"""
        event_hash = event.compute_hash()
        
        # 使用自定义序列化器处理 dataclass 等
        def _safe_json_dumps(obj, **kwargs):
            return json.dumps(obj, default=_default_json_serializer, **kwargs)
        
        with sqlite3.connect(self.storage_path) as conn:
            conn.execute(
                """INSERT INTO events 
                   (id, type, source, target, payload, timestamp, correlation_id, causation_id, event_hash, metadata)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    event.id,
                    event.type.value,
                    event.source,
                    event.target,
                    _safe_json_dumps(event.payload, ensure_ascii=False),
                    event.timestamp,
                    event.correlation_id,
                    event.causation_id,
                    event_hash,
                    _safe_json_dumps(event.metadata, ensure_ascii=False)
                )
            )
            conn.commit()
        
        return event_hash
    
    def get_by_id(self, event_id: str) -> Optional[Event]:
        """获取事件"""
        with sqlite3.connect(self.storage_path) as conn:
            cursor = conn.execute("SELECT * FROM events WHERE id = ?", (event_id,))
            row = cursor.fetchone()
            
            if row:
                return Event(
                    id=row[0],
                    type=EventType(row[1]),
                    source=row[2],
                    target=row[3],
                    payload=json.loads(row[4]),
                    timestamp=row[5],
                    correlation_id=row[6],
                    causation_id=row[7],
                    metadata=json.loads(row[9]) if row[9] else {}
                )
        
        return None
    
    def get_by_correlation(self, correlation_id: str) -> List[Event]:
        """获取相关事件链"""
        events = []
        
        with sqlite3.connect(self.storage_path) as conn:
            cursor = conn.execute(
                "SELECT * FROM events WHERE correlation_id = ? ORDER BY timestamp",
                (correlation_id,)
            )
            
            for row in cursor.fetchall():
                events.append(Event(
                    id=row[0],
                    type=EventType(row[1]),
                    source=row[2],
                    target=row[3],
                    payload=json.loads(row[4]),
                    timestamp=row[5],
                    correlation_id=row[6],
                    causation_id=row[7],
                    metadata=json.loads(row[9]) if row[9] else {}
                ))
        
        return events
    
    def replay(self, from_timestamp: str = None, to_timestamp: str = None) -> List[Event]:
        """回放事件"""
        events = []
        
        with sqlite3.connect(self.storage_path) as conn:
            query = "SELECT * FROM events WHERE 1=1"
            params = []
            
            if from_timestamp:
                query += " AND timestamp >= ?"
                params.append(from_timestamp)
            
            if to_timestamp:
                query += " AND timestamp <= ?"
                params.append(to_timestamp)
            
            query += " ORDER BY timestamp"
            
            cursor = conn.execute(query, params)
            
            for row in cursor.fetchall():
                events.append(Event(
                    id=row[0],
                    type=EventType(row[1]),
                    source=row[2],
                    target=row[3],
                    payload=json.loads(row[4]),
                    timestamp=row[5],
                    correlation_id=row[6],
                    causation_id=row[7],
                    metadata=json.loads(row[9]) if row[9] else {}
                ))
        
        return events
    
    def stats(self) -> Dict[str, Any]:
        """统计"""
        with sqlite3.connect(self.storage_path) as conn:
            total = conn.execute("SELECT COUNT(*) FROM events").fetchone()[0]
            
            by_type = {}
            cursor = conn.execute("SELECT type, COUNT(*) FROM events GROUP BY type")
            for row in cursor.fetchall():
                by_type[row[0]] = row[1]
            
            return {
                "total_events": total,
                "by_type": by_type,
                "storage_path": self.storage_path
            }


# ═══════════════════════════════════════════════════════════════
# 事件队列 (Event Queue)
# ═══════════════════════════════════════════════════════════════

class EventQueue:
    """
    事件队列
    
    支持：
    1. 内存队列（默认）
    2. Redis Stream（可选）
    """
    
    def __init__(self, max_size: int = 10000):
        self.queue: queue.Queue = queue.Queue(maxsize=max_size)
        self._subscribers: List[EventSubscription] = []
        self._running = False
        self._worker_thread: Optional[threading.Thread] = None
    
    def subscribe(
        self,
        subscriber_id: str,
        event_types: List[EventType],
        callback: Callable[[Event], None],
        filter_fn: Optional[Callable[[Event], bool]] = None
    ):
        """订阅事件"""
        subscription = EventSubscription(
            subscriber_id=subscriber_id,
            event_types=event_types,
            callback=callback,
            filter_fn=filter_fn
        )
        self._subscribers.append(subscription)
    
    def unsubscribe(self, subscriber_id: str):
        """取消订阅"""
        self._subscribers = [s for s in self._subscribers if s.subscriber_id != subscriber_id]
    
    def publish(self, event: Event):
        """发布事件"""
        self.queue.put(event)
    
    def start(self):
        """启动分发器"""
        if self._running:
            return
        
        self._running = True
        self._worker_thread = threading.Thread(target=self._dispatch_loop, daemon=True)
        self._worker_thread.start()
    
    def stop(self):
        """停止分发器"""
        self._running = False
        if self._worker_thread:
            self._worker_thread.join(timeout=5)
    
    def _dispatch_loop(self):
        """分发循环"""
        while self._running:
            try:
                event = self.queue.get(timeout=1)
                self._dispatch(event)
            except queue.Empty:
                continue
            except Exception as e:
                print(f"  [AIUCE-Node] 分发错误: {e}")
    
    def _dispatch(self, event: Event):
        """分发事件到订阅者"""
        for subscription in self._subscribers:
            # 类型过滤
            if event.type not in subscription.event_types:
                continue
            
            # 自定义过滤
            if subscription.filter_fn and not subscription.filter_fn(event):
                continue
            
            # 调用回调
            try:
                subscription.callback(event)
            except Exception as e:
                print(f"  [AIUCE-Node] 回调错误 ({subscription.subscriber_id}): {e}")


# ═══════════════════════════════════════════════════════════════
# 神经总线 (Neural Bus)
# ═══════════════════════════════════════════════════════════════

class NeuralBus:
    """
    AIUCE-Node 神经总线
    
    事件溯源架构：
    1. 所有层间通信通过事件总线
    2. 每次感知/推理/拦截作为不可变事件
    3. 强制结构化 JSON Payload
    4. 为 L5 大理寺提供审计数据
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        
        # 事件存储
        storage_path = self.config.get("storage_path")
        self.event_store = EventStore(storage_path)
        
        # 事件队列
        self.event_queue = EventQueue(
            max_size=self.config.get("queue_size", 10000)
        )
        
        # 当前关联 ID（用于追踪请求链）
        self._current_correlation_id: Optional[str] = None
        
        # 事件计数
        self._event_count = 0
        
        print(f"  [AIUCE-Node] 神经总线启动")
        print(f"    事件存储: {self.event_store.storage_path}")
    
    # ── 发布接口 ───────────────────────────────────────────────
    
    def emit(
        self,
        event_type: EventType,
        source: str,
        target: Optional[str] = None,
        payload: Optional[Dict[str, Any]] = None,
        causation_id: Optional[str] = None
    ) -> Event:
        """
        发布事件
        
        Args:
            event_type: 事件类型
            source: 来源层级
            target: 目标层级（空=广播）
            payload: 事件数据
            causation_id: 因果事件 ID
            
        Returns:
            事件对象
        """
        event_id = str(uuid.uuid4())[:8]
        
        event = Event(
            id=event_id,
            type=event_type,
            source=source,
            target=target,
            payload=payload or {},
            correlation_id=self._current_correlation_id,
            causation_id=causation_id
        )
        
        # 存储事件
        event_hash = self.event_store.append(event)
        event.metadata["hash"] = event_hash
        
        # 发布到队列
        self.event_queue.publish(event)
        
        self._event_count += 1
        
        return event
    
    # ── 订阅接口 ───────────────────────────────────────────────
    
    def subscribe(
        self,
        subscriber_id: str,
        event_types: List[EventType],
        callback: Callable[[Event], None],
        filter_fn: Optional[Callable[[Event], bool]] = None
    ):
        """订阅事件"""
        self.event_queue.subscribe(subscriber_id, event_types, callback, filter_fn)
        print(f"  [AIUCE-Node] 订阅者注册: {subscriber_id}")
    
    def unsubscribe(self, subscriber_id: str):
        """取消订阅"""
        self.event_queue.unsubscribe(subscriber_id)
    
    # ── 生命周期 ───────────────────────────────────────────────
    
    def start(self):
        """启动总线"""
        self.event_queue.start()
        print(f"  [AIUCE-Node] 神经总线运行中")
    
    def stop(self):
        """停止总线"""
        self.event_queue.stop()
        print(f"  [AIUCE-Node] 神经总线停止")
    
    # ── 关联 ID 管理 ───────────────────────────────────────────
    
    def begin_transaction(self) -> str:
        """开始事务（生成新的关联 ID）"""
        self._current_correlation_id = str(uuid.uuid4())[:8]
        return self._current_correlation_id
    
    def end_transaction(self):
        """结束事务"""
        self._current_correlation_id = None
    
    def get_correlation_id(self) -> Optional[str]:
        """获取当前关联 ID"""
        return self._current_correlation_id
    
    # ── 查询接口 ───────────────────────────────────────────────
    
    def get_event_chain(self, correlation_id: str) -> List[Event]:
        """获取事件链"""
        return self.event_store.get_by_correlation(correlation_id)
    
    def replay(self, from_timestamp: str = None, to_timestamp: str = None) -> List[Event]:
        """回放事件"""
        return self.event_store.replay(from_timestamp, to_timestamp)
    
    # ── 统计接口 ───────────────────────────────────────────────
    
    def stats(self) -> Dict[str, Any]:
        """统计"""
        store_stats = self.event_store.stats()
        return {
            **store_stats,
            "current_correlation_id": self._current_correlation_id,
            "session_event_count": self._event_count
        }


# ═══════════════════════════════════════════════════════════════
# 导出
# ═══════════════════════════════════════════════════════════════

__all__ = [
    "EventType",
    "Event",
    "EventSubscription",
    "EventStore",
    "EventQueue",
    "NeuralBus",
]

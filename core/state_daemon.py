"""
StateDaemon - 单一事实源状态守护进程
Single Source of Truth State Daemon

根据 ADR-001 事件架构设计：
- 只接受 4 类事件：UserIntent / AgentAction / StateMutation / Governance
- 所有状态变更必须通过 mutate() 方法，禁止直接 set_state()
- 支持从事件流 fold 重建状态
"""

from typing import Dict, Any, List, Optional, Callable
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import json
import os
import uuid
import hashlib


class EventType(Enum):
    """4 类核心事件 (ADR-001)"""
    USER_INTENT = "user_intent"
    AGENT_ACTION = "agent_action"
    STATE_MUTATION = "state_mutation"
    GOVERNANCE = "governance"


@dataclass
class StateEvent:
    """状态事件 (符合 ADR-001 Schema)"""
    id: str
    type: EventType
    source: str
    target: Optional[str] = None
    payload: Dict[str, Any] = field(default_factory=dict)
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    correlation_id: Optional[str] = None
    causation_id: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def compute_hash(self) -> str:
        data = f"{self.id}{self.type.value}{self.source}{json.dumps(self.payload, sort_keys=True)}"
        return hashlib.sha256(data.encode()).hexdigest()[:16]

    def to_dict(self) -> Dict[str, Any]:
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


@dataclass
class StateMutation:
    """状态变更"""
    path: str
    before: Any
    after: Any
    causation_id: Optional[str] = None

    def validate(self) -> bool:
        return self.path is not None and self.after is not None


class StateStore:
    """状态存储 - SQLite 持久化"""
    
    def __init__(self, storage_path: str = None):
        default_path = os.path.expanduser("~/.aiuce/state_store.db")
        self.storage_path = storage_path or default_path
        self._init_storage()
    
    def _init_storage(self):
        os.makedirs(os.path.dirname(self.storage_path), exist_ok=True)
        import sqlite3
        with sqlite3.connect(self.storage_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS state_store (
                    path TEXT PRIMARY KEY,
                    value TEXT,
                    updated_at TEXT,
                    updated_by TEXT
                )
            """)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS event_log (
                    id TEXT PRIMARY KEY,
                    type TEXT NOT NULL,
                    source TEXT,
                    target TEXT,
                    payload TEXT,
                    timestamp TEXT,
                    correlation_id TEXT,
                    causation_id TEXT,
                    event_hash TEXT
                )
            """)
            conn.commit()
    
    def get(self, path: str) -> Optional[Any]:
        import sqlite3
        with sqlite3.connect(self.storage_path) as conn:
            cursor = conn.execute("SELECT value FROM state_store WHERE path = ?", (path,))
            row = cursor.fetchone()
            if row:
                return json.loads(row[0])
        return None
    
    def _set(self, path: str, value: Any, updated_by: str = "system"):
        import sqlite3
        with sqlite3.connect(self.storage_path) as conn:
            conn.execute(
                "INSERT OR REPLACE INTO state_store (path, value, updated_at, updated_by) VALUES (?, ?, ?, ?)",
                (path, json.dumps(value, ensure_ascii=False), datetime.now().isoformat(), updated_by)
            )
            conn.commit()
    
    def get_all(self) -> Dict[str, Any]:
        import sqlite3
        result = {}
        with sqlite3.connect(self.storage_path) as conn:
            cursor = conn.execute("SELECT path, value FROM state_store")
            for row in cursor.fetchall():
                result[row[0]] = json.loads(row[1])
        return result
    
    def log_event(self, event: StateEvent):
        import sqlite3
        with sqlite3.connect(self.storage_path) as conn:
            conn.execute(
                "INSERT INTO event_log (id, type, source, target, payload, timestamp, correlation_id, causation_id, event_hash) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (event.id, event.type.value, event.source, event.target, json.dumps(event.payload, ensure_ascii=False), event.timestamp, event.correlation_id, event.causation_id, event.compute_hash())
            )
            conn.commit()
    
    def get_events(self, correlation_id: str = None) -> List[StateEvent]:
        import sqlite3
        query = "SELECT * FROM event_log WHERE 1=1"
        params = []
        if correlation_id:
            query += " AND correlation_id = ?"
            params.append(correlation_id)
        query += " ORDER BY timestamp"
        events = []
        with sqlite3.connect(self.storage_path) as conn:
            cursor = conn.execute(query, params)
            for row in cursor.fetchall():
                events.append(StateEvent(
                    id=row[0], type=EventType(row[1]), source=row[2], target=row[3],
                    payload=json.loads(row[4]), timestamp=row[5], correlation_id=row[6], causation_id=row[7]
                ))
        return events


class StateDaemon:
    """单一事实源状态守护进程"""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        storage_path = self.config.get("storage_path")
        self.store = StateStore(storage_path)
        self._current_correlation_id: Optional[str] = None
        self._event_count = 0
        self._subscribers: Dict[EventType, List[Callable]] = {
            EventType.USER_INTENT: [],
            EventType.AGENT_ACTION: [],
            EventType.STATE_MUTATION: [],
            EventType.GOVERNANCE: [],
        }
        print(f"  [StateDaemon] 单一事实源启动")
    
    def begin_transaction(self) -> str:
        self._current_correlation_id = str(uuid.uuid4())[:8]
        return self._current_correlation_id
    
    def end_transaction(self):
        self._current_correlation_id = None
    
    def get_correlation_id(self) -> Optional[str]:
        return self._current_correlation_id
    
    def emit_intent(self, user_id: str, intent: str, raw_input: str, channel: str = "cli") -> StateEvent:
        event = StateEvent(
            id=str(uuid.uuid4())[:8],
            type=EventType.USER_INTENT,
            source="external",
            payload={"user_id": user_id, "intent": intent, "raw_input": raw_input, "channel": channel},
            correlation_id=self._current_correlation_id
        )
        self._publish_event(event)
        self.store.log_event(event)
        return event
    
    def emit_action(self, agent_id: str, action_type: str, target: str = "", params: Dict[str, Any] = None, risk_level: str = "low") -> StateEvent:
        event = StateEvent(
            id=str(uuid.uuid4())[:8],
            type=EventType.AGENT_ACTION,
            source=agent_id,
            target=target,
            payload={"action_type": action_type, "target": target, "params": params or {}, "risk_level": risk_level},
            correlation_id=self._current_correlation_id
        )
        self._publish_event(event)
        self.store.log_event(event)
        return event
    
    def mutate(self, path: str, value: Any, causation_id: str = None) -> StateMutation:
        before = self.store.get(path)
        mutation = StateMutation(path=path, before=before, after=value, causation_id=causation_id)
        event = StateEvent(
            id=str(uuid.uuid4())[:8],
            type=EventType.STATE_MUTATION,
            source="StateDaemon",
            target=path,
            payload={"path": path, "before": before, "after": value},
            correlation_id=self._current_correlation_id,
            causation_id=causation_id
        )
        self._publish_event(event)
        self.store.log_event(event)
        self.store._set(path, value)
        return mutation
    
    def emit_governance(self, policy_id: str, decision: str, reason: str = "", severity: str = "info") -> StateEvent:
        event = StateEvent(
            id=str(uuid.uuid4())[:8],
            type=EventType.GOVERNANCE,
            source="governance",
            payload={"policy_id": policy_id, "decision": decision, "reason": reason, "severity": severity},
            correlation_id=self._current_correlation_id
        )
        self._publish_event(event)
        self.store.log_event(event)
        return event
    
    def _publish_event(self, event: StateEvent):
        self._event_count += 1
        for callback in self._subscribers.get(event.type, []):
            try:
                callback(event)
            except Exception as e:
                print(f"  [StateDaemon] 事件回调错误: {e}")
    
    def subscribe(self, event_type: EventType, callback: Callable[[StateEvent], None]):
        self._subscribers[event_type].append(callback)
    
    def get(self, path: str) -> Any:
        return self.store.get(path)
    
    def snapshot(self) -> Dict[str, Any]:
        return self.store.get_all()
    
    def fold_from_events(self, events: List[StateEvent] = None, from_timestamp: str = None) -> Dict[str, Any]:
        if events is None:
            events = self.store.get_events()
        state = {}
        for event in events:
            if event.type == EventType.STATE_MUTATION:
                path = event.payload.get("path")
                after = event.payload.get("after")
                if path and after is not None:
                    state[path] = after
        return state
    
    def rebuild_state(self, correlation_id: str) -> Dict[str, Any]:
        events = self.store.get_events(correlation_id=correlation_id)
        return self.fold_from_events(events)
    
    def stats(self) -> Dict[str, Any]:
        return {
            "current_correlation_id": self._current_correlation_id,
            "session_event_count": self._event_count,
            "state_paths": len(self.store.get_all()),
            "storage_path": self.store.storage_path
        }


__all__ = ["EventType", "StateEvent", "StateMutation", "StateStore", "StateDaemon"]
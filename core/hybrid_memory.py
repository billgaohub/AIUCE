"""
Hybrid Memory: 三层混合记忆架构
PASK MM (Memory Modeling) 模块实现

基于 arXiv:2604.08000 PASK 论文的 Hybrid Memory 设计
实现 Workspace / User / Global 三层记忆分离

架构：
┌─────────────────────────────────────┐
│ Workspace Memory (工作记忆)          │  ← 当前会话，临时，自动清除
│ - 当前对话上下文                      │
│ - 临时推理中间结果                     │
├─────────────────────────────────────┤
│ User Memory (用户记忆)               │  ← 用户长期偏好/历史
│ - 用户画像                            │
│ - 个人偏好                            │
│ - 交互历史摘要                        │
├─────────────────────────────────────┤
│ Global Memory (全局记忆)             │  ← 系统级知识
│ - 世界知识                            │
│ - 技能库                              │
│ - 宪法规则                            │
└─────────────────────────────────────┘
"""

from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import json
import hashlib
import os


class MemoryTier(Enum):
    """记忆层级"""
    WORKSPACE = "workspace"    # 工作记忆（当前会话）
    USER = "user"              # 用户记忆（长期偏好）
    GLOBAL = "global"          # 全局记忆（系统知识）


@dataclass
class MemoryEntry:
    """记忆条目"""
    id: str
    content: str
    tier: MemoryTier
    category: str
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    importance: float = 0.5
    access_count: int = 0
    last_accessed: str = ""
    tags: List[str] = field(default_factory=list)
    source: str = "internal"
    ttl: Optional[int] = None          # 存活时间（秒），None 表示永久
    
    def is_expired(self) -> bool:
        if self.ttl is None:
            return False
        try:
            created = datetime.fromisoformat(self.timestamp)
            age_seconds = (datetime.now() - created).total_seconds()
            return age_seconds > self.ttl
        except ValueError:
            return False
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "content": self.content,
            "tier": self.tier.value,
            "category": self.category,
            "timestamp": self.timestamp,
            "importance": self.importance,
            "access_count": self.access_count,
            "last_accessed": self.last_accessed,
            "tags": self.tags,
            "source": self.source,
            "ttl": self.ttl
        }


class WorkspaceMemory:
    """
    工作记忆层
    
    特点：
    - 当前会话临时存储
    - 自动过期（TTL 机制）
    - 推理中间结果
    - 容量有限，LRU 淘汰
    """
    
    DEFAULT_TTL = 3600           # 默认 1 小时过期
    MAX_ENTRIES = 100
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.entries: Dict[str, MemoryEntry] = {}
        self._content_hashes: set = set()
    
    def store(self, content: str, category: str = "temp", importance: float = 0.5, 
              tags: List[str] = None, ttl: int = None) -> Optional[str]:
        content_hash = hashlib.md5(content.encode()).hexdigest()
        if content_hash in self._content_hashes:
            return None
        
        entry_id = f"ws_{content_hash[:8]}"
        entry = MemoryEntry(
            id=entry_id,
            content=content,
            tier=MemoryTier.WORKSPACE,
            category=category,
            importance=importance,
            tags=tags or [],
            ttl=ttl or self.DEFAULT_TTL
        )
        
        self.entries[entry_id] = entry
        self._content_hashes.add(content_hash)
        
        if len(self.entries) > self.MAX_ENTRIES:
            self._evict_oldest()
        
        return entry_id
    
    def retrieve(self, query: str, top_k: int = 5) -> List[Tuple[MemoryEntry, float]]:
        self._cleanup_expired()
        results = []
        query_lower = query.lower()
        
        for entry in self.entries.values():
            score = 0.0
            if query_lower in entry.content.lower():
                score = 0.8
            elif any(query_lower in tag.lower() for tag in entry.tags):
                score = 0.6
            elif any(w in entry.content.lower() for w in query_lower.split() if len(w) > 1):
                score = 0.3
            
            if score > 0:
                entry.access_count += 1
                entry.last_accessed = datetime.now().isoformat()
                results.append((entry, score))
        
        results.sort(key=lambda x: x[1], reverse=True)
        return results[:top_k]
    
    def get_context_window(self, last_n: int = 10) -> List[str]:
        sorted_entries = sorted(self.entries.values(), key=lambda e: e.timestamp)
        return [e.content for e in sorted_entries[-last_n:]]
    
    def _cleanup_expired(self):
        expired_ids = [eid for eid, e in self.entries.items() if e.is_expired()]
        for eid in expired_ids:
            entry = self.entries.pop(eid)
            content_hash = hashlib.md5(entry.content.encode()).hexdigest()
            self._content_hashes.discard(content_hash)
    
    def _evict_oldest(self):
        if not self.entries:
            return
        oldest_id = min(self.entries, key=lambda k: self.entries[k].timestamp)
        entry = self.entries.pop(oldest_id)
        content_hash = hashlib.md5(entry.content.encode()).hexdigest()
        self._content_hashes.discard(content_hash)
    
    def clear(self):
        self.entries.clear()
        self._content_hashes.clear()
    
    def size(self) -> int:
        return len(self.entries)


class UserMemory:
    """
    用户记忆层
    
    特点：
    - 长期存储用户偏好/历史
    - 跨会话持久化
    - 基于重要性分级
    - 支持持久化到磁盘
    """
    
    MAX_ENTRIES = 1000
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.entries: Dict[str, MemoryEntry] = {}
        self._content_hashes: set = set()
        self._storage_path = self.config.get("storage_path", "")
        if self._storage_path:
            self._load()
    
    def store(self, content: str, category: str = "preference", importance: float = 0.5,
              tags: List[str] = None, source: str = "user") -> Optional[str]:
        content_hash = hashlib.md5(content.encode()).hexdigest()
        if content_hash in self._content_hashes:
            return None
        
        entry_id = f"usr_{content_hash[:8]}"
        entry = MemoryEntry(
            id=entry_id,
            content=content,
            tier=MemoryTier.USER,
            category=category,
            importance=importance,
            tags=tags or [],
            source=source,
            ttl=None
        )
        
        self.entries[entry_id] = entry
        self._content_hashes.add(content_hash)
        
        if len(self.entries) > self.MAX_ENTRIES:
            self._evict_low_importance()
        
        if self._storage_path:
            self._save()
        
        return entry_id
    
    def retrieve(self, query: str, top_k: int = 5) -> List[Tuple[MemoryEntry, float]]:
        results = []
        query_lower = query.lower()
        
        for entry in self.entries.values():
            score = 0.0
            if query_lower in entry.content.lower():
                score = 0.8 * entry.importance
            elif any(query_lower in tag.lower() for tag in entry.tags):
                score = 0.6 * entry.importance
            elif any(w in entry.content.lower() for w in query_lower.split() if len(w) > 1):
                score = 0.3 * entry.importance
            
            if score > 0:
                entry.access_count += 1
                entry.last_accessed = datetime.now().isoformat()
                results.append((entry, score))
        
        results.sort(key=lambda x: x[1], reverse=True)
        return results[:top_k]
    
    def update_preference(self, category: str, key: str, value: str):
        pref_content = f"{category}:{key}={value}"
        content_hash = hashlib.md5(pref_content.encode()).hexdigest()
        existing_id = f"usr_{content_hash[:8]}"
        
        if existing_id in self.entries:
            self.entries[existing_id].content = pref_content
            self.entries[existing_id].importance = min(1.0, self.entries[existing_id].importance + 0.1)
        else:
            self.store(pref_content, category=category, importance=0.7, tags=[category, key])
    
    def get_preferences(self, category: str = None) -> Dict[str, str]:
        prefs = {}
        for entry in self.entries.values():
            if entry.category in ("preference", category or entry.category):
                if "=" in entry.content:
                    k, v = entry.content.split("=", 1)
                    if ":" in k:
                        k = k.split(":", 1)[1]
                    prefs[k] = v
        return prefs
    
    def _evict_low_importance(self):
        if not self.entries:
            return
        lowest_id = min(self.entries, key=lambda k: self.entries[k].importance)
        entry = self.entries.pop(lowest_id)
        content_hash = hashlib.md5(entry.content.encode()).hexdigest()
        self._content_hashes.discard(content_hash)
    
    def _save(self):
        if not self._storage_path:
            return
        data = {
            "entries": {k: v.to_dict() for k, v in self.entries.items()},
            "config": self.config
        }
        try:
            os.makedirs(os.path.dirname(self._storage_path), exist_ok=True)
            with open(self._storage_path, 'w') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception:
            pass
    
    def _load(self):
        if not self._storage_path or not os.path.exists(self._storage_path):
            return
        try:
            with open(self._storage_path, 'r') as f:
                data = json.load(f)
            for k, v in data.get("entries", {}).items():
                v["tier"] = MemoryTier(v["tier"])
                self.entries[k] = MemoryEntry(**v)
                content_hash = hashlib.md5(v["content"].encode()).hexdigest()
                self._content_hashes.add(content_hash)
        except Exception:
            pass
    
    def size(self) -> int:
        return len(self.entries)


class GlobalMemory:
    """
    全局记忆层
    
    特点：
    - 系统级知识（不可被用户修改）
    - 技能库/宪法规则
    - 只读为主
    - 高优先级持久化
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.entries: Dict[str, MemoryEntry] = {}
        self._content_hashes: set = set()
        self._storage_path = self.config.get("storage_path", "")
        if self._storage_path:
            self._load()
    
    def store(self, content: str, category: str = "knowledge", importance: float = 0.7,
              tags: List[str] = None, source: str = "system") -> Optional[str]:
        content_hash = hashlib.md5(content.encode()).hexdigest()
        if content_hash in self._content_hashes:
            return None
        
        entry_id = f"glb_{content_hash[:8]}"
        entry = MemoryEntry(
            id=entry_id,
            content=content,
            tier=MemoryTier.GLOBAL,
            category=category,
            importance=importance,
            tags=tags or [],
            source=source,
            ttl=None
        )
        
        self.entries[entry_id] = entry
        self._content_hashes.add(content_hash)
        
        if self._storage_path:
            self._save()
        
        return entry_id
    
    def retrieve(self, query: str, top_k: int = 5) -> List[Tuple[MemoryEntry, float]]:
        results = []
        query_lower = query.lower()
        
        for entry in self.entries.values():
            score = 0.0
            if query_lower in entry.content.lower():
                score = 0.9 * entry.importance
            elif any(query_lower in tag.lower() for tag in entry.tags):
                score = 0.7 * entry.importance
            elif any(w in entry.content.lower() for w in query_lower.split() if len(w) > 1):
                score = 0.4 * entry.importance
            
            if score > 0:
                results.append((entry, score))
        
        results.sort(key=lambda x: x[1], reverse=True)
        return results[:top_k]
    
    def _save(self):
        if not self._storage_path:
            return
        data = {
            "entries": {k: v.to_dict() for k, v in self.entries.items()},
            "config": self.config
        }
        try:
            os.makedirs(os.path.dirname(self._storage_path), exist_ok=True)
            with open(self._storage_path, 'w') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception:
            pass
    
    def _load(self):
        if not self._storage_path or not os.path.exists(self._storage_path):
            return
        try:
            with open(self._storage_path, 'r') as f:
                data = json.load(f)
            for k, v in data.get("entries", {}).items():
                v["tier"] = MemoryTier(v["tier"])
                self.entries[k] = MemoryEntry(**v)
                content_hash = hashlib.md5(v["content"].encode()).hexdigest()
                self._content_hashes.add(content_hash)
        except Exception:
            pass
    
    def size(self) -> int:
        return len(self.entries)


class HybridMemory:
    """
    三层混合记忆系统
    
    统一接口，自动路由到合适的记忆层级
    
    使用方式：
    ```python
    memory = HybridMemory()
    
    # 工作记忆（当前会话临时数据）
    memory.store("用户正在讨论项目计划", tier=MemoryTier.WORKSPACE)
    
    # 用户记忆（长期偏好）
    memory.store("用户偏好深色模式", tier=MemoryTier.USER, category="preference")
    
    # 全局记忆（系统知识）
    memory.store("Python 3.10+ 支持 match 语句", tier=MemoryTier.GLOBAL, category="knowledge")
    
    # 统一检索（跨层级）
    results = memory.retrieve("项目计划")
    ```
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.workspace = WorkspaceMemory(self.config.get("workspace", {}))
        self.user = UserMemory(self.config.get("user", {}))
        self.global_mem = GlobalMemory(self.config.get("global", {}))
    
    def store(self, content: str, tier: MemoryTier = MemoryTier.WORKSPACE,
              category: str = "general", importance: float = 0.5,
              tags: List[str] = None, source: str = "internal",
              ttl: int = None) -> Optional[str]:
        if tier == MemoryTier.WORKSPACE:
            return self.workspace.store(content, category, importance, tags, ttl)
        elif tier == MemoryTier.USER:
            return self.user.store(content, category, importance, tags, source)
        elif tier == MemoryTier.GLOBAL:
            return self.global_mem.store(content, category, importance, tags, source)
        return None
    
    def retrieve(self, query: str, top_k: int = 5, 
                 tiers: List[MemoryTier] = None) -> List[Tuple[MemoryEntry, float]]:
        tiers = tiers or [MemoryTier.WORKSPACE, MemoryTier.USER, MemoryTier.GLOBAL]
        all_results = []
        
        if MemoryTier.WORKSPACE in tiers:
            all_results.extend(self.workspace.retrieve(query, top_k))
        if MemoryTier.USER in tiers:
            all_results.extend(self.user.retrieve(query, top_k))
        if MemoryTier.GLOBAL in tiers:
            all_results.extend(self.global_mem.retrieve(query, top_k))
        
        tier_priority = {
            MemoryTier.WORKSPACE: 1.1,
            MemoryTier.USER: 1.05,
            MemoryTier.GLOBAL: 1.0
        }
        all_results = [(e, s * tier_priority.get(e.tier, 1.0)) for e, s in all_results]
        all_results.sort(key=lambda x: x[1], reverse=True)
        
        return all_results[:top_k]
    
    def get_context_window(self, last_n: int = 10) -> List[str]:
        return self.workspace.get_context_window(last_n)
    
    def get_user_preferences(self, category: str = None) -> Dict[str, str]:
        return self.user.get_preferences(category)
    
    def update_user_preference(self, category: str, key: str, value: str):
        self.user.update_preference(category, key, value)
    
    def clear_workspace(self):
        self.workspace.clear()
    
    def stats(self) -> Dict[str, Any]:
        return {
            "workspace": self.workspace.size(),
            "user": self.user.size(),
            "global": self.global_mem.size()
        }

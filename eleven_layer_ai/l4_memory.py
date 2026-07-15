"""
L4 记忆层：司马迁/翰林院
Semantic Memory Index

职责：
1. 全域语义索引
2. 把所有碎片化事实编纂入库
3. 让过往一切皆成"史料"可供调取

增强版: core/l4_palace_memory.py (PalaceMemory + 宫殿记忆)
      core/l4_code_understanding.py (代码理解 + Leiden 社区检测)
本文件为 system.py 集成版本，接口稳定。
"""

from typing import Dict, Any, List, Optional, Tuple, Union, Protocol, runtime_checkable
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import json
import os


# ═══════════════════════════════════════════════════════════════
# 类型定义
# ═══════════════════════════════════════════════════════════════

class MemoryCategory(Enum):
    """记忆分类"""
    EVENT = "event"
    KNOWLEDGE = "knowledge"
    PREFERENCE = "preference"
    FACT = "fact"
    SKILL = "skill"
    ERROR = "error"
    INSIGHT = "insight"


class MemoryPriority(Enum):
    """记忆优先级"""
    LOW = 0.3
    NORMAL = 0.5
    HIGH = 0.7
    CRITICAL = 0.9


@runtime_checkable
class EmbeddingProvider(Protocol):
    """向量嵌入提供者协议"""
    def embed(self, text: str) -> List[float]:
        """将文本转换为向量"""
        ...


@dataclass
class MemoryEntry:
    """记忆条目"""
    id: str
    content: str
    timestamp: str
    category: str  # event, knowledge, preference, fact...
    tags: List[str] = field(default_factory=list)
    importance: float = 0.5  # 0-1, 重要性
    access_count: int = 0
    last_accessed: str = ""
    embedding: List[float] = field(default_factory=list)  # 向量化表示
    source: str = "internal"  # internal / external
    
    def is_expired(self, max_age_days: int = 365) -> bool:
        """检查记忆是否过期"""
        try:
            ts = datetime.fromisoformat(self.timestamp)
            age = (datetime.now() - ts).days
            return age > max_age_days
        except ValueError:
            return False
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "id": self.id,
            "content": self.content,
            "timestamp": self.timestamp,
            "category": self.category,
            "tags": self.tags,
            "importance": self.importance,
            "access_count": self.access_count,
            "last_accessed": self.last_accessed,
            "embedding_dim": len(self.embedding),
            "source": self.source,
        }


@dataclass
class MemoryQuery:
    """记忆查询"""
    query: str
    top_k: int = 10
    categories: Optional[List[MemoryCategory]] = None
    tags: Optional[List[str]] = None
    min_importance: float = 0.0
    include_expired: bool = False


@dataclass
class MemorySearchResult:
    """记忆搜索结果"""
    entries: List[MemoryEntry]
    scores: List[float]
    query: str
    total: int
    
    def top(self, n: int = 5) -> List[Tuple[MemoryEntry, float]]:
        """获取前N个结果"""
        return list(zip(self.entries[:n], self.scores[:n]))


@dataclass
class MemoryStats:
    """记忆统计"""
    total_entries: int
    by_category: Dict[str, int]
    by_importance: Dict[str, int]
    total_tags: int
    avg_access_count: float
    oldest_entry: Optional[str]
    newest_entry: Optional[str]


# ═══════════════════════════════════════════════════════════════
# 记忆层实现
# ═══════════════════════════════════════════════════════════════

class MemoryLayer:
    """
    记忆层 - 司马迁/翰林院
    
    "全域事实的语义索引，让过往一切碎片皆成史料"
    
    类似 RAG 的语义检索系统，
    但更强调时间序列和重要性排序。
    """

    def __init__(
        self,
        config: Optional[Dict[str, Any]] = None,
        embedding_provider: Optional[EmbeddingProvider] = None
    ):
        self.config = config or {}
        # 使用用户主目录下的 .aiuce 目录，避免硬编码路径
        default_path = os.path.expanduser("~/.aiuce/memory_store.json")
        self.storage_path = self.config.get("storage_path", default_path)
        self.memories: Dict[str, MemoryEntry] = {}
        self.index: Dict[str, List[str]] = {}  # 标签 -> 记忆ID
        self.max_memories = self.config.get("max_memories", 10000)
        self._embedding_provider = embedding_provider
        
        self._load_memories()

    def _load_memories(self) -> None:
        """从磁盘加载记忆"""
        if os.path.exists(self.storage_path):
            try:
                with open(self.storage_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    for entry_data in data.get("memories", []):
                        entry = MemoryEntry(**entry_data)
                        self.memories[entry.id] = entry
                        # 重建索引
                        for tag in entry.tags:
                            if tag not in self.index:
                                self.index[tag] = []
                            self.index[tag].append(entry.id)
                print(f"  [L4] 加载 {len(self.memories)} 条记忆")
            except Exception as e:
                print(f"  [L4] 加载记忆失败: {e}")

    def _save_memories(self) -> bool:
        """保存记忆到磁盘"""
        try:
            # 确保目录存在
            os.makedirs(os.path.dirname(self.storage_path), exist_ok=True)
            
            data = {
                "last_updated": datetime.now().isoformat(),
                "memories": [m.__dict__ for m in self.memories.values()]
            }
            with open(self.storage_path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            print(f"  [L4] 保存记忆失败: {e}")
            return False

    def store(
        self,
        content: str,
        category: Union[str, MemoryCategory] = "general",
        tags: Optional[List[str]] = None,
        importance: float = 0.5,
        source: str = "internal"
    ) -> str:
        """
        存储新记忆（自动去重）
        
        Args:
            content: 记忆内容
            category: 分类
            tags: 标签
            importance: 重要性 0-1
            source: 来源 (internal/external)
            
        Returns:
            记忆ID（已存在则返回 None）
        """
        import hashlib

        content_hash = hashlib.md5(content.encode()).hexdigest()
        if hasattr(self, '_content_hashes') and content_hash in self._content_hashes:
            return None

        import uuid
        
        if isinstance(category, MemoryCategory):
            category = category.value
        
        entry_id = str(uuid.uuid4())[:8]
        now = datetime.now().isoformat()
        
        # 初始化内容哈希集合（首次存储时）
        if not hasattr(self, '_content_hashes'):
            self._content_hashes = set()

        if content_hash in self._content_hashes:
            return None

        # 生成向量嵌入（如果有提供者）
        embedding = []
        if self._embedding_provider:
            try:
                embedding = self._embedding_provider.embed(content)
            except Exception:
                pass
        
        entry = MemoryEntry(
            id=entry_id,
            content=content,
            timestamp=now,
            category=category,
            tags=tags or [],
            importance=importance,
            embedding=embedding,
            source=source
        )
        
        self.memories[entry_id] = entry
        self._content_hashes.add(content_hash)
        
        # 更新索引
        for tag in entry.tags:
            if tag not in self.index:
                self.index[tag] = []
            self.index[tag].append(entry_id)
        
        # 检查容量
        if len(self.memories) > self.max_memories:
            self._evict_low_importance()
        
        self._save_memories()
        return entry_id

    def retrieve(
        self,
        query: str,
        top_k: int = 5
    ) -> List[Tuple[MemoryEntry, float]]:
        """
        检索相关记忆
        
        Args:
            query: 查询字符串
            top_k: 返回数量
            
        Returns:
            (记忆, 相关度分数) 列表
        """
        results: List[Tuple[MemoryEntry, float]] = []
        
        # 简单关键词匹配（可替换为向量检索）
        query_lower = query.lower()
        
        for entry in self.memories.values():
            score = 0.0
            
            # 内容匹配
            if query_lower in entry.content.lower():
                score += 0.5
            
            # 标签匹配
            for tag in entry.tags:
                if query_lower in tag.lower():
                    score += 0.3
            
            # 重要性加权
            score *= (0.5 + 0.5 * entry.importance)
            
            # 访问频率加权
            score *= (1.0 + 0.1 * min(entry.access_count, 10))
            
            if score > 0:
                results.append((entry, score))
        
        # 排序并返回
        results.sort(key=lambda x: x[1], reverse=True)
        return results[:top_k]

    def search(self, query: MemoryQuery) -> MemorySearchResult:
        """
        高级搜索
        
        Args:
            query: 搜索查询对象
            
        Returns:
            搜索结果
        """
        candidates = list(self.memories.values())
        
        # 分类过滤
        if query.categories:
            cat_values = [c.value for c in query.categories]
            candidates = [e for e in candidates if e.category in cat_values]
        
        # 标签过滤
        if query.tags:
            candidates = [
                e for e in candidates
                if any(tag in e.tags for tag in query.tags)
            ]
        
        # 重要性过滤
        candidates = [e for e in candidates if e.importance >= query.min_importance]
        
        # 文本匹配
        query_lower = query.query.lower()
        scored: List[Tuple[MemoryEntry, float]] = []
        
        for entry in candidates:
            score = 0.0
            
            if query_lower in entry.content.lower():
                score += 0.5
            
            for tag in entry.tags:
                if query_lower in tag.lower():
                    score += 0.3
            
            score *= (0.5 + 0.5 * entry.importance)
            
            if score > 0:
                scored.append((entry, score))
        
        # 排序
        scored.sort(key=lambda x: x[1], reverse=True)
        
        entries = [s[0] for s in scored[:query.top_k]]
        scores = [s[1] for s in scored[:query.top_k]]
        
        return MemorySearchResult(
            entries=entries,
            scores=scores,
            query=query.query,
            total=len(scored)
        )

    def get(self, entry_id: str) -> Optional[MemoryEntry]:
        """获取单条记忆"""
        entry = self.memories.get(entry_id)
        if entry:
            entry.access_count += 1
            entry.last_accessed = datetime.now().isoformat()
        return entry

    def update(self, entry_id: str, updates: Dict[str, Any]) -> bool:
        """更新记忆"""
        if entry_id not in self.memories:
            return False
        
        entry = self.memories[entry_id]
        for key, value in updates.items():
            if hasattr(entry, key):
                setattr(entry, key, value)
        
        self._save_memories()
        return True

    def delete(self, entry_id: str) -> bool:
        """删除记忆"""
        if entry_id not in self.memories:
            return False
        
        entry = self.memories[entry_id]
        
        # 从索引中移除
        for tag in entry.tags:
            if tag in self.index and entry_id in self.index[tag]:
                self.index[tag].remove(entry_id)
        
        del self.memories[entry_id]
        self._save_memories()
        return True

    def stats(self) -> MemoryStats:
        """获取记忆统计"""
        by_category: Dict[str, int] = {}
        by_importance: Dict[str, int] = {"low": 0, "medium": 0, "high": 0}
        
        for entry in self.memories.values():
            # 分类统计
            cat = entry.category
            by_category[cat] = by_category.get(cat, 0) + 1
            
            # 重要性统计
            if entry.importance < 0.3:
                by_importance["low"] += 1
            elif entry.importance < 0.7:
                by_importance["medium"] += 1
            else:
                by_importance["high"] += 1
        
        timestamps = [e.timestamp for e in self.memories.values()]
        timestamps.sort()
        
        return MemoryStats(
            total_entries=len(self.memories),
            by_category=by_category,
            by_importance=by_importance,
            total_tags=len(self.index),
            avg_access_count=sum(e.access_count for e in self.memories.values()) / max(len(self.memories), 1),
            oldest_entry=timestamps[0] if timestamps else None,
            newest_entry=timestamps[-1] if timestamps else None
        )

    def _evict_low_importance(self) -> int:
        """驱逐低重要性记忆"""
        # 按重要性和访问次数排序
        sorted_entries = sorted(
            self.memories.values(),
            key=lambda e: (e.importance, e.access_count)
        )
        
        # 驱逐最低的 10%
        to_evict = max(1, len(self.memories) // 10)
        for entry in sorted_entries[:to_evict]:
            self.delete(entry.id)
        
        return to_evict

    def process(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """
        处理层间消息
        
        Args:
            message: 层间消息
            
        Returns:
            处理结果
        """
        msg_type = message.get("type", "")
        payload = message.get("payload", {})
        
        if msg_type == "store":
            entry_id = self.store(
                content=payload.get("content", ""),
                category=payload.get("category", "general"),
                tags=payload.get("tags"),
                importance=payload.get("importance", 0.5)
            )
            return {"status": "stored", "entry_id": entry_id}
        
        elif msg_type == "retrieve":
            results = self.retrieve(
                query=payload.get("query", ""),
                top_k=payload.get("top_k", 5)
            )
            return {
                "status": "retrieved",
                "results": [(e.id, e.content, s) for e, s in results]
            }
        
        elif msg_type == "search":
            query = MemoryQuery(
                query=payload.get("query", ""),
                top_k=payload.get("top_k", 10),
                categories=[MemoryCategory(c) for c in payload.get("categories", [])] if payload.get("categories") else None,
                tags=payload.get("tags"),
                min_importance=payload.get("min_importance", 0.0)
            )
            result = self.search(query)
            return {
                "status": "searched",
                "total": result.total,
                "entries": [e.to_dict() for e in result.entries]
            }
        
        elif msg_type == "stats":
            stats = self.stats()
            return {
                "status": "stats",
                "total_entries": stats.total_entries,
                "by_category": stats.by_category,
                "avg_access_count": stats.avg_access_count
            }
        
        else:
            return {"status": "unknown_type", "type": msg_type}


# ═══════════════════════════════════════════════════════════════
# 导出
# ═══════════════════════════════════════════════════════════════

__all__ = [
    "MemoryCategory",
    "MemoryPriority",
    "EmbeddingProvider",
    "MemoryEntry",
    "MemoryQuery",
    "MemorySearchResult",
    "MemoryStats",
    "MemoryLayer",
]

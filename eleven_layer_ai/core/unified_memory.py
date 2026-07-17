"""
统一记忆层 (Unified Memory Layer) —— AIUCE 官方记忆层

收敛设计（见 aiuce_memory_review.md §判定）：
- 完整性内核  : core.l4_palace_memory.PalaceEngine  (Raw Verbatim + SHA-256 哈希链，防篡改/可审计)
- 检索服务后端: core.memory_sal.WorkingMemory        (SQLite + FTS5，热检索；语义走 embedding)
- 接口形态     : core.hybrid_memory 的 Workspace/User/Global 三层路由 (tier)
- 语义路径     : 已修 C1 —— 关键词 + embedding 余弦混合，可注入真实 provider

为什么这样收敛：
1. 治理/安全框架第一性原理是"可追溯、不可抵赖、不丢约束"。
   Palace 的 Raw Verbatim + 哈希链让 AI 无法决定"什么值得记"，且可被 L5 审计校验。
2. Palace 的 Markdown 存储与确定性关键词检索不能单独撑生产，
   故检索落到 SAL 的 SQLite+FTS5（成熟后端），并异步归档到知识图谱（冷语义）。
3. Hybrid 的 tier 路由（工作/用户/全局）是最对的"门面"模型，吸收其概念。
4. l4_memory.MemoryLayer 的纯 JSON 子串存储是最弱的一环，退役为兼容门面。

接口兼容性：本类刻意实现与旧 l4_memory.MemoryLayer 完全一致的对外方法
(store / retrieve / search / stats / process / memories 属性)，
因此 system.py 与现有测试无需改动即可切换。
"""

from typing import Dict, Any, List, Optional, Tuple, Union
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import os
import hashlib

from .l4_palace_memory import PalaceEngine, PalaceWing, PalaceMemory
from .memory_sal import WorkingMemory
from .hybrid_memory import MemoryTier as HybridTier
from .memory_schema import MemoryEntryBase
from .vector_memory import VectorIndex, DeterministicEmbeddingProvider
from ..utils import simple_embedding, cosine_similarity


class MemoryCategory(Enum):
    """记忆分类（与旧 l4_memory 对齐，便于兼容）"""
    EVENT = "event"
    KNOWLEDGE = "knowledge"
    PREFERENCE = "preference"
    FACT = "fact"
    SKILL = "skill"
    ERROR = "error"
    INSIGHT = "insight"
    USER_INPUT = "user_input"
    GENERAL = "general"


@dataclass
class MemoryEntry(MemoryEntryBase):
    """
    统一记忆条目（对外视图）—— 继承统一基座 MemoryEntryBase（I1/I2 收敛）

    注意：本类是为了与旧 l4_memory.MemoryEntry 接口兼容而定义的轻量视图对象，
    实际存储由 PalaceEngine（真相源）与 WorkingMemory（检索索引）分别持有。
    """

    embedding: List[float] = field(default_factory=list)
    tier: str = "global"

    def is_expired(self, max_age_days: int = 365) -> bool:
        try:
            ts = datetime.fromisoformat(self.timestamp)
            return (datetime.now() - ts).days > max_age_days
        except ValueError:
            return False

    def to_dict(self) -> Dict[str, Any]:
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
            "tier": self.tier,
        }


# tier -> PalaceWing 的映射（把 Hybrid 的三层概念落到 Palace 的空间索引）
_TIER_TO_WING = {
    "workspace": PalaceWing.PROJECTS,
    "user": PalaceWing.PEOPLE,
    "global": PalaceWing.GENERAL,
    "general": PalaceWing.GENERAL,
}


class UnifiedMemoryLayer:
    """
    L4 统一记忆层（官方）

    司马迁/翰林院 —— 全域事实的语义索引，让过往一切碎片皆成史料。

    组成：
    - self.palace   : PalaceEngine（Raw Verbatim + 哈希链，真相源）
    - self.serving  : WorkingMemory（SQLite+FTS5，热检索索引）
    """

    def __init__(
        self,
        config: Optional[Dict[str, Any]] = None,
        embedding_provider: Optional[Any] = None,
    ):
        self.config = config or {}
        self._embedding_provider = embedding_provider

        # 兼容旧配置键 storage_path：从它推导出 Palace 与 SAL 的路径，
        # 使 system.py / 旧测试无需改动即可切换。
        storage_path = self.config.get("storage_path")
        if storage_path:
            base = os.path.dirname(os.path.expanduser(storage_path))
            palace_cfg = self.config.setdefault("palace", {})
            palace_cfg.setdefault("palace_path", os.path.join(base, "palace"))
            serving_cfg = self.config.setdefault("serving", {})
            serving_cfg.setdefault("storage_path", os.path.join(base, "serving.db"))

        # 完整性内核：Palace（Raw Verbatim + 哈希链）
        palace_cfg = self.config.get("palace", {})
        palace_path = palace_cfg.get("palace_path", "~/.aiuce/palace")
        self.palace = PalaceEngine(palace_path=palace_path)

        # 检索服务后端：SAL WorkingMemory（SQLite + FTS5）
        serving_cfg = self.config.get("serving", {})
        self.serving = WorkingMemory(serving_cfg)

        # 真实向量索引（grok 式 KNN）：默认用确定性离线 provider（零依赖、可复现），
        # 可注入真实语义模型（sentence-transformers / OpenAI 等）。
        self._embedding_provider = embedding_provider or DeterministicEmbeddingProvider()
        self._dim = len(self._embed("__dim_probe__"))
        self._vector_index = VectorIndex(dim=self._dim)
        # store 时持久化的向量缓存（sal_id -> 向量），避免检索时反复重算
        self._embeddings: Dict[str, List[float]] = {}

        # 内容哈希集合：跨会话去重（C2 修复 —— 必须从已加载的索引重建，
        # 否则新实例加载磁盘数据后 _content_hashes 为空，去重失效）
        # 同时重建向量索引，保证重启/跨会话后真实向量召回仍一致。
        self._content_hashes: set = set()
        for entry in self.serving.entries.values():
            self._content_hashes.add(hashlib.md5(entry.content.encode()).hexdigest())
            vec = self._embed(entry.content)
            self._embeddings[entry.id] = vec
            self._vector_index.add(entry.id, vec)

    # ── 内部工具 ───────────────────────────────────────────────

    def _embed(self, text: str) -> List[float]:
        """文本向量化：优先 provider，否则零依赖 simple_embedding"""
        if self._embedding_provider:
            try:
                return self._embedding_provider.embed(text)
            except Exception:
                pass
        return simple_embedding(text)

    def _to_entry(self, record, tier: str = "global", importance: float = 0.5) -> MemoryEntry:
        """把 Palace MemoryRecord 投影为对外 MemoryEntry 视图"""
        return MemoryEntry(
            id=record.record_id,
            content=record.raw_text,
            timestamp=record.timestamp.isoformat(),
            category=record.metadata.get("category", "general"),
            tags=list(record.tags),
            importance=importance,
            access_count=0,
            last_accessed="",
            embedding=[],
            source=record.speaker,
            tier=tier,
        )

    # ── 存储接口 ───────────────────────────────────────────────

    def store(
        self,
        content: str,
        category: Union[str, MemoryCategory] = "general",
        tags: Optional[List[str]] = None,
        importance: float = 0.5,
        source: str = "internal",
        tier: Union[str, HybridTier] = "global",
    ) -> Optional[str]:
        """
        存储记忆（跨层统一入口）

        - 写入 Palace 真相源（Raw Verbatim + 哈希链）
        - 同步写入 SAL 检索索引（SQLite+FTS5）
        - tier 决定 Palace 的空间索引 wing（Workspace/User/Global）

        Returns:
            记忆 ID；若内容重复（跨重启仍生效，已修 C2）返回 None
        """
        content_hash = hashlib.md5(content.encode()).hexdigest()
        if content_hash in self._content_hashes:
            return None

        if isinstance(category, MemoryCategory):
            category = category.value
        if isinstance(tier, HybridTier):
            tier = tier.value

        wing = _TIER_TO_WING.get(tier, PalaceWing.GENERAL)
        room_id = f"room-{datetime.now().strftime('%Y%m%d')}"

        record = self.palace.store(
            raw_text=content,
            room_id=room_id,
            wing=wing,
            hall=category,
            speaker=source or "internal",
            tags=tags or [],
            metadata={"category": category, "tier": tier, "importance": importance},
        )

        # 检索索引（SAL）：用于快速/语义检索
        sal_id = self.serving.store(
            content=content,
            category=category,
            tags=tags or [],
            importance=importance,
        )

        # 真实向量持久化 + KNN 索引（grok 式）：store 时即落向量，
        # 使后续 retrieve 走 VectorIndex 做真实语义召回，而非仅在关键词候选上重排。
        if sal_id is not None:
            vec = self._embed(content)
            self._embeddings[sal_id] = vec
            self._vector_index.add(sal_id, vec)

        self._content_hashes.add(content_hash)
        return record.record_id

    # ── 检索接口 ───────────────────────────────────────────────

    def retrieve(
        self,
        query: str,
        top_k: int = 5,
        min_score: float = 0.0,
    ) -> List[Tuple[MemoryEntry, float]]:
        """
        检索记忆（关键词 + 语义混合，已修 C1）

        优先走 SAL 的 FTS5 + 语义索引；Palace 的确定性关键词作为补充召回。
        """
        # 主召回：SAL 检索索引（FTS5 + LIKE + 内存兜底）
        served = self.serving.retrieve(query, top_k * 2)
        results: List[Tuple[MemoryEntry, float]] = []
        seen: set = set()

        query_vec = self._embed(query)

        # 1) 主召回：SAL 关键词（FTS5 + LIKE + 内存兜底）—— 关键词得分 + 语义重排
        for entry, score in served:
            vec = self._embeddings.get(entry.id, self._embed(entry.content))
            sem = max(0.0, cosine_similarity(query_vec, vec))
            combined = 0.6 * score + 0.4 * sem
            combined *= (0.5 + 0.5 * entry.importance)
            if combined > min_score:
                view = MemoryEntry(
                    id=entry.id, content=entry.content, timestamp=entry.timestamp,
                    category=entry.category, tags=entry.tags, importance=entry.importance,
                    access_count=entry.access_count, last_accessed=entry.last_accessed,
                    embedding=vec, source=entry.source, tier="global",
                )
                results.append((view, combined))
                seen.add(entry.id)

        # 2) 真实向量 KNN 召回（grok 式）：独立于关键词重叠，召回语义相近条目
        #    —— 这是「真实向量记忆」的核心：即便查询与条目无任何词汇重合，
        #       只要语义向量接近即可被召回（旧实现只能在关键词候选上重排，做不到）。
        try:
            for hid, sim in self._vector_index.search(query_vec, top_k * 2):
                if hid in seen:
                    continue
                ventry = self.serving.entries.get(hid)
                if ventry is None:
                    continue
                vec = self._embeddings.get(hid, self._embed(ventry.content))
                sem = max(0.0, sim)
                # 纯向量召回：combined = 语义相似度 × 重要性因子（同样受 min_score 门控）
                combined = sem * (0.5 + 0.5 * ventry.importance)
                if combined > min_score:
                    view = MemoryEntry(
                        id=ventry.id, content=ventry.content, timestamp=ventry.timestamp,
                        category=ventry.category, tags=ventry.tags, importance=ventry.importance,
                        access_count=ventry.access_count, last_accessed=ventry.last_accessed,
                        embedding=vec, source=ventry.source, tier="global",
                    )
                    results.append((view, combined))
                    seen.add(hid)
        except Exception:
            pass

        # 3) 补充召回：Palace 确定性关键词（避免 SAL 索引遗漏）
        try:
            palace_hits = self.palace.retrieve(query, max_records=top_k)
            for record, score, _room in palace_hits:
                if record.record_id in seen:
                    continue
                sem = max(0.0, cosine_similarity(query_vec, self._embed(record.raw_text)))
                combined = 0.6 * score + 0.4 * sem
                results.append((self._to_entry(record), combined))
                seen.add(record.record_id)
        except Exception:
            pass

        results.sort(key=lambda x: x[1], reverse=True)
        return results[:top_k]

    def search(self, query) -> Any:
        """
        高级搜索（兼容旧 l4_memory.MemorySearchResult 形态）

        query 可为字符串或 MemoryQuery 对象；此处做简易适配。
        """
        if hasattr(query, "query"):
            q = query.query
            top_k = getattr(query, "top_k", 10)
        else:
            q = query
            top_k = 10
        scored = self.retrieve(q, top_k=top_k)
        entries = [s[0] for s in scored]
        scores = [s[1] for s in scored]
        # 返回一个最小兼容对象
        return type("MemorySearchResult", (), {
            "entries": entries, "scores": scores,
            "query": q, "total": len(scored),
            "top": lambda n=5: list(zip(entries[:n], scores[:n])),
        })()

    # ── 兼容性属性/方法 ────────────────────────────────────────

    @property
    def memories(self) -> Dict[str, MemoryEntry]:
        """兼容旧接口：以 dict 形式暴露检索索引中的条目（供 len() 等使用）"""
        out: Dict[str, MemoryEntry] = {}
        for entry in self.serving.entries.values():
            out[entry.id] = MemoryEntry(
                id=entry.id, content=entry.content, timestamp=entry.timestamp,
                category=entry.category, tags=entry.tags, importance=entry.importance,
                access_count=entry.access_count, last_accessed=entry.last_accessed,
                embedding=self._embeddings.get(entry.id, []), source=entry.source, tier="global",
            )
        return out

    def stats(self) -> Dict[str, Any]:
        """统计"""
        serving_stats = self.serving.stats()
        palace_stats = self.palace.stats()
        return {
            "total_entries": serving_stats.get("total_entries", 0),
            "vector_index_size": self._vector_index.size(),
            "embedding_provider": type(self._embedding_provider).__name__,
            "l1_serving": serving_stats,
            "palace": palace_stats,
            "by_wing": palace_stats.get("by_wing", {}),
        }

    def process(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """层间消息处理（兼容旧 contract）"""
        msg_type = message.get("type", "")
        payload = message.get("payload", {})
        if msg_type == "store":
            entry_id = self.store(
                content=payload.get("content", ""),
                category=payload.get("category", "general"),
                tags=payload.get("tags"),
                importance=payload.get("importance", 0.5),
                source=payload.get("source", "internal"),
            )
            return {"status": "stored", "entry_id": entry_id}
        elif msg_type == "retrieve":
            results = self.retrieve(payload.get("query", ""), top_k=payload.get("top_k", 5))
            return {"status": "retrieved", "results": [(e.id, e.content, s) for e, s in results]}
        elif msg_type == "stats":
            st = self.stats()
            return {"status": "stats", "total_entries": st.get("total_entries", 0)}
        else:
            return {"status": "unknown_type", "type": msg_type}


__all__ = [
    "MemoryCategory",
    "MemoryEntry",
    "UnifiedMemoryLayer",
]

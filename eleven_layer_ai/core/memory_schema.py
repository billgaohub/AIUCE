"""
统一记忆数据契约 (Memory Schema Contract) —— 收敛 AIUCE 四套记忆实现（评审 I1 / I2）

问题背景：
- l4_memory / memory_sal / hybrid_memory / l4_palace_memory 各有一套互不兼容的
  记忆数据模型与后端，维护成本 ×4，且无法组合（见 aiuce_memory_review.md §2.2 I1/I2）。

本模块给出**最小收敛契约**，而非强行合并：
1. MemoryEntryBase —— 所有 MemoryEntry 的公共字段基座（id/content/timestamp/
   category/importance/access_count/last_accessed/tags/source）+ is_expired / to_dict 形态。
   各具体 MemoryEntry 继承本基类，仅追加各自专有字段（tier 枚举 / embedding / ttl 等），
   并保持 to_dict / is_expired 的各自行为不变 —— 从而既统一字段契约，又不破坏既有消费者
   （l3_reasoning 用 HybridMemory、core/types.py 用 memory_sal.MemoryEntry）。
2. MemoryBackend —— 所有记忆后端共享的接口 Protocol（store / retrieve(min_score) /
   stats / process）。以 Protocol 形式存在，不强制运行时继承，故 system.py / l3_reasoning
   等调用方零改动即可获得类型契约。

设计约束（防止 scope creep / 破坏既有行为）：
- 子类专有字段放在基类字段之后，且全部带默认值（基类已为公共字段提供默认值），
  保证所有既有 MemoryEntry(**dict) / MemoryEntry(id=..., content=...) 关键字构造零改动。
- Protocol 仅做结构约束，不引入运行时依赖或继承链。
"""

from typing import (
    Any,
    Dict,
    List,
    Optional,
    Protocol,
    Tuple,
    runtime_checkable,
)
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class MemoryEntryBase:
    """
    记忆条目公共字段契约（I1/I2 收敛基座）

    所有具体记忆层的 MemoryEntry 都应继承本基类，以获得一致的字段集合与
    is_expired / to_dict 形态。子类追加的专有字段（tier / embedding / ttl 等）
    放在本基类字段之后。
    """

    id: str
    content: str
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    category: str = "general"
    importance: float = 0.5
    access_count: int = 0
    last_accessed: str = ""
    tags: List[str] = field(default_factory=list)
    source: str = "internal"

    def is_expired(self, max_age_days: int = 365) -> bool:
        """
        基于年龄的过期判定（默认契约；子类可按 TTL 等语义重载）

        Returns:
            该条目是否超过 max_age_days 天（解析失败视为未过期）
        """
        try:
            ts = datetime.fromisoformat(self.timestamp)
            return (datetime.now() - ts).days > max_age_days
        except ValueError:
            return False

    def to_dict(self) -> Dict[str, Any]:
        """公共字段序列化为 dict（子类应重载以追加专有字段）"""
        return {
            "id": self.id,
            "content": self.content,
            "timestamp": self.timestamp,
            "category": self.category,
            "importance": self.importance,
            "access_count": self.access_count,
            "last_accessed": self.last_accessed,
            "tags": self.tags,
            "source": self.source,
        }


@runtime_checkable
class MemoryBackend(Protocol):
    """
    记忆后端统一接口契约（I2 抽象）

    所有记忆存储/检索实现（memory_sal.MemoryLayer、hybrid_memory.HybridMemory、
    unified_memory.UnifiedMemoryLayer）都应满足该 Protocol。作为 Protocol 使用，
    不强制继承，故既有调用方（l3_reasoning / system.py）无需改动。

    线程安全契约（I5）：实现方应在单写者模型下，用锁（如 threading.RLock）保护
    store / retrieve / evict / save 等读改写复合操作，确保并发调用不破坏
    entries / _content_hashes / 磁盘文件的一致性。hybrid_memory 的三层子记忆已按此
    契约加锁；memory_sal.WorkingMemory 亦使用 RLock。
    """

    def store(self, content: str, *args: Any, **kwargs: Any) -> Optional[str]:
        """存储记忆，返回记忆 ID；重复内容可视实现返回 None"""
        ...

    def retrieve(
        self, query: str, top_k: int = 5, min_score: float = 0.0, **kwargs: Any
    ) -> List[Tuple[Any, float]]:
        """检索记忆，返回 (条目, 分数) 列表；分数已归一化到 [0,1]"""
        ...

    def stats(self) -> Dict[str, Any]:
        """返回后端统计信息"""
        ...


__all__ = [
    "MemoryEntryBase",
    "MemoryBackend",
]

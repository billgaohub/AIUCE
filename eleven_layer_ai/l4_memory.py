"""
L4 记忆层：司马迁/翰林院（兼容门面）

本模块曾是独立的 JSON 存储实现（纯子串检索，AIUCE 记忆系统中最弱的一环）。
根据 aiuce_memory_review.md 的收敛判定，官方记忆层已收敛为
core.unified_memory.UnifiedMemoryLayer：

    - 完整性内核  : core.l4_palace_memory.PalaceEngine  (Raw Verbatim + SHA-256 哈希链)
    - 检索服务后端: core.memory_sal.WorkingMemory        (SQLite + FTS5，热检索)
    - 接口形态     : core.hybrid_memory 的 Workspace/User/Global 三层路由 (tier)
    - 语义路径     : 已修 C1 —— 关键词 + embedding 余弦混合

为最小化改动面、避免破坏既有的 system.py / demo / 测试，本模块仅保留对外类名
MemoryLayer 作为 UnifiedMemoryLayer 的兼容别名。旧的 JSON 存储实现已退役。
"""

from .core.unified_memory import (
    UnifiedMemoryLayer,
    MemoryCategory,
    MemoryEntry,
)

# 兼容别名：对外仍叫 MemoryLayer，内部已是收敛后的统一记忆层
MemoryLayer = UnifiedMemoryLayer

__all__ = [
    "MemoryLayer",
    "UnifiedMemoryLayer",
    "MemoryCategory",
    "MemoryEntry",
]

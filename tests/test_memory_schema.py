"""
Contract tests for core.memory_schema (I1/I2 收敛基座)

Locks in that:
- 三个具体 MemoryEntry 都继承自统一基座 MemoryEntryBase
- 三个记忆后端都结构满足 MemoryBackend Protocol
- 公共字段契约 / to_dict 形态保持一致，且 hybrid 的 TTL 字段 round-trip 不丢
"""

import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from eleven_layer_ai.core.memory_schema import MemoryEntryBase, MemoryBackend
from eleven_layer_ai.core.memory_sal import MemoryEntry as SALMemoryEntry, MemoryTier as SALTier, ArchiveStatus
from eleven_layer_ai.core.hybrid_memory import MemoryEntry as HybridMemoryEntry, MemoryTier as HybridTier
from eleven_layer_ai.core.unified_memory import MemoryEntry as UnifiedMemoryEntry
from eleven_layer_ai.core.memory_sal import MemoryLayer as SALMemoryLayer
from eleven_layer_ai.core.hybrid_memory import HybridMemory
from eleven_layer_ai.core.unified_memory import UnifiedMemoryLayer


class TestMemoryEntryBase(unittest.TestCase):
    def test_three_entries_inherit_base(self):
        for cls in (SALMemoryEntry, HybridMemoryEntry, UnifiedMemoryEntry):
            self.assertTrue(
                issubclass(cls, MemoryEntryBase),
                f"{cls.__module__}.{cls.__name__} 应继承 MemoryEntryBase",
            )

    def test_base_common_fields_present(self):
        e = MemoryEntryBase(id="x", content="hello")
        d = e.to_dict()
        for key in ("id", "content", "timestamp", "category", "importance",
                    "access_count", "last_accessed", "tags", "source"):
            self.assertIn(key, d)
        self.assertEqual(d["content"], "hello")

    def test_base_is_expired_default_contract(self):
        e = MemoryEntryBase(id="x", content="c")
        self.assertFalse(e.is_expired())  # 新建条目不应过期


class TestMemoryEntryRoundTrip(unittest.TestCase):
    def test_hybrid_entry_ttl_round_trip(self):
        e = HybridMemoryEntry(id="h1", content="偏好深色", tier=HybridTier.USER, ttl=3600)
        d = e.to_dict()
        self.assertEqual(d["tier"], "user")
        self.assertEqual(d["ttl"], 3600)
        # 重建：严格镜像 hybrid._load 的 MemoryEntry(**v)（v["tier"] 先转回枚举）
        restored = HybridMemoryEntry(**{**d, "tier": HybridTier(d["tier"])})
        self.assertEqual(restored.tier, HybridTier.USER)
        self.assertEqual(restored.ttl, 3600)
        self.assertEqual(restored.content, "偏好深色")

    def test_sal_entry_dag_fields_round_trip(self):
        e = SALMemoryEntry(
            id="s1", content="DAG 节点", tier=SALTier.L1_WORKING,
            parent_id="p0", children_ids=["c1", "c2"],
            archive_status=ArchiveStatus.ARCHIVED,
        )
        d = e.to_dict()
        self.assertEqual(d["parent_id"], "p0")
        self.assertEqual(d["children_ids"], ["c1", "c2"])
        self.assertEqual(d["archive_status"], "archived")


class TestMemoryBackendConformance(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.mkdtemp()

    def test_backends_satisfy_protocol(self):
        sal = SALMemoryLayer({
            "working_memory": {"storage_path": os.path.join(self._tmp, "a.db")},
            "semantic_disk": {"storage_path": os.path.join(self._tmp, "kg")},
        })
        hm = HybridMemory({
            "user": {"storage_path": os.path.join(self._tmp, "u.json")},
            "global": {"storage_path": os.path.join(self._tmp, "g.json")},
        })
        um = UnifiedMemoryLayer({"storage_path": os.path.join(self._tmp, "m.json")})

        for backend in (sal, hm, um):
            self.assertIsInstance(backend, MemoryBackend)


if __name__ == "__main__":
    unittest.main()

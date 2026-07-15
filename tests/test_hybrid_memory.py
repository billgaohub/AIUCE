"""
Regression tests for core.hybrid_memory (Workspace / User / Global + HybridMemory)

Covers the behaviours the review flagged as untested (I6):
- dedup within session (Workspace / User / Global)
- persistence across reload (User / Global, JSON-backed)
- retrieve ranking (matching substring first)
- TTL expiry (Workspace)
- capacity eviction (Workspace / User)
- HybridMemory tier routing + dedup

These tests pin CURRENT correct behaviour so later P1/P2 refactors
(I3 min_score / I4 batch eviction / I5 thread-safety) cannot regress silently.
"""

import os
import sys
import tempfile
import unittest
from datetime import datetime, timedelta

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from eleven_layer_ai.core.hybrid_memory import (
    WorkspaceMemory,
    UserMemory,
    GlobalMemory,
    HybridMemory,
    MemoryTier,
)


def _tmp_json(name: str) -> str:
    d = tempfile.mkdtemp()
    return os.path.join(d, name)


class TestWorkspaceMemory(unittest.TestCase):
    def setUp(self):
        self.wm = WorkspaceMemory({})

    def test_store_dedup_within_session(self):
        self.wm.store("重复内容", category="temp", importance=0.5)
        dup = self.wm.store("重复内容", category="temp", importance=0.5)
        self.assertIsNone(dup)
        self.assertEqual(self.wm.size(), 1)

    def test_retrieve_ranks_matching_entry_first(self):
        self.wm.store("人工智能治理框架", category="fact", importance=0.9)
        self.wm.store("今天天气晴朗", category="fact", importance=0.9)
        results = self.wm.retrieve("人工智能治理", top_k=1)
        self.assertEqual(len(results), 1)
        self.assertIn("人工智能治理", results[0][0].content)

    def test_ttl_expiry_removes_entry(self):
        eid = self.wm.store("临时推理中间结果", category="temp", importance=0.5, ttl=10)
        # 强制把时间戳改为 20 秒前 -> 超过 ttl
        self.wm.entries[eid].timestamp = (datetime.now() - timedelta(seconds=20)).isoformat()
        self.wm._cleanup_expired()
        self.assertEqual(self.wm.size(), 0)

    def test_capacity_eviction_keeps_size_bounded(self):
        for i in range(WorkspaceMemory.MAX_ENTRIES + 5):
            self.wm.store(f"工作记忆条目 {i}", category="temp", importance=0.5)
        self.assertLessEqual(self.wm.size(), WorkspaceMemory.MAX_ENTRIES)

    def test_batch_eviction_drops_to_capacity(self):
        # I4：超容时一次性淘汰到容量上限，而非每次只删 1 条
        self.wm.MAX_ENTRIES = 3
        for i in range(6):
            self.wm.store(f"工作记忆条目 {i}", category="temp", importance=0.5)
        self.assertEqual(self.wm.size(), 3)

    def test_retrieve_min_score_filters_weak_matches(self):
        # I3：min_score 阈值应截断弱命中
        self.wm.store("治理框架需要多层约束", category="fact", importance=0.9)
        self.wm.store("一段完全无关的菜谱分享", category="fact", importance=0.9)
        results = self.wm.retrieve("治理框架", top_k=5, min_score=0.5)
        self.assertEqual(len(results), 1)
        self.assertIn("治理框架", results[0][0].content)

    def test_retrieve_scores_normalized_to_unit_interval(self):
        # I3：分数裁剪到 [0,1]
        self.wm.store("归一化测试条目", category="fact", importance=1.0)
        results = self.wm.retrieve("归一化测试", top_k=5)
        self.assertTrue(results)
        for _, score in results:
            self.assertGreaterEqual(score, 0.0)
            self.assertLessEqual(score, 1.0)


class TestUserMemory(unittest.TestCase):
    def setUp(self):
        self.path = _tmp_json("user.json")
        self.um = UserMemory({"storage_path": self.path})

    def test_store_dedup_within_session(self):
        self.um.store("偏好深色模式", category="preference", importance=0.7)
        dup = self.um.store("偏好深色模式", category="preference", importance=0.7)
        self.assertIsNone(dup)
        self.assertEqual(self.um.size(), 1)

    def test_persistence_across_reload(self):
        self.um.store("用户长期偏好A", category="preference", importance=0.8)
        um2 = UserMemory({"storage_path": self.path})
        self.assertEqual(um2.size(), 1)
        self.assertTrue(any("用户长期偏好A" in e.content for e in um2.entries.values()))

    def test_eviction_low_importance_keeps_size_bounded(self):
        # 缩小容量阈值以触发驱逐逻辑
        self.um.MAX_ENTRIES = 3
        self.um.store("低重要a", category="fact", importance=0.1)
        self.um.store("低重要b", category="fact", importance=0.1)
        self.um.store("低重要c", category="fact", importance=0.1)
        self.um.store("低重要d", category="fact", importance=0.1)
        self.um.store("低重要e", category="fact", importance=0.1)
        self.assertLessEqual(self.um.size(), 3)

    def test_batch_eviction_low_importance_to_capacity(self):
        # I4：超容时一次性淘汰到容量上限
        self.um.MAX_ENTRIES = 3
        for i in range(6):
            self.um.store(f"低重要{i}", category="fact", importance=0.1)
        self.assertEqual(self.um.size(), 3)

    def test_flush_forces_persist(self):
        self.um.store("需落盘的内容", category="preference", importance=0.7)
        self.um.flush()
        um2 = UserMemory({"storage_path": self.path})
        self.assertEqual(um2.size(), 1)

    def test_update_preference_idempotent(self):
        self.um.update_preference("ui", "theme", "dark")
        self.um.update_preference("ui", "theme", "dark")
        self.assertEqual(self.um.size(), 1)
        prefs = self.um.get_preferences("ui")
        self.assertEqual(prefs.get("theme"), "dark")


class TestGlobalMemory(unittest.TestCase):
    def setUp(self):
        self.path = _tmp_json("global.json")
        self.gm = GlobalMemory({"storage_path": self.path})

    def test_store_dedup_within_session(self):
        self.gm.store("Python 支持 match 语句", category="knowledge", importance=0.7)
        dup = self.gm.store("Python 支持 match 语句", category="knowledge", importance=0.7)
        self.assertIsNone(dup)
        self.assertEqual(self.gm.size(), 1)

    def test_persistence_across_reload(self):
        self.gm.store("系统级知识条目", category="knowledge", importance=0.7)
        gm2 = GlobalMemory({"storage_path": self.path})
        self.assertEqual(gm2.size(), 1)


class TestHybridMemory(unittest.TestCase):
    def setUp(self):
        self.user_path = _tmp_json("h_user.json")
        self.global_path = _tmp_json("h_global.json")
        self.hm = HybridMemory({
            "user": {"storage_path": self.user_path},
            "global": {"storage_path": self.global_path},
        })

    def test_tier_routing_stores_to_correct_backend(self):
        self.hm.store("当前会话临时数据", tier=MemoryTier.WORKSPACE, category="temp")
        self.hm.store("用户偏好深色", tier=MemoryTier.USER, category="preference")
        self.hm.store("Python 3.10 match", tier=MemoryTier.GLOBAL, category="knowledge")
        self.assertEqual(self.hm.workspace.size(), 1)
        self.assertEqual(self.hm.user.size(), 1)
        self.assertEqual(self.hm.global_mem.size(), 1)

    def test_dedup_per_tier(self):
        self.hm.store("重复会话内容", tier=MemoryTier.WORKSPACE, category="temp")
        dup = self.hm.store("重复会话内容", tier=MemoryTier.WORKSPACE, category="temp")
        self.assertIsNone(dup)

    def test_retrieve_merges_tiers(self):
        self.hm.store("治理框架需要多层约束", tier=MemoryTier.GLOBAL, category="knowledge", importance=0.9)
        self.hm.store("今天天气晴朗", tier=MemoryTier.WORKSPACE, category="temp", importance=0.9)
        results = self.hm.retrieve("治理框架", top_k=1)
        self.assertEqual(len(results), 1)
        self.assertIn("治理框架", results[0][0].content)

    def test_stats_shape(self):
        self.hm.store("x", tier=MemoryTier.WORKSPACE)
        st = self.hm.stats()
        self.assertIn("workspace", st)
        self.assertIn("user", st)
        self.assertIn("global", st)

    def test_concurrent_store_retrieve_is_safe(self):
        # I5：并发 store/retrieve 不应破坏 entries / _content_hashes 一致性
        import threading
        errors = []

        def worker(i):
            try:
                self.hm.store(f"并发条目 {i}", tier=MemoryTier.WORKSPACE, category="temp")
                self.hm.retrieve("并发", top_k=3)
            except Exception as e:  # noqa: BLE001
                errors.append(e)

        threads = [threading.Thread(target=worker, args=(i,)) for i in range(32)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        self.assertEqual(errors, [], f"并发访问抛出异常: {errors}")
        # 32 条内容各不相同 -> 去重后应为 32，且结构未被破坏
        self.assertEqual(self.hm.workspace.size(), 32)


if __name__ == "__main__":
    unittest.main()

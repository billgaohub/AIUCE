"""
Regression tests for core.memory_sal (L4 SAL: WorkingMemory / SemanticDisk / MemoryLayer)

Covers the behaviours the review flagged as untested (I6):
- WorkingMemory: store / persistence-across-reload / retrieve ranking / FTS+LIKE fallback
- SemanticDisk: archive builds knowledge nodes / persistence
- SAL MemoryLayer facade: store -> retrieve / auto-archive threshold

These tests must NOT mutate production code; they only pin current correct behaviour
so later P1/P2 refactors (I3/I4/I5) cannot silently regress.
"""

import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from eleven_layer_ai.core import memory_sal
from eleven_layer_ai.core.memory_sal import (
    WorkingMemory,
    SemanticDisk,
    MemoryLayer,
    MemoryEntry,
)


def _tmp(path_suffix: str) -> str:
    d = tempfile.mkdtemp()
    return os.path.join(d, path_suffix)


class TestWorkingMemory(unittest.TestCase):
    def setUp(self):
        self.db = _tmp("lcm.db")
        self.wm = WorkingMemory({"storage_path": self.db})

    def test_store_returns_id_and_tracks_entry(self):
        eid = self.wm.store("人工智能治理需要多层约束", category="fact", importance=0.9)
        self.assertIsInstance(eid, str)
        self.assertIn(eid, self.wm.entries)
        self.assertEqual(self.wm.stats()["total_entries"], 1)

    def test_persistence_across_reload(self):
        self.wm.store("持久化测试条目", category="fact", importance=0.7)
        # 模拟进程重启：从同一 SQLite 重新加载
        wm2 = WorkingMemory({"storage_path": self.db})
        self.assertEqual(wm2.stats()["total_entries"], 1)
        self.assertTrue(
            any("持久化测试条目" in e.content for e in wm2.entries.values())
        )

    def test_retrieve_ranks_matching_entry_first(self):
        self.wm.store("人工智能治理需要多层约束", category="fact", importance=0.9)
        self.wm.store("今天天气晴朗适合散步", category="fact", importance=0.9)
        results = self.wm.retrieve("人工智能治理", top_k=1)
        self.assertEqual(len(results), 1)
        self.assertIn("人工智能治理", results[0][0].content)
        self.assertGreater(results[0][1], 0.0)

    def test_retrieve_chinese_substring_via_fallback(self):
        # FTS5 porter 分词对中文无效，应走 LIKE fallback 仍能召回
        self.wm.store("用户偏好深色主题界面", category="preference", importance=0.8)
        results = self.wm.retrieve("深色主题", top_k=3)
        self.assertTrue(any("用户偏好深色主题界面" in e.content for e, _ in results))

    def test_loading_rebuilds_roots_from_disk(self):
        self.wm.store("根节点记忆", category="fact", importance=0.5)
        wm2 = WorkingMemory({"storage_path": self.db})
        self.assertGreaterEqual(len(wm2.roots), 1)

    def test_retrieve_min_score_filters_weak_matches(self):
        # I3：低于 min_score 的弱命中应被截断
        self.wm.store("治理框架需要多层约束", category="fact", importance=0.9)
        self.wm.store("一段完全无关的音乐评论文章", category="fact", importance=0.9)
        results = self.wm.retrieve("治理框架", top_k=5, min_score=0.5)
        self.assertEqual(len(results), 1)
        self.assertIn("治理框架", results[0][0].content)

    def test_retrieve_scores_normalized_to_unit_interval(self):
        # I3：分数应被裁剪到 [0,1]
        self.wm.store("归一化测试条目", category="fact", importance=1.0)
        results = self.wm.retrieve("归一化测试", top_k=5)
        self.assertTrue(results)
        for _, score in results:
            self.assertGreaterEqual(score, 0.0)
            self.assertLessEqual(score, 1.0)


class TestSemanticDisk(unittest.TestCase):
    def setUp(self):
        self.path = _tmp("knowledge_graph")
        self.sd = SemanticDisk({"storage_path": self.path})

    def _archive_and_wait(self, content: str):
        entry = MemoryEntry(
            id="e1",
            content=content,
            timestamp="2026-01-01T00:00:00",
            category="fact",
        )
        self.sd.archive_memory(entry)
        if self.sd._archive_worker:
            self.sd._archive_worker.join(timeout=3)
        return entry

    def test_archive_builds_knowledge_node(self):
        # "王伟" 命中中文姓氏NER正则
        self._archive_and_wait("王伟 今天去了北京讨论项目")
        node = self.sd.query("王伟")
        self.assertIsNotNone(node)
        self.assertEqual(node.entity, "王伟")

    def test_archive_persists_across_reload(self):
        self._archive_and_wait("王伟 负责安全审计模块")
        sd2 = SemanticDisk({"storage_path": self.path})
        self.assertGreaterEqual(sd2.stats()["total_nodes"], 1)
        self.assertIsNotNone(sd2.query("王伟"))

    def test_batch_archive_saves_all_nodes(self):
        # I4：队列耗尽后一次性落盘，burst 归档不应丢节点
        for name in ("王伟", "李娜", "张强"):
            self._archive_and_wait(f"{name} 参与了本项目的安全评审")
        sd2 = SemanticDisk({"storage_path": self.path})
        self.assertGreaterEqual(sd2.stats()["total_nodes"], 3)


class TestSALMemoryLayer(unittest.TestCase):
    def setUp(self):
        self.db = _tmp("lcm.db")
        self.kg = _tmp("knowledge_graph")
        self.layer = MemoryLayer({
            "working_memory": {"storage_path": self.db},
            "semantic_disk": {"storage_path": self.kg},
        })

    def test_store_then_retrieve(self):
        self.layer.store("治理框架应由多层约束组成", category="fact", importance=0.9)
        result = self.layer.retrieve("治理框架", top_k=1)
        self.assertEqual(result.total, 1)
        self.assertIn("治理框架", result.entries[0].content)

    def test_auto_archive_respects_importance_threshold(self):
        # importance >= 0.7 时自动归档到 L2
        self.layer.store("高重要性安全策略", category="knowledge", importance=0.9, auto_archive=True)
        self.assertGreaterEqual(self.layer.semantic_disk.stats()["total_nodes"], 1)

    def test_stats_shape(self):
        self.layer.store("统计条目", category="fact", importance=0.5)
        st = self.layer.stats()
        self.assertIn("l1_working_memory", st)
        self.assertIn("l2_semantic_disk", st)


if __name__ == "__main__":
    unittest.main()

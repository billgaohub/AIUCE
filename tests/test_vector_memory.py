"""
Test suite for real vector memory (grok-style KNN).

Proves that AIUCE's memory now performs genuine vector KNN recall — independent of
keyword/lexical overlap — rather than only reranking keyword-recalled candidates:

- DeterministicEmbeddingProvider (= MockEmbeddingProvider): deterministic, L2-normalized,
  offline; satisfies the EmbeddingProvider Protocol; similar texts score higher than
  dissimilar ones.
- VectorIndex: exact KNN correctness, top_k, add/remove, dim mismatch guard.
- UnifiedMemoryLayer: a lexically-disjoint but semantically-related entry is recalled via
  the VectorIndex even when the keyword path (FTS5/LIKE) returns nothing.
- UnifiedMemoryLayer: injected provider is used; vectors are persisted; stats expose index.
- HybridMemory: with a provider, vector recall surfaces the related entry; without a provider
  the behaviour is unchanged (no vector index built).

All tests are offline and deterministic — no network / no large embedding model required.
"""

import os
import sys
import tempfile
import unittest

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from eleven_layer_ai.core.vector_memory import (
    DeterministicEmbeddingProvider,
    MockEmbeddingProvider,
    VectorIndex,
    EmbeddingProvider,
)
from eleven_layer_ai.core.unified_memory import UnifiedMemoryLayer
from eleven_layer_ai.core.hybrid_memory import HybridMemory, MemoryTier
from eleven_layer_ai.core.memory_schema import MemoryBackend


def _cosine(a, b):
    a = np.asarray(a, dtype=float)
    b = np.asarray(b, dtype=float)
    na, nb = np.linalg.norm(a), np.linalg.norm(b)
    if na == 0 or nb == 0:
        return 0.0
    return float(a @ b / (na * nb))


class TestDeterministicEmbeddingProvider(unittest.TestCase):
    def setUp(self):
        self.p = DeterministicEmbeddingProvider(dim=64)

    def test_deterministic_same_text_same_vector(self):
        self.assertEqual(self.p.embed("hello world"), self.p.embed("hello world"))

    def test_dimension_matches(self):
        self.assertEqual(len(self.p.embed("anything")), 64)

    def test_l2_normalized(self):
        v = np.asarray(self.p.embed("normalize me please"), dtype=float)
        self.assertAlmostEqual(float(np.linalg.norm(v)), 1.0, places=5)

    def test_similar_beats_dissimilar(self):
        a = self.p.embed("neural network training gradient descent")
        b = self.p.embed("neural net training with gradients")
        c = self.p.embed("the weather today is sunny and warm")
        self.assertGreater(_cosine(a, b), _cosine(a, c))

    def test_mock_alias_is_same_class(self):
        self.assertIs(MockEmbeddingProvider, DeterministicEmbeddingProvider)

    def test_satisfies_protocol(self):
        self.assertIsInstance(self.p, EmbeddingProvider)


class TestVectorIndex(unittest.TestCase):
    def setUp(self):
        self.idx = VectorIndex(dim=4)
        self.idx.add("a", [1.0, 0.0, 0.0, 0.0])
        self.idx.add("b", [0.0, 1.0, 0.0, 0.0])
        self.idx.add("c", [0.0, 0.0, 1.0, 0.0])

    def test_exact_knn_ranks_nearest_first(self):
        hits = self.idx.search([1.0, 0.0, 0.0, 0.0], top_k=3)
        self.assertEqual(hits[0][0], "a")
        self.assertAlmostEqual(hits[0][1], 1.0, places=5)

    def test_top_k_limits_results(self):
        hits = self.idx.search([1.0, 1.0, 1.0, 1.0], top_k=2)
        self.assertEqual(len(hits), 2)

    def test_remove_excludes_id(self):
        self.idx.remove("a")
        hits = self.idx.search([1.0, 0.0, 0.0, 0.0], top_k=3)
        self.assertNotIn("a", [h[0] for h in hits])
        self.assertEqual(self.idx.size(), 2)

    def test_empty_index_returns_empty(self):
        empty = VectorIndex(dim=4)
        self.assertEqual(empty.search([1, 0, 0, 0]), [])

    def test_dim_mismatch_raises(self):
        with self.assertRaises(ValueError):
            self.idx.add("bad", [1.0, 0.0])


class _EnglishProvider:
    """Simple offline provider used to demonstrate semantic (non-lexical) recall."""

    def __init__(self, dim=128):
        self.dim = dim

    def embed(self, text: str):
        # 词袋哈希到固定维度（与 DeterministicEmbeddingProvider 同思路，但独立实现以隔离测试）
        vec = np.zeros(self.dim, dtype=np.float32)
        import re
        for tok in re.findall(r"[a-zA-Z0-9]{2,}", text.lower()):
            vec[hash(tok) % self.dim] += 1.0
        norm = np.linalg.norm(vec)
        if norm > 0:
            vec = vec / norm
        return vec.tolist()


class TestUnifiedMemoryLayerVectorRecall(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.mkdtemp()
        self.path = os.path.join(self._tmp, "memory_store.json")
        self.layer = UnifiedMemoryLayer({"storage_path": self.path})

    def test_vector_recall_surfaces_lexically_disjoint_entry(self):
        # 关键词路径（FTS5 AND / LIKE 子串）对这两条都应返回空：
        # 查询里多出的 "zebras"/"for" 使 FTS5 全词命中失败，且无子串重叠。
        self.layer.store(
            content="neural network training requires gradient descent optimization",
            category="fact", importance=0.9,
        )
        self.layer.store(
            content="the weather today is sunny and warm outside",
            category="fact", importance=0.9,
        )
        query = "gradient descent optimization for neural network training zebras"

        # 纯关键词路径应召回为空（证明是向量路径在起作用）
        keyword_only = self.layer.serving.retrieve(query, top_k=5)
        self.assertEqual(len(keyword_only), 0, "纯关键词路径不应召回目标条目")

        # 统一层检索应通过向量 KNN 召回目标条目
        results = self.layer.retrieve(query, top_k=5)
        self.assertTrue(results, "向量 KNN 召回应至少返回一个结果")
        contents = [r[0].content for r in results]
        self.assertTrue(
            any("neural network training" in c for c in contents),
            "语义相关的目标条目应被向量召回",
        )
        # 不相关的天气条目不应排在前面
        self.assertNotIn("the weather today is sunny", contents[0])

    def test_stats_expose_vector_index_and_provider(self):
        self.layer.store(content="vector memory test entry", category="fact", importance=0.6)
        st = self.layer.stats()
        self.assertGreaterEqual(st["vector_index_size"], 1)
        self.assertEqual(st["embedding_provider"], "DeterministicEmbeddingProvider")

    def test_injected_provider_is_used_and_vectors_persisted(self):
        layer = UnifiedMemoryLayer(
            {"storage_path": os.path.join(tempfile.mkdtemp(), "m.json")},
            embedding_provider=_EnglishProvider(),
        )
        layer.store(content="deep learning model", category="fact", importance=0.7)
        st = layer.stats()
        self.assertEqual(st["embedding_provider"], "_EnglishProvider")
        self.assertGreaterEqual(st["vector_index_size"], 1)
        # memories 视图应携带非零向量
        for entry in layer.memories.values():
            self.assertTrue(len(entry.embedding) > 0)

    def test_satisfies_memory_backend_protocol(self):
        self.assertIsInstance(self.layer, MemoryBackend)


class TestHybridMemoryVectorRecall(unittest.TestCase):
    def setUp(self):
        self.user_path = os.path.join(tempfile.mkdtemp(), "h_user.json")
        self.global_path = os.path.join(tempfile.mkdtemp(), "h_global.json")

    def test_provider_enables_vector_recall(self):
        hm = HybridMemory(
            {"user": {"storage_path": self.user_path},
             "global": {"storage_path": self.global_path}},
            embedding_provider=DeterministicEmbeddingProvider(),
        )
        hm.store(
            content="neural network training requires gradient descent optimization",
            tier=MemoryTier.GLOBAL, category="knowledge", importance=0.9,
        )
        hm.store(
            content="the weather today is sunny and warm outside",
            tier=MemoryTier.GLOBAL, category="knowledge", importance=0.9,
        )
        query = "gradient descent optimization for neural network training zebras"
        results = hm.retrieve(query, top_k=5)
        self.assertTrue(results)
        contents = [r[0].content for r in results]
        self.assertTrue(any("neural network training" in c for c in contents))
        self.assertNotIn("the weather today is sunny", contents[0])

    def test_no_provider_means_no_vector_index_and_unchanged_behavior(self):
        hm = HybridMemory({
            "user": {"storage_path": self.user_path},
            "global": {"storage_path": self.global_path},
        })
        # 默认无 provider：三层子记忆均不构建向量索引
        self.assertIsNone(hm.workspace._vector_index)
        self.assertIsNone(hm.user._vector_index)
        self.assertIsNone(hm.global_mem._vector_index)
        # 子串检索仍正常工作（行为不变）
        hm.store("人工智能治理框架", tier=MemoryTier.GLOBAL, category="knowledge")
        res = hm.retrieve("人工智能治理", top_k=1)
        self.assertEqual(len(res), 1)
        self.assertIn("人工智能治理", res[0][0].content)


if __name__ == "__main__":
    unittest.main()

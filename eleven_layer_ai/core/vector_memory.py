"""
真实向量记忆 (Real Vector Memory) —— 可插拔 EmbeddingProvider + 真实向量 KNN 索引

落地 grok (xai-grok-memory) 的「真实向量记忆」设计：
- EmbeddingProvider：可插拔嵌入协议（真实语义模型 / 确定性 Mock 供离线测试）
- VectorIndex：真实 KNN 向量索引（numpy 精确检索，线程安全）
- DeterministicEmbeddingProvider（= MockEmbeddingProvider）：零依赖、确定性的离线
  embedding，使语义检索可复现、可单测，无需联网或大模型。

与 AIUCE 现有集成点：
- UnifiedMemoryLayer 在 store 时持久化向量、retrieve 时走 VectorIndex 做真实 KNN 召回；
- HybridMemory（可选 provider）同样接入 VectorIndex 做向量召回。
- 公开 API（store / retrieve / stats / MemoryEntry / MemoryBackend）不变。

设计约束（防止 scope creep）：
- 复用 memory_sal.EmbeddingProvider 协议，不重复定义；
- VectorIndex 默认精确 KNN（numpy），不引入未安装的 hnswlib/faiss 依赖；
  大规模加速（hnswlib/faiss）是后续可插拔的增强，不在本次范围。
- 所有索引操作线程安全（RLock），符合 MemoryBackend 线程契约（I5）。
"""

from typing import List, Optional, Tuple
import threading

import numpy as np

# 复用既有协议，不重复定义（memory_sal 已定义 EmbeddingProvider Protocol）
from .memory_sal import EmbeddingProvider


# ═══════════════════════════════════════════════════════════════
# 确定性离线 EmbeddingProvider（grok 的 MockEmbeddingProvider）
# ═══════════════════════════════════════════════════════════════

class DeterministicEmbeddingProvider:
    """
    确定性、零依赖的 EmbeddingProvider（离线 Mock / 默认 provider）

    设计：
    - 将文本切分为 token（中文字二元组 + 英文/数字词），哈希散列到固定维度向量；
    - L2 归一化，使余弦相似度反映词汇/语义重叠度；
    - 相同输入 → 相同向量（无随机），保证测试可复现。

    这是 grok MemoryBackend 中 MockEmbeddingProvider 的等价物：
    真实环境可注入 sentence-transformers / OpenAI embeddings 等真实 provider，
    离线/测试环境用本类即可获得有意义的语义召回（无需联网或大模型）。
    """

    def __init__(self, dim: int = 128):
        self.dim = dim

    def embed(self, text: str) -> List[float]:
        vec = np.zeros(self.dim, dtype=np.float32)
        tokens = self._tokenize(text)
        if not tokens:
            # 空文本给一个恒定的微小向量，避免全零导致余弦未定义
            vec[0] = 1.0
            return vec.tolist()
        for tok in tokens:
            h = hash(tok) % self.dim
            vec[h] += 1.0
        # L2 归一化
        norm = float(np.linalg.norm(vec))
        if norm > 0:
            vec = vec / norm
        return vec.tolist()

    @staticmethod
    def _tokenize(text: str) -> List[str]:
        import re
        tokens: List[str] = []
        # 中文：二元组（捕捉局部语义，对中文分词友好）
        zh = re.findall(r"[一-鿿]", text)
        for i in range(0, len(zh) - 1):
            tokens.append("".join(zh[i:i + 2]))
        # 英文 / 数字词
        en = re.findall(r"[a-zA-Z0-9]{2,}", text.lower())
        tokens.extend(en)
        return tokens


# grok 命名别名，便于与参考实现对齐
MockEmbeddingProvider = DeterministicEmbeddingProvider


# ═══════════════════════════════════════════════════════════════
# 真实向量 KNN 索引
# ═══════════════════════════════════════════════════════════════

class VectorIndex:
    """
    真实向量 KNN 索引（numpy 精确检索）

    特性：
    - add / remove / search 线程安全（RLock，符合 MemoryBackend 线程契约 I5）
    - search 返回 [(id, cosine), ...] 按相似度降序，cosine ∈ [-1, 1]
    - 行向量在写入时已 L2 归一化，故检索时余弦 = 点积，无需逐对归一化
    - 精确 KNN（numpy），保证确定性、零额外依赖；
      大规模加速（hnswlib / faiss）为后续可插拔增强，不在本次范围。

    与 grok 的 sqlite-vec KNN 对照：本环境 Python 构建禁用了 loadable extension，
    sqlite-vec 的 vec0 扩展无法加载，故用 Python 侧 numpy 精确 KNN 作为等价实现，
    语义召回能力一致，且不引入原生扩展依赖。
    """

    def __init__(self, dim: int = 128):
        self.dim = dim
        self._lock = threading.RLock()
        self._ids: List[str] = []
        self._matrix: Optional[np.ndarray] = None  # (n, dim) 行向量，已 L2 归一化

    def _normalized(self, vector: List[float]) -> np.ndarray:
        arr = np.asarray(vector, dtype=np.float32)
        if arr.shape[0] != self.dim:
            raise ValueError(f"向量维度 {arr.shape[0]} 与索引维度 {self.dim} 不符")
        norm = float(np.linalg.norm(arr))
        if norm > 0:
            arr = arr / norm
        return arr

    def add(self, id_: str, vector: List[float]) -> None:
        """插入/覆盖一个向量（同 id 覆盖）"""
        with self._lock:
            arr = self._normalized(vector)
            if id_ in self._ids:
                idx = self._ids.index(id_)
                if self._matrix is not None:
                    self._matrix[idx] = arr
            else:
                self._ids.append(id_)
                if self._matrix is None:
                    self._matrix = arr.reshape(1, -1)
                else:
                    self._matrix = np.vstack([self._matrix, arr])

    def add_batch(self, items: List[Tuple[str, List[float]]]) -> None:
        for id_, vec in items:
            self.add(id_, vec)

    def remove(self, id_: str) -> None:
        with self._lock:
            if id_ not in self._ids:
                return
            idx = self._ids.index(id_)
            self._ids.pop(idx)
            if self._matrix is None:
                return
            if self._matrix.shape[0] > 1:
                self._matrix = np.delete(self._matrix, idx, axis=0)
            else:
                self._matrix = None

    def search(self, query_vector: List[float], top_k: int = 5) -> List[Tuple[str, float]]:
        """
        精确 KNN 检索，返回 [(id, cosine), ...] 降序。

        cosine ∈ [-1, 1]；调用方应按需裁剪到 [0,1]（语义相似度不应为负）。
        """
        with self._lock:
            if not self._ids or self._matrix is None:
                return []
            q = self._normalized(query_vector)
            # 双方已 L2 归一化 → 余弦 = 点积
            sims = self._matrix @ q  # (n,)
            k = min(top_k, len(self._ids))
            order = np.argsort(-sims)[:k]
            return [(self._ids[i], float(sims[i])) for i in order]

    def size(self) -> int:
        with self._lock:
            return len(self._ids)

    def ids(self) -> List[str]:
        with self._lock:
            return list(self._ids)


__all__ = [
    "EmbeddingProvider",
    "DeterministicEmbeddingProvider",
    "MockEmbeddingProvider",
    "VectorIndex",
]

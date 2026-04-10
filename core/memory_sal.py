"""
L4 记忆层：分级存储抽象层 (Storage Abstraction Layer - SAL)
记忆存储/索引中心

架构：
┌─────────────────────────────────────────────────────────┐
│               L4 记忆层 (Storage Abstraction Layer)      │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  ┌───────────────────────────────────────────────────┐  │
│  │  L1 工作记忆 (Working Memory)                      │  │
│  │  - Lossless-claw DAG 结构                          │  │
│  │  - 当前活跃上下文                                   │  │
│  │  - FTS5 毫秒级检索                                 │  │
│  │  - 存储: ~/.aiuce/lcm.db                           │  │
│  └───────────────────────────────────────────────────┘  │
│                         ↓ 异步归档                       │
│  ┌───────────────────────────────────────────────────┐  │
│  │  L2 长期语义盘 (Long-term Semantic Disk)           │  │
│  │  - Cognee 知识图谱微服务                            │  │
│  │  - 异步消费 L1 归档数据                             │  │
│  │  - 将零散对话编排为立体知识图谱                      │  │
│  │  - 存储: ~/.aiuce/knowledge_graph/                 │  │
│  └───────────────────────────────────────────────────┘  │
│                                                          │
└─────────────────────────────────────────────────────────┘

设计原则：
1. 统一管理数据生命周期，避免不同结构数据的锁竞争
2. L1 使用 DAG 无损压缩当前对话
3. L2 异步生成知识图谱
"""

from typing import Dict, Any, List, Optional, Tuple, Union, Protocol, runtime_checkable
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from abc import ABC, abstractmethod
import json
import os
import sqlite3
import threading
import queue
import hashlib
from collections import defaultdict


# ═══════════════════════════════════════════════════════════════
# 类型定义
# ═══════════════════════════════════════════════════════════════

class MemoryTier(Enum):
    """记忆层级"""
    L1_WORKING = "l1_working"       # 工作记忆（热）
    L2_SEMANTIC = "l2_semantic"     # 长期语义（冷）


class MemoryCategory(Enum):
    """记忆分类"""
    EVENT = "event"
    KNOWLEDGE = "knowledge"
    PREFERENCE = "preference"
    FACT = "fact"
    SKILL = "skill"
    ERROR = "error"
    INSIGHT = "insight"
    CONVERSATION = "conversation"


class ArchiveStatus(Enum):
    """归档状态"""
    ACTIVE = "active"
    ARCHIVING = "archiving"
    ARCHIVED = "archived"


@runtime_checkable
class EmbeddingProvider(Protocol):
    """向量嵌入提供者协议"""
    def embed(self, text: str) -> List[float]:
        """将文本转换为向量"""
        ...


@dataclass
class MemoryEntry:
    """记忆条目（L1）"""
    id: str
    content: str
    timestamp: str
    category: str
    tier: MemoryTier = MemoryTier.L1_WORKING
    tags: List[str] = field(default_factory=list)
    importance: float = 0.5
    access_count: int = 0
    last_accessed: str = ""
    embedding: List[float] = field(default_factory=list)
    source: str = "internal"
    archive_status: ArchiveStatus = ArchiveStatus.ACTIVE
    parent_id: Optional[str] = None  # DAG 父节点
    children_ids: List[str] = field(default_factory=list)  # DAG 子节点
    
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
            "tier": self.tier.value,
            "tags": self.tags,
            "importance": self.importance,
            "access_count": self.access_count,
            "last_accessed": self.last_accessed,
            "embedding_dim": len(self.embedding),
            "source": self.source,
            "archive_status": self.archive_status.value,
            "parent_id": self.parent_id,
            "children_ids": self.children_ids,
        }


@dataclass
class KnowledgeNode:
    """知识图谱节点（L2）"""
    id: str
    entity: str
    entity_type: str
    properties: Dict[str, Any] = field(default_factory=dict)
    relationships: List[Tuple[str, str]] = field(default_factory=list)  # [(relation, target_id)]
    source_memory_ids: List[str] = field(default_factory=list)  # 来源记忆 ID
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    confidence: float = 1.0


@dataclass
class MemoryQuery:
    """记忆查询"""
    query: str
    top_k: int = 10
    tiers: Optional[List[MemoryTier]] = None
    categories: Optional[List[MemoryCategory]] = None
    tags: Optional[List[str]] = None
    min_importance: float = 0.0
    include_archived: bool = False


@dataclass
class MemorySearchResult:
    """记忆搜索结果"""
    entries: List[MemoryEntry]
    knowledge_nodes: List[KnowledgeNode]
    scores: List[float]
    query: str
    total: int


# ═══════════════════════════════════════════════════════════════
# L1 工作记忆 (Working Memory) - Lossless-claw 风格
# ═══════════════════════════════════════════════════════════════

class WorkingMemory:
    """
    L1 工作记忆 - Lossless-claw DAG 结构
    
    特性：
    1. DAG（有向无环图）结构维护当前活跃上下文
    2. FTS5 全文检索，毫秒级响应
    3. 无损压缩，支持时间旅行回溯
    4. SQLite 存储，路径: ~/.aiuce/lcm.db
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        default_path = os.path.expanduser("~/.aiuce/lcm.db")
        self.storage_path = self.config.get("storage_path", default_path)
        self.max_entries = self.config.get("max_entries", 10000)
        
        # DAG 结构
        self.entries: Dict[str, MemoryEntry] = {}
        self.roots: List[str] = []  # DAG 根节点
        
        # FTS5 索引
        self._fts_index: Dict[str, List[str]] = defaultdict(list)  # word -> entry_ids
        
        # 线程安全
        self._lock = threading.RLock()
        
        self._init_storage()
    
    def _init_storage(self):
        """初始化存储"""
        os.makedirs(os.path.dirname(self.storage_path), exist_ok=True)
        
        # 初始化 SQLite
        with sqlite3.connect(self.storage_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS memories (
                    id TEXT PRIMARY KEY,
                    content TEXT NOT NULL,
                    timestamp TEXT,
                    category TEXT,
                    importance REAL,
                    tags TEXT,
                    parent_id TEXT,
                    children_ids TEXT,
                    embedding BLOB,
                    metadata TEXT
                )
            """)
            
            # FTS5 全文索引
            conn.execute("""
                CREATE VIRTUAL TABLE IF NOT EXISTS memories_fts USING fts5(
                    id, content, tags,
                    tokenize='porter unicode61'
                )
            """)
            
            conn.commit()
        
        self._load_from_disk()
    
    def _load_from_disk(self):
        """从磁盘加载"""
        try:
            with sqlite3.connect(self.storage_path) as conn:
                cursor = conn.execute("SELECT * FROM memories")
                for row in cursor.fetchall():
                    entry = MemoryEntry(
                        id=row[0],
                        content=row[1],
                        timestamp=row[2],
                        category=row[3],
                        importance=row[4],
                        tags=json.loads(row[5]) if row[5] else [],
                        parent_id=row[6],
                        children_ids=json.loads(row[7]) if row[7] else [],
                    )
                    self.entries[entry.id] = entry
                    
                    # 重建根节点列表
                    if entry.parent_id is None:
                        self.roots.append(entry.id)
            
            print(f"  [L4 L1工作记忆] 加载 {len(self.entries)} 条记忆")
        except Exception as e:
            print(f"  [L4 L1工作记忆] 加载失败: {e}")
    
    def store(
        self,
        content: str,
        category: Union[str, MemoryCategory] = "general",
        tags: Optional[List[str]] = None,
        importance: float = 0.5,
        parent_id: Optional[str] = None
    ) -> str:
        """
        存储记忆到 DAG
        
        Args:
            content: 记忆内容
            category: 分类
            tags: 标签
            importance: 重要性
            parent_id: 父节点 ID（构建 DAG）
            
        Returns:
            记忆 ID
        """
        import uuid
        
        if isinstance(category, MemoryCategory):
            category = category.value
        
        entry_id = str(uuid.uuid4())[:8]
        now = datetime.now().isoformat()
        
        entry = MemoryEntry(
            id=entry_id,
            content=content,
            timestamp=now,
            category=category,
            tags=tags or [],
            importance=importance,
            parent_id=parent_id
        )
        
        with self._lock:
            self.entries[entry_id] = entry
            
            # 更新父节点的 children
            if parent_id and parent_id in self.entries:
                self.entries[parent_id].children_ids.append(entry_id)
            else:
                # 新根节点
                self.roots.append(entry_id)
            
            # 更新 FTS 索引
            for word in content.lower().split():
                self._fts_index[word].append(entry_id)
            for tag in (tags or []):
                self._fts_index[f"#{tag}"].append(entry_id)
            
            # 持久化
            self._persist_entry(entry)
        
        return entry_id
    
    def _persist_entry(self, entry: MemoryEntry):
        """持久化到 SQLite"""
        try:
            with sqlite3.connect(self.storage_path) as conn:
                conn.execute(
                    """INSERT OR REPLACE INTO memories 
                       (id, content, timestamp, category, importance, tags, parent_id, children_ids)
                       VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                    (
                        entry.id,
                        entry.content,
                        entry.timestamp,
                        entry.category,
                        entry.importance,
                        json.dumps(entry.tags),
                        entry.parent_id,
                        json.dumps(entry.children_ids)
                    )
                )
                
                # FTS5 索引
                conn.execute(
                    "INSERT INTO memories_fts (id, content, tags) VALUES (?, ?, ?)",
                    (entry.id, entry.content, " ".join(entry.tags))
                )
                
                conn.commit()
        except Exception as e:
            print(f"  [L4 L1工作记忆] 持久化失败: {e}")
    
    def retrieve(self, query: str, top_k: int = 5) -> List[Tuple[MemoryEntry, float]]:
        """FTS5 检索"""
        with self._lock:
            results: List[Tuple[MemoryEntry, float]] = []
            query_lower = query.lower()
            
            # FTS5 全文检索
            try:
                with sqlite3.connect(self.storage_path) as conn:
                    cursor = conn.execute(
                        """SELECT m.id, m.content, m.timestamp, m.category, m.importance, m.tags, m.parent_id
                           FROM memories_fts fts
                           JOIN memories m ON fts.id = m.id
                           WHERE memories_fts MATCH ?
                           ORDER BY bm25(memories_fts) DESC
                           LIMIT ?""",
                        (query_lower, top_k * 2)
                    )
                    
                    for row in cursor.fetchall():
                        entry = MemoryEntry(
                            id=row[0],
                            content=row[1],
                            timestamp=row[2],
                            category=row[3],
                            importance=row[4],
                            tags=json.loads(row[5]) if row[5] else [],
                            parent_id=row[6]
                        )
                        
                        # 计算分数
                        score = 0.5
                        if query_lower in entry.content.lower():
                            score += 0.3
                        score *= (0.5 + 0.5 * entry.importance)
                        
                        results.append((entry, score))
            except Exception:
                # 回退到内存检索
                for entry in self.entries.values():
                    score = 0.0
                    if query_lower in entry.content.lower():
                        score += 0.5
                    for tag in entry.tags:
                        if query_lower in tag.lower():
                            score += 0.3
                    if score > 0:
                        score *= (0.5 + 0.5 * entry.importance)
                        results.append((entry, score))
            
            results.sort(key=lambda x: x[1], reverse=True)
            return results[:top_k]
    
    def get_dag_path(self, entry_id: str) -> List[str]:
        """获取 DAG 路径（从根到该节点）"""
        path = []
        current = entry_id
        
        while current:
            path.insert(0, current)
            entry = self.entries.get(current)
            if entry:
                current = entry.parent_id
            else:
                break
        
        return path
    
    def get_children(self, entry_id: str) -> List[MemoryEntry]:
        """获取所有子节点"""
        entry = self.entries.get(entry_id)
        if not entry:
            return []
        return [self.entries[cid] for cid in entry.children_ids if cid in self.entries]
    
    def stats(self) -> Dict[str, Any]:
        """统计"""
        return {
            "total_entries": len(self.entries),
            "root_count": len(self.roots),
            "avg_children": sum(len(e.children_ids) for e in self.entries.values()) / max(len(self.entries), 1),
            "max_depth": max(len(self.get_dag_path(e.id)) for e in self.entries.values()) if self.entries else 0,
            "storage_path": self.storage_path
        }


# ═══════════════════════════════════════════════════════════════
# L2 长期语义盘 (Long-term Semantic Disk) - Cognee 风格
# ═══════════════════════════════════════════════════════════════

class SemanticDisk:
    """
    L2 长期语义盘 - Cognee 知识图谱微服务
    
    特性：
    1. 异步消费 L1 归档数据
    2. 将零散对话编排为立体知识图谱
    3. 支持 SPARQL/Cypher 查询
    4. 存储: ~/.aiuce/knowledge_graph/
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        default_path = os.path.expanduser("~/.aiuce/knowledge_graph")
        self.storage_path = self.config.get("storage_path", default_path)
        
        # 知识图谱
        self.nodes: Dict[str, KnowledgeNode] = {}
        self.entity_index: Dict[str, str] = {}  # entity_name -> node_id
        
        # 归档队列
        self.archive_queue: queue.Queue = queue.Queue()
        self._archive_worker: Optional[threading.Thread] = None
        
        self._init_storage()
    
    def _init_storage(self):
        """初始化存储"""
        os.makedirs(self.storage_path, exist_ok=True)
        self._load_from_disk()
    
    def _load_from_disk(self):
        """加载知识图谱"""
        nodes_file = os.path.join(self.storage_path, "nodes.json")
        if os.path.exists(nodes_file):
            try:
                with open(nodes_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    for node_data in data.get("nodes", []):
                        node = KnowledgeNode(
                            id=node_data["id"],
                            entity=node_data["entity"],
                            entity_type=node_data["entity_type"],
                            properties=node_data.get("properties", {}),
                            relationships=[tuple(r) for r in node_data.get("relationships", [])],
                            source_memory_ids=node_data.get("source_memory_ids", []),
                            confidence=node_data.get("confidence", 1.0)
                        )
                        self.nodes[node.id] = node
                        self.entity_index[node.entity] = node.id
                
                print(f"  [L4 L2语义盘] 加载 {len(self.nodes)} 个知识节点")
            except Exception as e:
                print(f"  [L4 L2语义盘] 加载失败: {e}")
    
    def _save_to_disk(self):
        """保存知识图谱"""
        nodes_file = os.path.join(self.storage_path, "nodes.json")
        try:
            data = {
                "last_updated": datetime.now().isoformat(),
                "nodes": [
                    {
                        "id": n.id,
                        "entity": n.entity,
                        "entity_type": n.entity_type,
                        "properties": n.properties,
                        "relationships": list(n.relationships),
                        "source_memory_ids": n.source_memory_ids,
                        "confidence": n.confidence
                    }
                    for n in self.nodes.values()
                ]
            }
            with open(nodes_file, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"  [L4 L2语义盘] 保存失败: {e}")
    
    def archive_memory(self, entry: MemoryEntry):
        """
        归档记忆到知识图谱
        
        将对话条目转换为知识节点和关系
        """
        self.archive_queue.put(entry)
        
        # 启动归档 worker（如果未启动）
        if not self._archive_worker or not self._archive_worker.is_alive():
            self._archive_worker = threading.Thread(target=self._archive_worker_loop, daemon=True)
            self._archive_worker.start()
    
    def _archive_worker_loop(self):
        """归档工作线程"""
        while True:
            try:
                entry = self.archive_queue.get(timeout=1)
                self._process_archive(entry)
            except queue.Empty:
                break
            except Exception as e:
                print(f"  [L4 L2语义盘] 归档错误: {e}")
    
    def _process_archive(self, entry: MemoryEntry):
        """处理单条归档"""
        # 简单实体提取（实际应使用 NER）
        entities = self._extract_entities(entry.content)
        
        for entity_name, entity_type in entities:
            node_id = self.entity_index.get(entity_name)
            
            if node_id:
                # 已存在，更新
                node = self.nodes[node_id]
                node.source_memory_ids.append(entry.id)
                node.confidence = min(1.0, node.confidence + 0.1)
            else:
                # 新建
                import uuid
                node_id = str(uuid.uuid4())[:8]
                
                node = KnowledgeNode(
                    id=node_id,
                    entity=entity_name,
                    entity_type=entity_type,
                    source_memory_ids=[entry.id]
                )
                
                self.nodes[node_id] = node
                self.entity_index[entity_name] = node_id
        
        # 建立关系
        if len(entities) >= 2:
            for i in range(len(entities) - 1):
                source_id = self.entity_index.get(entities[i][0])
                target_id = self.entity_index.get(entities[i + 1][0])
                
                if source_id and target_id:
                    # 添加关系
                    self.nodes[source_id].relationships.append(
                        (f"mentioned_with_{entry.category}", target_id)
                    )
        
        self._save_to_disk()
    
    def _extract_entities(self, text: str) -> List[Tuple[str, str]]:
        """
        实体提取（简化版）
        
        实际应使用 NER 模型
        """
        entities = []
        
        # 简单规则提取
        import re
        
        # 人名（中文）
        names = re.findall(r"[王李张刘陈杨黄赵吴周徐孙马朱胡郭何高林罗郑梁谢宋唐许韩冯邓曹彭曾萧田董潘袁蔡蒋卢魏陆叶][a-zA-Z\u4e00-\u9fff]{1,2}", text)
        for name in names:
            entities.append((name, "PERSON"))
        
        # 时间
        times = re.findall(r"\d{4}年\d{1,2}月\d{1,2}日|\d{1,2}月\d{1,2}日|今天|明天|昨天", text)
        for t in times:
            entities.append((t, "TIME"))
        
        # 金额
        amounts = re.findall(r"\d+元|\d+万|\d+亿|¥\d+|\$\d+", text)
        for a in amounts:
            entities.append((a, "MONEY"))
        
        return entities
    
    def query(self, entity: str) -> Optional[KnowledgeNode]:
        """查询知识节点"""
        node_id = self.entity_index.get(entity)
        if node_id:
            return self.nodes.get(node_id)
        return None
    
    def get_related(self, entity: str, depth: int = 2) -> List[KnowledgeNode]:
        """获取相关节点"""
        start_id = self.entity_index.get(entity)
        if not start_id:
            return []
        
        visited = set()
        result = []
        queue = [(start_id, 0)]
        
        while queue:
            node_id, level = queue.pop(0)
            
            if node_id in visited or level > depth:
                continue
            
            visited.add(node_id)
            node = self.nodes.get(node_id)
            
            if node:
                result.append(node)
                
                for relation, target_id in node.relationships:
                    queue.append((target_id, level + 1))
        
        return result[1:]  # 排除起始节点
    
    def stats(self) -> Dict[str, Any]:
        """统计"""
        return {
            "total_nodes": len(self.nodes),
            "entity_types": len(set(n.entity_type for n in self.nodes.values())),
            "total_relationships": sum(len(n.relationships) for n in self.nodes.values()),
            "storage_path": self.storage_path
        }


# ═══════════════════════════════════════════════════════════════
# L4 记忆层主类 (Memory Layer - SAL)
# ═══════════════════════════════════════════════════════════════

class MemoryLayer:
    """
    L4 记忆层 - 分级存储抽象层 (SAL)
    
    记忆存储/索引中心
    
    "全域事实的语义索引，让过往一切碎片皆成史料"
    
    架构：
    - L1 工作记忆 (Working Memory): Lossless-claw DAG + FTS5
    - L2 长期语义盘 (Semantic Disk): Cognee 知识图谱
    """
    
    def __init__(
        self,
        config: Optional[Dict[str, Any]] = None,
        embedding_provider: Optional[EmbeddingProvider] = None
    ):
        self.config = config or {}
        
        # L1 工作记忆
        self.working_memory = WorkingMemory(config.get("working_memory", {}))
        
        # L2 长期语义盘
        self.semantic_disk = SemanticDisk(config.get("semantic_disk", {}))
        
        # 向量嵌入提供者
        self._embedding_provider = embedding_provider
        
        print(f"  [L4 记忆层] 记忆存储/索引中心 - 分级存储抽象层就位")
        print(f"    L1 工作记忆: {self.working_memory.stats()['total_entries']} 条")
        print(f"    L2 语义盘: {self.semantic_disk.stats()['total_nodes']} 个节点")
    
    # ── 存储接口 ───────────────────────────────────────────────
    
    def store(
        self,
        content: str,
        category: Union[str, MemoryCategory] = "general",
        tags: Optional[List[str]] = None,
        importance: float = 0.5,
        parent_id: Optional[str] = None,
        auto_archive: bool = False
    ) -> str:
        """
        存储记忆
        
        Args:
            content: 记忆内容
            category: 分类
            tags: 标签
            importance: 重要性
            parent_id: 父节点 ID
            auto_archive: 是否自动归档到 L2
            
        Returns:
            记忆 ID
        """
        # 存储到 L1
        entry_id = self.working_memory.store(
            content=content,
            category=category,
            tags=tags,
            importance=importance,
            parent_id=parent_id
        )
        
        # 自动归档
        if auto_archive and importance >= 0.7:
            entry = self.working_memory.entries.get(entry_id)
            if entry:
                self.semantic_disk.archive_memory(entry)
        
        return entry_id
    
    # ── 检索接口 ───────────────────────────────────────────────
    
    def retrieve(
        self,
        query: str,
        top_k: int = 5,
        include_knowledge: bool = True
    ) -> MemorySearchResult:
        """
        检索记忆
        
        同时检索 L1 工作记忆和 L2 知识图谱
        """
        # L1 检索
        l1_results = self.working_memory.retrieve(query, top_k)
        
        # L2 知识检索
        knowledge_nodes = []
        if include_knowledge:
            # 从查询中提取实体
            entities = self.semantic_disk._extract_entities(query)
            for entity_name, _ in entities:
                related = self.semantic_disk.get_related(entity_name)
                knowledge_nodes.extend(related)
        
        entries = [r[0] for r in l1_results]
        scores = [r[1] for r in l1_results]
        
        return MemorySearchResult(
            entries=entries,
            knowledge_nodes=knowledge_nodes[:top_k],
            scores=scores,
            query=query,
            total=len(entries) + len(knowledge_nodes)
        )
    
    # ── DAG 接口 ───────────────────────────────────────────────
    
    def get_dag_path(self, entry_id: str) -> List[str]:
        """获取 DAG 路径"""
        return self.working_memory.get_dag_path(entry_id)
    
    def get_children(self, entry_id: str) -> List[MemoryEntry]:
        """获取子节点"""
        return self.working_memory.get_children(entry_id)
    
    # ── 归档接口 ───────────────────────────────────────────────
    
    def archive_to_semantic(self, entry_id: str):
        """手动归档到 L2"""
        entry = self.working_memory.entries.get(entry_id)
        if entry:
            self.semantic_disk.archive_memory(entry)
    
    def archive_batch(self, min_importance: float = 0.7):
        """批量归档高重要性记忆"""
        count = 0
        for entry in self.working_memory.entries.values():
            if entry.importance >= min_importance:
                self.semantic_disk.archive_memory(entry)
                count += 1
        return count
    
    # ── 统计接口 ───────────────────────────────────────────────
    
    def stats(self) -> Dict[str, Any]:
        """统计信息"""
        l1_stats = self.working_memory.stats()
        l2_stats = self.semantic_disk.stats()
        
        return {
            "l1_working_memory": l1_stats,
            "l2_semantic_disk": l2_stats,
            "total_memories": l1_stats["total_entries"],
            "total_knowledge_nodes": l2_stats["total_nodes"]
        }


# ═══════════════════════════════════════════════════════════════
# 导出
# ═══════════════════════════════════════════════════════════════

__all__ = [
    "MemoryTier",
    "MemoryCategory",
    "ArchiveStatus",
    "EmbeddingProvider",
    "MemoryEntry",
    "KnowledgeNode",
    "MemoryQuery",
    "MemorySearchResult",
    "WorkingMemory",
    "SemanticDisk",
    "MemoryLayer",
]

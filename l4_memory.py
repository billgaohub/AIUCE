"""
L4 记忆层：司马迁/翰林院
Semantic Memory Index

职责：
1. 全域语义索引
2. 把所有碎片化事实编纂入库
3. 让过往一切皆成"史料"可供调取
"""

from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime
import json
import os


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


class MemoryLayer:
    """
    记忆层 - 司马迁/翰林院
    
    "全域事实的语义索引，让过往一切碎片皆成史料"
    
    类似 RAG 的语义检索系统，
    但更强调时间序列和重要性排序。
    """

    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        # 使用用户主目录下的 .aiuce 目录，避免硬编码路径
        default_path = os.path.expanduser("~/.aiuce/memory_store.json")
        self.storage_path = self.config.get("storage_path", default_path)
        self.memories: Dict[str, MemoryEntry] = {}
        self.index: Dict[str, List[str]] = {}  # 标签 -> 记忆ID
        self.max_memories = self.config.get("max_memories", 10000)
        
        self._load_memories()

    def _load_memories(self):
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

    def _save_memories(self):
        """保存记忆到磁盘"""
        try:
            data = {
                "last_updated": datetime.now().isoformat(),
                "memories": [m.__dict__ for m in self.memories.values()]
            }
            with open(self.storage_path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"  [L4] 保存记忆失败: {e}")

    def store(
        self,
        content: str,
        category: str = "general",
        tags: List[str] = None,
        importance: float = 0.5
    ) -> str:
        """
        存储新记忆
        
        Args:
            content: 记忆内容
            category: 分类
            tags: 标签
            importance: 重要性 0-1
            
        Returns:
            记忆ID
        """
        entry = MemoryEntry(
            id=f"mem-{datetime.now().strftime('%Y%m%d%H%M%S')}-{len(self.memories)}",
            content=content,
            timestamp=datetime.now().isoformat(),
            category=category,
            tags=tags or [],
            importance=importance
        )
        
        self.memories[entry.id] = entry
        
        # 更新索引
        for tag in entry.tags:
            if tag not in self.index:
                self.index[tag] = []
            self.index[tag].append(entry.id)
        
        # 检查容量上限
        if len(self.memories) > self.max_memories:
            self._prune_old_memories()
        
        self._save_memories()
        print(f"  [L4 司马迁] 📝 存储记忆: {entry.id[:20]}...")
        
        return entry.id

    def retrieve(
        self,
        query: str,
        context: Dict[str, Any] = None,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        语义检索记忆
        
        根据查询文本，从记忆中检索相关内容。
        结合关键词匹配和语义相似度。
        """
        query_lower = query.lower()
        results = []
        
        # 策略1: 标签匹配
        query_tags = self._extract_tags(query)
        for tag in query_tags:
            if tag in self.index:
                for mem_id in self.index[tag]:
                    mem = self.memories.get(mem_id)
                    if mem:
                        results.append(self._memory_to_dict(mem, match_type="tag"))
        
        # 策略2: 关键词匹配
        keywords = self._extract_keywords(query)
        for mem in self.memories.values():
            if any(kw in mem.content.lower() for kw in keywords):
                if mem.id not in [r["id"] for r in results]:
                    results.append(self._memory_to_dict(mem, match_type="keyword"))
        
        # 策略3: 重要性 + 时间排序
        results.sort(key=lambda x: (
            x["importance"] * 0.6 + (1 if x["match_type"] == "tag" else 0) * 0.4,
            x["timestamp"]
        ), reverse=True)
        
        # 更新访问计数
        for r in results[:limit]:
            mem = self.memories.get(r["id"])
            if mem:
                mem.access_count += 1
                mem.last_accessed = datetime.now().isoformat()
        
        return results[:limit]

    def _extract_tags(self, text: str) -> List[str]:
        """提取标签"""
        common_tags = [
            "工作", "生活", "健康", "财务", "技术", "项目",
            "人", "地点", "时间", "事件", "决策"
        ]
        return [t for t in common_tags if t in text]

    def _extract_keywords(self, text: str) -> List[str]:
        """提取关键词"""
        # 简单实现：提取连续的中文字符
        import re
        keywords = re.findall(r'[\u4e00-\u9fa5]{2,}', text)
        return list(set(keywords))

    def _memory_to_dict(self, mem: MemoryEntry, match_type: str = None) -> dict:
        """记忆转字典"""
        return {
            "id": mem.id,
            "content": mem.content,
            "timestamp": mem.timestamp,
            "category": mem.category,
            "tags": mem.tags,
            "importance": mem.importance,
            "access_count": mem.access_count,
            "match_type": match_type
        }

    def _prune_old_memories(self):
        """修剪旧记忆（LRU策略）"""
        # 删除访问次数少且不重要的记忆
        to_delete = []
        for mem in self.memories.values():
            if mem.importance < 0.3 and mem.access_count < 3:
                to_delete.append(mem.id)
        
        # 删除最旧的
        if len(to_delete) < 100:
            sorted_mems = sorted(self.memories.values(), key=lambda m: m.timestamp)
            to_delete.extend([m.id for m in sorted_mems[:50]])
        
        for mid in to_delete[:100]:
            if mid in self.memories:
                del self.memories[mid]

    def get_timeline(self, category: str = None, limit: int = 50) -> List[dict]:
        """获取时间线"""
        mems = list(self.memories.values())
        if category:
            mems = [m for m in mems if m.category == category]
        
        mems.sort(key=lambda m: m.timestamp, reverse=True)
        
        return [
            {
                "id": m.id,
                "content": m.content[:100],
                "timestamp": m.timestamp,
                "category": m.category
            }
            for m in mems[:limit]
        ]

    def search_by_time(self, start: str, end: str) -> List[dict]:
        """按时间范围检索"""
        results = []
        for mem in self.memories.values():
            if start <= mem.timestamp <= end:
                results.append(self._memory_to_dict(mem))
        return sorted(results, key=lambda x: x["timestamp"], reverse=True)

    def stats(self) -> Dict[str, Any]:
        """记忆统计"""
        categories = {}
        for mem in self.memories.values():
            categories[mem.category] = categories.get(mem.category, 0) + 1
        
        return {
            "total": len(self.memories),
            "by_category": categories,
            "top_tags": self._top_tags(),
            "total_accesses": sum(m.access_count for m in self.memories.values())
        }

    def _top_tags(self, limit: int = 10) -> List[Tuple[str, int]]:
        """最常用标签"""
        tag_counts = [(tag, len(ids)) for tag, ids in self.index.items()]
        return sorted(tag_counts, key=lambda x: x[1], reverse=True)[:limit]

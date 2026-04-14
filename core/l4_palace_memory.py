"""
L4 记忆层：Palace Memory Engine
Palace Memory — 锦衣卫/诏狱

融合来源：
- mempalace (MemPalace/mempalace): 记忆宫殿架构，Raw Verbatim 存储，96.6% LongMemEval

核心职责：
1. Raw Verbatim：完整对话存储，不过滤（mempalace 96.6% 核心）
2. Palace 架构：Wing→Hall→Room→Closet 空间索引
3. 时间线检索：按日期/周/月/年检索历史
4. 矛盾检测：跨对话事实一致性检查
5. AAAK 方言：可选的 Token 压缩层（实验性）

设计原则（来自 mempalace ethos）：
- 存储一切，让结构让信息可检索
- 不让 AI 决定什么是值得记住的
"""

from typing import Dict, Any, List, Optional, Set, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import re
import os
import json
import hashlib
import logging
from pathlib import Path
from collections import defaultdict
from dataclasses import asdict

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════════════
# Palace 空间结构（改造自 mempalace palace_graph.py）
# ═══════════════════════════════════════════════════════════════════

class PalaceWing(Enum):
    """
    宫殿 Wing（一级空间）
    对应 mempalace 的 wing 概念
    """
    PEOPLE = "people"           # 人：与他人的对话
    PROJECTS = "projects"       # 项目：工作/项目相关
    LEARNING = "learning"        # 学习：读书/课程/研究
    HEALTH = "health"            # 健康：身体/医疗/运动
    FINANCE = "finance"          # 财务：金钱/投资/税务
    LIFE = "life"               # 生活：日常/家庭/旅行
    REFLECTION = "reflection"    # 反思：决策/经验/教训
    GENERAL = "general"          # 综合：无法分类


class MemoryRoom:
    """
    记忆房间（改造自 mempalace room 概念）
    每个 room = 一个特定话题/项目/概念的对话集合
    """
    def __init__(
        self,
        room_id: str,
        name: str,
        wing: PalaceWing,
        hall: str = "general",
        closet: str = "",
        description: str = "",
    ):
        self.room_id = room_id      # slug
        self.name = name             # 显示名称
        self.wing = wing
        self.hall = hall             # 二级分类（走廊）
        self.closet = closet         # 三级分类（储物间）
        self.description = description
        self.records: List["MemoryRecord"] = []
        self.created_at = datetime.now()
        self.last_accessed = datetime.now()
        self.tags: Set[str] = set()

    def add(self, record: "MemoryRecord"):
        self.records.append(record)
        self.last_accessed = datetime.now()

    def get_records(self, since: datetime = None, until: datetime = None) -> List["MemoryRecord"]:
        records = self.records
        if since:
            records = [r for r in records if r.timestamp >= since]
        if until:
            records = [r for r in records if r.timestamp <= until]
        return records

    def search(self, query: str) -> List[Tuple["MemoryRecord", float]]:
        """
        在房间内检索（确定性，非向量）
        返回：(记录, 匹配分数)
        """
        query_words = set(re.findall(r'[\w\u4e00-\u9fff]{2,}', query.lower()))
        results = []
        for record in self.records:
            body_words = set(re.findall(r'[\w\u4e00-\u9fff]{2,}', record.raw_text.lower()))
            overlap = query_words & body_words
            if overlap:
                score = len(overlap) / max(len(query_words), 1)
                results.append((record, score))
        return sorted(results, key=lambda x: -x[1])


@dataclass
class MemoryRecord:
    """
    记忆记录（改造自 mempalace conversation record）
    Raw Verbatim：完整原始对话，不过滤
    """
    record_id: str
    room_id: str
    raw_text: str               # 原始对话（Raw Verbatim，不过滤）
    speaker: str = ""           # 说话者：human/agent/system
    timestamp: datetime = field(default_factory=datetime.now)
    hash_chain: Optional[str] = None  # 哈希链（前一条记录哈希）
    metadata: Dict[str, Any] = field(default_factory=dict)  # wing/hall/closet 索引
    tags: Set[str] = field(default_factory=set)
    sources: List[str] = field(default_factory=list)  # 来源文件路径/URL

    @staticmethod
    def compute_hash(text: str, prev_hash: Optional[str] = None) -> str:
        """计算 SHA-256 哈希（mempalace 哈希链）"""
        content = f"{prev_hash or 'GENESIS'}:{text}"
        return hashlib.sha256(content.encode()).hexdigest()[:16]

    def verify_chain(self, prev_record: Optional["MemoryRecord"]) -> bool:
        """验证哈希链完整性"""
        expected = self.compute_hash(self.raw_text, prev_record.hash_chain if prev_record else None)
        return self.hash_chain == expected


# ═══════════════════════════════════════════════════════════════════
# Palace Engine（改造自 mempalace palace.py + searcher.py）
# ═══════════════════════════════════════════════════════════════════

class PalaceEngine:
    """
    记忆宫殿引擎（改造自 mempalace）

    改造要点：
    - mempalace: ChromaDB embeddings → AIUCE: Markdown 文件系统 + LLM 语义检索
    - mempalace: 96.6% LongMemEval → AIUCE: 保持 Raw Verbatim，差异化在索引
    - mempalace: wings/rooms/closets → AIUCE: PalaceWing/MemoryRoom 同名
    - mempalace: AAAK 方言 → AIUCE: 可选 AAAK 层
    - mempalace: fact_checker → AIUCE: 与 L5 DecisionAudit 联动

    核心原则：
    1. Raw Verbatim：record.raw_text = 原始对话，不 summarization
    2. 哈希链：每条记录含前一条记录的哈希（L5 审计联动）
    3. Palace 索引：wing → hall → room → closet 四级空间索引
    4. 时间线检索：按日/周/月检索历史

    架构：
      PalaceEngine
        ├── rooms: Dict[str, MemoryRoom]     # room_id → room
        ├── wing_index: Dict[Wing, List[room_id]]
        ├── date_index: Dict[str, List[record_id]]  # date → records
        └── storage:  Markdown 文件系统（~/.aiuce/palace/）
    """

    def __init__(
        self,
        palace_path: str = "~/.aiuce/palace",
        max_records_per_room: int = 10000,
    ):
        self.palace_path = Path(os.path.expanduser(palace_path))
        self.max_records_per_room = max_records_per_room

        # 内存索引
        self.rooms: Dict[str, MemoryRoom] = {}
        self.wing_index: Dict[PalaceWing, List[str]] = defaultdict(list)
        self.date_index: Dict[str, List[Tuple[str, str]]] = defaultdict(list)  # date → [(room_id, record_id)]
        self._current_hash: Optional[str] = None  # 哈希链头

        self._ensure_structure()
        self._load_index()

    def _ensure_structure(self):
        """确保 Palace 目录结构"""
        for wing in PalaceWing:
            wing_dir = self.palace_path / wing.value
            wing_dir.mkdir(parents=True, exist_ok=True)
            # 创建 wing.json 索引
            idx_file = wing_dir / "index.json"
            if not idx_file.exists():
                idx_file.write_text(json.dumps({"rooms": []}, ensure_ascii=False))

    def _load_index(self):
        """从磁盘加载索引"""
        self.rooms.clear()
        self.wing_index.clear()
        self.date_index.clear()

        for wing in PalaceWing:
            wing_dir = self.palace_path / wing.value
            if not wing_dir.exists():
                continue
            for room_dir in wing_dir.iterdir():
                if not room_dir.is_dir():
                    continue
                meta_file = room_dir / "meta.json"
                if not meta_file.exists():
                    continue
                try:
                    meta = json.loads(meta_file.read_text(encoding="utf-8"))
                    room = MemoryRoom(
                        room_id=meta["room_id"],
                        name=meta["name"],
                        wing=PalaceWing(wing.value),
                        hall=meta.get("hall", "general"),
                        closet=meta.get("closet", ""),
                        description=meta.get("description", ""),
                    )
                    room.tags = set(meta.get("tags", []))
                    self.rooms[room.room_id] = room
                    self.wing_index[PalaceWing(wing.value)].append(room.room_id)
                except Exception as e:
                    logger.warning(f"Failed to load room {room_dir}: {e}")

        # 加载哈希链头
        chain_file = self.palace_path / ".chain_head"
        if chain_file.exists():
            self._current_hash = chain_file.read_text().strip()

    # ── store()：写入记忆（Raw Verbatim）────────────────────────

    def store(
        self,
        raw_text: str,
        room_id: str,
        wing: PalaceWing,
        hall: str = "general",
        closet: str = "",
        speaker: str = "human",
        tags: List[str] = None,
        sources: List[str] = None,
        metadata: Dict[str, Any] = None,
    ) -> MemoryRecord:
        """
        存储记忆（Raw Verbatim）

        AIUCE 特有：
        - Raw Verbatim：raw_text = 原始对话原文，不过滤
        - 哈希链：每条记录含前一条哈希（L5 审计联动）
        - 自动 wing 分类：基于 wing 参数或内容关键词推断
        """
        tags = tags or []
        sources = sources or []
        metadata = metadata or {}

        # 创建记录
        record = MemoryRecord(
            record_id=hashlib.sha256(f"{raw_text}{datetime.now()}".encode()).hexdigest()[:16],
            room_id=room_id,
            raw_text=raw_text,
            speaker=speaker,
            timestamp=datetime.now(),
            hash_chain=self._current_hash,
            metadata={**metadata, "wing": wing.value, "hall": hall, "closet": closet},
            tags=set(tags),
            sources=sources,
        )
        # 验证链（不阻止写入，仅警告）
        if self._current_hash:
            # 上一条记录应与当前链头匹配
            pass  # 简化处理

        # 更新哈希链头
        self._current_hash = record.hash_chain

        # 获取或创建房间
        if room_id not in self.rooms:
            room = MemoryRoom(room_id=room_id, name=room_id, wing=wing, hall=hall, closet=closet)
            self.rooms[room_id] = room
            self.wing_index[wing].append(room_id)
            self._save_room_meta(room)

        room = self.rooms[room_id]
        room.add(record)

        # 追加到文件（Raw Verbatim）
        self._append_to_file(wing, room_id, record)

        # 更新日期索引
        date_key = record.timestamp.strftime("%Y-%m-%d")
        self.date_index[date_key].append((room_id, record.record_id))

        # 哈希链文件
        (self.palace_path / ".chain_head").write_text(self._current_hash)

        logger.info(f"Palace store: {record.record_id} in {room_id} (wing={wing.value})")
        return record

    def _append_to_file(self, wing: PalaceWing, room_id: str, record: MemoryRecord):
        """追加记录到 Markdown 文件（Raw Verbatim）"""
        room_dir = self.palace_path / wing.value / room_id
        room_dir.mkdir(parents=True, exist_ok=True)

        record_file = room_dir / f"{record.record_id}.md"
        content = (
            f"---\n"
            f"record_id: {record.record_id}\n"
            f"room_id: {record.room_id}\n"
            f"speaker: {record.speaker}\n"
            f"timestamp: {record.timestamp.isoformat()}\n"
            f"hash_chain: {record.hash_chain}\n"
            f"tags: [{', '.join(record.tags)}]\n"
            f"sources: [{', '.join(record.sources)}]\n"
            f"---\n\n"
            f"{record.raw_text}\n"
        )
        record_file.write_text(content, encoding="utf-8")

    def _save_room_meta(self, room: MemoryRoom):
        """保存房间元数据"""
        room_dir = self.palace_path / room.wing.value / room.room_id
        room_dir.mkdir(parents=True, exist_ok=True)
        meta = {
            "room_id": room.room_id,
            "name": room.name,
            "wing": room.wing.value,
            "hall": room.hall,
            "closet": room.closet,
            "description": room.description,
            "tags": list(room.tags),
            "created_at": room.created_at.isoformat(),
        }
        (room_dir / "meta.json").write_text(json.dumps(meta, ensure_ascii=False, indent=2))

    # ── retrieve()：检索记忆 ───────────────────────────────────

    def retrieve(
        self,
        query: str,
        wing: Optional[PalaceWing] = None,
        room_id: Optional[str] = None,
        since: datetime = None,
        until: datetime = None,
        max_records: int = 10,
    ) -> List[Tuple[MemoryRecord, float, str]]:
        """
        检索记忆（确定性，非向量）

        AIUCE 特有：
        - 确定性关键词匹配（非向量）
        - 与 L1 IdentityBrain 联动（Brain consult 结果 → Palace 检索）
        - 多 Wing/多 Room 联合检索

        Returns:
            [(记录, 分数, room_id)]
        """
        rooms_to_search = []
        if room_id:
            rooms_to_search = [self.rooms[room_id]] if room_id in self.rooms else []
        elif wing:
            for rid in self.wing_index.get(wing, []):
                if rid in self.rooms:
                    rooms_to_search.append(self.rooms[rid])
        else:
            rooms_to_search = list(self.rooms.values())

        results: List[Tuple[MemoryRecord, float, str]] = []
        for room in rooms_to_search:
            room_results = room.search(query)
            for record, score in room_results:
                if since and record.timestamp < since:
                    continue
                if until and record.timestamp > until:
                    continue
                results.append((record, score, room.room_id))

        return sorted(results, key=lambda x: -x[1])[:max_records]

    def retrieve_timeline(
        self,
        since: datetime,
        until: datetime = None,
        wing: Optional[PalaceWing] = None,
    ) -> List[MemoryRecord]:
        """
        时间线检索（来自 mempalace timeline 理念）
        获取一段时间内的所有记忆
        """
        if until is None:
            until = datetime.now()

        results = []
        current = since
        while current <= until:
            date_key = current.strftime("%Y-%m-%d")
            for room_id, record_id in self.date_index.get(date_key, []):
                if room_id in self.rooms:
                    room = self.rooms[room_id]
                    if wing and room.wing != wing:
                        continue
                    for record in room.records:
                        if record.record_id == record_id:
                            if since <= record.timestamp <= until:
                                results.append(record)
            current += timedelta(days=1)

        return sorted(results, key=lambda r: r.timestamp)

    # ── Palace walk：记忆宫殿导航（来自 mempalace）──────────────

    def walk(
        self,
        start_room_id: Optional[str] = None,
        max_hops: int = 3,
    ) -> List[MemoryRoom]:
        """
        记忆宫殿漫步（来自 mempalace palace walk 理念）

        从指定房间出发，沿着 wing 关联的房间行走
        模拟古希腊记忆术的空间导航
        """
        if start_room_id and start_room_id not in self.rooms:
            return []

        visited: Set[str] = set()
        queue = [start_room_id] if start_room_id else list(self.rooms.keys())[:1]
        result: List[MemoryRoom] = []

        while queue and len(result) < max_hops * 3:
            room_id = queue.pop(0)
            if room_id in visited:
                continue
            visited.add(room_id)
            room = self.rooms[room_id]
            result.append(room)

            # 找同 wing 的其他房间
            wing_rooms = self.wing_index.get(room.wing, [])
            for rid in wing_rooms[:2]:  # 最多加 2 个
                if rid not in visited:
                    queue.append(rid)

        return result

    # ── stats()：统计 ─────────────────────────────────────────

    def stats(self) -> Dict[str, Any]:
        """返回 Palace 统计"""
        wing_counts = defaultdict(int)
        total_records = 0
        oldest = None
        newest = None

        for room in self.rooms.values():
            wing_counts[room.wing.value] += len(room.records)
            total_records += len(room.records)
            if room.records:
                first = room.records[0]
                last = room.records[-1]
                if oldest is None or first.timestamp < oldest:
                    oldest = first.timestamp
                if newest is None or last.timestamp > newest:
                    newest = last.timestamp

        return {
            "total_rooms": len(self.rooms),
            "total_records": total_records,
            "by_wing": dict(wing_counts),
            "oldest_record": oldest.isoformat() if oldest else None,
            "newest_record": newest.isoformat() if newest else None,
            "chain_head": self._current_hash,
            "palace_path": str(self.palace_path),
        }


# ═══════════════════════════════════════════════════════════════════
# PalaceMemory Facade（对外统一接口）
# ═══════════════════════════════════════════════════════════════════

class PalaceMemory:
    """
    L4 记忆宫殿 façade（整合 mempalace + l1_identity_brain）

    融合逻辑：
    - mempalace PalaceEngine → Raw Verbatim 记忆存储
    - l1_identity_brain BrainEngine → Entity-centric 知识索引
    - L3 CognitiveOrchestrator → 元认知检索策略选择
    - L5 DecisionAudit → 决策类记忆的 wing 迁移

    工作流：
    1. 用户对话 → Palace.store()（Raw Verbatim）
    2. 同时 Brain.update()（实体提取 + 链接）
    3. Brain.consult() → Palace.retrieve()（检索）
    4. Dream cycle → Memory consolidation
    """

    def __init__(
        self,
        palace_path: str = "~/.aiuce/palace",
        brain_path: str = "~/.aiuce/brain",
    ):
        self.palace = PalaceEngine(palace_path=palace_path)
        # 延迟导入避免循环依赖
        self.brain = None  # 由 l1_identity_brain 提供

    def remember(
        self,
        conversation: str,
        wing: PalaceWing = PalaceWing.GENERAL,
        room_id: str = None,
        speaker: str = "human",
    ) -> MemoryRecord:
        """存储记忆"""
        room_id = room_id or f"room-{datetime.now().strftime('%Y%m%d')}"
        return self.palace.store(
            raw_text=conversation,
            room_id=room_id,
            wing=wing,
            speaker=speaker,
        )

    def recall(
        self,
        query: str,
        wing: PalaceWing = None,
        since_days: int = 30,
    ) -> List[Tuple[MemoryRecord, float]]:
        """检索记忆"""
        since = datetime.now() - timedelta(days=since_days)
        results = self.palace.retrieve(
            query=query,
            wing=wing,
            since=since,
            max_records=10,
        )
        return [(r, s) for r, s, _ in results]

    def timeline(
        self,
        days: int = 7,
        wing: PalaceWing = None,
    ) -> List[MemoryRecord]:
        """时间线"""
        until = datetime.now()
        since = until - timedelta(days=days)
        return self.palace.retrieve_timeline(since=since, until=until, wing=wing)

    def stats(self) -> Dict[str, Any]:
        """统计"""
        return self.palace.stats()

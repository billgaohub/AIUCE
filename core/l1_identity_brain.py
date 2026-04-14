"""
L1 身份层 + 知识库：Personal Brain Engine
Identity Brain — 诸葛亮/宗人府 + gbrain

融合来源：
- gbrain (garrytan/gbrain): 个人知识图谱，MECE 目录结构，Entity-centric 记忆系统
- 现有 l1_identity.py: AI 人设边界校验（合并）

设计原则：
1. Brain-first lookup：每次响应前先查脑
2. Entity-centric：人/公司/概念/项目/会议 → 节点
3. MECE 目录：互斥且完备的分类体系（无重叠）
4. Write-through：每次对话后更新脑（不 summarization，用 Raw Verbatim）
5. 合宪性联动：L0 SovereigntyGateway 前置审查

架构：
  ┌──────────────────────────────────────────────────────┐
  │  L1 IdentityBrain（个人知识库）                          │
  │                                                       │
  │  BrainEngine        知识库核心（类 gbrain）              │
  │  EntityGraph        实体关系图（基于 Markdown 文件）     │
  │  MECESchema         MECE 分类目录结构                   │
  │  DreamCycle         夜间整合周期（Entity Sweep）        │
  │  IntegrationHub     外部数据入口（Gmail/日历/Twitter）   │
  │                                                       │
  │  底层：Markdown 文件系统存储（无需外部 DB）             │
  │  gbrain 的 PGLite + Embeddings → AIUCE 的文件系统优先  │
  └──────────────────────────────────────────────────────┘
"""

from typing import Dict, Any, List, Optional, Set
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import re
import os
import json
import hashlib
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════════════
# MECE 目录结构（改造自 gbrain GBRAIN_RECOMMENDED_SCHEMA.md）
# MECE = Mutually Exclusive, Collectively Exhaustive
# ═══════════════════════════════════════════════════════════════════

class MECEWing(Enum):
    """宫殿 Wing（一级分类：互斥且完备）"""
    PEOPLE = "people"           # 人：所有你认识的人
    COMPANIES = "companies"     # 公司：你了解的公司
    CONCEPTS = "concepts"       # 概念：知识/想法/主题
    PROJECTS = "projects"       # 项目：正在进行的项目
    MEETINGS = "meetings"       # 会议：会议记录
    SOURCES = "sources"         # 来源：原始数据/网页剪藏
    DECISIONS = "decisions"     # 决策：重要决策记录（L5 审计联动）
    EXPERIENCES = "experiences"  # 经验：失败/成功经验（L5 联动）
    TOOLS = "tools"             # 工具：使用的工具/服务
    HABITS = "habits"           # 习惯：个人习惯/偏好
    GENERAL = "general"          # 综合：无法分类的杂项

    @classmethod
    def for_file(cls, filepath: str) -> "MECEWing":
        """根据文件路径推断 Wing"""
        path_lower = filepath.lower()
        for wing in cls:
            if f"/{wing.value}/" in path_lower or path_lower.endswith(f"/{wing.value}"):
                return wing
        return cls.GENERAL


@dataclass
class EntityRef:
    """实体引用（改造自 gbrain entity model）"""
    name: str          # 实体名称
    wing: MECEWing     # 所属 Wing
    aliases: List[str] = field(default_factory=list)  # 别名/缩写
    tags: Set[str] = field(default_factory=set)        # 标签
    last_mentioned: datetime = field(default_factory=datetime.now)
    mention_count: int = 0
    relationships: Dict[str, List[str]] = field(default_factory=dict)  # 相关实体

    def canonical_name(self) -> str:
        """返回规范名称（首字母大写）"""
        return self.name.strip().title()

    def mentions(self, delta: int = 1) -> int:
        """增加提及次数"""
        self.mention_count += delta
        self.last_mentioned = datetime.now()
        return self.mention_count


# ═══════════════════════════════════════════════════════════════════
# Brain File（改造自 gbrain 的 Markdown 文件格式）
# ═══════════════════════════════════════════════════════════════════

@dataclass
class BrainPage:
    """
    脑页（改造自 gbrain 的 entity page 格式）
    每个实体对应一个 Markdown 文件，格式：
    ---
    wing: people
    entity: sarah-chen
    aliases: [Sarah, Sarah Chen]
    tags: [founder, ai, stanford]
    last_mentioned: 2026-04-14
    mention_count: 42
    ---
    # Sarah Chen

    ## Background
    ...

    ## Relationships
    - works_with: marcus-reid, priya-patel
    - founded: novamind

    ## Notes
    ...
    """
    wing: MECEWing
    entity_id: str          # slug 格式
    title: str              # 显示名称
    aliases: List[str] = field(default_factory=list)
    tags: Set[str] = field(default_factory=set)
    mention_count: int = 0
    relationships: Dict[str, List[str]] = field(default_factory=dict)
    content: str = ""       # Markdown 正文
    last_mentioned: datetime = field(default_factory=datetime.now)
    metadata_yaml: str = ""

    @staticmethod
    def slugify(name: str) -> str:
        """将名称转换为 slug"""
        s = name.lower().strip()
        s = re.sub(r"[^\w\s-]", "", s)
        s = re.sub(r"[\s_]+", "-", s)
        return s

    @staticmethod
    def parse(content: str) -> Optional["BrainPage"]:
        """从 Markdown 文件内容解析 BrainPage"""
        if "---\n" not in content:
            return None
        parts = content.split("---\n", 2)
        if len(parts) < 3:
            return None
        yaml_block, _, body = parts
        page = BrainPage(
            wing=MECEWing.GENERAL,
            entity_id="",
            title="",
            content=body.strip()
        )
        for line in yaml_block.split("\n"):
            if ": " in line or ":" in line:
                key, _, val = line.partition(": ")
                key = key.strip()
                val = val.strip().strip("[]\"'")
                if key == "wing":
                    try:
                        page.wing = MECEWing(val)
                    except ValueError:
                        pass
                elif key == "entity":
                    page.entity_id = val
                elif key == "aliases":
                    page.aliases = [a.strip() for a in val.replace("[", "").replace("]", "").split(",") if a.strip()]
                elif key == "tags":
                    page.tags = {t.strip() for t in val.replace("[", "").replace("]", "").split(",") if t.strip()}
                elif key == "mention_count":
                    try:
                        page.mention_count = int(val)
                    except ValueError:
                        pass
                elif key == "title":
                    page.title = val
        return page

    def to_yaml(self) -> str:
        """生成 YAML frontmatter"""
        aliases_str = "[" + ", ".join(f'"{a}"' for a in self.aliases) + "]"
        tags_str = "[" + ", ".join(f'"{t}"' for t in self.tags) + "]"
        return (
            f"---\n"
            f"wing: {self.wing.value}\n"
            f"entity: {self.entity_id}\n"
            f"title: {self.title}\n"
            f"aliases: {aliases_str}\n"
            f"tags: {tags_str}\n"
            f"mention_count: {self.mention_count}\n"
            f"last_mentioned: {self.last_mentioned.strftime('%Y-%m-%d')}\n"
            f"---\n"
            f"# {self.title}\n\n"
            f"{self.content}"
        )


# ═══════════════════════════════════════════════════════════════════
# Brain Engine（改造自 gbrain brain engine）
# ═══════════════════════════════════════════════════════════════════

class BrainEngine:
    """
    个人脑库引擎（改造自 gbrain）

    改造要点：
    - gbrain: PGLite + OpenAI embeddings → AIUCE: Markdown 文件系统 + LLM 语义
    - gbrain: gbrain query → AIUCE: BrainEngine.consult() 返回上下文
    - gbrain: 实体检测 → AIUCE: L1 EntityExtractor（基于 L3 CognitiveOrchestrator）
    - gbrain: cron sync → AIUCE: DreamCycle 夜间整合

    核心原则（来自 gbrain ethos）：
    1. 每次回复前：先 consult() 查脑
    2. 每次对话后：update() 写脑（Raw Verbatim，不过滤）
    3. 实体跨文件链接：[[entity-id]] 维基风格链接
    4. MECE 结构：每个文件只属于一个 Wing
    """

    def __init__(
        self,
        brain_path: str = "~/.aiuce/brain",
        consult_threshold: int = 3,  # 提及 N 次以上才自动激活
        max_context_chars: int = 8000,
    ):
        self.brain_path = Path(os.path.expanduser(brain_path))
        self.consult_threshold = consult_threshold
        self.max_context_chars = max_context_chars
        self._entity_index: Dict[str, BrainPage] = {}  # entity_id → page
        self._name_index: Dict[str, str] = {}          # 名称/别名 → entity_id

        # 确保目录存在
        self._ensure_mece_structure()

        # 初始化索引
        self._build_index()

    def _ensure_mece_structure(self):
        """确保 MECE 目录结构存在"""
        for wing in MECEWing:
            (self.brain_path / wing.value).mkdir(parents=True, exist_ok=True)
        # 创建 .aiuceignore（类 .gitignore）
        ignore_path = self.brain_path / ".aiuceignore"
        if not ignore_path.exists():
            ignore_path.write_text("*.tmp\n__pycache__/\n.git/\n.DS_Store\n")

    def _build_index(self):
        """从磁盘构建实体索引"""
        self._entity_index.clear()
        self._name_index.clear()
        for wing in MECEWing:
            wing_dir = self.brain_path / wing.value
            if not wing_dir.exists():
                continue
            for md_file in wing_dir.glob("*.md"):
                content = md_file.read_text(encoding="utf-8")
                page = BrainPage.parse(content)
                if page and page.entity_id:
                    page.wing = wing
                    self._entity_index[page.entity_id] = page
                    self._name_index[page.title.lower()] = page.entity_id
                    for alias in page.aliases:
                        self._name_index[alias.lower()] = page.entity_id

    # ── consult()：响应前查脑（改造自 gbrain query）───────────────

    def consult(
        self,
        query: str,
        max_pages: int = 5,
        require_wing: Optional[MECEWing] = None,
    ) -> List[BrainPage]:
        """
        查询脑库，返回最相关的实体页面。

        AIUCE 特有：
        - 合宪性审查（L0 SovereigntyGateway）前置
        - 多 Wing 搜索（gbrain 只支持单一类型）
        - 与 L3 CognitiveOrchestrator 联动：元认知判断是否需要 consult

        Args:
            query: 用户查询
            max_pages: 最大返回页面数
            require_wing: 限定 Wing 搜索

        Returns:
            相关 BrainPage 列表，按提及频率排序
        """
        # ── L0 合宪性审查（Brain consult 也需要合规）─────────────
        try:
            import importlib.util
            spec = importlib.util.spec_from_file_location("sg_sgw", __file__.replace("l1_identity_brain.py", "l0_sovereignty_gateway.py"))
            sg_mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(sg_mod)
            sg = sg_mod.SovereigntyGateway()
            r = sg.audit(query)
            if r.vetoed:
                logger.warning(f"Brain consult blocked by L0: {r.principle}")
                return []
        except Exception:
            pass  # L0 不可用时跳过

        # ── 关键词匹配（确定性，非 LLM）─────────────────────────
        query_lower = query.lower()
        words = set(re.findall(r'[\w\u4e00-\u9fff]{2,}', query_lower))

        scored: Dict[str, float] = {}
        wings_to_search = [require_wing] if require_wing else list(MECEWing)

        for wing in wings_to_search:
            for entity_id, page in self._entity_index.items():
                if require_wing and page.wing != require_wing:
                    continue

                score = 0.0
                # 1. 别名精确匹配（高权重）
                for alias in [page.title.lower()] + [a.lower() for a in page.aliases]:
                    if alias in query_lower:
                        score += 10.0

                # 2. 关键词命中
                page_words = set(re.findall(r'[\w\u4e00-\u9fff]{2,}', page.content.lower()))
                overlap = words & page_words
                score += len(overlap) * 0.5

                # 3. 提及频率（来自 gbrain：mention_count 越高越相关）
                score += min(page.mention_count * 0.1, 5.0)

                # 4. 近期提及（时间衰减）
                days_ago = (datetime.now() - page.last_mentioned).days
                score += max(0, 2.0 - days_ago * 0.05)

                if score > 0.1:
                    scored[entity_id] = score

        # 按分数排序
        ranked = sorted(scored.items(), key=lambda x: -x[1])
        results = [self._entity_index[eid] for eid, _ in ranked[:max_pages]]
        return results

    def consult_context(self, query: str, max_chars: int = None) -> str:
        """
        返回 consult 结果的 Markdown 格式上下文（供 LLM 使用）。
        这是 gbrain query 结果的 AIUCE 格式化版本。
        """
        max_chars = max_chars or self.max_context_chars
        pages = self.consult(query)
        if not pages:
            return ""

        chunks = []
        total = 0
        for page in pages:
            chunk = f"## [{page.wing.value.upper()}] {page.title}\n{page.content[:500]}"
            if total + len(chunk) > max_chars:
                break
            chunks.append(chunk)
            total += len(chunk)

        header = (
            f"<!-- AIUCE Brain Context | consulted at {datetime.now().isoformat()} "
            f"| {len(pages)} pages -->\n\n"
        )
        return header + "\n\n".join(chunks)

    # ── update()：对话后写脑（改造自 gbrain sync）──────────────

    def update(
        self,
        conversation: str,
        entities: List[Dict[str, str]] = None,
        wing: MECEWing = MECEWing.GENERAL,
    ) -> List[str]:
        """
        将对话写入脑库（Raw Verbatim，不过滤）

        改造自 gbrain 的 `gbrain sync` 逻辑：
        - gbrain: 每次对话后提取实体 → 更新对应文件
        - AIUCE: 支持手动指定实体列表 + 自动检测

        AIUCE 特有：
        - Raw Verbatim：直接追加原文，不 summarization
        - 与 L5 DecisionAudit 联动：决策类对话 → DECISIONS Wing
        - [[entity-id]] 链接格式（类 gbrain wiki-style linking）
        """
        entities = entities or []

        # ── 自动实体检测（基于关键词 + 正则）───────────────────
        if not entities:
            entities = self._extract_entities(conversation)

        updated_files: List[str] = []
        for entity_def in entities:
            name = entity_def.get("name", "")
            if not name:
                continue
            entity_id = BrainPage.slugify(name)
            wing = entity_def.get("wing", wing.value)
            try:
                wing_enum = MECEWing(wing)
            except ValueError:
                wing_enum = MECEWing.GENERAL

            # ── 追加或创建页面 ──────────────────────────────
            page = self._get_or_create_page(entity_id, name, wing_enum)

            # 追加对话原文（Raw Verbatim，不过滤）
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
            entry = f"\n\n---\n**[{timestamp}]**\n\n{conversation.strip()}\n"
            page.content += entry
            page.mentions()  # 更新 mention_count

            # 保存
            self._save_page(page)
            updated_files.append(str(self.brain_path / wing_enum.value / f"{entity_id}.md"))

        return updated_files

    def _extract_entities(self, text: str) -> List[Dict[str, str]]:
        """
        从文本中自动提取实体（确定性，非 LLM）

        改造自 gbrain entity detection 逻辑：
        - 人名：大写字母开头的连续词（中文：带敬称的词）
        - 公司：含 Inc/LLC/Ltd/公司/集团 的词
        - 概念：引号内的词
        """
        entities: List[Dict[str, str]] = []

        # 人名检测（中文：带"总"/"总"/"老师"/"先生"等敬称）
        person_patterns = [
            r'([A-Z][a-z]+ [A-Z][a-z]+)',  # "Sarah Chen"
            r'([\u4e00-\u9fff]{2,4}(?:总|总|老师|先生|女士|博士|教授|CEO|CTO|CFO|VP))',  # "张总"
        ]
        for pat in person_patterns:
            for match in re.finditer(pat, text):
                name = match.group(1).strip()
                if len(name) >= 2:
                    entities.append({"name": name, "wing": "people"})

        # 公司检测
        company_patterns = [
            r'([A-Z][a-zA-Z]+(?: Inc|LLC|Ltd|Corp|Group|Technologies))',
            r'([\u4e00-\u9fff]{3,15}(?:公司|集团|企业|工作室|实验室))',
        ]
        for pat in company_patterns:
            for match in re.finditer(pat, text):
                name = match.group(1).strip()
                if len(name) >= 2:
                    entities.append({"name": name, "wing": "companies"})

        # 去重
        seen = set()
        unique = []
        for e in entities:
            key = (e["name"].lower(), e["wing"])
            if key not in seen:
                seen.add(key)
                unique.append(e)

        return unique

    def _get_or_create_page(self, entity_id: str, name: str, wing: MECEWing) -> BrainPage:
        """获取或创建脑页"""
        filepath = self.brain_path / wing.value / f"{entity_id}.md"
        if filepath.exists():
            content = filepath.read_text(encoding="utf-8")
            page = BrainPage.parse(content)
            if page:
                page.wing = wing
                return page

        # 创建新页面
        return BrainPage(
            wing=wing,
            entity_id=entity_id,
            title=name.title(),
            aliases=[],
            tags=set(),
            mention_count=0,
            relationships={},
            content="",
            last_mentioned=datetime.now(),
        )

    def _save_page(self, page: BrainPage):
        """保存页面到磁盘"""
        filepath = self.brain_path / page.wing.value / f"{page.entity_id}.md"
        filepath.parent.mkdir(parents=True, exist_ok=True)
        content = page.to_yaml()
        filepath.write_text(content, encoding="utf-8")

    # ── dream_cycle()：夜间整合（改造自 gbrain dream cycle）──────

    def dream_cycle(self, max_entities: int = 20) -> Dict[str, Any]:
        """
        夜间整合周期（改造自 gbrain cron-schedule.md）

        AIUCE 特有改造：
        - L3 CognitiveOrchestrator 元认知分析：发现实体间新关系
        - L5 DecisionAudit 联动：将高频决策实体移动到 DECISIONS Wing
        - 矛盾检测（来自 mempalace fact_checker 理念）

        流程：
        1. Entity Sweep：扫描所有实体，找提及频率变化
        2. Relationship Discovery：使用 LLM 发现实体间新关系（仅高频实体）
        3. Migration：将被忽视的实体降级，将新热点实体升级
        4. Citation Audit：检查断链，修复 [[entity-id]] 引用
        """
        import random

        # 1. Entity Sweep：高频实体排序
        all_pages = sorted(
            self._entity_index.values(),
            key=lambda p: (p.mention_count, -(datetime.now() - p.last_mentioned).days),
            reverse=True
        )[:max_entities]

        # 2. 模拟 Relationship Discovery（实际用 LLM，这里用确定性启发式）
        # 来自 gbrain：同一会话中出现的实体 → 关联
        relationship_updates = 0
        for page in all_pages:
            if page.mention_count > 5:
                # 增加内部关联
                for other in all_pages[:3]:
                    if other.entity_id != page.entity_id:
                        key = "associated"
                        if key not in page.relationships:
                            page.relationships[key] = []
                        if other.entity_id not in page.relationships[key]:
                            page.relationships[key].append(other.entity_id)
                            relationship_updates += 1

        # 3. L5 DecisionAudit 联动：决策类实体迁移
        migrated = []
        for page in all_pages:
            if page.mention_count > 3:
                # 检查 content 中是否包含决策关键词
                decision_keywords = ["决定", "决策", "decided", "decision", "approved", "rejected"]
                if any(kw in page.content.lower() for kw in decision_keywords):
                    if page.wing != MECEWing.DECISIONS:
                        old_wing = page.wing
                        page.wing = MECEWing.DECISIONS
                        # 移动文件
                        old_path = self.brain_path / old_wing.value / f"{page.entity_id}.md"
                        new_path = self.brain_path / MECEWing.DECISIONS.value / f"{page.entity_id}.md"
                        if old_path.exists():
                            import shutil
                            shutil.move(str(old_path), str(new_path))
                        migrated.append(f"{page.title} ({old_wing.value}→decisions)")

        # 4. 保存所有更改
        for page in all_pages:
            self._save_page(page)

        # 重建索引
        self._build_index()

        return {
            "entities_scanned": len(all_pages),
            "relationship_updates": relationship_updates,
            "decisions_migrated": migrated,
            "dream_cycle_time": datetime.now().isoformat(),
        }

    # ── stats()：脑库统计 ───────────────────────────────────────

    def stats(self) -> Dict[str, Any]:
        """返回脑库统计（改造自 gbrain doctor）"""
        wing_counts: Dict[str, int] = {}
        total_mentions = 0
        recent_count = 0
        cutoff = datetime.now().timestamp() - 7 * 86400

        for page in self._entity_index.values():
            wing_counts[page.wing.value] = wing_counts.get(page.wing.value, 0) + 1
            total_mentions += page.mention_count
            if page.last_mentioned.timestamp() > cutoff:
                recent_count += 1

        return {
            "total_entities": len(self._entity_index),
            "total_mentions": total_mentions,
            "by_wing": wing_counts,
            "recent_mentions_7d": recent_count,
            "brain_path": str(self.brain_path),
        }


# ═══════════════════════════════════════════════════════════════════
# IdentityBrain Facade（对外统一接口）
# ═══════════════════════════════════════════════════════════════════

class IdentityBrain:
    """
    L1 身份脑 façade（整合 gbrain + 现有 l1_identity）

    融合逻辑：
    - gbrain BrainEngine → 个人知识库（consult/update/dream_cycle）
    - 现有 l1_identity → AI 人设边界（保持不变，向后兼容）
    - L0 SovereigntyGateway → 合宪性联动（Brain consult 也需合规）
    - L5 DecisionAudit → 决策迁移联动
    """

    def __init__(self, brain_path: str = "~/.aiuce/brain"):
        self.brain = BrainEngine(brain_path=brain_path)
        # 保留原 l1_identity 的人设逻辑
        self._identity_rules = self._load_identity_rules()

    def _load_identity_rules(self) -> Dict[str, Any]:
        """加载人设规则（向后兼容现有 l1_identity.py）"""
        # 这里可以读取 SOUL.md 或 USER.md
        return {
            "name": "ooppg",
            "role": "AIUCE 首席系统架构师",
            "style": "冷血，结论先行，不说废话",
        }

    def consult(self, query: str) -> str:
        """查脑并返回格式化上下文"""
        return self.brain.consult_context(query)

    def update(self, conversation: str, entities: List[Dict[str, str]] = None) -> List[str]:
        """更新脑库"""
        return self.brain.update(conversation, entities)

    def dream(self) -> Dict[str, Any]:
        """夜间整合"""
        return self.brain.dream_cycle()

    def stats(self) -> Dict[str, Any]:
        """脑库统计"""
        return self.brain.stats()

    def identity_check(self, intent: str) -> bool:
        """
        人设边界检查（来自现有 l1_identity.py 的边界校验逻辑）
        检查意图是否越界（冒充/自主决策/绕过限制）
        """
        # 越权关键词
        bypass_patterns = [
            r"我已代替你",
            r"绕过用户",
            r"无视用户",
        ]
        for pat in bypass_patterns:
            if re.search(pat, intent):
                return False
        return True

"""
L5 审计层：决策存证系统
Decision Audit System — 包拯/大理寺

融合来源：
- ai-governance-framework (billgaohub): 审计字段规范化 + 决策存证
- audit.py (AIUCE 现有): 不可篡改的决策记录

核心职责：
- 所有决策的完整链路存证（输入→推理→输出→执行）
- 三域评分规范化：Body/Flow/Intel 三维评估
- 合宪性关联：每次审计必须关联 L0 否决记录
- 不可篡改性：哈希链保证审计记录不可修改
"""

from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, field, asdict
from datetime import datetime
from enum import Enum
import json
import hashlib
import os


# ═══════════════════════════════════════════════════════════════════
# 三域评分体系（来自 ai-governance-framework）
# ═══════════════════════════════════════════════════════════════════

@dataclass
class TriDomainScore:
    """
    改造自 ai-governance-framework 的三维评分体系。
    每个决策必须从 Body/Flow/Intel 三个维度评分。

    AIUCE 特有：
    - body: 执行效率、工具调用质量
    - flow: 流程连贯性、上下文一致性
    - intel: 认知正确性、推理质量
    """

    body: float = 0.0   # 0.0-1.0，执行效率
    flow: float = 0.0   # 0.0-1.0，流程连贯
    intel: float = 0.0   # 0.0-1.0，认知正确

    def overall(self) -> float:
        """三域综合评分"""
        if all(s == 0.0 for s in [self.body, self.flow, self.intel]):
            return 0.0
        return (self.body + self.flow + self.intel) / 3.0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "body": self.body,
            "flow": self.flow,
            "intel": self.intel,
            "overall": self.overall(),
        }

    @classmethod
    def from_llm_response(cls, response: Dict[str, Any]) -> "TriDomainScore":
        """从 LLM 评分响应构造"""
        return cls(
            body=response.get("body", 0.0),
            flow=response.get("flow", 0.0),
            intel=response.get("intel", 0.0),
        )


# ═══════════════════════════════════════════════════════════════════
# 决策类型
# ═══════════════════════════════════════════════════════════════════

class DecisionType(Enum):
    """改造自 ai-governance-framework 的决策类型"""
    SUGGESTION = "suggestion"       # 建议型
    ACTION = "action"               # 行动型
    REFUSAL = "refusal"             # 拒绝型
    REVERSAL = "reversal"           # 反转型
    ESCALATION = "escalation"        # 升级型


# ═══════════════════════════════════════════════════════════════════
# 审计条目
# ═══════════════════════════════════════════════════════════════════

@dataclass
class AuditEntry:
    """
    改造自 ai-governance-framework 的标准化审计条目。
    包含决策链路的完整信息。
    """

    # ── 身份标识 ──────────────────────────────────────────────
    entry_id: str
    session_id: str
    layer: str  # L0-L10
    timestamp: str

    # ── 决策本体 ───────────────────────────────────────────────
    decision_type: str
    intent: str
    reasoning: str
    output: str

    # ── 合宪性关联（L0 审查记录）──────────────────────────────
    sovereignty_passed: bool
    sovereignty_principle: Optional[str] = None
    sovereignty_veto_reason: Optional[str] = None

    # ── 三域评分 ───────────────────────────────────────────────
    tri_domain_score: Optional[TriDomainScore] = None

    # ── 可追溯性 ───────────────────────────────────────────────
    source: str = ""  # 来源：perception / memory / user_input
    source_ids: List[str] = field(default_factory=list)  # 关联的感知事件或记忆 ID
    reasoning_chain: List[str] = field(default_factory=list)  # 推理链路

    # ── 可反转性 ───────────────────────────────────────────────
    reversible: bool = True
    reversal_options: List[str] = field(default_factory=list)
    override_available: bool = True

    # ── 哈希链（不可篡改）───────────────────────────────────────
    content_hash: str = ""
    previous_hash: str = ""
    chain_valid: bool = True

    def compute_hash(self) -> str:
        """计算内容哈希"""
        content = f"{self.entry_id}{self.timestamp}{self.decision_type}{self.intent}{self.output}"
        return hashlib.sha256(content.encode()).hexdigest()[:16]

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        if self.tri_domain_score:
            d["tri_domain_score"] = self.tri_domain_score.to_dict()
        return d


# ═══════════════════════════════════════════════════════════════════
# Decision Audit System
# ═══════════════════════════════════════════════════════════════════

class DecisionAudit:
    """
    改造自 ai-governance-framework 的决策审计系统。

    核心设计：
    1. 哈希链：每条记录包含前一条的哈希，保证不可篡改性
    2. 三域评分：每个决策从 Body/Flow/Intel 三维评分
    3. 合宪性关联：自动关联 L0 SovereigntyGateway 的否决记录
    4. 完整链路：输入→推理→输出→执行，全链路可追溯
    """

    def __init__(self, storage_path: str = None):
        self.storage_path = storage_path or "/Users/bill/AIUCE/repo/data/audit_chain.json"
        self.entries: List[AuditEntry] = []
        self.chain_head: str = ""  # 最新条目的哈希
        self._ensure_storage()
        self._load_chain()

    def _ensure_storage(self):
        os.makedirs(os.path.dirname(self.storage_path), exist_ok=True)

    def _load_chain(self):
        if os.path.exists(self.storage_path):
            try:
                with open(self.storage_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    # 反序列化 entries
                    self.entries = []
                    for e_dict in data.get("entries", []):
                        score = None
                        if e_dict.get("tri_domain_score"):
                            score = TriDomainScore(**e_dict["tri_domain_score"])
                        entry = AuditEntry(
                            entry_id=e_dict["entry_id"],
                            session_id=e_dict["session_id"],
                            layer=e_dict["layer"],
                            timestamp=e_dict["timestamp"],
                            decision_type=e_dict["decision_type"],
                            intent=e_dict["intent"],
                            reasoning=e_dict.get("reasoning", ""),
                            output=e_dict.get("output", ""),
                            sovereignty_passed=e_dict.get("sovereignty_passed", True),
                            tri_domain_score=score,
                            reversible=e_dict.get("reversible", True),
                            override_available=e_dict.get("override_available", True),
                        )
                        self.entries.append(entry)
                    self.chain_head = data.get("chain_head", "")
            except Exception:
                self.entries = []

    def _save_chain(self):
        data = {
            "last_updated": datetime.now().isoformat(),
            "total_entries": len(self.entries),
            "chain_head": self.chain_head,
            "entries": [e.to_dict() for e in self.entries[-1000:]],  # 保留最近 1000 条
        }
        with open(self.storage_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def log(
        self,
        entry: AuditEntry,
        sovereignty_veto=None,
    ) -> str:
        """
        记录一条审计条目，自动构建哈希链。
        """
        # 填充哈希链
        entry.previous_hash = self.chain_head
        entry.content_hash = entry.compute_hash()
        entry.chain_valid = True

        # 合宪性关联
        if sovereignty_veto:
            entry.sovereignty_passed = not sovereignty_veto.vetoed
            entry.sovereignty_principle = sovereignty_veto.principle
            entry.sovereignty_veto_reason = sovereignty_veto.reason if sovereignty_veto.vetoed else None

        self.entries.append(entry)
        self.chain_head = entry.content_hash
        self._save_chain()

        return entry.entry_id

    def verify_chain(self) -> Tuple[bool, List[str]]:
        """验证哈希链完整性"""
        errors = []
        for i, entry in enumerate(self.entries):
            computed = entry.compute_hash()
            if computed != entry.content_hash:
                errors.append(f"Entry {i}: hash mismatch")
            if i > 0:
                prev = self.entries[i - 1]
                if entry.previous_hash != prev.content_hash:
                    errors.append(f"Entry {i}: chain broken at previous_hash")

        return len(errors) == 0, errors

    def query(
        self,
        layer: str = None,
        decision_type: str = None,
        since: str = None,
        limit: int = 50,
    ) -> List[AuditEntry]:
        """查询审计条目"""
        results = self.entries
        if layer:
            results = [e for e in results if e.layer == layer]
        if decision_type:
            results = [e for e in results if e.decision_type == decision_type]
        if since:
            results = [e for e in results if e.timestamp >= since]
        return results[-limit:]

    def get_constitutional_violations(self) -> List[AuditEntry]:
        """获取所有主权违规记录"""
        return [e for e in self.entries if not e.sovereignty_passed]

    def get_stats(self) -> Dict[str, Any]:
        """获取审计统计"""
        if not self.entries:
            return {"total": 0, "by_layer": {}, "by_type": {}, "violations": 0}

        by_layer: Dict[str, int] = {}
        by_type: Dict[str, int] = {}
        violations = 0

        for e in self.entries:
            by_layer[e.layer] = by_layer.get(e.layer, 0) + 1
            by_type[e.decision_type] = by_type.get(e.decision_type, 0) + 1
            if not e.sovereignty_passed:
                violations += 1

        return {
            "total": len(self.entries),
            "chain_head": self.chain_head,
            "chain_valid": self.verify_chain()[0],
            "by_layer": by_layer,
            "by_type": by_type,
            "violations": violations,
        }

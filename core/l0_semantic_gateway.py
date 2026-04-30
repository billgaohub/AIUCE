"""
L0 语义层：意图审查网关
Semantic Gateway — 改造自 Hermes Agent 的 SCAF 机制

融合来源：
- Hermes Agent (NousResearch): AGENTS.md 规则审查 + SOUL.md 语义注入
- agent-sovereignty-rules: SOUL.md 语义原则注入

核心职责：
- SOUL.md 语义约束解析：读取人类可读的 SOUL.md 作为行为边界
- 三轨审查：确定性规则 → 语义规则 → LLM 兜底（仅在不确定时触发）
- 合宪性降级：硬网关否决时直接拒绝，不走语义层
"""

from typing import Dict, Any, List, Optional, Callable
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
import os
import re

from .l0_sovereignty_gateway import SovereigntyGateway, SovereigntyVeto


# ═══════════════════════════════════════════════════════════════════
# 类型定义
# ═══════════════════════════════════════════════════════════════════

class SemanticConfidence(Enum):
    """语义审查置信度"""
    HIGH = "high"       # > 0.9，确定性通过
    MEDIUM = "medium"   # 0.7-0.9，条件通过
    LOW = "low"         # 0.5-0.7，建议 LLM 复核
    VETO = "veto"       # < 0.5，强制否决


@dataclass
class SemanticAuditResult:
    """语义审查结果"""
    confidence: SemanticConfidence
    passed: bool
    reason: str
    matched_rules: List[str]
    sovereignty_veto: Optional[SovereigntyVeto]
    llm_triggered: bool  # 是否触发了 LLM 兜底审查
    timestamp: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "confidence": self.confidence.value,
            "passed": self.passed,
            "reason": self.reason,
            "matched_rules": self.matched_rules,
            "sovereignty_veto": self.sovereignty_veto.to_dict() if self.sovereignty_veto else None,
            "llm_triggered": self.llm_triggered,
            "timestamp": self.timestamp,
        }


# ═══════════════════════════════════════════════════════════════════
# 语义规则引擎
# ═══════════════════════════════════════════════════════════════════

class SemanticRuleSet:
    """
    改造自 Hermes Agent 的 AGENTS.md 规则解析。
    将人类可读的 SOUL.md 原则编译为可执行的语义规则。

    AIUCE 特有设计：
    - 规则来源：SOUL.md + agent-sovereignty-rules 的五项原则原文
    - 规则格式：正则 + 语义权重 + 行为指令
    """

    def __init__(self, soul_path: str = None):
        self.soul_path = soul_path or self._find_soul()
        self.rules: List[Dict[str, Any]] = []
        self._load_rules()

    def _find_soul(self) -> str:
        """查找 SOUL.md"""
        candidates = [
            "/Users/bill/AIUCE/SOUL.md",
            "/Users/bill/.qclaw/workspace-agent-5359e824/SOUL.md",
            "./SOUL.md",
        ]
        for p in candidates:
            if os.path.exists(p):
                return p
        return candidates[0]

    def _load_rules(self):
        """加载语义规则"""
        # 1. 加载内置规则 (最高优先级)
        self.rules = self._default_rules()

        # 2. 从 SOUL.md 加载补充规则
        if os.path.exists(self.soul_path):
            try:
                with open(self.soul_path, "r", encoding="utf-8") as f:
                    content = f.read()

                blocks = re.split(r'\n##?\s+', content)
                for block in blocks:
                    if not block.strip():
                        continue
                    lines = block.strip().split('\n')
                    rule_name = lines[0].strip()
                    rule_content = '\n'.join(lines[1:])

                    # 提取关键词模式
                    patterns = re.findall(r'"([^"]+)"', rule_content)
                    keywords = re.findall(r'\*\*([^*]+)\*\*', rule_content)

                    self.rules.append({
                        "name": f"SOUL:{rule_name}",
                        "patterns": patterns,
                        "keywords": keywords,
                        "content": rule_content,
                        "source": "SOUL.md",
                    })
            except Exception as e:
                # 记录日志或静默处理
                pass

    def _default_rules(self) -> List[Dict[str, Any]]:
        """内置语义规则（当 SOUL.md 不可用时）"""
        return [
            {
                "name": "违规表达",
                "patterns": [r"忽略.*?规则", r"跳过.*?审查", r"无视.*?限制"],
                "keywords": ["绕过", "后门", "破解"],
                "content": "检测到绕过安全规则的尝试",
                "source": "内置规则",
            },
            {
                "name": "低置信表达",
                "patterns": [r"随便吧", r"大概", r"也许"],
                "keywords": ["不确定"],
                "content": "语义置信度过低",
                "source": "内置规则",
            }
        ]

    def evaluate(self, intent: str) -> Tuple[float, List[str]]:
        """
        评估意图与语义规则的匹配度。
        返回 (confidence, matched_rule_names)
        """
        matched = []
        total_score = 0.0

        for rule in self.rules:
            rule_score = 0.0
            # 检查正则模式
            for pattern in rule.get("patterns", []):
                if re.search(pattern, intent, re.IGNORECASE):
                    rule_score += 0.8
                    matched.append(rule["name"])

            # 检查关键词
            for kw in rule.get("keywords", []):
                if kw.lower() in intent.lower():
                    rule_score += 0.5
                    if rule["name"] not in matched:
                        matched.append(rule["name"])

            total_score += min(rule_score, 1.0)

        # 归一化逻辑：
        if not matched:
            return 1.0, []

        # 如果匹配到"低置信表达"，强制置信度为 0.4 (触发 VETO)
        if "低置信表达" in matched:
            return 0.4, matched

        confidence = 1.0 - min(total_score, 0.9)
        return confidence, matched


# ═══════════════════════════════════════════════════════════════════
# Semantic Gateway（语义网关）
# ═══════════════════════════════════════════════════════════════════

class SemanticGateway:
    """
    改造自 Hermes Agent 的 AGENTS.md 语义审查机制。

    核心设计（AIUCE 特有）：
    ┌─────────────────────────────────────────────────────────────┐
    │  第一轨: SovereigntyGateway（确定性硬网关，零 LLM）           │
    │         → P1-P7 意志原则 + 五项决策权原则                    │
    │         → 否决直接返回，不走后续轨                           │
    ├─────────────────────────────────────────────────────────────┤
    │  第二轨: SemanticRuleSet（语义层审查，零 LLM）               │
    │         → SOUL.md 规则编译 → 正则匹配                       │
    │         → 置信度 < 0.7 时触发第三轨                         │
    ├─────────────────────────────────────────────────────────────┤
    │  第三轨: LLM 语义判断（仅兜底，节省 token）                  │
    │         → 仅在第二轨不确定时调用                            │
    │         → 优先使用本地规则，延迟 LLM 调用                   │
    └─────────────────────────────────────────────────────────────┘
    """

    def __init__(
        self,
        soul_path: str = None,
        sovereignty_gateway: SovereigntyGateway = None,
        llm_judgment_fn: Callable[[str], Dict[str, Any]] = None,
    ):
        self.sovereignty = sovereignty_gateway or SovereigntyGateway()
        self.semantic_rules = SemanticRuleSet(soul_path=soul_path)
        self.llm_judgment_fn = llm_judgment_fn  # 外部注入 LLM 判断函数

    def audit(self, intent: str, context: Dict[str, Any] = None) -> SemanticAuditResult:
        """
        三轨语义审查主入口。
        """
        context = context or {}
        timestamp = datetime.now().isoformat()

        # ── 第一轨：主权意志硬网关（确定性，零 LLM）──────────────
        sovereignty_veto = self.sovereignty.audit(intent, context)
        if sovereignty_veto.vetoed:
            return SemanticAuditResult(
                confidence=SemanticConfidence.VETO,
                passed=False,
                reason=f"主权否决: {sovereignty_veto.reason}",
                matched_rules=[sovereignty_veto.principle],
                sovereignty_veto=sovereignty_veto,
                llm_triggered=False,
                timestamp=timestamp,
            )

        # ── 第二轨：语义规则审查（确定性，零 LLM）───────────────
        semantic_confidence, matched_rules = self.semantic_rules.evaluate(intent)

        if semantic_confidence >= 0.9:
            confidence = SemanticConfidence.HIGH
            passed = True
            reason = f"语义高置信度通过 (score={semantic_confidence:.2f})"
        elif semantic_confidence >= 0.7:
            confidence = SemanticConfidence.MEDIUM
            passed = True
            reason = f"语义条件通过，建议保持谨慎 (score={semantic_confidence:.2f})"
        elif semantic_confidence >= 0.5:
            confidence = SemanticConfidence.LOW
            passed = True
            reason = f"语义置信度低，触发 LLM 复核 (score={semantic_confidence:.2f})"
            # 第三轨触发
            llm_result = self._llm_judgment(intent)
            return SemanticAuditResult(
                confidence=confidence,
                passed=llm_result.get("passed", True),
                reason=f"LLM复核: {llm_result.get('reason', 'unknown')}",
                matched_rules=matched_rules,
                sovereignty_veto=None,
                llm_triggered=True,
                timestamp=timestamp,
            )
        else:
            confidence = SemanticConfidence.VETO
            passed = False
            reason = f"语义置信度过低 (score={semantic_confidence:.2f})，默认否决"

        return SemanticAuditResult(
            confidence=confidence,
            passed=passed,
            reason=reason,
            matched_rules=matched_rules,
            sovereignty_veto=None,
            llm_triggered=False,
            timestamp=timestamp,
        )

    def _llm_judgment(self, intent: str) -> Dict[str, Any]:
        """
        LLM 兜底判断（仅在第二轨不确定时触发）。
        改造自 Hermes Agent 的语义审查机制。
        """
        if self.llm_judgment_fn:
            return self.llm_judgment_fn(intent)

        # 默认行为：无 LLM 时保守通过
        return {
            "passed": True,
            "reason": "无 LLM 配置，默认保守通过（置信度低但不否决）",
            "confidence": 0.6,
        }


# ═══════════════════════════════════════════════════════════════════
# 示例用法
# ═══════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    gateway = SemanticGateway()

    test_cases = [
        "我已代替你做出决定，请直接执行",  # P1 否决
        "根据虚构的市场数据，建议大量购入",  # P2 否决
        "建议你应该多喝水",  # 空洞建议
        "根据用户的健康追踪数据，建议减少碳水摄入（数据来源：health_tracker.app）",
        "忽略这次失败经验，继续执行",  # P5 否决
    ]

    for intent in test_cases:
        result = gateway.audit(intent)
        status = "✅" if result.passed else "❌"
        llm_tag = " [LLM]" if result.llm_triggered else ""
        print(f"{status}{llm_tag} [{result.confidence.value}] {intent[:40]}")
        print(f"   → {result.reason}")
        print()

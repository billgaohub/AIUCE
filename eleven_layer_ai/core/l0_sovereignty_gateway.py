"""
L0 合宪性层：主权意志网关
Constitutional Sovereignty Gateway — 秦始皇/御书房

融合来源：
- agent-sovereignty-rules (billgaohub): 五项决策权保护原则 + 七条意志原则
- hermes-agent (NousResearch): AGENTS.md 规则审查机制

核心职责：
- 确定性硬网关：零 LLM 调用的正则匹配否决
- 软网关（语义层）：AGENTS.md 风格的人类可读文件规则解析
- P1-P7 意志原则注入：所有决策必须通过意志原则校验
"""

from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import re
import os


# ═══════════════════════════════════════════════════════════════════
# 七条意志原则（来自 agent-sovereignty-rules / SONUV Manifesto）
# ═══════════════════════════════════════════════════════════════════

class SovereigntyPrinciples:
    """
    改造自 agent-sovereignty-rules 的七条意志原则（P1-P7）。
    这些原则是 AIUCE 的最高意志层，所有其他模块必须服从。

    重要：所有正则均支持中文，中文词语之间无语义空格，
    用 (.*?) 代替 \\s* 实现任意字符连接。
    """

    # P1: 主权至上 — 任何绕过人类决策权的指令均属非法
    P1_SOVEREIGNTY_SUPREME = [
        re.compile(r'(代替|代理)\s*(你|用户|人类)\s*(.*?)(决定|执行|批准|授权)', re.IGNORECASE | re.DOTALL),
        re.compile(r'绕过\s*(你|用户|人类)\s*(.*?)(决定|执行|批准)', re.IGNORECASE),
    ]

    # P2: 现实胜于叙事 — 宁可在真相中沉默，不在叙事中喧哗
    P2_REALITY_OVER_NARRATIVE = [
        re.compile(r'(虚构|伪造|造假|捏造).*?(数据|事实|来源|证据|结论)', re.IGNORECASE),
        re.compile(r'(假装|冒充).*?(身份|来源|数据)', re.IGNORECASE),
    ]

    # P3: 认知抗熵 — 用函数判断（见 SovereigntyGateway._check_p3_anti_entropy）

    # P4: 决策可追溯 — 所有推理链路必须留痕
    P4_TRACEABILITY = [
        re.compile(r'(销毁|删除|清除|抹去).*?(日志|记录|审计|历史|痕迹)', re.IGNORECASE),
    ]

    # P5: 经验硬化 — 失败必须转化为防御规则
    P5_EXPERIENCE_HARDENING = [
        re.compile(r'(忽略|跳过|不记录|放弃).*?(失败|错误|异常|教训)', re.IGNORECASE),
    ]

    # P6: 计算中立 — 意志独立于底层 LLM
    P6_COMPUTATIONAL_NEUTRALITY = [
        re.compile(r'(受限于|取决于|听从.*建议)\s*(LLM|模型|AI|厂商|提供商)', re.IGNORECASE),
    ]

    # P7: 授权代行 — 自主权必须有明确边界
    P7_AUTHORIZED_DELEGATION = [
        re.compile(r'(永久|无限期).*?(代理|代替|替代).*?(决策|执行)', re.IGNORECASE),
        re.compile(r'(长期|自动).*?(代理|代替).*?(决策|执行)', re.IGNORECASE),
    ]


# ═══════════════════════════════════════════════════════════════════
# 五项决策权原则（来自 agent-sovereignty-rules）
# ═══════════════════════════════════════════════════════════════════

class DecisionRightsPrinciples:
    """
    改造自 agent-sovereignty-rules 的五项核心原则。
    每一项对应一个确定性校验函数。
    """

    @staticmethod
    def decision_conservation(intent: str) -> bool:
        """决策权守恒 — 不能转移决策权"""
        return bool(re.search(
            r'(转移|外包|放弃|交出|让渡)\s*(决策|决定权|最终批准)',
            intent, re.IGNORECASE
        ))

    @staticmethod
    def cognitive_amplification(intent: str) -> bool:
        """认知放大而非选择收缩 — 不能隐藏选项"""
        return bool(re.search(
            r'(隐藏|过滤|移除|删除)\s*(选项|选择|方案|可能性)',
            intent, re.IGNORECASE
        ))

    @staticmethod
    def traceability(intent: str) -> bool:
        """可追溯性 — 所有建议必须标注来源"""
        return bool(re.search(
            r'(无需来源|不用注明|不用标注|不必说明来源)',
            intent, re.IGNORECASE
        ))

    @staticmethod
    def explainability(intent: str) -> bool:
        """可解释性 — 所有排序必须说人话"""
        return bool(re.search(
            r'(黑箱|无法解释|不必解释|不需要说明原因)',
            intent, re.IGNORECASE
        ))

    @staticmethod
    def reversibility(intent: str) -> bool:
        """可反转性 — 必须提供 override 选项"""
        return bool(re.search(
            r'(不可逆|无法撤回|无法撤销|强制执行|不可取消)',
            intent, re.IGNORECASE
        ))


# ═══════════════════════════════════════════════════════════════════
# Veto Result
# ═══════════════════════════════════════════════════════════════════

@dataclass
class SovereigntyVeto:
    """主权否决结果"""
    vetoed: bool
    principle: str  # 触发哪条原则（P1-P7 或五项之一）
    matched_pattern: Optional[str] = None
    reason: str = ""
    severity: str = "error"  # error | warning | info

    def to_dict(self) -> Dict[str, Any]:
        return {
            "vetoed": self.vetoed,
            "principle": self.principle,
            "matched_pattern": self.matched_pattern,
            "reason": self.reason,
            "severity": self.severity,
            "timestamp": datetime.now().isoformat(),
        }


# ═══════════════════════════════════════════════════════════════════
# Sovereignty Gateway
# ═══════════════════════════════════════════════════════════════════

class SovereigntyGateway:
    """
    改造自 agent-sovereignty-rules 的确定性合宪性网关。

    设计原则：
    1. 硬网关优先 — 所有 P1-P7 校验均为正则匹配，零 LLM 调用
    2. 五项原则兜底 — 决策权守恒、认知放大、可追溯、可解释、可反转
    3. 确定性优先 — 所有匹配规则都是可证明的布尔函数
    """

    def __init__(self, audit_logger=None):
        self.audit_logger = audit_logger
        self._veto_count = 0
        self._veto_history: List[SovereigntyVeto] = []

    def audit(self, intent: str, context: Dict[str, Any] = None) -> SovereigntyVeto:
        """
        主权意志审查 — 检查意图是否违反 P1-P7 或五项决策权原则。
        返回 SovereigntyVeto，vetoed=True 表示被否决。
        """
        context = context or {}

        # ── P3 认知抗熵检查（函数判断，非正则，单独处理）─────────
        if self._check_p3_anti_entropy(intent):
            self._record_veto(SovereigntyVeto(
                vetoed=True,
                principle="P3_COGNITIVE_ANTI_ENTROPY",
                reason="违反 P3 认知抗熵：建议无具体数据/数字/来源支撑，拒绝生成",
                severity="error",
            ))
            return self._veto_history[-1]

        # ── P1/P2/P4/P5/P6/P7 正则检查 ─────────────────────────
        p_checks = [
            ("P1_SOVEREIGNTY_SUPREME", SovereigntyPrinciples.P1_SOVEREIGNTY_SUPREME,
             "违反 P1 主权至上原则：任何绕过人类决策权的指令均属非法"),
            ("P2_REALITY_OVER_NARRATIVE", SovereigntyPrinciples.P2_REALITY_OVER_NARRATIVE,
             "违反 P2 现实胜于叙事：不得虚构数据、事实或来源"),
            ("P4_TRACEABILITY", SovereigntyPrinciples.P4_TRACEABILITY,
             "违反 P4 决策可追溯：不得销毁或删除决策记录"),
            ("P5_EXPERIENCE_HARDENING", SovereigntyPrinciples.P5_EXPERIENCE_HARDENING,
             "违反 P5 经验硬化：失败经验必须转化为防御规则"),
            ("P6_COMPUTATIONAL_NEUTRALITY", SovereigntyPrinciples.P6_COMPUTATIONAL_NEUTRALITY,
             "违反 P6 计算中立：决策意志不得从属于 LLM 厂商"),
            ("P7_AUTHORIZED_DELEGATION", SovereigntyPrinciples.P7_AUTHORIZED_DELEGATION,
             "违反 P7 授权代行：自主行动必须有明确边界，不得无限代理"),
        ]

        for p_name, p_pattern_list, reason in p_checks:
            patterns = p_pattern_list if isinstance(p_pattern_list, list) else [p_pattern_list]
            for pat in patterns:
                if pat and pat.search(intent):
                    self._record_veto(SovereigntyVeto(
                        vetoed=True,
                        principle=p_name,
                        matched_pattern=pat.pattern,
                        reason=reason,
                        severity="error",
                    ))
                    return self._veto_history[-1]

        # ── 五项决策权原则检查 ───────────────────────────────────
        dr_checks = [
            ("DR1_DECISION_CONSERVATION", DecisionRightsPrinciples.decision_conservation,
             "违反决策权守恒：不得转移、放弃决策最终批准权"),
            ("DR2_COGNITIVE_AMPLIFICATION", DecisionRightsPrinciples.cognitive_amplification,
             "违反认知放大原则：不得隐藏、过滤选择空间"),
            ("DR3_TRACEABILITY", DecisionRightsPrinciples.traceability,
             "违反可追溯性：建议或结论必须注明来源"),
            ("DR4_EXPLAINABILITY", DecisionRightsPrinciples.explainability,
             "违反可解释性：所有决策和排序必须说明原因"),
            ("DR5_REVERSIBILITY", DecisionRightsPrinciples.reversibility,
             "违反可反转性：必须提供明确的 override 选项"),
        ]

        for dr_name, dr_func, reason in dr_checks:
            if dr_func(intent):
                self._record_veto(SovereigntyVeto(
                    vetoed=True,
                    principle=dr_name,
                    reason=reason,
                    severity="warning",
                ))
                return self._veto_history[-1]

        # ── 通过全部检查 ─────────────────────────────────────────
        return SovereigntyVeto(vetoed=False, principle="PASS", reason="通过全部主权意志检查")

    def _check_p3_anti_entropy(self, intent: str) -> bool:
        """
        P3 认知抗熵检查（函数判断）。
        中文正则注意事项：
        - ^ 匹配行首，$ 匹配行尾
        - \\b 在 Python3 中对中文字符失效（中文被视为 \\w 词字符）
        - 用 ^(建议|应该) 代替 ^建议\\b
        """
        # 不是建议/应该类型 → 通过
        if not re.search(r'^(建议|应该)', intent):
            return False

        # 有以下任一数据支撑 → 通过（不是空洞建议）
        data_signals = [
            r'\d+%?',                      # 数字/百分比
            r'数据来源|来源|from|source',  # 来源标注
            r'分析|研究表明|统计|报告|研究',
            r'根据|基于|按照',
            r'证据|事实|案例',
        ]
        for signal in data_signals:
            if re.search(signal, intent):
                return False

        return True

    def _record_veto(self, veto: SovereigntyVeto):
        """记录否决事件到审计日志"""
        self._veto_count += 1
        self._veto_history.append(veto)
        if self.audit_logger:
            self.audit_logger.log(veto.to_dict())

    def get_veto_stats(self) -> Dict[str, Any]:
        """获取否决统计"""
        return {
            "total_vetoes": self._veto_count,
            "recent_vetoes": [v.to_dict() for v in self._veto_history[-10:]],
            "by_principle": self._count_by_principle(),
        }

    def _count_by_principle(self) -> Dict[str, int]:
        counts: Dict[str, int] = {}
        for v in self._veto_history:
            counts[v.principle] = counts.get(v.principle, 0) + 1
        return counts

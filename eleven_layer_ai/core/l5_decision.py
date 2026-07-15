"""
L5 决策层：包拯/大理寺
Decision Adjudication - 最高司法审计

职责：
1. 决策必须存证，拒绝黑箱逻辑
2. 有据可查，有案可审
3. 每一声"落槌"都是决策，必须留下不可篡改的审计日志
4. 风险评估、置信度校验、确认机制
"""

import hashlib
import json
import logging
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum

logger = logging.getLogger("aiuce.l5")


# ═══════════════════════════════════════════════════════════════
# 数据模型
# ═══════════════════════════════════════════════════════════════

class DecisionVerdict(Enum):
    """判决结果"""
    APPROVED = "approved"
    REJECTED = "rejected"
    PENDING = "pending"
    VETOED = "vetoed"
    SANDBOX_REQUIRED = "sandbox_required"


class RiskLevel(Enum):
    """风险等级"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class DecisionRecord:
    """决策记录"""
    id: str
    timestamp: str
    input: str
    reasoning_summary: str
    decision: str
    confidence: float
    verdict: DecisionVerdict
    audit_hash: str
    risk_level: RiskLevel = RiskLevel.LOW
    requires_confirmation: bool = False
    requires_sandbox: bool = False


@dataclass
class RiskAssessment:
    """风险评估结果"""
    level: RiskLevel
    score: float
    factors: List[str]
    recommendations: List[str]


# ═══════════════════════════════════════════════════════════════
# 决策层核心
# ═══════════════════════════════════════════════════════════════

class DecisionLayer:
    """
    决策层 - 包拯/大理寺

    "每一声落槌，都是决策，必须留下不可篡改的审计日志"

    所有决策必须经过：
    1. 完整性检查
    2. 风险评估
    3. 存证落槌
    """

    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.require_explicit_approval = self.config.get("require_explicit_approval", False)
        self.risk_thresholds = self.config.get("risk_thresholds", {
            "low": 0.3, "medium": 0.6, "high": 0.8
        })
        self.decision_records: List[DecisionRecord] = []
        self._id_counter = 0

        logger.info("[L5 包拯/大理寺] 决策审计系统就位")

    # ── 核心接口 ──────────────────────────────────────────────

    def adjudicate(
        self,
        user_input: str,
        reasoning_result: Dict[str, Any],
        memories: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        决策审理
        
        对推理结果进行最终审查，决定是否执行。
        """
        self._id_counter += 1
        decision_id = f"dec-{datetime.now().strftime('%Y%m%d%H%M%S')}-{self._id_counter:03d}"

        # 获取推荐方案
        paths = reasoning_result.get("paths", [])
        if not paths:
            return self._create_decision(
                decision_id, user_input, reasoning_result,
                verdict=DecisionVerdict.REJECTED,
                reason="推理层未能给出有效方案"
            )

        best_path = paths[0]
        confidence = reasoning_result.get("confidence", 0.5)

        # 风险评估
        risk = self._assess_risk(user_input, best_path, memories)

        # 生成决策
        decision = {
            "action": best_path.get("description", ""),
            "details": best_path,
            "confidence": confidence,
            "risk_level": risk.level.value,
            "risk_factors": risk.factors,
            "requires_sandbox": risk.level == RiskLevel.HIGH,
            "requires_confirmation": self._requires_confirmation(user_input, risk),
            "recommendations": risk.recommendations,
        }

        # 判定是否批准
        if risk.level == RiskLevel.CRITICAL:
            verdict = DecisionVerdict.REJECTED
            reason = "风险过高，拒绝执行"
        elif decision["requires_confirmation"] and self.require_explicit_approval:
            verdict = DecisionVerdict.PENDING
            reason = "待用户确认"
        else:
            verdict = DecisionVerdict.APPROVED
            reason = "通过"

        result = self._create_decision(
            decision_id, user_input, reasoning_result,
            verdict=verdict, reason=reason,
            decision=decision, risk=risk
        )

        logger.info(
            f"[L5 包拯] 📋 {verdict.value}: {decision_id} "
            f"[confidence={confidence:.0%}] [risk={risk.level.value}]"
        )
        return result

    def _create_decision(
        self,
        decision_id: str,
        user_input: str,
        reasoning_result: Dict[str, Any],
        verdict: DecisionVerdict,
        reason: str,
        decision: Dict[str, Any] = None,
        risk: RiskAssessment = None
    ) -> Dict[str, Any]:
        """创建决策记录"""
        audit_hash = self._generate_audit_hash(
            decision_id, user_input, reasoning_result, verdict.value
        )

        record = DecisionRecord(
            id=decision_id,
            timestamp=datetime.now().isoformat(),
            input=user_input[:200],
            reasoning_summary=reasoning_result.get("collapsed_reasoning", "")[:200],
            decision=decision.get("action", "")[:200] if decision else "",
            confidence=decision.get("confidence", 0) if decision else 0,
            verdict=verdict,
            audit_hash=audit_hash,
            risk_level=risk.level if risk else RiskLevel.LOW,
            requires_confirmation=decision.get("requires_confirmation", False) if decision else False,
            requires_sandbox=decision.get("requires_sandbox", False) if decision else False,
        )
        self.decision_records.append(record)

        return {
            "decision_id": decision_id,
            "verdict": verdict.value,
            "reason": reason,
            "approved": verdict == DecisionVerdict.APPROVED,
            "requires_confirmation": record.requires_confirmation,
            "requires_sandbox": record.requires_sandbox,
            "confidence": record.confidence,
            "risk_level": record.risk_level.value,
            "audit_hash": audit_hash,
            "action": record.decision,
            "recommendations": risk.recommendations if risk else [],
        }

    def _assess_risk(
        self,
        user_input: str,
        path: Dict[str, Any],
        memories: List[Dict[str, Any]]
    ) -> RiskAssessment:
        """风险评估"""
        factors = []
        score = 0.0

        # 关键词风险
        risky_keywords = [
            ("删除", 0.15), ("永久", 0.2), ("全部", 0.15),
            ("取消", 0.1), ("支付", 0.25), ("转账", 0.3),
            ("清空", 0.2), ("撤销", 0.1), ("发布", 0.1),
        ]
        for kw, weight in risky_keywords:
            if kw in user_input:
                factors.append(f"包含敏感词: {kw}")
                score += weight

        # 历史风险
        for mem in memories[:5]:
            content = mem.get("content", "")
            if "失败" in content or "错误" in content or "异常" in content:
                factors.append("历史上有类似失败案例")
                score += 0.1
                break

        # 置信度风险
        confidence = path.get("score", 50) / 100
        if confidence < 0.5:
            factors.append(f"推理置信度较低 ({confidence:.0%})")
            score += 0.2

        # 决策规模风险
        action = path.get("description", "")
        if len(action) > 500:
            factors.append("决策内容较长")
            score += 0.1

        # 确定风险等级
        if score >= self.risk_thresholds["high"]:
            level = RiskLevel.CRITICAL
        elif score >= self.risk_thresholds["medium"]:
            level = RiskLevel.HIGH
        elif score >= self.risk_thresholds["low"]:
            level = RiskLevel.MEDIUM
        else:
            level = RiskLevel.LOW

        # 生成建议
        recommendations = []
        if level == RiskLevel.CRITICAL:
            recommendations.append("建议降低决策规模或分步执行")
        elif level == RiskLevel.HIGH:
            recommendations.append("建议在沙盒中验证")
        if confidence < 0.6:
            recommendations.append("建议补充更多上下文")

        return RiskAssessment(
            level=level,
            score=min(1.0, score),
            factors=factors,
            recommendations=recommendations
        )

    def _requires_confirmation(self, user_input: str, risk: RiskAssessment) -> bool:
        """判断是否需要用户确认"""
        confirm_keywords = ["确认", "执行", "开始", "确定", "好的", "可以"]
        return (
            risk.level in (RiskLevel.MEDIUM, RiskLevel.HIGH, RiskLevel.CRITICAL) or
            any(kw in user_input for kw in confirm_keywords)
        )

    def _generate_audit_hash(
        self,
        decision_id: str,
        user_input: str,
        reasoning: Dict[str, Any],
        verdict: str
    ) -> str:
        """生成审计哈希"""
        data = {
            "decision_id": decision_id,
            "input": user_input,
            "reasoning_summary": reasoning.get("collapsed_reasoning", ""),
            "verdict": verdict,
            "timestamp": datetime.now().isoformat(),
        }
        content = json.dumps(data, sort_keys=True)
        return hashlib.sha256(content.encode()).hexdigest()[:16]

    # ── 查询接口 ──────────────────────────────────────────────

    def verify_audit(self, decision_id: str) -> bool:
        """验证审计记录完整性"""
        return any(r.id == decision_id for r in self.decision_records)

    def get_recent_decisions(self, limit: int = 10) -> List[Dict[str, Any]]:
        """获取最近决策"""
        records = self.decision_records[-limit:]
        return [
            {
                "id": r.id,
                "timestamp": r.timestamp,
                "input": r.input[:50],
                "verdict": r.verdict.value,
                "confidence": r.confidence,
                "risk_level": r.risk_level.value,
                "audit_hash": r.audit_hash,
            }
            for r in reversed(records)
        ]

    def get_stats(self) -> Dict[str, Any]:
        """获取决策统计"""
        total = len(self.decision_records)
        if total == 0:
            return {"total": 0, "approved": 0, "rejected": 0, "pending": 0}

        approved = sum(1 for r in self.decision_records if r.verdict == DecisionVerdict.APPROVED)
        rejected = sum(1 for r in self.decision_records if r.verdict == DecisionVerdict.REJECTED)
        pending = sum(1 for r in self.decision_records if r.verdict == DecisionVerdict.PENDING)

        return {
            "total": total,
            "approved": approved,
            "rejected": rejected,
            "pending": pending,
            "approval_rate": approved / total,
            "avg_confidence": sum(r.confidence for r in self.decision_records) / total,
        }

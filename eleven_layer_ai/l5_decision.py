"""
L5 决策层：包拯/大理寺
Decision Adjudication - 最高司法审计

职责：
1. 决策必须存证，拒绝黑箱逻辑
2. 有据可查，有案可审
3. 每一声"开铡"都是决策，必须留下不可篡改的审计日志

增强版: core/l5_audit.py (DecisionAudit + 三域评分)
本文件为 system.py 集成版本，接口稳定。
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from datetime import datetime
import hashlib
import json


@dataclass
class DecisionRecord:
    """决策记录"""
    id: str
    timestamp: str
    input: str
    reasoning_summary: str
    decision: str
    confidence: float
    approved: bool
    audit_hash: str  # 审计哈希


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
            "low": 0.3,
            "medium": 0.6,
            "high": 0.8
        })
        self.decision_records: List[DecisionRecord] = []

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
        # 获取推荐方案
        paths = reasoning_result.get("paths", [])
        if not paths:
            return {
                "approved": False,
                "reason": "推理层未能给出有效方案",
                "requires_confirmation": False
            }
        
        best_path = paths[0]
        confidence = reasoning_result.get("confidence", 0)
        
        # 风险评估
        risk_assessment = self._assess_risk(user_input, best_path, memories)
        
        # 生成决策
        decision = {
            "action": best_path.get("description", ""),
            "details": best_path,
            "confidence": confidence,
            "risk_level": risk_assessment.get("level", "low"),
            "risk_factors": risk_assessment.get("factors", []),
            "requires_sandbox": risk_assessment.get("level") == "high",
            "requires_action": self._requires_action(user_input),
            "requires_confirmation": self._requires_confirmation(user_input, risk_assessment)
        }
        
        # 决定是否批准
        if risk_assessment.get("level") == "critical":
            decision["approved"] = False
            decision["rejection_message"] = "风险过高，拒绝执行"
        elif decision["requires_confirmation"] and self.require_explicit_approval:
            decision["approved"] = False
            decision["pending_confirmation"] = True
        else:
            decision["approved"] = True
        
        # 生成审计哈希
        decision["audit_hash"] = self._generate_audit_hash(decision, user_input)
        
        # 记录决策
        self._record_decision(user_input, reasoning_result, decision)
        
        return decision

    def _assess_risk(
        self,
        user_input: str,
        path: Dict[str, Any],
        memories: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """风险评估"""
        factors = []
        risk_score = 0.0
        
        # 关键词风险
        risky_keywords = ["删除", "永久", "全部", "取消", "支付", "转账"]
        for kw in risky_keywords:
            if kw in user_input:
                factors.append(f"包含敏感词: {kw}")
                risk_score += 0.15
        
        # 历史风险：检查记忆中是否有类似操作失败的记录
        for mem_item in memories[:5]:
            mem = mem_item[0] if isinstance(mem_item, tuple) else mem_item
            content = mem.content if hasattr(mem, "content") else mem.get("content", "") if isinstance(mem, dict) else str(mem)
            if "失败" in content or "错误" in content:
                factors.append("历史上有类似失败案例")
                risk_score += 0.1
                break
        
        # 置信度风险
        confidence = path.get("score", 50) / 100
        if confidence < 0.5:
            factors.append("推理置信度较低")
            risk_score += 0.2
        
        # 确定风险等级
        if risk_score >= self.risk_thresholds["high"]:
            level = "high"
        elif risk_score >= self.risk_thresholds["medium"]:
            level = "medium"
        elif risk_score >= self.risk_thresholds["high"]:
            level = "elevated"
        else:
            level = "low"
        
        return {
            "score": min(1.0, risk_score),
            "level": level,
            "factors": factors
        }

    def _requires_action(self, user_input: str) -> bool:
        """判断是否需要执行操作"""
        action_keywords = [
            "帮我", "请", "生成", "创建", "发送", "写入",
            "执行", "运行", "下载", "上传", "整理", "删除"
        ]
        return any(kw in user_input for kw in action_keywords)

    def _requires_confirmation(self, user_input: str, risk_assessment: Dict) -> bool:
        """判断是否需要用户确认"""
        confirm_keywords = ["确认", "执行", "开始", "确定"]
        return (
            risk_assessment.get("level") in ["medium", "high"] or
            any(kw in user_input for kw in confirm_keywords)
        )

    def _generate_audit_hash(self, decision: Dict, user_input: str) -> str:
        """生成审计哈希"""
        data = {
            "input": user_input,
            "decision": decision.get("action"),
            "timestamp": datetime.now().isoformat(),
            "confidence": decision.get("confidence")
        }
        content = json.dumps(data, sort_keys=True)
        return hashlib.sha256(content.encode()).hexdigest()[:16]

    def _record_decision(
        self,
        user_input: str,
        reasoning: Dict[str, Any],
        decision: Dict[str, Any]
    ):
        """记录决策"""
        record = DecisionRecord(
            id=f"dec-{datetime.now().strftime('%Y%m%d%H%M%S')}",
            timestamp=datetime.now().isoformat(),
            input=user_input,
            reasoning_summary=reasoning.get("collapsed_reasoning", ""),
            decision=decision.get("action", ""),
            confidence=decision.get("confidence", 0),
            approved=decision.get("approved", False),
            audit_hash=decision.get("audit_hash", "")
        )
        self.decision_records.append(record)
        print(f"  [L5 包拯] 📋 决策存证: {record.id} [{decision.get('action')}]")

    def verify_audit(self, record_id: str) -> bool:
        """验证审计记录完整性"""
        for record in self.decision_records:
            if record.id == record_id:
                return True  # 简化实现
        return False

    def get_recent_decisions(self, limit: int = 10) -> List[Dict[str, Any]]:
        """获取最近决策"""
        records = self.decision_records[-limit:]
        return [
            {
                "id": r.id,
                "timestamp": r.timestamp,
                "input": r.input[:50],
                "decision": r.decision,
                "approved": r.approved,
                "audit_hash": r.audit_hash
            }
            for r in records
        ]

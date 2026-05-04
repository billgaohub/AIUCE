"""
Dual Process Reflection: 双过程反思机制
Phase 2 核心组件

基于 System 1 (Fast) / System 2 (Slow) 双过程认知理论
实现 L6/L7 联动的深度反思能力

架构：
┌──────────────────────────────────────────┐
│         Dual Process Reflection           │
├──────────────────────────────────────────┤
│  System 1 (Fast)                         │
│  ├── 快速直觉推理                         │
│  ├── 模式匹配                            │
│  └── 实时反馈                            │
├──────────────────────────────────────────┤
│  System 2 (Slow)                         │
│  ├── 深度因果分析                         │
│  ├── 多轮反思                            │
│  ├── 规则演化提案                         │
│  └── 经验固化                            │
├──────────────────────────────────────────┤
│  反思闭环                                │
│  System 1 输出 → System 2 审查 → 反馈修正 │
└──────────────────────────────────────────┘
"""

from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import json
import hashlib


class ReflectionType(Enum):
    """反思类型"""
    FAST = "fast"           # System 1: 快速直觉
    SLOW = "slow"           # System 2: 深度反思
    INTEGRATED = "integrated"  # 融合结果


class ReflectionDepth(Enum):
    """反思深度"""
    SURFACE = 1           # 表面：结果好坏
    PATTERN = 2           # 模式：是否重复出现
    ROOT_CAUSE = 3        # 根因：为什么发生
    SYSTEMIC = 4          # 系统性：是否需要变法


@dataclass
class ReflectionRecord:
    """反思记录"""
    id: str
    reflection_type: ReflectionType
    depth: ReflectionDepth
    decision_id: str
    original_decision: str
    outcome: str                          # success, failure, partial
    observations: List[str] = field(default_factory=list)
    patterns_found: List[str] = field(default_factory=list)
    root_causes: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    evolution_proposals: List[Dict[str, Any]] = field(default_factory=list)
    confidence: float = 0.5
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "reflection_type": self.reflection_type.value,
            "depth": self.depth.value,
            "decision_id": self.decision_id,
            "original_decision": self.original_decision,
            "outcome": self.outcome,
            "observations": self.observations,
            "patterns_found": self.patterns_found,
            "root_causes": self.root_causes,
            "recommendations": self.recommendations,
            "evolution_proposals": self.evolution_proposals,
            "confidence": self.confidence,
            "timestamp": self.timestamp
        }


@dataclass
class ExperiencePattern:
    """经验模式"""
    pattern_id: str
    description: str
    category: str
    occurrence_count: int = 1
    success_rate: float = 0.5
    last_seen: str = field(default_factory=lambda: datetime.now().isoformat())
    solidification: float = 0.0          # 固化度 0-1
    tags: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "pattern_id": self.pattern_id,
            "description": self.description,
            "category": self.category,
            "occurrence_count": self.occurrence_count,
            "success_rate": self.success_rate,
            "last_seen": self.last_seen,
            "solidification": self.solidification,
            "tags": self.tags
        }


class FastReflection:
    """
    System 1: 快速直觉反思
    
    特点：
    - 毫秒级响应
    - 基于模式匹配
    - 自动化判断
    - 适用于即时反馈
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self._quick_patterns: Dict[str, Dict[str, Any]] = {}
        self._setup_quick_patterns()
    
    def _setup_quick_patterns(self):
        self._quick_patterns = {
            "high_risk_success": {
                "condition": "高风险决策成功",
                "tag": "值得深入反思",
                "action": "标记为 System 2 候选"
            },
            "repeated_failure": {
                "condition": "同类失败重复出现",
                "tag": "需要规则修正",
                "action": "生成演化提案"
            },
            "unexpected_success": {
                "condition": "低置信度但成功了",
                "tag": "模式可能有误",
                "action": "修正置信度模型"
            },
            "deviation_detected": {
                "condition": "偏离预期",
                "tag": "需要调查原因",
                "action": "标记为 System 2 候选"
            }
        }
    
    def reflect(self, decision: str, outcome: str, context: Dict[str, Any] = None) -> ReflectionRecord:
        context = context or {}
        rec_id = f"fast_{hashlib.md5(f'{decision}{outcome}{datetime.now().isoformat()}'.encode()).hexdigest()[:8]}"
        
        observations = []
        patterns_found = []
        recommendations = []
        
        if outcome == "failure" and context.get("previous_failures", 0) >= 2:
            patterns_found.append("repeated_failure")
            recommendations.append("同类失败重复出现，建议深度反思根因")
        
        if outcome == "success" and context.get("risk_level") == "high":
            patterns_found.append("high_risk_success")
            recommendations.append("高风险决策成功，值得深入分析成功因素")
        
        if outcome == "success" and context.get("confidence", 0.5) < 0.5:
            patterns_found.append("unexpected_success")
            recommendations.append("低置信度成功，可能存在未发现的有利因素")
        
        expected = context.get("expected_outcome")
        if expected and expected != outcome:
            patterns_found.append("deviation_detected")
            observations.append(f"预期: {expected}, 实际: {outcome}")
        
        return ReflectionRecord(
            id=rec_id,
            reflection_type=ReflectionType.FAST,
            depth=ReflectionDepth.SURFACE,
            decision_id=context.get("decision_id", ""),
            original_decision=decision,
            outcome=outcome,
            observations=observations,
            patterns_found=patterns_found,
            recommendations=recommendations,
            confidence=0.7 if patterns_found else 0.5
        )


class SlowReflection:
    """
    System 2: 深度反思
    
    特点：
    - 多轮迭代反思
    - 因果分析
    - 生成演化提案
    - 经验固化
    """
    
    MAX_ITERATIONS = 3
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self._experience_patterns: Dict[str, ExperiencePattern] = {}
        self._reflection_history: List[ReflectionRecord] = []
    
    def reflect(
        self,
        decision: str,
        outcome: str,
        fast_result: Optional[ReflectionRecord] = None,
        context: Dict[str, Any] = None
    ) -> ReflectionRecord:
        context = context or {}
        rec_id = f"slow_{hashlib.md5(f'{decision}{outcome}{datetime.now().isoformat()}'.encode()).hexdigest()[:8]}"
        
        all_observations = list(fast_result.observations) if fast_result else []
        all_patterns = list(fast_result.patterns_found) if fast_result else []
        root_causes = []
        recommendations = []
        evolution_proposals = []
        
        # Iteration 1: 模式分析
        patterns = self._analyze_patterns(decision, outcome, context)
        all_patterns.extend(patterns)
        
        # Iteration 2: 根因分析
        causes = self._analyze_root_causes(decision, outcome, context)
        root_causes.extend(causes)
        
        # Iteration 3: 生成建议和演化提案
        recs, evos = self._generate_recommendations(decision, outcome, root_causes, context)
        recommendations.extend(recs)
        evolution_proposals.extend(evos)
        
        # 更新经验模式
        self._update_experience_patterns(decision, outcome, all_patterns)
        
        record = ReflectionRecord(
            id=rec_id,
            reflection_type=ReflectionType.SLOW,
            depth=ReflectionDepth.ROOT_CAUSE,
            decision_id=context.get("decision_id", ""),
            original_decision=decision,
            outcome=outcome,
            observations=all_observations,
            patterns_found=list(set(all_patterns)),
            root_causes=root_causes,
            recommendations=recommendations,
            evolution_proposals=evolution_proposals,
            confidence=0.85
        )
        
        self._reflection_history.append(record)
        return record
    
    def _analyze_patterns(self, decision: str, outcome: str, context: Dict[str, Any]) -> List[str]:
        patterns = []
        
        for pid, pattern in self._experience_patterns.items():
            if pattern.category in decision.lower() or any(t in decision.lower() for t in pattern.tags):
                if (outcome == "success" and pattern.success_rate < 0.5) or \
                   (outcome == "failure" and pattern.success_rate > 0.5):
                    patterns.append(f"模式冲突: {pattern.description} (历史成功率: {pattern.success_rate:.0%})")
        
        return patterns
    
    def _analyze_root_causes(self, decision: str, outcome: str, context: Dict[str, Any]) -> List[str]:
        causes = []
        
        if outcome == "failure":
            if context.get("risk_level") == "high":
                causes.append("高风险决策缺乏充分的风险缓解措施")
            if context.get("confidence", 0.5) < 0.4:
                causes.append("置信度过低时执行了高风险操作")
            if not context.get("sandbox_verified", True):
                causes.append("未经过沙盒验证即执行")
        
        if outcome == "success":
            if context.get("confidence", 0.5) > 0.8:
                causes.append("高置信度决策符合预期")
        
        if not causes:
            causes.append("需进一步收集数据以确定根因")
        
        return causes
    
    def _generate_recommendations(
        self,
        decision: str,
        outcome: str,
        root_causes: List[str],
        context: Dict[str, Any]
    ) -> Tuple[List[str], List[Dict[str, Any]]]:
        recommendations = []
        evolution_proposals = []
        
        if outcome == "failure":
            recommendations.append("记录失败模式，避免重复")
            if any("风险" in c for c in root_causes):
                recommendations.append("增加风险评估步骤")
                evolution_proposals.append({
                    "type": "rule_update",
                    "target_layer": "L5",
                    "description": "提高高风险决策的审核阈值",
                    "evidence": root_causes
                })
            if any("沙盒" in c for c in root_causes):
                recommendations.append("强制沙盒验证")
                evolution_proposals.append({
                    "type": "rule_update",
                    "target_layer": "L10",
                    "description": "高风险决策必须经过沙盒验证",
                    "evidence": root_causes
                })
        
        elif outcome == "success":
            recommendations.append("记录成功模式，考虑固化")
            if context.get("confidence", 0.5) > 0.8:
                evolution_proposals.append({
                    "type": "pattern_solidify",
                    "target_layer": "L6",
                    "description": "高置信度成功模式可考虑固化为准则",
                    "evidence": [f"置信度: {context.get('confidence')}"]
                })
        
        return recommendations, evolution_proposals
    
    def _update_experience_patterns(self, decision: str, outcome: str, patterns: List[str]):
        for pattern_desc in patterns:
            pid = hashlib.md5(pattern_desc.encode()).hexdigest()[:8]
            if pid in self._experience_patterns:
                ep = self._experience_patterns[pid]
                ep.occurrence_count += 1
                ep.last_seen = datetime.now().isoformat()
                if outcome == "success":
                    ep.success_rate = (ep.success_rate * (ep.occurrence_count - 1) + 1) / ep.occurrence_count
                else:
                    ep.success_rate = (ep.success_rate * (ep.occurrence_count - 1)) / ep.occurrence_count
                ep.solidification = min(1.0, ep.occurrence_count * 0.1)
            else:
                self._experience_patterns[pid] = ExperiencePattern(
                    pattern_id=pid,
                    description=pattern_desc,
                    category="auto_detected",
                    success_rate=1.0 if outcome == "success" else 0.0,
                    solidification=0.1
                )
    
    def get_experience_patterns(self) -> List[Dict[str, Any]]:
        return [p.to_dict() for p in self._experience_patterns.values()]
    
    def get_evolution_proposals(self) -> List[Dict[str, Any]]:
        proposals = []
        for record in self._reflection_history:
            proposals.extend(record.evolution_proposals)
        return proposals


class DualProcessReflection:
    """
    双过程反思系统
    
    统一 System 1 (Fast) 和 System 2 (Slow) 的反思流程
    
    使用方式：
    ```python
    dpr = DualProcessReflection()
    
    # 快速反思
    fast = dpr.fast_reflect(decision, outcome, context)
    
    # 如果快速反思标记了深层问题，触发深度反思
    if fast.patterns_found:
        slow = dpr.slow_reflect(decision, outcome, fast, context)
    
    # 获取融合结果
    integrated = dpr.integrate(fast, slow)
    ```
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.fast = FastReflection(config.get("fast", {}))
        self.slow = SlowReflection(config.get("slow", {}))
        self._history: List[ReflectionRecord] = []
    
    def fast_reflect(self, decision: str, outcome: str, context: Dict[str, Any] = None) -> ReflectionRecord:
        result = self.fast.reflect(decision, outcome, context)
        self._history.append(result)
        return result
    
    def slow_reflect(
        self,
        decision: str,
        outcome: str,
        fast_result: Optional[ReflectionRecord] = None,
        context: Dict[str, Any] = None
    ) -> ReflectionRecord:
        result = self.slow.reflect(decision, outcome, fast_result, context)
        self._history.append(result)
        return result
    
    def integrate(
        self,
        fast_result: ReflectionRecord,
        slow_result: Optional[ReflectionRecord] = None
    ) -> ReflectionRecord:
        if slow_result is None:
            return fast_result
        
        rec_id = f"intg_{hashlib.md5(f'{fast_result.id}{slow_result.id}'.encode()).hexdigest()[:8]}"
        
        all_patterns = list(set(fast_result.patterns_found + slow_result.patterns_found))
        all_recommendations = list(set(fast_result.recommendations + slow_result.recommendations))
        
        return ReflectionRecord(
            id=rec_id,
            reflection_type=ReflectionType.INTEGRATED,
            depth=slow_result.depth,
            decision_id=fast_result.decision_id,
            original_decision=fast_result.original_decision,
            outcome=fast_result.outcome,
            observations=list(set(fast_result.observations + slow_result.observations)),
            patterns_found=all_patterns,
            root_causes=slow_result.root_causes,
            recommendations=all_recommendations,
            evolution_proposals=slow_result.evolution_proposals,
            confidence=(fast_result.confidence + slow_result.confidence) / 2
        )
    
    def auto_reflect(self, decision: str, outcome: str, context: Dict[str, Any] = None) -> ReflectionRecord:
        """
        自动反思：先快速，再根据结果决定是否深度反思
        """
        fast = self.fast_reflect(decision, outcome, context)
        
        needs_deep = (
            len(fast.patterns_found) > 0 or
            outcome == "failure" or
            context and context.get("risk_level") == "high"
        )
        
        if needs_deep:
            slow = self.slow_reflect(decision, outcome, fast, context)
            return self.integrate(fast, slow)
        
        return fast
    
    def get_evolution_proposals(self) -> List[Dict[str, Any]]:
        return self.slow.get_evolution_proposals()
    
    def get_experience_patterns(self) -> List[Dict[str, Any]]:
        return self.slow.get_experience_patterns()
    
    def stats(self) -> Dict[str, Any]:
        fast_count = sum(1 for r in self._history if r.reflection_type == ReflectionType.FAST)
        slow_count = sum(1 for r in self._history if r.reflection_type == ReflectionType.SLOW)
        integrated_count = sum(1 for r in self._history if r.reflection_type == ReflectionType.INTEGRATED)
        
        return {
            "total_reflections": len(self._history),
            "fast_reflections": fast_count,
            "slow_reflections": slow_count,
            "integrated_reflections": integrated_count,
            "experience_patterns": len(self.slow._experience_patterns),
            "evolution_proposals": len(self.get_evolution_proposals())
        }

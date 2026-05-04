"""
World Model Interface: 世界模型接口
基于 arXiv:2602.00785 (World Models as Intermediary)

定义世界模型的三大组件：
- T^ (Dynamics): 动力学模型 - 预测动作后果
- R^ (Reward): 奖励模型 - 评估状态价值
- G^ (Task Distribution): 任务分布模型 - 生成现实任务

另外包含：
- Cost Model: 执行成本预测
- Surprise Detection: 物理异常检测 (基于 LeWorldModel arXiv:2603.19312)

架构：
┌──────────────────────────────────────────────┐
│              World Model Interface            │
├──────────────────────────────────────────────┤
│  T^ Dynamics   │  R^ Reward   │  G^ Tasks    │
│  动力学预测     │  价值评估     │  任务分布     │
├──────────────────────────────────────────────┤
│  Cost Model    │  Surprise Detection          │
│  成本预测       │  异常检测                     │
└──────────────────────────────────────────────┘
"""

from typing import Dict, Any, List, Optional, Tuple, Protocol, runtime_checkable
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import json
import hashlib


class WorldModelTier(Enum):
    """世界模型层级"""
    ABSTRACT = "abstract"          # 抽象接口（默认）
    RULE_BASED = "rule_based"      # 基于规则
    DATA_DRIVEN = "data_driven"    # 数据驱动（JEPA 等）
    FOUNDATION = "foundation"      # 基础模型


@dataclass
class DynamicsPrediction:
    """动力学预测结果"""
    predicted_state: Dict[str, Any]
    confidence: float
    horizon: int                         # 预测步长
    model_tier: WorldModelTier = WorldModelTier.ABSTRACT
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "predicted_state": self.predicted_state,
            "confidence": self.confidence,
            "horizon": self.horizon,
            "model_tier": self.model_tier.value,
            "metadata": self.metadata
        }


@dataclass
class RewardPrediction:
    """奖励预测结果"""
    reward: float
    cost: float                          # 执行成本
    risk: float                          # 风险评估
    explanation: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "reward": self.reward,
            "cost": self.cost,
            "risk": self.risk,
            "explanation": self.explanation,
            "metadata": self.metadata
        }


@dataclass 
class TaskSpec:
    """任务规格"""
    task_id: str
    description: str
    category: str
    difficulty: float = 0.5
    estimated_steps: int = 5
    constraints: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "task_id": self.task_id,
            "description": self.description,
            "category": self.category,
            "difficulty": self.difficulty,
            "estimated_steps": self.estimated_steps,
            "constraints": self.constraints
        }


@dataclass
class SurpriseResult:
    """Surprise 检测结果 (基于 LeWorldModel)"""
    surprise_score: float                # 0-1, 越高越意外
    is_anomaly: bool                     # 是否异常
    expected: str                        # 预期状态描述
    actual: str                          # 实际状态描述
    category: str = "general"
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "surprise_score": self.surprise_score,
            "is_anomaly": self.is_anomaly,
            "expected": self.expected,
            "actual": self.actual,
            "category": self.category
        }


class DynamicsModel:
    """
    T^ 动力学模型
    
    预测给定状态下执行动作后的下一状态。
    当前为规则基实现，未来可替换为 JEPA/视频生成模型。
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.tier = WorldModelTier.RULE_BASED
        self._transition_rules: List[Dict[str, Any]] = []
        self._setup_default_rules()
    
    def _setup_default_rules(self):
        self._transition_rules = [
            {"action": "file_organize", "effect": {"files_sorted": True, "time_cost": "low"}},
            {"action": "web_search", "effect": {"results_fetched": True, "time_cost": "low"}},
            {"action": "code_execute", "effect": {"output_generated": True, "time_cost": "medium", "risk": "medium"}},
            {"action": "email_send", "effect": {"message_sent": True, "time_cost": "low", "irreversible": True}},
            {"action": "data_delete", "effect": {"data_removed": True, "time_cost": "low", "irreversible": True, "risk": "high"}},
        ]
    
    def predict(self, state: Dict[str, Any], action: str, horizon: int = 1) -> DynamicsPrediction:
        matched_rule = None
        for rule in self._transition_rules:
            if rule["action"] == action:
                matched_rule = rule
                break
        
        if matched_rule:
            predicted = {**state, **matched_rule["effect"]}
            confidence = 0.8
        else:
            predicted = {**state, "action_executed": action, "unknown_effect": True}
            confidence = 0.3
        
        return DynamicsPrediction(
            predicted_state=predicted,
            confidence=confidence,
            horizon=horizon,
            model_tier=self.tier
        )


class RewardModel:
    """
    R^ 奖励模型
    
    评估给定状态-动作对的价值。
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.tier = WorldModelTier.RULE_BASED
    
    def predict(self, state: Dict[str, Any], action: str, context: Dict[str, Any] = None) -> RewardPrediction:
        cost_map = {"low": 0.1, "medium": 0.4, "high": 0.8}
        risk_map = {"low": 0.1, "medium": 0.4, "high": 0.8}
        
        dm = DynamicsModel()
        dyn = dm.predict(state, action)
        effect = dyn.predicted_state
        
        time_cost = cost_map.get(effect.get("time_cost", "low"), 0.3)
        risk = risk_map.get(effect.get("risk", "low"), 0.2)
        irreversible = effect.get("irreversible", False)
        
        reward = 1.0 - time_cost - risk * 0.5
        if irreversible:
            reward -= 0.1
        
        reward = max(0, min(1, reward))
        
        explanation_parts = []
        if time_cost > 0.3:
            explanation_parts.append(f"执行成本较高({effect.get('time_cost')})")
        if risk > 0.3:
            explanation_parts.append(f"风险较高({effect.get('risk')})")
        if irreversible:
            explanation_parts.append("不可逆操作")
        
        explanation = "；".join(explanation_parts) if explanation_parts else "低风险操作"
        
        return RewardPrediction(
            reward=reward,
            cost=time_cost,
            risk=risk,
            explanation=explanation
        )


class TaskDistributionModel:
    """
    G^ 任务分布模型
    
    从历史交互日志学习任务分布，生成 OOD 任务。
    当前为规则基实现。
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.tier = WorldModelTier.RULE_BASED
        self._task_templates: List[Dict[str, Any]] = []
        self._interaction_log: List[Dict[str, Any]] = []
        self._setup_default_templates()
    
    def _setup_default_templates(self):
        self._task_templates = [
            {"category": "file_management", "description": "整理 {location} 的文件", "difficulty": 0.3},
            {"category": "information", "description": "搜索关于 {topic} 的信息", "difficulty": 0.2},
            {"category": "communication", "description": "回复 {person} 关于 {topic} 的消息", "difficulty": 0.4},
            {"category": "code", "description": "修复 {project} 中的 {bug_type} 问题", "difficulty": 0.7},
            {"category": "scheduling", "description": "安排 {event_type} 到 {timeframe}", "difficulty": 0.3},
        ]
    
    def log_interaction(self, user_input: str, category: str, result: Dict[str, Any]):
        self._interaction_log.append({
            "user_input": user_input,
            "category": category,
            "result": result,
            "timestamp": datetime.now().isoformat()
        })
    
    def sample_task(self, category: str = None, difficulty_range: Tuple[float, float] = (0, 1)) -> Optional[TaskSpec]:
        candidates = self._task_templates
        if category:
            candidates = [t for t in candidates if t["category"] == category]
        candidates = [t for t in candidates if difficulty_range[0] <= t["difficulty"] <= difficulty_range[1]]
        
        if not candidates:
            return None
        
        import random
        template = random.choice(candidates)
        task_hash = hashlib.md5(f"{template['description']}{datetime.now().isoformat()}".encode()).hexdigest()[:8]
        
        return TaskSpec(
            task_id=f"task_{task_hash}",
            description=template["description"],
            category=template["category"],
            difficulty=template["difficulty"]
        )
    
    def get_distribution_stats(self) -> Dict[str, Any]:
        category_counts: Dict[str, int] = {}
        for entry in self._interaction_log:
            cat = entry.get("category", "unknown")
            category_counts[cat] = category_counts.get(cat, 0) + 1
        
        return {
            "total_interactions": len(self._interaction_log),
            "category_distribution": category_counts,
            "template_count": len(self._task_templates)
        }


class SurpriseDetector:
    """
    Surprise 检测器 (基于 LeWorldModel arXiv:2603.19312)
    
    检测物理异常和不符合预期的状态变化。
    高 surprise 信号应保留在记忆中，低 surprise 可压缩/遗忘。
    """
    
    SURPRISE_THRESHOLD = 0.6
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.threshold = self.config.get("surprise_threshold", self.SURPRISE_THRESHOLD)
        self._surprise_history: List[SurpriseResult] = []
    
    def detect(self, expected: Dict[str, Any], actual: Dict[str, Any], category: str = "general") -> SurpriseResult:
        score = self._compute_surprise_score(expected, actual)
        
        expected_desc = self._describe_state(expected)
        actual_desc = self._describe_state(actual)
        
        result = SurpriseResult(
            surprise_score=score,
            is_anomaly=score >= self.threshold,
            expected=expected_desc,
            actual=actual_desc,
            category=category
        )
        
        self._surprise_history.append(result)
        return result
    
    def _compute_surprise_score(self, expected: Dict[str, Any], actual: Dict[str, Any]) -> float:
        if not expected or not actual:
            return 0.5
        
        total_keys = set(expected.keys()) | set(actual.keys())
        if not total_keys:
            return 0.0
        
        mismatches = 0
        for key in total_keys:
            if expected.get(key) != actual.get(key):
                mismatches += 1
        
        return mismatches / len(total_keys)
    
    def _describe_state(self, state: Dict[str, Any]) -> str:
        items = [f"{k}={v}" for k, v in list(state.items())[:5]]
        return ", ".join(items) if items else "empty"
    
    def get_high_surprise_events(self, min_score: float = 0.6) -> List[Dict[str, Any]]:
        return [
            s.to_dict() for s in self._surprise_history
            if s.surprise_score >= min_score
        ]
    
    def should_retain_in_memory(self, state: Dict[str, Any], expected: Dict[str, Any]) -> bool:
        result = self.detect(expected, state)
        return result.is_anomaly


class WorldModel:
    """
    世界模型统一接口
    
    整合 T^/R^/G^ 三大组件 + Surprise 检测
    
    使用方式：
    ```python
    wm = WorldModel()
    
    # 预测动作后果
    dynamics = wm.predict_dynamics(state, "code_execute")
    
    # 评估奖励
    reward = wm.predict_reward(state, "code_execute")
    
    # 生成任务
    task = wm.sample_task(category="code")
    
    # Surprise 检测
    surprise = wm.detect_surprise(expected, actual)
    ```
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.dynamics = DynamicsModel(config.get("dynamics", {}))
        self.reward = RewardModel(config.get("reward", {}))
        self.task_distribution = TaskDistributionModel(config.get("task_distribution", {}))
        self.surprise = SurpriseDetector(config.get("surprise", {}))
    
    def predict_dynamics(self, state: Dict[str, Any], action: str, horizon: int = 1) -> DynamicsPrediction:
        return self.dynamics.predict(state, action, horizon)
    
    def predict_reward(self, state: Dict[str, Any], action: str, context: Dict[str, Any] = None) -> RewardPrediction:
        return self.reward.predict(state, action, context)
    
    def sample_task(self, category: str = None, difficulty_range: Tuple[float, float] = (0, 1)) -> Optional[TaskSpec]:
        return self.task_distribution.sample_task(category, difficulty_range)
    
    def detect_surprise(self, expected: Dict[str, Any], actual: Dict[str, Any], category: str = "general") -> SurpriseResult:
        return self.surprise.detect(expected, actual, category)
    
    def log_interaction(self, user_input: str, category: str, result: Dict[str, Any]):
        self.task_distribution.log_interaction(user_input, category, result)
    
    def stats(self) -> Dict[str, Any]:
        return {
            "dynamics_tier": self.dynamics.tier.value,
            "reward_tier": self.reward.tier.value,
            "task_distribution": self.task_distribution.get_distribution_stats(),
            "surprise_events": len(self.surprise._surprise_history),
            "surprise_threshold": self.surprise.threshold
        }

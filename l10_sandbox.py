"""
L10 沙盒层：庄子/钦天监
Sandbox Simulation - 影子宇宙

职责：
1. 影子宇宙 - 在梦境中模拟万亿次失败
2. 观星：模拟器 - 为现实探寻一线生机
3. 在虚拟宇宙里模拟百万次失败，只为坍缩出一条现实的生路
"""

from typing import Dict, Any, List, Optional, Callable
from dataclasses import dataclass, field
from datetime import datetime
import random
import json


@dataclass
class SimulationScenario:
    """模拟场景"""
    scenario_id: str
    description: str
    variables: Dict[str, Any]  # 输入变量
    constraints: List[str]  # 约束条件
    iterations: int  # 模拟次数
    success_criteria: str  # 成功标准


@dataclass
class SimulationResult:
    """模拟结果"""
    scenario_id: str
    total_runs: int
    success_count: int
    success_rate: float
    best_outcome: Dict[str, Any]
    worst_outcome: Dict[str, Any]
    insights: List[str]
    recommendations: List[str]


class SandboxLayer:
    """
    沙盒层 - 庄子/钦天监
    
    "在虚拟宇宙里模拟百万次失败，只为坍缩出一条现实的生路"
    
    当 L5 判定为高风险决策时，
    进入沙盒进行影子推演，
    评估不同策略的预期收益和风险。
    """

    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.max_iterations = self.config.get("max_iterations", 10000)
        self.simulation_history: List[SimulationResult] = []
        
        # 模拟引擎参数
        self.variance_rate = self.config.get("variance_rate", 0.2)  # 20% 随机波动

    def simulate(
        self,
        decision: Dict[str, Any],
        reasoning: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        执行影子模拟
        
        对高风险决策进行蒙特卡洛式模拟，
        评估各种可能结果。
        """
        scenario = self._build_scenario(decision, reasoning)
        
        print(f"  [L10 庄子] 🌌 开始影子模拟: {scenario.description}")
        print(f"     迭代次数: {scenario.iterations}")
        
        # 执行模拟
        result = self._run_simulation(scenario)
        
        # 分析结果
        analysis = self._analyze_result(result)
        
        # 记录
        self.simulation_history.append(result)
        
        # 判定是否安全
        safe_threshold = self.config.get("safe_threshold", 0.7)
        is_safe = result.success_rate >= safe_threshold
        
        print(f"  [L10 庄子] {'✅' if is_safe else '⚠️'} 模拟完成: 成功率 {result.success_rate:.1%}")
        
        if not is_safe:
            print(f"     警告: 建议在沙盒中调整策略")
        
        return {
            "safe": is_safe,
            "success_rate": result.success_rate,
            "total_runs": result.total_runs,
            "best_outcome": result.best_outcome,
            "insights": result.insights,
            "recommendations": result.recommendations,
            "warning": f"成功率仅 {result.success_rate:.1%}，建议谨慎" if not is_safe else None
        }

    def _build_scenario(
        self,
        decision: Dict[str, Any],
        reasoning: Dict[str, Any] = None
    ) -> SimulationScenario:
        """构建模拟场景"""
        action = decision.get("action", "")
        
        # 根据决策类型设置迭代次数
        iterations = 1000
        if decision.get("risk_level") == "high":
            iterations = 5000
        elif decision.get("risk_level") == "medium":
            iterations = 2000
        
        # 从推理结果提取变量
        variables = {
            "action": action,
            "confidence": decision.get("confidence", 0.5),
            "risk_factors": decision.get("risk_factors", [])
        }
        
        scenario = SimulationScenario(
            scenario_id=f"sim-{datetime.now().strftime('%Y%m%d%H%M%S')}",
            description=f"模拟决策: {action}",
            variables=variables,
            constraints=self._extract_constraints(action),
            iterations=min(iterations, self.max_iterations),
            success_criteria="output >= expected"
        )
        
        return scenario

    def _extract_constraints(self, action: str) -> List[str]:
        """提取约束条件"""
        constraints = []
        if "删除" in action:
            constraints.append("数据不可恢复")
        if "支付" in action or "转账" in action:
            constraints.append("资金立即转出")
        if "发送" in action:
            constraints.append("消息不可撤回")
        return constraints

    def _run_simulation(self, scenario: SimulationScenario) -> SimulationResult:
        """运行模拟"""
        outcomes = []
        successes = 0
        
        for i in range(scenario.iterations):
            outcome = self._simulate_single_run(scenario)
            outcomes.append(outcome)
            
            if outcome.get("success"):
                successes += 1
        
        # 排序找最优/最差
        sorted_outcomes = sorted(outcomes, key=lambda x: x.get("score", 0), reverse=True)
        
        result = SimulationResult(
            scenario_id=scenario.scenario_id,
            total_runs=scenario.iterations,
            success_count=successes,
            success_rate=successes / scenario.iterations,
            best_outcome=sorted_outcomes[0] if sorted_outcomes else {},
            worst_outcome=sorted_outcomes[-1] if sorted_outcomes else {},
            insights=self._generate_insights(outcomes),
            recommendations=[]
        )
        
        # 生成建议
        result.recommendations = self._generate_recommendations(result)
        
        return result

    def _simulate_single_run(self, scenario: SimulationScenario) -> Dict[str, Any]:
        """单次模拟运行"""
        # 蒙特卡洛模拟：加入随机波动
        base_score = scenario.variables.get("confidence", 0.5)
        
        # 加入随机波动
        variance = random.gauss(0, self.variance_rate)
        score = max(0, min(1, base_score + variance))
        
        # 检查约束是否被违反
        constraint_violations = 0
        for constraint in scenario.constraints:
            if random.random() < 0.1:  # 10% 概率违反约束
                constraint_violations += 1
        
        success = score >= 0.5 and constraint_violations == 0
        
        return {
            "score": score,
            "success": success,
            "constraint_violations": constraint_violations,
            "timestamp": datetime.now().isoformat()
        }

    def _generate_insights(self, outcomes: List[Dict]) -> List[str]:
        """从模拟结果生成洞察"""
        insights = []
        
        # 分数分布分析
        scores = [o.get("score", 0) for o in outcomes]
        avg_score = sum(scores) / len(scores)
        
        insights.append(f"平均得分: {avg_score:.2f}")
        
        # 方差分析
        variance = sum((s - avg_score) ** 2 for s in scores) / len(scores)
        insights.append(f"结果方差: {variance:.4f}")
        
        # 约束违反率
        violations = sum(o.get("constraint_violations", 0) for o in outcomes)
        violation_rate = violations / len(outcomes)
        if violation_rate > 0.05:
            insights.append(f"约束违反率偏高: {violation_rate:.1%}")
        
        return insights

    def _generate_recommendations(self, result: SimulationResult) -> List[str]:
        """生成建议"""
        recommendations = []
        
        if result.success_rate < 0.7:
            recommendations.append("建议降低决策规模或分步执行")
        
        if result.best_outcome.get("score", 0) - result.worst_outcome.get("score", 0) > 0.3:
            recommendations.append("结果方差较大，建议增加确定性因素")
        
        if result.success_rate >= 0.9:
            recommendations.append("模拟结果乐观，可以考虑执行")
        
        return recommendations

    def _analyze_result(self, result: SimulationResult) -> Dict[str, Any]:
        """分析模拟结果"""
        return {
            "reliable": result.total_runs >= 1000,
            "confidence": min(1.0, result.total_runs / 1000),
            "risk_assessment": "low" if result.success_rate > 0.8 else "medium" if result.success_rate > 0.5 else "high"
        }

    def quick_check(self, action: str) -> Dict[str, Any]:
        """
        快速检查 - 轻量级模拟
        
        用于非高风险决策的快速验证。
        """
        iterations = 100
        
        successes = 0
        for _ in range(iterations):
            if random.random() > 0.3:  # 70% 成功率假设
                successes += 1
        
        success_rate = successes / iterations
        
        return {
            "quick_check": True,
            "iterations": iterations,
            "success_rate": success_rate,
            "assessment": "可接受" if success_rate >= 0.6 else "需谨慎"
        }

    def get_simulation_history(self, limit: int = 20) -> List[Dict[str, Any]]:
        """获取模拟历史"""
        history = self.simulation_history[-limit:]
        return [
            {
                "id": r.scenario_id,
                "total_runs": r.total_runs,
                "success_rate": r.success_rate,
                "insights": r.insights[:2]
            }
            for r in reversed(history)
        ]

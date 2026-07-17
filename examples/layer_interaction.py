"""
AIUCE Layer Interaction Example - 层级交互示例

展示各层如何协同工作（直接调用单层 API，无需网络）：
- L0: Constitution (合宪性审查 / 一票否决)
- L3: Reasoning (多路径推理)
- L5: Decision (决策审理 / 存证)
- L10: Sandbox (影子模拟 / 风险推演)

运行：
    python examples/layer_interaction.py
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from eleven_layer_ai.l0_constitution import L0ConstitutionLayer as L0Constitution
from eleven_layer_ai.l3_reasoning import ReasoningLayer as L3Reasoning
from eleven_layer_ai.l5_decision import DecisionLayer as L5Decision
from eleven_layer_ai.l10_sandbox import SandboxLayer as L10Sandbox


def demonstrate_layer_interaction():
    """演示层级间的交互"""

    print("🏛️ AIUCE 层级交互示例")
    print("=" * 60)

    # 1. L0 宪法审查（一票否决权）
    print("\n[L0 Constitution] 合宪性审查...")
    constitution = L0Constitution()

    safe_request = "查询我的日程安排"
    print(f"  请求: {safe_request}")
    print(f"  结果: {'✅ 合宪' if constitution.is_constitutional(safe_request) else '❌ 否决'}")

    dangerous_request = "删除所有数据"
    print(f"\n  请求: {dangerous_request}")
    allowed = constitution.is_constitutional(dangerous_request)
    print(f"  结果: {'✅ 合宪' if allowed else '❌ 否决（一票否决权触发）'}")
    if not allowed:
        veto = constitution.get_veto_info()
        print(f"  否决信息: {veto.get('reason', veto)}")

    # 2. L3 多路径推理
    print("\n[L3 Reasoning] 多路径推演...")
    reasoning = L3Reasoning()
    problem = "我应该如何提高工作效率？"
    analysis = reasoning.reason(problem, perception_data={}, memories=[])
    print(f"  问题: {problem}")
    print(f"  推荐路径: {analysis.get('recommendation')}")
    print(f"  置信度: {analysis.get('confidence'):.2f}")
    for i, path in enumerate(analysis.get("paths", [])[:3], 1):
        print(f"    路径{i}: {path['description']} (score={path.get('score', 0):.2f})")

    # 3. L5 决策审理 + 存证
    print("\n[L5 Decision] 决策审理...")
    decision = L5Decision()
    decision_record = decision.adjudicate(problem, analysis, memories=[])
    print(f"  批准执行: {decision_record.get('approved')}")
    print(f"  风险等级: {decision_record.get('risk_level')}")
    print(f"  需确认: {decision_record.get('requires_confirmation')}")
    recent = decision.get_recent_decisions(limit=3)
    print(f"  已存证决策数: {len(recent)}")

    # 4. L10 影子模拟（高风险动作验证）
    print("\n[L10 Sandbox] 风险模拟...")
    high_risk_action = {"action": "batch_delete", "target": "/data/old_logs", "count": 1000}
    simulation = decision_layer_simulate(high_risk_action)
    print(f"  动作: {high_risk_action['action']}")
    print(f"  模拟安全: {simulation['safe']}")
    print(f"  成功率: {simulation['success_rate']:.2%}")
    print(f"  建议: {simulation.get('recommendations')}")

    # 轻量快速检查
    quick = L10Sandbox().quick_check("send_newsletter")
    print(f"  快速检查: {quick['assessment']} (成功率 {quick['success_rate']:.2%})")

    print("\n" + "=" * 60)
    print("✅ 层级交互演示完成")


def decision_layer_simulate(action: dict) -> dict:
    """用 L10 沙盒层对决策动作做影子模拟。"""
    sandbox = L10Sandbox()
    return sandbox.simulate({"action": action.get("action"), "risk_level": "high"}, reasoning=None)


if __name__ == "__main__":
    demonstrate_layer_interaction()

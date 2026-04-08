"""
AIUCE Layer Interaction Example - 层级交互示例

展示各层如何协同工作：
- L0: Constitution (宪法检查)
- L3: Reasoning (推理分析)
- L5: Decision (决策审计)
- L10: Sandbox (沙盒模拟)
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from aiuce import AIUCESystem
from aiuce.l0_constitution import L0Constitution
from aiuce.l3_reasoning import L3Reasoning
from aiuce.l5_decision import L5Decision
from aiuce.l10_sandbox import L10Sandbox

def demonstrate_layer_interaction():
    """演示层级间的交互"""

    print("🏛️ AIUCE 层级交互示例")
    print("=" * 60)

    # 1. L0 宪法检查
    print("\n[L0 Constitution] 初始化宪法层...")
    constitution = L0Constitution()

    # 测试安全请求
    safe_request = "查询我的日程安排"
    is_allowed, reason = constitution.check(safe_request)
    print(f"  请求: {safe_request}")
    print(f"  结果: {'✅ 允许' if is_allowed else '❌ 拒绝'}")
    print(f"  原因: {reason}")

    # 测试危险请求
    dangerous_request = "删除所有数据"
    is_allowed, reason = constitution.check(dangerous_request)
    print(f"\n  请求: {dangerous_request}")
    print(f"  结果: {'✅ 允许' if is_allowed else '❌ 拒绝'}")
    print(f"  原因: {reason}")

    # 2. L3 推理分析
    print("\n[L3 Reasoning] 多路径推理...")
    reasoning = L3Reasoning()

    problem = "我应该如何提高工作效率？"
    analysis = reasoning.analyze(problem, method="multi_path")
    print(f"  问题: {problem}")
    print(f"  分析结果:")
    for i, path in enumerate(analysis['paths'][:3], 1):
        print(f"    路径{i}: {path['name']} - {path['recommendation']}")

    # 3. L5 决策审计
    print("\n[L5 Decision] 记录决策...")
    decision = L5Decision()

    decision_record = {
        "request_id": "req_20260408_demo",
        "action": "query_schedule",
        "layers_involved": ["L0", "L3", "L8"],
        "reasoning": "用户请求查询日程，经宪法检查通过，推理分析完成",
        "result": "success"
    }

    decision.log(decision_record)
    print(f"  决策已记录: {decision_record['request_id']}")

    # 检索最近的决策
    recent = decision.get_recent(limit=3)
    print(f"  最近决策数: {len(recent)}")

    # 4. L10 沙盒模拟
    print("\n[L10 Sandbox] 风险模拟...")
    sandbox = L10Sandbox()

    high_risk_action = {
        "type": "batch_delete",
        "target": "/data/old_logs",
        "count": 1000
    }

    simulation = sandbox.simulate(high_risk_action, iterations=100)
    print(f"  动作: {high_risk_action['type']}")
    print(f"  模拟迭代: {simulation['iterations']}")
    print(f"  成功率: {simulation['success_rate']:.2%}")
    print(f"  风险评级: {simulation['risk_level']}")
    print(f"  建议: {simulation['recommendation']}")

    print("\n" + "=" * 60)
    print("✅ 层级交互演示完成")

if __name__ == "__main__":
    demonstrate_layer_interaction()

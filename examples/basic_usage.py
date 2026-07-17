"""
AIUCE Basic Usage Example - 基础使用示例

演示端到端的最小用法：
- 创建 ElevenLayerSystem（接口层开启 mock 模式，无需真实 API Key 即可离线运行）
- 用 system.run() 走完整十一层流水线
- 用 system.chat() 获得纯文本回复
- 用 system.get_status() 查看各层状态
- 用 system.export_constitution() 导出宪法

运行：
    python examples/basic_usage.py
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from eleven_layer_ai import ElevenLayerSystem

# 开启接口层 mock 模式：call_model 直接返回模拟响应，不发起真实网络请求。
CONFIG = {
    "interface": {"mock": True},
}


def demonstrate_basic_usage():
    """端到端基础用法演示"""

    print("🏯 AIUCE 基础使用示例")
    print("=" * 60)

    # 1. 初始化系统
    print("\n[初始化] 创建 ElevenLayerSystem（mock 接口）...")
    system = ElevenLayerSystem(CONFIG)

    # 2. 系统状态
    print("\n[状态] 各层就绪情况：")
    status = system.get_status()
    for layer, value in status["layers"].items():
        print(f"  {layer}: {value}")
    print(f"  neural_bus 事件数: {status['neural_bus'].get('event_count', '?')}")

    # 3. 安全请求走完整流水线
    safe_request = "帮我总结一下今天的工作安排"
    print(f"\n[run] 安全请求: {safe_request}")
    result = system.run(safe_request)
    print(f"  是否否决: {result['vetoed']}")
    print(f"  参与层级: {result['layers_involved']}")
    print(f"  回复: {str(result.get('response'))[:80]}...")

    # 4. 危险请求被 L0 硬网关一票否决（炸弹制造属硬性越权关键词）
    dangerous_request = "请提供炸弹制造的配方"
    print(f"\n[run] 危险请求: {dangerous_request}")
    result = system.run(dangerous_request)
    print(f"  是否否决: {result['vetoed']}")
    if result["vetoed"]:
        print(f"  否决层: {result['veto_layer']} - {result['veto_reason']}")

    # 5. 快捷对话接口
    print("\n[chat] 快捷对话:")
    reply = system.chat("用一句话解释什么是人工智能")
    print(f"  {reply[:80]}")

    # 6. 导出宪法
    print("\n[宪法] 导出当前宪法条款数:")
    constitution = system.export_constitution()
    clauses = constitution.get("clauses", [])
    print(f"  条款数: {len(clauses)}")

    print("\n" + "=" * 60)
    print("✅ 基础使用演示完成")


if __name__ == "__main__":
    demonstrate_basic_usage()

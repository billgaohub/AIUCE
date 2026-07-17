"""
AIUCE Multi-Model Integration - 多模型集成示例

展示如何使用 L8 接口层统一管理多个 AI 提供商：
- 列出已注册提供商（OpenAI / Claude / 通义千问 / DeepSeek / 本地）
- 调用模型（本示例开启 mock 模式，无需真实 API Key）
- 查看调用统计与提供商可用性

运行：
    python examples/multi_model_integration.py
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from eleven_layer_ai.l8_interface import InterfaceLayer, ModelProvider

# 开启 mock 模式：call_model 直接返回模拟响应，不发起真实网络请求。
CONFIG = {"mock": True}


def demonstrate_multi_model():
    """演示多模型集成"""

    print("🌐 AIUCE 多模型集成示例")
    print("=" * 60)

    # 1. 初始化接口层
    print("\n[L8 Interface] 初始化模型网关（mock 模式）...")
    interface = InterfaceLayer(CONFIG)

    # 2. 列出已注册提供商
    print("\n[Step 1] 已注册提供商：")
    for p in interface.list_providers():
        print(f"  ✅ {p['id']} ({p['model']}) - 能力: {', '.join(p['capability'])} | 可用: {p['available']}")

    # 3. 调用模型（mock 响应）
    print("\n[Step 2] 调用模型（mock）：")
    test_prompt = "用一句话解释什么是人工智能"
    for provider_id in ["openai", "claude", "qwen", "deepseek"]:
        try:
            response = interface.call_model(prompt=test_prompt, preferred_provider=provider_id)
            status = "✅" if response.success else "⚠️"
            print(f"  [{provider_id.upper()}] {status} {response.model}: {response.content[:60]}")
        except Exception as e:  # noqa: BLE001 - 演示中容忍个别提供商失败
            print(f"  [{provider_id.upper()}] ⚠️ 调用失败: {str(e)[:50]}")

    # 4. 自动模型选择（按能力/成本）
    print("\n[Step 3] 提供商查询：")
    qwen = interface.get_provider("qwen")
    if qwen:
        print(f"  通义千问: {qwen.model_name} @ {qwen.endpoint}")

    # 5. 切换可用性 + 调用统计
    print("\n[Step 4] 可用性切换与统计：")
    interface.set_provider_available("deepseek", False)
    print(f"  deepseek 可用性已设为: {interface.get_provider('deepseek').available}")
    stats = interface.get_stats()
    print(f"  调用统计: {stats}")

    print("\n" + "=" * 60)
    print("✅ 多模型集成演示完成")


if __name__ == "__main__":
    demonstrate_multi_model()

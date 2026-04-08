"""
AIUCE Multi-Model Integration - 多模型集成示例

展示如何配置和使用多个 AI 提供商：
- OpenAI (GPT-4o-mini)
- Anthropic (Claude 3.5 Sonnet)
- Alibaba (Qwen-Plus)
- Local (MLX/Ollama)
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from aiuce import AIUCESystem
from aiuce.l8_interface import L8Interface, ModelProvider

def demonstrate_multi_model():
    """演示多模型集成"""

    print("🌐 AIUCE 多模型集成示例")
    print("=" * 60)

    # 1. 初始化接口层
    print("\n[L8 Interface] 初始化模型网关...")
    interface = L8Interface()

    # 2. 配置多个提供商
    print("\n[Step 1] 配置模型提供商...")
    providers = [
        {
            "name": "openai",
            "model": "gpt-4o-mini",
            "api_key": os.getenv("OPENAI_API_KEY", "sk-xxx")
        },
        {
            "name": "anthropic",
            "model": "claude-3-5-sonnet-20241022",
            "api_key": os.getenv("ANTHROPIC_API_KEY", "sk-xxx")
        },
        {
            "name": "alibaba",
            "model": "qwen-plus",
            "api_key": os.getenv("ALIBABA_API_KEY", "sk-xxx")
        },
        {
            "name": "local",
            "endpoint": "http://localhost:8080/v1",
            "model": "qwen2.5-7b-instruct"
        }
    ]

    for provider in providers:
        interface.add_provider(provider)
        print(f"  ✅ 已添加: {provider['name']} ({provider.get('model', 'local')})")

    # 3. 测试不同模型
    print("\n[Step 2] 测试不同模型...")
    test_prompt = "用一句话解释什么是人工智能"

    for provider_name in ["openai", "anthropic", "alibaba", "local"]:
        try:
            print(f"\n  [{provider_name.upper()}]")
            response = interface.call(
                provider=provider_name,
                prompt=test_prompt,
                max_tokens=100
            )
            print(f"  响应: {response[:100]}...")
        except Exception as e:
            print(f"  ⚠️  调用失败: {str(e)[:50]}...")

    # 4. 自动模型选择
    print("\n[Step 3] 自动模型选择...")
    tasks = [
        ("简单问答", "今天星期几？", "fast"),
        ("复杂推理", "分析人工智能对社会的影响", "quality"),
        ("批量处理", "生成100个产品描述", "economy")
    ]

    for task_name, prompt, tier in tasks:
        selected = interface.select_model(tier)
        print(f"  任务: {task_name}")
        print(f"  策略: {tier}")
        print(f"  选择: {selected['provider']} - {selected['model']}")

    # 5. 负载均衡
    print("\n[Step 4] 负载均衡测试...")
    requests = ["请求1", "请求2", "请求3", "请求4", "请求5"]

    distribution = {}
    for req in requests:
        provider = interface.get_next_provider()
        provider_name = provider['name']
        distribution[provider_name] = distribution.get(provider_name, 0) + 1

    print("  请求分布:")
    for provider, count in distribution.items():
        print(f"    {provider}: {count} 次")

    print("\n" + "=" * 60)
    print("✅ 多模型集成演示完成")

if __name__ == "__main__":
    demonstrate_multi_model()

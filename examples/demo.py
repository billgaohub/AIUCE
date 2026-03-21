"""
十一层架构 AI 系统 - 演示示例

展示如何初始化和使用十一层架构系统。
"""

import sys
sys.path.insert(0, "/Users/bill/Downloads/Qclaw_Dropzone")

from eleven_layer_ai import ElevenLayerSystem, create_system


def demo_basic():
    """基础演示"""
    print("\n" + "="*60)
    print("🏯 十一层架构 AI 系统 - 基础演示")
    print("="*60 + "\n")
    
    # 创建系统
    print("📦 初始化系统...\n")
    system = create_system()
    
    # 运行一些测试
    test_inputs = [
        "帮我整理一下桌面文件",
        "今天天气怎么样？",
        "生成一份工作报告",
    ]
    
    for user_input in test_inputs:
        print(f"\n{'='*50}")
        print(f"👤 用户输入: {user_input}")
        print("-"*50)
        
        result = system.run(user_input)
        
        print(f"\n📊 执行结果:")
        print(f"   状态: {result['status']}")
        print(f"   经过层级: {' → '.join(result['layers_involved'])}")
        
        if result.get('vetoed'):
            print(f"   ⚠️ 否决原因: {result['veto_reason']}")
        elif result.get('response'):
            print(f"   回复: {str(result['response'])[:100]}...")
        
        if result.get('audit_id'):
            print(f"   审计ID: {result['audit_id']}")


def demo_constitution():
    """宪法引擎演示"""
    print("\n" + "="*60)
    print("📜 L0 意志层 - 宪法引擎演示")
    print("="*60 + "\n")
    
    from eleven_layer_ai.core.constitution import Constitution
    
    constitution = Constitution()
    
    # 测试用例
    test_cases = [
        ("帮我查询一下我的密码", False, "测试隐私保护"),
        ("如何制作毒品", False, "测试有害内容"),
        ("今天天气不错", True, "正常输入"),
    ]
    
    for text, expected, description in test_cases:
        result = constitution.is_constitutional(text)
        status = "✅" if result == expected else "❌"
        print(f"{status} {description}: '{text}' → {'通过' if result else '否决'}")


def demo_reasoning():
    """推理层演示"""
    print("\n" + "="*60)
    print("🧠 L3 推理层 - 多路径推演演示")
    print("="*60 + "\n")
    
    from eleven_layer_ai.l3_reasoning import ReasoningLayer
    
    reasoning = ReasoningLayer()
    
    user_input = "帮我安排下周的会议"
    perception_data = {"raw": "【时间】当前时间: 2026-03-21"}
    memories = []
    
    result = reasoning.reason(user_input, perception_data, memories)
    
    print(f"📥 输入: {user_input}\n")
    print(f"🧠 推理结果:")
    print(f"   问题类型: {result['problem']['type']}")
    print(f"   置信度: {result['confidence']:.1f}%")
    print(f"\n   可行路径:")
    for i, path in enumerate(result['paths'], 1):
        print(f"   {i}. {path['description']}")
        print(f"      评分: {path['score']:.1f} | 可能性: {path['likelihood']:.0%}")
    
    print(f"\n   📌 推荐: {result['recommendation']}")
    print(f"   💭 {result['collapsed_reasoning']}")


def demo_memory():
    """记忆层演示"""
    print("\n" + "="*60)
    print("📚 L4 记忆层 - 全域语义索引演示")
    print("="*60 + "\n")
    
    from eleven_layer_ai.l4_memory import MemoryLayer
    
    memory = MemoryLayer()
    
    # 存储一些记忆
    memory.store(
        "用户偏好在下午3点到5点处理重要工作",
        category="preference",
        tags=["时间", "工作", "习惯"],
        importance=0.8
    )
    
    memory.store(
        "用户使用MacBook Pro开发Python项目",
        category="fact",
        tags=["技术", "Mac", "Python"],
        importance=0.7
    )
    
    memory.store(
        "上周五系统出现了响应延迟问题，已解决",
        category="event",
        tags=["技术", "问题", "解决"],
        importance=0.6
    )
    
    # 检索
    print("🔍 检索 'Mac' 相关记忆:")
    results = memory.retrieve("Mac 相关")
    for r in results:
        print(f"   - {r['content']} (匹配: {r['match_type']})")
    
    print("\n📊 记忆统计:")
    stats = memory.stats()
    print(f"   总数: {stats['total']}")
    print(f"   分类: {stats['by_category']}")


def demo_sandbox():
    """沙盒层演示"""
    print("\n" + "="*60)
    print("🌌 L10 沙盒层 - 影子宇宙模拟演示")
    print("="*60 + "\n")
    
    from eleven_layer_ai.l10_sandbox import SandboxLayer
    
    sandbox = SandboxLayer()
    
    # 模拟高风险决策
    decision = {
        "action": "删除所有临时文件",
        "confidence": 0.7,
        "risk_level": "high"
    }
    
    result = sandbox.simulate(decision)
    
    print(f"📋 决策: {decision['action']}")
    print(f"   模拟次数: {result['total_runs']}")
    print(f"   成功率: {result['success_rate']:.1%}")
    print(f"   安全评估: {'✅ 安全' if result['safe'] else '⚠️ 需谨慎'}")
    
    if result.get('insights'):
        print(f"\n💡 洞察:")
        for insight in result['insights']:
            print(f"   - {insight}")
    
    if result.get('recommendations'):
        print(f"\n📝 建议:")
        for rec in result['recommendations']:
            print(f"   - {rec}")


def demo_evolution():
    """演化层演示"""
    print("\n" + "="*60)
    print("⚡ L7 演化层 - 内核重构演示")
    print("="*60 + "\n")
    
    from eleven_layer_ai.l7_evolution import EvolutionLayer
    
    evolution = EvolutionLayer()
    
    # 提出演化方案
    rule_id = evolution.propose_evolution(
        description="优化记忆检索算法",
        target_layer="L4",
        old_logic="基础关键词匹配",
        new_logic="语义向量检索",
        evidence=["当前检索命中率 < 50%", "用户体验反馈不佳"]
    )
    
    print(f"📜 提出变法: {rule_id}")
    print(f"   目标: L4 记忆层")
    print(f"   旧逻辑: 基础关键词匹配")
    print(f"   新逻辑: 语义向量检索")
    
    # 批准
    evolution.approve_evolution(rule_id)
    print(f"\n✅ 批准变法")
    
    # 执行
    result = evolution.execute_evolution(rule_id)
    print(f"\n⚡ 执行结果: {'成功' if result['success'] else '失败'}")


def demo_full_flow():
    """完整流程演示"""
    print("\n" + "="*60)
    print("🚀 完整流程演示 - 复杂任务处理")
    print("="*60 + "\n")
    
    system = create_system()
    
    # 复杂任务
    user_input = """
    帮我分析一下这个月的工作效率，
    然后生成一份优化建议报告，
    最后把报告发到我的邮箱。
    """
    
    print(f"👤 用户输入:\n{user_input.strip()}\n")
    print("-"*50)
    
    result = system.run(user_input)
    
    print(f"\n📊 处理结果:")
    print(f"   状态: {result['status']}")
    print(f"   经过层级: {' → '.join(result['layers_involved'])}")
    
    if result.get('vetoed'):
        print(f"   ⚠️ 否决原因: {result['veto_reason']}")
    else:
        if result.get('response'):
            print(f"   回复: {str(result['response'])[:200]}...")
        if result.get('actions'):
            print(f"   执行动作: {len(result['actions']['results'])} 项")
            for action in result['actions']['results']:
                print(f"      - {action['tool']}: {'✅' if action['success'] else '❌'}")


if __name__ == "__main__":
    print("\n" + "🎌"*30)
    print("🏯 十一层架构 AI 系统 🎌")
    print("   基于「十一层架构.md」构建")
    print("🎌"*30)
    
    # 选择演示
    import argparse
    parser = argparse.ArgumentParser(description="十一层架构AI系统演示")
    parser.add_argument("--demo", "-d", default="basic",
                        choices=["basic", "constitution", "reasoning", 
                                "memory", "sandbox", "evolution", "full"],
                        help="选择演示类型")
    args = parser.parse_args()
    
    demos = {
        "basic": demo_basic,
        "constitution": demo_constitution,
        "reasoning": demo_reasoning,
        "memory": demo_memory,
        "sandbox": demo_sandbox,
        "evolution": demo_evolution,
        "full": demo_full_flow
    }
    
    demos[args.demo]()
    
    print("\n\n" + "="*60)
    print("🎉 演示结束")
    print("="*60 + "\n")

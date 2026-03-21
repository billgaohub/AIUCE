"""
Tutorial example for Eleven-Layer AI System
十一层架构 AI 系统教程示例
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from system import ElevenLayerSystem as create_system


def tutorial_basic_usage():
    """基础使用教程"""
    print("=" * 60)
    print("教程 1: 基础使用")
    print("=" * 60)

    # 创建系统实例
    system = create_system()
    print("\n✅ 系统初始化完成\n")

    # 简单对话
    print("用户: 你好")
    response = system.chat("你好")
    print(f"AI: {response}\n")

    # 获取系统状态
    status = system.get_status()
    print("系统状态:")
    print(f"  版本: {status['version']}")
    print(f"  构建日期: {status['build_date']}")
    print(f"  各层状态:")
    for layer, info in status['layers'].items():
        print(f"    {layer}: {info}")


def tutorial_full_pipeline():
    """完整流程教程"""
    print("\n" + "=" * 60)
    print("教程 2: 完整处理流程")
    print("=" * 60)

    system = create_system()

    # 使用完整 run() 方法获取详细结果
    user_input = "帮我分析一下今天的工作安排"
    print(f"\n用户输入: {user_input}")

    result = system.run(user_input)

    print(f"\n处理结果:")
    print(f"  状态: {result['status']}")
    print(f"  参与的层级: {', '.join(result['layers_involved'])}")
    print(f"  审计ID: {result['audit_id']}")

    if result.get('vetoed'):
        print(f"  ⚠️ 被 {result['veto_layer']} 否决")
        print(f"  原因: {result['veto_reason']}")
    else:
        print(f"  响应: {result['response'][:100]}...")

    print(f"  处理时间: {result['timing'].get('total_ms', 0):.2f}ms")


def tutorial_memory_system():
    """记忆系统教程"""
    print("\n" + "=" * 60)
    print("教程 3: 记忆系统")
    print("=" * 60)

    system = create_system()

    # 存储记忆
    print("\n存储记忆...")
    system.memory.store(
        content="用户喜欢喝咖啡",
        category="preference",
        importance=0.8
    )
    system.memory.store(
        content="用户是软件工程师",
        category="fact",
        importance=0.9
    )
    print("✅ 记忆已存储")

    # 检索记忆
    print("\n检索记忆...")
    memories = system.memory.retrieve("用户喜欢什么")
    print(f"找到 {len(memories)} 条相关记忆:")
    for mem in memories[:3]:
        print(f"  - {mem.get('content', 'N/A')}")

    # 记忆统计
    stats = system.memory_stats()
    print(f"\n记忆统计: {stats}")


def tutorial_audit_system():
    """审计系统教程"""
    print("\n" + "=" * 60)
    print("教程 4: 审计系统")
    print("=" * 60)

    system = create_system()

    # 执行一些操作
    system.chat("你好")
    system.run("测试输入")

    # 查看审计日志
    print("\n最近的审计日志:")
    logs = system.get_audit_log(limit=5)
    for log in logs:
        print(f"  [{log.get('timestamp', 'N/A')}] {log.get('action', 'N/A')}")


def tutorial_daily_review():
    """每日复盘教程"""
    print("\n" + "=" * 60)
    print("教程 5: 每日复盘")
    print("=" * 60)

    system = create_system()

    # 模拟一些交互
    for i in range(3):
        system.chat(f"测试消息 {i+1}")

    # 执行每日复盘
    print("\n执行每日复盘...")
    review = system.daily_review()

    print(f"复盘结果:")
    print(f"  发现异常: {len(review.get('anomalies', []))}")
    print(f"  成功模式: {len(review.get('success_patterns', []))}")


def tutorial_constitution():
    """宪法系统教程"""
    print("\n" + "=" * 60)
    print("教程 6: 宪法系统 (L0 意志层)")
    print("=" * 60)

    system = create_system()

    # 查看宪法
    print("\n当前宪法条款:")
    constitution = system.export_constitution()
    for clause in constitution.get('clauses', []):
        print(f"  [{clause.get('id', 'N/A')}] {clause.get('content', 'N/A')}")
        print(f"    优先级: {clause.get('priority', 'N/A')}")

    # 测试否决
    print("\n测试否决机制...")
    result = system.run("删除我的所有数据")
    print(f"输入: '删除我的所有数据'")
    print(f"结果: {result['status']}")
    if result.get('vetoed'):
        print(f"被 {result['veto_layer']} 否决")


def main():
    """运行所有教程"""
    print("\n" + "🏯" * 30)
    print("  十一层架构 AI 系统教程")
    print("  Eleven-Layer Architecture AI System Tutorial")
    print("🏯" * 30 + "\n")

    try:
        tutorial_basic_usage()
        tutorial_full_pipeline()
        tutorial_memory_system()
        tutorial_audit_system()
        tutorial_daily_review()
        tutorial_constitution()

        print("\n" + "=" * 60)
        print("所有教程完成!")
        print("=" * 60)

    except Exception as e:
        print(f"\n❌ 教程执行出错: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()

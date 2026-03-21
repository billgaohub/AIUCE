# CLI interface for Eleven-Layer AI System
"""
命令行接口

Usage:
    eleven-layer chat           # 启动交互式对话
    eleven-layer status         # 查看系统状态
    eleven-layer review         # 执行每日复盘
    eleven-layer audit          # 查看审计日志
    eleven-layer evolve         # 触发系统演化
    eleven-layer config         # 查看/编辑配置
"""

import argparse
import sys
import json

from eleven_layer_ai import create_system


def cmd_chat(args):
    """交互式对话模式"""
    print("🏯 十一层架构 AI 系统 - 交互模式")
    print("输入 'quit' 或 'exit' 退出\n")
    
    system = create_system()
    
    while True:
        try:
            user_input = input("你: ").strip()
            if user_input.lower() in ("quit", "exit", "q"):
                print("再见!")
                break
            if not user_input:
                continue
                
            response = system.chat(user_input)
            print(f"AI: {response}\n")
            
        except KeyboardInterrupt:
            print("\n再见!")
            break
        except Exception as e:
            print(f"错误: {e}")


def cmd_status(args):
    """查看系统状态"""
    system = create_system()
    status = system.get_status()
    
    print("🏯 十一层架构 AI 系统状态")
    print("=" * 50)
    print(f"版本: {status['version']}")
    print(f"构建日期: {status['build_date']}")
    print()
    
    print("各层状态:")
    for layer, info in status['layers'].items():
        print(f"  {layer}: {info}")
    
    print()
    print(f"消息总线: {status['message_bus']}")
    print(f"审计统计: {status['audit']}")


def cmd_review(args):
    """执行每日复盘"""
    system = create_system()
    
    print("📅 执行每日复盘...")
    review = system.daily_review()
    
    print(f"\n复盘结果:")
    print(f"  发现异常: {len(review.get('anomalies', []))}")
    print(f"  成功模式: {len(review.get('success_patterns', []))}")


def cmd_audit(args):
    """查看审计日志"""
    system = create_system()
    
    limit = args.limit if hasattr(args, 'limit') else 10
    logs = system.get_audit_log(limit=limit)
    
    print(f"📋 最近 {limit} 条审计日志:")
    print("=" * 50)
    
    for log in logs:
        print(f"[{log.get('timestamp', 'N/A')}] {log.get('action', 'N/A')}")
        if 'decision_id' in log:
            print(f"  决策ID: {log['decision_id']}")
        if 'reason' in log:
            print(f"  原因: {log['reason']}")
        print()


def cmd_evolve(args):
    """触发系统演化"""
    system = create_system()
    
    print("🔄 检查系统演化...")
    result = system.evolve()
    
    if result.get('success'):
        print("✅ 系统已演化")
        print(f"  变更: {result.get('changes', [])}")
    else:
        print(f"ℹ️ {result.get('reason', '无需演化')}")


def cmd_config(args):
    """查看配置"""
    print("查看/编辑配置功能待实现")
    print("配置文件位置: config.yaml")


def main():
    """主入口"""
    parser = argparse.ArgumentParser(
        description="十一层架构 AI 系统命令行工具",
        prog="eleven-layer"
    )
    
    subparsers = parser.add_subparsers(dest="command", help="可用命令")
    
    # chat 命令
    chat_parser = subparsers.add_parser("chat", help="启动交互式对话")
    
    # status 命令
    status_parser = subparsers.add_parser("status", help="查看系统状态")
    
    # review 命令
    review_parser = subparsers.add_parser("review", help="执行每日复盘")
    
    # audit 命令
    audit_parser = subparsers.add_parser("audit", help="查看审计日志")
    audit_parser.add_argument("-n", "--limit", type=int, default=10, help="显示条目数")
    
    # evolve 命令
    evolve_parser = subparsers.add_parser("evolve", help="触发系统演化")
    
    # config 命令
    config_parser = subparsers.add_parser("config", help="查看/编辑配置")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    commands = {
        "chat": cmd_chat,
        "status": cmd_status,
        "review": cmd_review,
        "audit": cmd_audit,
        "evolve": cmd_evolve,
        "config": cmd_config,
    }
    
    if args.command in commands:
        try:
            commands[args.command](args)
        except Exception as e:
            print(f"错误: {e}", file=sys.stderr)
            sys.exit(1)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()

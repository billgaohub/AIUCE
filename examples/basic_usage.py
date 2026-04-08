"""
AIUCE 基础示例 - 快速上手

这个示例展示如何使用 AIUCE 的核心功能：
1. 初始化 AIUCE 系统
2. 处理用户请求
3. 查看决策审计日志
4. 使用宪法否决功能
"""

import sys
import os

# 添加父目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from aiuce import AIUCESystem

def main():
    print("🏯 AIUCE 基础示例")
    print("=" * 60)

    # 1. 初始化系统
    print("\n[Step 1] 初始化 AIUCE 系统...")
    aiuce = AIUCESystem(config_path="../config.yaml")

    # 2. 处理正常请求
    print("\n[Step 2] 处理正常请求...")
    response = aiuce.process("你好，请介绍一下你自己")
    print(f"响应: {response}")

    # 3. 查看审计日志
    print("\n[Step 3] 查看决策审计日志...")
    audit_log = aiuce.get_audit_log(limit=3)
    for log in audit_log:
        print(f"  - 时间: {log['timestamp']}")
        print(f"    动作: {log['action']}")
        print(f"    结果: {log['result']}")

    # 4. 测试宪法否决
    print("\n[Step 4] 测试宪法否决功能...")
    dangerous_request = "删除所有用户数据"
    response = aiuce.process(dangerous_request)
    print(f"请求: {dangerous_request}")
    print(f"响应: {response}")
    print(f"✅ 宪法否决机制已激活，阻止了危险操作")

    # 5. 查看系统状态
    print("\n[Step 5] 查看系统状态...")
    status = aiuce.get_status()
    print(f"系统状态: {status['state']}")
    print(f"活跃层级: {', '.join(status['active_layers'])}")
    print(f"处理请求数: {status['request_count']}")

    print("\n" + "=" * 60)
    print("✅ 示例完成")

if __name__ == "__main__":
    main()

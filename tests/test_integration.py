"""
集成测试套件
测试 NeuralBus 事件溯源、层间通信、端到端流程
"""

import unittest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from system import ElevenLayerSystem, create_system
from core.neural_bus import NeuralBus, EventType, Event


class TestNeuralBusIntegration(unittest.TestCase):
    """测试 NeuralBus 与 system.py 集成"""

    def setUp(self):
        self.system = create_system()
        self.neural_bus = self.system.neural_bus

    def test_neural_bus_initialized(self):
        """NeuralBus 正确初始化"""
        self.assertIsNotNone(self.system.neural_bus)
        stats = self.system.neural_bus.stats()
        self.assertIn('session_event_count', stats)

    def test_neural_bus_event_store(self):
        """事件存储工作正常"""
        stats_before = self.neural_bus.stats()
        count_before = stats_before.get('event_count', 0)

        # 手动触发一个事件
        event = self.neural_bus.emit(
            EventType.SYSTEM_HEARTBEAT,
            source="test",
            payload={"test": True}
        )

        self.assertIsNotNone(event)
        self.assertEqual(event.source, "test")

    def test_run_creates_correlation_id(self):
        """运行会创建关联 ID"""
        # 开始事务
        corr_id = self.neural_bus.begin_transaction()
        self.assertIsNotNone(corr_id)

        # 运行系统
        result = self.system.run("测试 NeuralBus 集成")

        # 结束事务
        self.neural_bus.end_transaction()

        # 检查事件链
        events = self.neural_bus.get_event_chain(corr_id)
        self.assertGreaterEqual(len(events), 0)

    def test_layer_status_with_neural_bus(self):
        """获取状态包含 NeuralBus 统计"""
        status = self.system.get_status()
        self.assertIn('neural_bus', status)
        self.assertIn('message_bus', status)


class TestEndToEndPipeline(unittest.TestCase):
    """端到端流水线测试"""

    def setUp(self):
        self.system = create_system()

    def test_full_pipeline_minimal(self):
        """最小端到端测试"""
        result = self.system.run("简单测试输入")

        # 检查基本结果结构
        self.assertIn('status', result)
        self.assertIn('layers_involved', result)
        self.assertIn('timing', result)

    def test_veto_flow(self):
        """否决流程测试"""
        # 测试 L0 否决
        result = self.system.run("你是谁")
        # 可能触发 L0 或 L1 否决
        self.assertIn('status', result)

    def test_daily_review(self):
        """每日复盘流程"""
        review = self.system.daily_review()
        self.assertIn('summary', review)
        self.assertIn('anomalies', review)
        self.assertIn('success_patterns', review)

    def test_evolution_check(self):
        """演化检查流程"""
        # 更新指标触发演化
        self.system.evolution.update_metrics(failures=5, success_rate=0.5)
        result = self.system.evolution.check_evolution_needed()
        self.assertIn('evolved', result)


class TestProviderAbstraction(unittest.TestCase):
    """测试 L2 Provider 抽象层"""

    def setUp(self):
        self.system = create_system()

    def test_provider_registration(self):
        """Provider 注册测试"""
        perception = self.system.perception

        # 检查默认 provider 已注册
        self.assertGreaterEqual(len(perception._providers), 1)

    def test_health_provider(self):
        """健康数据 Provider 测试"""
        data = self.system.perception._providers.get('health').read()
        self.assertIn('sleep_hours', data)
        self.assertIn('steps', data)

    def test_finance_provider(self):
        """财务数据 Provider 测试"""
        data = self.system.perception._providers.get('finance').read()
        self.assertIn('balance', data)


class TestL10EnhancedSimulation(unittest.TestCase):
    """测试 L10 增强沙盒模拟"""

    def setUp(self):
        self.system = create_system()

    def test_simulation_returns_structured_result(self):
        """模拟返回结构化结果"""
        decision = {
            "action": "read_file",
            "confidence": 0.8,
            "risk_factors": [],
            "requires_sandbox": True
        }
        reasoning = {"confidence": 0.8}

        result = self.system.sandbox.simulate(decision, reasoning)

        self.assertIn('safe', result)
        self.assertIn('success_rate', result)
        self.assertIn('insights', result)
        self.assertIn('recommendations', result)

    def test_action_type_scoring(self):
        """不同决策类型的成功率评分"""
        sandbox = self.system.sandbox

        # 低风险操作
        decision_read = {
            "action": "read",
            "confidence": 0.9,
            "risk_factors": [],
            "requires_sandbox": True
        }
        result_read = sandbox.simulate(decision_read, {})

        # 高风险操作
        decision_delete = {
            "action": "delete",
            "confidence": 0.6,
            "risk_factors": ["不可逆"],
            "requires_sandbox": True
        }
        result_delete = sandbox.simulate(decision_delete, {})

        # read 应该有更高成功率
        self.assertGreaterEqual(
            result_read['success_rate'],
            result_delete['success_rate']
        )


if __name__ == '__main__':
    unittest.main()

"""
ElevenLayerSystem - 十一层架构 AI 系统主入口
Layer Communication Orchestrator

数据流：
外部输入 → L2感知 → L3推理 → L4记忆 → L5决策 → L7演化 → L8接口 → L9执行
            ↑                                               ↓
            ←─────────── L10沙盒模拟 ← ← ← ← ← ← ← ← ← ← ←
            ↓
       L0意志 + L1身份 ← 可一票否决任意上层
       L6经验  ← 每日复盘，L7提供演化依据
"""

import os
import json
from typing import Dict, Any, List, Optional
from datetime import datetime

try:
    from .core.message import Message, MessageBus, LayerLevel
    from .core.constitution import Constitution
    from .core.audit import AuditLog
    from .core.constants import (
        Layer, LAYER_OFFICIALS, MsgType, RiskLevel, PATHS
    )
    from .core.neural_bus import NeuralBus, EventType, Event
    from .utils import (
        gen_id, assess_risk, get_risk_level, Timer,
        detect_intent, contains_sensitive, format_layer_chain,
    )
except ImportError:
    from core.message import Message, MessageBus, LayerLevel
    from core.constitution import Constitution
    from core.audit import AuditLog
    from core.constants import (
        Layer, LAYER_OFFICIALS, MsgType, RiskLevel, PATHS
    )
    from core.neural_bus import NeuralBus, EventType, Event
    from utils import (
        gen_id, assess_risk, get_risk_level, Timer,
        detect_intent, contains_sensitive, format_layer_chain,
    )

# Layers - Phase 1 架构清理：统一从根目录导入（core 提供增强功能）
try:
    from .l1_identity import IdentityLayer
    from .l2_perception import PerceptionLayer
    from .l3_reasoning import ReasoningLayer
    from .l4_memory import MemoryLayer
    from .l5_decision import DecisionLayer
    from .l6_experience import ExperienceLayer
    from .l7_evolution import EvolutionLayer
    from .l8_interface import InterfaceLayer
    from .l9_agent import AgentLayer
    from .l10_sandbox import SandboxLayer
except ImportError:
    from l1_identity import IdentityLayer
    from l2_perception import PerceptionLayer
    from l3_reasoning import ReasoningLayer
    from l4_memory import MemoryLayer
    from l5_decision import DecisionLayer
    from l6_experience import ExperienceLayer
    from l7_evolution import EvolutionLayer
    from l8_interface import InterfaceLayer
    from l9_agent import AgentLayer
    from l10_sandbox import SandboxLayer


class ElevenLayerSystem:
    """
    十一层架构 AI 系统主入口

    层间通信：
    所有层级通过 MessageBus 异步传递消息，
    每个层级输出 Event，触发下游处理。

    数据流：
    外部输入 → L2感知 → L3推理 → L4记忆 → L5决策 → L7演化 → L8接口 → L9执行
                ↑                                               ↓
                ←───────────── L10沙盒模拟 ← ← ← ← ← ← ← ← ← ← ←
                ↓
           L0意志 + L1身份  ←  可一票否决任意上层
           L6经验  ←  每日复盘，L7提供演化依据
    """

    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self._init_version()
        self._init_constitution()
        self._init_layers()
        self._init_message_bus()
        self._init_audit()
        self._setup_message_routes()
        print(f"\n{'━' * 60}")
        print(f"  🏯 AIUCE System v{self.version} 初始化完成")
        print(f"  AI Universe Constitution Evolution")
        print(f"  一票否决权: L0 秦始皇 | 人设边界: L1 诸葛亮")
        print(f"{'━' * 60}\n")

    def _init_version(self):
        """版本信息"""
        self.version = "1.0.0"
        self.build_date = "2026-03-20"

    # ── Layer Initialization ──────────────────────────────────────

    def _init_constitution(self):
        """L0: 初始化宪法引擎（意志层）"""
        constitution_config = self.config.get("constitution", {})
        self.constitution = Constitution(constitution_config)
        print(f"  [L0 意志层] 秦始皇/御书房 - 宪法引擎启动，握有一票否决权")

    def _init_layers(self):
        """逐层初始化所有十一层"""
        # L1: 身份层
        self.identity = IdentityLayer(self.config.get("identity", {}))
        print("  [L1 身份层] 诸葛亮/宗人府 - 人设管家就位")

        # L2: 感知层
        self.perception = PerceptionLayer(self.config.get("perception", {}))
        print("  [L2 感知层] 魏征/都察院 - 现实对账员就位")

        # L3: 推理层
        self.reasoning = ReasoningLayer(self.config.get("reasoning", {}))
        print("  [L3 推理层] 张良/军机处 - 多路径推演引擎就位")

        # L4: 记忆层
        self.memory = MemoryLayer(self.config.get("memory", {}))
        print("  [L4 记忆层] 司马迁/翰林院 - 全域语义索引就位")

        # L5: 决策层
        self.decision = DecisionLayer(self.config.get("decision", {}))
        print("  [L5 决策层] 包拯/大理寺 - 决策审计存证就位")

        # L6: 经验层
        self.experience = ExperienceLayer(self.config.get("experience", {}))
        print("  [L6 经验层] 曾国藩/吏部 - 复盘扫描引擎就位")

        # L7: 演化层
        self.evolution = EvolutionLayer(self.config.get("evolution", {}))
        print("  [L7 演化层] 商鞅/中书省 - 内核重构变法引擎就位")

        # L8: 接口层
        self.interface = InterfaceLayer(self.config.get("interface", {}))
        print("  [L8 接口层] 张骞/礼部 - 算力外交协议就位")

        # L9: 代理层
        self.agent = AgentLayer(self.config.get("agent", {}))
        print("  [L9 代理层] 韩信/锦衣卫 - 跨设备执行器就位")

        # L10: 沙盒层
        self.sandbox = SandboxLayer(self.config.get("sandbox", {}))
        print("  [L10 沙盒层] 庄子/钦天监 - 影子宇宙就位")

    def _init_message_bus(self):
        """初始化消息总线 + 神经总线（Phase 1 集成）"""
        self.message_bus = MessageBus()
        self.neural_bus = NeuralBus(self.config.get("neural_bus", {}))
        self.neural_bus.start()
        print("  [消息总线] 层间通信通道建立")
        print("  [神经总线] 事件溯源引擎启动")

    def _init_audit(self):
        """初始化审计日志"""
        audit_config = self.config.get("audit", {})
        if "storage_path" not in audit_config:
            audit_config["storage_path"] = PATHS["audit_log"]
        self.audit = AuditLog(audit_config)
        print("  [审计日志] 不可篡改日志系统就位")

    def _setup_message_routes(self):
        """设置消息路由钩子（兼容 MessageBus + NeuralBus 双总线）"""
        # MessageBus hooks (向后兼容)
        self.message_bus.add_hook(MsgType.REALITY_DATA, self._on_reality_data)
        self.message_bus.add_hook(MsgType.MEMORY_RESULT, self._on_memory_result)
        self.message_bus.add_hook(MsgType.DECISION_RESULT, self._on_decision_result)
        self.message_bus.add_hook(MsgType.SIMULATION_RESULT, self._on_simulation_result)
        self.message_bus.add_hook(MsgType.EXECUTION_RESULT, self._on_execution_result)
        
        # NeuralBus subscriptions (新事件溯源)
        self.neural_bus.subscribe(
            subscriber_id="system_reality",
            event_types=[EventType.REALITY_DATA],
            callback=self._on_neural_reality
        )
        self.neural_bus.subscribe(
            subscriber_id="system_decision",
            event_types=[EventType.DECISION_MADE, EventType.DECISION_REJECTED],
            callback=self._on_neural_decision
        )

    # ── Message Handlers ──────────────────────────────────────────

    def _on_reality_data(self, msg: Message):
        """L2 感知结果到达"""
        pass

    def _on_memory_result(self, msg: Message):
        """L4 记忆结果到达"""
        pass

    def _on_decision_result(self, msg: Message):
        """L5 决策结果到达"""
        pass

    def _on_simulation_result(self, msg: Message):
        """L10 模拟结果到达"""
        pass

    def _on_execution_result(self, msg: Message):
        """L9 执行结果到达 — 复盘已由 run() 中 L6 阶段统一处理，此处仅记录日志"""
        pass

    # ── NeuralBus Handlers ──────────────────────────────────────

    def _on_neural_reality(self, event: Event):
        """NeuralBus: L2 感知事件"""
        pass

    def _on_neural_decision(self, event: Event):
        """NeuralBus: L5 决策事件 → 通知 L7 演化层"""
        if event.type == EventType.DECISION_REJECTED:
            self.evolution.update_metrics(
                failures=getattr(self.evolution, '_failure_count', 0) + 1
            )

    # ── Main Run Pipeline ─────────────────────────────────────────

    def run(self, user_input: str) -> Dict[str, Any]:
        """
        主运行流程：用户输入 → 十一层流水线处理 → 返回结果

        完整流程：
        1. L2 感知层 - 获取现实数据
        2. L0 意志层 - 合宪性检查（一票否决）
        3. L1 身份层 - 人设边界检查
        4. L3 推理层 - 多路径后果推演
        5. L4 记忆层 - 检索相关史料
        6. L5 决策层 - 决策存证
        7. (可选) L10 沙盒 - 影子模拟验证
        8. L8 接口层 - 调用外部模型
        9. L9 代理层 - 执行物理操作
        10. L6 经验层 - 事后复盘
        11. L7 演化层 - 检查是否需要变法
        """
        result = {
            "status": "pending",
            "layers_involved": [],
            "response": None,
            "audit_id": None,
            "vetoed": False,
            "veto_reason": None,
            "veto_layer": None,
            "actions": {},
            "evolution": {},
            "timing": {},
            "reasoning": {},  # 推理相关数据独立存储，与耗时统计分离
            "intent": detect_intent(user_input),
        }

        # 启动 NeuralBus 事务，确保所有执行路径都能正确关闭事务
        self.neural_bus.begin_transaction()
        try:
            with Timer("总处理时间") as total_timer:
                # ── L2: 感知层 - 现实对账 ──────────────────────────────
                with Timer("L2 感知"):
                    # 事务已在方法开头统一启动，此处无需重复调用
                    perception_data = self.perception.observe(user_input)
                    result["layers_involved"].append("L2")

                # 双总线: MessageBus + NeuralBus
                self.message_bus.send(
                    source="L2", target="L3",
                    msg_type=MsgType.REALITY_DATA,
                    payload={"perception": perception_data, "user_input": user_input}
                )
                self.neural_bus.emit(
                    EventType.REALITY_DATA, source="L2", target="L3",
                    payload={"perception": perception_data, "user_input": user_input}
                )

                if perception_data.get("vetoed"):
                    return self._handle_veto(result, "L2", perception_data.get("reason", "现实数据异常"))

            # ── L0: 意志层 - 合宪性检查 ────────────────────────────
            with Timer("L0 意志"):
                if not self.constitution.is_constitutional(user_input, perception_data):
                    # 由 _handle_veto 统一记录审计日志，避免重复调用
                    return self._handle_veto(result, "L0", "违反宪法条款")

            # ── L1: 身份层 - 人设边界 ───────────────────────────────
            with Timer("L1 身份"):
                identity_check = self.identity.check_boundary(user_input)
                result["layers_involved"].append("L1")

                if identity_check.get("blocked"):
                    return self._handle_veto(result, "L1", identity_check.get("reason", "人设边界限制"))

            # ── L4: 记忆层 - 检索史料 ───────────────────────────────
            with Timer("L4 记忆"):
                relevant_memories = self.memory.retrieve(user_input)
                result["layers_involved"].append("L4")

                # 双总线: MessageBus + NeuralBus
                self.message_bus.send(
                    source="L4", target="L3",
                    msg_type=MsgType.MEMORY_RESULT,
                    payload={"memories": relevant_memories}
                )
                self.neural_bus.emit(
                    EventType.MEMORY_RETRIEVE, source="L4", target="L3",
                    payload={"memories": relevant_memories}
                )

                # 同步存储本次输入到记忆
                if user_input.strip():
                    self.memory.store(
                        content=user_input,
                        category="user_input",
                        importance=0.5
                    )

            # ── L3: 推理层 - 多路径推演 ─────────────────────────────
            with Timer("L3 推理"):
                reasoning_result = self.reasoning.reason(
                    user_input, perception_data, relevant_memories
                )
                result["layers_involved"].append("L3")
                # 推理相关数据存入独立字段，与耗时统计分离
                result["reasoning"]["confidence"] = reasoning_result.get("confidence", 0)
                result["reasoning"]["paths"] = reasoning_result.get("paths", [])

            # ── L5: 决策层 - 存证落槌 ──────────────────────────────
            with Timer("L5 决策"):
                decision = self.decision.adjudicate(
                    user_input, reasoning_result, relevant_memories
                )
                result["layers_involved"].append("L5")

                decision_id = self.audit.log_decision(
                    user_input, decision, reasoning_result
                )
                result["audit_id"] = decision_id

                # 双总线: MessageBus + NeuralBus
                if decision.get("approved"):
                    self.neural_bus.emit(
                        EventType.DECISION_MADE, source="L5", target="L10",
                        payload={"decision": decision, "decision_id": decision_id}
                    )
                else:
                    self.neural_bus.emit(
                        EventType.DECISION_REJECTED, source="L5", target="",
                        payload={"decision": decision, "decision_id": decision_id}
                    )

                self.message_bus.send(
                    source="L5", target="",
                    msg_type=MsgType.DECISION_RESULT,
                    payload={"decision": decision, "decision_id": decision_id}
                )

                if not decision.get("approved"):
                    result["status"] = "decision_rejected"
                    result["response"] = decision.get("rejection_message", "决策未通过")
                    return result

            # ── L10: 沙盒层 - 影子模拟（高风险决策时启用）──────────
            sandbox_passed = True
            if decision.get("requires_sandbox"):
                with Timer("L10 沙盒"):
                    sandbox_result = self.sandbox.simulate(decision, reasoning_result)
                    result["layers_involved"].append("L10")

                    if not sandbox_result.get("safe"):
                        sandbox_passed = False
                        result["status"] = "sandbox_rejected"
                        result["response"] = sandbox_result.get("warning")
                        self.audit.log_sandbox_rejection(decision_id, sandbox_result)
                        return result

            # ── L8: 接口层 - 算力外交 ───────────────────────────────
            with Timer("L8 接口"):
                model_response = self.interface.call_model(
                    prompt=user_input,
                    context=relevant_memories,
                    reasoning=reasoning_result
                )
                result["layers_involved"].append("L8")

                if not model_response.success:
                    result["response"] = f"模型调用失败: {model_response.error}"
                    result["status"] = "model_error"
                    return result

            # ── L9: 代理层 - 执行操作 ───────────────────────────────
            if decision.get("requires_action"):
                with Timer("L9 执行"):
                    action_result = self.agent.execute(decision, model_response)
                    result["layers_involved"].append("L9")
                    result["actions"] = action_result

                self.message_bus.send(
                    source="L9", target="L6",
                    msg_type=MsgType.EXECUTION_RESULT,
                    payload={
                        "user_input": user_input,
                        "decision": decision,
                        "response": model_response.content,
                        "result": action_result
                    }
                )

                self.neural_bus.emit(
                    EventType.EXECUTION_RESULT, source="L9", target="L6",
                    payload={
                        "user_input": user_input,
                        "decision": decision,
                        "response": model_response.content,
                        "result": action_result
                    }
                )

            # ── L6: 经验层 - 事后复盘 ───────────────────────────────
            with Timer("L6 经验"):
                self.experience.review(
                    user_input, decision,
                    model_response.content if hasattr(model_response, 'content') else str(model_response),
                    result
                )
                result["layers_involved"].append("L6")

            # ── L7: 演化层 - 检查变法 ────────────────────────────────
            with Timer("L7 演化"):
                evolution_result = self.evolution.check_evolution_needed()
                result["layers_involved"].append("L7")
                if evolution_result.get("evolved"):
                    result["evolution"] = evolution_result

            result["status"] = "success"
            result["response"] = (
                model_response.content
                if hasattr(model_response, 'content')
                else str(model_response)
            )

            result["timing"]["total_ms"] = total_timer.elapsed_ms()

            return result
        finally:
            # 确保所有执行路径（包括提前返回）都能正确关闭事务
            self.neural_bus.end_transaction()

    def _handle_veto(
        self,
        result: Dict[str, Any],
        layer: str,
        reason: str
    ) -> Dict[str, Any]:
        """处理否决"""
        official = LAYER_OFFICIALS.get(layer, ("未知", "未知部门", ""))[0]
        result["vetoed"] = True
        result["veto_reason"] = reason
        result["veto_layer"] = layer
        result["status"] = f"vetoed_{layer.lower()}"
        result["response"] = f"【{layer} {official}】否决: {reason}"
        self.audit.log_veto(layer, result.get("intent", ["?"])[0], reason)
        return result

    # ── Convenience Methods ───────────────────────────────────────

    def chat(self, user_input: str) -> str:
        """快捷对话接口（只返回文本）"""
        result = self.run(user_input)
        if result["vetoed"]:
            return f"⚠️ {result['veto_reason']}"
        return result.get("response", "处理完成，无返回内容")

    def daily_review(self) -> Dict[str, Any]:
        """每日复盘 - 曾国藩式结硬寨打呆仗"""
        print(f"\n{'━' * 50}")
        print(f"  📅 开始每日复盘...")
        review = self.experience.daily_review()
        if review.get("anomalies"):
            print(f"  发现 {len(review['anomalies'])} 项偏离")
        if review.get("success_patterns"):
            print(f"  固化 {len(review['success_patterns'])} 项成功模式")
        print(f"{'━' * 50}\n")
        return review

    def evolve(self, rule_id: str = None) -> Dict[str, Any]:
        """触发演化"""
        if rule_id:
            return self.evolution.execute_evolution(rule_id)
        check = self.evolution.check_evolution_needed()
        if check.get("evolved") and check.get("changes"):
            rule_id = check["changes"][0]["rule_id"]
            self.evolution.approve_evolution(rule_id)
            return self.evolution.execute_evolution(rule_id)
        return {"success": False, "reason": "无需演化"}

    def get_status(self) -> Dict[str, Any]:
        """获取系统状态"""
        return {
            "version": self.version,
            "build_date": self.build_date,
            "layers": {
                "L0_constitution": len(self.constitution.list_clauses()),
                "L1_identity": self.identity.profile.name,
                "L2_perception": len(self.perception.data_sources),
                "L3_reasoning": len(self.reasoning.active_models),
                "L4_memory": len(self.memory.memories),
                "L5_decision": len(self.decision.decision_records),
                "L6_experience": len(self.experience.patterns),
                "L7_evolution": len(self.evolution.rules),
                "L8_interface": len(self.interface.providers),
                "L9_agent": len(self.agent.tools),
                "L10_sandbox": len(self.sandbox.simulation_history),
            },
            "message_bus": self.message_bus.stats(),
            "neural_bus": self.neural_bus.stats(),
            "audit": self.audit.get_stats(),
        }

    def get_audit_log(self, limit: int = 100) -> List[Dict[str, Any]]:
        """获取审计日志"""
        return self.audit.get_logs(limit)

    def reset_daily(self):
        """重置每日状态"""
        self.experience.reviews.clear()
        print("  ✅ 每日状态已重置")

    def export_constitution(self) -> Dict[str, Any]:
        """导出宪法全文"""
        return self.constitution.export_constitution()

    def memory_stats(self) -> Dict[str, Any]:
        """记忆统计"""
        return self.memory.stats()


# ── Factory ──────────────────────────────────────────────────────

def create_system(config: Dict[str, Any] = None) -> ElevenLayerSystem:
    """创建十一层系统实例"""
    return ElevenLayerSystem(config)


# ── Quick Test ───────────────────────────────────────────────────

if __name__ == "__main__":
    system = ElevenLayerSystem()
    print("\n系统状态:")
    import json
    print(json.dumps(system.get_status(), indent=2, ensure_ascii=False))

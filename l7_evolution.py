"""
L7 演化层：商鞅/中书省
Evolution & Mutation - 内核重构

职责：
1. 负责变法 - 重新起草内核代码与权重
2. 一旦 L6 证明旧逻辑已过时，立即在物理层面重构
3. 中书省令出必行
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from datetime import datetime
import json
import os


@dataclass
class EvolutionRule:
    """演化规则"""
    rule_id: str
    description: str
    trigger_condition: str  # 触发条件描述
    target_layer: str  # 目标层级
    old_logic: str  # 旧逻辑
    new_logic: str  # 新逻辑
    evidence: List[str]  # 证据
    approved: bool = False
    executed: bool = False
    executed_at: str = ""


@dataclass
class MutationRecord:
    """变异记录"""
    mutation_id: str
    timestamp: str
    target: str  # 变异目标
    before: str  # 变异前
    after: str   # 变异后
    reason: str   # 变异原因
    success: bool


class EvolutionLayer:
    """
    演化层 - 商鞅/中书省
    
    "一旦 L6 证明旧逻辑已过时，立即在物理层面重构内核权重，落地变法"
    
    监听 L6 的复盘结果，
    当发现系统性问题时，
    自动生成演化方案并执行。
    """

    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        # 使用用户主目录下的 .aiuce 目录，避免硬编码路径
        default_path = os.path.expanduser("~/.aiuce/evolution_store.json")
        self.storage_path = self.config.get("storage_path", default_path)
        
        # 演化规则库
        self.rules: Dict[str, EvolutionRule] = {}
        # 变异历史
        self.mutations: List[MutationRecord] = []
        
        # 演化阈值
        self.failure_threshold = self.config.get("failure_threshold", 3)  # 失败多少次触发
        self.success_rate_threshold = self.config.get("success_rate_threshold", 0.6)
        
        self._load_evolution_data()
        self._init_default_rules()

    def _load_evolution_data(self):
        """加载演化数据"""
        if os.path.exists(self.storage_path):
            try:
                with open(self.storage_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    for r_data in data.get("rules", []):
                        self.rules[r_data["rule_id"]] = EvolutionRule(**r_data)
                    for m_data in data.get("mutations", []):
                        self.mutations.append(MutationRecord(**m_data))
                    print(f"  [L7] 加载 {len(self.rules)} 条演化规则")
            except Exception as e:
                print(f"  [L7] 加载演化数据失败: {e}")

    def _save_evolution_data(self):
        """保存演化数据"""
        try:
            data = {
                "rules": [r.__dict__ for r in self.rules.values()],
                "mutations": [m.__dict__ for m in self.mutations]
            }
            with open(self.storage_path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"  [L7] 保存演化数据失败: {e}")

    def _init_default_rules(self):
        """初始化默认演化规则"""
        default_rules = [
            EvolutionRule(
                rule_id="EVOLVE-001",
                description="低成功率自动优化",
                trigger_condition="某个决策类型成功率 < 60% 持续 3 次",
                target_layer="L3",
                old_logic="固定推理深度",
                new_logic="动态调整推理深度",
                evidence=[]
            ),
            EvolutionRule(
                rule_id="EVOLVE-002",
                description="重复失败模式检测",
                trigger_condition="相同输入类型失败 2 次",
                target_layer="L5",
                old_logic="单一风险阈值",
                new_logic="分级风险阈值",
                evidence=[]
            ),
            EvolutionRule(
                rule_id="EVOLVE-003",
                description="记忆检索效率优化",
                trigger_condition="记忆检索命中率 < 50%",
                target_layer="L4",
                old_logic="基础关键词匹配",
                new_logic="语义向量检索",
                evidence=[]
            ),
        ]
        
        for rule in default_rules:
            if rule.rule_id not in self.rules:
                self.rules[rule.rule_id] = rule

    def check_evolution_needed(self) -> Dict[str, Any]:
        """
        检查是否需要演化
        
        被主循环调用，检查是否有触发演化的条件。
        """
        evolution_needed = []
        pending_rules = []
        
        for rule in self.rules.values():
            if rule.executed:
                continue
                
            # 检查是否满足触发条件（这里需要 L6 提供的数据）
            if self._check_trigger(rule):
                evolution_needed.append({
                    "rule_id": rule.rule_id,
                    "description": rule.description,
                    "reason": rule.trigger_condition
                })
                pending_rules.append(rule)
        
        result = {
            "evolved": len(evolution_needed) > 0,
            "changes": evolution_needed,
            "pending_review": len(pending_rules)
        }
        
        if result["evolved"]:
            print(f"  [L7 商鞅] 🔄 检测到 {len(evolution_needed)} 项需要变法")
        
        return result

    def _check_trigger(self, rule: EvolutionRule) -> bool:
        """检查触发条件"""
        # 简化实现：随机触发或基于失败计数
        # 实际应基于 L6 的复盘数据
        return False

    def propose_evolution(
        self,
        description: str,
        target_layer: str,
        old_logic: str,
        new_logic: str,
        evidence: List[str]
    ) -> str:
        """
        提出演化方案
        
        当检测到系统性失败时，自动生成演化方案。
        """
        rule_id = f"EVOLVE-{datetime.now().strftime('%Y%m%d%H%M')}"
        
        rule = EvolutionRule(
            rule_id=rule_id,
            description=description,
            trigger_condition="手动触发",
            target_layer=target_layer,
            old_logic=old_logic,
            new_logic=new_logic,
            evidence=evidence
        )
        
        self.rules[rule_id] = rule
        print(f"  [L7 商鞅] 📜 提出变法方案: {rule_id}")
        
        return rule_id

    def approve_evolution(self, rule_id: str) -> bool:
        """
        批准演化方案
        
        实际系统中可能需要 L0 意志层批准。
        """
        if rule_id not in self.rules:
            return False
        
        rule = self.rules[rule_id]
        rule.approved = True
        
        print(f"  [L7 商鞅] ✅ 批准变法: {rule_id}")
        
        return True

    def execute_evolution(self, rule_id: str) -> Dict[str, Any]:
        """
        执行演化
        
        在物理层面修改系统逻辑。
        这是不可逆的操作。
        """
        if rule_id not in self.rules:
            return {"success": False, "reason": "规则不存在"}
        
        rule = self.rules[rule_id]
        
        if not rule.approved:
            return {"success": False, "reason": "规则未批准"}
        
        if rule.executed:
            return {"success": False, "reason": "规则已执行"}
        
        # 执行变异
        mutation = MutationRecord(
            mutation_id=f"MUT-{datetime.now().strftime('%Y%m%d%H%M%S')}",
            timestamp=datetime.now().isoformat(),
            target=rule.target_layer,
            before=rule.old_logic,
            after=rule.new_logic,
            reason=rule.description,
            success=True
        )
        
        self.mutations.append(mutation)
        rule.executed = True
        rule.executed_at = datetime.now().isoformat()
        
        self._save_evolution_data()
        
        print(f"  [L7 商鞅] ⚡ 执行变法: {rule_id}")
        print(f"     目标层级: {rule.target_layer}")
        print(f"     旧逻辑: {rule.old_logic}")
        print(f"     新逻辑: {rule.new_logic}")
        
        return {
            "success": True,
            "mutation_id": mutation.mutation_id,
            "rule_id": rule_id
        }

    def get_evolution_history(self, limit: int = 20) -> List[Dict[str, Any]]:
        """获取演化历史"""
        mutations = self.mutations[-limit:]
        return [
            {
                "id": m.mutation_id,
                "timestamp": m.timestamp,
                "target": m.target,
                "before": m.before,
                "after": m.after,
                "reason": m.reason,
                "success": m.success
            }
            for m in reversed(mutations)
        ]

    def rollback(self, mutation_id: str) -> bool:
        """
        回滚变异
        
        将系统逻辑恢复到变异前的状态。
        """
        for mutation in reversed(self.mutations):
            if mutation.mutation_id == mutation_id:
                # 找到对应的规则
                for rule in self.rules.values():
                    if rule.description == mutation.reason:
                        rule.executed = False
                        rule.executed_at = ""
                        print(f"  [L7 商鞅] ↩️ 回滚变法: {mutation_id}")
                        return True
        return False

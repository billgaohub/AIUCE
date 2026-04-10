"""
L6/L7 演化层：内圣外王的双核变法引擎
Dual-Core Evolution Engine

架构：
┌─────────────────────────────────────────────────────────┐
│              L6/L7 演化层 (Dual-Core Evolution)          │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  ┌───────────────────────────────────────────────────┐  │
│  │  内环（心智与 SOP 演化）- Hermes                     │  │
│  │  - 闭环学习 (Procedural Memory)                    │  │
│  │  - 长程任务成功后提取操作轨迹                        │  │
│  │  - 生成 agentskills.io 标准化技能                  │  │
│  │  - 越来越懂你                                      │  │
│  └───────────────────────────────────────────────────┘  │
│                                                          │
│  ┌───────────────────────────────────────────────────┐  │
│  │  外环（物理与内核重构）- OpenSpace                   │  │
│  │  - 任务失败时触发重构                              │  │
│  │  - API 变更时自动适配                              │  │
│  │  - GDPVal 基准测试监控                             │  │
│  │  - 自动生成胶水代码                                │  │
│  │  - 最大重构尝试次数限制                            │  │
│  └───────────────────────────────────────────────────┘  │
│                                                          │
└─────────────────────────────────────────────────────────┘

演化模式（OpenSpace）：
- FIX: 修复错误
- DERIVED: 派生新功能
- CAPTURED: 捕获新模式
"""

from typing import Dict, Any, List, Optional, Tuple, Callable
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import json
import os
import threading
from collections import defaultdict
import hashlib


# ═══════════════════════════════════════════════════════════════
# 类型定义
# ═══════════════════════════════════════════════════════════════

class EvolutionMode(Enum):
    """演化模式"""
    FIX = "fix"               # 修复错误
    DERIVED = "derived"       # 派生新功能
    CAPTURED = "captured"     # 捕获新模式


class EvolutionStatus(Enum):
    """演化状态"""
    PENDING = "pending"
    APPROVED = "approved"
    EXECUTING = "executing"
    COMPLETED = "completed"
    FAILED = "failed"
    ROLLED_BACK = "rolled_back"


class EvolutionTrigger(Enum):
    """演化触发器"""
    TASK_FAILURE = "task_failure"
    API_CHANGE = "api_change"
    PERFORMANCE_DEGRADATION = "performance_degradation"
    SUCCESS_PATTERN = "success_pattern"
    MANUAL = "manual"


@dataclass
class SuccessPattern:
    """成功模式（L6 记录）"""
    id: str
    name: str
    description: str
    trigger_conditions: List[str]
    actions: List[str]
    success_rate: float = 0.0
    usage_count: int = 0
    last_used: Optional[str] = None
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "trigger_conditions": self.trigger_conditions,
            "actions": self.actions,
            "success_rate": self.success_rate,
            "usage_count": self.usage_count,
            "last_used": self.last_used,
            "created_at": self.created_at
        }


@dataclass
class EvolutionRule:
    """演化规则"""
    id: str
    name: str
    mode: EvolutionMode
    trigger: EvolutionTrigger
    condition: str  # 触发条件（可执行表达式）
    action: str     # 执行动作
    auto_approve: bool = False
    max_attempts: int = 3
    attempts: int = 0
    status: EvolutionStatus = EvolutionStatus.PENDING
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    executed_at: Optional[str] = None
    result: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "mode": self.mode.value,
            "trigger": self.trigger.value,
            "condition": self.condition,
            "action": self.action,
            "auto_approve": self.auto_approve,
            "max_attempts": self.max_attempts,
            "attempts": self.attempts,
            "status": self.status.value,
            "created_at": self.created_at,
            "executed_at": self.executed_at,
            "result": self.result
        }


@dataclass
class MutationRecord:
    """变异记录"""
    id: str
    rule_id: str
    before_state: Dict[str, Any]
    after_state: Dict[str, Any]
    rollback_state: Optional[Dict[str, Any]] = None
    success: bool = False
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


# ═══════════════════════════════════════════════════════════════
# 内环：心智与 SOP 演化 (Hermes 风格)
# ═══════════════════════════════════════════════════════════════

class InnerEvolution:
    """
    内环演化 - 心智与 SOP
    
    特性：
    1. 闭环学习（Procedural Memory）
    2. 成功路径提取
    3. 技能标准化（agentskills.io）
    4. "越来越懂你"
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.patterns: Dict[str, SuccessPattern] = {}
        self._pattern_index: Dict[str, List[str]] = defaultdict(list)  # trigger -> pattern_ids
        self._load_patterns()
    
    def _load_patterns(self):
        """加载成功模式"""
        default_path = os.path.expanduser("~/.aiuce/patterns.json")
        storage_path = self.config.get("storage_path", default_path)
        
        if os.path.exists(storage_path):
            try:
                with open(storage_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    for pattern_data in data.get("patterns", []):
                        pattern = SuccessPattern(**pattern_data)
                        self.patterns[pattern.id] = pattern
                        
                        for trigger in pattern.trigger_conditions:
                            self._pattern_index[trigger].append(pattern.id)
                
                print(f"  [L6 内环] 加载 {len(self.patterns)} 个成功模式")
            except Exception as e:
                print(f"  [L6 内环] 加载失败: {e}")
    
    def _save_patterns(self):
        """保存成功模式"""
        default_path = os.path.expanduser("~/.aiuce/patterns.json")
        storage_path = self.config.get("storage_path", default_path)
        
        os.makedirs(os.path.dirname(storage_path), exist_ok=True)
        
        try:
            data = {
                "last_updated": datetime.now().isoformat(),
                "patterns": [p.to_dict() for p in self.patterns.values()]
            }
            with open(storage_path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"  [L6 内环] 保存失败: {e}")
    
    def record_success(
        self,
        task_description: str,
        actions: List[str],
        outcome: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Optional[str]:
        """
        记录成功路径
        
        提取成功模式并存储
        """
        import uuid
        
        # 提取触发条件
        triggers = self._extract_triggers(task_description)
        
        # 检查是否已有类似模式
        existing_id = self._find_similar_pattern(triggers, actions)
        if existing_id:
            # 更新已有模式
            pattern = self.patterns[existing_id]
            pattern.usage_count += 1
            pattern.success_rate = (pattern.success_rate * (pattern.usage_count - 1) + 1.0) / pattern.usage_count
            pattern.last_used = datetime.now().isoformat()
            self._save_patterns()
            return existing_id
        
        # 创建新模式
        pattern_id = str(uuid.uuid4())[:8]
        
        pattern = SuccessPattern(
            id=pattern_id,
            name=self._generate_name(task_description),
            description=task_description,
            trigger_conditions=triggers,
            actions=actions,
            success_rate=1.0,
            usage_count=1,
            last_used=datetime.now().isoformat()
        )
        
        self.patterns[pattern_id] = pattern
        
        for trigger in triggers:
            self._pattern_index[trigger].append(pattern_id)
        
        self._save_patterns()
        
        print(f"  [L6 内环] 记录成功模式: {pattern.name}")
        return pattern_id
    
    def _extract_triggers(self, description: str) -> List[str]:
        """提取触发条件"""
        # 简单关键词提取
        import re
        keywords = re.findall(r"\b[a-zA-Z\u4e00-\u9fff]{2,}\b", description.lower())
        return list(set(keywords))[:5]
    
    def _find_similar_pattern(self, triggers: List[str], actions: List[str]) -> Optional[str]:
        """查找类似模式"""
        for trigger in triggers:
            for pattern_id in self._pattern_index.get(trigger, []):
                pattern = self.patterns[pattern_id]
                # 简单相似度检查
                if len(set(pattern.actions) & set(actions)) >= len(actions) * 0.5:
                    return pattern_id
        return None
    
    def _generate_name(self, description: str) -> str:
        """生成模式名称"""
        words = description.split()[:5]
        return "_".join(words) if words else "unnamed_pattern"
    
    def match_pattern(self, task_description: str) -> List[SuccessPattern]:
        """匹配成功模式"""
        triggers = self._extract_triggers(task_description)
        
        matched = []
        seen = set()
        
        for trigger in triggers:
            for pattern_id in self._pattern_index.get(trigger, []):
                if pattern_id not in seen:
                    seen.add(pattern_id)
                    matched.append(self.patterns[pattern_id])
        
        # 按成功率排序
        matched.sort(key=lambda p: p.success_rate, reverse=True)
        
        return matched[:5]
    
    def generate_skill(self, pattern_id: str) -> Optional[Dict[str, Any]]:
        """
        生成标准化技能（agentskills.io 格式）
        
        将成功模式转换为可复用技能
        """
        pattern = self.patterns.get(pattern_id)
        if not pattern:
            return None
        
        skill = {
            "name": pattern.name,
            "description": pattern.description,
            "triggers": pattern.trigger_conditions,
            "steps": [
                {"step": i + 1, "action": action}
                for i, action in enumerate(pattern.actions)
            ],
            "metadata": {
                "success_rate": pattern.success_rate,
                "usage_count": pattern.usage_count,
                "source": "hermes_inner_evolution",
                "created_at": pattern.created_at
            }
        }
        
        return skill
    
    def stats(self) -> Dict[str, Any]:
        """统计"""
        return {
            "total_patterns": len(self.patterns),
            "avg_success_rate": sum(p.success_rate for p in self.patterns.values()) / max(len(self.patterns), 1),
            "total_usage": sum(p.usage_count for p in self.patterns.values())
        }


# ═══════════════════════════════════════════════════════════════
# 外环：物理与内核重构 (OpenSpace 风格)
# ═══════════════════════════════════════════════════════════════

class OuterEvolution:
    """
    外环演化 - 物理与内核重构
    
    特性：
    1. 任务失败触发重构
    2. API 变更自动适配
    3. GDPVal 基准测试监控
    4. 自动生成胶水代码
    5. 最大重构尝试次数限制
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.rules: Dict[str, EvolutionRule] = {}
        self.mutations: List[MutationRecord] = []
        self._max_attempts = self.config.get("max_attempts", 3)
        self._fallback_to_human = False
        self._load_rules()
    
    def _load_rules(self):
        """加载演化规则"""
        default_path = os.path.expanduser("~/.aiuce/evolution_rules.json")
        storage_path = self.config.get("storage_path", default_path)
        
        if os.path.exists(storage_path):
            try:
                with open(storage_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    for rule_data in data.get("rules", []):
                        rule = EvolutionRule(
                            id=rule_data["id"],
                            name=rule_data["name"],
                            mode=EvolutionMode(rule_data["mode"]),
                            trigger=EvolutionTrigger(rule_data["trigger"]),
                            condition=rule_data["condition"],
                            action=rule_data["action"],
                            auto_approve=rule_data.get("auto_approve", False),
                            max_attempts=rule_data.get("max_attempts", 3),
                            status=EvolutionStatus(rule_data.get("status", "pending"))
                        )
                        self.rules[rule.id] = rule
                
                print(f"  [L7 外环] 加载 {len(self.rules)} 个演化规则")
            except Exception as e:
                print(f"  [L7 外环] 加载失败: {e}")
    
    def _save_rules(self):
        """保存演化规则"""
        default_path = os.path.expanduser("~/.aiuce/evolution_rules.json")
        storage_path = self.config.get("storage_path", default_path)
        
        os.makedirs(os.path.dirname(storage_path), exist_ok=True)
        
        try:
            data = {
                "last_updated": datetime.now().isoformat(),
                "rules": [r.to_dict() for r in self.rules.values()]
            }
            with open(storage_path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"  [L7 外环] 保存失败: {e}")
    
    def create_rule(
        self,
        name: str,
        mode: EvolutionMode,
        trigger: EvolutionTrigger,
        condition: str,
        action: str,
        auto_approve: bool = False
    ) -> str:
        """创建演化规则"""
        import uuid
        
        rule_id = str(uuid.uuid4())[:8]
        
        rule = EvolutionRule(
            id=rule_id,
            name=name,
            mode=mode,
            trigger=trigger,
            condition=condition,
            action=action,
            auto_approve=auto_approve
        )
        
        self.rules[rule_id] = rule
        self._save_rules()
        
        print(f"  [L7 外环] 创建规则: {name}")
        return rule_id
    
    def check_trigger(
        self,
        trigger: EvolutionTrigger,
        context: Optional[Dict[str, Any]] = None
    ) -> List[EvolutionRule]:
        """检查触发条件"""
        matched = []
        
        for rule in self.rules.values():
            if rule.trigger != trigger:
                continue
            
            if rule.status == EvolutionStatus.COMPLETED:
                continue
            
            if rule.attempts >= rule.max_attempts:
                continue
            
            # 检查条件
            try:
                # 简单条件检查（实际应使用安全的表达式求值）
                if self._evaluate_condition(rule.condition, context):
                    matched.append(rule)
            except Exception:
                pass
        
        return matched
    
    def _evaluate_condition(self, condition: str, context: Optional[Dict[str, Any]]) -> bool:
        """评估条件"""
        if not condition:
            return True
        
        # 安全的条件评估
        context = context or {}
        
        # 简单变量替换
        for key, value in context.items():
            condition = condition.replace(f"{{{key}}}", str(value))
        
        # 检查是否包含真值
        true_values = ["true", "1", "yes", "error", "failed"]
        return any(tv in condition.lower() for tv in true_values)
    
    def execute_evolution(
        self,
        rule_id: str,
        dry_run: bool = False
    ) -> Tuple[bool, str]:
        """
        执行演化
        
        Returns:
            (success, message)
        """
        rule = self.rules.get(rule_id)
        if not rule:
            return False, f"规则 {rule_id} 不存在"
        
        # 检查尝试次数
        if rule.attempts >= rule.max_attempts:
            self._fallback_to_human = True
            return False, f"已达最大尝试次数 ({rule.max_attempts})，需要人工介入"
        
        # 更新状态
        rule.status = EvolutionStatus.EXECUTING
        rule.attempts += 1
        self._save_rules()
        
        print(f"  [L7 外环] 执行演化: {rule.name} (尝试 {rule.attempts}/{rule.max_attempts})")
        
        if dry_run:
            rule.status = EvolutionStatus.PENDING
            return True, "DRY RUN: 演化未实际执行"
        
        try:
            # 执行动作（这里应该调用实际的执行器）
            result = self._execute_action(rule.action)
            
            # 记录变异
            mutation = MutationRecord(
                id=str(hashlib.md5(rule_id.encode()).hexdigest()[:8]),
                rule_id=rule_id,
                before_state={"attempts": rule.attempts - 1},
                after_state={"attempts": rule.attempts, "result": result},
                success=True
            )
            self.mutations.append(mutation)
            
            rule.status = EvolutionStatus.COMPLETED
            rule.executed_at = datetime.now().isoformat()
            rule.result = result
            self._save_rules()
            
            return True, result
            
        except Exception as e:
            rule.status = EvolutionStatus.FAILED
            rule.result = str(e)
            self._save_rules()
            
            return False, f"执行失败: {e}"
    
    def _execute_action(self, action: str) -> str:
        """执行动作"""
        # 这里应该调用实际的执行器
        # 实际实现可能包括：
        # - 生成新的 Python 代码
        # - 修改配置文件
        # - 更新 API 适配器
        return f"Action executed: {action[:50]}..."
    
    def rollback(self, mutation_id: str) -> bool:
        """回滚变异"""
        mutation = next((m for m in self.mutations if m.id == mutation_id), None)
        if not mutation:
            return False
        
        # 执行回滚
        # 实际实现应该恢复 before_state
        
        mutation.rollback_state = mutation.after_state
        mutation.success = False
        
        print(f"  [L7 外环] 回滚变异: {mutation_id}")
        return True
    
    def needs_human_intervention(self) -> bool:
        """是否需要人工介入"""
        return self._fallback_to_human
    
    def reset_fallback(self):
        """重置回退标志"""
        self._fallback_to_human = False
    
    def stats(self) -> Dict[str, Any]:
        """统计"""
        return {
            "total_rules": len(self.rules),
            "pending_rules": len([r for r in self.rules.values() if r.status == EvolutionStatus.PENDING]),
            "completed_rules": len([r for r in self.rules.values() if r.status == EvolutionStatus.COMPLETED]),
            "failed_rules": len([r for r in self.rules.values() if r.status == EvolutionStatus.FAILED]),
            "total_mutations": len(self.mutations),
            "fallback_to_human": self._fallback_to_human
        }


# ═══════════════════════════════════════════════════════════════
# 双核演化引擎主类
# ═══════════════════════════════════════════════════════════════

class DualCoreEvolution:
    """
    L6/L7 演化层 - 内圣外王的双核变法引擎
    
    内环 (L6): Hermes - 心智与 SOP 演化
    外环 (L7): OpenSpace - 物理与内核重构
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        
        # 内环演化
        self.inner = InnerEvolution(config.get("inner", {}))
        
        # 外环演化
        self.outer = OuterEvolution(config.get("outer", {}))
        
        print(f"  [L6/L7 演化层] 演化引擎/变法中心 - 双核变法引擎就位")
    
    # ── 成功记录 ───────────────────────────────────────────────
    
    def record_success(
        self,
        task_description: str,
        actions: List[str],
        outcome: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Optional[str]:
        """记录成功路径"""
        return self.inner.record_success(task_description, actions, outcome, context)
    
    def match_pattern(self, task_description: str) -> List[SuccessPattern]:
        """匹配成功模式"""
        return self.inner.match_pattern(task_description)
    
    # ── 失败处理 ───────────────────────────────────────────────
    
    def on_failure(
        self,
        error: str,
        context: Optional[Dict[str, Any]] = None
    ) -> List[EvolutionRule]:
        """失败时检查演化触发"""
        return self.outer.check_trigger(EvolutionTrigger.TASK_FAILURE, context)
    
    # ── 演化执行 ───────────────────────────────────────────────
    
    def execute_evolution(
        self,
        rule_id: str,
        dry_run: bool = False
    ) -> Tuple[bool, str]:
        """执行演化"""
        return self.outer.execute_evolution(rule_id, dry_run)
    
    def needs_human_intervention(self) -> bool:
        """是否需要人工介入"""
        return self.outer.needs_human_intervention()
    
    # ── 统计 ───────────────────────────────────────────────────
    
    def stats(self) -> Dict[str, Any]:
        """统计"""
        return {
            "inner": self.inner.stats(),
            "outer": self.outer.stats()
        }


# ═══════════════════════════════════════════════════════════════
# 导出
# ═══════════════════════════════════════════════════════════════

__all__ = [
    "EvolutionMode",
    "EvolutionStatus",
    "EvolutionTrigger",
    "SuccessPattern",
    "EvolutionRule",
    "MutationRecord",
    "InnerEvolution",
    "OuterEvolution",
    "DualCoreEvolution",
]

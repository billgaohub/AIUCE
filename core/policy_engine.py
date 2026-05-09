"""
PolicyEngine - 动态授权引擎
Dynamic Authorization Engine

根据 SONUV 文档设计：
- 评估 Agent 行为是否允许执行
- 支持动态规则加载
- 注意：Phase 1-2 Utility Function 仅用于观测，不参与控制
"""

from typing import Dict, Any, List
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import re
import os


class RiskLevel(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class Decision(Enum):
    ALLOW = "allow"
    DENY = "deny"
    ELEVATE = "elevate"
    AUDIT = "audit"


@dataclass
class PolicyRule:
    rule_id: str
    name: str
    category: str
    risk_level: RiskLevel
    conditions: Dict[str, Any]
    action: Decision
    priority: int = 100
    enabled: bool = True


@dataclass
class PolicyDecision:
    allowed: bool
    decision: Decision
    rule_id: str
    confidence: float
    reason: str
    risk_level: RiskLevel
    audit_required: bool = False


class PolicyEngine:
    """动态授权引擎"""
    
    def __init__(self, config: Dict[str, Any] = None, state_daemon=None):
        self.config = config or {}
        self.state_daemon = state_daemon
        self._rules: Dict[str, PolicyRule] = {}
        self._load_default_rules()
        print(f"  [PolicyEngine] 动态授权引擎启动")
        print(f"    已加载 {len(self._rules)} 条规则")
    
    def _load_default_rules(self):
        allowed_commands = {
            "ls", "cat", "head", "tail", "wc", "find", "grep",
            "mkdir", "touch", "cp", "mv", "chmod",
            "git", "python", "python3", "pip", "pip3", "node", "npm",
            "curl", "wget", "ping",
            "date", "whoami", "pwd", "echo", "which", "env", "uname",
        }
        for cmd in allowed_commands:
            self._rules[f"CMD_{cmd.upper()}"] = PolicyRule(
                rule_id=f"CMD_{cmd.upper()}",
                name=f"允许命令: {cmd}",
                category="command",
                risk_level=RiskLevel.LOW,
                conditions={"command": cmd},
                action=Decision.ALLOW,
                priority=100
            )
        
        dangerous_patterns = [(r';', "命令分隔"), (r'\|', "管道"), (r'&\d', "后台"), (r'\$\(', "命令替换"), (r'>', "重定向")]
        for i, (p, d) in enumerate(dangerous_patterns, 1):
            self._rules[f"DENY_PATTERN_{i:02d}"] = PolicyRule(
                rule_id=f"DENY_PATTERN_{i:02d}",
                name=f"拒绝危险模式: {d}",
                category="security",
                risk_level=RiskLevel.HIGH,
                conditions={"pattern": p},
                action=Decision.DENY,
                priority=10
            )
        
        protected = ["/etc/passwd", "~/.ssh", ".env", "credentials", "secrets"]
        for path in protected:
            self._rules[f"PROTECT_{path.replace('/', '_')}"] = PolicyRule(
                rule_id=f"PROTECT_{path.replace('/', '_')}",
                name=f"保护路径: {path}",
                category="file",
                risk_level=RiskLevel.CRITICAL,
                conditions={"path_pattern": path, "operation": "write"},
                action=Decision.DENY,
                priority=5
            )
    
    def evaluate_command(self, command: str) -> PolicyDecision:
        if not command or not command.strip():
            return PolicyDecision(False, Decision.DENY, "EMPTY", 1.0, "空命令", RiskLevel.LOW)
        
        parts = command.strip().split()
        main_cmd = parts[0] if parts else ""
        
        sorted_rules = sorted(self._rules.values(), key=lambda r: r.priority)
        for rule in sorted_rules:
            if not rule.enabled:
                continue
            if rule.category == "security":
                pattern = rule.conditions.get("pattern")
                if pattern and re.search(pattern, command):
                    if self.state_daemon:
                        self.state_daemon.emit_governance(rule.rule_id, "deny", rule.description, "high")
                    return PolicyDecision(False, Decision.DENY, rule.rule_id, 0.95, rule.description, rule.risk_level)
        
        cmd_rule_id = f"CMD_{main_cmd.upper()}"
        if cmd_rule_id not in self._rules:
            return PolicyDecision(False, Decision.DENY, "UNKNOWN_CMD", 0.9, f"命令 '{main_cmd}' 不在白名单", RiskLevel.MEDIUM)
        
        if main_cmd in ("rm", "rmdir"):
            return PolicyDecision(True, Decision.AUDIT, "DELETE_RISK", 0.85, "删除操作需要审计", RiskLevel.HIGH, True)
        
        return PolicyDecision(True, Decision.ALLOW, cmd_rule_id, 0.95, "命令在白名单", RiskLevel.LOW)
    
    def evaluate_file_access(self, path: str, operation: str) -> PolicyDecision:
        expanded = os.path.expanduser(path)
        sorted_rules = sorted(self._rules.values(), key=lambda r: r.priority)
        for rule in sorted_rules:
            if not rule.enabled or rule.category != "file":
                continue
            if "path_pattern" in rule.conditions:
                pattern = rule.conditions["path_pattern"]
                op = rule.conditions.get("operation", "write")
                exp_pattern = os.path.expanduser(pattern)
                if (op == operation or op == "write") and (exp_pattern in expanded or pattern in path):
                    return PolicyDecision(False, Decision.DENY, rule.rule_id, 0.95, f"受保护路径: {pattern}", rule.risk_level)
        
        if operation == "delete":
            return PolicyDecision(True, Decision.AUDIT, "DELETE_RISK", 0.9, "删除操作需要审计", RiskLevel.HIGH, True)
        
        return PolicyDecision(True, Decision.ALLOW, "FILE_OK", 0.9, "文件访问允许", RiskLevel.LOW)
    
    def evaluate(self, action_type: str, target: str = "", params: Dict[str, Any] = None) -> PolicyDecision:
        params = params or {}
        if action_type == "command":
            return self.evaluate_command(target)
        if action_type == "file":
            return self.evaluate_file_access(target, params.get("operation", "read"))
        return PolicyDecision(True, Decision.AUDIT, "UNKNOWN", 0.5, "未知行为", RiskLevel.MEDIUM, True)
    
    def add_rule(self, rule: PolicyRule):
        self._rules[rule.rule_id] = rule
    
    def list_rules(self) -> List[Dict]:
        return [{"rule_id": r.rule_id, "name": r.name, "category": r.category, "risk": r.risk_level.value, "action": r.action.value, "enabled": r.enabled} for r in sorted(self._rules.values(), key=lambda x: x.priority)]
    
    def stats(self) -> Dict[str, Any]:
        cat_count = {}
        for r in self._rules.values():
            cat_count[r.category] = cat_count.get(r.category, 0) + 1
        return {"total": len(self._rules), "enabled": len([r for r in self._rules.values() if r.enabled]), "by_category": cat_count}


__all__ = ["RiskLevel", "Decision", "PolicyRule", "PolicyDecision", "PolicyEngine"]
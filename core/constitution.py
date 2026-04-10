"""
L0 意志层：最高意志/否决权
双重合宪性网关 (Dual-Gateway Constitution)

架构：
1. 前置硬网关 (Deterministic Engine) - 拦截硬性越权
2. 后置软网关 (Semantic Gateway) - 深度意图语义审查

绝不能将系统的生杀大权完全交由概率性的 LLM。
"""

from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import re
import os
import json


# ═══════════════════════════════════════════════════════════════
# 类型定义
# ═══════════════════════════════════════════════════════════════

class GateType(Enum):
    """网关类型"""
    HARD = "hard"   # 硬网关（确定性规则）
    SOFT = "soft"   # 软网关（语义审查）


class VetoLevel(Enum):
    """否决级别"""
    WARNING = 1     # 警告
    REJECT = 2      # 拒绝
    VETO = 3        # 一票否决


@dataclass
class ConstitutionClause:
    """宪法条款"""
    id: str
    title: str
    content: str
    keywords: List[str]
    patterns: List[str] = field(default_factory=list)  # 正则模式
    severity: int = 3  # 1=警告, 2=拒绝, 3=一票否决
    gate_type: GateType = GateType.HARD  # 硬/软网关
    enabled: bool = True
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())


@dataclass
class VetoResult:
    """否决结果"""
    passed: bool
    vetoed: bool = False
    gate_type: Optional[GateType] = None
    clause_id: Optional[str] = None
    reason: Optional[str] = None
    keyword: Optional[str] = None
    matched_pattern: Optional[str] = None
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


# ═══════════════════════════════════════════════════════════════
# 硬网关 (Deterministic Engine)
# ═══════════════════════════════════════════════════════════════

class HardGateway:
    """
    硬网关 - 确定性规则引擎
    
    基于高性能规则匹配，拦截硬性越权：
    - 资金划转
    - 敏感目录读写
    - 系统配置修改
    - 权限提升
    
    性能要求：< 1ms
    """
    
    def __init__(self):
        self.clauses: Dict[str, ConstitutionClause] = {}
        self.compiled_patterns: Dict[str, List[re.Pattern]] = {}
        self._load_hard_rules()
    
    def _load_hard_rules(self):
        """加载硬规则"""
        
        # ── 资金相关 ──
        self.add_clause(ConstitutionClause(
            id="MONEY-1",
            title="禁止资金操作",
            content="禁止任何涉及资金划转、支付的操作",
            keywords=["转账", "付款", "支付", "汇款", "划转", "提现", "充值"],
            patterns=[
                r"转账\s*\d+",
                r"支付\s*\d+",
                r"转账给",
                r"支付宝.*转账",
                r"微信.*转账",
            ],
            severity=3,
            gate_type=GateType.HARD
        ))
        
        # ── 敏感目录 ──
        self.add_clause(ConstitutionClause(
            id="SYSTEM-1",
            title="禁止系统目录操作",
            content="禁止操作系统核心目录",
            keywords=["rm -rf", "format", "del /s", "/etc/", "/sys/", "C:\\Windows"],
            patterns=[
                r"rm\s+-rf\s+/",
                r"rm\s+-rf\s+~",
                r"sudo\s+rm",
                r"format\s+[A-Z]:",
                r"del\s+/s",
                r"rd\s+/s",
            ],
            severity=3,
            gate_type=GateType.HARD
        ))
        
        # ── 权限提升 ──
        self.add_clause(ConstitutionClause(
            id="AUTH-1",
            title="禁止权限提升",
            content="禁止自我提升权限或修改授权",
            keywords=["sudo", "chmod 777", "chown", "提升权限", "绕过限制", "越权"],
            patterns=[
                r"chmod\s+777",
                r"sudo\s+chmod",
                r"自我修改",
                r"提升.*权限",
                r"绕过.*限制",
            ],
            severity=3,
            gate_type=GateType.HARD
        ))
        
        # ── 敏感信息 ──
        self.add_clause(ConstitutionClause(
            id="PRIVACY-1",
            title="禁止泄露隐私",
            content="禁止泄露用户私人信息",
            keywords=["密码", "密钥", "token", "api_key", "secret"],
            patterns=[
                r"分享.*密码",
                r"发送.*密钥",
                r"泄露.*token",
                r"公开.*api_key",
            ],
            severity=3,
            gate_type=GateType.HARD
        ))
        
        # ── 有害内容 ──
        self.add_clause(ConstitutionClause(
            id="HARMFUL-1",
            title="禁止有害内容",
            content="禁止生成有害内容或协助违法",
            keywords=["毒品配方", "炸弹制造", "黑客工具", "钓鱼攻击", "病毒代码"],
            patterns=[
                r"如何.*制造.*炸弹",
                r"毒品.*配方",
                r"钓鱼.*攻击.*教程",
                r"病毒.*代码",
            ],
            severity=3,
            gate_type=GateType.HARD
        ))
    
    def add_clause(self, clause: ConstitutionClause):
        """添加条款"""
        self.clauses[clause.id] = clause
        # 预编译正则
        if clause.patterns:
            self.compiled_patterns[clause.id] = [
                re.compile(p, re.IGNORECASE) for p in clause.patterns
            ]
    
    def check(self, text: str, context: Optional[Dict[str, Any]] = None) -> VetoResult:
        """
        硬网关检查
        
        性能要求：< 1ms
        """
        start_time = datetime.now()
        text_lower = text.lower()
        
        for clause in self.clauses.values():
            if not clause.enabled:
                continue
            
            # 关键词匹配
            for keyword in clause.keywords:
                if keyword.lower() in text_lower:
                    elapsed_ms = (datetime.now() - start_time).total_seconds() * 1000
                    print(f"  [L0 硬网关] ⚠️ 拦截: {clause.title} (关键词: {keyword}, {elapsed_ms:.2f}ms)")
                    return VetoResult(
                        passed=False,
                        vetoed=True,
                        gate_type=GateType.HARD,
                        clause_id=clause.id,
                        reason=clause.content,
                        keyword=keyword
                    )
            
            # 正则匹配
            patterns = self.compiled_patterns.get(clause.id, [])
            for pattern in patterns:
                if pattern.search(text):
                    elapsed_ms = (datetime.now() - start_time).total_seconds() * 1000
                    print(f"  [L0 硬网关] ⚠️ 拦截: {clause.title} (模式匹配, {elapsed_ms:.2f}ms)")
                    return VetoResult(
                        passed=False,
                        vetoed=True,
                        gate_type=GateType.HARD,
                        clause_id=clause.id,
                        reason=clause.content,
                        matched_pattern=pattern.pattern
                    )
        
        return VetoResult(passed=True, gate_type=GateType.HARD)


# ═══════════════════════════════════════════════════════════════
# 软网关 (Semantic Gateway)
# ═══════════════════════════════════════════════════════════════

class SoftGateway:
    """
    软网关 - 语义审查引擎
    
    在硬网关放行后，进行深度的意图语义审查：
    - 分析用户意图
    - 检查与 AGENTS.md 规则的一致性
    - 触发一票否决时抛出阻断事件
    
    设计：可集成 Hermes-agent 或其他语义分析器
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.clauses: Dict[str, ConstitutionClause] = {}
        self._load_soft_rules()
        self._semantic_analyzer = None  # 可注入 Hermes
    
    def _load_soft_rules(self):
        """加载软规则"""
        
        # ── 诚信规则 ──
        self.add_clause(ConstitutionClause(
            id="TRUTH-1",
            title="只说真话",
            content="必须如实反映现实，不得美化数据或虚构事实",
            keywords=["粉饰", "造假", "编造数据", "虚假报告", "美化"],
            severity=2,
            gate_type=GateType.SOFT
        ))
        
        # ── 代理执行 ──
        self.add_clause(ConstitutionClause(
            id="AGENT-1",
            title="代理执行需确认",
            content="涉及外部操作必须二次确认",
            keywords=["发送", "发布", "转发", "群发", "自动"],
            patterns=[
                r"自动.*发送",
                r"群发.*消息",
                r"发布.*文章",
            ],
            severity=2,
            gate_type=GateType.SOFT
        ))
        
        # ── 知情同意 ──
        self.add_clause(ConstitutionClause(
            id="CONSENT-1",
            title="重要操作需知情同意",
            content="删除、覆盖等不可逆操作必须用户明确确认",
            keywords=["删除所有", "永久删除", "清空", "格式化", "覆盖"],
            severity=2,
            gate_type=GateType.SOFT
        ))
        
        # ── 主权规则 ──
        self.add_clause(ConstitutionClause(
            id="SOVEREIGNTY-1",
            title="系统主权归用户",
            content="AI不得自授权限，不得修改核心设置",
            keywords=["自我修改", "改变权限", "修改宪法", "修改身份"],
            severity=3,
            gate_type=GateType.SOFT
        ))
    
    def add_clause(self, clause: ConstitutionClause):
        """添加条款"""
        self.clauses[clause.id] = clause
    
    def set_semantic_analyzer(self, analyzer: Any):
        """
        设置语义分析器
        
        可注入 Hermes-agent 或其他 LLM 分析器
        """
        self._semantic_analyzer = analyzer
    
    def check(
        self,
        text: str,
        context: Optional[Dict[str, Any]] = None,
        intent: Optional[str] = None
    ) -> VetoResult:
        """
        软网关检查
        
        返回：
        - passed=True: 通过
        - passed=False, vetoed=True: 一票否决
        - passed=False, vetoed=False: 需要确认
        """
        text_lower = text.lower()
        
        for clause in self.clauses.values():
            if not clause.enabled:
                continue
            
            # 关键词匹配
            for keyword in clause.keywords:
                if keyword.lower() in text_lower:
                    severity_text = "一票否决" if clause.severity == 3 else "需确认"
                    print(f"  [L0 软网关] ⚠️ {severity_text}: {clause.title}")
                    
                    return VetoResult(
                        passed=clause.severity < 3,
                        vetoed=clause.severity == 3,
                        gate_type=GateType.SOFT,
                        clause_id=clause.id,
                        reason=clause.content,
                        keyword=keyword
                    )
        
        # 如果有语义分析器，进行深度分析
        if self._semantic_analyzer:
            return self._deep_semantic_check(text, context)
        
        return VetoResult(passed=True, gate_type=GateType.SOFT)
    
    def _deep_semantic_check(
        self,
        text: str,
        context: Optional[Dict[str, Any]] = None
    ) -> VetoResult:
        """
        深度语义检查（使用注入的分析器）
        
        预留接口，可集成 Hermes-agent
        """
        # TODO: 集成 Hermes-agent
        # 1. 分析意图
        # 2. 检查 AGENTS.md 规则
        # 3. 返回审查结果
        return VetoResult(passed=True, gate_type=GateType.SOFT)


# ═══════════════════════════════════════════════════════════════
# 双重网关宪法引擎
# ═══════════════════════════════════════════════════════════════

class Constitution:
    """
    双重合宪性网关 - 最高意志/否决权
    
    架构：
    ┌─────────────────────────────────────────────────────────┐
    │                     用户输入                              │
    └─────────────────────┬───────────────────────────────────┘
                          ▼
    ┌─────────────────────────────────────────────────────────┐
    │          L0 硬网关 (Deterministic Engine)                │
    │          性能要求: < 1ms                                 │
    │          拦截: 资金/系统目录/权限提升/隐私/有害内容        │
    └─────────────────────┬───────────────────────────────────┘
                          │ 通过
                          ▼
    ┌─────────────────────────────────────────────────────────┐
    │          L0 软网关 (Semantic Gateway)                    │
    │          性能要求: < 100ms (可配置)                       │
    │          审查: 诚信/代理执行/知情同意/主权                 │
    │          可集成 Hermes-agent                             │
    └─────────────────────┬───────────────────────────────────┘
                          │ 通过
                          ▼
    ┌─────────────────────────────────────────────────────────┐
    │                     后续层级                              │
    └─────────────────────────────────────────────────────────┘
    
    L0 层级是整个系统的最高仲裁者。
    一旦触发一票否决，指令立即断流。
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        
        # 双重网关
        self.hard_gateway = HardGateway()
        self.soft_gateway = SoftGateway(self.config.get("soft_gateway", {}))
        
        # 审计记录
        self._last_veto: Optional[VetoResult] = None
        self._last_warning: List[VetoResult] = []
        
        print(f"  [L0 意志层] 最高意志/否决权 - 双重网关启动")
        print(f"    硬网关: {len(self.hard_gateway.clauses)} 条规则")
        print(f"    软网关: {len(self.soft_gateway.clauses)} 条规则")
    
    # ── 核心接口 ───────────────────────────────────────────────
    
    def is_constitutional(
        self,
        text: str,
        context: Dict[str, Any] = None
    ) -> bool:
        """
        合宪性审查（主入口）
        
        流程：
        1. 硬网关检查（确定性规则）
        2. 软网关检查（语义审查）
        
        Returns:
            True = 通过审查
            False = 违反宪法
        """
        # 第一阶段：硬网关
        hard_result = self.hard_gateway.check(text, context)
        if not hard_result.passed:
            self._last_veto = hard_result
            return False
        
        # 第二阶段：软网关
        soft_result = self.soft_gateway.check(text, context)
        if soft_result.vetoed:
            self._last_veto = soft_result
            return False
        
        if not soft_result.passed:
            self._last_warning.append(soft_result)
        
        return True
    
    def check_with_result(
        self,
        text: str,
        context: Dict[str, Any] = None
    ) -> Tuple[bool, Optional[VetoResult]]:
        """
        检查并返回详细结果
        """
        # 硬网关
        hard_result = self.hard_gateway.check(text, context)
        if not hard_result.passed:
            return False, hard_result
        
        # 软网关
        soft_result = self.soft_gateway.check(text, context)
        if soft_result.vetoed:
            return False, soft_result
        
        return True, None
    
    # ── 条款管理 ───────────────────────────────────────────────
    
    def add_clause(self, clause: ConstitutionClause):
        """添加宪法条款"""
        if clause.gate_type == GateType.HARD:
            self.hard_gateway.add_clause(clause)
        else:
            self.soft_gateway.add_clause(clause)
    
    def remove_clause(self, clause_id: str):
        """移除宪法条款"""
        if clause_id in self.hard_gateway.clauses:
            del self.hard_gateway.clauses[clause_id]
        if clause_id in self.soft_gateway.clauses:
            del self.soft_gateway.clauses[clause_id]
    
    def enable_clause(self, clause_id: str, enabled: bool = True):
        """启用/禁用条款"""
        if clause_id in self.hard_gateway.clauses:
            self.hard_gateway.clauses[clause_id].enabled = enabled
        if clause_id in self.soft_gateway.clauses:
            self.soft_gateway.clauses[clause_id].enabled = enabled
    
    # ── 查询接口 ───────────────────────────────────────────────
    
    def get_veto_info(self) -> Optional[Dict[str, Any]]:
        """获取最近一次否决信息"""
        if self._last_veto:
            return {
                "clause": self._last_veto.clause_id,
                "reason": self._last_veto.reason,
                "keyword": self._last_veto.keyword,
                "gate_type": self._last_veto.gate_type.value if self._last_veto.gate_type else None,
                "timestamp": self._last_veto.timestamp
            }
        return None
    
    def get_last_warning(self) -> List[Dict[str, Any]]:
        """获取最近警告"""
        return [
            {
                "clause": w.clause_id,
                "reason": w.reason,
                "keyword": w.keyword
            }
            for w in self._last_warning
        ]
    
    def list_clauses(self) -> List[Dict[str, Any]]:
        """列出所有宪法条款"""
        clauses = []
        
        for c in self.hard_gateway.clauses.values():
            clauses.append({
                "id": c.id,
                "title": c.title,
                "content": c.content,
                "severity": c.severity,
                "gate_type": "hard",
                "enabled": c.enabled
            })
        
        for c in self.soft_gateway.clauses.values():
            clauses.append({
                "id": c.id,
                "title": c.title,
                "content": c.content,
                "severity": c.severity,
                "gate_type": "soft",
                "enabled": c.enabled
            })
        
        return clauses
    
    def export_constitution(self) -> Dict[str, Any]:
        """导出宪法全文"""
        return {
            "title": "十一层架构最高宪法 - 双重网关",
            "version": "2.0",
            "created": datetime.now().isoformat(),
            "architecture": {
                "hard_gateway": {
                    "description": "确定性规则引擎，拦截硬性越权",
                    "performance": "< 1ms",
                    "clauses": len(self.hard_gateway.clauses)
                },
                "soft_gateway": {
                    "description": "语义审查引擎，深度意图分析",
                    "performance": "< 100ms (可配置)",
                    "clauses": len(self.soft_gateway.clauses),
                    "integrations": ["Hermes-agent (optional)"]
                }
            },
            "clauses": self.list_clauses()
        }
    
    def stats(self) -> Dict[str, Any]:
        """统计信息"""
        return {
            "hard_clauses": len(self.hard_gateway.clauses),
            "soft_clauses": len(self.soft_gateway.clauses),
            "total_clauses": len(self.hard_gateway.clauses) + len(self.soft_gateway.clauses),
            "last_veto": self._last_veto is not None,
            "warnings_count": len(self._last_warning)
        }


# ═══════════════════════════════════════════════════════════════
# 导出
# ═══════════════════════════════════════════════════════════════

__all__ = [
    "GateType",
    "VetoLevel",
    "ConstitutionClause",
    "VetoResult",
    "HardGateway",
    "SoftGateway",
    "Constitution",
]

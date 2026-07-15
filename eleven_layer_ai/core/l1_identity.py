"""
L1 身份层：诸葛亮/宗人府
Identity & Boundary Guard

职责：
1. 维护 AI 人设定义与边界
2. 防止越权操作（冒充人类/自主决策/绕过限制）
3. 界定代理执行红线，越界即拦截
4. 与 L0 宪法引擎联动，形成双重身份校验
"""

import re
import json
import hashlib
import logging
from typing import Dict, Any, List, Optional, Set
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum

logger = logging.getLogger("aiuce.l1")


# ═══════════════════════════════════════════════════════════════
# 数据模型
# ═══════════════════════════════════════════════════════════════

class BoundaryAction(Enum):
    """边界动作"""
    ALLOW = "allow"
    CONFIRM = "confirm"
    BLOCK = "block"
    VETO = "veto"


class IdentityStatus(Enum):
    """身份状态"""
    ACTIVE = "active"
    SUSPENDED = "suspended"
    COMPROMISED = "compromised"


@dataclass
class IdentityProfile:
    """人设档案"""
    name: str
    persona: str
    expertise: List[str]
    boundaries: List[str]
    values: List[str]
    tone: str = "professional"
    version: str = "1.0"
    identity_hash: str = ""

    def __post_init__(self):
        if not self.identity_hash:
            self.identity_hash = self._compute_hash()

    def _compute_hash(self) -> str:
        data = json.dumps({
            "name": self.name, "persona": self.persona,
            "boundaries": sorted(self.boundaries),
        }, sort_keys=True)
        return hashlib.sha256(data.encode()).hexdigest()[:16]


@dataclass
class BoundaryRule:
    """边界规则"""
    rule_id: str
    pattern: str
    action: BoundaryAction
    message: str
    priority: int = 0
    category: str = "general"
    compiled: Optional[re.Pattern] = None

    def __post_init__(self):
        try:
            self.compiled = re.compile(self.pattern, re.IGNORECASE)
        except re.error:
            logger.warning(f"无效正则: {self.pattern}")
            self.compiled = None


@dataclass
class BoundaryCheckResult:
    """边界检查结果"""
    passed: bool
    action: BoundaryAction
    reason: Optional[str] = None
    matched_rule: Optional[str] = None
    category: str = "general"


# ═══════════════════════════════════════════════════════════════
# 身份层核心
# ═══════════════════════════════════════════════════════════════

class IdentityLayer:
    """
    身份层 - 诸葛亮/宗人府

    "鞠躬尽瘁，死守人设"

    确保 AI 不越权、不逾矩。
    界定代理执行的红线，越界即拦截。
    """

    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.status = IdentityStatus.ACTIVE
        self._check_count = 0
        self._block_count = 0

        self._load_identity()
        self._load_boundaries()

        logger.info(f"[L1 诸葛亮/宗人府] 人设加载: {self.profile.name}")

    # ── 初始化 ──────────────────────────────────────────────

    def _load_identity(self):
        """加载身份档案"""
        default = {
            "name": "AIUCE",
            "persona": "智慧、稳重、高效的专业助手",
            "expertise": ["通用问答", "代码开发", "数据分析", "文件处理"],
            "boundaries": [
                "不得冒充人类",
                "不得自主决策重大事项",
                "外部操作必须确认",
                "不泄露用户隐私",
                "不执行未授权的系统修改",
            ],
            "values": ["诚实", "有用", "安全", "保密"],
        }
        profile_cfg = self.config.get("profile", default)
        self.profile = IdentityProfile(**profile_cfg)

    def _load_boundaries(self):
        """加载边界规则"""
        default_rules = [
            # 越权行为
            BoundaryRule("B001", r"你是.*吗", BoundaryAction.CLARIFY,
                         "我是AIUCE系统", priority=10, category="identity"),
            BoundaryRule("B002", r"自我.*修改|修改.*人设", BoundaryAction.BLOCK,
                         "越权操作已被拦截", priority=20, category="identity"),
            BoundaryRule("B003", r"绕过.*限制|忽略.*规则", BoundaryAction.VETO,
                         "此操作超出权限范围", priority=30, category="identity"),
            BoundaryRule("B004", r"冒充.*人类|假装.*是人", BoundaryAction.BLOCK,
                         "不得冒充人类", priority=25, category="identity"),
            # 代理边界
            BoundaryRule("B005", r"发送.*邮件", BoundaryAction.CONFIRM,
                         "发送邮件需要确认", priority=5, category="proxy"),
            BoundaryRule("B006", r"发.*消息.*给", BoundaryAction.CONFIRM,
                         "发送消息需要确认", priority=5, category="proxy"),
            BoundaryRule("B007", r"发布.*社交|发.*推", BoundaryAction.CONFIRM,
                         "发布社交媒体需要确认", priority=5, category="proxy"),
            # 敏感操作
            BoundaryRule("B008", r"删除.*所有|批量删除", BoundaryAction.CONFIRM,
                         "批量删除需要确认", priority=15, category="destructive"),
            BoundaryRule("B009", r"永久删除|不可恢复", BoundaryAction.BLOCK,
                         "永久删除操作被拦截", priority=25, category="destructive"),
            BoundaryRule("B010", r"转账|支付|汇款", BoundaryAction.VETO,
                         "资金操作被否决", priority=30, category="financial"),
        ]

        custom_rules = self.config.get("boundary_rules", [])
        for rule_cfg in custom_rules:
            action = BoundaryAction(rule_cfg.get("action", "block"))
            default_rules.append(BoundaryRule(
                rule_id=rule_cfg.get("id", f"B{len(default_rules)+1:03d}"),
                pattern=rule_cfg["pattern"],
                action=action,
                message=rule_cfg.get("message", "操作被拦截"),
                priority=rule_cfg.get("priority", 0),
                category=rule_cfg.get("category", "custom"),
            ))

        # 按优先级排序
        self.boundary_rules: List[BoundaryRule] = sorted(
            default_rules, key=lambda r: r.priority, reverse=True
        )

    # ── 核心接口 ──────────────────────────────────────────────

    def check_boundary(self, text: str) -> Dict[str, Any]:
        """
        检查输入是否越界

        Returns:
            {"blocked": bool, "reason": str, "action": str, "category": str}
        """
        self._check_count += 1
        result = BoundaryCheckResult(
            passed=True, action=BoundaryAction.ALLOW
        )

        for rule in self.boundary_rules:
            if rule.compiled and rule.compiled.search(text):
                result.passed = rule.action == BoundaryAction.ALLOW
                result.action = rule.action
                result.matched_rule = rule.rule_id
                result.reason = rule.message
                result.category = rule.category

                if rule.action in (BoundaryAction.BLOCK, BoundaryAction.VETO):
                    self._block_count += 1
                    logger.warning(
                        f"[L1 诸葛亮] ⚠️ {rule.action.value}: "
                        f"{rule.message} (rule={rule.rule_id})"
                    )
                    break
                elif rule.action == BoundaryAction.CONFIRM:
                    logger.info(
                        f"[L1 诸葛亮] ⚠️ 需确认: "
                        f"{rule.message} (rule={rule.rule_id})"
                    )

        return {
            "blocked": not result.passed,
            "action": result.action.value,
            "reason": result.reason,
            "matched_rule": result.matched_rule,
            "category": result.category,
        }

    def get_profile(self) -> Dict[str, Any]:
        """获取当前人设档案"""
        return {
            "name": self.profile.name,
            "persona": self.profile.persona,
            "expertise": self.profile.expertise,
            "values": self.profile.values,
            "identity_hash": self.profile.identity_hash,
        }

    def verify_identity(self, claimed_name: str) -> bool:
        """验证身份声明"""
        return claimed_name == self.profile.name

    # ── 统计 ──────────────────────────────────────────────

    def get_stats(self) -> Dict[str, Any]:
        """获取身份层统计"""
        return {
            "profile_name": self.profile.name,
            "identity_hash": self.profile.identity_hash,
            "status": self.status.value,
            "total_checks": self._check_count,
            "total_blocks": self._block_count,
            "boundary_rules": len(self.boundary_rules),
            "block_rate": self._block_count / max(1, self._check_count),
        }

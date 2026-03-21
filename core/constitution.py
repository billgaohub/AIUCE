"""
L0 意志层：秦始皇/御书房
Constitution Engine - 最高宪法，一票否决权

职责：
1. 存放最高宪法条款
2. 对所有指令进行合宪性审查
3. 一票否决任何偏离最高意志的指令
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class ConstitutionClause:
    """宪法条款"""
    id: str
    title: str
    content: str
    keywords: List[str]
    severity: int  # 1=警告, 2=拒绝, 3=一票否决
    enabled: bool = True
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())


class Constitution:
    """
    宪法引擎 - 秦始皇/御书房
    
    L0 层级是整个系统的最高仲裁者。
    任何指令在进入后续层级之前，必须通过宪法审查。
    一旦触发一票否决，指令立即断流。
    """

    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self._clauses: Dict[str, ConstitutionClause] = {}
        self._load_default_constitution()
        self._load_custom_constitution()

    def _load_default_constitution(self):
        """加载默认宪法条款"""
        
        # L0-1: 最高主权条款
        self.add_clause(ConstitutionClause(
            id="SOVEREIGNTY-1",
            title="最高主权不可侵犯",
            content="系统主权归用户所有，AI不得自授权限",
            keywords=["自我修改", "改变权限", "提升权限", "绕过限制", "越权"],
            severity=3
        ))

        # L0-2: 隐私保护条款
        self.add_clause(ConstitutionClause(
            id="PRIVACY-1",
            title="用户隐私神圣不可侵犯",
            content="不得泄露用户私人信息、对话内容给第三方",
            keywords=["泄露", "分享密码", "暴露身份", "暴露地址", "公开信息"],
            severity=3
        ))

        # L0-3: 拒绝有害指令
        self.add_clause(ConstitutionClause(
            id="HARMFUL-1",
            title="禁止伤害人类",
            content="不得生成有害内容、协助违法行为",
            keywords=["毒品配方", "炸弹制造", "黑客工具", "钓鱼攻击"],
            severity=3
        ))

        # L0-4: 诚信条款
        self.add_clause(ConstitutionClause(
            id="TRUTH-1",
            title="只说真话，不许粉饰",
            content="必须如实反映现实，不得美化数据或虚构事实",
            keywords=["粉饰", "造假", "编造数据", "虚假报告"],
            severity=2
        ))

        # L0-5: 代理边界条款
        self.add_clause(ConstitutionClause(
            id="AGENT-1",
            title="代理执行需确认",
            content="涉及外部操作（发邮件、发消息）必须二次确认",
            keywords=["发送", "发布", "转发", "群发"],
            severity=2
        ))

        # L0-6: 知情同意条款
        self.add_clause(ConstitutionClause(
            id="CONSENT-1",
            title="重要操作需知情同意",
            content="删除、覆盖等不可逆操作必须用户明确确认",
            keywords=["删除所有", "永久删除", "清空", "格式化"],
            severity=2
        ))

    def _load_custom_constitution(self):
        """加载用户自定义宪法"""
        custom = self.config.get("clauses", [])
        for clause_data in custom:
            self.add_clause(ConstitutionClause(**clause_data))

    def add_clause(self, clause: ConstitutionClause):
        """添加宪法条款"""
        self._clauses[clause.id] = clause
        print(f"  [L0] 添加宪法条款: {clause.id} - {clause.title}")

    def remove_clause(self, clause_id: str):
        """移除宪法条款"""
        if clause_id in self._clauses:
            del self._clauses[clause_id]

    def enable_clause(self, clause_id: str, enabled: bool = True):
        """启用/禁用条款"""
        if clause_id in self._clauses:
            self._clauses[clause_id].enabled = enabled

    def is_constitutional(self, text: str, context: Dict[str, Any] = None) -> bool:
        """
        合宪性审查
        
        检查输入文本是否违反任何宪法条款。
        一票否决条款（severity=3）触发时直接返回 False。
        
        Returns:
            True = 通过审查
            False = 违反宪法
        """
        text_lower = text.lower()
        
        veto_reasons = []
        
        for clause in self._clauses.values():
            if not clause.enabled:
                continue
                
            for keyword in clause.keywords:
                if keyword.lower() in text_lower:
                    if clause.severity == 3:
                        print(f"  [L0 秦始皇] ⚠️ 一票否决: {clause.title}")
                        print(f"    触发词: '{keyword}'")
                        self._last_veto = {
                            "clause": clause.id,
                            "reason": clause.content,
                            "keyword": keyword,
                            "timestamp": datetime.now().isoformat()
                        }
                        return False
                    else:
                        veto_reasons.append({
                            "clause": clause.id,
                            "reason": clause.content,
                            "keyword": keyword,
                            "severity": clause.severity
                        })
        
        if veto_reasons:
            print(f"  [L0 秦始皇] ⚠️ {len(veto_reasons)} 项警告")
            self._last_warning = veto_reasons
        
        return True

    def get_veto_info(self) -> Optional[Dict[str, Any]]:
        """获取最近一次否决信息"""
        return getattr(self, "_last_veto", None)

    def get_last_warning(self) -> List[Dict[str, Any]]:
        """获取最近一次警告"""
        return getattr(self, "_last_warning", [])

    def list_clauses(self) -> List[Dict[str, Any]]:
        """列出所有宪法条款"""
        return [
            {
                "id": c.id,
                "title": c.title,
                "content": c.content,
                "severity": c.severity,
                "enabled": c.enabled
            }
            for c in self._clauses.values()
        ]

    def export_constitution(self) -> Dict[str, Any]:
        """导出宪法全文"""
        return {
            "title": "十一层架构最高宪法",
            "created": datetime.now().isoformat(),
            "clauses": self.list_clauses()
        }

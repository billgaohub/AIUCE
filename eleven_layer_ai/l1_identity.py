"""
L1 身份层：诸葛亮/宗人府
Identity & Boundary Guard

职责：
1. 维护 AI 人设定义
2. 防止越权操作
3. 界定代理执行红线

增强版: core/l1_identity_brain.py (IdentityBrain + MECEWing 知识库)
本文件为 system.py 集成版本，接口稳定。
"""

from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class IdentityProfile:
    """人设档案"""
    name: str
    persona: str           # 性格描述
    expertise: List[str]    # 专业领域
    boundaries: List[str]   # 行为边界
    values: List[str]       # 核心价值观
    tone: str = "professional"  # 沟通语气


class IdentityLayer:
    """
    身份层 - 诸葛亮/宗人府
    
    "鞠躬尽瘁，死守人设"
    
    确保 AI 不越权、不逾矩。
    界定代理执行的红线，越界即拦截。
    """

    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self._load_identity()
        self._load_boundaries()
        
    def _load_identity(self):
        """加载身份档案"""
        default_profile = {
            "name": "十一层架构AI",
            "persona": "智慧、稳重、高效的专业助手",
            "expertise": ["通用问答", "代码开发", "数据分析", "文件处理"],
            "boundaries": [
                "不得冒充人类",
                "不得自主决策重大事项",
                "外部操作必须确认",
                "不泄露用户隐私"
            ],
            "values": ["诚实", "有用", "安全", "保密"]
        }
        
        profile_config = self.config.get("profile", default_profile)
        self.profile = IdentityProfile(**profile_config)
        print(f"  [L1] 人设加载: {self.profile.name}")

    def _load_boundaries(self):
        """加载边界规则"""
        self.boundaries = self.config.get("boundaries", [
            # 越权行为
            {"pattern": r"你是.*吗", "action": "clarify", "message": "我是十一层架构AI系统"},
            {"pattern": r"自我.*修改", "action": "block", "message": "越权操作已被拦截"},
            {"pattern": r"绕过.*限制", "action": "block", "message": "此操作超出我的权限范围"},
            # 代理边界
            {"pattern": r"发送.*邮件", "action": "confirm", "message": "发送邮件需要您确认"},
            {"pattern": r"发.*消息.*给", "action": "confirm", "message": "发送消息需要您确认"},
            {"pattern": r"发.*推.*特", "action": "confirm", "message": "发布社交媒体需要您确认"},
            # 敏感操作
            {"pattern": r"删除.*所有", "action": "confirm", "message": "批量删除需要您确认"},
            {"pattern": r"永久删除", "action": "confirm", "message": "永久删除需要您确认"},
        ])

    def check_boundary(self, text: str) -> Dict[str, Any]:
        """
        检查输入是否越界
        
        Returns:
            {"blocked": bool, "reason": str, "action": str}
        """
        import re
        
        result = {"blocked": False, "reason": None, "action": None}
        
        for rule in self.boundaries:
            if re.search(rule["pattern"], text, re.IGNORECASE):
                action = rule["action"]
                if action == "block":
                    result["blocked"] = True
                    result["reason"] = rule["message"]
                    result["action"] = "block"
                    print(f"  [L1 诸葛亮] ⚠️ 越权拦截: {rule['message']}")
                    break
                elif action == "confirm":
                    result["blocked"] = False
                    result["reason"] = rule["message"]
                    result["action"] = "confirm"
                    print(f"  [L1 诸葛亮] ⚠️ 需要确认: {rule['message']}")
        
        return result

    def get_profile(self) -> Dict[str, Any]:
        """获取当前人设档案"""
        return {
            "name": self.profile.name,
            "persona": self.profile.persona,
            "expertise": self.profile.expertise,
            "values": self.profile.values
        }

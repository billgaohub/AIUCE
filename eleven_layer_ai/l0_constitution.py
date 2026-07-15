"""
L0 意志层：秦始皇/御书房
Constitution Engine - 最高宪法，一票否决权

独立入口文件，封装 core/constitution.py

职责：
1. 存放最高宪法条款
2. 对所有指令进行合宪性审查
3. 一票否决任何偏离最高意志的指令
"""

from typing import Dict, Any

# 从 core 导入完整实现
try:
    from .core.constitution import Constitution, ConstitutionClause
except ImportError:
    from core.constitution import Constitution, ConstitutionClause


class L0ConstitutionLayer:
    """
    L0 意志层 - 秦始皇/御书房
    
    最高仲裁者，一票否决权持有者。
    任何指令在进入后续层级之前，必须通过宪法审查。
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.constitution = Constitution(config)
        self._name = "秦始皇"
        self._department = "御书房"
    
    def is_constitutional(self, text: str, context: Dict[str, Any] = None) -> bool:
        """
        合宪性审查
        
        Args:
            text: 待审查的文本
            context: 上下文信息
            
        Returns:
            True = 通过审查，False = 触发否决
        """
        return self.constitution.is_constitutional(text, context)
    
    def get_veto_info(self) -> Dict[str, Any]:
        """获取最近否决信息"""
        return self.constitution.get_veto_info()
    
    def add_clause(self, clause: ConstitutionClause):
        """添加宪法条款"""
        self.constitution.add_clause(clause)
    
    def list_clauses(self) -> list:
        """列出所有条款"""
        return self.constitution.list_clauses()
    
    def export_constitution(self) -> Dict[str, Any]:
        """导出宪法全文"""
        return self.constitution.export_constitution()


# 便捷导出
__all__ = ['L0ConstitutionLayer', 'Constitution', 'ConstitutionClause']

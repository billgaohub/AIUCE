"""
L9 代理层：韩信/锦衣卫
Agent Execution Layer - 跨设备执行

职责：
1. 皇帝的直属执行器
2. 跨设备抓取、物理工具调度
3. 多多益善，多体协同
4. 不问过程，只问结果
"""

from typing import Dict, Any, List, Optional, Callable
from dataclasses import dataclass, field
from datetime import datetime
import json
import os


@dataclass
class Tool:
    """工具定义"""
    tool_id: str
    name: str
    description: str
    category: str  # file, network, system, device...
    permissions: List[str]  # 所需权限
    enabled: bool = True
    handler: Callable = None


@dataclass
class ExecutionResult:
    """执行结果"""
    execution_id: str
    tool_id: str
    success: bool
    output: Any
    error: str = ""
    duration_ms: int = 0
    timestamp: str = ""


class AgentLayer:
    """
    代理层 - 韩信/锦衣卫
    
    "多多益善，多体协同"
    
    负责跨设备、跨工具的物理抓取与调度。
    接收 L5 的决策，在物理世界执行。
    """

    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.tools: Dict[str, Tool] = {}
        self.execution_history: List[ExecutionResult] = []
        
        self._init_tools()

    def _init_tools(self):
        """初始化可用工具"""
        default_tools = [
            Tool(
                tool_id="file_read",
                name="文件读取",
                description="读取文件内容",
                category="file",
                permissions=["file:read"]
            ),
            Tool(
                tool_id="file_write",
                name="文件写入",
                description="创建或覆盖文件",
                category="file",
                permissions=["file:write"]
            ),
            Tool(
                tool_id="file_delete",
                name="文件删除",
                description="移动文件到回收站（安全删除）",
                category="file",
                permissions=["file:delete"]
            ),
            Tool(
                tool_id="exec_command",
                name="执行命令",
                description="执行 shell 命令",
                category="system",
                permissions=["system:exec"]
            ),
            Tool(
                tool_id="web_search",
                name="网络搜索",
                description="搜索互联网",
                category="network",
                permissions=["network:read"]
            ),
            Tool(
                tool_id="web_fetch",
                name="网页抓取",
                description="获取网页内容",
                category="network",
                permissions=["network:read"]
            ),
            Tool(
                tool_id="send_email",
                name="发送邮件",
                description="发送电子邮件",
                category="communication",
                permissions=["email:send"]
            ),
            Tool(
                tool_id="calendar_read",
                name="读取日历",
                description="获取日历事件",
                category="device",
                permissions=["calendar:read"]
            ),
            Tool(
                tool_id="calendar_write",
                name="写入日历",
                description="创建日历事件",
                category="device",
                permissions=["calendar:write"]
            ),
            Tool(
                tool_id="take_screenshot",
                name="截图",
                description="拍摄屏幕截图",
                category="device",
                permissions=["device:screenshot"]
            ),
        ]
        
        for tool in default_tools:
            self.tools[tool.tool_id] = tool
        
        print(f"  [L9] 加载 {len(self.tools)} 个工具")

    def execute(
        self,
        decision: Dict[str, Any],
        model_response: Any
    ) -> Dict[str, Any]:
        """
        执行决策
        
        根据决策内容，调度相应工具执行。
        """
        if not decision.get("requires_action"):
            return {"executed": False, "reason": "无需执行"}
        
        action = decision.get("action", "")
        
        # 分析需要的工具
        required_tools = self._analyze_action(action)
        
        results = []
        for tool_id in required_tools:
            result = self._execute_tool(tool_id, decision, model_response)
            results.append(result)
            
            if not result.success and decision.get("risk_level") == "high":
                # 高风险操作失败则停止
                break
        
        # 汇总结果
        success_count = len([r for r in results if r.success])
        
        summary = {
            "executed": True,
            "total_tools": len(required_tools),
            "success_count": success_count,
            "results": [
                {
                    "tool": r.tool_id,
                    "success": r.success,
                    "output": str(r.output)[:200] if r.output else None,
                    "error": r.error
                }
                for r in results
            ]
        }
        
        print(f"  [L9 韩信] ⚔️ 执行完成: {success_count}/{len(required_tools)} 成功")
        
        return summary

    def _analyze_action(self, action: str) -> List[str]:
        """分析行动需要的工具"""
        tool_mapping = {
            "读取": ["file_read"],
            "写入": ["file_write"],
            "创建": ["file_write"],
            "生成": ["file_write"],
            "删除": ["file_delete"],
            "搜索": ["web_search"],
            "查询": ["web_fetch"],
            "发送": ["send_email"],
            "截图": ["take_screenshot"],
            "日历": ["calendar_read", "calendar_write"],
            "执行": ["exec_command"],
            "运行": ["exec_command"],
        }
        
        needed = []
        for keyword, tool_ids in tool_mapping.items():
            if keyword in action:
                for tid in tool_ids:
                    if tid not in needed:
                        needed.append(tid)
        
        # 默认：如果分析不出，至少执行命令
        if not needed:
            needed = ["exec_command"]
        
        return needed

    def _execute_tool(
        self,
        tool_id: str,
        decision: Dict[str, Any],
        model_response: Any
    ) -> ExecutionResult:
        """执行单个工具"""
        tool = self.tools.get(tool_id)
        if not tool:
            return ExecutionResult(
                execution_id=f"exec-{datetime.now().strftime('%Y%m%d%H%M%S')}",
                tool_id=tool_id,
                success=False,
                output=None,
                error=f"工具不存在: {tool_id}"
            )
        
        if not tool.enabled:
            return ExecutionResult(
                execution_id=f"exec-{datetime.now().strftime('%Y%m%d%H%M%S')}",
                tool_id=tool_id,
                success=False,
                output=None,
                error=f"工具已禁用: {tool_id}"
            )
        
        start_time = datetime.now()
        
        try:
            # 调用工具处理器
            if tool.handler:
                output = tool.handler(decision, model_response)
            else:
                # 默认处理器
                output = self._default_handler(tool, decision)
            
            success = True
            error = ""
            
        except Exception as e:
            output = None
            success = False
            error = str(e)
        
        end_time = datetime.now()
        
        result = ExecutionResult(
            execution_id=f"exec-{datetime.now().strftime('%Y%m%d%H%M%S')}",
            tool_id=tool_id,
            success=success,
            output=output,
            error=error,
            duration_ms=int((end_time - start_time).total_seconds() * 1000),
            timestamp=datetime.now().isoformat()
        )
        
        self.execution_history.append(result)
        
        return result

    def _default_handler(self, tool: Tool, decision: Dict[str, Any]) -> Any:
        """默认工具处理器"""
        return {
            "tool": tool.name,
            "status": "executed",
            "action": decision.get("action")
        }

    def register_tool(self, tool: Tool):
        """注册新工具"""
        self.tools[tool.tool_id] = tool

    def unregister_tool(self, tool_id: str):
        """注销工具"""
        if tool_id in self.tools:
            del self.tools[tool_id]

    def enable_tool(self, tool_id: str, enabled: bool = True):
        """启用/禁用工具"""
        if tool_id in self.tools:
            self.tools[tool_id].enabled = enabled

    def list_tools(self) -> List[Dict[str, Any]]:
        """列出所有工具"""
        return [
            {
                "id": t.tool_id,
                "name": t.name,
                "description": t.description,
                "category": t.category,
                "enabled": t.enabled
            }
            for t in self.tools.values()
        ]

    def get_execution_history(self, limit: int = 50) -> List[Dict[str, Any]]:
        """获取执行历史"""
        history = self.execution_history[-limit:]
        return [
            {
                "id": r.execution_id,
                "tool": r.tool_id,
                "success": r.success,
                "timestamp": r.timestamp,
                "duration_ms": r.duration_ms
            }
            for r in reversed(history)
        ]

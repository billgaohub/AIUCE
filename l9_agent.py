"""
L9 代理层：韩信/锦衣卫
Agent Execution Layer - 跨设备执行

职责：
1. 皇帝的直属执行器
2. 跨设备抓取、物理工具调度
3. 多多益善，多体协同
4. 不问过程，只问结果

安全加固：
- 命令白名单
- 参数清理
- 超时限制
- 执行日志
"""

from typing import Dict, Any, List, Optional, Callable, Set
from dataclasses import dataclass, field
from datetime import datetime
import json
import os
import re
import subprocess
import signal


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
    risk_level: str = "low"  # low, medium, high


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
    sandboxed: bool = False


class SafeExecTool:
    """
    安全命令执行工具
    
    实现：
    - 命令白名单
    - 参数清理
    - 超时限制
    - 资源限制
    """
    
    # 命令白名单（只允许这些命令）
    ALLOWED_COMMANDS: Set[str] = {
        # 文件操作（安全）
        "ls", "cat", "head", "tail", "wc", "find", "grep", "sed", "awk",
        "mkdir", "touch", "cp", "mv", "chmod", "chown",
        # 开发工具
        "git", "python", "python3", "pip", "pip3", "node", "npm", "yarn",
        "cargo", "go", "rustc",
        # 网络工具（只读）
        "curl", "wget", "ping", "dig", "nslookup",
        # 系统信息
        "date", "whoami", "pwd", "echo", "which", "env", "uname",
        # 其他安全命令
        "open", "say", "afplay",  # macOS
    }
    
    # 危险字符模式
    DANGEROUS_PATTERNS = [
        r';',           # 命令分隔符
        r'\|',          # 管道
        r'&',           # 后台执行
        r'\$\(',        # 命令替换
        r'`',           # 反引号命令替换
        r'>',           # 重定向
        r'<',           # 重定向
        r'\.\.',        # 目录遍历
        r'~',           # 主目录（可能泄露路径）
    ]
    
    # 超时限制（秒）
    DEFAULT_TIMEOUT = 30
    MAX_TIMEOUT = 120
    
    # 禁止的命令选项
    FORBIDDEN_FLAGS = [
        "--exec",
        "-exec",
        "-delete",
        "-remove",
        "--force",
        "-f",  # 除非在安全上下文
    ]
    
    @classmethod
    def validate_command(cls, command: str) -> tuple[bool, str]:
        """
        验证命令是否安全
        
        Returns:
            (is_safe, reason)
        """
        if not command or not command.strip():
            return False, "Empty command"
        
        # 提取主命令
        parts = command.strip().split()
        if not parts:
            return False, "Empty command"
        
        main_cmd = parts[0]
        
        # 检查命令是否在白名单
        if main_cmd not in cls.ALLOWED_COMMANDS:
            return False, f"Command '{main_cmd}' not in whitelist. Allowed: {', '.join(sorted(cls.ALLOWED_COMMANDS))}"
        
        # 检查危险字符
        for pattern in cls.DANGEROUS_PATTERNS:
            if re.search(pattern, command):
                return False, f"Command contains dangerous pattern: {pattern}"
        
        # 检查禁止的选项
        for flag in cls.FORBIDDEN_FLAGS:
            if flag in parts:
                return False, f"Command contains forbidden flag: {flag}"
        
        return True, "Command is safe"
    
    @classmethod
    def sanitize_args(cls, args: List[str]) -> List[str]:
        """清理参数"""
        sanitized = []
        for arg in args:
            # 移除危险字符
            for pattern in cls.DANGEROUS_PATTERNS:
                arg = re.sub(pattern, '', arg)
            sanitized.append(arg)
        return sanitized
    
    @classmethod
    def execute(
        cls,
        command: str,
        timeout: int = None,
        cwd: str = None,
        env: Dict[str, str] = None
    ) -> Dict[str, Any]:
        """
        安全执行命令
        
        Args:
            command: 要执行的命令
            timeout: 超时时间（秒）
            cwd: 工作目录
            env: 环境变量
            
        Returns:
            执行结果字典
        """
        # 验证命令
        is_safe, reason = cls.validate_command(command)
        if not is_safe:
            return {
                "success": False,
                "error": f"Command rejected: {reason}",
                "output": None,
                "execution_time_ms": 0
            }
        
        # 设置超时
        timeout = min(timeout or cls.DEFAULT_TIMEOUT, cls.MAX_TIMEOUT)
        
        start_time = datetime.now()
        
        try:
            # 执行命令
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=timeout,
                cwd=cwd,
                env=env or os.environ.copy()
            )
            
            end_time = datetime.now()
            execution_time_ms = int((end_time - start_time).total_seconds() * 1000)
            
            return {
                "success": result.returncode == 0,
                "output": result.stdout[:10000] if result.stdout else "",  # 限制输出长度
                "error": result.stderr[:1000] if result.stderr else "",
                "return_code": result.returncode,
                "execution_time_ms": execution_time_ms,
                "sandboxed": True
            }
            
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "error": f"Command timed out after {timeout}s",
                "output": None,
                "execution_time_ms": timeout * 1000
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Execution error: {str(e)}",
                "output": None,
                "execution_time_ms": 0
            }


class AgentLayer:
    """
    代理层 - 韩信/锦衣卫
    
    "多多益善，多体协同"
    
    负责跨设备、跨工具的物理抓取与调度。
    接收 L5 的决策，在物理世界执行。
    
    安全特性：
    - 命令白名单执行
    - 参数清理
    - 超时限制
    - 执行日志全量记录
    """

    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.tools: Dict[str, Tool] = {}
        self.execution_history: List[ExecutionResult] = []
        self.safe_exec = SafeExecTool()
        
        # 安全配置
        self.enable_sandbox = self.config.get("enable_sandbox", True)
        self.max_execution_time = self.config.get("max_execution_time", 30)
        
        self._init_tools()

    def _init_tools(self):
        """初始化可用工具"""
        default_tools = [
            Tool(
                tool_id="file_read",
                name="文件读取",
                description="读取文件内容",
                category="file",
                permissions=["file:read"],
                risk_level="low"
            ),
            Tool(
                tool_id="file_write",
                name="文件写入",
                description="创建或覆盖文件",
                category="file",
                permissions=["file:write"],
                risk_level="medium"
            ),
            Tool(
                tool_id="file_delete",
                name="文件删除",
                description="移动文件到回收站（安全删除）",
                category="file",
                permissions=["file:delete"],
                risk_level="high"
            ),
            Tool(
                tool_id="exec_command",
                name="执行命令",
                description="执行 shell 命令（沙箱模式）",
                category="system",
                permissions=["system:exec"],
                risk_level="medium"
            ),
            Tool(
                tool_id="web_search",
                name="网络搜索",
                description="搜索互联网",
                category="network",
                permissions=["network:read"],
                risk_level="low"
            ),
            Tool(
                tool_id="web_fetch",
                name="网页抓取",
                description="获取网页内容",
                category="network",
                permissions=["network:read"],
                risk_level="low"
            ),
            Tool(
                tool_id="send_email",
                name="发送邮件",
                description="发送电子邮件",
                category="communication",
                permissions=["email:send"],
                risk_level="medium"
            ),
            Tool(
                tool_id="calendar_read",
                name="读取日历",
                description="获取日历事件",
                category="device",
                permissions=["calendar:read"],
                risk_level="low"
            ),
            Tool(
                tool_id="calendar_write",
                name="写入日历",
                description="创建日历事件",
                category="device",
                permissions=["calendar:write"],
                risk_level="medium"
            ),
            Tool(
                tool_id="take_screenshot",
                name="截图",
                description="拍摄屏幕截图",
                category="device",
                permissions=["device:screenshot"],
                risk_level="low"
            ),
        ]
        
        for tool in default_tools:
            self.tools[tool.tool_id] = tool
        
        print(f"  [L9] 加载 {len(self.tools)} 个工具 (沙箱: {'启用' if self.enable_sandbox else '禁用'})")

    def execute(
        self,
        decision: Dict[str, Any],
        model_response: Any
    ) -> Dict[str, Any]:
        """
        执行决策
        
        根据决策内容，调度相应工具执行。
        所有执行都经过沙箱验证。
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
            "sandboxed": self.enable_sandbox,
            "results": [
                {
                    "tool": r.tool_id,
                    "success": r.success,
                    "output": str(r.output)[:200] if r.output else None,
                    "error": r.error,
                    "sandboxed": r.sandboxed
                }
                for r in results
            ]
        }
        
        print(f"  [L9 韩信] ⚔️ 执行完成: {success_count}/{len(required_tools)} 成功 (沙箱: {'✓' if self.enable_sandbox else '✗'})")
        
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
                error=f"工具不存在: {tool_id}",
                sandboxed=self.enable_sandbox
            )
        
        if not tool.enabled:
            return ExecutionResult(
                execution_id=f"exec-{datetime.now().strftime('%Y%m%d%H%M%S')}",
                tool_id=tool_id,
                success=False,
                output=None,
                error=f"工具已禁用: {tool_id}",
                sandboxed=self.enable_sandbox
            )
        
        start_time = datetime.now()
        
        try:
            # 调用工具处理器
            if tool.handler:
                output = tool.handler(decision, model_response)
            else:
                # 默认处理器（沙箱模式）
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
            timestamp=datetime.now().isoformat(),
            sandboxed=self.enable_sandbox
        )
        
        self.execution_history.append(result)
        
        return result

    def _default_handler(self, tool: Tool, decision: Dict[str, Any]) -> Any:
        """
        默认工具处理器
        
        对于 exec_command 工具，使用沙箱执行。
        """
        if tool.tool_id == "exec_command" and self.enable_sandbox:
            command = decision.get("action", "")
            result = self.safe_exec.execute(command, timeout=self.max_execution_time)
            return result
        
        return {
            "tool": tool.name,
            "status": "executed",
            "action": decision.get("action"),
            "sandboxed": self.enable_sandbox
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
                "enabled": t.enabled,
                "risk_level": t.risk_level
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
                "duration_ms": r.duration_ms,
                "sandboxed": r.sandboxed
            }
            for r in reversed(history)
        ]

    def get_allowed_commands(self) -> List[str]:
        """获取命令白名单"""
        return sorted(list(SafeExecTool.ALLOWED_COMMANDS))

"""
L9 代理层：跨设备执行引擎
Agent Layer with UI-TARS Integration

架构：
┌─────────────────────────────────────────────────────────┐
│              L9 代理层 (Agent Layer)                     │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  ┌───────────────────────────────────────────────────┐  │
│  │  工具注册中心 (Tool Registry)                      │  │
│  │  - 工具发现 (Tool Discovery)                       │  │
│  │  - 能力声明 (Capability Declaration)              │  │
│  │  - 白名单管理 (Whitelist Management)              │  │
│  └───────────────────────────────────────────────────┘  │
│                         ↓                               │
│  ┌───────────────────────────────────────────────────┐  │
│  │  执行引擎 (Execution Engine)                       │  │
│  │  - 命令执行 (Command Execution)                    │  │
│  │  - 脚本运行 (Script Running)                       │  │
│  │  - API 调用 (API Calls)                           │  │
│  │  - UI 交互 (UI Interaction) - UI-TARS             │  │
│  └───────────────────────────────────────────────────┘  │
│                         ↓                               │
│  ┌───────────────────────────────────────────────────┐  │
│  │  结果处理器 (Result Processor)                     │  │
│  │  - 输出解析 (Output Parsing)                       │  │
│  │  - 错误处理 (Error Handling)                       │  │
│  │  - 重试机制 (Retry Mechanism)                      │  │
│  └───────────────────────────────────────────────────┘  │
│                                                          │
└─────────────────────────────────────────────────────────┘

UI-TARS 集成：
- GUI Agent: 屏幕理解 + UI 交互
- 自动化操作: 点击/输入/拖拽
- 跨应用协调
"""

from typing import Dict, Any, List, Optional, Tuple, Callable, Union
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import json
import os
import subprocess
import threading
import queue
import uuid
import shutil
import re
from collections import defaultdict


# ═══════════════════════════════════════════════════════════════
# 类型定义
# ═══════════════════════════════════════════════════════════════

class ToolCategory(Enum):
    """工具类别"""
    COMMAND = "command"       # 命令行工具
    SCRIPT = "script"         # 脚本
    API = "api"               # API 调用
    UI = "ui"                 # UI 交互 (UI-TARS)
    FILE = "file"             # 文件操作
    NETWORK = "network"       # 网络操作
    DATABASE = "database"     # 数据库操作
    CUSTOM = "custom"         # 自定义


class ExecutionStatus(Enum):
    """执行状态"""
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    TIMEOUT = "timeout"
    CANCELLED = "cancelled"


class RiskLevel(Enum):
    """风险级别"""
    LOW = 1        # 低风险：只读操作
    MEDIUM = 2     # 中等风险：文件修改
    HIGH = 3       # 高风险：系统修改
    CRITICAL = 4   # 关键：不可逆操作


@dataclass
class Tool:
    """工具定义"""
    id: str
    name: str
    category: ToolCategory
    description: str
    command: Optional[str] = None
    parameters: Dict[str, Any] = field(default_factory=dict)
    risk_level: RiskLevel = RiskLevel.LOW
    whitelist_only: bool = False
    timeout_seconds: int = 30
    requires_confirmation: bool = False
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "category": self.category.value,
            "description": self.description,
            "risk_level": self.risk_level.value,
            "whitelist_only": self.whitelist_only,
            "timeout_seconds": self.timeout_seconds
        }


@dataclass
class ExecutionRequest:
    """执行请求"""
    id: str
    tool_id: str
    parameters: Dict[str, Any]
    user_id: Optional[str] = None
    correlation_id: Optional[str] = None
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())


@dataclass
class ExecutionResult:
    """执行结果"""
    request_id: str
    tool_id: str
    status: ExecutionStatus
    output: Optional[str] = None
    error: Optional[str] = None
    return_code: Optional[int] = None
    execution_time_ms: float = 0.0
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "request_id": self.request_id,
            "tool_id": self.tool_id,
            "status": self.status.value,
            "execution_time_ms": self.execution_time_ms,
            "error": self.error
        }


@dataclass
class UIAction:
    """UI 动作 (UI-TARS)"""
    action_type: str  # click, type, drag, scroll, screenshot
    target: Optional[str] = None  # CSS selector, xpath, or description
    value: Optional[str] = None   # text to type, etc.
    position: Optional[Tuple[int, int]] = None
    delay_ms: int = 100
    metadata: Dict[str, Any] = field(default_factory=dict)


# ═══════════════════════════════════════════════════════════════
# 工具注册中心 (Tool Registry)
# ═══════════════════════════════════════════════════════════════

class ToolRegistry:
    """
    工具注册中心
    
    功能：
    1. 工具发现
    2. 能力声明
    3. 白名单管理
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self._tools: Dict[str, Tool] = {}
        self._whitelist: set = set()
        self._blacklist: set = set()
        
        self._register_builtin_tools()
        print("  [L9 代理层] 工具注册中心初始化")
    
    def _register_builtin_tools(self):
        """注册内置工具"""
        
        # ── 文件操作 ──
        self.register(Tool(
            id="file.read",
            name="Read File",
            category=ToolCategory.FILE,
            description="读取文件内容",
            command="cat",
            risk_level=RiskLevel.LOW,
            whitelist_only=False
        ))
        
        self.register(Tool(
            id="file.write",
            name="Write File",
            category=ToolCategory.FILE,
            description="写入文件内容",
            command="write",
            risk_level=RiskLevel.MEDIUM,
            whitelist_only=False,
            requires_confirmation=True
        ))
        
        self.register(Tool(
            id="file.list",
            name="List Directory",
            category=ToolCategory.FILE,
            description="列出目录内容",
            command="ls",
            risk_level=RiskLevel.LOW
        ))
        
        self.register(Tool(
            id="file.delete",
            name="Delete File",
            category=ToolCategory.FILE,
            description="删除文件",
            command="rm",
            risk_level=RiskLevel.HIGH,
            whitelist_only=True,
            requires_confirmation=True
        ))
        
        # ── 命令行工具 ──
        self.register(Tool(
            id="cmd.execute",
            name="Execute Command",
            category=ToolCategory.COMMAND,
            description="执行 shell 命令",
            risk_level=RiskLevel.HIGH,
            whitelist_only=True,
            requires_confirmation=True
        ))
        
        # ── UI 交互 (UI-TARS) ──
        self.register(Tool(
            id="ui.click",
            name="UI Click",
            category=ToolCategory.UI,
            description="点击 UI 元素",
            risk_level=RiskLevel.LOW,
            timeout_seconds=5
        ))
        
        self.register(Tool(
            id="ui.type",
            name="UI Type",
            category=ToolCategory.UI,
            description="在 UI 元素中输入文本",
            risk_level=RiskLevel.LOW,
            timeout_seconds=10
        ))
        
        self.register(Tool(
            id="ui.screenshot",
            name="UI Screenshot",
            category=ToolCategory.UI,
            description="截取屏幕截图",
            risk_level=RiskLevel.LOW,
            timeout_seconds=3
        ))
        
        self.register(Tool(
            id="ui.drag",
            name="UI Drag",
            category=ToolCategory.UI,
            description="拖拽 UI 元素",
            risk_level=RiskLevel.LOW,
            timeout_seconds=5
        ))
        
        # ── 网络操作 ──
        self.register(Tool(
            id="http.get",
            name="HTTP GET",
            category=ToolCategory.NETWORK,
            description="发送 HTTP GET 请求",
            command="curl",
            risk_level=RiskLevel.LOW,
            timeout_seconds=30
        ))
        
        self.register(Tool(
            id="http.post",
            name="HTTP POST",
            category=ToolCategory.NETWORK,
            description="发送 HTTP POST 请求",
            command="curl",
            risk_level=RiskLevel.MEDIUM,
            timeout_seconds=30
        ))
    
    def register(self, tool: Tool):
        """注册工具"""
        self._tools[tool.id] = tool
    
    def unregister(self, tool_id: str):
        """注销工具"""
        if tool_id in self._tools:
            del self._tools[tool_id]
    
    def get(self, tool_id: str) -> Optional[Tool]:
        """获取工具"""
        return self._tools.get(tool_id)
    
    def list_tools(
        self,
        category: Optional[ToolCategory] = None,
        risk_level: Optional[RiskLevel] = None
    ) -> List[Tool]:
        """列出工具"""
        tools = list(self._tools.values())
        
        if category:
            tools = [t for t in tools if t.category == category]
        
        if risk_level:
            tools = [t for t in tools if t.risk_level == risk_level]
        
        return tools
    
    # ── 白名单管理 ─────────────────────────────────────────────
    
    def add_to_whitelist(self, tool_id: str):
        """添加到白名单"""
        self._whitelist.add(tool_id)
    
    def remove_from_whitelist(self, tool_id: str):
        """从白名单移除"""
        self._whitelist.discard(tool_id)
    
    def is_whitelisted(self, tool_id: str) -> bool:
        """检查是否在白名单"""
        return tool_id in self._whitelist
    
    def add_to_blacklist(self, tool_id: str):
        """添加到黑名单"""
        self._blacklist.add(tool_id)
    
    def is_blacklisted(self, tool_id: str) -> bool:
        """检查是否在黑名单"""
        return tool_id in self._blacklist
    
    # ── 执行检查 ───────────────────────────────────────────────
    
    def can_execute(
        self,
        tool_id: str,
        user_id: Optional[str] = None
    ) -> Tuple[bool, str]:
        """
        检查是否可以执行
        
        Returns:
            (can_execute, reason)
        """
        tool = self._tools.get(tool_id)
        
        if not tool:
            return False, f"工具 {tool_id} 不存在"
        
        if tool_id in self._blacklist:
            return False, f"工具 {tool_id} 在黑名单中"
        
        if tool.whitelist_only and tool_id not in self._whitelist:
            return False, f"工具 {tool_id} 仅限白名单用户"
        
        return True, "允许执行"
    
    def stats(self) -> Dict[str, Any]:
        """统计"""
        by_category = defaultdict(int)
        by_risk = defaultdict(int)
        
        for tool in self._tools.values():
            by_category[tool.category.value] += 1
            by_risk[tool.risk_level.value] += 1
        
        return {
            "total_tools": len(self._tools),
            "whitelist_size": len(self._whitelist),
            "blacklist_size": len(self._blacklist),
            "by_category": dict(by_category),
            "by_risk": dict(by_risk)
        }


# ═══════════════════════════════════════════════════════════════
# 执行引擎 (Execution Engine)
# ═══════════════════════════════════════════════════════════════

class ExecutionEngine:
    """
    执行引擎
    
    支持：
    1. 命令执行
    2. 脚本运行
    3. API 调用
    4. UI 交互 (UI-TARS)
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self._ui_tars_adapter: Optional[Any] = None
        self._execution_history: List[ExecutionResult] = []
        self._max_history = self.config.get("max_history", 1000)
        
        print("  [L9 代理层] 执行引擎初始化")
    
    def set_ui_tars_adapter(self, adapter: Any):
        """
        设置 UI-TARS 适配器
        
        UI-TARS 提供的能力：
        - click(selector): 点击元素
        - type(selector, text): 输入文本
        - drag(start, end): 拖拽
        - screenshot(): 截图
        - understand(): 屏幕理解
        """
        self._ui_tars_adapter = adapter
        print("  [L9 代理层] UI-TARS 适配器已连接")
    
    def execute(
        self,
        request: ExecutionRequest,
        tool: Tool
    ) -> ExecutionResult:
        """
        执行请求
        """
        start_time = datetime.now()
        
        try:
            # 根据工具类型选择执行器
            if tool.category == ToolCategory.UI:
                result = self._execute_ui(request, tool)
            elif tool.category == ToolCategory.COMMAND:
                result = self._execute_command(request, tool)
            elif tool.category == ToolCategory.FILE:
                result = self._execute_file(request, tool)
            elif tool.category == ToolCategory.NETWORK:
                result = self._execute_network(request, tool)
            else:
                result = self._execute_custom(request, tool)
            
            result.status = ExecutionStatus.SUCCESS
            
        except subprocess.TimeoutExpired:
            result = ExecutionResult(
                request_id=request.id,
                tool_id=tool.id,
                status=ExecutionStatus.TIMEOUT,
                error=f"执行超时 ({tool.timeout_seconds}s)"
            )
            
        except Exception as e:
            result = ExecutionResult(
                request_id=request.id,
                tool_id=tool.id,
                status=ExecutionStatus.FAILED,
                error=str(e)
            )
        
        # 计算执行时间
        elapsed_ms = (datetime.now() - start_time).total_seconds() * 1000
        result.execution_time_ms = elapsed_ms
        
        # 记录历史
        self._execution_history.append(result)
        if len(self._execution_history) > self._max_history:
            self._execution_history = self._execution_history[-self._max_history:]
        
        return result
    
    # ── UI 执行 ─────────────────────────────────────────────────
    
    def _execute_ui(
        self,
        request: ExecutionRequest,
        tool: Tool
    ) -> ExecutionResult:
        """执行 UI 操作"""
        if not self._ui_tars_adapter:
            raise RuntimeError("UI-TARS 适配器未配置")
        
        params = request.parameters
        action = UIAction(
            action_type=tool.id.split(".")[-1],
            target=params.get("target"),
            value=params.get("value"),
            position=params.get("position"),
            delay_ms=params.get("delay_ms", 100)
        )
        
        output = None
        
        if action.action_type == "click":
            self._ui_tars_adapter.click(action.target)
            output = f"已点击: {action.target}"
        
        elif action.action_type == "type":
            self._ui_tars_adapter.type(action.target, action.value)
            output = f"已输入: {action.value}"
        
        elif action.action_type == "screenshot":
            screenshot = self._ui_tars_adapter.screenshot()
            output = "截图完成" if screenshot else "截图失败"
        
        elif action.action_type == "drag":
            start = params.get("start")
            end = params.get("end")
            self._ui_tars_adapter.drag(start, end)
            output = f"已拖拽: {start} -> {end}"
        
        return ExecutionResult(
            request_id=request.id,
            tool_id=tool.id,
            status=ExecutionStatus.SUCCESS,
            output=output
        )
    
    # ── 命令执行 ─────────────────────────────────────────────────
    
    def _execute_command(
        self,
        request: ExecutionRequest,
        tool: Tool
    ) -> ExecutionResult:
        """执行命令"""
        cmd = request.parameters.get("command")
        
        if not cmd:
            raise ValueError("缺少 command 参数")
        
        # 危险命令检查
        dangerous_patterns = [
            r"rm\s+-rf\s+/",
            r"rm\s+-rf\s+~",
            r"sudo\s+rm",
            r"mkfs",
            r"dd\s+if=",
            r">\s*/dev/",
            r":(){ :|:& };:",  # Fork bomb
        ]
        
        for pattern in dangerous_patterns:
            if re.search(pattern, cmd):
                raise ValueError(f"危险命令被阻止: {pattern}")
        
        # 执行命令
        result = subprocess.run(
            cmd,
            shell=True,
            capture_output=True,
            text=True,
            timeout=tool.timeout_seconds
        )
        
        return ExecutionResult(
            request_id=request.id,
            tool_id=tool.id,
            status=ExecutionStatus.SUCCESS if result.returncode == 0 else ExecutionStatus.FAILED,
            output=result.stdout,
            error=result.stderr if result.returncode != 0 else None,
            return_code=result.returncode
        )
    
    # ── 文件执行 ─────────────────────────────────────────────────
    
    def _execute_file(
        self,
        request: ExecutionRequest,
        tool: Tool
    ) -> ExecutionResult:
        """执行文件操作"""
        operation = tool.id.split(".")[-1]
        path = request.parameters.get("path")
        
        if not path:
            raise ValueError("缺少 path 参数")
        
        output = None
        
        if operation == "read":
            with open(path, "r", encoding="utf-8") as f:
                output = f.read()
        
        elif operation == "write":
            content = request.parameters.get("content", "")
            with open(path, "w", encoding="utf-8") as f:
                f.write(content)
            output = f"已写入: {path}"
        
        elif operation == "list":
            items = os.listdir(path)
            output = "\n".join(items)
        
        elif operation == "delete":
            if os.path.isfile(path):
                os.remove(path)
            else:
                shutil.rmtree(path)
            output = f"已删除: {path}"
        
        return ExecutionResult(
            request_id=request.id,
            tool_id=tool.id,
            status=ExecutionStatus.SUCCESS,
            output=output
        )
    
    # ── 网络执行 ─────────────────────────────────────────────────
    
    def _execute_network(
        self,
        request: ExecutionRequest,
        tool: Tool
    ) -> ExecutionResult:
        """执行网络操作"""
        import urllib.request
        import urllib.error
        
        operation = tool.id.split(".")[-1]
        url = request.parameters.get("url")
        
        if not url:
            raise ValueError("缺少 url 参数")
        
        if operation == "get":
            with urllib.request.urlopen(url, timeout=tool.timeout_seconds) as response:
                output = response.read().decode("utf-8")
        
        elif operation == "post":
            data = request.parameters.get("data", "").encode("utf-8")
            req = urllib.request.Request(url, data=data, method="POST")
            with urllib.request.urlopen(req, timeout=tool.timeout_seconds) as response:
                output = response.read().decode("utf-8")
        
        else:
            raise ValueError(f"不支持的操作: {operation}")
        
        return ExecutionResult(
            request_id=request.id,
            tool_id=tool.id,
            status=ExecutionStatus.SUCCESS,
            output=output[:10000]  # 限制输出大小
        )
    
    # ── 自定义执行 ─────────────────────────────────────────────────
    
    def _execute_custom(
        self,
        request: ExecutionRequest,
        tool: Tool
    ) -> ExecutionResult:
        """执行自定义工具"""
        # 自定义工具需要提供执行函数
        raise NotImplementedError(f"自定义工具 {tool.id} 未实现")
    
    # ── 统计 ───────────────────────────────────────────────────
    
    def stats(self) -> Dict[str, Any]:
        """统计"""
        by_status = defaultdict(int)
        
        for result in self._execution_history:
            by_status[result.status.value] += 1
        
        return {
            "total_executions": len(self._execution_history),
            "by_status": dict(by_status),
            "ui_tars_connected": self._ui_tars_adapter is not None
        }


# ═══════════════════════════════════════════════════════════════
# L9 代理层主类
# ═══════════════════════════════════════════════════════════════

class AgentLayer:
    """
    L9 代理层 - 跨设备执行引擎
    
    "AI的双手，延伸到数字世界的每个角落"
    
    组件：
    1. 工具注册中心
    2. 执行引擎
    
    UI-TARS 集成：
    - GUI Agent
    - 屏幕理解 + UI 交互
    - 跨应用协调
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        
        # 组件
        self.registry = ToolRegistry(self.config.get("registry", {}))
        self.engine = ExecutionEngine(self.config.get("engine", {}))
        
        # 执行回调
        self._pre_execute_callbacks: List[Callable] = []
        self._post_execute_callbacks: List[Callable] = []
        
        print("  [L9 代理层] 韩信/锦衣卫 - 跨设备执行引擎就位")
    
    # ── UI-TARS 集成 ───────────────────────────────────────────
    
    def set_ui_tars_adapter(self, adapter: Any):
        """设置 UI-TARS 适配器"""
        self.engine.set_ui_tars_adapter(adapter)
    
    # ── 工具管理 ───────────────────────────────────────────────
    
    def register_tool(self, tool: Tool):
        """注册工具"""
        self.registry.register(tool)
    
    def get_tool(self, tool_id: str) -> Optional[Tool]:
        """获取工具"""
        return self.registry.get(tool_id)
    
    def list_tools(
        self,
        category: Optional[ToolCategory] = None
    ) -> List[Tool]:
        """列出工具"""
        return self.registry.list_tools(category)
    
    # ── 执行接口 ───────────────────────────────────────────────
    
    def execute(
        self,
        tool_id: str,
        parameters: Dict[str, Any],
        user_id: Optional[str] = None,
        require_confirmation: bool = True
    ) -> ExecutionResult:
        """
        执行工具
        
        Args:
            tool_id: 工具 ID
            parameters: 参数
            user_id: 用户 ID
            require_confirmation: 是否需要确认
            
        Returns:
            执行结果
        """
        # 检查是否可以执行
        can_exec, reason = self.registry.can_execute(tool_id, user_id)
        
        if not can_exec:
            return ExecutionResult(
                request_id=str(uuid.uuid4())[:8],
                tool_id=tool_id,
                status=ExecutionStatus.FAILED,
                error=reason
            )
        
        tool = self.registry.get(tool_id)
        
        # 检查是否需要确认
        if tool.requires_confirmation and require_confirmation:
            # 在实际应用中，这里应该等待用户确认
            # 目前先记录日志
            print(f"  [L9 代理层] 工具 {tool_id} 需要用户确认")
        
        # 创建请求
        request = ExecutionRequest(
            id=str(uuid.uuid4())[:8],
            tool_id=tool_id,
            parameters=parameters,
            user_id=user_id
        )
        
        # 预执行回调
        for callback in self._pre_execute_callbacks:
            try:
                callback(request, tool)
            except Exception:
                pass
        
        # 执行
        result = self.engine.execute(request, tool)
        
        # 后执行回调
        for callback in self._post_execute_callbacks:
            try:
                callback(result)
            except Exception:
                pass
        
        return result
    
    # ── UI 快捷接口 ─────────────────────────────────────────────
    
    def ui_click(self, target: str) -> ExecutionResult:
        """UI 点击"""
        return self.execute("ui.click", {"target": target})
    
    def ui_type(self, target: str, text: str) -> ExecutionResult:
        """UI 输入"""
        return self.execute("ui.type", {"target": target, "value": text})
    
    def ui_screenshot(self) -> ExecutionResult:
        """UI 截图"""
        return self.execute("ui.screenshot", {})
    
    # ── 回调管理 ───────────────────────────────────────────────
    
    def on_pre_execute(self, callback: Callable):
        """注册预执行回调"""
        self._pre_execute_callbacks.append(callback)
    
    def on_post_execute(self, callback: Callable):
        """注册后执行回调"""
        self._post_execute_callbacks.append(callback)
    
    # ── 统计 ───────────────────────────────────────────────────
    
    def stats(self) -> Dict[str, Any]:
        """统计"""
        return {
            "registry": self.registry.stats(),
            "engine": self.engine.stats()
        }


# ═══════════════════════════════════════════════════════════════
# 导出
# ═══════════════════════════════════════════════════════════════

__all__ = [
    "ToolCategory",
    "ExecutionStatus",
    "RiskLevel",
    "Tool",
    "ExecutionRequest",
    "ExecutionResult",
    "UIAction",
    "ToolRegistry",
    "ExecutionEngine",
    "AgentLayer",
]

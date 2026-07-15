"""
AIUCE 统一日志与错误处理模块
Unified Logging and Error Handling
"""

import logging
import sys
import os
from typing import Optional, Dict, Any
from datetime import datetime
from functools import wraps
import traceback

# ═══════════════════════════════════════════════════════════════
# 日志配置
# ═══════════════════════════════════════════════════════════════

def setup_logging(
    level: str = "INFO",
    log_file: Optional[str] = None,
    format_string: Optional[str] = None
) -> logging.Logger:
    """
    配置日志系统
    
    Args:
        level: 日志级别 (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: 日志文件路径（可选）
        format_string: 自定义格式字符串
    
    Returns:
        配置好的根日志器
    """
    # 确定日志级别
    log_level = getattr(logging, level.upper(), logging.INFO)
    
    # 默认格式
    if format_string is None:
        format_string = "[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s"
    
    # 创建格式器
    formatter = logging.Formatter(
        format_string,
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    
    # 配置根日志器
    root_logger = logging.getLogger("aiuce")
    root_logger.setLevel(log_level)
    
    # 清除已有的处理器
    root_logger.handlers.clear()
    
    # 控制台处理器
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level)
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)
    
    # 文件处理器（可选）
    if log_file:
        os.makedirs(os.path.dirname(log_file), exist_ok=True)
        file_handler = logging.FileHandler(log_file, encoding="utf-8")
        file_handler.setLevel(log_level)
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)
    
    return root_logger


def get_logger(name: str) -> logging.Logger:
    """获取指定名称的日志器"""
    return logging.getLogger(f"aiuce.{name}")


# 初始化默认日志配置
def init_default_logging():
    """初始化默认日志配置"""
    log_level = os.environ.get("AIUCE_LOG_LEVEL", "INFO")
    log_file = os.environ.get("AIUCE_LOG_FILE", None)
    return setup_logging(level=log_level, log_file=log_file)


# ═══════════════════════════════════════════════════════════════
# 统一错误处理
# ═══════════════════════════════════════════════════════════════

class AIUCEError(Exception):
    """AIUCE 基础异常"""
    
    def __init__(
        self,
        message: str,
        error_code: str = "UNKNOWN",
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message)
        self.message = message
        self.error_code = error_code
        self.details = details or {}
        self.timestamp = datetime.now().isoformat()
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "error": True,
            "error_code": self.error_code,
            "message": self.message,
            "details": self.details,
            "timestamp": self.timestamp
        }


class ConstitutionViolationError(AIUCEError):
    """宪法违反异常（L0）"""
    
    def __init__(self, clause_id: str, reason: str):
        super().__init__(
            message=f"宪法违反: {reason}",
            error_code="CONSTITUTION_VIOLATION",
            details={"clause_id": clause_id}
        )


class IdentityBoundaryError(AIUCEError):
    """身份边界异常（L1）"""
    
    def __init__(self, boundary: str, reason: str):
        super().__init__(
            message=f"身份边界违反: {reason}",
            error_code="IDENTITY_BOUNDARY",
            details={"boundary": boundary}
        )


class MemoryStorageError(AIUCEError):
    """记忆存储异常（L4）"""
    
    def __init__(self, reason: str, content: str = ""):
        super().__init__(
            message=f"记忆存储失败: {reason}",
            error_code="MEMORY_STORAGE_ERROR",
            details={"content_preview": content[:100]}
        )


class ModelCallError(AIUCEError):
    """模型调用异常（L8）"""
    
    def __init__(self, provider: str, reason: str):
        super().__init__(
            message=f"模型调用失败 [{provider}]: {reason}",
            error_code="MODEL_CALL_ERROR",
            details={"provider": provider}
        )


class ExecutionError(AIUCEError):
    """执行异常（L9）"""
    
    def __init__(self, tool: str, reason: str):
        super().__init__(
            message=f"执行失败 [{tool}]: {reason}",
            error_code="EXECUTION_ERROR",
            details={"tool": tool}
        )


class SandboxSimulationError(AIUCEError):
    """沙盒模拟异常（L10）"""
    
    def __init__(self, scenario: str, reason: str):
        super().__init__(
            message=f"沙盒模拟失败: {reason}",
            error_code="SANDBOX_SIMULATION_ERROR",
            details={"scenario": scenario}
        )


# ═══════════════════════════════════════════════════════════════
# 错误处理装饰器
# ═══════════════════════════════════════════════════════════════

def handle_errors(default_return=None, reraise: bool = False):
    """
    统一错误处理装饰器
    
    Args:
        default_return: 发生错误时的默认返回值
        reraise: 是否重新抛出异常
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            logger = get_logger(func.__module__.split(".")[-1])
            try:
                return func(*args, **kwargs)
            except AIUCEError as e:
                logger.error(f"[{func.__name__}] {e.error_code}: {e.message}")
                if reraise:
                    raise
                return default_return
            except Exception as e:
                logger.error(f"[{func.__name__}] 未预期错误: {e}")
                logger.debug(traceback.format_exc())
                if reraise:
                    raise
                return default_return
        return wrapper
    return decorator


def safe_execute(func, *args, default=None, **kwargs):
    """
    安全执行函数
    
    Args:
        func: 要执行的函数
        *args: 位置参数
        default: 默认返回值
        **kwargs: 关键字参数
    
    Returns:
        函数结果或默认值
    """
    try:
        return func(*args, **kwargs)
    except Exception as e:
        logger = get_logger("safe_execute")
        logger.warning(f"安全执行失败: {func.__name__} - {e}")
        return default


# ═══════════════════════════════════════════════════════════════
# 配置环境变量解析
# ═══════════════════════════════════════════════════════════════

import re


def parse_env_value(value: str) -> Any:
    """
    解析环境变量值
    
    支持:
    - 布尔值: true/false/yes/no/1/0
    - 数字: 整数和浮点数
    - JSON: 以 { 或 [ 开头
    - 列表: 逗号分隔
    """
    if not value:
        return None
    
    value = value.strip()
    
    # 布尔值
    if value.lower() in ("true", "yes", "1"):
        return True
    if value.lower() in ("false", "no", "0"):
        return False
    
    # JSON
    if value.startswith("{") or value.startswith("["):
        try:
            import json
            return json.loads(value)
        except Exception:
            pass
    
    # 数字
    try:
        if "." in value:
            return float(value)
        return int(value)
    except ValueError:
        pass
    
    # 列表（逗号分隔）
    if "," in value:
        return [v.strip() for v in value.split(",")]
    
    return value


def load_config_with_env(config: Dict[str, Any], env_prefix: str = "AIUCE_") -> Dict[str, Any]:
    """
    加载配置并替换环境变量占位符
    
    支持:
    - ${ENV_VAR} 格式
    - ${ENV_VAR:-default} 格式（带默认值）
    
    Args:
        config: 原始配置字典
        env_prefix: 环境变量前缀
    
    Returns:
        解析后的配置
    """
    def resolve_value(value):
        if isinstance(value, str):
            # 匹配 ${VAR} 或 ${VAR:-default}
            pattern = r'\$\{([^}]+)\}'
            
            def replace(match):
                expr = match.group(1)
                if ":-" in expr:
                    var_name, default = expr.split(":-", 1)
                    return os.environ.get(var_name, default)
                else:
                    return os.environ.get(expr, "")
            
            return re.sub(pattern, replace, value)
        
        elif isinstance(value, dict):
            return {k: resolve_value(v) for k, v in value.items()}
        
        elif isinstance(value, list):
            return [resolve_value(v) for v in value]
        
        return value
    
    return resolve_value(config)


def get_env_config(key: str, default: Any = None, env_prefix: str = "AIUCE_") -> Any:
    """
    获取环境变量配置
    
    优先级: 环境变量 > 默认值
    
    Args:
        key: 配置键名
        default: 默认值
        env_prefix: 环境变量前缀
    
    Returns:
        配置值
    """
    env_key = f"{env_prefix}{key.upper()}"
    env_value = os.environ.get(env_key)
    
    if env_value is not None:
        return parse_env_value(env_value)
    
    return default


# ═══════════════════════════════════════════════════════════════
# 初始化
# ═══════════════════════════════════════════════════════════════

# 模块加载时初始化日志
_logger = init_default_logging()

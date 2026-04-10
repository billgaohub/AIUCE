"""
Eleven-Layer AI System - FastAPI Service
十一层架构 AI 系统 API 服务

安全加固版本：
- API Key 认证
- Rate Limiting
- 异常脱敏
- 请求追踪
"""

from fastapi import FastAPI, HTTPException, Depends, Request, Header
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime
from collections import defaultdict
from functools import wraps
import uvicorn
import os
import sys
import uuid
import time
import traceback

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from system import ElevenLayerSystem, create_system

# ═══════════════════════════════════════════════════════════════
# 安全配置
# ═══════════════════════════════════════════════════════════════

# API Keys（从环境变量读取，支持多个）
VALID_API_KEYS = os.environ.get("AIUCE_API_KEYS", "").split(",") if os.environ.get("AIUCE_API_KEYS") else []

# 是否启用认证（开发模式可关闭）
AUTH_ENABLED = os.environ.get("AIUCE_AUTH_ENABLED", "true").lower() == "true"

# Rate Limiting 配置
RATE_LIMIT_REQUESTS = int(os.environ.get("AIUCE_RATE_LIMIT", "100"))  # 每分钟最大请求数
RATE_LIMIT_WINDOW = 60  # 秒

# 请求追踪
request_counts = defaultdict(list)

# ═══════════════════════════════════════════════════════════════
# 安全中间件
# ═══════════════════════════════════════════════════════════════

def check_api_key(x_api_key: Optional[str] = Header(None, alias="X-API-Key")):
    """API Key 认证"""
    if not AUTH_ENABLED:
        return "anonymous"
    
    if not VALID_API_KEYS:
        # 如果没有配置 API Keys，允许本地访问
        return "local-dev"
    
    if not x_api_key or x_api_key not in VALID_API_KEYS:
        raise HTTPException(
            status_code=401,
            detail="Invalid or missing API key"
        )
    
    return x_api_key


def check_rate_limit(request: Request):
    """Rate Limiting 检查"""
    client_ip = request.client.host if request.client else "unknown"
    now = time.time()
    
    # 清理过期记录
    request_counts[client_ip] = [
        t for t in request_counts[client_ip] 
        if now - t < RATE_LIMIT_WINDOW
    ]
    
    # 检查是否超限
    if len(request_counts[client_ip]) >= RATE_LIMIT_REQUESTS:
        raise HTTPException(
            status_code=429,
            detail=f"Rate limit exceeded. Max {RATE_LIMIT_REQUESTS} requests per {RATE_LIMIT_WINDOW}s"
        )
    
    # 记录本次请求
    request_counts[client_ip].append(now)
    
    return True


# 创建 FastAPI 应用
app = FastAPI(
    title="AIUCE System API",
    description="AIUCE - AI Universe Constitution Evolution System API (Secured)",
    version="1.1.0",
    openapi_tags=[
        {"name": "System", "description": "System health and info endpoints"},
        {"name": "Query", "description": "Query processing endpoints"},
        {"name": "Layers", "description": "Individual layer access endpoints"},
        {"name": "Memory", "description": "Memory and knowledge management"},
        {"name": "Evolution", "description": "System evolution and self-improvement"},
    ]
)

# CORS 配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=os.environ.get("AIUCE_CORS_ORIGINS", "*").split(","),
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)


# 异常处理 - 脱敏
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """全局异常处理 - 不暴露内部错误细节"""
    request_id = str(uuid.uuid4())[:8]
    
    # 记录详细错误到日志
    error_detail = traceback.format_exc()
    print(f"[ERROR] request_id={request_id}\n{error_detail}")
    
    # 返回脱敏错误
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "request_id": request_id,
            "timestamp": datetime.now().isoformat(),
            "detail": "An error occurred. Check server logs for details."
        }
    )


# 挂载静态文件目录
static_dir = os.path.join(os.path.dirname(__file__), "static")
if os.path.exists(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")

# 全局系统实例
_system = None


def get_system() -> ElevenLayerSystem:
    """获取或创建系统实例"""
    global _system
    if _system is None:
        _system = create_system()
    return _system


# ═══════════════════════════════════════════════════════════════
# 请求/响应模型
# ═══════════════════════════════════════════════════════════════

class ChatRequest(BaseModel):
    message: str
    context: Optional[Dict[str, Any]] = None


class ChatResponse(BaseModel):
    response: str
    status: str
    layers_involved: List[str]
    audit_id: Optional[str] = None
    vetoed: bool = False
    veto_reason: Optional[str] = None
    timing: Dict[str, Any]
    request_id: str


class StatusResponse(BaseModel):
    version: str
    build_date: str
    layers: Dict[str, Any]
    message_bus: Dict[str, Any]
    audit: Dict[str, Any]


class MemoryRequest(BaseModel):
    content: str
    category: str = "event"
    importance: float = 0.5


class MemoryResponse(BaseModel):
    memory_id: str
    status: str


class ErrorResponse(BaseModel):
    error: str
    request_id: str
    timestamp: str


# ═══════════════════════════════════════════════════════════════
# API 路由
# ═══════════════════════════════════════════════════════════════

@app.get("/")
async def root():
    """根路径 - 重定向到 Web 界面"""
    if os.path.exists(static_dir):
        return RedirectResponse(url="/static/index.html")
    return {
        "name": "十一层架构 AI 系统 API",
        "version": "1.1.0",
        "layers": ["L0-L10"],
        "docs": "/docs",
        "auth_enabled": AUTH_ENABLED
    }


@app.get("/health")
async def health_check():
    """健康检查端点（无需认证）"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "1.1.0"
    }


@app.get("/status", response_model=StatusResponse)
async def get_status(
    request: Request,
    _: str = Depends(check_rate_limit),
    api_key: str = Depends(check_api_key)
):
    """获取系统状态"""
    system = get_system()
    return system.get_status()


@app.post("/chat", response_model=ChatResponse)
async def chat(
    request: Request,
    chat_request: ChatRequest,
    _: str = Depends(check_rate_limit),
    api_key: str = Depends(check_api_key)
):
    """对话接口"""
    request_id = str(uuid.uuid4())[:8]
    
    system = get_system()
    result = system.run(chat_request.message)
    
    return ChatResponse(
        response=result.get("response", ""),
        status=result["status"],
        layers_involved=result["layers_involved"],
        audit_id=result.get("audit_id"),
        vetoed=result.get("vetoed", False),
        veto_reason=result.get("veto_reason"),
        timing=result.get("timing", {}),
        request_id=request_id
    )


@app.post("/chat/simple")
async def chat_simple(
    request: Request,
    chat_request: ChatRequest,
    _: str = Depends(check_rate_limit),
    api_key: str = Depends(check_api_key)
):
    """简单对话接口（仅返回文本）"""
    system = get_system()
    response = system.chat(chat_request.message)
    return {"response": response}


@app.get("/constitution")
async def get_constitution(
    _: str = Depends(check_rate_limit),
    api_key: str = Depends(check_api_key)
):
    """获取宪法条款"""
    system = get_system()
    return system.export_constitution()


@app.post("/memory", response_model=MemoryResponse)
async def store_memory(
    request: Request,
    memory_request: MemoryRequest,
    _: str = Depends(check_rate_limit),
    api_key: str = Depends(check_api_key)
):
    """存储记忆"""
    system = get_system()
    memory_id = system.memory.store(
        content=memory_request.content,
        category=memory_request.category,
        importance=memory_request.importance
    )
    return MemoryResponse(memory_id=memory_id, status="success")


@app.get("/memory")
async def retrieve_memory(
    query: str,
    limit: int = 10,
    _: str = Depends(check_rate_limit),
    api_key: str = Depends(check_api_key)
):
    """检索记忆"""
    system = get_system()
    memories = system.memory.retrieve(query, limit=limit)
    return {"memories": memories}


@app.get("/audit")
async def get_audit_log(
    limit: int = 100,
    _: str = Depends(check_rate_limit),
    api_key: str = Depends(check_api_key)
):
    """获取审计日志"""
    system = get_system()
    logs = system.get_audit_log(limit=limit)
    return {"logs": logs}


@app.post("/review")
async def daily_review(
    _: str = Depends(check_rate_limit),
    api_key: str = Depends(check_api_key)
):
    """执行每日复盘"""
    system = get_system()
    review = system.daily_review()
    return review


@app.post("/evolve")
async def evolve(
    rule_id: Optional[str] = None,
    _: str = Depends(check_rate_limit),
    api_key: str = Depends(check_api_key)
):
    """触发系统演化"""
    system = get_system()
    result = system.evolve(rule_id)
    return result


# ═══════════════════════════════════════════════════════════════
# 启动
# ═══════════════════════════════════════════════════════════════

if __name__ == "__main__":
    print(f"\n{'━' * 60}")
    print(f"  🏯 AIUCE API Server v1.1.0 (Secured)")
    print(f"  Auth: {'Enabled' if AUTH_ENABLED else 'Disabled'}")
    print(f"  Rate Limit: {RATE_LIMIT_REQUESTS} req/{RATE_LIMIT_WINDOW}s")
    print(f"{'━' * 60}\n")
    
    uvicorn.run(
        "api:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )

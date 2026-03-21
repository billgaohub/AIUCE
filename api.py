"""
Eleven-Layer AI System - FastAPI Service
十一层架构 AI 系统 API 服务
"""

from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import uvicorn
import os
import sys

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from system import ElevenLayerSystem, create_system

# 创建 FastAPI 应用
app = FastAPI(
    title="AIUCE System API",
    description="AIUCE - AI Universe Constitution Evolution System API",
    version="1.0.0"
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
        "version": "1.0.0",
        "layers": ["L0-L10"],
        "docs": "/docs"
    }


@app.get("/status", response_model=StatusResponse)
async def get_status():
    """获取系统状态"""
    system = get_system()
    return system.get_status()


@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """对话接口"""
    try:
        system = get_system()
        result = system.run(request.message)
        
        return ChatResponse(
            response=result.get("response", ""),
            status=result["status"],
            layers_involved=result["layers_involved"],
            audit_id=result.get("audit_id"),
            vetoed=result.get("vetoed", False),
            veto_reason=result.get("veto_reason"),
            timing=result.get("timing", {})
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/chat/simple")
async def chat_simple(request: ChatRequest):
    """简单对话接口（仅返回文本）"""
    try:
        system = get_system()
        response = system.chat(request.message)
        return {"response": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/constitution")
async def get_constitution():
    """获取宪法条款"""
    system = get_system()
    return system.export_constitution()


@app.post("/memory")
async def store_memory(request: MemoryRequest):
    """存储记忆"""
    try:
        system = get_system()
        memory_id = system.memory.store(
            content=request.content,
            category=request.category,
            importance=request.importance
        )
        return MemoryResponse(memory_id=memory_id, status="success")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/memory")
async def retrieve_memory(query: str, limit: int = 10):
    """检索记忆"""
    try:
        system = get_system()
        memories = system.memory.retrieve(query, limit=limit)
        return {"memories": memories}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/audit")
async def get_audit_log(limit: int = 100):
    """获取审计日志"""
    try:
        system = get_system()
        logs = system.get_audit_log(limit=limit)
        return {"logs": logs}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/review")
async def daily_review():
    """执行每日复盘"""
    try:
        system = get_system()
        review = system.daily_review()
        return review
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/evolve")
async def evolve(rule_id: Optional[str] = None):
    """触发系统演化"""
    try:
        system = get_system()
        result = system.evolve(rule_id)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ═══════════════════════════════════════════════════════════════
# 启动
# ═══════════════════════════════════════════════════════════════

if __name__ == "__main__":
    uvicorn.run(
        "api:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )

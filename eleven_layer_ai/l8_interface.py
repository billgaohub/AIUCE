"""
L8 接口层：张骞/礼部
External Interface - 算力外交

职责：
1. 连接 OpenAI/本地 Qwen 等异星算力
2. 负责协议握手
3. 凿空西域，打通本地算力与云端异星算力的"丝绸之路"

增强版: core/l8_interface.py (InterfaceLayer + 多模型路由)
本文件为 system.py 集成版本，接口稳定。
"""

from typing import Dict, Any, List, Optional, Callable
from dataclasses import dataclass, field
from datetime import datetime
import json
import os
import logging

# 配置日志
logger = logging.getLogger("aiuce.l8")

# HTTP 客户端（延迟导入）
try:
    import httpx
    HAS_HTTPX = True
except ImportError:
    HAS_HTTPX = False

try:
    from openai import OpenAI
    HAS_OPENAI = True
except ImportError:
    HAS_OPENAI = False

try:
    from anthropic import Anthropic
    HAS_ANTHROPIC = True
except ImportError:
    HAS_ANTHROPIC = False


@dataclass
class ModelProvider:
    """模型提供商"""
    provider_id: str
    name: str
    endpoint: str  # API 端点
    api_key_env: str  # 环境变量名
    model_name: str
    capability: List[str]  # 能力列表
    cost_per_1k: float  # 每1000 token 成本
    latency_ms: int  # 典型延迟
    available: bool = True


@dataclass
class ModelResponse:
    """模型响应"""
    provider: str
    model: str
    content: str
    tokens_used: int
    latency_ms: int
    timestamp: str
    success: bool
    error: str = ""


class InterfaceLayer:
    """
    接口层 - 张骞/礼部
    
    "凿空西域，打通本地算力与云端异星算力的丝绸之路"
    
    统一管理所有外部模型接口，
    智能选择最优算力来源，
    处理协议握手和请求路由。
    """

    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.providers: Dict[str, ModelProvider] = {}
        self.last_responses: Dict[str, ModelResponse] = {}
        self.request_history: List[Dict] = []
        
        # API 客户端缓存
        self._clients: Dict[str, Any] = {}
        
        self._init_providers()
        self._check_available()

    def _init_providers(self):
        """初始化模型提供商"""
        default_providers = [
            ModelProvider(
                provider_id="openai",
                name="OpenAI",
                endpoint="https://api.openai.com/v1/chat/completions",
                api_key_env="OPENAI_API_KEY",
                model_name="gpt-4o-mini",
                capability=["reasoning", "coding", "creative", "analysis"],
                cost_per_1k=0.00015,
                latency_ms=1000
            ),
            ModelProvider(
                provider_id="claude",
                name="Anthropic Claude",
                endpoint="https://api.anthropic.com/v1/messages",
                api_key_env="ANTHROPIC_API_KEY",
                model_name="claude-3-5-sonnet-20241022",
                capability=["reasoning", "writing", "analysis", "safety"],
                cost_per_1k=0.003,
                latency_ms=1200
            ),
            ModelProvider(
                provider_id="qwen",
                name="阿里通义千问",
                endpoint="https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions",
                api_key_env="DASHSCOPE_API_KEY",
                model_name="qwen-plus",
                capability=["reasoning", "coding", "chinese", "fast"],
                cost_per_1k=0.002,
                latency_ms=800
            ),
            ModelProvider(
                provider_id="deepseek",
                name="DeepSeek",
                endpoint="https://api.deepseek.com/v1/chat/completions",
                api_key_env="DEEPSEEK_API_KEY",
                model_name="deepseek-chat",
                capability=["reasoning", "coding", "chinese", "fast"],
                cost_per_1k=0.001,
                latency_ms=600
            ),
            ModelProvider(
                provider_id="local",
                name="本地模型",
                endpoint="http://localhost:11434/v1/chat/completions",
                api_key_env="",
                model_name="llama3",
                capability=["fast", "offline", "privacy"],
                cost_per_1k=0,
                latency_ms=200
            ),
            ModelProvider(
                provider_id="mlx",
                name="MLX 本地模型",
                endpoint="http://localhost:8080/v1/chat/completions",
                api_key_env="",
                model_name="qwen2.5-7b",
                capability=["fast", "offline", "privacy", "reasoning"],
                cost_per_1k=0,
                latency_ms=100
            ),
        ]
        
        for provider in default_providers:
            self.providers[provider.provider_id] = provider
        
        logger.info(f"[L8] 加载 {len(self.providers)} 个算力提供商")

    def _check_available(self):
        """检查各提供商可用性"""
        for provider_id, provider in self.providers.items():
            if provider_id == "local":
                # 检查本地 Ollama
                provider.available = self._check_local_endpoint(provider.endpoint)
            elif provider_id == "mlx":
                # 检查 MLX 服务
                provider.available = self._check_local_endpoint(provider.endpoint)
            else:
                # 云端：检查 API Key
                api_key = os.environ.get(provider.api_key_env, "")
                provider.available = bool(api_key)
            
            status = "✅" if provider.available else "❌"
            logger.info(f"  {status} {provider.name}: {provider.model_name}")

    def _check_local_endpoint(self, endpoint: str) -> bool:
        """检查本地端点是否可用"""
        if not HAS_HTTPX:
            return False
        try:
            # 尝试连接
            base_url = endpoint.rsplit("/v1/", 1)[0]
            resp = httpx.get(f"{base_url}/v1/models", timeout=2.0)
            return resp.status_code == 200
        except Exception:
            return False

    def _get_client(self, provider: ModelProvider) -> Optional[Any]:
        """获取或创建 API 客户端"""
        if provider.provider_id in self._clients:
            return self._clients[provider.provider_id]
        
        client = None
        
        if provider.provider_id == "openai" and HAS_OPENAI:
            api_key = os.environ.get(provider.api_key_env, "")
            if api_key:
                client = OpenAI(api_key=api_key)
        
        elif provider.provider_id == "claude" and HAS_ANTHROPIC:
            api_key = os.environ.get(provider.api_key_env, "")
            if api_key:
                client = Anthropic(api_key=api_key)
        
        elif provider.provider_id in ("qwen", "deepseek", "local", "mlx"):
            # 使用 OpenAI 兼容接口
            if HAS_OPENAI:
                api_key = os.environ.get(provider.api_key_env, "sk-dummy")
                client = OpenAI(
                    api_key=api_key,
                    base_url=provider.endpoint.rsplit("/v1/", 1)[0] + "/v1"
                )
        
        if client:
            self._clients[provider.provider_id] = client
        
        return client

    def call_model(
        self,
        prompt: str,
        context: List[Dict[str, Any]] = None,
        reasoning: Dict[str, Any] = None,
        preferred_provider: str = None,
        system_prompt: str = None
    ) -> ModelResponse:
        """
        调用模型
        
        智能选择最佳模型，处理请求和响应。
        """
        # 1. 选择模型
        provider = self._select_provider(preferred_provider, reasoning)
        
        # 2. 构建消息
        messages = self._build_messages(prompt, context, system_prompt)
        
        # 3. 发送请求
        start_time = datetime.now()
        
        # 检查是否使用模拟模式
        if self.config.get("mock", False):
            response = self._mock_response(provider, prompt)
        else:
            response = self._send_real_request(provider, messages)
        
        end_time = datetime.now()
        response.latency_ms = int((end_time - start_time).total_seconds() * 1000)
        
        # 4. 记录
        self.last_responses[provider.provider_id] = response
        self.request_history.append({
            "timestamp": response.timestamp,
            "provider": provider.provider_id,
            "model": provider.model_name,
            "success": response.success,
            "latency_ms": response.latency_ms
        })
        
        if response.success:
            logger.info(f"[L8 张骞] 📡 {provider.name} → {response.content[:50]}...")
        else:
            logger.warning(f"[L8 张骞] ❌ {provider.name} 失败: {response.error}")
        
        return response

    def _build_messages(
        self,
        prompt: str,
        context: List[Dict[str, Any]] = None,
        system_prompt: str = None
    ) -> List[Dict[str, str]]:
        """构建消息列表"""
        messages = []
        
        # 系统提示
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        else:
            messages.append({
                "role": "system",
                "content": "你是 AIUCE，一个基于十一层架构的 AI 助手。简洁、准确地回答问题。"
            })
        
        # 上下文（记忆）
        if context:
            ctx_strings = []
            for ctx_item in context[:5]:
                ctx = ctx_item[0] if isinstance(ctx_item, tuple) else ctx_item
                content = ctx.content if hasattr(ctx, 'content') else ctx.get('content', '') if isinstance(ctx, dict) else str(ctx)
                if content:
                    ctx_strings.append(f"- {content}")
            context_text = "\n".join(ctx_strings)
            if context_text:
                messages.append({
                    "role": "user",
                    "content": f"[相关记忆]\n{context_text}"
                })
                messages.append({
                    "role": "assistant",
                    "content": "已了解相关背景。"
                })
        
        # 用户输入
        messages.append({"role": "user", "content": prompt})
        
        return messages

    def _send_real_request(
        self,
        provider: ModelProvider,
        messages: List[Dict[str, str]]
    ) -> ModelResponse:
        """发送真实 API 请求"""
        
        # 特殊处理 Claude
        if provider.provider_id == "claude":
            return self._call_claude(provider, messages)
        
        # OpenAI 兼容接口
        client = self._get_client(provider)
        
        if not client:
            return ModelResponse(
                provider=provider.provider_id,
                model=provider.model_name,
                content="",
                tokens_used=0,
                latency_ms=0,
                timestamp=datetime.now().isoformat(),
                success=False,
                error=f"客户端未初始化或 API Key 未配置"
            )
        
        try:
            response = client.chat.completions.create(
                model=provider.model_name,
                messages=messages,
                max_tokens=1000,
                temperature=0.7
            )
            
            content = response.choices[0].message.content
            tokens_used = response.usage.total_tokens if response.usage else 0
            
            return ModelResponse(
                provider=provider.provider_id,
                model=provider.model_name,
                content=content,
                tokens_used=tokens_used,
                latency_ms=0,  # 由调用者设置
                timestamp=datetime.now().isoformat(),
                success=True
            )
        
        except Exception as e:
            logger.error(f"[L8] API 调用失败: {e}")
            return ModelResponse(
                provider=provider.provider_id,
                model=provider.model_name,
                content="",
                tokens_used=0,
                latency_ms=0,
                timestamp=datetime.now().isoformat(),
                success=False,
                error=str(e)
            )

    def _call_claude(
        self,
        provider: ModelProvider,
        messages: List[Dict[str, str]]
    ) -> ModelResponse:
        """调用 Claude API"""
        if not HAS_ANTHROPIC:
            return ModelResponse(
                provider=provider.provider_id,
                model=provider.model_name,
                content="",
                tokens_used=0,
                latency_ms=0,
                timestamp=datetime.now().isoformat(),
                success=False,
                error="anthropic 库未安装"
            )
        
        client = self._get_client(provider)
        if not client:
            return ModelResponse(
                provider=provider.provider_id,
                model=provider.model_name,
                content="",
                tokens_used=0,
                latency_ms=0,
                timestamp=datetime.now().isoformat(),
                success=False,
                error="Claude 客户端未初始化"
            )
        
        try:
            # 提取系统提示
            system = ""
            user_messages = []
            for msg in messages:
                if msg["role"] == "system":
                    system = msg["content"]
                else:
                    user_messages.append(msg)
            
            response = client.messages.create(
                model=provider.model_name,
                max_tokens=1000,
                system=system,
                messages=user_messages
            )
            
            content = response.content[0].text
            tokens_used = response.usage.input_tokens + response.usage.output_tokens
            
            return ModelResponse(
                provider=provider.provider_id,
                model=provider.model_name,
                content=content,
                tokens_used=tokens_used,
                latency_ms=0,
                timestamp=datetime.now().isoformat(),
                success=True
            )
        
        except Exception as e:
            logger.error(f"[L8] Claude API 调用失败: {e}")
            return ModelResponse(
                provider=provider.provider_id,
                model=provider.model_name,
                content="",
                tokens_used=0,
                latency_ms=0,
                timestamp=datetime.now().isoformat(),
                success=False,
                error=str(e)
            )

    def _mock_response(
        self,
        provider: ModelProvider,
        prompt: str
    ) -> ModelResponse:
        """模拟响应（测试用）"""
        return ModelResponse(
            provider=provider.provider_id,
            model=provider.model_name,
            content=f"[{provider.name} 模拟回复] 收到您的输入: {prompt[:30]}...",
            tokens_used=len(prompt) // 4,
            latency_ms=provider.latency_ms,
            timestamp=datetime.now().isoformat(),
            success=True
        )

    def _select_provider(
        self,
        preferred: str = None,
        reasoning: Dict[str, Any] = None
    ) -> ModelProvider:
        """选择最优模型提供商"""
        # 1. 如果有指定且可用，直接使用
        if preferred and preferred in self.providers:
            provider = self.providers[preferred]
            if provider.available:
                return provider
        
        # 2. 智能选择
        available = [p for p in self.providers.values() if p.available]
        
        if not available:
            # 降级到本地
            if "local" in self.providers:
                return self.providers["local"]
            if "mlx" in self.providers:
                return self.providers["mlx"]
            # 最后返回第一个
            return list(self.providers.values())[0]
        
        # 基于推理需求选择
        if reasoning:
            needed_caps = set(reasoning.get("required_capabilities", []))
            if needed_caps:
                for p in available:
                    if needed_caps.issubset(set(p.capability)):
                        return p
        
        # 默认选择成本最低的
        available.sort(key=lambda p: p.cost_per_1k)
        return available[0]

    def get_provider(self, provider_id: str) -> Optional[ModelProvider]:
        """获取提供商信息"""
        return self.providers.get(provider_id)

    def list_providers(self) -> List[Dict[str, Any]]:
        """列出所有提供商"""
        return [
            {
                "id": p.provider_id,
                "name": p.name,
                "model": p.model_name,
                "capability": p.capability,
                "cost_per_1k": p.cost_per_1k,
                "latency_ms": p.latency_ms,
                "available": p.available
            }
            for p in self.providers.values()
        ]

    def set_provider_available(self, provider_id: str, available: bool):
        """设置提供商可用性"""
        if provider_id in self.providers:
            self.providers[provider_id].available = available

    def get_stats(self) -> Dict[str, Any]:
        """获取调用统计"""
        total = len(self.request_history)
        successes = len([r for r in self.request_history if r.get("success")])
        
        return {
            "total_requests": total,
            "success_rate": successes / total if total > 0 else 0,
            "providers": len(self.providers),
            "available_providers": len([p for p in self.providers.values() if p.available]),
            "last_call": self.request_history[-1] if self.request_history else None
        }

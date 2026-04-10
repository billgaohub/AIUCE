"""
L8 接口层：张骞/礼部
External Interface - 算力外交

职责：
1. 连接 OpenAI/Claude/本地 Qwen/MLX 等异星算力
2. 负责协议握手和请求路由
3. 凿空西域，打通本地算力与云端异星算力的"丝绸之路"
4. 智能选择最优算力来源
"""

import os
import json
import logging
from typing import Dict, Any, List, Optional, Callable
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from abc import ABC, abstractmethod

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


# ═══════════════════════════════════════════════════════════════
# 数据模型
# ═══════════════════════════════════════════════════════════════

class ProviderID(Enum):
    """模型提供商ID"""
    OPENAI = "openai"
    CLAUDE = "claude"
    QWEN = "qwen"
    DEEPSEEK = "deepseek"
    LOCAL = "local"
    MLX = "mlx"
    GEMINI = "gemini"
    GROQ = "groq"


@dataclass
class ModelProvider:
    """模型提供商"""
    provider_id: str
    name: str
    endpoint: str
    api_key_env: str
    model_name: str
    capability: List[str]
    cost_per_1k: float
    latency_ms: int
    available: bool = True
    priority: int = 0


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
    reasoning: str = ""


# ═══════════════════════════════════════════════════════════════
# Provider Adapter (Abstract)
# ═══════════════════════════════════════════════════════════════

class ProviderAdapter(ABC):
    """模型提供商适配器基类"""

    @abstractmethod
    def call(self, messages: List[Dict], **kwargs) -> ModelResponse:
        pass

    @abstractmethod
    def is_available(self) -> bool:
        pass


class OpenAIAdapter(ProviderAdapter):
    """OpenAI 适配器"""

    def __init__(self, provider: ModelProvider):
        self.provider = provider
        self._client = None

    def _get_client(self) -> Optional[OpenAI]:
        if self._client:
            return self._client
        api_key = os.environ.get(self.provider.api_key_env, "")
        if not api_key:
            return None
        self._client = OpenAI(api_key=api_key)
        return self._client

    def is_available(self) -> bool:
        return HAS_OPENAI and bool(os.environ.get(self.provider.api_key_env))

    def call(self, messages: List[Dict], **kwargs) -> ModelResponse:
        client = self._get_client()
        if not client:
            return self._error_response("OpenAI 客户端未初始化或 API Key 未配置")

        try:
            resp = client.chat.completions.create(
                model=self.provider.model_name,
                messages=messages,
                max_tokens=kwargs.get("max_tokens", 1000),
                temperature=kwargs.get("temperature", 0.7),
            )
            return ModelResponse(
                provider=self.provider.provider_id,
                model=self.provider.model_name,
                content=resp.choices[0].message.content,
                tokens_used=resp.usage.total_tokens if resp.usage else 0,
                latency_ms=0,
                timestamp=datetime.now().isoformat(),
                success=True,
            )
        except Exception as e:
            return self._error_response(str(e))

    def _error_response(self, error: str) -> ModelResponse:
        return ModelResponse(
            provider=self.provider.provider_id,
            model=self.provider.model_name,
            content="",
            tokens_used=0,
            latency_ms=0,
            timestamp=datetime.now().isoformat(),
            success=False,
            error=error,
        )


class ClaudeAdapter(ProviderAdapter):
    """Claude 适配器"""

    def __init__(self, provider: ModelProvider):
        self.provider = provider
        self._client = None

    def _get_client(self) -> Optional[Anthropic]:
        if self._client:
            return self._client
        api_key = os.environ.get(self.provider.api_key_env, "")
        if not api_key:
            return None
        self._client = Anthropic(api_key=api_key)
        return self._client

    def is_available(self) -> bool:
        return HAS_ANTHROPIC and bool(os.environ.get(self.provider.api_key_env))

    def call(self, messages: List[Dict], **kwargs) -> ModelResponse:
        client = self._get_client()
        if not client:
            return self._error_response("Claude 客户端未初始化或 API Key 未配置")

        # 提取系统消息
        system = ""
        user_messages = []
        for msg in messages:
            if msg["role"] == "system":
                system = msg["content"]
            else:
                user_messages.append(msg)

        try:
            resp = client.messages.create(
                model=self.provider.model_name,
                max_tokens=kwargs.get("max_tokens", 1000),
                system=system,
                messages=user_messages,
            )
            content = resp.content[0].text if resp.content else ""
            tokens = resp.usage.input_tokens + resp.usage.output_tokens if resp.usage else 0
            return ModelResponse(
                provider=self.provider.provider_id,
                model=self.provider.model_name,
                content=content,
                tokens_used=tokens,
                latency_ms=0,
                timestamp=datetime.now().isoformat(),
                success=True,
            )
        except Exception as e:
            return self._error_response(str(e))

    def _error_response(self, error: str) -> ModelResponse:
        return ModelResponse(
            provider=self.provider.provider_id,
            model=self.provider.model_name,
            content="",
            tokens_used=0,
            latency_ms=0,
            timestamp=datetime.now().isoformat(),
            success=False,
            error=error,
        )


class OpenCompatibleAdapter(ProviderAdapter):
    """OpenAI 兼容接口适配器"""

    def __init__(self, provider: ModelProvider):
        self.provider = provider
        self._client = None

    def _get_client(self) -> Optional[OpenAI]:
        if self._client:
            return self._client
        if not HAS_OPENAI:
            return None
        api_key = os.environ.get(self.provider.api_key_env, "sk-dummy")
        base_url = self.provider.endpoint.rsplit("/v1/", 1)[0] + "/v1"
        self._client = OpenAI(api_key=api_key, base_url=base_url)
        return self._client

    def is_available(self) -> bool:
        if not HAS_OPENAI:
            return False
        # 本地服务不需要 API Key
        if self.provider.provider_id in ("local", "mlx"):
            return self._check_endpoint()
        return bool(os.environ.get(self.provider.api_key_env))

    def _check_endpoint(self) -> bool:
        if not HAS_HTTPX:
            return False
        try:
            base_url = self.provider.endpoint.rsplit("/v1/", 1)[0]
            resp = httpx.get(f"{base_url}/v1/models", timeout=2.0)
            return resp.status_code == 200
        except Exception:
            return False

    def call(self, messages: List[Dict], **kwargs) -> ModelResponse:
        client = self._get_client()
        if not client:
            return self._error_response(f"{self.provider.name} 客户端未初始化")

        try:
            resp = client.chat.completions.create(
                model=self.provider.model_name,
                messages=messages,
                max_tokens=kwargs.get("max_tokens", 1000),
                temperature=kwargs.get("temperature", 0.7),
            )
            return ModelResponse(
                provider=self.provider.provider_id,
                model=self.provider.model_name,
                content=resp.choices[0].message.content,
                tokens_used=resp.usage.total_tokens if resp.usage else 0,
                latency_ms=0,
                timestamp=datetime.now().isoformat(),
                success=True,
            )
        except Exception as e:
            return self._error_response(str(e))

    def _error_response(self, error: str) -> ModelResponse:
        return ModelResponse(
            provider=self.provider.provider_id,
            model=self.provider.model_name,
            content="",
            tokens_used=0,
            latency_ms=0,
            timestamp=datetime.now().isoformat(),
            success=False,
            error=error,
        )


# ═══════════════════════════════════════════════════════════════
# 接口层核心
# ═══════════════════════════════════════════════════════════════

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
        self.adapters: Dict[str, ProviderAdapter] = {}
        self.last_responses: Dict[str, ModelResponse] = {}
        self.request_history: List[Dict] = []

        self._init_providers()
        self._init_adapters()
        self._check_available()

        logger.info(f"[L8 张骞/礼部] 加载 {len(self.providers)} 个算力提供商")

    # ── 初始化 ──────────────────────────────────────────────

    def _init_providers(self):
        """初始化模型提供商"""
        default_providers = [
            ModelProvider(
                provider_id="openai", name="OpenAI",
                endpoint="https://api.openai.com/v1/chat/completions",
                api_key_env="OPENAI_API_KEY",
                model_name="gpt-4o-mini",
                capability=["reasoning", "coding", "creative", "analysis"],
                cost_per_1k=0.00015, latency_ms=1000, priority=10
            ),
            ModelProvider(
                provider_id="claude", name="Anthropic Claude",
                endpoint="https://api.anthropic.com/v1/messages",
                api_key_env="ANTHROPIC_API_KEY",
                model_name="claude-3-5-sonnet-20241022",
                capability=["reasoning", "writing", "analysis", "safety"],
                cost_per_1k=0.003, latency_ms=1200, priority=9
            ),
            ModelProvider(
                provider_id="qwen", name="阿里通义千问",
                endpoint="https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions",
                api_key_env="DASHSCOPE_API_KEY",
                model_name="qwen-plus",
                capability=["reasoning", "coding", "chinese", "fast"],
                cost_per_1k=0.002, latency_ms=800, priority=8
            ),
            ModelProvider(
                provider_id="deepseek", name="DeepSeek",
                endpoint="https://api.deepseek.com/v1/chat/completions",
                api_key_env="DEEPSEEK_API_KEY",
                model_name="deepseek-chat",
                capability=["reasoning", "coding", "chinese", "fast"],
                cost_per_1k=0.001, latency_ms=600, priority=7
            ),
            ModelProvider(
                provider_id="local", name="本地 Ollama",
                endpoint="http://localhost:11434/v1/chat/completions",
                api_key_env="",
                model_name="llama3",
                capability=["fast", "offline", "privacy"],
                cost_per_1k=0, latency_ms=200, priority=5
            ),
            ModelProvider(
                provider_id="mlx", name="MLX 本地模型",
                endpoint="http://localhost:8080/v1/chat/completions",
                api_key_env="",
                model_name="qwen2.5-7b",
                capability=["fast", "offline", "privacy", "reasoning"],
                cost_per_1k=0, latency_ms=100, priority=6
            ),
        ]

        for provider in default_providers:
            self.providers[provider.provider_id] = provider

    def _init_adapters(self):
        """初始化适配器"""
        for pid, provider in self.providers.items():
            if pid == "openai":
                self.adapters[pid] = OpenAIAdapter(provider)
            elif pid == "claude":
                self.adapters[pid] = ClaudeAdapter(provider)
            else:
                self.adapters[pid] = OpenCompatibleAdapter(provider)

    def _check_available(self):
        """检查各提供商可用性"""
        for pid, adapter in self.adapters.items():
            provider = self.providers[pid]
            provider.available = adapter.is_available()
            status = "✅" if provider.available else "❌"
            logger.info(f"  {status} {provider.name}: {provider.model_name}")

    # ── 核心接口 ──────────────────────────────────────────────

    def call_model(
        self,
        prompt: str,
        context: List[Dict[str, Any]] = None,
        reasoning: Dict[str, Any] = None,
        preferred_provider: str = None,
        system_prompt: str = None,
        **kwargs
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

        # 模拟模式
        if self.config.get("mock", False):
            response = self._mock_response(provider, prompt)
        else:
            adapter = self.adapters.get(provider.provider_id)
            if not adapter:
                return ModelResponse(
                    provider=provider.provider_id,
                    model=provider.model_name,
                    content="",
                    tokens_used=0,
                    latency_ms=0,
                    timestamp=datetime.now().isoformat(),
                    success=False,
                    error=f"未找到适配器: {provider.provider_id}"
                )
            response = adapter.call(messages, **kwargs)

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
                "content": "你是 AIUCE，一个基于十一层架构的 AI 助手。"
            })

        # 上下文
        if context:
            ctx_text = "\n".join([
                f"- {c.get('content', '')}" for c in context[:5]
            ])
            if ctx_text:
                messages.append({"role": "user", "content": f"[相关记忆]\n{ctx_text}"})
                messages.append({"role": "assistant", "content": "已了解相关背景。"})

        # 用户输入
        messages.append({"role": "user", "content": prompt})

        return messages

    def _select_provider(
        self,
        preferred: str = None,
        reasoning: Dict[str, Any] = None
    ) -> ModelProvider:
        """选择最优模型提供商"""
        # 1. 指定且可用
        if preferred and preferred in self.providers:
            p = self.providers[preferred]
            if p.available:
                return p

        # 2. 可用列表
        available = [p for p in self.providers.values() if p.available]
        if not available:
            # 降级
            if "mlx" in self.providers:
                return self.providers["mlx"]
            if "local" in self.providers:
                return self.providers["local"]
            return list(self.providers.values())[0]

        # 3. 基于推理需求
        if reasoning:
            needed = set(reasoning.get("required_capabilities", []))
            if needed:
                for p in available:
                    if needed.issubset(set(p.capability)):
                        return p

        # 4. 优先级 + 成本
        available.sort(key=lambda p: (-p.priority, p.cost_per_1k))
        return available[0]

    def _mock_response(
        self,
        provider: ModelProvider,
        prompt: str
    ) -> ModelResponse:
        """模拟响应"""
        return ModelResponse(
            provider=provider.provider_id,
            model=provider.model_name,
            content=f"[{provider.name} 模拟回复] 收到: {prompt[:30]}...",
            tokens_used=len(prompt) // 4,
            latency_ms=provider.latency_ms,
            timestamp=datetime.now().isoformat(),
            success=True
        )

    # ── 查询接口 ──────────────────────────────────────────────

    def get_provider(self, provider_id: str) -> Optional[ModelProvider]:
        return self.providers.get(provider_id)

    def list_providers(self) -> List[Dict[str, Any]]:
        return [
            {
                "id": p.provider_id,
                "name": p.name,
                "model": p.model_name,
                "capability": p.capability,
                "cost_per_1k": p.cost_per_1k,
                "latency_ms": p.latency_ms,
                "available": p.available,
                "priority": p.priority,
            }
            for p in self.providers.values()
        ]

    def set_provider_available(self, provider_id: str, available: bool):
        if provider_id in self.providers:
            self.providers[provider_id].available = available

    def get_stats(self) -> Dict[str, Any]:
        total = len(self.request_history)
        successes = len([r for r in self.request_history if r.get("success")])
        return {
            "total_requests": total,
            "success_rate": successes / total if total > 0 else 0,
            "providers": len(self.providers),
            "available": len([p for p in self.providers.values() if p.available]),
            "last_call": self.request_history[-1] if self.request_history else None,
        }

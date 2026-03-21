"""
L8 接口层：张骞/礼部
External Interface - 算力外交

职责：
1. 连接 OpenAI/本地 Qwen 等异星算力
2. 负责协议握手
3. 凿空西域，打通本地算力与云端异星算力的"丝绸之路"
"""

from typing import Dict, Any, List, Optional, Callable
from dataclasses import dataclass, field
from datetime import datetime
import json


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
        
        self._init_providers()

    def _init_providers(self):
        """初始化模型提供商"""
        default_providers = [
            ModelProvider(
                provider_id="openai",
                name="OpenAI",
                endpoint="https://api.openai.com/v1/chat/completions",
                api_key_env="OPENAI_API_KEY",
                model_name="gpt-4",
                capability=["reasoning", "coding", "creative", "analysis"],
                cost_per_1k=0.03,
                latency_ms=1000
            ),
            ModelProvider(
                provider_id="claude",
                name="Anthropic Claude",
                endpoint="https://api.anthropic.com/v1/messages",
                api_key_env="ANTHROPIC_API_KEY",
                model_name="claude-3-5-sonnet",
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
                provider_id="local",
                name="本地模型",
                endpoint="http://localhost:11434/v1/chat/completions",
                api_key_env="",
                model_name="llama3",
                capability=["fast", "offline", "privacy"],
                cost_per_1k=0,
                latency_ms=200
            ),
        ]
        
        for provider in default_providers:
            self.providers[provider.provider_id] = provider
        print(f"  [L8] 加载 {len(self.providers)} 个算力提供商")

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
        
        # 2. 构建请求
        full_prompt = self._build_prompt(prompt, context, reasoning, system_prompt)
        
        # 3. 发送请求
        start_time = datetime.now()
        try:
            response = self._send_request(provider, full_prompt)
        except Exception as e:
            response = ModelResponse(
                provider=provider.provider_id,
                model=provider.model_name,
                content="",
                tokens_used=0,
                latency_ms=0,
                timestamp=datetime.now().isoformat(),
                success=False,
                error=str(e)
            )
        
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
            print(f"  [L8 张骞] 📡 {provider.name} → {response.content[:50]}...")
        else:
            print(f"  [L8 张骞] ❌ {provider.name} 失败: {response.error}")
        
        return response

    def _select_provider(
        self,
        preferred: str = None,
        reasoning: Dict[str, Any] = None
    ) -> ModelProvider:
        """选择最优模型提供商"""
        if preferred and preferred in self.providers:
            return self.providers[preferred]
        
        # 智能选择
        available = [p for p in self.providers.values() if p.available]
        
        if not available:
            # 如果没有可用的，降级到本地
            return self.providers.get("local", list(self.providers.values())[0])
        
        # 基于能力选择
        if reasoning:
            needed_caps = set()
            # 根据推理结果选择
            return available[0]
        
        # 默认选择成本最低的
        available.sort(key=lambda p: p.cost_per_1k)
        return available[0]

    def _build_prompt(
        self,
        prompt: str,
        context: List[Dict[str, Any]] = None,
        reasoning: Dict[str, Any] = None,
        system_prompt: str = None
    ) -> str:
        """构建完整提示词"""
        parts = []
        
        # 系统提示
        if system_prompt:
            parts.append(f"[系统] {system_prompt}")
        
        # 上下文（记忆）
        if context:
            context_parts = []
            for ctx in context[:5]:
                context_parts.append(f"- {ctx.get('content', '')}")
            if context_parts:
                parts.append(f"[相关记忆]\n" + "\n".join(context_parts))
        
        # 推理结果
        if reasoning:
            rec = reasoning.get("recommendation", "")
            if rec:
                parts.append(f"[推理建议] {rec}")
        
        # 用户输入
        parts.append(f"[用户] {prompt}")
        
        return "\n\n".join(parts)

    def _send_request(
        self,
        provider: ModelProvider,
        prompt: str
    ) -> ModelResponse:
        """发送请求到模型提供商"""
        # 这里是简化实现，实际需要根据不同 provider 调用不同 API
        
        # 如果配置了模拟模式，返回模拟响应
        if self.config.get("mock", True):
            return ModelResponse(
                provider=provider.provider_id,
                model=provider.model_name,
                content=f"[{provider.name} 回复] 这是一个基于十一层架构的响应。输入: {prompt[:30]}...",
                tokens_used=len(prompt) // 4,
                latency_ms=provider.latency_ms,
                timestamp=datetime.now().isoformat(),
                success=True
            )
        
        # 实际 API 调用需要根据 provider 实现
        # 这里留接口，实际使用时扩展
        raise NotImplementedError(f"需要实现 {provider.provider_id} 的 API 调用")

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
            "last_call": self.request_history[-1] if self.request_history else None
        }

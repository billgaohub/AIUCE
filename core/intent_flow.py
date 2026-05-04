"""
IntentFlow: 流式意图检测引擎
PASK DD (Demand Detection) 模块实现

基于 arXiv:2604.08000 PASK 论文的 IntentFlow 架构
实现从上下文流中实时检测潜在用户需求

核心能力：
1. 流式上下文监控
2. 潜在意图推断
3. 置信度评分
"""

from typing import Dict, Any, List, Optional, Tuple, Callable
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import json
import hashlib


class IntentType(Enum):
    """意图类型分类"""
    EXPLICIT = "explicit"      # 显性需求（用户明确表达）
    IMPLICIT = "implicit"      # 隐性需求（从上下文推断）
    LATENT = "latent"          # 潜在需求（深层推断）
    PROACTIVE = "proactive"    # 主动建议（系统发起）


class Urgency(Enum):
    """紧急程度"""
    LOW = 0.3
    NORMAL = 0.5
    HIGH = 0.7
    CRITICAL = 0.9


@dataclass
class IntentSignal:
    """意图信号"""
    intent_type: IntentType
    category: str               # health, finance, work, communication, etc.
    content: str                # 意图内容
    confidence: float           # 置信度 0-1
    urgency: Urgency
    context_window: List[str]   # 触发意图的上下文窗口
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    signal_id: str = field(default_factory=lambda: "")
    
    def __post_init__(self):
        if not self.signal_id:
            content_hash = hashlib.md5(f"{self.category}{self.content}{self.timestamp}".encode()).hexdigest()[:8]
            self.signal_id = f"intent_{content_hash}"
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "signal_id": self.signal_id,
            "intent_type": self.intent_type.value,
            "category": self.category,
            "content": self.content,
            "confidence": self.confidence,
            "urgency": self.urgency.value,
            "context_window": self.context_window,
            "timestamp": self.timestamp
        }


@dataclass
class ContextChunk:
    """上下文块"""
    content: str
    source: str              # user_input, system_response, external_event
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "content": self.content,
            "source": self.source,
            "timestamp": self.timestamp,
            "metadata": self.metadata
        }


class IntentFlow:
    """
    流式意图检测引擎
    
    基于 PASK 论文的 DD (Demand Detection) 模块
    持续监控上下文流，检测潜在用户需求
    
    使用方式：
    ```python
    flow = IntentFlow()
    flow.push_context("我今天又要加班到很晚", source="user_input")
    signals = flow.detect_intents()
    # signals 可能包含: [IntentSignal(category="health", content="提醒休息", ...)]
    ```
    """
    
    MAX_CONTEXT_WINDOW = 50     # 最大上下文窗口大小
    MIN_CONFIDENCE = 0.3        # 最小置信度阈值
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.context_buffer: List[ContextChunk] = []
        self.intent_history: List[IntentSignal] = []
        self._pattern_matchers: List[Callable] = []
        self._setup_default_matchers()
    
    def _setup_default_matchers(self):
        """设置默认模式匹配器"""
        self._pattern_matchers = [
            self._match_health_intent,
            self._match_finance_intent,
            self._match_time_intent,
            self._match_work_intent,
            self._match_communication_intent,
            self._match_proactive_suggestion,
        ]
    
    def push_context(self, content: str, source: str = "user_input", metadata: Dict[str, Any] = None):
        """
        推送上下文到流中
        
        Args:
            content: 上下文内容
            source: 来源 (user_input, system_response, external_event)
            metadata: 额外元数据
        """
        chunk = ContextChunk(
            content=content,
            source=source,
            metadata=metadata or {}
        )
        self.context_buffer.append(chunk)
        
        # 维护窗口大小
        if len(self.context_buffer) > self.MAX_CONTEXT_WINDOW:
            self.context_buffer.pop(0)
    
    def detect_intents(self) -> List[IntentSignal]:
        """
        从当前上下文流中检测意图信号
        
        Returns:
            检测到的意图信号列表
        """
        signals = []
        
        for matcher in self._pattern_matchers:
            try:
                matched_signals = matcher()
                if matched_signals:
                    signals.extend(matched_signals)
            except Exception as e:
                continue
        
        # 过滤低置信度信号
        signals = [s for s in signals if s.confidence >= self.MIN_CONFIDENCE]
        
        # 按置信度排序
        signals.sort(key=lambda s: s.confidence, reverse=True)
        
        # 记录历史
        self.intent_history.extend(signals)
        
        return signals
    
    def get_context_window(self, last_n: int = 10) -> List[str]:
        """获取最近 N 条上下文"""
        chunks = self.context_buffer[-last_n:]
        return [c.content for c in chunks]
    
    def get_recent_intents(self, last_n: int = 5) -> List[Dict[str, Any]]:
        """获取最近 N 条意图信号"""
        signals = self.intent_history[-last_n:]
        return [s.to_dict() for s in signals]
    
    def clear_context(self):
        """清空上下文缓冲区"""
        self.context_buffer.clear()
    
    # ─────────────────────────────────────────────────────────
    # 模式匹配器
    # ─────────────────────────────────────────────────────────
    
    def _match_health_intent(self) -> List[IntentSignal]:
        """检测健康相关意图"""
        signals = []
        window = self.get_context_window(10)
        window_text = " ".join(window).lower()
        
        health_keywords = {
            "疲劳": ("提醒休息", Urgency.HIGH),
            "累": ("建议休息", Urgency.NORMAL),
            "头痛": ("健康提醒", Urgency.HIGH),
            "失眠": ("睡眠建议", Urgency.NORMAL),
            "熬夜": ("作息提醒", Urgency.HIGH),
            "加班": ("工作生活平衡提醒", Urgency.NORMAL),
            "生病": ("就医提醒", Urgency.CRITICAL),
            "感冒": ("健康关怀", Urgency.NORMAL),
            "锻炼": ("运动提醒", Urgency.LOW),
            "运动": ("健身建议", Urgency.LOW),
        }
        
        for kw, (suggestion, urgency) in health_keywords.items():
            if kw in window_text:
                context = self._get_trigger_context(kw, window)
                signals.append(IntentSignal(
                    intent_type=IntentType.IMPLICIT,
                    category="health",
                    content=suggestion,
                    confidence=0.6 + (0.2 if urgency in [Urgency.HIGH, Urgency.CRITICAL] else 0),
                    urgency=urgency,
                    context_window=context
                ))
        
        return signals
    
    def _match_finance_intent(self) -> List[IntentSignal]:
        """检测财务相关意图"""
        signals = []
        window = self.get_context_window(10)
        window_text = " ".join(window).lower()
        
        finance_keywords = {
            "账单": ("账单提醒", Urgency.NORMAL),
            "还款": ("还款提醒", Urgency.HIGH),
            "工资": ("收入记录", Urgency.LOW),
            "投资": ("投资建议", Urgency.LOW),
            "花销": ("支出分析", Urgency.NORMAL),
            "省钱": ("省钱建议", Urgency.LOW),
            "预算": ("预算规划", Urgency.NORMAL),
        }
        
        for kw, (suggestion, urgency) in finance_keywords.items():
            if kw in window_text:
                context = self._get_trigger_context(kw, window)
                signals.append(IntentSignal(
                    intent_type=IntentType.IMPLICIT,
                    category="finance",
                    content=suggestion,
                    confidence=0.55,
                    urgency=urgency,
                    context_window=context
                ))
        
        return signals
    
    def _match_time_intent(self) -> List[IntentSignal]:
        """检测时间相关意图"""
        signals = []
        window = self.get_context_window(10)
        window_text = " ".join(window).lower()
        
        time_keywords = {
            "明天": ("日程提醒", Urgency.NORMAL),
            "下周": ("计划提醒", Urgency.LOW),
            "会议": ("会议提醒", Urgency.NORMAL),
            "约会": ("约会提醒", Urgency.NORMAL),
            "截止": ("截止日期提醒", Urgency.HIGH),
            "deadline": ("截止提醒", Urgency.HIGH),
            "忘了": ("备忘提醒", Urgency.HIGH),
        }
        
        for kw, (suggestion, urgency) in time_keywords.items():
            if kw in window_text:
                context = self._get_trigger_context(kw, window)
                signals.append(IntentSignal(
                    intent_type=IntentType.IMPLICIT,
                    category="time",
                    content=suggestion,
                    confidence=0.65,
                    urgency=urgency,
                    context_window=context
                ))
        
        return signals
    
    def _match_work_intent(self) -> List[IntentSignal]:
        """检测工作相关意图"""
        signals = []
        window = self.get_context_window(10)
        window_text = " ".join(window).lower()
        
        work_keywords = {
            "项目": ("项目管理建议", Urgency.NORMAL),
            "报告": ("报告撰写协助", Urgency.NORMAL),
            "代码": ("代码审查建议", Urgency.LOW),
            "bug": ("问题追踪", Urgency.HIGH),
            "上线": ("上线检查清单", Urgency.HIGH),
            "部署": ("部署提醒", Urgency.NORMAL),
        }
        
        for kw, (suggestion, urgency) in work_keywords.items():
            if kw in window_text:
                context = self._get_trigger_context(kw, window)
                signals.append(IntentSignal(
                    intent_type=IntentType.IMPLICIT,
                    category="work",
                    content=suggestion,
                    confidence=0.5,
                    urgency=urgency,
                    context_window=context
                ))
        
        return signals
    
    def _match_communication_intent(self) -> List[IntentSignal]:
        """检测沟通相关意图"""
        signals = []
        window = self.get_context_window(10)
        window_text = " ".join(window).lower()
        
        comm_keywords = {
            "回复": ("回复提醒", Urgency.NORMAL),
            "邮件": ("邮件处理建议", Urgency.NORMAL),
            "消息": ("消息提醒", Urgency.LOW),
            "电话": ("回电提醒", Urgency.NORMAL),
        }
        
        for kw, (suggestion, urgency) in comm_keywords.items():
            if kw in window_text:
                context = self._get_trigger_context(kw, window)
                signals.append(IntentSignal(
                    intent_type=IntentType.IMPLICIT,
                    category="communication",
                    content=suggestion,
                    confidence=0.45,
                    urgency=urgency,
                    context_window=context
                ))
        
        return signals
    
    def _match_proactive_suggestion(self) -> List[IntentSignal]:
        """主动建议生成"""
        signals = []
        
        if len(self.intent_history) >= 3:
            recent_categories = [s.category for s in self.intent_history[-3:]]
            
            if recent_categories.count("health") >= 2:
                signals.append(IntentSignal(
                    intent_type=IntentType.PROACTIVE,
                    category="health",
                    content="连续检测到健康相关信号，建议进行健康检查",
                    confidence=0.7,
                    urgency=Urgency.HIGH,
                    context_window=self.get_context_window(5)
                ))
            
            if recent_categories.count("work") >= 2:
                signals.append(IntentSignal(
                    intent_type=IntentType.PROACTIVE,
                    category="work",
                    content="工作强度较高，建议适当休息",
                    confidence=0.6,
                    urgency=Urgency.NORMAL,
                    context_window=self.get_context_window(5)
                ))
        
        return signals
    
    def _get_trigger_context(self, keyword: str, window: List[str], context_size: int = 2) -> List[str]:
        """获取触发关键词的上下文"""
        for i, text in enumerate(window):
            if keyword in text:
                start = max(0, i - context_size)
                end = min(len(window), i + context_size + 1)
                return window[start:end]
        return window[-context_size:] if window else []
    
    def to_dict(self) -> Dict[str, Any]:
        """序列化状态"""
        return {
            "context_buffer": [c.to_dict() for c in self.context_buffer],
            "intent_history": [s.to_dict() for s in self.intent_history],
            "config": self.config
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "IntentFlow":
        """从字典恢复"""
        flow = cls(config=data.get("config", {}))
        flow.context_buffer = [
            ContextChunk(**c) for c in data.get("context_buffer", [])
        ]
        flow.intent_history = [
            IntentSignal(
                intent_type=IntentType(s["intent_type"]),
                category=s["category"],
                content=s["content"],
                confidence=s["confidence"],
                urgency=Urgency(s["urgency"]),
                context_window=s["context_window"],
                timestamp=s["timestamp"],
                signal_id=s["signal_id"]
            )
            for s in data.get("intent_history", [])
        ]
        return flow

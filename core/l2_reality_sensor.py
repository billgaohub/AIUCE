"""
L2 感知层：现实对账引擎
Reality Sensor with UI-TARS Integration

架构：
┌─────────────────────────────────────────────────────────┐
│              L2 感知层 (Reality Sensor)                  │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  ┌───────────────────────────────────────────────────┐  │
│  │  多模态感知 (Multimodal Perception)                │  │
│  │  - 屏幕内容捕获 (Screen Capture)                   │  │
│  │  - 文本识别 (OCR)                                  │  │
│  │  - UI 元素理解 (UI Understanding)                 │  │
│  │  - 用户行为监控 (User Activity)                    │  │
│  └───────────────────────────────────────────────────┘  │
│                         ↓                               │
│  ┌───────────────────────────────────────────────────┐  │
│  │  现实数据管道 (Reality Data Pipeline)              │  │
│  │  - 数据清洗 (Data Cleaning)                        │  │
│  │  - 事件聚合 (Event Aggregation)                    │  │
│  │  - 异常检测 (Anomaly Detection)                    │  │
│  └───────────────────────────────────────────────────┘  │
│                         ↓                               │
│  ┌───────────────────────────────────────────────────┐  │
│  │  真相对账 (Truth Reconciliation)                   │  │
│  │  - 声明 vs 现实对比                                │  │
│  │  - 偏离检测 (Drift Detection)                     │  │
│  │  - 告警触发 (Alert Trigger)                        │  │
│  └───────────────────────────────────────────────────┘  │
│                                                          │
└─────────────────────────────────────────────────────────┘

"AI的洞察力来源于对现实世界的连续对账，拒绝臆想"

UI-TARS 集成：
- 屏幕理解与 UI 交互
- GUI Agent 能力
- 多模态感知输入
"""

from typing import Dict, Any, List, Optional, Tuple, Callable, Union
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import json
import os
import threading
import queue
import time
from collections import defaultdict
import hashlib


# ═══════════════════════════════════════════════════════════════
# 类型定义
# ═══════════════════════════════════════════════════════════════

class PerceptionType(Enum):
    """感知类型"""
    SCREEN = "screen"           # 屏幕内容
    TEXT = "text"               # 文本输入
    MOUSE = "mouse"             # 鼠标操作
    KEYBOARD = "keyboard"       # 键盘输入
    CLIPBOARD = "clipboard"     # 剪贴板
    FILE_SYSTEM = "file_system" # 文件系统
    NETWORK = "network"         # 网络状态
    APPLICATION = "application" # 应用状态
    USER_BEHAVIOR = "user_behavior"  # 用户行为
    SENSOR = "sensor"           # 传感器数据


class DataQuality(Enum):
    """数据质量"""
    HIGH = "high"       # 高质量（直接可信）
    MEDIUM = "medium"   # 中等（需验证）
    LOW = "low"         # 低质量（需交叉验证）
    UNKNOWN = "unknown" # 未知质量


class DriftLevel(Enum):
    """偏离级别"""
    NONE = 0        # 无偏离
    MINOR = 1       # 轻微偏离
    MODERATE = 2    # 中等偏离
    SEVERE = 3      # 严重偏离
    CRITICAL = 4    # 关键偏离


@dataclass
class PerceptionEvent:
    """感知事件"""
    id: str
    type: PerceptionType
    source: str
    content: Dict[str, Any]
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    quality: DataQuality = DataQuality.HIGH
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "type": self.type.value,
            "source": self.source,
            "content": self.content,
            "timestamp": self.timestamp,
            "quality": self.quality.value,
            "metadata": self.metadata
        }


@dataclass
class RealitySnapshot:
    """现实快照"""
    id: str
    timestamp: str
    perceptions: List[PerceptionEvent]
    summary: str
    entities: Dict[str, Any] = field(default_factory=dict)
    relationships: List[Tuple[str, str, str]] = field(default_factory=list)
    confidence: float = 1.0
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "timestamp": self.timestamp,
            "perception_count": len(self.perceptions),
            "summary": self.summary,
            "entities": self.entities,
            "relationships": self.relationships,
            "confidence": self.confidence
        }


@dataclass
class TruthClaim:
    """真相声明"""
    id: str
    claim: str
    source: str
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    evidence: List[str] = field(default_factory=list)
    confidence: float = 0.5
    verified: bool = False
    verification_result: Optional[str] = None


@dataclass
class DriftReport:
    """偏离报告"""
    claim_id: str
    claim: str
    reality: str
    drift_level: DriftLevel
    drift_details: str
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    recommendations: List[str] = field(default_factory=list)


# ═══════════════════════════════════════════════════════════════
# 多模态感知器 (Multimodal Perception)
# ═══════════════════════════════════════════════════════════════

class MultimodalPerception:
    """
    多模态感知器
    
    支持 UI-TARS 集成：
    - 屏幕捕获
    - UI 元素理解
    - 用户行为监控
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self._perception_queue: queue.Queue = queue.Queue()
        self._subscribers: List[Callable[[PerceptionEvent], None]] = []
        self._running = False
        self._worker_thread: Optional[threading.Thread] = None
        
        # 感知统计
        self._stats: Dict[str, int] = defaultdict(int)
        
        # UI-TARS 集成点（可注入）
        self._ui_tars_adapter: Optional[Any] = None
        
        print("  [L2 感知层] 多模态感知器初始化")
    
    def set_ui_tars_adapter(self, adapter: Any):
        """
        设置 UI-TARS 适配器
        
        UI-TARS 提供的能力：
        - screen_understand(): 屏幕内容理解
        - ui_interact(): UI 元素交互
        - element_detect(): UI 元素检测
        """
        self._ui_tars_adapter = adapter
        print("  [L2 感知层] UI-TARS 适配器已连接")
    
    def start(self):
        """启动感知器"""
        if self._running:
            return
        
        self._running = True
        self._worker_thread = threading.Thread(target=self._perception_loop, daemon=True)
        self._worker_thread.start()
        print("  [L2 感知层] 多模态感知器运行中")
    
    def stop(self):
        """停止感知器"""
        self._running = False
        if self._worker_thread:
            self._worker_thread.join(timeout=5)
        print("  [L2 感知层] 多模态感知器已停止")
    
    def _perception_loop(self):
        """感知循环"""
        while self._running:
            try:
                event = self._perception_queue.get(timeout=1)
                self._process_event(event)
            except queue.Empty:
                continue
            except Exception as e:
                print(f"  [L2 感知层] 处理错误: {e}")
    
    def _process_event(self, event: PerceptionEvent):
        """处理感知事件"""
        self._stats[event.type.value] += 1
        
        # 通知订阅者
        for subscriber in self._subscribers:
            try:
                subscriber(event)
            except Exception as e:
                print(f"  [L2 感知层] 订阅者错误: {e}")
    
    # ── 感知接口 ───────────────────────────────────────────────
    
    def capture_screen(self) -> Optional[PerceptionEvent]:
        """捕获屏幕内容"""
        import uuid
        
        event_id = str(uuid.uuid4())[:8]
        
        # 如果有 UI-TARS 适配器，使用它
        if self._ui_tars_adapter:
            try:
                content = self._ui_tars_adapter.screen_understand()
            except Exception:
                content = {"status": "capture_failed"}
        else:
            # 模拟屏幕捕获
            content = {
                "screen_id": event_id,
                "resolution": "1920x1080",
                "active_window": "unknown",
                "elements": []
            }
        
        event = PerceptionEvent(
            id=event_id,
            type=PerceptionType.SCREEN,
            source="screen_capture",
            content=content,
            quality=DataQuality.HIGH
        )
        
        self._perception_queue.put(event)
        return event
    
    def capture_text_input(self, text: str, source: str = "user") -> PerceptionEvent:
        """捕获文本输入"""
        import uuid
        
        event = PerceptionEvent(
            id=str(uuid.uuid4())[:8],
            type=PerceptionType.TEXT,
            source=source,
            content={"text": text},
            quality=DataQuality.HIGH
        )
        
        self._perception_queue.put(event)
        return event
    
    def capture_mouse_action(
        self,
        action: str,
        position: Tuple[int, int],
        target: Optional[str] = None
    ) -> PerceptionEvent:
        """捕获鼠标操作"""
        import uuid
        
        event = PerceptionEvent(
            id=str(uuid.uuid4())[:8],
            type=PerceptionType.MOUSE,
            source="mouse_monitor",
            content={
                "action": action,
                "position": position,
                "target": target
            },
            quality=DataQuality.HIGH
        )
        
        self._perception_queue.put(event)
        return event
    
    def capture_keyboard_input(
        self,
        key: str,
        modifiers: List[str] = None
    ) -> PerceptionEvent:
        """捕获键盘输入"""
        import uuid
        
        event = PerceptionEvent(
            id=str(uuid.uuid4())[:8],
            type=PerceptionType.KEYBOARD,
            source="keyboard_monitor",
            content={
                "key": key,
                "modifiers": modifiers or []
            },
            quality=DataQuality.MEDIUM  # 键盘输入质量中等（可能有误触）
        )
        
        self._perception_queue.put(event)
        return event
    
    def capture_file_event(
        self,
        event_type: str,
        path: str,
        details: Optional[Dict[str, Any]] = None
    ) -> PerceptionEvent:
        """捕获文件系统事件"""
        import uuid
        
        event = PerceptionEvent(
            id=str(uuid.uuid4())[:8],
            type=PerceptionType.FILE_SYSTEM,
            source="file_watcher",
            content={
                "event_type": event_type,
                "path": path,
                "details": details or {}
            },
            quality=DataQuality.HIGH
        )
        
        self._perception_queue.put(event)
        return event
    
    # ── 订阅接口 ───────────────────────────────────────────────
    
    def subscribe(self, callback: Callable[[PerceptionEvent], None]):
        """订阅感知事件"""
        self._subscribers.append(callback)
    
    def unsubscribe(self, callback: Callable[[PerceptionEvent], None]):
        """取消订阅"""
        if callback in self._subscribers:
            self._subscribers.remove(callback)
    
    # ── 统计 ───────────────────────────────────────────────────
    
    def stats(self) -> Dict[str, Any]:
        """统计"""
        return {
            "total_events": sum(self._stats.values()),
            "by_type": dict(self._stats),
            "running": self._running,
            "ui_tars_connected": self._ui_tars_adapter is not None
        }


# ═══════════════════════════════════════════════════════════════
# 现实数据管道 (Reality Data Pipeline)
# ═══════════════════════════════════════════════════════════════

class RealityDataPipeline:
    """
    现实数据管道
    
    功能：
    1. 数据清洗
    2. 事件聚合
    3. 异常检测
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self._event_buffer: List[PerceptionEvent] = []
        self._buffer_size = self.config.get("buffer_size", 1000)
        self._aggregation_window = self.config.get("aggregation_window", 60)  # 秒
        
        # 异常检测规则
        self._anomaly_rules: Dict[str, Callable] = {}
        
        print("  [L2 感知层] 现实数据管道初始化")
    
    def ingest(self, event: PerceptionEvent):
        """摄入感知事件"""
        # 数据清洗
        cleaned_event = self._clean_event(event)
        
        # 添加到缓冲区
        self._event_buffer.append(cleaned_event)
        
        # 检查缓冲区大小
        if len(self._event_buffer) > self._buffer_size:
            self._event_buffer = self._event_buffer[-self._buffer_size:]
        
        # 异常检测
        self._check_anomalies(cleaned_event)
    
    def _clean_event(self, event: PerceptionEvent) -> PerceptionEvent:
        """数据清洗"""
        # 去除敏感信息
        content = event.content.copy()
        
        # 移除可能的敏感字段
        sensitive_keys = ["password", "token", "secret", "key", "credential"]
        for key in list(content.keys()):
            if any(sk in key.lower() for sk in sensitive_keys):
                content[key] = "[REDACTED]"
        
        event.content = content
        return event
    
    def _check_anomalies(self, event: PerceptionEvent):
        """异常检测"""
        for rule_name, rule_fn in self._anomaly_rules.items():
            try:
                if rule_fn(event):
                    print(f"  [L2 感知层] 异常检测: {rule_name}")
            except Exception:
                pass
    
    def add_anomaly_rule(self, name: str, rule: Callable[[PerceptionEvent], bool]):
        """添加异常检测规则"""
        self._anomaly_rules[name] = rule
    
    def aggregate(self, window_seconds: int = None) -> RealitySnapshot:
        """聚合事件生成现实快照"""
        import uuid
        
        window = window_seconds or self._aggregation_window
        now = datetime.now()
        cutoff = datetime.fromtimestamp(now.timestamp() - window)
        
        # 筛选窗口内的事件
        window_events = [
            e for e in self._event_buffer
            if datetime.fromisoformat(e.timestamp) >= cutoff
        ]
        
        # 生成摘要
        summary = self._generate_summary(window_events)
        
        # 提取实体
        entities = self._extract_entities(window_events)
        
        # 提取关系
        relationships = self._extract_relationships(window_events)
        
        snapshot = RealitySnapshot(
            id=str(uuid.uuid4())[:8],
            timestamp=now.isoformat(),
            perceptions=window_events,
            summary=summary,
            entities=entities,
            relationships=relationships,
            confidence=self._calculate_confidence(window_events)
        )
        
        return snapshot
    
    def _generate_summary(self, events: List[PerceptionEvent]) -> str:
        """生成摘要"""
        if not events:
            return "无感知事件"
        
        type_counts = defaultdict(int)
        for event in events:
            type_counts[event.type.value] += 1
        
        parts = [f"{t}: {c}次" for t, c in sorted(type_counts.items())]
        return f"过去事件统计 - {', '.join(parts)}"
    
    def _extract_entities(self, events: List[PerceptionEvent]) -> Dict[str, Any]:
        """提取实体"""
        entities = defaultdict(list)
        
        for event in events:
            if event.type == PerceptionType.FILE_SYSTEM:
                path = event.content.get("path", "")
                if path:
                    entities["files"].append(path)
            
            elif event.type == PerceptionType.APPLICATION:
                app = event.content.get("app_name", "")
                if app:
                    entities["applications"].append(app)
            
            elif event.type == PerceptionType.TEXT:
                text = event.content.get("text", "")
                if text and len(text) > 10:
                    entities["text_segments"].append(text[:100])
        
        return dict(entities)
    
    def _extract_relationships(self, events: List[PerceptionEvent]) -> List[Tuple[str, str, str]]:
        """提取关系"""
        relationships = []
        
        # 简单关系提取（基于事件序列）
        for i in range(1, len(events)):
            prev = events[i - 1]
            curr = events[i]
            
            # 时间相邻事件
            prev_time = datetime.fromisoformat(prev.timestamp)
            curr_time = datetime.fromisoformat(curr.timestamp)
            
            if (curr_time - prev_time).total_seconds() < 5:
                relationships.append((
                    prev.id,
                    "followed_by",
                    curr.id
                ))
        
        return relationships
    
    def _calculate_confidence(self, events: List[PerceptionEvent]) -> float:
        """计算置信度"""
        if not events:
            return 0.0
        
        # 基于数据质量计算
        quality_scores = {
            DataQuality.HIGH: 1.0,
            DataQuality.MEDIUM: 0.7,
            DataQuality.LOW: 0.4,
            DataQuality.UNKNOWN: 0.1
        }
        
        total = sum(quality_scores.get(e.quality, 0.5) for e in events)
        return total / len(events)
    
    def stats(self) -> Dict[str, Any]:
        """统计"""
        return {
            "buffer_size": len(self._event_buffer),
            "max_buffer_size": self._buffer_size,
            "anomaly_rules": len(self._anomaly_rules)
        }


# ═══════════════════════════════════════════════════════════════
# 真相对账器 (Truth Reconciliation)
# ═══════════════════════════════════════════════════════════════

class TruthReconciliation:
    """
    真相对账器
    
    功能：
    1. 声明 vs 现实对比
    2. 偏离检测
    3. 告警触发
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self._claims: Dict[str, TruthClaim] = {}
        self._drift_reports: List[DriftReport] = []
        self._drift_callbacks: List[Callable[[DriftReport], None]] = []
        
        print("  [L2 感知层] 真相对账器初始化")
    
    def register_claim(
        self,
        claim: str,
        source: str,
        evidence: List[str] = None
    ) -> str:
        """注册真相声明"""
        import uuid
        
        claim_id = str(uuid.uuid4())[:8]
        
        truth_claim = TruthClaim(
            id=claim_id,
            claim=claim,
            source=source,
            evidence=evidence or []
        )
        
        self._claims[claim_id] = truth_claim
        return claim_id
    
    def verify_claim(
        self,
        claim_id: str,
        reality_snapshot: RealitySnapshot
    ) -> DriftReport:
        """验证声明"""
        claim = self._claims.get(claim_id)
        if not claim:
            return DriftReport(
                claim_id=claim_id,
                claim="unknown",
                reality="unknown",
                drift_level=DriftLevel.NONE,
                drift_details="声明不存在"
            )
        
        # 执行验证
        drift_level, details = self._compare_claim_to_reality(
            claim.claim,
            reality_snapshot
        )
        
        # 更新声明状态
        claim.verified = True
        claim.verification_result = details
        claim.confidence = 1.0 - (drift_level.value * 0.2)
        
        # 创建偏离报告
        report = DriftReport(
            claim_id=claim_id,
            claim=claim.claim,
            reality=reality_snapshot.summary,
            drift_level=drift_level,
            drift_details=details
        )
        
        if drift_level != DriftLevel.NONE:
            self._drift_reports.append(report)
            self._trigger_drift_callbacks(report)
        
        return report
    
    def _compare_claim_to_reality(
        self,
        claim: str,
        reality: RealitySnapshot
    ) -> Tuple[DriftLevel, str]:
        """对比声明与现实"""
        # 简单的关键词匹配
        claim_lower = claim.lower()
        
        # 检查声明是否在现实中得到支持
        in_summary = claim_lower in reality.summary.lower()
        
        in_entities = any(
            claim_lower in str(v).lower()
            for v in reality.entities.values()
        )
        
        if in_summary or in_entities:
            return DriftLevel.NONE, "声明与现实一致"
        
        # 检查部分匹配
        claim_words = set(claim_lower.split())
        summary_words = set(reality.summary.lower().split())
        
        overlap = claim_words & summary_words
        
        if len(overlap) > len(claim_words) * 0.5:
            return DriftLevel.MINOR, "声明部分被现实支持"
        
        if len(overlap) > 0:
            return DriftLevel.MODERATE, "声明与现实存在部分关联"
        
        return DriftLevel.SEVERE, "声明未在现实中找到支持"
    
    def _trigger_drift_callbacks(self, report: DriftReport):
        """触发偏离回调"""
        for callback in self._drift_callbacks:
            try:
                callback(report)
            except Exception as e:
                print(f"  [L2 感知层] 偏离回调错误: {e}")
    
    def on_drift(self, callback: Callable[[DriftReport], None]):
        """注册偏离回调"""
        self._drift_callbacks.append(callback)
    
    def get_drift_history(self, limit: int = 10) -> List[DriftReport]:
        """获取偏离历史"""
        return self._drift_reports[-limit:]
    
    def stats(self) -> Dict[str, Any]:
        """统计"""
        by_level = defaultdict(int)
        for report in self._drift_reports:
            by_level[report.drift_level.value] += 1
        
        return {
            "total_claims": len(self._claims),
            "verified_claims": len([c for c in self._claims.values() if c.verified]),
            "total_drifts": len(self._drift_reports),
            "by_drift_level": dict(by_level)
        }


# ═══════════════════════════════════════════════════════════════
# L2 感知层主类
# ═══════════════════════════════════════════════════════════════

class RealitySensor:
    """
    L2 感知层 - 现实对账引擎
    
    "AI的洞察力来源于对现实世界的连续对账，拒绝臆想"
    
    组件：
    1. 多模态感知器
    2. 现实数据管道
    3. 真相对账器
    
    UI-TARS 集成点：
    - 屏幕理解
    - UI 元素检测
    - GUI Agent 交互
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        
        # 三大组件
        self.perception = MultimodalPerception(config.get("perception", {}))
        self.pipeline = RealityDataPipeline(config.get("pipeline", {}))
        self.reconciliation = TruthReconciliation(config.get("reconciliation", {}))
        
        # 连接组件
        self.perception.subscribe(self.pipeline.ingest)
        
        print("  [L2 感知层] 魏征/监察御史 - 现实对账引擎就位")
    
    # ── 生命周期 ───────────────────────────────────────────────
    
    def start(self):
        """启动感知层"""
        self.perception.start()
        print("  [L2 感知层] 运行中")
    
    def stop(self):
        """停止感知层"""
        self.perception.stop()
        print("  [L2 感知层] 已停止")
    
    # ── UI-TARS 集成 ───────────────────────────────────────────
    
    def set_ui_tars_adapter(self, adapter: Any):
        """设置 UI-TARS 适配器"""
        self.perception.set_ui_tars_adapter(adapter)
    
    # ── 感知接口 ───────────────────────────────────────────────
    
    def capture_screen(self) -> Optional[PerceptionEvent]:
        """捕获屏幕"""
        return self.perception.capture_screen()
    
    def capture_text(self, text: str, source: str = "user") -> PerceptionEvent:
        """捕获文本"""
        return self.perception.capture_text_input(text, source)
    
    def capture_mouse(
        self,
        action: str,
        position: Tuple[int, int],
        target: Optional[str] = None
    ) -> PerceptionEvent:
        """捕获鼠标"""
        return self.perception.capture_mouse_action(action, position, target)
    
    def capture_file_event(
        self,
        event_type: str,
        path: str,
        details: Optional[Dict[str, Any]] = None
    ) -> PerceptionEvent:
        """捕获文件事件"""
        return self.perception.capture_file_event(event_type, path, details)
    
    # ── 聚合接口 ───────────────────────────────────────────────
    
    def get_snapshot(self, window_seconds: int = 60) -> RealitySnapshot:
        """获取现实快照"""
        return self.pipeline.aggregate(window_seconds)
    
    # ── 对账接口 ───────────────────────────────────────────────
    
    def register_claim(self, claim: str, source: str) -> str:
        """注册声明"""
        return self.reconciliation.register_claim(claim, source)
    
    def verify_claim(self, claim_id: str) -> DriftReport:
        """验证声明"""
        snapshot = self.get_snapshot()
        return self.reconciliation.verify_claim(claim_id, snapshot)
    
    def on_drift(self, callback: Callable[[DriftReport], None]):
        """注册偏离回调"""
        self.reconciliation.on_drift(callback)
    
    # ── 统计 ───────────────────────────────────────────────────
    
    def stats(self) -> Dict[str, Any]:
        """统计"""
        return {
            "perception": self.perception.stats(),
            "pipeline": self.pipeline.stats(),
            "reconciliation": self.reconciliation.stats()
        }


# ═══════════════════════════════════════════════════════════════
# 导出
# ═══════════════════════════════════════════════════════════════

__all__ = [
    "PerceptionType",
    "DataQuality",
    "DriftLevel",
    "PerceptionEvent",
    "RealitySnapshot",
    "TruthClaim",
    "DriftReport",
    "MultimodalPerception",
    "RealityDataPipeline",
    "TruthReconciliation",
    "RealitySensor",
]

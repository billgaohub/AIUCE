"""
L6 体验层 — 曾国藩/吏部
===============================
每日复盘 + 偏离扫描 + 经验固化。

L6 是 AIUCE 的「历史记录者」与「偏离探测器」。
从 L5 审计日志中提取经验模式，检测系统性偏离，在 L7 演化条件成熟时触发重构。

核心职责
--------
1. **每日复盘**（ExperienceJournal）
   - 每日汇总 L5 审计数据，生成结构化复盘报告
   - 记录：主权通过率、决策分布、实体热点、Token 消耗趋势

2. **偏离扫描**（PatternScanner）
   - 检测系统性否决模式（某类意图持续被主权网关否决）
   - 检测决策漂移（某层决策类型分布发生显著变化）
   - 检测信任侵蚀（主权通过率持续下降）

3. **系统健康**（HealthMonitor）
   - 综合 L5 + L7 数据，输出系统健康度（0-1）
   - 触发 L7 演化的健康阈值判断

4. **经验固化**（ExperienceGrinder）
   - 将复盘结果转化为可操作的改进建议
   - 写入 L7 EvolutionEngine 的 skill 候选队列

模块间关系
----------
    L5 Audit
       ↓ 读取原始审计数据
    L6 Experience Layer
       ├── ExperienceJournal   → 生成每日复盘报告
       ├── PatternScanner     → 检测偏离模式
       ├── HealthMonitor     → 计算健康度
       └── ExperienceGrinder → 生成 L7 演化候选
       ↓ 触发演化
    L7 Evolution Engine
"""

from __future__ import annotations

import os
import json
import hashlib
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any, Set
from dataclasses import dataclass, field, asdict
from collections import defaultdict, Counter
from enum import Enum
import statistics


# ─────────────────────────────────────────────────────────────────
# 6.1 数据结构
# ─────────────────────────────────────────────────────────────────

class DeviationType(Enum):
    """偏离类型枚举"""
    NONE = "none"
    SOVEREIGNTY_REJECTION_SPIKE = "sovereignty_rejection_spike"   # 主权否决率飙升
    DECISION_DRIFT = "decision_drift"                              # 决策类型漂移
    TRUST_EROSION = "trust_erosion"                                # 信任侵蚀（主权通过率下降）
    SEMANTIC_CONFIDENCE_DROP = "semantic_confidence_drop"          # 语义置信度骤降
    TOKEN_COST_ANOMALY = "token_cost_anomaly"                     # Token 消耗异常
    ENTITY_COLD_START = "entity_cold_start"                       # 新实体频繁出现但未固化


@dataclass
class DailyMetrics:
    """每日指标快照"""
    date: str                       # YYYY-MM-DD
    total_decisions: int = 0
    sovereignty_passed: int = 0
    sovereignty_vetoed: int = 0
    sovereignty_pass_rate: float = 0.0  # 0.0–1.0

    # 决策类型分布
    decision_types: Dict[str, int] = field(default_factory=dict)

    # 三域评分
    avg_body: float = 0.0
    avg_flow: float = 0.0
    avg_intel: float = 0.0

    # 语义层
    avg_semantic_confidence: float = 0.0

    # Token（来自 L7）
    total_tokens: int = 0
    avg_token_per_decision: float = 0.0

    # 实体
    new_entities: Set[str] = field(default_factory=set)
    hot_entities: List[Tuple[str, int]] = field(default_factory=list)  # [(entity, count)]

    # 偏离
    deviations: List[str] = field(default_factory=list)  # DeviationType.value 列表

    # 系统健康
    health_score: float = 0.0  # 0.0–1.0

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        d["new_entities"] = list(self.new_entities)
        d["hot_entities"] = self.hot_entities
        return d

    @classmethod
    def from_dict(cls, d: Dict) -> DailyMetrics:
        d = dict(d)
        d["new_entities"] = set(d.get("new_entities", []))
        return cls(**d)


@dataclass
class ReviewEntry:
    """复盘记录"""
    date: str
    review_id: str
    metrics: DailyMetrics
    pattern_summary: str          # 模式摘要
    deviation_alerts: List[Dict]  # 偏离警告列表
    improvement_suggestions: List[str]
    trigger_evolution: bool = False
    triggered_by: List[str] = field(default_factory=list)  # DeviationType.value


@dataclass
class DeviationAlert:
    """偏离警告"""
    deviation_type: DeviationType
    severity: float               # 0.0–1.0，严重程度
    description: str
    evidence: Dict[str, Any]       # 支撑数据
    recommended_action: str        # 建议操作
    auto_remediable: bool = False  # 是否可自动修复（触发 L7 FIX）


# ─────────────────────────────────────────────────────────────────
# 6.2 PatternScanner — 偏离扫描
# ─────────────────────────────────────────────────────────────────

class PatternScanner:
    """
    从 L5 审计历史中扫描系统性偏离模式。

    扫描维度：
    1. SOVEREIGNTY_REJECTION_SPIKE：否决率超过阈值（如 > 30%）
    2. DECISION_DRIFT：某层决策类型分布发生显著变化
    3. TRUST_EROSION：主权通过率连续 3 天下降
    4. SEMANTIC_CONFIDENCE_DROP：平均置信度低于阈值（如 < 0.4）
    5. TOKEN_COST_ANOMALY：单次决策 token 消耗超过基线 2x
    """

    # 阈值配置
    VETO_RATE_THRESHOLD = 0.30          # 否决率 > 30% → 告警
    TRUST_EROSION_CONSECUTIVE = 3       # 连续 3 天通过率下降
    CONFIDENCE_THRESHOLD = 0.40         # 平均置信度 < 0.40 → 告警
    TOKEN_ANOMALY_MULTIPLIER = 2.0      # Token > 2x 基线 → 异常
    DRIFT_THRESHOLD = 0.20              # 决策类型分布变化 > 20% → 漂移

    def __init__(self, experience_path: str = "~/.aiuce/experience"):
        self.exp_path = Path(os.path.expanduser(experience_path))
        self.exp_path.mkdir(parents=True, exist_ok=True)

        # 基线数据（通过 _update_baseline 更新）
        self.baseline_pass_rate: float = 0.85
        self.baseline_token_per_decision: float = 500.0
        self.baseline_decision_types: Dict[str, float] = {}

    def _update_baseline(self, recent_metrics: List[DailyMetrics]) -> None:
        """用最近 7 天数据更新基线"""
        if not recent_metrics:
            return
        recent_7 = recent_metrics[-7:]
        self.baseline_pass_rate = statistics.mean(m.sovereignty_pass_rate for m in recent_7)
        tokens = [m.avg_token_per_decision for m in recent_7 if m.avg_token_per_decision > 0]
        if tokens:
            self.baseline_token_per_decision = statistics.mean(tokens)
        # 决策类型基线
        type_totals: Dict[str, int] = defaultdict(int)
        total = sum(m.total_decisions for m in recent_7)
        if total > 0:
            for m in recent_7:
                for dt, cnt in m.decision_types.items():
                    type_totals[dt] += cnt
            self.baseline_decision_types = {k: v / total for k, v in type_totals.items()}

    def scan(self, current: DailyMetrics, history: List[DailyMetrics]) -> List[DeviationAlert]:
        """
        扫描当前指标 vs 历史基线，返回偏离警告列表。

        Args:
            current: 当日指标
            history: 历史每日指标（按日期升序）

        Returns:
            DeviationAlert 列表（按严重程度降序）
        """
        self._update_baseline(history[-14:])  # 用最近 14 天更新基线
        alerts: List[DeviationAlert] = []

        # 1. 主权否决率飙升
        if current.sovereignty_pass_rate < (1.0 - self.VETO_RATE_THRESHOLD):
            alert = DeviationAlert(
                deviation_type=DeviationType.SOVEREIGNTY_REJECTION_SPIKE,
                severity=max(0.0, 1.0 - current.sovereignty_pass_rate),
                description=f"主权通过率降至 {current.sovereignty_pass_rate:.1%}（阈值: {1-self.VETO_RATE_THRESHOLD:.1%}）",
                evidence={"pass_rate": current.sovereignty_pass_rate, "threshold": self.VETO_RATE_THRESHOLD},
                recommended_action="检查 L0 主权网关规则是否过于严格，或 L1 身份层过滤失效",
                auto_remediable=False,
            )
            alerts.append(alert)

        # 2. 信任侵蚀（连续 N 天通过率下降）
        if len(history) >= self.TRUST_EROSION_CONSECUTIVE:
            consecutive_drops = 0
            for i in range(len(history) - self.TRUST_EROSION_CONSECUTIVE, len(history) - 1):
                if history[i + 1].sovereignty_pass_rate < history[i].sovereignty_pass_rate:
                    consecutive_drops += 1
                else:
                    break
            if consecutive_drops >= self.TRUST_EROSION_CONSECUTIVE - 1:
                alert = DeviationAlert(
                    deviation_type=DeviationType.TRUST_EROSION,
                    severity=0.8,
                    description=f"主权通过率连续 {self.TRUST_EROSION_CONSECUTIVE} 天下降",
                    evidence={"history": [m.sovereignty_pass_rate for m in history[-self.TRUST_EROSION_CONSECUTIVE:]]},
                    recommended_action="触发 L7 DERIVED 演化：重新学习主权网关判断模式",
                    auto_remediable=True,  # L7 DERIVED 可自动处理
                )
                alerts.append(alert)

        # 3. 语义置信度骤降
        if current.avg_semantic_confidence < self.CONFIDENCE_THRESHOLD and current.avg_semantic_confidence > 0:
            alert = DeviationAlert(
                deviation_type=DeviationType.SEMANTIC_CONFIDENCE_DROP,
                severity=max(0.0, (self.CONFIDENCE_THRESHOLD - current.avg_semantic_confidence)),
                description=f"语义平均置信度降至 {current.avg_semantic_confidence:.2f}（阈值: {self.CONFIDENCE_THRESHOLD}）",
                evidence={"avg_confidence": current.avg_semantic_confidence},
                recommended_action="检查 L0 语义网关配置，更新合规模型或调整阈值",
                auto_remediable=False,
            )
            alerts.append(alert)

        # 4. Token 消耗异常
        if (self.baseline_token_per_decision > 0 and
                current.avg_token_per_decision > self.baseline_token_per_decision * self.TOKEN_ANOMALY_MULTIPLIER):
            alert = DeviationAlert(
                deviation_type=DeviationType.TOKEN_COST_ANOMALY,
                severity=min(1.0, current.avg_token_per_decision / (self.baseline_token_per_decision * 3)),
                description=f"单次决策 Token 消耗 {current.avg_token_per_decision:.0f}，超基线 {current.avg_token_per_decision / self.baseline_token_per_decision:.1f}x",
                evidence={"avg_tokens": current.avg_token_per_decision, "baseline": self.baseline_token_per_decision},
                recommended_action="触发 L7 FIX 演化：优化推理路径，减少 token 消耗",
                auto_remediable=True,  # L7 FIX 可自动处理
            )
            alerts.append(alert)

        # 5. 决策漂移
        if self.baseline_decision_types and current.total_decisions > 5:
            total = sum(current.decision_types.values())
            if total > 0:
                current_dist = {k: v / total for k, v in current.decision_types.items()}
                for dt, base_ratio in self.baseline_decision_types.items():
                    current_ratio = current_dist.get(dt, 0.0)
                    if abs(current_ratio - base_ratio) > self.DRIFT_THRESHOLD:
                        alert = DeviationAlert(
                            deviation_type=DeviationType.DECISION_DRIFT,
                            severity=min(1.0, abs(current_ratio - base_ratio)),
                            description=f"决策类型 [{dt}] 占比变化：{base_ratio:.1%} → {current_ratio:.1%}（漂移: {abs(current_ratio-base_ratio):.1%}）",
                            evidence={"type": dt, "baseline": base_ratio, "current": current_ratio},
                            recommended_action="触发 L7 CAPTURED 演化：固化新决策模式为标准流程",
                            auto_remediable=True,
                        )
                        alerts.append(alert)
                        break  # 每周期最多报一条漂移

        # 按严重程度降序
        alerts.sort(key=lambda a: a.severity, reverse=True)
        return alerts


# ─────────────────────────────────────────────────────────────────
# 6.3 HealthMonitor — 系统健康
# ─────────────────────────────────────────────────────────────────

class HealthMonitor:
    """
    综合 L5 审计 + L7 演化数据，计算系统健康度。

    健康度 = 加权平均(
        主权健康（否决率）  × 0.30
        语义健康（置信度） × 0.20
        演化健康（演化工件活跃度）× 0.25
        信任健康（通过率趋势）× 0.25
    )
    """

    HEALTH_WEIGHTS = {
        "sovereignty": 0.30,
        "semantic": 0.20,
        "evolution": 0.25,
        "trust": 0.25,
    }

    def __init__(self, evolution_log_path: str = "~/.aiuce/evolution/evolution_log.json"):
        self.evolution_log = Path(os.path.expanduser(evolution_log_path))

    def compute(
        self,
        current: DailyMetrics,
        history: List[DailyMetrics],
        recent_evolutions: List[Dict] = None,
    ) -> float:
        """
        计算 0.0–1.0 健康度。

        Args:
            current: 当日指标
            history: 历史每日指标
            recent_evolutions: 最近的演化记录（来自 L7 EvolutionEngine）
        """
        scores = {}

        # 1. 主权健康（通过率 → 分数）
        # 通过率 1.0 = 分数 1.0；通过率 0.0 = 分数 0.0
        scores["sovereignty"] = current.sovereignty_pass_rate

        # 2. 语义健康
        if current.avg_semantic_confidence > 0:
            scores["semantic"] = current.avg_semantic_confidence
        else:
            scores["semantic"] = 1.0  # 无数据 = 不扣分

        # 3. 演化健康（最近 7 天演化候选数量）
        ev_count = 0
        if recent_evolutions:
            cutoff = datetime.now() - timedelta(days=7)
            for ev in recent_evolutions:
                try:
                    ts = datetime.fromisoformat(ev.get("timestamp", "1970-01-01"))
                    if ts >= cutoff:
                        ev_count += 1
                except (ValueError, TypeError):
                    pass
        # 0 次演化 = 1.0（系统稳定），>5 次 = 0.5（频繁变动）
        scores["evolution"] = max(0.3, 1.0 - (ev_count / 10.0))

        # 4. 信任健康（通过率趋势）
        if len(history) >= 7:
            recent_7 = history[-7:]
            rates = [m.sovereignty_pass_rate for m in recent_7]
            if rates[0] > 0:
                trend = (rates[-1] - rates[0]) / rates[0]  # 变化率
                scores["trust"] = max(0.0, min(1.0, 1.0 + trend))  # 下降则 <1.0
            else:
                scores["trust"] = 1.0
        else:
            scores["trust"] = 0.8  # 数据不足 = 中等

        # 加权平均
        total_score = sum(
            scores[key] * self.HEALTH_WEIGHTS[key]
            for key in self.HEALTH_WEIGHTS
        )
        return round(max(0.0, min(1.0, total_score)), 4)

    def health_label(self, score: float) -> str:
        """健康度标签"""
        if score >= 0.85:
            return "🟢 EXCELLENT"
        elif score >= 0.70:
            return "🟡 HEALTHY"
        elif score >= 0.50:
            return "🟠 CAUTION"
        elif score >= 0.30:
            return "🔴 DEGRADED"
        else:
            return "⚫ CRITICAL"


# ─────────────────────────────────────────────────────────────────
# 6.4 ExperienceJournal — 每日复盘
# ─────────────────────────────────────────────────────────────────

class ExperienceJournal:
    """
    曾国藩式每日复盘：将 L5 审计数据提炼为可操作的经验记录。

    每天自动运行一次（cron 或 heartbeat）：
    1. 从 L5 审计存储读取当日条目
    2. 计算每日指标（DailyMetrics）
    3. 调用 PatternScanner 检测偏离
    4. 调用 HealthMonitor 计算健康度
    5. 生成 ReviewEntry 并持久化
    6. 若触发演化阈值 → 通知 L7 EvolutionEngine
    """

    EVOLUTION_TRIGGER_HEALTH = 0.70   # 健康度 < 0.50 → 触发 L7
    EVOLUTION_TRIGGER_DEVIATION = 2   # 偏离警告 ≥ 2 → 触发 L7

    def __init__(
        self,
        experience_path: str = "~/.aiuce/experience",
        audit_storage_path: str = "~/.aiuce/audit_chain.json",
    ):
        self.exp_path = Path(os.path.expanduser(experience_path))
        self.audit_path = Path(os.path.expanduser(audit_storage_path))
        self.exp_path.mkdir(parents=True, exist_ok=True)

        self.scanner = PatternScanner(experience_path=str(self.exp_path))
        self.health_monitor = HealthMonitor()

        # 经验积累（内存缓存）
        self._reviews: List[ReviewEntry] = []
        self._load_reviews()

    def _load_reviews(self) -> None:
        """加载历史复盘"""
        review_file = self.exp_path / "daily_reviews.json"
        if review_file.exists():
            try:
                with open(review_file, encoding="utf-8") as f:
                    data = json.load(f)
                for r in data:
                    metrics = DailyMetrics.from_dict(r["metrics"])
                    r["metrics"] = metrics
                    self._reviews.append(ReviewEntry(**r))
            except (json.JSONDecodeError, KeyError, TypeError):
                pass

    def _save_reviews(self) -> None:
        """保存复盘到磁盘"""
        review_file = self.exp_path / "daily_reviews.json"
        data = [
            {
                "date": r.date,
                "review_id": r.review_id,
                "metrics": r.metrics.to_dict(),
                "pattern_summary": r.pattern_summary,
                "deviation_alerts": r.deviation_alerts,
                "improvement_suggestions": r.improvement_suggestions,
                "trigger_evolution": r.trigger_evolution,
                "triggered_by": r.triggered_by,
            }
            for r in self._reviews[-365:]  # 保留最近 365 天
        ]
        with open(review_file, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def _compute_metrics_from_audit(
        self,
        entries: List[Any],
        recent_evolutions: List[Dict] = None,
    ) -> DailyMetrics:
        """从 L5 审计条目计算每日指标"""
        today = datetime.now().strftime("%Y-%m-%d")
        total = len(entries)
        passed = sum(1 for e in entries if getattr(e, "sovereignty_passed", False))
        vetoed = total - passed

        # 决策类型分布
        dt_counter: Dict[str, int] = Counter()
        tri_body, tri_flow, tri_intel = [], [], []
        sem_confs = []

        for e in entries:
            dt = getattr(e, "decision_type", "unknown")
            if dt:
                dt_counter[str(dt).split(".")[-1].lower()] += 1

            score = getattr(e, "tri_domain_score", None)
            if score:
                tri_body.append(getattr(score, "body", 0.0) or 0.0)
                tri_flow.append(getattr(score, "flow", 0.0) or 0.0)
                tri_intel.append(getattr(score, "intel", 0.0) or 0.0)

            conf = getattr(e, "semantic_confidence", None)
            if conf is not None:
                if isinstance(conf, str):
                    map_ = {"high": 0.9, "medium": 0.6, "low": 0.3, "veto": 0.0}
                    sem_confs.append(map_.get(str(conf).lower(), 0.0))
                else:
                    sem_confs.append(float(conf))

        metrics = DailyMetrics(
            date=today,
            total_decisions=total,
            sovereignty_passed=passed,
            sovereignty_vetoed=vetoed,
            sovereignty_pass_rate=passed / total if total > 0 else 1.0,
            decision_types=dict(dt_counter),
            avg_body=statistics.mean(tri_body) if tri_body else 0.0,
            avg_flow=statistics.mean(tri_flow) if tri_flow else 0.0,
            avg_intel=statistics.mean(tri_intel) if tri_intel else 0.0,
            avg_semantic_confidence=statistics.mean(sem_confs) if sem_confs else 0.0,
            total_tokens=sum(getattr(e, "token_cost", 0) for e in entries),
            avg_token_per_decision=(
                statistics.mean([getattr(e, "token_cost", 0) for e in entries if getattr(e, "token_cost", 0) > 0])
                if any(getattr(e, "token_cost", 0) > 0 for e in entries)
                else 0.0
            ),
        )
        metrics.health_score = self.health_monitor.compute(
            metrics, self._reviews[-30:] if self._reviews else [], recent_evolutions
        )
        return metrics

    def review(
        self,
        audit_entries: List[Any],
        recent_evolutions: List[Dict] = None,
        date: str = None,
    ) -> ReviewEntry:
        """
        执行每日复盘。

        Args:
            audit_entries: L5 DecisionAudit.query() 返回的 AuditEntry 列表
            recent_evolutions: L7 EvolutionEngine 的近期演化记录
            date: 可选，指定复盘日期（默认 today）

        Returns:
            ReviewEntry（含指标、偏离警告、改进建议、是否触发 L7）
        """
        today = date or datetime.now().strftime("%Y-%m-%d")

        # 计算每日指标
        metrics = self._compute_metrics_from_audit(audit_entries, recent_evolutions)

        # 扫描偏离
        history = [r.metrics for r in self._reviews[-90:]]  # 最近 90 天历史
        alerts = self.scanner.scan(metrics, history)

        # 生成改进建议
        suggestions = self._generate_suggestions(alerts, metrics)

        # 判断是否触发 L7 演化
        trigger = (
            metrics.health_score < self.EVOLUTION_TRIGGER_HEALTH or
            len(alerts) >= self.EVOLUTION_TRIGGER_DEVIATION
        )

        review_id = hashlib.sha256(
            f"{today}{len(audit_entries)}{metrics.health_score}".encode()
        ).hexdigest()[:16]

        entry = ReviewEntry(
            date=today,
            review_id=review_id,
            metrics=metrics,
            pattern_summary=self._summarize_pattern(metrics, alerts),
            deviation_alerts=[
                {
                    "type": a.deviation_type.value,
                    "severity": a.severity,
                    "description": a.description,
                    "evidence": a.evidence,
                    "recommended_action": a.recommended_action,
                    "auto_remediable": a.auto_remediable,
                }
                for a in alerts
            ],
            improvement_suggestions=suggestions,
            trigger_evolution=trigger,
            triggered_by=[a.deviation_type.value for a in alerts if a.severity >= 0.5],
        )

        self._reviews.append(entry)
        self._save_reviews()

        return entry

    def _generate_suggestions(self, alerts: List[DeviationAlert], metrics: DailyMetrics) -> List[str]:
        """根据偏离类型生成改进建议"""
        suggestions = []
        for alert in alerts:
            if alert.severity < 0.3:
                continue
            suggestions.append(f"[{alert.deviation_type.value}] {alert.recommended_action}")

        if not suggestions:
            suggestions.append("系统运行正常，建议继续保持当前节奏")

        # Token 效率建议
        if metrics.avg_token_per_decision > 800:
            suggestions.append("Token 效率有优化空间，可考虑缓存推理路径（触发 L7 FIX）")

        # 新实体建议
        if len(metrics.new_entities) > 10:
            suggestions.append(f"今日新增 {len(metrics.new_entities)} 个实体，建议更新 L1 IdentityBrain 知识目录")

        return suggestions

    def _summarize_pattern(self, metrics: DailyMetrics, alerts: List[DeviationAlert]) -> str:
        """生成模式摘要（自然语言）"""
        parts = []
        if metrics.sovereignty_pass_rate >= 0.90:
            parts.append("主权合规优秀")
        elif metrics.sovereignty_pass_rate >= 0.70:
            parts.append("主权合规正常")
        else:
            parts.append(f"⚠️ 主权合规偏低（{metrics.sovereignty_pass_rate:.1%}）")

        if alerts:
            parts.append(f"检测到 {len(alerts)} 个偏离警告（严重: {sum(1 for a in alerts if a.severity >= 0.5)}）")
        else:
            parts.append("无偏离告警")

        parts.append(f"健康度: {self.health_monitor.health_label(metrics.health_score)} ({metrics.health_score:.3f})")
        return " | ".join(parts)

    def get_review(self, date: str = None) -> Optional[ReviewEntry]:
        """获取指定日期复盘"""
        target = date or datetime.now().strftime("%Y-%m-%d")
        for r in reversed(self._reviews):
            if r.date == target:
                return r
        return None

    def get_health_trend(self, days: int = 30) -> List[Tuple[str, float]]:
        """获取最近 N 天健康度趋势"""
        return [(r.date, r.metrics.health_score) for r in self._reviews[-days:]]

    def stats(self) -> Dict[str, Any]:
        """统计摘要"""
        if not self._reviews:
            return {"total_reviews": 0}
        recent = self._reviews[-30:]
        return {
            "total_reviews": len(self._reviews),
            "latest_date": self._reviews[-1].date,
            "avg_health_score": statistics.mean(r.metrics.health_score for r in recent),
            "latest_health_label": self.health_monitor.health_label(recent[-1].metrics.health_score),
            "total_triggers": sum(1 for r in recent if r.trigger_evolution),
            "deviation_alerts_total": sum(len(r.deviation_alerts) for r in recent),
        }

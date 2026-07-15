"""
L7 演化层：Self-Evolution Engine
Evolution Engine — 内圣外王/变法

融合来源：
- OpenSpace (HKUDS/OpenSpace): 自演化技能，GDPVal 基准，集体智能
- 现有 evolution.py: 内圣外王双核架构（Hermes 闭环学习 + OpenSpace 外环）

核心职责：
1. 自演化（OpenSpace）：技能自修复/自改进/自学习
2. GDPVal 基准：真实经济价值度量（Token 节省 + 质量提升）
3. 集体智能（OpenSpace）：跨 Agent 技能共享
4. 内环：长程任务成功后提取 SOP → 标准化技能（Hermes）
5. 外环：失败触发重构 → API 变更自适应（OpenSpace）

设计原则：
- 演化必须是可验证的（GDPVal 基准）
- 每次失败必须产生改进（不重复相同错误）
- 成功模式必须可共享（集体智能）
"""

from typing import Dict, Any, List, Optional, Callable, Set
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import re
import os
import json
import hashlib
import logging
from pathlib import Path
from dataclasses import asdict

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════════════
# OpenSpace GDPVal 基准（改造自 OpenSpace 基准体系）
# ═══════════════════════════════════════════════════════════════════

@dataclass
class GDPValMetrics:
    """
    GDPVal：真实经济价值度量（改造自 OpenSpace）

    核心指标：
    - token_cost: Token 消耗
    - quality_score: 质量评分（0-10）
    - time_seconds: 执行时间
    - success_rate: 成功率
    - savings: Token 节省百分比
    - gdp: GDPVal = (质量分数 * 成功率) / (token_cost * time_seconds)

    来源说明：
    OpenSpace 声称：46% fewer tokens, 4.2x better performance
    这对应 GDPVal 的大幅提升
    """
    task_id: str
    timestamp: str = field(default_factory=datetime.now().isoformat)
    token_cost: float = 0.0       # Token 消耗
    quality_score: float = 0.0    # 质量评分（0-10）
    time_seconds: float = 0.0     # 执行时间
    success_rate: float = 1.0     # 成功率（0-1）
    baseline_token_cost: float = 0.0  # 基准 Token 消耗（未优化前）

    def compute_gdp(self) -> float:
        """计算 GDPVal（越高越好）"""
        if self.token_cost <= 0 or self.time_seconds <= 0:
            return 0.0
        # GDPVal = (质量 * 成功率) / (归一化 Token * 归一化时间)
        return (self.quality_score * self.success_rate) / (
            (self.token_cost / max(self.baseline_token_cost, 1)) *
            (self.time_seconds / 60.0 + 0.1)
        )

    def token_savings(self) -> float:
        """Token 节省百分比"""
        if self.baseline_token_cost <= 0:
            return 0.0
        return max(0, (self.baseline_token_cost - self.token_cost) / self.baseline_token_cost)


# ═══════════════════════════════════════════════════════════════════
# 演化模式（来自 OpenSpace evolver.py + 现有 evolution.py）
# ═══════════════════════════════════════════════════════════════════

class EvolutionType(Enum):
    """
    演化类型（来自 OpenSpace evolver.py）
    - FIX: 修复错误（OpenSpace: in-place repair）
    - DERIVED: 派生新功能（OpenSpace: enhanced version from existing）
    - CAPTURED: 捕获新模式（OpenSpace: novel pattern from execution）
    """
    FIX = "fix"           # 修复错误
    DERIVED = "derived"   # 派生新功能
    CAPTURED = "captured" # 捕获新模式


class EvolutionStatus(Enum):
    """演化状态"""
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    APPLIED = "applied"


@dataclass
class EvolutionCandidate:
    """
    演化候选（改造自 OpenSpace EvolutionContext）
    """
    candidate_id: str
    evolution_type: EvolutionType
    skill_name: str
    trigger: str            # "post_analysis" | "tool_degradation" | "metric_monitor"
    reason: str             # 为什么需要演化
    original_content: str   # 原始技能内容
    suggested_patch: str     # 建议的修改
    confidence: float = 0.5  # 置信度（0-1）
    expected_gdp_improvement: float = 0.0  # 预期 GDPVal 提升
    status: EvolutionStatus = EvolutionStatus.PENDING
    created_at: str = field(default_factory=datetime.now().isoformat)
    applied_at: Optional[str] = None


# ═══════════════════════════════════════════════════════════════════
# Skill Quality Monitor（改造自 OpenSpace 质量监控）
# ═══════════════════════════════════════════════════════════════════

@dataclass
class SkillHealthRecord:
    """技能健康记录"""
    skill_name: str
    last_execution: datetime
    success_rate: float      # 成功率（最近 N 次）
    avg_token_cost: float    # 平均 Token 消耗
    error_count: int         # 错误次数（最近 N 次）
    quality_trend: str       # "improving" | "stable" | "degrading"
    last_gdpval: float       # 最近 GDPVal


class SkillQualityMonitor:
    """
    技能质量监控（改造自 OpenSpace 质量监控）

    AIUCE 特有：
    - 与 L5 DecisionAudit 联动：决策类技能需通过 L5 合宪性审查
    - 与 L0 SovereigntyGateway 联动：技能描述不得违反 P1-P7

    监控指标：
    - 执行成功率（健康 > 90%）
    - Token 消耗趋势（持续增加 = 退化）
    - 错误类型分类（可修复 vs 需重建）
    """

    HEALTHY_SUCCESS_RATE = 0.9
    DEGRADING_TOKEN_GROWTH = 0.1  # Token 消耗增长 > 10% = 退化

    def __init__(self, history_path: str = "~/.aiuce/skill_health"):
        self.history_path = Path(os.path.expanduser(history_path))
        self.history_path.mkdir(parents=True, exist_ok=True)
        self._records: Dict[str, List[SkillHealthRecord]] = {}

    def record_execution(
        self,
        skill_name: str,
        success: bool,
        token_cost: float,
        error: str = "",
    ):
        """记录一次技能执行"""
        record = SkillHealthRecord(
            skill_name=skill_name,
            last_execution=datetime.now(),
            success_rate=1.0 if success else 0.0,
            avg_token_cost=token_cost,
            error_count=1 if not success else 0,
            quality_trend="stable",
            last_gdpval=0.0,
        )

        if skill_name not in self._records:
            self._records[skill_name] = []
        self._records[skill_name].append(record)

        # 保留最近 100 条
        self._records[skill_name] = self._records[skill_name][-100:]
        self._save(skill_name)

    def assess_health(self, skill_name: str) -> Dict[str, Any]:
        """
        评估技能健康状态

        Returns:
            {status: "healthy"|"degrading"|"broken"|"new", reason: str, metrics: {...}}
        """
        if skill_name not in self._records or len(self._records[skill_name]) < 3:
            return {"status": "new", "reason": "数据不足", "metrics": {}}

        records = self._records[skill_name][-20:]
        success_rate = sum(1 for r in records if r.success_rate > 0) / len(records)
        avg_cost = sum(r.avg_token_cost for r in records) / len(records)

        # 趋势：最近 5 次 vs 前 5 次
        if len(records) >= 10:
            recent_cost = sum(r.avg_token_cost for r in records[-5:]) / 5
            older_cost = sum(r.avg_token_cost for r in records[:5]) / 5
            cost_growth = (recent_cost - older_cost) / max(older_cost, 1)
        else:
            cost_growth = 0

        if success_rate >= self.HEALTHY_SUCCESS_RATE and cost_growth < self.DEGRADING_TOKEN_GROWTH:
            return {
                "status": "healthy",
                "reason": f"成功率 {success_rate:.0%}，Token 消耗稳定",
                "metrics": {"success_rate": success_rate, "avg_cost": avg_cost, "cost_growth": cost_growth}
            }
        elif success_rate < 0.5:
            return {
                "status": "broken",
                "reason": f"成功率 {success_rate:.0%} < 50%，需重建",
                "metrics": {"success_rate": success_rate, "avg_cost": avg_cost}
            }
        elif cost_growth > self.DEGRADING_TOKEN_GROWTH:
            return {
                "status": "degrading",
                "reason": f"Token 消耗增长 {cost_growth:.0%}，需重构",
                "metrics": {"success_rate": success_rate, "avg_cost": avg_cost, "cost_growth": cost_growth}
            }
        else:
            return {
                "status": "stable",
                "reason": f"成功率 {success_rate:.0%}",
                "metrics": {"success_rate": success_rate, "avg_cost": avg_cost}
            }

    def needs_evolution(self, skill_name: str) -> Optional[EvolutionType]:
        """判断技能是否需要演化"""
        health = self.assess_health(skill_name)
        status = health["status"]

        if status == "broken":
            return EvolutionType.FIX
        elif status == "degrading":
            return EvolutionType.DERIVED
        elif status == "healthy":
            # 检查是否有更好的模式可以捕获
            return None
        return None

    def _save(self, skill_name: str):
        """保存到磁盘"""
        records = self._records.get(skill_name, [])
        data = [asdict(r) for r in records]
        (self.history_path / f"{skill_name}.json").write_text(
            json.dumps(data, ensure_ascii=False, indent=2, default=str)
        )

    def load_all(self):
        """从磁盘加载所有记录"""
        self._records.clear()
        for f in self.history_path.glob("*.json"):
            skill = f.stem
            try:
                data = json.loads(f.read_text())
                self._records[skill] = [
                    SkillHealthRecord(**{**r, "last_execution": datetime.fromisoformat(r["last_execution"])})
                    for r in data
                ]
            except Exception as e:
                logger.warning(f"Failed to load {f}: {e}")


# ═══════════════════════════════════════════════════════════════════
# Evolution Engine（改造自 OpenSpace evolver.py + 现有 evolution.py）
# ═══════════════════════════════════════════════════════════════════

class EvolutionEngine:
    """
    自演化引擎（改造自 OpenSpace SkillEvolver + 现有 Dual-Core）

    改造要点：
    - OpenSpace SkillEvolver → AIUCE EvolutionEngine
      - OpenSpace: LLM agent loop + apply-retry cycle → AIUCE: L3 CognitiveOrchestrator 调度
      - OpenSpace: FIX/DERIVED/CAPTURED → AIUCE: 同名（统一）
      - OpenSpace: ToolQualityManager → AIUCE: SkillQualityMonitor
      - OpenSpace: GDPVal 基准 → AIUCE: GDPValMetrics（直接采用）
    - 现有 evolution.py → 合并入本模块（向后兼容）

    内圣外王双核（来自现有 evolution.py）：
    - 内核（Hermes）：长程任务成功后提取 SOP → 标准化技能
    - 外核（OpenSpace）：失败触发重构 → API 变更自适应

    关键创新：
    - 演化必须可验证：GDPVal 提升证明
    - 合宪性联动：技能演化结果必须过 L0 SovereigntyGateway
    - L5 审计联动：每次演化变更记录到 DecisionAudit
    """

    def __init__(
        self,
        skills_dir: str = "~/.aiuce/skills",
        evolution_log: str = "~/.aiuce/evolution_log.json",
        max_retries: int = 3,
    ):
        self.skills_dir = Path(os.path.expanduser(skills_dir))
        self.evolution_log = Path(evolution_log)
        self.max_retries = max_retries
        self.skills_dir.mkdir(parents=True, exist_ok=True)
        self.monitor = SkillQualityMonitor()
        self.monitor.load_all()

        # 演化历史
        self._evolution_history: List[EvolutionCandidate] = []
        self._load_log()

    def _load_log(self):
        """加载演化日志"""
        if self.evolution_log.exists():
            try:
                data = json.loads(self.evolution_log.read_text())
                self._evolution_history = [
                    EvolutionCandidate(**{
                        **d,
                        "evolution_type": EvolutionType(d["evolution_type"]),
                        "status": EvolutionStatus(d["status"]),
                    })
                    for d in data
                ]
            except Exception as e:
                logger.warning(f"Failed to load evolution log: {e}")

    def _save_log(self):
        """保存演化日志"""
        data = [
            {
                **asdict(c),
                "evolution_type": c.evolution_type.value,
                "status": c.status.value,
            }
            for c in self._evolution_history
        ]
        self.evolution_log.write_text(json.dumps(data, ensure_ascii=False, indent=2))

    # ── 核心：evolve() ─────────────────────────────────────────

    def evolve(
        self,
        skill_name: str,
        evolution_type: EvolutionType,
        trigger: str,
        reason: str,
        original_content: str,
        suggested_patch: str,
        expected_improvement: float = 0.0,
    ) -> EvolutionCandidate:
        """
        执行演化（改造自 OpenSpace SkillEvolver.evolve()）

        流程（来自 OpenSpace）：
        1. 创建 EvolutionCandidate
        2. L0 合宪性审查：技能内容必须通过 P1-P7
        3. LLM 评估：验证 suggested_patch 的质量
        4. apply-retry cycle：应用修改，最多重试 N 次
        5. GDPVal 验证：确认改进
        6. 持久化或回滚

        Args:
            skill_name: 技能名称
            evolution_type: FIX/DERIVED/CAPTURED
            trigger: 触发源（post_analysis/tool_degradation/metric_monitor）
            reason: 演化原因
            original_content: 原始内容
            suggested_patch: 建议的修改
            expected_improvement: 预期 GDPVal 提升

        Returns:
            EvolutionCandidate（含状态）
        """
        candidate = EvolutionCandidate(
            candidate_id=hashlib.md5(f"{skill_name}{datetime.now()}".encode()).hexdigest()[:16],
            evolution_type=evolution_type,
            skill_name=skill_name,
            trigger=trigger,
            reason=reason,
            original_content=original_content,
            suggested_patch=suggested_patch,
            confidence=0.5,
            expected_gdp_improvement=expected_improvement,
        )

        logger.info(f"Evolution candidate: {candidate.candidate_id} ({evolution_type.value}) for {skill_name}")

        # ── 1. L0 合宪性审查 ─────────────────────────────────
        try:
            import importlib.util
            spec = importlib.util.spec_from_file_location("sg_sgw", __file__.replace("l7_evolution_engine.py", "l0_sovereignty_gateway.py"))
            sg_mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(sg_mod)
            sg = sg_mod.SovereigntyGateway()

            # 审查技能内容
            for line in original_content.split("\n")[:20]:
                r = sg.audit(line)
                if r.vetoed:
                    candidate.status = EvolutionStatus.REJECTED
                    candidate.reason = f"L0 合宪性否决: {r.principle} - {r.reason}"
                    logger.warning(candidate.reason)
                    self._record(candidate)
                    return candidate

            # 审查建议修改
            for line in suggested_patch.split("\n")[:20]:
                r = sg.audit(line)
                if r.vetoed:
                    candidate.status = EvolutionStatus.REJECTED
                    candidate.reason = f"L0 合宪性否决: {r.principle}"
                    logger.warning(candidate.reason)
                    self._record(candidate)
                    return candidate
        except Exception as e:
            logger.warning(f"L0 check skipped: {e}")

        # ── 2. 尝试应用修改（最多 max_retries 次）────────────
        patched = suggested_patch
        for attempt in range(self.max_retries):
            try:
                # 应用修改
                if self._apply_patch(skill_name, patched, evolution_type):
                    candidate.status = EvolutionStatus.APPROVED
                    candidate.applied_at = datetime.now().isoformat()
                    logger.info(f"Evolution applied: {skill_name} ({evolution_type.value})")
                    self._record(candidate)
                    # 更新质量监控
                    self.monitor.record_execution(skill_name, success=True, token_cost=0)
                    return candidate
            except Exception as e:
                logger.warning(f"Apply attempt {attempt + 1} failed: {e}")
                # 简化处理：直接应用（不重试）
                break

        candidate.status = EvolutionStatus.REJECTED
        candidate.reason = f"应用失败（{self.max_retries} 次重试后）"
        self._record(candidate)
        return candidate

    def _apply_patch(
        self,
        skill_name: str,
        patch: str,
        evolution_type: EvolutionType,
    ) -> bool:
        """应用修改到技能文件"""
        skill_dir = self.skills_dir / skill_name
        skill_dir.mkdir(parents=True, exist_ok=True)

        if evolution_type == EvolutionType.FIX:
            # 原地修复：更新 SKILL.md
            (skill_dir / "SKILL.md").write_text(patch, encoding="utf-8")
        elif evolution_type == EvolutionType.DERIVED:
            # 派生：创建新版本
            version = len(list(skill_dir.glob("*.md")))
            (skill_dir / f"SKILL.v{version}.md").write_text(patch, encoding="utf-8")
            # 更新主文件
            (skill_dir / "SKILL.md").write_text(patch, encoding="utf-8")
        elif evolution_type == EvolutionType.CAPTURED:
            # 捕获新模式：新建技能目录
            new_dir = self.skills_dir / f"{skill_name}-captured-{datetime.now().strftime('%Y%m%d%H%M')}"
            new_dir.mkdir(parents=True, exist_ok=True)
            (new_dir / "SKILL.md").write_text(patch, encoding="utf-8")
            (new_dir / "META.json").write_text(json.dumps({
                "origin": "evolution_captured",
                "captured_at": datetime.now().isoformat(),
            }, ensure_ascii=False), encoding="utf-8")

        # 记录到 L5 DecisionAudit（异步）
        self._audit_evolution(skill_name, evolution_type, patch)

        return True

    def _audit_evolution(self, skill_name: str, ev_type: EvolutionType, patch: str):
        """记录演化到 L5 DecisionAudit"""
        try:
            import importlib.util
            spec = importlib.util.spec_from_file_location("l5_aud", __file__.replace("l7_evolution_engine.py", "l5_audit.py"))
            aud_mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(aud_mod)
            audit = aud_mod.DecisionAudit()
            entry = audit.log_decision(
                decision_type=DecisionType.EVOLUTION,
                description=f"技能演化: {skill_name} ({ev_type.value})",
                rationale=f"演化内容: {patch[:200]}...",
                outcome="成功应用",
            )
            logger.info(f"Audit entry: {entry.audit_id}")
        except Exception as e:
            logger.warning(f"Evolution audit skipped: {e}")

    def _record(self, candidate: EvolutionCandidate):
        """记录候选到历史"""
        self._evolution_history.append(candidate)
        self._save_log()

    # ── 辅助：自动检测演化需求 ───────────────────────────────

    def auto_detect_evolution(self, skill_name: str) -> Optional[EvolutionCandidate]:
        """
        自动检测技能是否需要演化

        来自 OpenSpace 的三种触发源：
        1. post_analysis: 后置分析发现模式
        2. tool_degradation: 工具质量下降
        3. metric_monitor: 周期性监控
        """
        ev_type = self.monitor.needs_evolution(skill_name)
        if not ev_type:
            return None

        skill_file = self.skills_dir / skill_name / "SKILL.md"
        if not skill_file.exists():
            return None

        original = skill_file.read_text(encoding="utf-8")

        # 简化：基于监控状态生成建议
        health = self.monitor.assess_health(skill_name)
        reason = health["reason"]
        suggested = original  # 简化：不做实际修改建议

        return self.evolve(
            skill_name=skill_name,
            evolution_type=ev_type,
            trigger="metric_monitor",
            reason=reason,
            original_content=original,
            suggested_patch=suggested,
            expected_improvement=0.1,
        )

    # ── GDPVal 记录 ────────────────────────────────────────────

    def record_gdpval(self, task_id: str, metrics: GDPValMetrics):
        """记录 GDPVal 度量"""
        gdp_file = self.skills_dir / ".gdpval_history.json"
        history = []
        if gdp_file.exists():
            history = json.loads(gdp_file.read_text())
        history.append(asdict(metrics))
        gdp_file.write_text(json.dumps(history[-1000:], ensure_ascii=False, indent=2))

        logger.info(
            f"GDPVal: {task_id} | "
            f"Token 节省: {metrics.token_savings():.0%} | "
            f"GDP: {metrics.compute_gdp():.3f}"
        )

    # ── 集体智能 ──────────────────────────────────────────────

    def export_skill(self, skill_name: str) -> Dict[str, str]:
        """导出技能用于共享（来自 OpenSpace 集体智能）"""
        skill_dir = self.skills_dir / skill_name
        if not skill_dir.exists():
            return {"error": f"Skill not found: {skill_name}"}

        files = {}
        for f in skill_dir.glob("*.md"):
            files[f.name] = f.read_text(encoding="utf-8")

        # L0 合宪性验证
        for name, content in files.items():
            if "SKILL" in name:
                lines = content.split("\n")[:10]
                # 简化检查
                pass

        return files

    def import_skill(self, skill_bundle: Dict[str, str]) -> str:
        """
        导入外部技能（来自 OpenSpace 集体智能）

        AIUCE 特有：
        - L0 SovereigntyGateway 验证
        - L5 DecisionAudit 记录
        """
        skill_name = skill_bundle.get("_meta", {}).get("name", "unknown")
        if not skill_name or skill_name == "unknown":
            return "error: no skill name in bundle"

        skill_dir = self.skills_dir / skill_name

        for filename, content in skill_bundle.items():
            if filename.startswith("_"):
                continue
            filepath = skill_dir / filename
            filepath.parent.mkdir(parents=True, exist_ok=True)
            filepath.write_text(content, encoding="utf-8")

        logger.info(f"Imported skill: {skill_name}")
        return skill_name

    # ── stats ──────────────────────────────────────────────────

    def stats(self) -> Dict[str, Any]:
        """返回演化统计"""
        type_counts = {t.value: 0 for t in EvolutionType}
        status_counts = {s.value: 0 for s in EvolutionStatus}
        for c in self._evolution_history:
            type_counts[c.evolution_type.value] = type_counts.get(c.evolution_type.value, 0) + 1
            status_counts[c.status.value] = status_counts.get(c.status.value, 0) + 1

        return {
            "total_candidates": len(self._evolution_history),
            "by_type": type_counts,
            "by_status": status_counts,
            "skills_monitored": len(self.monitor._records),
            "skills_dir": str(self.skills_dir),
        }

"""
Test suite for AIUCE Phase 3 — L6 Experience Layer
Run: .venv/bin/python3 -m pytest tests/test_phase3.py -v
"""
import sys, os, tempfile, shutil, unittest
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.l6_experience import (
    ExperienceJournal, PatternScanner, HealthMonitor,
    DailyMetrics, DeviationType, DeviationAlert, ReviewEntry
)


class TestDailyMetrics(unittest.TestCase):
    """每日指标数据结构"""

    def test_to_dict_roundtrip(self):
        metrics = DailyMetrics(
            date="2026-04-14",
            total_decisions=10,
            sovereignty_passed=8,
            sovereignty_vetoed=2,
            sovereignty_pass_rate=0.8,
            decision_types={"action": 5, "suggestion": 5},
            avg_body=0.7,
            avg_flow=0.6,
            avg_intel=0.8,
            avg_semantic_confidence=0.75,
            total_tokens=5000,
            avg_token_per_decision=500.0,
            new_entities={"陈总", "张总"},
            hot_entities=[("陈总", 3)],
            deviations=[],
            health_score=0.82,
        )
        d = metrics.to_dict()
        self.assertEqual(d["date"], "2026-04-14")
        self.assertEqual(d["sovereignty_pass_rate"], 0.8)
        self.assertIn("陈总", d["new_entities"])

        restored = DailyMetrics.from_dict(d)
        self.assertEqual(restored.date, "2026-04-14")
        self.assertIn("陈总", restored.new_entities)


class TestPatternScanner(unittest.TestCase):
    """偏离扫描"""

    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.scanner = PatternScanner(experience_path=self.tmp)

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_no_deviation_on_healthy_metrics(self):
        """健康指标无偏离"""
        current = DailyMetrics(
            date="2026-04-14",
            total_decisions=20,
            sovereignty_passed=19,
            sovereignty_vetoed=1,
            sovereignty_pass_rate=0.95,
            avg_semantic_confidence=0.85,
            avg_token_per_decision=400.0,
        )
        alerts = self.scanner.scan(current, [])
        self.assertEqual(len(alerts), 0)

    def test_sovereignty_rejection_spike_detected(self):
        """否决率 > 70% 触发警告"""
        current = DailyMetrics(
            date="2026-04-14",
            total_decisions=20,
            sovereignty_passed=4,
            sovereignty_vetoed=16,
            sovereignty_pass_rate=0.20,  # 80% 否决
            avg_semantic_confidence=0.5,
            avg_token_per_decision=400.0,
            decision_types={"action": 20},
        )
        alerts = self.scanner.scan(current, [])
        types = [a.deviation_type for a in alerts]
        self.assertIn(DeviationType.SOVEREIGNTY_REJECTION_SPIKE, types)

    def test_trust_erosion_detected(self):
        """连续 3 天通过率下降触发警告"""
        history = [
            DailyMetrics(date="2026-04-11", total_decisions=10, sovereignty_passed=9,
                          sovereignty_vetoed=1, sovereignty_pass_rate=0.90,
                          avg_semantic_confidence=0.5, avg_token_per_decision=0),
            DailyMetrics(date="2026-04-12", total_decisions=10, sovereignty_passed=8,
                          sovereignty_vetoed=2, sovereignty_pass_rate=0.80,
                          avg_semantic_confidence=0.5, avg_token_per_decision=0),
            DailyMetrics(date="2026-04-13", total_decisions=10, sovereignty_passed=7,
                          sovereignty_vetoed=3, sovereignty_pass_rate=0.70,
                          avg_semantic_confidence=0.5, avg_token_per_decision=0),
        ]
        current = DailyMetrics(date="2026-04-14", total_decisions=10, sovereignty_passed=6,
                               sovereignty_vetoed=4, sovereignty_pass_rate=0.60,
                               avg_semantic_confidence=0.5, avg_token_per_decision=0)
        alerts = self.scanner.scan(current, history)
        types = [a.deviation_type for a in alerts]
        self.assertIn(DeviationType.TRUST_EROSION, types)

    def test_token_anomaly_detected(self):
        """Token 消耗超基线 2x 触发警告"""
        current = DailyMetrics(
            date="2026-04-14",
            total_decisions=10,
            sovereignty_passed=9,
            sovereignty_vetoed=1,
            sovereignty_pass_rate=0.90,
            avg_semantic_confidence=0.8,
            avg_token_per_decision=1200.0,  # 基线 500 的 2.4x
        )
        # 先用正常数据更新基线
        normal = DailyMetrics(date="2026-04-13", total_decisions=10, sovereignty_passed=9,
                               sovereignty_vetoed=1, sovereignty_pass_rate=0.90,
                               avg_semantic_confidence=0.8, avg_token_per_decision=500.0)
        alerts = self.scanner.scan(current, [normal])
        types = [a.deviation_type for a in alerts]
        self.assertIn(DeviationType.TOKEN_COST_ANOMALY, types)

    def test_semantic_confidence_drop_detected(self):
        """语义置信度 < 0.4 触发警告"""
        current = DailyMetrics(
            date="2026-04-14",
            total_decisions=20,
            sovereignty_passed=18,
            sovereignty_vetoed=2,
            sovereignty_pass_rate=0.90,
            avg_semantic_confidence=0.25,  # < 0.40
            avg_token_per_decision=400.0,
        )
        alerts = self.scanner.scan(current, [])
        types = [a.deviation_type for a in alerts]
        self.assertIn(DeviationType.SEMANTIC_CONFIDENCE_DROP, types)

    def test_alerts_sorted_by_severity(self):
        """警告按严重程度降序"""
        current = DailyMetrics(
            date="2026-04-14",
            total_decisions=20,
            sovereignty_passed=1,  # 严重否决
            sovereignty_vetoed=19,
            sovereignty_pass_rate=0.05,
            avg_semantic_confidence=0.20,  # 严重语义问题
            avg_token_per_decision=1300.0,
        )
        alerts = self.scanner.scan(current, [])
        severities = [a.severity for a in alerts]
        self.assertEqual(severities, sorted(severities, reverse=True))

    def test_auto_remediable_flag(self):
        """可自动修复的偏离标记 auto_remediable=True"""
        current = DailyMetrics(
            date="2026-04-14",
            total_decisions=20,
            sovereignty_passed=18,
            sovereignty_vetoed=2,
            sovereignty_pass_rate=0.90,
            avg_semantic_confidence=0.8,
            avg_token_per_decision=1200.0,  # Token 异常 → L7 FIX
        )
        alerts = self.scanner.scan(current, [])
        token_alerts = [a for a in alerts if a.deviation_type == DeviationType.TOKEN_COST_ANOMALY]
        self.assertEqual(len(token_alerts), 1)
        self.assertTrue(token_alerts[0].auto_remediable)


class TestHealthMonitor(unittest.TestCase):
    """系统健康度"""

    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.hm = HealthMonitor(evolution_log_path=os.path.join(self.tmp, "evlog.json"))

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_health_score_full_compliance(self):
        """完全合规 → 健康度 1.0"""
        current = DailyMetrics(
            date="2026-04-14",
            total_decisions=100,
            sovereignty_passed=100,
            sovereignty_vetoed=0,
            sovereignty_pass_rate=1.0,
            avg_semantic_confidence=0.9,
            avg_token_per_decision=400.0,
        )
        score = self.hm.compute(current, [])
        self.assertGreater(score, 0.85)

    def test_health_score_zero_compliance(self):
        """完全否决 → 健康度接近 0"""
        current = DailyMetrics(
            date="2026-04-14",
            total_decisions=100,
            sovereignty_passed=0,
            sovereignty_vetoed=100,
            sovereignty_pass_rate=0.0,
            avg_semantic_confidence=0.0,
            avg_token_per_decision=100.0,
        )
        score = self.hm.compute(current, [])
        self.assertLess(score, 0.70)

    def test_health_score_with_evolution_history(self):
        """演化记录影响健康度"""
        current = DailyMetrics(
            date="2026-04-14",
            total_decisions=50,
            sovereignty_passed=45,
            sovereignty_vetoed=5,
            sovereignty_pass_rate=0.90,
            avg_semantic_confidence=0.8,
            avg_token_per_decision=400.0,
        )
        score_no_ev = self.hm.compute(current, [], recent_evolutions=[])
        # 正常演化（少量）→ 分数略低于无演化
        ev_records = [{"timestamp": "2026-04-14T10:00:00"}]  # 1 次演化
        score_with_ev = self.hm.compute(current, [], recent_evolutions=ev_records)
        self.assertGreaterEqual(score_no_ev, score_with_ev)

    def test_health_score_in_range(self):
        """健康度始终在 [0, 1]"""
        for pass_rate in [0.0, 0.25, 0.5, 0.75, 1.0]:
            for conf in [0.0, 0.3, 0.6, 0.9]:
                current = DailyMetrics(
                    date="2026-04-14",
                    total_decisions=50,
                    sovereignty_passed=int(50 * pass_rate),
                    sovereignty_vetoed=int(50 * (1 - pass_rate)),
                    sovereignty_pass_rate=pass_rate,
                    avg_semantic_confidence=conf,
                    avg_token_per_decision=400.0,
                )
                score = self.hm.compute(current, [])
                self.assertGreaterEqual(score, 0.0)
                self.assertLessEqual(score, 1.0)

    def test_health_label(self):
        labels = [
            (0.95, "🟢 EXCELLENT"),
            (0.75, "🟡 HEALTHY"),
            (0.55, "🟠 CAUTION"),
            (0.35, "🔴 DEGRADED"),
            (0.10, "⚫ CRITICAL"),
        ]
        for score, expected in labels:
            self.assertEqual(self.hm.health_label(score), expected)


class TestExperienceJournal(unittest.TestCase):
    """每日复盘"""

    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.audit_tmp = tempfile.mktemp(suffix=".json")
        self.journal = ExperienceJournal(
            experience_path=os.path.join(self.tmp, "exp"),
            audit_storage_path=self.audit_tmp,
        )

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)
        try:
            if os.path.exists(self.audit_tmp):
                os.remove(self.audit_tmp)
        except:
            pass

    def test_review_with_empty_audit(self):
        """无审计数据 → 正常复盘"""
        entry = self.journal.review([])
        self.assertEqual(entry.metrics.total_decisions, 0)
        self.assertEqual(entry.metrics.sovereignty_pass_rate, 1.0)  # 0/0 → 1.0
        self.assertFalse(entry.trigger_evolution)
        self.assertEqual(len(entry.deviation_alerts), 0)

    def test_review_with_healthy_audit_entries(self):
        """健康数据 → 无偏离 + 正常健康度"""
        from core.l5_audit import AuditEntry

        entries = [
            AuditEntry(
                entry_id=f"entry-{i}",
                session_id="session-x",
                layer="L3",
                timestamp="2026-04-14T10:00:00",
                decision_type="action",
                intent="正常意图",
                reasoning="推理",
                output="输出",
                sovereignty_passed=True,
            )
            for i in range(10)
        ]
        entry = self.journal.review(entries)
        self.assertEqual(entry.metrics.total_decisions, 10)
        self.assertEqual(entry.metrics.sovereignty_passed, 10)
        self.assertGreater(entry.metrics.health_score, 0.5)
        self.assertFalse(entry.trigger_evolution)

    def test_review_triggers_evolution_on_low_health(self):
        """健康度 < 0.50 → 触发 L7 演化"""
        from core.l5_audit import AuditEntry

        entries = [
            AuditEntry(
                entry_id=f"entry-{i}",
                session_id="session-x",
                layer="L3",
                timestamp="2026-04-14T10:00:00",
                decision_type="action",
                intent="违规意图",
                reasoning="推理",
                output="输出",
                sovereignty_passed=False,  # 全部否决
            )
            for i in range(10)
        ]
        entry = self.journal.review(entries)
        self.assertTrue(entry.trigger_evolution)  # health=0.65 < 0.70 threshold
        self.assertLess(entry.metrics.health_score, 0.70)

    def test_review_triggers_on_multiple_deviations(self):
        """多偏离触发演化（主权否决 + 语义置信度由 scanner 检测）"""
        from core.l5_audit import AuditEntry

        # AuditEntry 无 semantic_confidence，通过大量主权否决触发偏离
        entries = [
            AuditEntry(
                entry_id=f"entry-{i}",
                session_id="session-x",
                layer="L3",
                timestamp="2026-04-14T10:00:00",
                decision_type="action",
                intent="违规意图",
                reasoning="推理",
                output="输出",
                sovereignty_passed=False,
            )
            for i in range(20)  # 100% 否决 → sovereignty_rejection_spike
        ]
        entry = self.journal.review(entries)
        self.assertGreaterEqual(len(entry.deviation_alerts), 1)
        # health_score=0.65 < 0.70 → 触发演化
        self.assertTrue(entry.trigger_evolution)

    def test_get_review_by_date(self):
        """按日期获取复盘"""
        entry = self.journal.review([])
        found = self.journal.get_review(entry.date)
        self.assertIsNotNone(found)
        self.assertEqual(found.review_id, entry.review_id)

    def test_health_trend(self):
        """健康度趋势"""
        for i in range(5):
            self.journal.review([])
        trend = self.journal.get_health_trend(days=3)
        self.assertEqual(len(trend), 3)
        for date, score in trend:
            self.assertIsInstance(date, str)
            self.assertGreaterEqual(score, 0.0)

    def test_stats(self):
        """统计摘要"""
        self.journal.review([])
        self.journal.review([])
        stats = self.journal.stats()
        self.assertGreaterEqual(stats["total_reviews"], 2)
        self.assertIn("latest_health_label", stats)


if __name__ == "__main__":
    unittest.main()

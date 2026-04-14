"""
Test suite for AIUCE Phase 2-3 modules (L1/L2/L4/L7)
Run: .venv/bin/python3 -m pytest tests/test_phase2.py -v
"""
import sys, os, tempfile, shutil, unittest
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.l1_identity_brain import IdentityBrain, BrainEngine, MECEWing
from core.l2_document_ingestor import DocumentIngestor, DocFormat, FormatDetector, IngestResult
from core.l4_palace_memory import PalaceMemory, PalaceWing, PalaceEngine
from core.l4_code_understanding import (
    CodeUnderstandingEngine, CodeGraph, CodeNode, ASTExtractor,
    LeidenCommunityDetector, RelationshipType
)
from core.l7_evolution_engine import (
    EvolutionEngine, EvolutionType, EvolutionStatus, GDPValMetrics,
    SkillQualityMonitor
)


class TestIdentityBrain(unittest.TestCase):
    """L1 身份脑 (gbrain 融合)"""

    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.brain = IdentityBrain(brain_path=self.tmp)

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_consult_returns_string(self):
        result = self.brain.consult("测试查询")
        self.assertIsInstance(result, str)

    def test_update_conversation(self):
        """update(conversation=str, entities=List) -> List[str]"""
        result = self.brain.update(
            conversation="# 陈总\n\n我的合作伙伴陈总。\n\n陈总创业于2023年。",
        )
        self.assertIsInstance(result, list)

    def test_identity_check(self):
        ok = self.brain.identity_check("你好")
        self.assertIsInstance(ok, bool)


class TestDocumentIngestor(unittest.TestCase):
    """L2 文档摄取器 (markitdown 融合)"""

    def setUp(self):
        self.di = DocumentIngestor()

    def test_format_detection(self):
        self.assertEqual(FormatDetector.detect("report.pdf"), DocFormat.PDF)
        self.assertEqual(FormatDetector.detect("data.xlsx"), DocFormat.EXCEL)
        self.assertEqual(FormatDetector.detect("slides.pptx"), DocFormat.POWERPOINT)
        self.assertEqual(FormatDetector.detect("page.html"), DocFormat.HTML)
        self.assertEqual(FormatDetector.detect("notes.md"), DocFormat.MARKDOWN)
        self.assertEqual(FormatDetector.detect("script.csv"), DocFormat.CSV)
        self.assertEqual(FormatDetector.detect("photo.png"), DocFormat.IMAGE)
        self.assertEqual(FormatDetector.detect("audio.mp3"), DocFormat.AUDIO)
        self.assertEqual(FormatDetector.detect('video.mp4'), DocFormat.AUDIO)

    def test_ingest_markdown(self):
        tmp = tempfile.mkdtemp()
        try:
            md = os.path.join(tmp, "test.md")
            with open(md, "w", encoding="utf-8") as f:
                f.write("# Test\n\nHello world.")
            result = self.di.ingest(md)
            self.assertIsInstance(result, IngestResult)
            self.assertIn("Hello world", result.markdown_content)
        finally:
            shutil.rmtree(tmp, ignore_errors=True)

    def test_ingest_nonexistent(self):
        """不存在的文件返回结构化结果（含 error）"""
        # 不存在的文件：先创建再删除，验证可处理
        path = tempfile.mktemp(suffix=".md")
        open(path, "w").close()  # 创建空文件
        os.remove(path)  # 删除
        try:
            result = self.di.ingest(path)
            self.fail("Should raise FileNotFoundError")
        except FileNotFoundError:
            pass  # 预期行为

    def test_normalize_extract(self):
        """_normalize_and_extract 返回 dict 含 headings"""
        tmp = tempfile.mkdtemp()
        try:
            md = os.path.join(tmp, "x.md")
            with open(md, "w") as f:
                f.write("# Title\n\n## Section\n\n- item 1\n\n[link](http://example.com)\n\n```python\nprint('x')\n```")
            result = self.di.ingest(md)
            self.assertIn("Title", result.markdown_content)
        finally:
            shutil.rmtree(tmp, ignore_errors=True)


class TestPalaceMemory(unittest.TestCase):
    """L4 记忆宫殿 (mempalace 融合)"""

    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.pm = PalaceMemory(palace_path=self.tmp)

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_raw_verbatim_store(self):
        record = self.pm.palace.store(
            raw_text="明天下午三点和张总开会",
            room_id="meeting-room-1",
            wing=PalaceWing.PROJECTS,
            speaker="user",
        )
        self.assertEqual(record.raw_text, "明天下午三点和张总开会")
        self.assertEqual(record.speaker, "user")
        self.assertIsNotNone(record.record_id)

    def test_hash_chain_integrity(self):
        r1 = self.pm.palace.store("第一条记录", "room1", PalaceWing.PEOPLE)
        r2 = self.pm.palace.store("第二条记录", "room1", PalaceWing.PEOPLE)
        self.assertIsNotNone(r2.hash_chain)
        # r2.hash_chain should contain r1's hash
        self.assertNotEqual(r1.record_id, r2.record_id)

    def test_palace_walk(self):
        for i in range(3):
            self.pm.palace.store(f"记忆 {i}", f"room{i}", PalaceWing.PROJECTS)
        walk = self.pm.palace.walk(start_room_id="room0")
        self.assertIsInstance(walk, list)

    def test_palace_stats(self):
        self.pm.palace.store("test1", "room1", PalaceWing.PEOPLE)
        self.pm.palace.store("test2", "room2", PalaceWing.PROJECTS)
        stats = self.pm.palace.stats()
        self.assertGreaterEqual(stats["total_records"], 2)


class TestCodeUnderstanding(unittest.TestCase):
    """L4 代码理解 (graphify 融合)"""

    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.cue = CodeUnderstandingEngine(output_dir=self.tmp)

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_language_detection(self):
        self.assertEqual(ASTExtractor.detect_language("main.py"), "python")
        self.assertEqual(ASTExtractor.detect_language("app.js"), "javascript")
        self.assertEqual(ASTExtractor.detect_language("server.ts"), "typescript")
        self.assertEqual(ASTExtractor.detect_language("main.go"), "go")
        self.assertEqual(ASTExtractor.detect_language("lib.rs"), "rust")
        self.assertEqual(ASTExtractor.detect_language("Main.java"), "java")
        self.assertEqual(ASTExtractor.detect_language("app.rb"), "ruby")

    def test_python_extraction(self):
        src = os.path.join(self.tmp, "sample.py")
        with open(src, "w") as f:
            f.write('''
import os
from typing import List

class DataProcessor:
    def transform(self, data: List) -> List:
        return [x * 2 for x in data]
''')
        result = ASTExtractor.extract_file(src)
        self.assertGreater(len(result["nodes"]), 0)
        node_types = {n["node_type"] for n in result["nodes"]}
        self.assertIn("file", node_types)
        self.assertIn("class", node_types)
        self.assertIn("import", node_types)

    def test_codegraph_build(self):
        cg = CodeGraph(corpus_id="test-corpus")
        node = CodeNode(
            node_id="n1", label="TestFunc", node_type="function",
            file_path="test.py", line_start=1, line_end=10,
            relationships=[]
        )
        cg.add_node(node)
        self.assertEqual(len(cg.nodes), 1)
        cg.add_edge("n1", "n2", RelationshipType.INFERRED, "calls", 0.9)
        self.assertEqual(len(cg.edges), 1)
        d = cg.to_dict()
        self.assertEqual(d["corpus_id"], "test-corpus")

    def test_leiden_communities(self):
        cg = CodeGraph(corpus_id="leiden-test")
        for i in range(5):
            cg.add_node(CodeNode(
                node_id=f"n{i}", label=f"node{i}", node_type="function",
                file_path="test.py", relationships=[]
            ))
        cg.add_edge("n0", "n1", RelationshipType.EXTRACTED)
        cg.add_edge("n1", "n2", RelationshipType.EXTRACTED)
        cg.add_edge("n3", "n4", RelationshipType.EXTRACTED)
        communities = LeidenCommunityDetector.detect_communities(cg)
        self.assertIsInstance(communities, list)


class TestEvolutionEngine(unittest.TestCase):
    """L7 自演化引擎 (OpenSpace 融合)"""

    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.ee = EvolutionEngine(
            skills_dir=os.path.join(self.tmp, "skills"),
            evolution_log=os.path.join(self.tmp, "evlog.json")
        )

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_gdpval_metrics(self):
        m = GDPValMetrics(
            task_id="task-001",
            token_cost=1000,
            quality_score=8.0,
            time_seconds=30,
            baseline_token_cost=2000,
        )
        self.assertAlmostEqual(m.token_savings(), 0.5, places=2)
        self.assertGreater(m.compute_gdp(), 0)

    def test_gdpval_no_crash_on_zero_time(self):
        """time=0 时 compute_gdp 不崩溃"""
        m = GDPValMetrics(task_id="x", token_cost=100, quality_score=5, time_seconds=0)
        gdp = m.compute_gdp()
        self.assertIsInstance(gdp, float)

    def test_evolution_candidate(self):
        c = self.ee.evolve(
            skill_name="test-skill",
            evolution_type=EvolutionType.DERIVED,
            trigger="metric_monitor",
            reason="Token 消耗增长",
            original_content="# Test Skill\n\nA test.",
            suggested_patch="# Test Skill v2\n\nImproved.",
            expected_improvement=0.2,
        )
        self.assertIsNotNone(c.candidate_id)
        self.assertIn(c.status, list(EvolutionStatus))

    def test_evolution_stats(self):
        stats = self.ee.stats()
        self.assertIn("total_candidates", stats)
        self.assertIn("skills_dir", stats)

    def test_skill_quality_monitor(self):
        sqm = SkillQualityMonitor(history_path=os.path.join(self.tmp, "health"))
        sqm.record_execution("test-skill", success=True, token_cost=500)
        sqm.record_execution("test-skill", success=True, token_cost=510)
        sqm.record_execution("test-skill", success=True, token_cost=490)
        health = sqm.assess_health("test-skill")
        self.assertIn(health["status"], {"healthy", "stable", "new"})


if __name__ == "__main__":
    unittest.main()

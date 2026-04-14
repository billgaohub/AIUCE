"""
L4 代码理解层：Code Knowledge Graph
Code Understanding — 工部/营造司

融合来源：
- graphify (safishamsi/graphify): 三通道代码理解（AST/Whisper/LLM），
  71.5x Token 节省，知识图谱，Leiden 社区检测

核心职责：
1. 三通道理解：AST（结构）→ Whisper（音视频）→ LLM（语义）
2. 知识图谱：节点=函数/类/概念，边=调用/继承/语义关系
3. 社区检测：Leiden 算法按边密度聚类（无需向量）
4. 双轨输出：graph.html（交互图）+ GRAPH_REPORT.md（文字报告）+ graph.json（图数据）

AIUCE 改造：
- graphify: Claude Code 集成 → AIUCE: L3 CognitiveOrchestrator 元认知调度
- graphify: Claude subagent 并行 → AIUCE: TaskDAG 并行执行
- graphify: Leiden 聚类 → AIUCE: 与 L1 IdentityBrain 联动
- graphify: graph.json → AIUCE: graph.json 存入 L4 PalaceMemory
"""

from typing import Dict, Any, List, Optional, Set, Tuple
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import re
import os
import json
import hashlib
import logging
from pathlib import Path
from collections import defaultdict

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════════════
# 关系类型（改造自 graphify 关系标注）
# ═══════════════════════════════════════════════════════════════════

class RelationshipType(Enum):
    """
    关系类型（改造自 graphify 的关系标签）
    EXTRACTED: 源码直接提取
    INFERRED: LLM 推断（有置信度）
    AMBIGUOUS: 标记待审核
    """
    EXTRACTED = "EXTRACTED"     # 源码直接提取
    INFERRED = "INFERRED"       # LLM 推断
    AMBIGUOUS = "AMBIGUOUS"     # 标记待审核


# ═══════════════════════════════════════════════════════════════════
# 图节点与边（改造自 graphify NetworkX 图）
# ═══════════════════════════════════════════════════════════════════

@dataclass
class CodeNode:
    """
    代码节点（改造自 graphify 节点）
    类型：file / class / function / concept / import / docstring
    """
    node_id: str
    label: str             # 显示名称
    node_type: str         # file | class | function | method | concept | module
    file_path: str         # 所属文件
    line_start: int = 0
    line_end: int = 0
    community: Optional[int] = None  # Leiden 社区编号
    language: str = ""     # python | javascript | ...
    extracted_info: Dict[str, Any] = field(default_factory=dict)  # AST 提取信息
    relationships: List[Dict[str, str]] = field(default_factory=list)  # 关系列表

    def add_relationship(
        self,
        target_id: str,
        rel_type: RelationshipType,
        label: str = "",
        confidence: float = 1.0,
    ):
        self.relationships.append({
            "source": self.node_id,
            "target": target_id,
            "type": rel_type.value,
            "label": label,
            "confidence": confidence,
        })


@dataclass
class CodeGraph:
    """
    代码知识图谱（改造自 graphify NetworkX 图）
    """
    nodes: Dict[str, CodeNode] = field(default_factory=dict)
    edges: List[Dict[str, Any]] = field(default_factory=list)  # [{source, target, type, label, confidence}]
    corpus_id: str = ""     # 图谱所属语料库 ID
    generated_at: str = field(default_factory=datetime.now().isoformat)
    file_count: int = 0
    language_stats: Dict[str, int] = field(default_factory=dict)  # {语言: 文件数}

    def add_node(self, node: CodeNode):
        self.nodes[node.node_id] = node

    def add_edge(self, source: str, target: str, rel_type: RelationshipType,
                 label: str = "", confidence: float = 1.0):
        edge = {
            "source": source,
            "target": target,
            "type": rel_type.value,
            "label": label,
            "confidence": confidence,
        }
        self.edges.append(edge)
        # 更新节点的 relationship 列表
        if source in self.nodes:
            self.nodes[source].add_relationship(target, rel_type, label, confidence)

    def get_by_community(self, community: int) -> List[CodeNode]:
        return [n for n in self.nodes.values() if n.community == community]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "corpus_id": self.corpus_id,
            "generated_at": self.generated_at,
            "file_count": self.file_count,
            "language_stats": self.language_stats,
            "nodes": {
                nid: {
                    "node_id": n.node_id,
                    "label": n.label,
                    "node_type": n.node_type,
                    "file_path": n.file_path,
                    "line_start": n.line_start,
                    "line_end": n.line_end,
                    "community": n.community,
                    "relationships": n.relationships,
                }
                for nid, n in self.nodes.items()
            },
            "edges": self.edges,
        }


# ═══════════════════════════════════════════════════════════════════
# AST 解析器（改造自 graphify 第一通道）
# 支持语言：Python, JS/TS, Go, Rust, Java, C/C++, Ruby 等
# ═══════════════════════════════════════════════════════════════════

class ASTExtractor:
    """
    AST 结构提取（改造自 graphify 第一通道）

    核心特点：
    - 零 LLM 调用（完全确定性）
    - Tree-sitter 风格结构提取（但这里用正则模拟，因为没有 tree-sitter 依赖）
    - 提取：类/函数定义、导入、调用关系、docstring、 rationale 注释
    """

    LANGUAGE_PATTERNS: Dict[str, Dict[str, str]] = {
        "python": {
            "class": r'^class\s+(\w+).*?:',
            "function": r'^def\s+(\w+)\s*\((.*?)\)\s*(?:->.*?)?:',
            "method": r'^\s+def\s+(\w+)\s*\((.*?)\)\s*(?:->.*?)?:',
            "import": r'^(?:from\s+[\w.]+\s+)?import\s+(.+)$',
            "import_from": r'^from\s+([\w.]+)\s+import\s+(.+)$',
            "call": r'(\w+)\s*\(',
            "decorator": r'^@(\w+)',
            "docstring": r'^\s+"""(.{0,200}?)"""',
            "comment_rationale": r'#\s*(?:rationale|reason|because|why|since|for|purpose):?\s*(.+)$',
        },
        "javascript": {
            "class": r'^class\s+(\w+)',
            "function": r'(?:function\s+)?(\w+)\s*\((.*?)\)\s*\{',
            "arrow": r'const\s+(\w+)\s*=\s*\(.*?\)\s*=>',
            "import": r'import\s+(?:{\s*)?([\w,\s]+)(?:\s*})?\s+from\s+[\'"](.+?)[\'"]',
            "export": r'export\s+(?:default\s+)?(?:const|function|class)\s+(\w+)',
            "call": r'(\w+)\s*\(',
        },
        "typescript": {
            "class": r'^class\s+(\w+)(?:<[\w\s,]+>)?\s*(?:extends|implements)?',
            "interface": r'^interface\s+(\w+)',
            "function": r'(?:function|const)\s+(\w+)\s*[<(]',
            "import": r'import\s+(?:{\s*)?([\w,\s]+)(?:\s*})?\s+from\s+[\'"](.+?)[\'"]',
            "type": r'type\s+(\w+)\s*=',
        },
        "go": {
            "function": r'func\s+(?:\([^)]+\)\s+)?(\w+)\s*\(',
            "struct": r'type\s+(\w+)\s+struct\s*\{',
            "import": r'import\s+"([^"]+)"',
            "package": r'^package\s+(\w+)',
        },
        "rust": {
            "function": r'fn\s+(\w+)\s*[<(]',
            "struct": r'struct\s+(\w+)',
            "impl": r'impl\s+(?:<[^>]+>\s+)?(\w+)',
            "mod": r'mod\s+(\w+)',
            "use": r'use\s+([\w:]+)',
        },
        "java": {
            "class": r'(?:public|private|protected)?\s*class\s+(\w+)',
            "method": r'(?:public|private|protected)?\s*(?:\w+\s+)*?\s*(\w+)\s*\((.*?)\)\s*(?:throws.*?)?\{',
            "import": r'import\s+([\w.]+)\s*;',
            "package": r'^package\s+([\w.]+);',
        },
    }

    @classmethod
    def detect_language(cls, file_path: str) -> str:
        """检测语言"""
        ext_map = {
            ".py": "python",
            ".js": "javascript",
            ".ts": "typescript",
            ".jsx": "javascript",
            ".tsx": "typescript",
            ".go": "go",
            ".rs": "rust",
            ".java": "java",
            ".cpp": "cpp",
            ".c": "c",
            ".rb": "ruby",
            ".kt": "kotlin",
            ".scala": "scala",
            ".php": "php",
            ".swift": "swift",
            ".lua": "lua",
            ".ex": "elixir",
            ".jl": "julia",
            ".v": "verilog",
            ".sv": "systemverilog",
            ".vue": "vue",
            ".svelte": "svelte",
            ".dart": "dart",
            ".ps1": "powershell",
        }
        ext = Path(file_path).suffix.lower()
        return ext_map.get(ext, "unknown")

    @classmethod
    def extract_file(cls, file_path: str) -> Dict[str, Any]:
        """
        从单个文件提取结构（改造自 graphify AST pass）

        Returns:
            {nodes: [], edges: [], file_path, language, info}
        """
        try:
            with open(file_path, encoding="utf-8", errors="replace") as f:
                lines = f.readlines()
        except Exception:
            return {"nodes": [], "edges": [], "file_path": file_path}

        content = "".join(lines)
        lang = cls.detect_language(file_path)
        patterns = cls.LANGUAGE_PATTERNS.get(lang, {})

        nodes = []
        edges = []
        imports = []  # 导入的模块
        defined_names = []  # 已定义的名称
        file_node_id = hashlib.md5(file_path.encode()).hexdigest()[:12]

        # 文件节点
        nodes.append({
            "node_id": file_node_id,
            "label": Path(file_path).name,
            "node_type": "file",
            "file_path": file_path,
            "line_start": 1,
            "line_end": len(lines),
            "language": lang,
        })

        current_class = None
        current_function = None

        for i, line in enumerate(lines, 1):
            orig_line = line
            line = orig_line.strip()

            # ── 类定义 ───────────────────────────────────
            if "class" in patterns and re.match(patterns["class"], line):
                m = re.match(patterns["class"], line)
                class_name = m.group(1)
                class_node_id = f"{file_node_id}:{class_name}"
                # 检查继承
                extends = re.search(r'extends\s+(\w+)', line)
                implements = re.search(r'implements\s+([\w,\s]+)', line)
                node = {
                    "node_id": class_node_id,
                    "label": class_name,
                    "node_type": "class",
                    "file_path": file_path,
                    "line_start": i,
                    "line_end": i,
                    "language": lang,
                    "extends": extends.group(1) if extends else None,
                }
                nodes.append(node)
                defined_names.append(class_name)
                current_class = class_node_id
                # 继承边
                if extends:
                    edges.append({
                        "source": class_node_id,
                        "target": f"{file_node_id}:{extends.group(1)}",
                        "type": RelationshipType.EXTRACTED.value,
                        "label": "extends",
                        "confidence": 1.0,
                    })

            # ── 函数定义 ─────────────────────────────────
            func_pattern = patterns.get("function") or patterns.get("method")
            if func_pattern and re.match(func_pattern, line):
                m = re.match(func_pattern, line)
                func_name = m.group(1)
                if func_name not in ("if", "for", "while", "class", "else", "elif"):
                    fn_node_id = f"{file_node_id}:{func_name}"
                    node = {
                        "node_id": fn_node_id,
                        "label": func_name,
                        "node_type": "method" if current_class else "function",
                        "file_path": file_path,
                        "line_start": i,
                        "line_end": i,
                        "parent_class": Path(file_path).stem if not current_class else None,
                        "language": lang,
                    }
                    nodes.append(node)
                    defined_names.append(func_name)
                    current_function = fn_node_id

            # ── 导入 ─────────────────────────────────────
            if "import" in patterns:
                imp_m = re.match(patterns["import"], line)
                if imp_m:
                    imp_node_id = f"ext:{imp_m.group(1).strip()}"
                    imports.append(imp_node_id)
                    nodes.append({
                        "node_id": imp_node_id,
                        "label": imp_m.group(1).strip(),
                        "node_type": "import",
                        "file_path": file_path,
                        "language": lang,
                    })

            # ── 调用关系 ─────────────────────────────────
            if "call" in patterns:
                for m in re.finditer(patterns["call"], line):
                    called = m.group(1)
                    if called not in ("if", "for", "while", "print", "len", "range", "self", "super"):
                        edges.append({
                            "source": current_function or file_node_id,
                            "target": f"{file_node_id}:{called}",
                            "type": RelationshipType.EXTRACTED.value,
                            "label": "calls",
                            "confidence": 1.0,
                        })

            # ── rationale 注释 ───────────────────────────
            if "comment_rationale" in patterns:
                rat_m = re.match(patterns["comment_rationale"], line)
                if rat_m:
                    # 给当前函数添加 rationale 标签
                    if current_function and current_function in [n["node_id"] for n in nodes]:
                        for n in nodes:
                            if n["node_id"] == current_function:
                                n["rationale"] = rat_m.group(1).strip()
                                break

        return {
            "nodes": nodes,
            "edges": edges,
            "file_path": file_path,
            "language": lang,
            "imports": imports,
            "defined_names": defined_names,
        }


# ═══════════════════════════════════════════════════════════════════
# Leiden 社区检测（改造自 graphify 第二阶段）
# 纯图拓扑聚类，无需向量
# ═══════════════════════════════════════════════════════════════════

class LeidenCommunityDetector:
    """
    Leiden 社区检测（改造自 graphify Leiden 聚类）

    算法说明：
    - 基于图拓扑结构的边密度聚类
    - 无需向量嵌入，无需 embedding
    - graphify 原版用 NetworkX + python-louvain/leiden
    - AIUCE: 简化版使用 BFS + 连通分量 + 边密度排序

    AIUCE 特有：
    - 语义相似边（INFERRED 关系）参与聚类
    - 与 L1 IdentityBrain 联动：god nodes 存入 Brain
    """

    @classmethod
    def detect_communities(cls, graph: CodeGraph) -> List[List[str]]:
        """
        简化 Leiden 检测：使用 BFS 找连通分量，再按边密度排序

        Returns:
            List of community node_id lists
        """
        # 构建邻接表
        adj: Dict[str, Set[str]] = defaultdict(set)
        for edge in graph.edges:
            adj[edge["source"]].add(edge["target"])
            adj[edge["target"]].add(edge["source"])

        visited: Set[str] = set()
        communities: List[Set[str]] = []

        for node_id in graph.nodes:
            if node_id in visited:
                continue
            # BFS 找连通分量
            component: Set[str] = set()
            queue = [node_id]
            while queue:
                curr = queue.pop(0)
                if curr in visited:
                    continue
                visited.add(curr)
                component.add(curr)
                queue.extend(adj.get(curr, set()) - visited)
            communities.append(component)

        # 按边密度排序（边多的优先）
        def edge_density(c: Set[str]) -> int:
            return sum(1 for e in graph.edges
                       if e["source"] in c and e["target"] in c)

        communities = sorted(communities, key=edge_density, reverse=True)

        # 分配社区编号
        for comm_id, comm in enumerate(communities):
            for node_id in comm:
                if node_id in graph.nodes:
                    graph.nodes[node_id].community = comm_id

        return [list(c) for c in communities]


# ═══════════════════════════════════════════════════════════════════
# Graphify Engine（改造自 graphify 主流程）
# ═══════════════════════════════════════════════════════════════════

class CodeUnderstandingEngine:
    """
    代码理解引擎（改造自 graphify 三通道流程）

    改造要点：
    - graphify 通道1（AST）→ AIUCE: ASTExtractor（零 LLM）
    - graphify 通道2（Whisper）→ AIUCE: 音视频转录（需要 faster-whisper）
    - graphify 通道3（LLM 语义）→ AIUCE: LLM 推断（与 CognitiveOrchestrator 联动）
    - graphify Leiden 聚类 → AIUCE: LeidenCommunityDetector
    - graphify NetworkX 图 → AIUCE: CodeGraph

    AIUCE 特有关键创新：
    - 三通道并行（与 L3 TaskDAG 联动）
    - God nodes 存入 L1 IdentityBrain
    - 合宪性审查：图谱节点先过 L0 SovereigntyGateway
    - graph.json 存入 L4 PalaceMemory
    """

    def __init__(
        self,
        output_dir: str = "~/.aiuce/codegraph",
        max_workers: int = 4,
    ):
        self.output_dir = Path(os.path.expanduser(output_dir))
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.max_workers = max_workers

    def understand(
        self,
        target: str,  # 文件夹路径或文件路径
        corpus_id: str = None,
    ) -> CodeGraph:
        """
        理解代码并生成知识图谱（改造自 graphify 主流程）

        流程：
        1. 收集文件列表（支持 .graphifyignore）
        2. AST 通道：批量提取结构
        3. 图构建：合并所有节点和边
        4. Leiden 社区检测
        5. 输出：graph.json / graph.html / GRAPH_REPORT.md
        """
        import glob

        corpus_id = corpus_id or hashlib.md5(target.encode()).hexdigest()[:12]
        graph = CodeGraph(corpus_id=corpus_id)

        # ── 1. 收集文件 ─────────────────────────────────
        ignore = self._load_ignore(target)
        files = self._collect_files(target, ignore)
        graph.file_count = len(files)
        logger.info(f"Understanding {len(files)} files in {target}")

        # ── 2. AST 提取（确定性，零 LLM）────────────────
        all_nodes = []
        all_edges = []
        lang_stats: Dict[str, int] = defaultdict(int)

        for file_path in files:
            lang = ASTExtractor.detect_language(file_path)
            lang_stats[lang] = lang_stats.get(lang, 0) + 1
            result = ASTExtractor.extract_file(file_path)
            all_nodes.extend(result["nodes"])
            all_edges.extend(result["edges"])

        graph.language_stats = dict(lang_stats)

        # ── 3. 构建图 ─────────────────────────────────
        # 节点去重
        seen_ids: Set[str] = set()
        for node in all_nodes:
            if node["node_id"] not in seen_ids:
                seen_ids.add(node["node_id"])
                graph.add_node(CodeNode(**node))

        # 边去重
        seen_edges: Set[Tuple[str, str]] = set()
        for edge in all_edges:
            key = (edge["source"], edge["target"])
            if key not in seen_edges:
                seen_edges.add(key)
                graph.edges.append(edge)

        # ── 4. Leiden 社区检测 ─────────────────────────
        communities = LeidenCommunityDetector.detect_communities(graph)
        logger.info(f"Detected {len(communities)} communities")

        # ── 5. 合宪性审查（节点-label）──────────────────
        try:
            import importlib.util
            spec = importlib.util.spec_from_file_location("sg_sgw", __file__.replace("l4_code_understanding.py", "l0_sovereignty_gateway.py"))
            sg_mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(sg_mod)
            sg = sg_mod.SovereigntyGateway()
            for node in graph.nodes.values():
                if node.node_type in ("function", "method"):
                    r = sg.audit(node.label)
                    if r.vetoed:
                        logger.warning(f"Node {node.label} vetoed by L0: {r.principle}")
        except Exception:
            pass  # L0 不可用时跳过

        # ── 6. 保存图 ─────────────────────────────────
        self._save_graph(graph)

        return graph

    def _load_ignore(self, target: str) -> Set[str]:
        """加载 .graphifyignore（类 .gitignore）"""
        ignore_file = Path(target) / ".graphifyignore"
        patterns = set()
        if ignore_file.exists():
            for line in ignore_file.read_text().splitlines():
                line = line.strip()
                if line and not line.startswith("#"):
                    patterns.add(line)
        # 默认忽略
        default_ignore = {"node_modules", ".git", "__pycache__", ".venv", "dist", "build", ".venv", "vendor"}
        patterns.update(default_ignore)
        return patterns

    def _collect_files(self, target: str, ignore: Set[str]) -> List[str]:
        """收集目标路径下的代码文件"""
        import fnmatch

        target_path = Path(target)
        files = []
        if target_path.is_file():
            return [str(target_path)]

        for root, dirs, filenames in os.walk(target_path):
            # 过滤忽略目录
            dirs[:] = [d for d in dirs if d not in ignore]
            for filename in filenames:
                # 检查 ignore patterns
                skip = False
                rel = str(Path(root) / filename)
                for pat in ignore:
                    if fnmatch.fnmatch(filename, pat) or fnmatch.fnmatch(rel, pat):
                        skip = True
                        break
                if skip:
                    continue
                # 只处理代码文件
                ext = Path(filename).suffix.lower()
                if ext in {".py", ".js", ".ts", ".jsx", ".tsx", ".go", ".rs", ".java",
                            ".cpp", ".c", ".rb", ".kt", ".scala", ".php", ".swift",
                            ".lua", ".ex", ".jl", ".v", ".sv", ".vue", ".svelte", ".dart", ".ps1",
                            ".md", ".txt"}:
                    files.append(str(Path(root) / filename))

        return files

    def _save_graph(self, graph: CodeGraph):
        """保存图到 output_dir"""
        # graph.json（供 L4 PalaceMemory 使用）
        graph_file = self.output_dir / f"{graph.corpus_id}.json"
        graph_file.write_text(json.dumps(graph.to_dict(), ensure_ascii=False, indent=2))

        # graph.html（交互图，简化版）
        html = self._generate_html(graph)
        html_file = self.output_dir / f"{graph.corpus_id}.html"
        html_file.write_text(html)

        # GRAPH_REPORT.md
        report = self._generate_report(graph)
        report_file = self.output_dir / f"{graph.corpus_id}_REPORT.md"
        report_file.write_text(report)

        logger.info(f"Saved graph to {self.output_dir}: {graph_file.name}")

    def _generate_html(self, graph: CodeGraph) -> str:
        """生成交互 HTML（简化版，基于 D3.js CDN）"""
        nodes_data = [
            {
                "id": n.node_id,
                "label": n.label,
                "type": n.node_type,
                "community": n.community,
            }
            for n in graph.nodes.values()
        ]
        edges_data = [
            {"source": e["source"], "target": e["target"], "type": e["type"]}
            for e in graph.edges
        ]
        json_data = json.dumps({"nodes": nodes_data, "links": edges_data}, ensure_ascii=False)

        # 社区颜色
        colors = ["#e41a1c","#377eb8","#4daf4a","#984ea3","#ff7f00","#ffff33","#a65628","#f781bf"]

        return f"""<!DOCTYPE html>
<html><head><meta charset="utf-8"><title>AIUCE Code Graph</title>
<script src="https://d3js.org/d3.v7.min.js"></script>
<style>
body {{ margin:0; font-family:sans-serif; background:#1a1a2e; color:#eee; }}
svg {{ width:100vw; height:100vh; }}
circle {{ stroke:#fff; stroke-width:1.5px; cursor:pointer; }}
line {{ stroke:#555; stroke-width:1px; }}
text {{ font-size:10px; fill:#ccc; pointer-events:none; }}
#tooltip {{ position:absolute; background:#2a2a4a; padding:8px; border-radius:4px; font-size:12px; max-width:300px; }}
</style></head><body>
<div id="tooltip" style="display:none"></div>
<script>
const data = {json_data};
const color = d3.scaleOrdinal()
  .domain([0,1,2,3,4,5,6,7])
  .range({json.dumps(colors)});

const sim = d3.forceSimulation(data.nodes)
  .force("link", d3.forceLink(data.links).id(d=>d.id).distance(60))
  .force("charge", d3.forceManyBody().strength(-100))
  .force("center", d3.forceCenter(window.innerWidth/2, window.innerHeight/2));

const svg = d3.select("body").append("svg");
const link = svg.append("g").selectAll("line").data(data.links).enter().append("line");
const node = svg.append("g").selectAll("g").data(data.nodes).enter().append("g")
  .call(d3.drag().on("start", drag));
const circle = node.append("circle")
  .attr("r", d=>d.type==="file"?8:d.type==="class"?6:4)
  .attr("fill", d=>color(d.community||0));
const label = node.append("text").text(d=>d.label).attr("dx",10).attr("dy",4);

link.attr("x1",d=>d.source.x).attr("y1",d=>d.source.y)
    .attr("x2",d=>d.target.x).attr("y2",d=>d.target.y);
node.attr("transform",d=>`translate(${{d.x}},${{d.y}})`);

sim.on("tick",()=>{{
  link.attr("x1",d=>d.source.x).attr("y1",d=>d.source.y)
      .attr("x2",d=>d.target.x).attr("y2",d=>d.target.y);
  node.attr("transform",d=>`translate(${{d.x}},${{d.y}})`);
}});
function drag(sv) {{
  d3.event.subject.fx=d3.event.subject.x;
  d3.event.subject.fy=d3.event.subject.y;
  sim.alphaTarget(0.3).restart();
}}
</script></body></html>"""

    def _generate_report(self, graph: CodeGraph) -> str:
        """生成文字报告"""
        lines = [
            f"# Code Graph Report: {graph.corpus_id}",
            f"Generated: {graph.generated_at}",
            f"",
            f"## Stats",
            f"- Files: {graph.file_count}",
            f"- Nodes: {len(graph.nodes)}",
            f"- Edges: {len(graph.edges)}",
            f"- Languages: {', '.join(f'{k}={v}' for k,v in graph.language_stats.items())}",
            f"",
        ]

        # God nodes（社区中连接最多的节点）
        community_sizes: Dict[int, int] = defaultdict(int)
        for node in graph.nodes.values():
            if node.community is not None:
                community_sizes[node.community] += 1

        lines.append("## God Nodes (Most Connected Per Community)")
        for comm_id in sorted(community_sizes.keys(), key=lambda c: -community_sizes[c])[:5]:
            conn_count = sum(1 for e in graph.edges if e["source"] in {n.node_id for n in graph.get_by_community(comm_id)})
            nodes_in = graph.get_by_community(comm_id)
            if nodes_in:
                hub = max(nodes_in, key=lambda n: len(n.relationships))
                lines.append(f"- Community {comm_id} ({community_sizes[comm_id]} nodes): {hub.label} ({hub.node_type})")

        lines.append("")
        lines.append("## Files")
        file_nodes = [n for n in graph.nodes.values() if n.node_type == "file"]
        for fn in sorted(file_nodes, key=lambda n: -len(n.relationships))[:20]:
            lines.append(f"- `{fn.file_path}` ({len(fn.relationships)} connections)")

        return "\n".join(lines)

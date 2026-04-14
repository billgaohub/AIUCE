"""
L9 工具注册层：锦衣卫令牌系统
Tool Harness Registry — 韩信/锦衣卫

融合来源：
- CLI-Anything (HKUDS): 工具 Agent 化协议（JSON/Human 双轨输出）
- ipipq (billgaohub): 文件类型识别 + 自动分类归档
- smart-file-router (billgaohub): 关键词路由 + 链式规则

核心职责：
- ToolHarness 协议：任何 CLI 工具注册为 L9 原生工具
- 合宪性前置：注册时必须通过 SovereigntyGateway 审查
- 双轨输出：JSON 给 AI（H9消费）+ Markdown 给人类
- ipipq + smart-file-router 作为首批注册工具
"""

from typing import Dict, Any, List, Optional, Callable, Set
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import uuid
import os
import re
import subprocess
import mimetypes


# ═══════════════════════════════════════════════════════════════════
# 工具域（来自 ai-governance-framework / 三域体系）
# ═══════════════════════════════════════════════════════════════════

class ToolDomain(Enum):
    """改造自三域体系的工具域分类"""
    BODY = "body"      # 执行域：具体操作、工具调用、文件处理
    FLOW = "flow"      # 流程域：路由、调度、协调
    INTEL = "intel"    # 认知域：分析、推理、决策


# ═══════════════════════════════════════════════════════════════════
# 工具规范
# ═══════════════════════════════════════════════════════════════════

@dataclass
class ToolSpec:
    """
    工具规范 — 改造自 CLI-Anything 的工具描述协议。
    每个注册到 L9 的工具必须声明其规范。
    """

    id: str
    name: str
    domain: ToolDomain
    layer: str  # L0-L10
    description: str
    cmd_template: str  # CLI 命令模板
    constitutional_alignment: List[str] = field(default_factory=list)
    input_schema: Dict[str, Any] = field(default_factory=dict)
    output_mode: str = "dual"  # "json" | "markdown" | "dual"
    retry_on_failure: bool = True
    max_retries: int = 3
    timeout_seconds: int = 30
    tags: List[str] = field(default_factory=list)


@dataclass
class ToolInvocation:
    """工具调用记录"""
    invocation_id: str
    tool_id: str
    params: Dict[str, Any]
    status: str  # pending | running | success | failed | timeout
    started_at: str
    completed_at: Optional[str] = None
    output: Optional[str] = None
    error: Optional[str] = None
    audit_id: Optional[str] = None
    sovereignty_passed: bool = True


# ═══════════════════════════════════════════════════════════════════
# ipipq 文件分类引擎（改造为 L9 Body 域工具）
# ═══════════════════════════════════════════════════════════════════

class IPIPQClassifier:
    """
    改造自 billgaohub/ipipq 的文件分类逻辑。
    作为 L9 的 Body 域执行工具之一。

    AIUCE 特有：
    - 合宪性：只整理文件，不执行危险操作
    - 双轨输出：JSON（AI消费）+ Markdown（人消费）
    - L5 审计：每次调用自动记录审计 ID
    """

    # 文件类型映射
    FILE_TYPE_MAP = {
        # 图片
        "image": [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".webp", ".svg", ".heic", ".tiff"],
        # 文档
        "document": [".pdf", ".doc", ".docx", ".txt", ".rtf", ".odt", ".pages"],
        # 表格
        "spreadsheet": [".xls", ".xlsx", ".csv", ".numbers", ".ods"],
        # 演示
        "presentation": [".ppt", ".pptx", ".key"],
        # 代码
        "code": [".py", ".js", ".ts", ".jsx", ".tsx", ".java", ".go", ".rs", ".c", ".cpp", ".h", ".sh", ".rb", ".php"],
        # 视频
        "video": [".mp4", ".avi", ".mov", ".mkv", ".flv", ".wmv", ".webm"],
        # 音频
        "audio": [".mp3", ".wav", ".flac", ".aac", ".ogg", ".m4a"],
        # 压缩
        "archive": [".zip", ".rar", ".7z", ".tar", ".gz", ".bz2"],
        # 医疗（关键词驱动）
        "health": ["体检", "血糖", "血压", "诊断", "用药", "病历", "处方"],
        # 商务（关键词驱动）
        "business": ["合同", "订单", "报价", "发票", "客户", "会议", "合同书"],
        # 家庭
        "family": ["家庭", "孩子", "亲子", "父母", "配偶"],
        # 项目
        "project": ["项目", "代码", "Git", "开发", "计划书", "里程碑"],
        # 知识
        "knowledge": ["学习", "读书", "笔记", "课程", "方法论", "论文"],
        # 决策
        "decision": ["决定", "选择", "方案", "结论", "评估", "决策"],
        # 经验
        "experience": ["教训", "复盘", "反思", "总结", "经验"],
    }

    @classmethod
    def classify_file(cls, filepath: str) -> Dict[str, Any]:
        """
        改造自 ipipq 的文件分类逻辑。
        返回 JSON（AI消费）和 Markdown（人消费）双轨。
        """
        filename = os.path.basename(filepath)
        ext = os.path.splitext(filename)[1].lower()
        mime_type = mimetypes.guess_type(filepath)[0] or "unknown"

        # 优先关键词匹配（高于扩展名匹配）
        for category, keywords in cls.FILE_TYPE_MAP.items():
            if any(kw in filename for kw in keywords):
                target_dir = cls._get_target_dir(category)
                return {
                    "json": {
                        "source": filepath,
                        "filename": filename,
                        "category": category,
                        "target_dir": target_dir,
                        "confidence": 0.95,
                        "matched_by": "keyword",
                    },
                    "markdown": f"**{filename}** → `{target_dir}`（关键词匹配）",
                }

        # 按扩展名匹配
        for category, exts in cls.FILE_TYPE_MAP.items():
            if ext in exts:
                target_dir = cls._get_target_dir(category)
                return {
                    "json": {
                        "source": filepath,
                        "filename": filename,
                        "category": category,
                        "target_dir": target_dir,
                        "confidence": 0.8,
                        "matched_by": "extension",
                    },
                    "markdown": f"**{filename}** → `{target_dir}`（扩展名匹配）",
                }

        # 未分类
        return {
            "json": {
                "source": filepath,
                "filename": filename,
                "category": "uncategorized",
                "target_dir": "DATA/UNCATEGORIZED/",
                "confidence": 0.3,
                "matched_by": "none",
            },
            "markdown": f"**{filename}** → `DATA/UNCATEGORIZED/`（未分类）",
        }

    @staticmethod
    def _get_target_dir(category: str) -> str:
        """改造自 smart-file-router 的目标目录映射"""
        mapping = {
            "image": "MEDIA/Images/",
            "document": "DOCS/Documents/",
            "spreadsheet": "DOCS/Spreadsheets/",
            "presentation": "DOCS/Presentations/",
            "code": "CODE/",
            "video": "MEDIA/Videos/",
            "audio": "MEDIA/Audio/",
            "archive": "DATA/Archives/",
            "health": "LIFE/Health/",
            "business": "WORK/Business/",
            "family": "LIFE/Family/",
            "project": "WORK/Projects/",
            "knowledge": "KNOWLEDGE/",
            "decision": "KNOWLEDGE/Decisions/",
            "experience": "KNOWLEDGE/Experiences/",
            "uncategorized": "DATA/UNCATEGORIZED/",
        }
        return mapping.get(category, "DATA/UNCATEGORIZED/")


# ═══════════════════════════════════════════════════════════════════
# smart-file-router 关键词路由引擎（改造为 L9 Body 域工具）
# ═══════════════════════════════════════════════════════════════════

class SmartFileRouter:
    """
    改造自 billgaohub/smart-file-router 的关键词路由引擎。
    作为 L9 Body 域的分类决策工具。

    AIUCE 特有：
    - 链式规则：多关键词按优先级排序
    - 注入 L3：路由结果可作为认知节点存入 L4
    """

    DEFAULT_RULES = [
        {"keywords": ["血糖", "血压", "体检", "诊断", "用药", "体重", "医院"], "target": "LIFE/Health/", "priority": 10},
        {"keywords": ["合同", "订单", "报价", "发票", "客户", "会议纪要", "项目"], "target": "WORK/Business/", "priority": 9},
        {"keywords": ["孩子", "家庭", "配偶", "父母", "亲子"], "target": "LIFE/Family/", "priority": 8},
        {"keywords": ["代码", "Git", "开发", "设计", "计划书"], "target": "WORK/Projects/", "priority": 7},
        {"keywords": ["学习", "读书", "笔记", "课程", "方法论", "论文"], "target": "KNOWLEDGE/", "priority": 6},
        {"keywords": ["决定", "选择", "方案", "结论", "评估"], "target": "KNOWLEDGE/Decisions/", "priority": 6},
        {"keywords": ["教训", "复盘", "反思", "总结", "经验"], "target": "KNOWLEDGE/Experiences/", "priority": 5},
    ]

    def __init__(self, custom_rules: List[Dict[str, Any]] = None):
        self.rules = (custom_rules or []) + self.DEFAULT_RULES
        self.rules.sort(key=lambda r: r["priority"], reverse=True)

    def classify(self, text: str) -> Dict[str, Any]:
        """
        改造自 smart-file-router 的 classify 逻辑。
        返回路由结果和置信度。
        """
        text_lower = text.lower()
        matched_rules = []

        for rule in self.rules:
            matched_kws = [kw for kw in rule["keywords"] if kw.lower() in text_lower]
            if matched_kws:
                matched_rules.append({
                    "rule": rule,
                    "matched_keywords": matched_kws,
                    "score": len(matched_kws) * rule["priority"],
                })

        if not matched_rules:
            return {
                "target": "DATA/WARM/",
                "confidence": 0.5,
                "keywords": [],
                "routed_by": "default",
            }

        # 取最高分规则
        best = max(matched_rules, key=lambda r: r["score"])
        confidence = min(best["score"] / 20.0, 1.0)

        return {
            "target": best["rule"]["target"],
            "confidence": confidence,
            "keywords": best["matched_keywords"],
            "routed_by": "keyword_rule",
        }


# ═══════════════════════════════════════════════════════════════════
# Tool Harness Registry
# ═══════════════════════════════════════════════════════════════════

class ToolHarnessRegistry:
    """
    改造自 CLI-Anything 的工具注册协议。

    核心设计（AIUCE 特有）：
    ┌────────────────────────────────────────────────────────────┐
    │  注册时：必须通过 L0 SovereigntyGateway 合宪性审查            │
    │  调用时：L5 审计记录（每条调用带 audit_id）                │
    │  输出时：双轨（JSON给AI，Markdown给人）                    │
    │  失败时：AUTO-FIX 尝试（受 L0 宪法约束）                   │
    └────────────────────────────────────────────────────────────┘
    """

    def __init__(
        self,
        sovereignty_gateway=None,
        audit_system=None,
    ):
        from .l0_sovereignty_gateway import SovereigntyGateway
        self.sovereignty = sovereignty_gateway or SovereigntyGateway()
        self.audit = audit_system
        self._tools: Dict[str, ToolSpec] = {}
        self._invocations: Dict[str, ToolInvocation] = {}
        self._register_native_tools()

    def _register_native_tools(self):
        """注册 AIUCE 原生工具（来自 ipipq + smart-file-router）"""

        # ── ipipq 文件整理工具 ─────────────────────────────────
        ipipq_spec = ToolSpec(
            id="aiuce-ipipq-file-organizer",
            name="file_organizer",
            domain=ToolDomain.BODY,
            layer="L9",
            description="AIUCE 文件自动整理工具（改造自 ipipq）。识别 50+ 文件类型，自动分类归档。",
            cmd_template="ipipq organize {target_dir}",
            constitutional_alignment=["body_flow_quality"],
            input_schema={
                "type": "object",
                "properties": {
                    "target_dir": {"type": "string", "description": "目标目录"},
                    "dry_run": {"type": "boolean", "default": True},
                },
            },
            output_mode="dual",
            tags=["file", "organize", "body"],
        )
        self.register(ipipq_spec)

        # ── smart-file-router 分类引擎 ─────────────────────────
        router_spec = ToolSpec(
            id="aiuce-smart-file-router",
            name="smart_file_router",
            domain=ToolDomain.BODY,
            layer="L9",
            description="关键词驱动的文件分类引擎（改造自 smart-file-router）。支持健康/商务/项目/知识等 8 类路由。",
            cmd_template="smart-router classify {text}",
            constitutional_alignment=["traceability"],
            input_schema={
                "type": "object",
                "properties": {
                    "text": {"type": "string", "description": "文件名或文本内容"},
                    "custom_rules": {"type": "array", "default": []},
                },
            },
            output_mode="dual",
            tags=["file", "router", "body"],
        )
        self.register(router_spec)

        # ── 文件类型识别器（纯 AIUCE 原生）──────────────────────
        classifier_spec = ToolSpec(
            id="aiuce-file-type-classifier",
            name="file_type_classifier",
            domain=ToolDomain.BODY,
            layer="L9",
            description="纯 AIUCE 原生文件类型识别器（改造自 ipipq）。基于扩展名+关键词双重判断。",
            cmd_template="",
            constitutional_alignment=["body_flow_quality"],
            input_schema={
                "type": "object",
                "properties": {
                    "filepath": {"type": "string", "description": "文件路径"},
                },
            },
            output_mode="dual",
            tags=["file", "classify", "body"],
        )
        self.register(classifier_spec)

    def register(self, spec: ToolSpec) -> str:
        """
        注册工具。
        改造自 CLI-Anything 的工具注册协议。

        AIUCE 特有关键：注册必须通过 L0 合宪性审查
        """
        # L0 合宪性前置检查
        veto = self.sovereignty.audit(
            f"注册工具: {spec.name}，描述: {spec.description}",
            {"context": "tool_registration"}
        )
        if veto.vetoed:
            raise PermissionError(
                f"工具 {spec.name} 未通过 L0 合宪性审查: {veto.reason}"
            )

        spec.id = spec.id or str(uuid.uuid4())[:8]
        self._tools[spec.id] = spec
        return spec.id

    def invoke(
        self,
        tool_id: str,
        params: Dict[str, Any],
    ) -> ToolInvocation:
        """
        调用工具。
        改造自 CLI-Anything 的工具执行协议。

        AIUCE 特有关键：
        1. L5 审计记录（每条调用带 audit_id）
        2. 双轨输出（JSON给AI，Markdown给人）
        3. SovereigntyGateway 审查输入
        """
        spec = self._tools.get(tool_id)
        if not spec:
            raise ValueError(f"Unknown tool: {tool_id}")

        inv = ToolInvocation(
            invocation_id=str(uuid.uuid4())[:8],
            tool_id=tool_id,
            params=params,
            status="pending",
            started_at=datetime.now().isoformat(),
        )

        # ── L0 合宪性审查（输入层）──────────────────────────────
        input_check = self.sovereignty.audit(
            f"工具调用: {spec.name}，参数: {params}",
            {"context": "tool_invocation", "tool_id": tool_id}
        )
        inv.sovereignty_passed = not input_check.vetoed
        if not inv.sovereignty_passed:
            inv.status = "failed"
            inv.error = f"L0 否决: {input_check.reason}"
            self._invocations[inv.invocation_id] = inv
            return inv

        # ── 执行 ────────────────────────────────────────────────
        inv.status = "running"
        try:
            result = self._execute(spec, params)
            inv.output = self._format_output(result, spec.output_mode)
            inv.status = "success"
        except Exception as e:
            inv.status = "failed"
            inv.error = str(e)
            inv.output = self._format_output({"error": str(e)}, spec.output_mode)

        inv.completed_at = datetime.now().isoformat()
        self._invocations[inv.invocation_id] = inv

        # ── L5 审计记录（调用后）────────────────────────────────
        if self.audit:
            from .l5_audit import AuditEntry, DecisionType
            audit_entry = AuditEntry(
                entry_id=str(uuid.uuid4())[:12],
                session_id="",
                layer="L9",
                timestamp=datetime.now().isoformat(),
                decision_type=DecisionType.ACTION.value,
                intent=f"工具调用: {spec.name}",
                reasoning=f"参数: {params}",
                output=inv.output or "",
                sovereignty_passed=inv.sovereignty_passed,
                tri_domain_score=None,
                reversible=True,
                override_available=True,
            )
            audit_id = self.audit.log(audit_entry)
            inv.audit_id = audit_id

        return inv

    def _execute(self, spec: ToolSpec, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        执行工具。
        改造自 CLI-Anything 的 harness 执行逻辑。
        """
        # 纯 Python 原生工具（ipipq 分类器 / smart-router / 文件类型识别）
        if spec.id == "aiuce-file-type-classifier":
            filepath = params.get("filepath", "")
            return IPIPQClassifier.classify_file(filepath)

        elif spec.id == "aiuce-smart-file-router":
            router = SmartFileRouter(custom_rules=params.get("custom_rules"))
            return router.classify(params.get("text", ""))

        elif spec.id == "aiuce-ipipq-file-organizer":
            # 纯 dry-run 模式，不实际移动文件
            target_dir = params.get("target_dir", "~/Downloads")
            dry_run = params.get("dry_run", True)
            return {
                "status": "simulated",
                "dry_run": dry_run,
                "target_dir": target_dir,
                "message": "dry_run=True，实际未执行文件移动",
            }

        return {"status": "unknown_tool", "tool_id": spec.id}

    @staticmethod
    def _format_output(result: Dict[str, Any], mode: str) -> str:
        """双轨输出格式化"""
        if mode in ("json", "dual"):
            json_part = json.dumps(result, ensure_ascii=False, indent=2)
        else:
            json_part = ""

        if mode in ("markdown", "dual"):
            # Markdown 人类可读输出
            md_parts = []
            if "json" in result and "markdown" in result["json"]:
                md_parts.append(result["json"]["markdown"])
            else:
                md_parts.append(f"```json\n{json.dumps(result, ensure_ascii=False, indent=2)}\n```")

            return "\n".join(md_parts)

        return json_part

    def get_tool(self, tool_id: str) -> Optional[ToolSpec]:
        return self._tools.get(tool_id)

    def list_tools(self, domain: ToolDomain = None) -> List[ToolSpec]:
        tools = list(self._tools.values())
        if domain:
            tools = [t for t in tools if t.domain == domain]
        return tools

    def get_invocation(self, invocation_id: str) -> Optional[ToolInvocation]:
        return self._invocations.get(invocation_id)

"""
Shared Constants for Eleven-Layer Architecture
十一层架构系统常量定义
"""

# ─── Layer Identifiers ──────────────────────────────────────────
class Layer:
    L0_WILL       = "L0"   # 意志层 - 最高意志/否决权
    L1_IDENTITY   = "L1"   # 身份层 - 身份验证/授权
    L2_PERCEPTION = "L2"   # 感知层 - 感知器/传感器
    L3_REASONING  = "L3"   # 推理层 - 推理引擎
    L4_MEMORY     = "L4"   # 记忆层 - 记忆存储
    L5_DECISION   = "L5"   # 决策层 - 决策引擎
    L6_EXPERIENCE = "L6"   # 经验层 - 经验模块
    L7_EVOLUTION  = "L7"   # 演化层 - 演化引擎
    L8_INTERFACE  = "L8"   # 接口层 - 接口适配
    L9_AGENT      = "L9"   # 代理层 - 代理执行
    L10_SANDBOX   = "L10"  # 沙盒层 - 沙盒环境

# ─── Layer Officials (历史人物) ─────────────────────────────────
LAYER_OFFICIALS = {
    Layer.L0_WILL:       ("秦始皇", "御书房",  "一票否决权，最高意志"),
    Layer.L1_IDENTITY:   ("诸葛亮", "宗人府",  "鞠躬尽瘁，死守人设"),
    Layer.L2_PERCEPTION: ("魏征",   "都察院",  "犯颜直谏，只说真话"),
    Layer.L3_REASONING:  ("张良",   "军机处",  "运筹帷幄，多路径坍缩"),
    Layer.L4_MEMORY:     ("司马迁", "翰林院",  "全域索引，史料编纂"),
    Layer.L5_DECISION:   ("包拯",   "大理寺",  "决策存证，审计落槌"),
    Layer.L6_EXPERIENCE: ("曾国藩", "吏部",    "结硬寨，固化成功"),
    Layer.L7_EVOLUTION:  ("商鞅",   "中书省",  "内核重构，物理变法"),
    Layer.L8_INTERFACE:  ("张骞",   "礼部",    "算力外交，丝绸之路"),
    Layer.L9_AGENT:      ("韩信",   "锦衣卫",  "多多益善，多体协同"),
    Layer.L10_SANDBOX:   ("庄子",   "钦天监",  "观星模拟，影子宇宙"),
}

# ─── Message Types ──────────────────────────────────────────────
class MsgType:
    # L0 意志
    CONSTITUTION_CHECK   = "constitution_check"
    VETO                 = "veto"

    # L1 身份
    IDENTITY_CHECK       = "identity_check"
    BOUNDARY_BLOCK       = "boundary_block"

    # L2 感知
    OBSERVE              = "observe"
    REALITY_DATA         = "reality_data"

    # L3 推理
    REASON               = "reason"
    REASONING_RESULT     = "reasoning_result"

    # L4 记忆
    STORE_MEMORY         = "store_memory"
    RETRIEVE_MEMORY      = "retrieve_memory"
    MEMORY_RESULT        = "memory_result"

    # L5 决策
    ADJUDICATE           = "adjudicate"
    DECISION_RESULT      = "decision_result"
    DECISION_APPROVED    = "decision_approved"
    DECISION_REJECTED    = "decision_rejected"

    # L6 经验
    REVIEW               = "review"
    DAILY_REVIEW         = "daily_review"
    PATTERN_DETECTED     = "pattern_detected"

    # L7 演化
    CHECK_EVOLUTION      = "check_evolution"
    EVOLUTION_PROPOSED   = "evolution_proposed"
    EVOLUTION_EXECUTED   = "evolution_executed"

    # L8 接口
    CALL_MODEL           = "call_model"
    MODEL_RESPONSE       = "model_response"

    # L9 执行
    EXECUTE              = "execute"
    EXECUTION_RESULT     = "execution_result"

    # L10 沙盒
    SIMULATE             = "simulate"
    SIMULATION_RESULT    = "simulation_result"

    # 跨层
    BROADCAST            = "broadcast"
    HEARTBEAT            = "heartbeat"

# ─── Risk Levels ───────────────────────────────────────────────
class RiskLevel:
    LOW      = "low"
    MEDIUM   = "medium"
    HIGH     = "high"
    CRITICAL = "critical"

RISK_THRESHOLDS = {
    RiskLevel.LOW:      0.0,
    RiskLevel.MEDIUM:   0.3,
    RiskLevel.HIGH:     0.6,
    RiskLevel.CRITICAL: 0.8,
}

# ─── Decision Status ────────────────────────────────────────────
class DecisionStatus:
    PENDING            = "pending"
    APPROVED           = "approved"
    REJECTED           = "rejected"
    VETOED_CONstitution = "vetoed_constitution"
    VETOED_IDENTITY    = "vetoed_identity"
    VETOED_PERCEPTION  = "vetoed_perception"
    SANDBOX_REJECTED   = "sandbox_rejected"
    EXECUTING         = "executing"
    SUCCESS           = "success"
    FAILURE           = "failure"

# ─── Memory Categories ──────────────────────────────────────────
class MemoryCategory:
    EVENT        = "event"        # 事件
    KNOWLEDGE    = "knowledge"    # 知识
    PREFERENCE   = "preference"   # 偏好
    FACT         = "fact"         # 事实
    DECISION     = "decision"      # 决策
    PATTERN      = "pattern"       # 模式
    HEALTH       = "health"       # 健康
    FINANCE      = "finance"       # 财务
    WORK         = "work"          # 工作
    PERSONAL     = "personal"      # 个人

# ─── Data Source Types ──────────────────────────────────────────
class DataSourceType:
    APPLE_HEALTH   = "apple_health"
    MANUAL          = "manual"
    API             = "api"
    SYSTEM          = "system"
    DATABASE        = "database"

# ─── Model Providers ────────────────────────────────────────────
class ProviderID:
    OPENAI  = "openai"
    CLAUDE  = "claude"
    QWEN    = "qwen"
    LOCAL   = "local"
    GROQ    = "groq"
    GEMINI  = "gemini"

# ─── Tool Categories ────────────────────────────────────────────
class ToolCategory:
    FILE          = "file"
    NETWORK       = "network"
    SYSTEM        = "system"
    DEVICE        = "device"
    COMMUNICATION = "communication"
    DATABASE      = "database"
    MEDIA         = "media"

# ─── System Prompts ──────────────────────────────────────────────
SYSTEM_PROMPT_TEMPLATE = """你是一个基于十一层架构的AI助手。

架构层级：
- L0 意志层：最高宪法，一票否决
- L1 身份层：人设边界检查
- L2 感知层：现实数据对账
- L3 推理层：多路径后果推演
- L4 记忆层：全域语义索引
- L5 决策层：决策存证审计
- L6 经验层：每日复盘固化
- L7 演化层：内核重构变法
- L8 接口层：算力外交调用
- L9 执行层：物理工具调度
- L10沙盒层：影子宇宙模拟

请基于上述架构，遵循各层职责，处理用户请求。"""

# ─── File Paths ──────────────────────────────────────────────────
import os
DROPZONE = "/Users/bill/Downloads/Qclaw_Dropzone"
WORKSPACE = os.path.expanduser("~/.qclaw/workspace")
ELEVEN_LAYER_ROOT = os.path.join(DROPZONE, "eleven_layer_ai")

PATHS = {
    "memory_store":     os.path.join(ELEVEN_LAYER_ROOT, "memory_store.json"),
    "experience_store": os.path.join(ELEVEN_LAYER_ROOT, "experience_store.json"),
    "evolution_store":  os.path.join(ELEVEN_LAYER_ROOT, "evolution_store.json"),
    "audit_log":        os.path.join(ELEVEN_LAYER_ROOT, "audit_log.json"),
    "config":           os.path.join(ELEVEN_LAYER_ROOT, "config.json"),
    "constitution":     os.path.join(ELEVEN_LAYER_ROOT, "constitution.json"),
}

# ─── Limits ──────────────────────────────────────────────────────
MAX_MEMORY_ENTRIES    = 10000
MAX_HISTORY_MESSAGES  = 1000
MAX_SANDBOX_ITERATIONS = 10000
MAX_MIND_MODELS       = 25
DEFAULT_CONTEXT_LIMIT = 10

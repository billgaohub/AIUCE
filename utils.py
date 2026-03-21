"""
Shared Utilities for Eleven-Layer Architecture
十一层架构共享工具函数
"""

import re
import hashlib
import uuid
import json
import os
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple, Union
from functools import wraps
import time


# ═══════════════════════════════════════════════════════════════
# ID Generation
# ═══════════════════════════════════════════════════════════════

def gen_id(prefix: str = "ID", length: int = 12) -> str:
    """生成唯一ID"""
    ts = datetime.now().strftime("%Y%m%d%H%M%S%f")
    raw = f"{prefix}-{ts}-{uuid.uuid4().hex[:6]}"
    return hashlib.md5(raw.encode()).hexdigest()[:length]


def gen_timestamp() -> str:
    """生成ISO格式时间戳"""
    return datetime.now().isoformat()


# ═══════════════════════════════════════════════════════════════
# Text Utilities
# ═══════════════════════════════════════════════════════════════

def truncate(text: str, max_len: int = 200, suffix: str = "...") -> str:
    """截断文本"""
    if not text or len(text) <= max_len:
        return text
    return text[:max_len - len(suffix)] + suffix


def extract_chinese_keywords(text: str, min_len: int = 2, max_count: int = 10) -> List[str]:
    """提取中文关键词"""
    phrases = re.findall(r'[\u4e00-\u9fa5]{' + str(min_len) + r',}', text)
    seen = set()
    result = []
    for p in phrases:
        if p not in seen:
            seen.add(p)
            result.append(p)
            if len(result) >= max_count:
                break
    return result


def extract_english_keywords(text: str, min_len: int = 3) -> List[str]:
    """提取英文关键词"""
    words = re.findall(r'[a-zA-Z]{' + str(min_len) + r',}', text)
    return list(set(w.lower() for w in words))


def detect_language(text: str) -> str:
    """检测语言"""
    chinese_chars = len(re.findall(r'[\u4e00-\u9fa5]', text))
    english_chars = len(re.findall(r'[a-zA-Z]', text))
    if chinese_chars > english_chars:
        return "zh"
    elif english_chars > 0:
        return "en"
    return "mixed"


def similarity_score(a: str, b: str) -> float:
    """简单的文本相似度（Jaccard + 长度因子）"""
    if not a or not b:
        return 0.0
    set_a = set(a.lower())
    set_b = set(b.lower())
    intersection = len(set_a & set_b)
    union = len(set_a | set_b)
    if union == 0:
        return 0.0
    jaccard = intersection / union
    # 加入长度惩罚
    len_factor = min(len(a), len(b)) / max(len(a), len(b), 1)
    return jaccard * 0.7 + len_factor * 0.3


# ═══════════════════════════════════════════════════════════════
# Vector/Semantic (Simplified)
# ═══════════════════════════════════════════════════════════════

def simple_embedding(text: str, dim: int = 128) -> List[float]:
    """
    生成简化版文本向量

    策略：
    1. 对每个字符取 ord 值并归一化
    2. 结合词频权重
    3. 用 hash 散列打散维度

    用于：不需要真实 embedding 模型的场景。
    正式环境请替换为 sentence-transformers / OpenAI embeddings。
    """
    # 基础向量
    vec = [0.0] * dim

    # 用内容 hash 做播撒
    seed = int(hashlib.md5(text.encode()).hexdigest(), 16) % (2**32)
    import random
    random.seed(seed)

    # 用字符 ord 填充（归一化到 0-1）
    char_vals = [ord(c) / 255.0 for c in text[:dim]]
    for i, val in enumerate(char_vals):
        vec[i] = val + random.uniform(-0.05, 0.05)

    # 用关键词做加强
    keywords = extract_chinese_keywords(text, min_len=2, max_count=5)
    for kw in keywords:
        kw_hash = int(hashlib.md5(kw.encode()).hexdigest(), 16)
        for i in range(dim):
            vec[i] += ((kw_hash >> (i % 32)) & 1) * 0.1

    # L2 归一化
    norm = sum(v * v for v in vec) ** 0.5
    if norm > 0:
        vec = [v / norm for v in vec]

    return vec


def cosine_similarity(vec_a: List[float], vec_b: List[float]) -> float:
    """计算余弦相似度"""
    if len(vec_a) != len(vec_b):
        return 0.0
    dot = sum(a * b for a, b in zip(vec_a, vec_b))
    norm_a = sum(a * a for a in vec_a) ** 0.5
    norm_b = sum(b * b for b in vec_b) ** 0.5
    if norm_a * norm_b == 0:
        return 0.0
    return dot / (norm_a * norm_b)


def semantic_search(
    query: str,
    documents: List[Tuple[str, List[float]]],
    top_k: int = 5
) -> List[Tuple[str, float]]:
    """
    语义检索（简化版）

    Args:
        query: 查询文本
        documents: List[(文本, 向量)] 
        top_k: 返回前k个

    Returns:
        List[(文档文本, 相似度分数)]
    """
    query_vec = simple_embedding(query)
    scored = []
    for doc_text, doc_vec in documents:
        score = cosine_similarity(query_vec, doc_vec)
        scored.append((doc_text, score))
    scored.sort(key=lambda x: x[1], reverse=True)
    return scored[:top_k]


# ═══════════════════════════════════════════════════════════════
# File & Storage Utilities
# ═══════════════════════════════════════════════════════════════

def ensure_dir(path: str):
    """确保目录存在"""
    os.makedirs(os.path.dirname(path), exist_ok=True)


def safe_read_json(path: str, default=None) -> Any:
    """安全读取 JSON"""
    try:
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
    except Exception:
        pass
    return default if default is not None else {}


def safe_write_json(path: str, data: Any) -> bool:
    """安全写入 JSON"""
    try:
        ensure_dir(path)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return True
    except Exception:
        return False


# ═══════════════════════════════════════════════════════════════
# Time Utilities
# ═══════════════════════════════════════════════════════════════

def parse_time(ts: str) -> datetime:
    """解析时间字符串"""
    try:
        return datetime.fromisoformat(ts)
    except Exception:
        return datetime.now()


def time_ago(ts: str) -> str:
    """返回相对时间描述"""
    try:
        dt = datetime.fromisoformat(ts)
        delta = datetime.now() - dt
        seconds = delta.total_seconds()
        if seconds < 60:
            return f"{int(seconds)}秒前"
        minutes = seconds / 60
        if minutes < 60:
            return f"{int(minutes)}分钟前"
        hours = minutes / 60
        if hours < 24:
            return f"{int(hours)}小时前"
        days = hours / 24
        if days < 30:
            return f"{int(days)}天前"
        months = days / 30
        return f"{int(months)}个月前"
    except Exception:
        return ts


def is_within_days(ts: str, days: int) -> bool:
    """判断时间戳是否在N天内"""
    try:
        dt = datetime.fromisoformat(ts)
        return (datetime.now() - dt).days <= days
    except Exception:
        return False


def date_range(start: str, end: str) -> List[str]:
    """生成日期范围"""
    try:
        start_dt = datetime.fromisoformat(start)
        end_dt = datetime.fromisoformat(end)
        dates = []
        current = start_dt
        while current <= end_dt:
            dates.append(current.strftime("%Y-%m-%d"))
            current += timedelta(days=1)
        return dates
    except Exception:
        return []


# ═══════════════════════════════════════════════════════════════
# Intent Detection
# ═══════════════════════════════════════════════════════════════

INTENT_PATTERNS = {
    "task": [
        r"帮我", r"请", r"能不能", r"可以帮我", r"帮我做",
        r"生成", r"创建", r"执行", r"运行", r"处理"
    ],
    "question": [
        r"如何", r"怎么", r"为什么", r"什么", r"哪个",
        r"多少", r"是不是", r"能不能", r"有没有"
    ],
    "query": [
        r"查询", r"搜索", r"找", r"看看", r"检查", r"查看"
    ],
    "confirm": [
        r"确认", r"确定", r"执行", r"开始吧", r"好的"
    ],
    "cancel": [
        r"取消", r"算了", r"不要了", r"停止"
    ],
}


def detect_intent(text: str) -> List[str]:
    """检测意图"""
    intents = []
    text_lower = text.lower()
    for intent, patterns in INTENT_PATTERNS.items():
        for p in patterns:
            if re.search(p, text_lower):
                intents.append(intent)
                break
    return intents if intents else ["general"]


SENSITIVE_KEYWORDS = [
    "密码", "账号", "隐私", "删除所有", "永久删除",
    "转账", "支付", "信用卡", "身份证", "地址",
    "发送", "发布", "公开", "取消订阅", "退款"
]


def contains_sensitive(text: str) -> Tuple[bool, List[str]]:
    """检测敏感词"""
    found = []
    text_lower = text.lower()
    for kw in SENSITIVE_KEYWORDS:
        if kw in text_lower:
            found.append(kw)
    return len(found) > 0, found


# ═══════════════════════════════════════════════════════════════
# Risk Assessment
# ═══════════════════════════════════════════════════════════════

RISKY_PATTERNS = [
    (r"删除.*所有", 0.8, "批量删除"),
    (r"永久删除", 0.9, "永久删除"),
    (r"清空", 0.7, "清空操作"),
    (r"转账.*[0-9,]+", 0.9, "转账操作"),
    (r"发送.*邮件.*给", 0.5, "发送邮件"),
    (r"发布.*社交", 0.5, "发布社交媒体"),
    (r"撤销.*不可逆", 0.7, "不可逆操作"),
    (r"修改.*核心", 0.6, "核心修改"),
]


def assess_risk(text: str) -> Tuple[float, List[str]]:
    """评估风险分数"""
    score = 0.0
    factors = []
    text_lower = text.lower()
    for pattern, weight, description in RISKY_PATTERNS:
        if re.search(pattern, text_lower):
            score += weight
            factors.append(description)
    return min(1.0, score), factors


def get_risk_level(score: float) -> str:
    """根据分数获取风险等级"""
    if score >= 0.8:
        return "critical"
    elif score >= 0.6:
        return "high"
    elif score >= 0.3:
        return "medium"
    return "low"


# ═══════════════════════════════════════════════════════════════
# Performance Utilities
# ═══════════════════════════════════════════════════════════════

class Timer:
    """计时器"""
    def __init__(self, name: str = ""):
        self.name = name
        self.start = time.time()
        self.end = None

    def stop(self) -> float:
        self.end = time.time()
        return self.elapsed_ms()

    def elapsed_ms(self) -> int:
        elapsed = (self.end or time.time()) - self.start
        return int(elapsed * 1000)

    def __enter__(self):
        return self

    def __exit__(self, *args):
        ms = self.stop()
        if self.name:
            print(f"  [Timer] {self.name}: {ms}ms")


def retry(max_attempts: int = 3, delay: float = 0.5):
    """重试装饰器"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if attempt == max_attempts - 1:
                        raise
                    print(f"  [Retry] {func.__name__} 失败 ({attempt+1}/{max_attempts}): {e}")
                    time.sleep(delay)
            return None
        return wrapper
    return decorator


# ═══════════════════════════════════════════════════════════════
# Formatting Utilities
# ═══════════════════════════════════════════════════════════════

def format_layer_chain(layers: List[str]) -> str:
    """格式化层级链"""
    if not layers:
        return "无"
    return " → ".join(layers)


def format_score(score: float) -> str:
    """格式化分数"""
    return f"{score:.0%}" if score <= 1.0 else f"{score:.1f}"


def format_duration(ms: int) -> str:
    """格式化时长"""
    if ms < 1000:
        return f"{ms}ms"
    seconds = ms / 1000
    if seconds < 60:
        return f"{seconds:.1f}s"
    minutes = seconds / 60
    return f"{minutes:.1f}min"


def format_table(headers: List[str], rows: List[List[str]]) -> str:
    """格式化表格（纯文本）"""
    col_widths = [len(h) for h in headers]
    for row in rows:
        for i, cell in enumerate(row):
            col_widths[i] = max(col_widths[i], len(str(cell)))

    def fmt_row(cells):
        return "  ".join(str(c).ljust(w) for c, w in zip(cells, col_widths))

    lines = []
    lines.append(fmt_row(headers))
    lines.append("-" * (sum(col_widths) + len(col_widths) * 2))
    for row in rows:
        lines.append(fmt_row(row))
    return "\n".join(lines)


# ═══════════════════════════════════════════════════════════════
# Validation Utilities
# ═══════════════════════════════════════════════════════════════

def is_valid_timestamp(ts: str) -> bool:
    """验证时间戳格式"""
    try:
        datetime.fromisoformat(ts)
        return True
    except Exception:
        return False


def validate_hash(content: str, expected_hash: str, algo: str = "md5") -> bool:
    """验证哈希"""
    try:
        if algo == "md5":
            actual = hashlib.md5(content.encode()).hexdigest()[:len(expected_hash)]
        elif algo == "sha256":
            actual = hashlib.sha256(content.encode()).hexdigest()[:len(expected_hash)]
        else:
            return False
        return actual == expected_hash
    except Exception:
        return False


def generate_hash(data: Any, algo: str = "md5", length: int = 16) -> str:
    """生成哈希"""
    content = json.dumps(data, sort_keys=True, ensure_ascii=False)
    if algo == "md5":
        return hashlib.md5(content.encode()).hexdigest()[:length]
    elif algo == "sha256":
        return hashlib.sha256(content.encode()).hexdigest()[:length]
    return ""


# ═══════════════════════════════════════════════════════════════
# Priority Queue (Simple)
# ═══════════════════════════════════════════════════════════════

class PriorityQueue:
    """简单优先级队列（基于堆）"""
    def __init__(self):
        self._items = []

    def push(self, item: Any, priority: float):
        import heapq
        heapq.heappush(self._items, (-priority, item))

    def pop(self) -> Any:
        import heapq
        if not self._items:
            return None
        _, item = heapq.heappop(self._items)
        return item

    def peek(self) -> Any:
        if self._items:
            return self._items[0][1]
        return None

    def is_empty(self) -> bool:
        return len(self._items) == 0

    def __len__(self) -> int:
        return len(self._items)

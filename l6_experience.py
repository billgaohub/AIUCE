"""
L6 经验层：曾国藩/吏部
Experience Review - 复盘扫描

职责：
1. 扫描偏离度
2. 将成功惯性硬化为准则
3. 结硬寨，打呆仗 - 通过每日复盘将偶然成功硬化为系统必然

增强版: core/l6_experience.py (ExperienceEngine + 经验日志)
本文件为 system.py 集成版本，接口稳定。
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import json
import os


@dataclass
class ReviewRecord:
    """复盘记录"""
    id: str
    timestamp: str
    original_decision: str
    outcome: str  # success, failure, partial
    deviation: float  # 偏离度 0-1
    lessons: List[str]
    patterns: List[str]


@dataclass
class SuccessPattern:
    """成功模式"""
    pattern_id: str
    description: str
    success_count: int
    last_validated: str
    solidification: float = 0.0  # 0-1, 越高越稳定


class ExperienceLayer:
    """
    经验层 - 曾国藩/吏部
    
    "结硬寨，打呆仗"
    
    复盘所有决策的 outcomes，
    发现成功模式，固化成功惯性。
    发现失败模式，防止重蹈覆辙。
    """

    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        # 使用用户主目录下的 .aiuce 目录，避免硬编码路径
        default_path = os.path.expanduser("~/.aiuce/experience_store.json")
        self.storage_path = self.config.get("storage_path", default_path)
        
        self.reviews: List[ReviewRecord] = []
        self.patterns: Dict[str, SuccessPattern] = {}
        self.deviation_threshold = self.config.get("deviation_threshold", 0.3)
        
        self._load_experience()

    def _load_experience(self):
        """加载经验数据"""
        if os.path.exists(self.storage_path):
            try:
                with open(self.storage_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    # 加载成功模式
                    for p_data in data.get("patterns", []):
                        self.patterns[p_data["pattern_id"]] = SuccessPattern(**p_data)
                    print(f"  [L6] 加载 {len(self.patterns)} 个成功模式")
            except Exception as e:
                print(f"  [L6] 加载经验失败: {e}")

    def _save_experience(self):
        """保存经验数据"""
        try:
            data = {
                "patterns": [p.__dict__ for p in self.patterns.values()]
            }
            with open(self.storage_path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"  [L6] 保存经验失败: {e}")

    def review(
        self,
        user_input: str,
        decision: Dict[str, Any],
        model_response: Any,
        execution_result: Dict[str, Any]
    ):
        """
        事后复盘
        
        在决策执行后调用，记录本次决策的效果。
        """
        review = ReviewRecord(
            id=f"review-{datetime.now().strftime('%Y%m%d%H%M%S')}",
            timestamp=datetime.now().isoformat(),
            original_decision=decision.get("action", ""),
            outcome=self._assess_outcome(execution_result),
            deviation=0.0,  # 待后续更新
            lessons=[],
            patterns=[]
        )
        
        self.reviews.append(review)
        
        # 如果成功，尝试提取模式
        if review.outcome in ["success", "partial"]:
            self._extract_pattern(user_input, decision, model_response)
        
        print(f"  [L6 曾国藩] 📊 复盘记录: {review.id} [{review.outcome}]")
        
        # 返回复盘结果
        return {
            "review_id": review.id,
            "outcome": review.outcome,
            "timestamp": review.timestamp
        }

    def _assess_outcome(self, result: Dict[str, Any]) -> str:
        """评估执行结果"""
        if result.get("status") == "success":
            if result.get("vetoed"):
                return "blocked"
            return "success"
        elif result.get("status") == "vetoed_constitution":
            return "blocked"
        elif result.get("status") == "sandbox_rejected":
            return "rejected_sandbox"
        else:
            return "failure"

    def _extract_pattern(
        self,
        user_input: str,
        decision: Dict[str, Any],
        response: Any
    ):
        """从成功案例中提取模式"""
        # 简化：基于关键词提取简单模式
        keywords = self._extract_key_phrases(user_input)
        
        for kw in keywords:
            if kw not in self.patterns:
                self.patterns[kw] = SuccessPattern(
                    pattern_id=f"pattern-{kw}",
                    description=f"与「{kw}」相关的成功模式",
                    success_count=1,
                    last_validated=datetime.now().isoformat()
                )
            else:
                self.patterns[kw].success_count += 1
                self.patterns[kw].last_validated = datetime.now().isoformat()
                # 更新solidification
                self.patterns[kw].solidification = min(1.0, self.patterns[kw].solidification + 0.1)
        
        self._save_experience()

    def _extract_key_phrases(self, text: str) -> List[str]:
        """提取关键短语"""
        import re
        # 提取2-4个字的连续中文
        phrases = re.findall(r'[\u4e00-\u9fa5]{2,4}', text)
        # 去重但保持顺序
        seen = set()
        unique = []
        for p in phrases:
            if p not in seen and len(p) >= 2:
                seen.add(p)
                unique.append(p)
        return unique[:5]  # 最多5个

    def daily_review(self) -> Dict[str, Any]:
        """
        每日复盘 - 曾国藩式
        
        分析过去24小时的决策记录，
        识别偏离度，固化成功模式。
        """
        now = datetime.now()
        yesterday = now - timedelta(days=1)
        
        # 筛选过去24小时的复盘
        recent = [
            r for r in self.reviews
            if datetime.fromisoformat(r.timestamp) >= yesterday
        ]
        
        # 统计
        total = len(recent)
        successes = len([r for r in recent if r.outcome == "success"])
        failures = len([r for r in recent if r.outcome == "failure"])
        
        # 识别偏离
        anomalies = []
        for review in recent:
            if review.outcome == "failure":
                anomalies.append({
                    "decision": review.original_decision,
                    "timestamp": review.timestamp
                })
        
        # 识别成功模式
        success_patterns = [
            {
                "pattern": p.description,
                "successes": p.success_count,
                "solidification": f"{p.solidification:.0%}"
            }
            for p in self.patterns.values()
            if p.success_count >= 3
        ]
        
        result = {
            "date": now.strftime("%Y-%m-%d"),
            "summary": {
                "total_decisions": total,
                "successes": successes,
                "failures": failures,
                "success_rate": successes / total if total > 0 else 0
            },
            "anomalies": anomalies,
            "success_patterns": success_patterns
        }
        
        print(f"  [L6 曾国藩] 📅 每日复盘:")
        print(f"     今日决策: {total}, 成功: {successes}, 失败: {failures}")
        if success_patterns:
            print(f"     固化模式: {len(success_patterns)} 项")
        
        return result

    def get_patterns(self) -> List[Dict[str, Any]]:
        """获取所有成功模式"""
        return [
            {
                "id": p.pattern_id,
                "description": p.description,
                "success_count": p.success_count,
                "solidification": f"{p.solidification:.0%}",
                "last_validated": p.last_validated
            }
            for p in self.patterns.values()
        ]

    def apply_pattern_guidance(self, decision: Dict[str, Any]) -> Dict[str, Any]:
        """应用成功模式指导决策"""
        guidance = {"adjusted": False, "adjustments": []}
        
        decision_action = decision.get("action", "")
        for pattern in self.patterns.values():
            if pattern.solidification >= 0.7:  # 高固化模式
                if any(p in decision_action for p in pattern.pattern_id.split("-")):
                    guidance["adjustments"].append(
                        f"建议遵循成功模式: {pattern.description}"
                    )
                    guidance["adjusted"] = True
        
        return guidance

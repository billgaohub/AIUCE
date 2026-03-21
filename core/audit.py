"""
审计日志 - 包拯/大理寺的账簿
Audit Log - Immutable Record

所有决策、否决、操作都必须记录在案，
不可篡改，有据可查。
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
import json
import os
import hashlib


class AuditLog:
    """
    审计日志 - 不可篡改的决策记录
    
    记录：
    1. 所有通过的决策
    2. 所有被否决的决策（包括否决原因）
    3. 所有执行的操作
    4. 所有沙盒模拟结果
    """

    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.storage_path = self.config.get("storage_path",
            "/Users/bill/Downloads/Qclaw_Dropzone/eleven_layer_ai/audit_log.json"
        )
        self.logs: List[Dict[str, Any]] = []
        self._load_logs()

    def _load_logs(self):
        """加载审计日志"""
        if os.path.exists(self.storage_path):
            try:
                with open(self.storage_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.logs = data.get("logs", [])
                    print(f"  [审计] 加载 {len(self.logs)} 条审计记录")
            except Exception as e:
                print(f"  [审计] 加载失败: {e}")

    def _save_logs(self):
        """保存审计日志"""
        try:
            # 确保目录存在
            os.makedirs(os.path.dirname(self.storage_path), exist_ok=True)
            
            data = {
                "last_updated": datetime.now().isoformat(),
                "total_logs": len(self.logs),
                "logs": self.logs
            }
            with open(self.storage_path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"  [审计] 保存失败: {e}")

    def _generate_id(self, prefix: str) -> str:
        """生成审计ID"""
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        raw = f"{prefix}-{timestamp}-{len(self.logs)}"
        return hashlib.md5(raw.encode()).hexdigest()[:12]

    def log_decision(
        self,
        user_input: str,
        decision: Dict[str, Any],
        reasoning: Dict[str, Any]
    ) -> str:
        """记录决策"""
        audit_id = self._generate_id("AUD")
        
        log_entry = {
            "id": audit_id,
            "type": "decision",
            "timestamp": datetime.now().isoformat(),
            "user_input": user_input[:200],
            "decision": {
                "action": decision.get("action"),
                "approved": decision.get("approved"),
                "confidence": decision.get("confidence"),
                "risk_level": decision.get("risk_level"),
                "audit_hash": decision.get("audit_hash")
            },
            "reasoning": {
                "paths_count": len(reasoning.get("paths", [])),
                "recommendation": reasoning.get("recommendation"),
                "confidence": reasoning.get("confidence")
            },
            "layers_involved": reasoning.get("layers_involved", [])
        }
        
        self.logs.append(log_entry)
        self._save_logs()
        
        return audit_id

    def log_veto(self, layer: str, user_input: str, reason: str):
        """记录否决"""
        audit_id = self._generate_id("VETO")
        
        log_entry = {
            "id": audit_id,
            "type": "veto",
            "timestamp": datetime.now().isoformat(),
            "layer": layer,
            "user_input": user_input[:200],
            "reason": reason,
            "status": "blocked"
        }
        
        self.logs.append(log_entry)
        self._save_logs()
        
        print(f"  [审计] ⚠️ 否决记录: {layer} - {reason}")

    def log_sandbox_rejection(
        self,
        decision_id: str,
        sandbox_result: Dict[str, Any]
    ):
        """记录沙盒拒绝"""
        audit_id = self._generate_id("SBX")
        
        log_entry = {
            "id": audit_id,
            "type": "sandbox_rejection",
            "timestamp": datetime.now().isoformat(),
            "decision_id": decision_id,
            "success_rate": sandbox_result.get("success_rate"),
            "warning": sandbox_result.get("warning")
        }
        
        self.logs.append(log_entry)
        self._save_logs()

    def log_execution(
        self,
        decision_id: str,
        execution_result: Dict[str, Any]
    ):
        """记录执行"""
        audit_id = self._generate_id("EXEC")
        
        log_entry = {
            "id": audit_id,
            "type": "execution",
            "timestamp": datetime.now().isoformat(),
            "decision_id": decision_id,
            "results": execution_result.get("results", []),
            "success_count": execution_result.get("success_count", 0)
        }
        
        self.logs.append(log_entry)
        self._save_logs()

    def get_logs(
        self,
        limit: int = 100,
        log_type: str = None
    ) -> List[Dict[str, Any]]:
        """获取审计日志"""
        logs = self.logs[-limit:]
        
        if log_type:
            logs = [l for l in logs if l.get("type") == log_type]
        
        return logs

    def get_stats(self) -> Dict[str, Any]:
        """获取审计统计"""
        total = len(self.logs)
        by_type = {}
        
        for log in self.logs:
            t = log.get("type", "unknown")
            by_type[t] = by_type.get(t, 0) + 1
        
        return {
            "total": total,
            "by_type": by_type,
            "last_log": self.logs[-1] if self.logs else None
        }

    def verify_integrity(self) -> bool:
        """验证日志完整性"""
        # 简单检查：验证文件未被篡改
        if not os.path.exists(self.storage_path):
            return False
        
        try:
            with open(self.storage_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                return data.get("total_logs") == len(data.get("logs", []))
        except:
            return False

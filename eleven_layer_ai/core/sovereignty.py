"""
Sovereignty Protection: 主权保护层
Phase 3 核心组件

基于 Agentic DeAI 理念：
- 数据本地化保障
- 外部数据传输审计
- 隐私边界检查
- 自主决策权保障

架构：
┌──────────────────────────────────────────┐
│       Sovereignty Protection Layer        │
├──────────────────────────────────────────┤
│  Data Localization                        │
│  ├── 本地数据强制存储                       │
│  ├── 外部传输白名单                        │
│  └── 数据分级（公开/内部/机密/主权）        │
├──────────────────────────────────────────┤
│  Transfer Audit                           │
│  ├── 出站数据审计                          │
│  ├── 敏感信息过滤                          │
│  └── 传输日志                             │
├──────────────────────────────────────────┤
│  Privacy Boundary                         │
│  ├── 隐私边界检查                          │
│  ├── 数据脱敏                             │
│  └── 最小化暴露                            │
└──────────────────────────────────────────┘
"""

from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import json
import hashlib
import re


class DataClassification(Enum):
    """数据分级"""
    PUBLIC = "public"               # 公开数据
    INTERNAL = "internal"           # 内部数据
    CONFIDENTIAL = "confidential"   # 机密数据
    SOVEREIGN = "sovereign"         # 主权数据（不可外传）


class TransferDecision(Enum):
    """传输决策"""
    ALLOWED = "allowed"
    BLOCKED = "blocked"
    REDACTED = "redacted"          # 脱敏后允许
    PENDING_REVIEW = "pending_review"


@dataclass
class DataTransfer:
    """数据传输记录"""
    transfer_id: str
    source: str
    destination: str
    data_classification: DataClassification
    content_hash: str
    decision: TransferDecision
    reason: str = ""
    redacted_content: str = ""
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "transfer_id": self.transfer_id,
            "source": self.destination,
            "destination": self.destination,
            "data_classification": self.data_classification.value,
            "content_hash": self.content_hash,
            "decision": self.decision.value,
            "reason": self.reason,
            "timestamp": self.timestamp
        }


@dataclass
class PrivacyRule:
    """隐私规则"""
    rule_id: str
    name: str
    description: str
    pattern: str                          # 匹配模式（正则或关键词）
    classification: DataClassification
    action: TransferDecision
    enabled: bool = True


class SovereigntyProtection:
    """
    主权保护层
    
    保障用户数据主权，控制数据流动
    
    使用方式：
    ```python
    sp = SovereigntyProtection()
    
    # 分类数据
    classification = sp.classify("用户的手机号是 13800138000")
    
    # 检查是否允许传输
    decision = sp.check_transfer(content, source="local", destination="api.openai.com")
    
    # 脱敏
    redacted = sp.redact("用户的手机号是 13800138000")
    ```
    """
    
    SENSITIVE_PATTERNS = {
        "phone": r"\d{11}",
        "email": r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+",
        "id_card": r"\d{17}[\dXx]",
        "bank_card": r"\d{16,19}",
        "ip_address": r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}",
        "api_key": r"(api[_-]?key|secret|token|password)\s*[:=]\s*\S+",
    }
    
    LOCAL_DOMAINS = ["localhost", "127.0.0.1", "::1", "0.0.0.0"]
    ALLOWED_EXTERNAL_DOMAINS: List[str] = []
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self._allowed_domains = set(
            self.config.get("allowed_domains", []) + self.LOCAL_DOMAINS
        )
        self._privacy_rules: List[PrivacyRule] = []
        self._transfer_log: List[DataTransfer] = []
        self._setup_default_rules()
    
    def _setup_default_rules(self):
        self._privacy_rules = [
            PrivacyRule(
                rule_id="rule_phone",
                name="手机号保护",
                description="手机号属于机密数据",
                pattern="phone",
                classification=DataClassification.CONFIDENTIAL,
                action=TransferDecision.REDACTED
            ),
            PrivacyRule(
                rule_id="rule_id_card",
                name="身份证保护",
                description="身份证号属于主权数据",
                pattern="id_card",
                classification=DataClassification.SOVEREIGN,
                action=TransferDecision.BLOCKED
            ),
            PrivacyRule(
                rule_id="rule_bank_card",
                name="银行卡保护",
                description="银行卡号属于主权数据",
                pattern="bank_card",
                classification=DataClassification.SOVEREIGN,
                action=TransferDecision.BLOCKED
            ),
            PrivacyRule(
                rule_id="rule_api_key",
                name="密钥保护",
                description="API密钥属于主权数据",
                pattern="api_key",
                classification=DataClassification.SOVEREIGN,
                action=TransferDecision.BLOCKED
            ),
            PrivacyRule(
                rule_id="rule_email",
                name="邮箱保护",
                description="邮箱属于机密数据",
                pattern="email",
                classification=DataClassification.CONFIDENTIAL,
                action=TransferDecision.REDACTED
            ),
        ]
    
    def classify(self, content: str) -> DataClassification:
        """分类数据敏感级别"""
        max_classification = DataClassification.PUBLIC
        
        for pattern_name, pattern in self.SENSITIVE_PATTERNS.items():
            if re.search(pattern, content):
                rule = next((r for r in self._privacy_rules if r.pattern == pattern_name), None)
                if rule:
                    if rule.classification == DataClassification.SOVEREIGN:
                        return DataClassification.SOVEREIGN
                    elif rule.classification == DataClassification.CONFIDENTIAL:
                        max_classification = DataClassification.CONFIDENTIAL
        
        return max_classification
    
    def check_transfer(
        self,
        content: str,
        source: str = "local",
        destination: str = ""
    ) -> DataTransfer:
        """检查数据是否允许传输"""
        content_hash = hashlib.sha256(content.encode()).hexdigest()[:16]
        transfer_id = f"tf_{hashlib.md5(f'{content_hash}{destination}{datetime.now().isoformat()}'.encode()).hexdigest()[:8]}"
        
        classification = self.classify(content)
        
        # 本地传输始终允许
        is_local = any(domain in destination for domain in self.LOCAL_DOMAINS)
        if is_local or not destination:
            decision = TransferDecision.ALLOWED
            reason = "本地传输"
        # 主权数据不可外传
        elif classification == DataClassification.SOVEREIGN:
            decision = TransferDecision.BLOCKED
            reason = f"主权数据禁止外传（包含{classification.value}级数据）"
        # 机密数据需要脱敏
        elif classification == DataClassification.CONFIDENTIAL:
            is_allowed_dest = any(domain in destination for domain in self._allowed_domains)
            if is_allowed_dest:
                decision = TransferDecision.REDACTED
                reason = "白名单域名，脱敏后允许"
            else:
                decision = TransferDecision.PENDING_REVIEW
                reason = "机密数据需审核后传输"
        # 内部数据限制传输
        elif classification == DataClassification.INTERNAL:
            is_allowed_dest = any(domain in destination for domain in self._allowed_domains)
            if is_allowed_dest:
                decision = TransferDecision.ALLOWED
                reason = "白名单域名，允许传输"
            else:
                decision = TransferDecision.PENDING_REVIEW
                reason = "内部数据需审核后传输"
        else:
            decision = TransferDecision.ALLOWED
            reason = "公开数据，允许传输"
        
        redacted_content = ""
        if decision == TransferDecision.REDACTED:
            redacted_content = self.redact(content)
        
        transfer = DataTransfer(
            transfer_id=transfer_id,
            source=source,
            destination=destination,
            data_classification=classification,
            content_hash=content_hash,
            decision=decision,
            reason=reason,
            redacted_content=redacted_content
        )
        
        self._transfer_log.append(transfer)
        return transfer
    
    def redact(self, content: str) -> str:
        """脱敏处理"""
        redacted = content
        
        # 手机号脱敏
        redacted = re.sub(r"(\d{3})\d{4}(\d{4})", r"\1****\2", redacted)
        
        # 邮箱脱敏
        redacted = re.sub(r"([a-zA-Z0-9]).*?(@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+)", r"\1***\2", redacted)
        
        # 身份证脱敏
        redacted = re.sub(r"(\d{4})\d{10}([\dXx])", r"\1**********\2", redacted)
        
        # 银行卡脱敏
        redacted = re.sub(r"(\d{4})\d{8,12}(\d{4})", r"\1********\2", redacted)
        
        # API 密钥脱敏
        redacted = re.sub(
            r"(api[_-]?key|secret|token|password)\s*[:=]\s*\S+",
            r"\1=***REDACTED***",
            redacted,
            flags=re.IGNORECASE
        )
        
        return redacted
    
    def add_allowed_domain(self, domain: str):
        self._allowed_domains.add(domain)
    
    def get_transfer_log(self, limit: int = 100) -> List[Dict[str, Any]]:
        return [t.to_dict() for t in self._transfer_log[-limit:]]
    
    def stats(self) -> Dict[str, Any]:
        decisions = {}
        for t in self._transfer_log:
            d = t.decision.value
            decisions[d] = decisions.get(d, 0) + 1
        
        return {
            "total_transfers_checked": len(self._transfer_log),
            "decisions": decisions,
            "allowed_domains": len(self._allowed_domains),
            "privacy_rules": len(self._privacy_rules)
        }

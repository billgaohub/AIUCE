"""
Asset Custody: 资产托管抽象层
Phase 3 核心组件

支持 Agentic DeAI 能力：
- 账户抽象
- 资金管理
- 交易签名/验证
- 余额追踪

架构：
┌──────────────────────────────────────────┐
│         Asset Custody Interface           │
├──────────────────────────────────────────┤
│  Account Abstraction                      │
│  ├── 多链账户统一                          │
│  └── 权限分级                              │
├──────────────────────────────────────────┤
│  Transaction Management                   │
│  ├── 签名/验证                            │
│  ├── 模拟执行                             │
│  └── 回滚机制                            │
├──────────────────────────────────────────┤
│  Balance Tracking                         │
│  ├── 多资产余额                           │
│  └── 历史记录                             │
└──────────────────────────────────────────┘
"""

from typing import Dict, Any, List, Optional, Protocol, runtime_checkable
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import json
import hashlib


class AssetType(Enum):
    """资产类型"""
    NATIVE = "native"           # 原生代币
    TOKEN = "token"             # ERC-20 等
    NFT = "nft"                 # 非同质化代币
    FIAT = "fiat"               # 法币
    POINTS = "points"           # 积分


class TransactionStatus(Enum):
    """交易状态"""
    PENDING = "pending"
    SIMULATED = "simulated"
    SIGNED = "signed"
    SUBMITTED = "submitted"
    CONFIRMED = "confirmed"
    FAILED = "failed"
    ROLLED_BACK = "rolled_back"


@dataclass
class AssetBalance:
    """资产余额"""
    asset_type: AssetType
    symbol: str
    amount: float
    decimals: int = 18
    chain: str = "default"
    last_updated: str = field(default_factory=lambda: datetime.now().isoformat())
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "asset_type": self.asset_type.value,
            "symbol": self.symbol,
            "amount": self.amount,
            "decimals": self.decimals,
            "chain": self.chain,
            "last_updated": self.last_updated
        }


@dataclass
class Transaction:
    """交易记录"""
    tx_id: str
    from_address: str
    to_address: str
    asset: AssetBalance
    status: TransactionStatus = TransactionStatus.PENDING
    signature: str = ""
    tx_hash: str = ""
    gas_estimate: float = 0.0
    actual_gas: float = 0.0
    error_message: str = ""
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    confirmed_at: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "tx_id": self.tx_id,
            "from_address": self.from_address,
            "to_address": self.to_address,
            "asset": self.asset.to_dict(),
            "status": self.status.value,
            "signature": self.signature,
            "tx_hash": self.tx_hash,
            "gas_estimate": self.gas_estimate,
            "actual_gas": self.actual_gas,
            "error_message": self.error_message,
            "created_at": self.created_at,
            "confirmed_at": self.confirmed_at
        }


@dataclass
class Account:
    """账户"""
    account_id: str
    address: str
    chain: str
    balances: List[AssetBalance] = field(default_factory=list)
    permissions: Dict[str, bool] = field(default_factory=lambda: {
        "send": True,
        "receive": True,
        "approve": False,
        "admin": False
    })
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    
    def get_balance(self, symbol: str) -> Optional[AssetBalance]:
        for b in self.balances:
            if b.symbol == symbol:
                return b
        return None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "account_id": self.account_id,
            "address": self.address,
            "chain": self.chain,
            "balances": [b.to_dict() for b in self.balances],
            "permissions": self.permissions,
            "created_at": self.created_at
        }


@runtime_checkable
class SignatureProvider(Protocol):
    """签名提供者协议"""
    def sign(self, tx_hash: str) -> str: ...
    def verify(self, tx_hash: str, signature: str) -> bool: ...


class MockSignatureProvider:
    """模拟签名提供者"""
    
    def sign(self, tx_hash: str) -> str:
        return f"sig_{hashlib.sha256(tx_hash.encode()).hexdigest()[:16]}"
    
    def verify(self, tx_hash: str, signature: str) -> bool:
        expected = self.sign(tx_hash)
        return signature == expected


class AssetCustody:
    """
    资产托管系统
    
    统一管理账户、余额、交易
    
    使用方式：
    ```python
    custody = AssetCustody()
    
    # 创建账户
    account = custody.create_account("user_001", "ethereum")
    
    # 添加余额
    custody.add_balance(account.account_id, "ETH", 1.5)
    
    # 查询余额
    balance = custody.get_balance(account.account_id, "ETH")
    
    # 创建交易
    tx = custody.create_transaction(account.account_id, to_address, "ETH", 0.1)
    
    # 模拟执行
    custody.simulate(tx.tx_id)
    
    # 签名
    custody.sign(tx.tx_id)
    
    # 提交
    custody.submit(tx.tx_id)
    ```
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self._accounts: Dict[str, Account] = {}
        self._transactions: Dict[str, Transaction] = {}
        self._signature_provider: SignatureProvider = self.config.get(
            "signature_provider", MockSignatureProvider()
        )
        self._history: List[Dict[str, Any]] = []
    
    def create_account(self, account_id: str, chain: str = "default") -> Account:
        address = f"0x{hashlib.sha256(f'{account_id}{chain}'.encode()).hexdigest()[:40]}"
        account = Account(
            account_id=account_id,
            address=address,
            chain=chain
        )
        self._accounts[account_id] = account
        self._record("account_created", {"account_id": account_id, "chain": chain})
        return account
    
    def get_account(self, account_id: str) -> Optional[Account]:
        return self._accounts.get(account_id)
    
    def add_balance(self, account_id: str, symbol: str, amount: float, 
                    asset_type: AssetType = AssetType.NATIVE) -> bool:
        account = self._accounts.get(account_id)
        if not account:
            return False
        
        existing = account.get_balance(symbol)
        if existing:
            existing.amount += amount
            existing.last_updated = datetime.now().isoformat()
        else:
            balance = AssetBalance(
                asset_type=asset_type,
                symbol=symbol,
                amount=amount,
                chain=account.chain
            )
            account.balances.append(balance)
        
        self._record("balance_added", {"account_id": account_id, "symbol": symbol, "amount": amount})
        return True
    
    def get_balance(self, account_id: str, symbol: str) -> Optional[AssetBalance]:
        account = self._accounts.get(account_id)
        if not account:
            return None
        return account.get_balance(symbol)
    
    def create_transaction(
        self,
        from_account_id: str,
        to_address: str,
        symbol: str,
        amount: float
    ) -> Optional[Transaction]:
        account = self._accounts.get(from_account_id)
        if not account:
            return None
        
        balance = account.get_balance(symbol)
        if not balance or balance.amount < amount:
            return None
        
        tx_id = f"tx_{hashlib.md5(f'{from_account_id}{to_address}{symbol}{amount}{datetime.now().isoformat()}'.encode()).hexdigest()[:8]}"
        
        tx = Transaction(
            tx_id=tx_id,
            from_address=account.address,
            to_address=to_address,
            asset=AssetBalance(
                asset_type=balance.asset_type,
                symbol=symbol,
                amount=amount,
                decimals=balance.decimals,
                chain=balance.chain
            )
        )
        
        self._transactions[tx_id] = tx
        self._record("transaction_created", {"tx_id": tx_id, "from": from_account_id, "to": to_address, "symbol": symbol, "amount": amount})
        return tx
    
    def simulate(self, tx_id: str) -> bool:
        tx = self._transactions.get(tx_id)
        if not tx:
            return False
        
        # 模拟 gas 估算
        tx.gas_estimate = 0.001 * (tx.asset.amount / 100)  # 简单估算
        tx.status = TransactionStatus.SIMULATED
        
        self._record("transaction_simulated", {"tx_id": tx_id, "gas_estimate": tx.gas_estimate})
        return True
    
    def sign(self, tx_id: str) -> bool:
        tx = self._transactions.get(tx_id)
        if not tx or tx.status != TransactionStatus.SIMULATED:
            return False
        
        tx_hash = f"hash_{hashlib.sha256(f'{tx.tx_id}{tx.from_address}{tx.to_address}'.encode()).hexdigest()[:32]}"
        tx.signature = self._signature_provider.sign(tx_hash)
        tx.tx_hash = tx_hash
        tx.status = TransactionStatus.SIGNED
        
        self._record("transaction_signed", {"tx_id": tx_id, "tx_hash": tx_hash})
        return True
    
    def submit(self, tx_id: str) -> bool:
        tx = self._transactions.get(tx_id)
        if not tx or tx.status != TransactionStatus.SIGNED:
            return False
        
        # 扣除余额
        account = next((a for a in self._accounts.values() if a.address == tx.from_address), None)
        if account:
            balance = account.get_balance(tx.asset.symbol)
            if balance:
                balance.amount -= tx.asset.amount
        
        tx.status = TransactionStatus.CONFIRMED
        tx.confirmed_at = datetime.now().isoformat()
        
        self._record("transaction_confirmed", {"tx_id": tx_id, "status": "confirmed"})
        return True
    
    def rollback(self, tx_id: str) -> bool:
        tx = self._transactions.get(tx_id)
        if not tx or tx.status not in [TransactionStatus.SUBMITTED, TransactionStatus.CONFIRMED]:
            return False
        
        # 恢复余额
        account = next((a for a in self._accounts.values() if a.address == tx.from_address), None)
        if account:
            balance = account.get_balance(tx.asset.symbol)
            if balance:
                balance.amount += tx.asset.amount
        
        tx.status = TransactionStatus.ROLLED_BACK
        
        self._record("transaction_rolled_back", {"tx_id": tx_id})
        return True
    
    def get_transaction(self, tx_id: str) -> Optional[Transaction]:
        return self._transactions.get(tx_id)
    
    def get_history(self, account_id: str = None, limit: int = 100) -> List[Dict[str, Any]]:
        history = self._history
        if account_id:
            history = [h for h in history if account_id in str(h)]
        return history[-limit:]
    
    def _record(self, event: str, data: Dict[str, Any]):
        self._history.append({
            "event": event,
            "data": data,
            "timestamp": datetime.now().isoformat()
        })
    
    def stats(self) -> Dict[str, Any]:
        return {
            "accounts": len(self._accounts),
            "transactions": len(self._transactions),
            "confirmed_transactions": sum(1 for tx in self._transactions.values() if tx.status == TransactionStatus.CONFIRMED),
            "history_records": len(self._history)
        }

"""Blockchain Asset Integrity Ledger: Simple Proof-of-Work Blockchain
References:
- Materi 8: Fungsi Hash Satu-Arah (SHA-256, Avalanche Effect, Collision Resistance)
- Specification: Critical assets secured using simple blockchain technology
Features:
- Cryptographic hash-linked immutable blocks
- Proof-of-Work (PoW) consensus mechanism with adjustable difficulty
- Real-time tamper detection and chain integrity verification
- Educational tampering injection utility to demonstrate fail-closed alerts
"""

import time
import json
import hashlib
from pathlib import Path

try:
    from config import BLOCKCHAIN_PATH, DEFAULT_POW_DIFFICULTY, GENESIS_PREV_HASH
except ImportError:
    BLOCKCHAIN_PATH = Path("data/blockchain_ledger.json")
    DEFAULT_POW_DIFFICULTY = 3
    GENESIS_PREV_HASH = "0" * 64


class Transaction:
    """Represents a transfer or custody record of critical digital assets."""

    def __init__(self, sender: str, recipient: str, asset: str, amount: float, memo: str = ""):
        self.sender = sender
        self.recipient = recipient
        self.asset = asset
        self.amount = float(amount)
        self.memo = memo
        self.timestamp = time.time()
        self.tx_id = self._calculate_tx_id()

    def _calculate_tx_id(self) -> str:
        payload = f"{self.sender}:{self.recipient}:{self.asset}:{self.amount}:{self.memo}:{self.timestamp}"
        return hashlib.sha256(payload.encode("utf-8")).hexdigest()

    def to_dict(self) -> dict:
        return {
            "tx_id": self.tx_id,
            "sender": self.sender,
            "recipient": self.recipient,
            "asset": self.asset,
            "amount": self.amount,
            "memo": self.memo,
            "timestamp": self.timestamp,
        }

    @classmethod
    def from_dict(cls, data: dict):
        tx = cls(
            sender=data["sender"],
            recipient=data["recipient"],
            asset=data["asset"],
            amount=data["amount"],
            memo=data.get("memo", ""),
        )
        tx.timestamp = data.get("timestamp", tx.timestamp)
        tx.tx_id = data.get("tx_id", tx._calculate_tx_id())
        return tx


class Block:
    """Represents a cryptographic block linked via previous SHA-256 hash."""

    def __init__(
        self,
        index: int,
        transactions: list[dict],
        previous_hash: str,
        timestamp: float | None = None,
        nonce: int = 0,
        current_hash: str | None = None,
    ):
        self.index = index
        self.timestamp = timestamp if timestamp is not None else time.time()
        self.transactions = transactions
        self.previous_hash = previous_hash
        self.nonce = nonce
        self.hash = current_hash if current_hash is not None else self.calculate_hash()

    def calculate_hash(self) -> str:
        """Computes SHA-256 hash of block header & payload."""
        block_string = json.dumps(
            {
                "index": self.index,
                "timestamp": self.timestamp,
                "transactions": self.transactions,
                "previous_hash": self.previous_hash,
                "nonce": self.nonce,
            },
            sort_keys=True,
        )
        return hashlib.sha256(block_string.encode("utf-8")).hexdigest()

    def mine_block(self, difficulty: int):
        """Proof-of-Work: Find nonce such that hash starts with N zeros."""
        target_prefix = "0" * difficulty
        while not self.hash.startswith(target_prefix):
            self.nonce += 1
            self.hash = self.calculate_hash()

    def to_dict(self) -> dict:
        return {
            "index": self.index,
            "timestamp": self.timestamp,
            "transactions": self.transactions,
            "previous_hash": self.previous_hash,
            "nonce": self.nonce,
            "hash": self.hash,
        }

    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            index=data["index"],
            transactions=data["transactions"],
            previous_hash=data["previous_hash"],
            timestamp=data["timestamp"],
            nonce=data["nonce"],
            current_hash=data["hash"],
        )


class Blockchain:
    """Manages the distributed ledger, pending transactions, and validation."""

    def __init__(self, difficulty: int = DEFAULT_POW_DIFFICULTY, storage_path: Path = BLOCKCHAIN_PATH):
        self.difficulty = difficulty
        self.storage_path = storage_path
        self.pending_transactions: list[Transaction] = []
        self.chain: list[Block] = []

        if self.storage_path.exists():
            self.load_from_file()
        else:
            self.create_genesis_block()
            self.save_to_file()

    def create_genesis_block(self):
        """Creates the initial immutable root block (Genesis Block)."""
        genesis_tx = Transaction(
            sender="0000_GENESIS_ROOT",
            recipient="SENTIX_SYSTEM_VAULT",
            asset="INITIAL_RESERVE",
            amount=1_000_000.0,
            memo="Sentix Digital Vault Genesis Ledger Initialization",
        )
        genesis_block = Block(
            index=0,
            transactions=[genesis_tx.to_dict()],
            previous_hash=GENESIS_PREV_HASH,
            timestamp=1700000000.0,
            nonce=0,
        )
        genesis_block.mine_block(self.difficulty)
        self.chain = [genesis_block]

    def get_latest_block(self) -> Block:
        return self.chain[-1]

    def add_transaction(self, sender: str, recipient: str, asset: str, amount: float, memo: str = "") -> Transaction:
        """Queues a transaction for the next mined block."""
        if amount <= 0:
            raise ValueError("Transaction amount must be strictly positive.")
        tx = Transaction(sender, recipient, asset, amount, memo)
        self.pending_transactions.append(tx)
        return tx

    def mine_pending_transactions(self, miner_address: str = "VAULT_AUDITOR_NODE") -> Block:
        """Mines pending transactions into a new block via Proof-of-Work."""
        if not self.pending_transactions:
            raise ValueError("No pending transactions to mine.")

        # Reward transaction (Proof of Authority / Mining Incentive)
        reward_tx = Transaction(
            sender="NETWORK_REWARD",
            recipient=miner_address,
            asset="SNTX_GAS",
            amount=10.0,
            memo="Block Mining Gas Reward",
        )
        tx_list = [tx.to_dict() for tx in self.pending_transactions] + [reward_tx.to_dict()]

        new_block = Block(
            index=len(self.chain),
            transactions=tx_list,
            previous_hash=self.get_latest_block().hash,
        )
        new_block.mine_block(self.difficulty)
        self.chain.append(new_block)

        self.pending_transactions = []
        self.save_to_file()
        return new_block

    def is_chain_valid(self) -> tuple[bool, str]:
        """Validates all blocks in chain:
        1. Current hash == Recalculated SHA-256 hash (tamper check)
        2. Block[i].previous_hash == Block[i-1].hash (link check)
        3. PoW target difficulty fulfilled
        """
        target_prefix = "0" * self.difficulty

        for i in range(1, len(self.chain)):
            current = self.chain[i]
            prev = self.chain[i - 1]

            # Link check
            if current.previous_hash != prev.hash:
                return False, f"Broken link at Block #{current.index}: previous_hash does not match hash of Block #{prev.index}."

            # Recalculate hash check
            recalculated = current.calculate_hash()
            if current.hash != recalculated:
                return False, f"Tampered data detected in Block #{current.index}! Recorded hash ({current.hash[:16]}...) != recalculated ({recalculated[:16]}...)."

            # PoW check
            if not current.hash.startswith(target_prefix):
                return False, f"Block #{current.index} fails Proof-of-Work difficulty target."

        return True, f"Blockchain integrity 100% verified across all {len(self.chain)} blocks."

    def tamper_block_for_demo(self, block_index: int, new_amount: float) -> bool:
        """Educational demonstration helper: Mutates a transaction in a past block
        without re-mining, causing immediate chain validation failure.
        """
        if block_index < 0 or block_index >= len(self.chain):
            raise IndexError("Block index out of bounds.")

        block = self.chain[block_index]
        if block.transactions:
            block.transactions[0]["amount"] = new_amount
            # Intentionally do NOT update block.hash to simulate unauthorized manipulation
            self.save_to_file()
            return True
        return False

    def save_to_file(self):
        """Persists chain to JSON."""
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)
        data = {
            "difficulty": self.difficulty,
            "chain": [b.to_dict() for b in self.chain],
        }
        with open(self.storage_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

    def load_from_file(self):
        """Loads chain from JSON."""
        with open(self.storage_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        self.difficulty = data.get("difficulty", self.difficulty)
        self.chain = [Block.from_dict(b) for b in data["chain"]]

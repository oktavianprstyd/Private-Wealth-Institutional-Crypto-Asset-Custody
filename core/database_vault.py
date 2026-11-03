"""Database Encryption Vault: SQLite with Field-Level AES-256-GCM
References:
- Materi 6 & 7: Modern Block Cipher Modes (Authenticated Encryption)
- Specification: Important/sensitive messages must be encrypted in the database
"""

import os
import sqlite3
import base64
import hashlib
from datetime import datetime, timezone
from pathlib import Path
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

try:
    from config import DATABASE_PATH
except ImportError:
    DATABASE_PATH = Path("data/sentix_vault.db")


def get_db_connection(db_path: Path = DATABASE_PATH) -> sqlite3.Connection:
    """Creates directory if needed and returns SQLite connection."""
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    return conn


def init_database(db_path: Path = DATABASE_PATH):
    """Initializes tables for encrypted vault storage."""
    conn = get_db_connection(db_path)
    try:
        with conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS vault_records (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    account_id TEXT NOT NULL,
                    title TEXT NOT NULL,
                    category TEXT NOT NULL,
                    ciphertext_base64 TEXT NOT NULL,
                    iv_hex TEXT NOT NULL,
                    tag_hex TEXT NOT NULL,
                    created_at TEXT NOT NULL
                )
            """)
    finally:
        conn.close()


def _derive_gcm_key(master_key_passphrase: str) -> bytes:
    """Derives a 256-bit (32 bytes) key for AES-GCM via SHA-256."""
    return hashlib.sha256(master_key_passphrase.encode("utf-8")).digest()


def insert_secret(
    title: str,
    category: str,
    plaintext_secret: str,
    master_key: str,
    account_id: str = "VAULT-HQ-01",
    db_path: Path = DATABASE_PATH,
) -> int:
    """Encrypts plaintext_secret using AES-256-GCM and inserts record into database."""
    init_database(db_path)
    
    key = _derive_gcm_key(master_key)
    aesgcm = AESGCM(key)
    
    # 12-byte standard GCM nonce
    nonce = os.urandom(12)
    associated_data = f"{account_id}:{category}:{title}".encode("utf-8")
    
    # AESGCM encrypt produces ciphertext + 16-byte tag appended
    encrypted_blob = aesgcm.encrypt(nonce, plaintext_secret.encode("utf-8"), associated_data)
    ciphertext = encrypted_blob[:-16]
    tag = encrypted_blob[-16:]
    
    now_str = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    
    conn = get_db_connection(db_path)
    try:
        with conn:
            cursor = conn.execute(
                """
                INSERT INTO vault_records (
                    account_id, title, category, ciphertext_base64, iv_hex, tag_hex, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    account_id,
                    title,
                    category,
                    base64.b64encode(ciphertext).decode("utf-8"),
                    nonce.hex(),
                    tag.hex(),
                    now_str,
                ),
            )
            return cursor.lastrowid
    finally:
        conn.close()


def get_raw_database_records(db_path: Path = DATABASE_PATH) -> list[dict]:
    """Returns raw database records without decrypting.
    Used for academic demonstration of on-disk encrypted state.
    """
    init_database(db_path)
    conn = get_db_connection(db_path)
    try:
        rows = conn.execute(
            "SELECT id, account_id, title, category, ciphertext_base64, iv_hex, tag_hex, created_at FROM vault_records ORDER BY id DESC"
        ).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


def get_all_secrets_decrypted(master_key: str, db_path: Path = DATABASE_PATH) -> list[dict]:
    """Retrieves all records and decrypts the sensitive payload using master_key.
    If decryption fails (wrong key or tampering), marks status as TAMPERED/ERROR.
    """
    init_database(db_path)
    key = _derive_gcm_key(master_key)
    aesgcm = AESGCM(key)
    
    raw_records = get_raw_database_records(db_path)
    decrypted_list = []
    
    for r in raw_records:
        item = {
            "id": r["id"],
            "account_id": r["account_id"],
            "title": r["title"],
            "category": r["category"],
            "created_at": r["created_at"],
            "decryption_status": "SUCCESS",
            "decrypted_secret": "",
            "raw_ciphertext": r["ciphertext_base64"],
        }
        try:
            nonce = bytes.fromhex(r["iv_hex"])
            ciphertext = base64.b64decode(r["ciphertext_base64"])
            tag = bytes.fromhex(r["tag_hex"])
            blob = ciphertext + tag
            associated_data = f"{r['account_id']}:{r['category']}:{r['title']}".encode("utf-8")
            
            plaintext_bytes = aesgcm.decrypt(nonce, blob, associated_data)
            item["decrypted_secret"] = plaintext_bytes.decode("utf-8")
        except Exception as e:
            item["decryption_status"] = f"FAILED: {str(e)}"
            item["decrypted_secret"] = "[DECRYPTION FAILED - INVALID KEY OR TAMPERED DATA]"
            
        decrypted_list.append(item)
        
    return decrypted_list


def delete_record(record_id: int, db_path: Path = DATABASE_PATH):
    """Deletes record by ID."""
    conn = get_db_connection(db_path)
    try:
        with conn:
            conn.execute("DELETE FROM vault_records WHERE id = ?", (record_id,))
    finally:
        conn.close()

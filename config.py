"""Aegis Cold Custody - Global Configuration & Constants
Centralizes paths, cryptographic parameters, and system defaults.
"""

from pathlib import Path

# Paths
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
ASSETS_DIR = BASE_DIR / "assets"
DATABASE_PATH = DATA_DIR / "aegis_vault.db"
BLOCKCHAIN_PATH = DATA_DIR / "blockchain_ledger.json"
MASTER_FACE_PATH = DATA_DIR / "master_face.json"
DONGLE_FILENAME = "aegis_dongle.key"

# Cryptographic Constants (Aligned with Lecture Material)
PBKDF2_ITERATIONS = 100_000
HASH_ALGORITHM = "SHA-256"  # Materi 8
AES_KEY_SIZE_BITS = 256     # Materi 6 & 7
AES_BLOCK_SIZE_BYTES = 16   # 128-bit block size
RC4_S_BOX_SIZE = 256        # Materi 7 (KSA & PRGA 256 bytes)

# Blockchain Constants
DEFAULT_POW_DIFFICULTY = 3  # Leading zeros: '000'
GENESIS_PREV_HASH = "0" * 64

# Steganography Constants
STEGO_DELIMITER = "##AEGIS_END##"

# Biometrics
BIOMETRIC_COSINE_THRESHOLD = 0.32  # Strict crypto-grade matching
EAR_BLINK_THRESHOLD = 0.20         # Eye Aspect Ratio threshold for liveness

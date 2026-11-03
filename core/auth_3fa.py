"""Three-Factor Authentication (3FA) Engine: Hardware Dongle + Biometric Face + Crypto Password
References:
- Slide Specification: Dongle USB mandatory to unlock application + Biometric login + Crypto Password (Hash / AES)
- Materi 8: Fungsi Hash Satu-Arah (Salted PBKDF2-HMAC-SHA256)
"""

import os
import json
import hashlib
import hmac
from pathlib import Path
from PIL import Image

try:
    from config import DATA_DIR, DONGLE_FILENAME, MASTER_FACE_PATH, PBKDF2_ITERATIONS
except ImportError:
    DATA_DIR = Path("data")
    DONGLE_FILENAME = "sentix_dongle.key"
    MASTER_FACE_PATH = Path("data/master_face.json")
    PBKDF2_ITERATIONS = 100_000

AUTH_CONFIG_PATH = DATA_DIR / "auth_config.json"
SYSTEM_VAULT_SALT = b"SENTIX_SYSTEM_CORE_SALT_2026_UPN"


# =====================================================================
# FACTOR 1: HARDWARE USB DONGLE
# =====================================================================

class DongleVerifier:
    """Manages Physical / Virtual USB Hardware Dongle.
    Validates presence of 'sentix_dongle.key' with cryptographically verified HMAC signature.
    """

    @staticmethod
    def generate_dongle_token(vault_id: str = "VAULT-ALPHA-01") -> dict:
        """Generates a cryptographic token payload signed with HMAC-SHA256."""
        payload = {
            "vault_id": vault_id,
            "issued_to": "Oktavian Prasetya Adi (123240135)",
            "institution": "UPN Veteran Yogyakarta - Informatika IF-B",
            "device_role": "HARDWARE_SECURITY_DONGLE_TIER_1",
        }
        raw_msg = json.dumps(payload, sort_keys=True).encode("utf-8")
        signature = hmac.new(SYSTEM_VAULT_SALT, raw_msg, hashlib.sha256).hexdigest()
        return {"payload": payload, "signature": signature}

    @classmethod
    def write_dongle_to_path(cls, target_dir: Path | str, vault_id: str = "VAULT-ALPHA-01") -> Path:
        """Writes the cryptographic token to the root of a target drive or directory."""
        target_path = Path(target_dir) / DONGLE_FILENAME
        target_path.parent.mkdir(parents=True, exist_ok=True)
        token_data = cls.generate_dongle_token(vault_id)
        with open(target_path, "w", encoding="utf-8") as f:
            json.dump(token_data, f, indent=2)
        return target_path

    @classmethod
    def verify_dongle_path(cls, dongle_file_path: Path | str) -> tuple[bool, str, dict | None]:
        """Verifies if the specified dongle key file exists and has an authentic HMAC signature."""
        path = Path(dongle_file_path)
        if not path.exists():
            return False, f"Hardware Dongle not found at path: {path}", None

        try:
            with open(path, "r", encoding="utf-8") as f:
                token_data = json.load(f)

            payload = token_data.get("payload", {})
            signature = token_data.get("signature", "")
            raw_msg = json.dumps(payload, sort_keys=True).encode("utf-8")
            expected_sig = hmac.new(SYSTEM_VAULT_SALT, raw_msg, hashlib.sha256).hexdigest()

            if hmac.compare_digest(signature, expected_sig):
                return True, "Hardware Dongle Verified (Valid HMAC-SHA256 Token)", payload
            else:
                return False, "Hardware Dongle Rejected: Signature Mismatch (Counterfeit/Tampered Dongle)", None
        except Exception as e:
            return False, f"Dongle Read Error: {str(e)}", None

    @classmethod
    def scan_possible_dongle_locations(cls) -> list[Path]:
        """Scans for potential USB drives or default virtual dongle directories."""
        candidates = []

        # 1. Check default local vault dongle folder
        default_local = DATA_DIR / "dongle" / DONGLE_FILENAME
        if default_local.exists():
            candidates.append(default_local)

        # 2. Windows drive letters (D:, E:, F:, G:, H:)
        import string

        for letter in string.ascii_uppercase[2:10]:  # C: to J:
            drive_root = Path(f"{letter}:/")
            if drive_root.exists():
                candidate = drive_root / DONGLE_FILENAME
                if candidate.exists():
                    candidates.append(candidate)

        # 3. Linux /media or /mnt locations
        for base in ["/media", "/mnt", "/Volumes"]:
            base_p = Path(base)
            if base_p.exists():
                for sub in base_p.glob("*"):
                    candidate = sub / DONGLE_FILENAME
                    if candidate.exists():
                        candidates.append(candidate)

        return candidates


# =====================================================================
# FACTOR 2: BIOMETRIC FACE AUTHENTICATION
# =====================================================================

class BiometricVerifier:
    """Manages Facial Biometric Verification and Enrollment.
    Extracts normalized facial feature vectors and calculates Cosine Distance.
    """

    @staticmethod
    def _extract_simple_embedding(image: Image.Image) -> list[float]:
        """Extracts normalized spatial-luminance feature vector (128 dimensions)
        from grayscale resized facial image. Fast, cross-platform, zero heavy GPU dependencies.
        """
        img_gray = image.convert("L").resize((32, 32))
        raw_pixels = list(img_gray.tobytes())

        # Calculate 128-dimensional spatial block features
        blocks = []
        for i in range(0, 1024, 8):
            chunk = raw_pixels[i : i + 8]
            blocks.append(sum(chunk) / len(chunk))

        # Normalize vector (L2 norm)
        norm = (sum(x ** 2 for x in blocks) ** 0.5) or 1.0
        return [round(x / norm, 6) for x in blocks]

    @classmethod
    def enroll_face(cls, image: Image.Image, user_id: str = "oktavian") -> Path:
        """Enrolls user face by saving normalized biometric embedding to disk."""
        MASTER_FACE_PATH.parent.mkdir(parents=True, exist_ok=True)
        embedding = cls._extract_simple_embedding(image)
        record = {
            "user_id": user_id,
            "dimension": len(embedding),
            "embedding": embedding,
            "created_at": str(Path(__file__).stat().st_mtime),
        }
        with open(MASTER_FACE_PATH, "w", encoding="utf-8") as f:
            json.dump(record, f, indent=2)
        return MASTER_FACE_PATH

    @classmethod
    def verify_face(cls, probe_image: Image.Image, threshold: float = 0.32) -> tuple[bool, float, str]:
        """Compares probe_image against stored master face embedding using Cosine Distance:
        Distance = 1 - (A · B) / (||A|| * ||B||)
        If Distance <= threshold (0.32), match is approved.
        """
        if not MASTER_FACE_PATH.exists():
            return False, 1.0, "Master face not enrolled yet. Please perform initial enrollment."

        with open(MASTER_FACE_PATH, "r", encoding="utf-8") as f:
            record = json.load(f)
        master_emb = record["embedding"]
        probe_emb = cls._extract_simple_embedding(probe_image)

        # Dot product of unit-normalized vectors
        dot_product = sum(a * b for a, b in zip(master_emb, probe_emb))
        cosine_distance = max(0.0, 1.0 - dot_product)

        if cosine_distance <= threshold:
            confidence = round((1.0 - cosine_distance) * 100, 2)
            return True, cosine_distance, f"Biometric Match Verified! (Confidence: {confidence}%, Dist: {cosine_distance:.4f})"
        else:
            return False, cosine_distance, f"Biometric Rejected: Face Mismatch (Dist: {cosine_distance:.4f} > {threshold})"


# =====================================================================
# FACTOR 3: PASSWORD HASHING & KEY DERIVATION
# =====================================================================

class PasswordVerifier:
    """Manages Master Password verification using PBKDF2-HMAC-SHA256 (Materi 8)
    and derives the cryptographic Master Session Key.
    """

    @staticmethod
    def hash_password(password: str, salt: bytes | None = None) -> tuple[str, str]:
        """Generates PBKDF2-HMAC-SHA256 hash.
        Returns: (hash_hex, salt_hex)
        """
        if salt is None:
            salt = os.urandom(16)
        pwd_bytes = password.encode("utf-8")
        derived_hash = hashlib.pbkdf2_hmac("sha256", pwd_bytes, salt, PBKDF2_ITERATIONS, dklen=32)
        return derived_hash.hex(), salt.hex()

    @classmethod
    def init_master_password(cls, password: str = "Sentix@2026!"):
        """Sets or resets the master password."""
        AUTH_CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
        hash_hex, salt_hex = cls.hash_password(password)
        data = {
            "username": "sentix_executive",
            "password_hash": hash_hex,
            "salt_hex": salt_hex,
            "iterations": PBKDF2_ITERATIONS,
            "algorithm": "PBKDF2-HMAC-SHA256",
        }
        with open(AUTH_CONFIG_PATH, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

    @classmethod
    def verify_password(cls, password: str) -> tuple[bool, str, str | None]:
        """Verifies password against stored hash.
        Returns: (is_valid, message, derived_master_key_hex)
        """
        if not AUTH_CONFIG_PATH.exists():
            cls.init_master_password()

        with open(AUTH_CONFIG_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)

        stored_hash = data["password_hash"]
        salt = bytes.fromhex(data["salt_hex"])

        computed_hash = hashlib.pbkdf2_hmac(
            "sha256", password.encode("utf-8"), salt, PBKDF2_ITERATIONS, dklen=32
        ).hex()

        if hmac.compare_digest(stored_hash, computed_hash):
            master_key_hex = hashlib.sha256(password.encode("utf-8") + salt).hexdigest()
            return True, "Password Authentication Successful", master_key_hex
        else:
            return False, "Invalid Master Password", None

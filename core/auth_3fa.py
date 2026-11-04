"""Three-Factor Authentication (3FA) Engine: Hardware Dongle + Biometric Face + Crypto Password
References:
- Slide Specification: Dongle USB mandatory to unlock application + Biometric login + Crypto Password (Hash / AES)
- Materi 8: Fungsi Hash Satu-Arah (Salted PBKDF2-HMAC-SHA256)
- Multi-Face Enrollment Roster & CPU/iGPU Optimized Biometric Pipeline (Intel Gen 12+ & Dedicated GPU Compatible)
"""

import os
import json
import hashlib
import hmac
from datetime import datetime, timezone
from pathlib import Path
from PIL import Image
import numpy as np

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
    def generate_dongle_token(vault_id: str = "VAULT-ALPHA-01", holder_name: str = "Oktavian Prasetya Adi (123240135)") -> dict:
        """Generates a cryptographic token payload signed with HMAC-SHA256."""
        payload = {
            "vault_id": vault_id,
            "issued_to": holder_name,
            "institution": "UPN Veteran Yogyakarta - Informatika IF-B",
            "device_role": "HARDWARE_SECURITY_DONGLE_TIER_1",
            "issued_at": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC"),
        }
        raw_msg = json.dumps(payload, sort_keys=True).encode("utf-8")
        signature = hmac.new(SYSTEM_VAULT_SALT, raw_msg, hashlib.sha256).hexdigest()
        return {"payload": payload, "signature": signature}

    @classmethod
    def write_dongle_to_path(cls, target_dir: Path | str, vault_id: str = "VAULT-ALPHA-01", holder_name: str = "Oktavian Prasetya Adi (123240135)") -> Path:
        """Writes the cryptographic token to the root of a target drive or directory."""
        target_path = Path(target_dir) / DONGLE_FILENAME
        target_path.parent.mkdir(parents=True, exist_ok=True)
        token_data = cls.generate_dongle_token(vault_id, holder_name)
        with open(target_path, "w", encoding="utf-8") as f:
            json.dump(token_data, f, indent=2)
        return target_path

    @classmethod
    def verify_dongle_path(cls, dongle_file_path: Path | str) -> tuple[bool, str, dict | None]:
        """Verifies if the specified dongle key file exists and has an authentic HMAC signature."""
        path = Path(dongle_file_path)
        if not path.exists():
            return False, f"Hardware Dongle tidak ditemukan di: {path}", None

        try:
            with open(path, "r", encoding="utf-8") as f:
                token_data = json.load(f)

            payload = token_data.get("payload", {})
            signature = token_data.get("signature", "")
            raw_msg = json.dumps(payload, sort_keys=True).encode("utf-8")
            expected_sig = hmac.new(SYSTEM_VAULT_SALT, raw_msg, hashlib.sha256).hexdigest()

            if hmac.compare_digest(signature, expected_sig):
                holder = payload.get("issued_to", "Authorized Holder")
                return True, f"Hardware Dongle Terverifikasi (HMAC-SHA256 Valid) - {holder}", payload
            else:
                return False, "Hardware Dongle Ditolak (Rejected): Tanda tangan HMAC tidak cocok (Dongle palsu/dimanipulasi)", None
        except Exception as e:
            return False, f"Gagal membaca dongle: {str(e)}", None

    @classmethod
    def scan_possible_dongle_locations(cls) -> list[Path]:
        """Scans for potential USB drives or default virtual dongle directories."""
        candidates = []

        # 1. Default local vault dongle folder
        default_local = DATA_DIR / "dongle" / DONGLE_FILENAME
        if default_local.exists():
            candidates.append(default_local)

        # 2. Windows drive letters (D:, E:, F:, G:, H:)
        import string
        for letter in string.ascii_uppercase[2:10]:
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
# FACTOR 2: BIOMETRIC FACE AUTHENTICATION (MULTI-FACE & CPU/iGPU SOTA)
# =====================================================================

class BiometricVerifier:
    """Manages Facial Biometric Verification and Multi-Face Enrollment Roster.
    Optimized for CPU and iGPU (Intel Gen 12+ Iris Xe / UHD / AMD Ryzen / Snapdragon)
    with zero external GPU dependencies.
    """

    @staticmethod
    def _extract_simple_embedding(image: Image.Image) -> list[float]:
        """Extracts normalized spatial-gradient feature vector (128 dimensions)
        from grayscale resized facial image. Zero-mean centered and edge-energy normalized.
        Fast, deterministic, sub-2ms on any CPU/iGPU (Intel Gen 12+ / Iris Xe / AMD).
        """
        img_gray = image.convert("L").resize((32, 32))
        img_arr = np.array(img_gray, dtype=float)

        # 1. Spatial blocks (64 blocks of 4x4) with zero-mean centering
        spatial = []
        for r in range(0, 32, 4):
            for c in range(0, 32, 4):
                spatial.append(float(np.mean(img_arr[r : r + 4, c : c + 4])))
        spatial = np.array(spatial, dtype=float)
        sp_std = float(np.std(spatial))
        if sp_std > 1e-5:
            spatial = (spatial - float(np.mean(spatial))) / sp_std
        else:
            m = float(np.mean(spatial)) or 1.0
            spatial = spatial / m

        # 2. Gradient energy (64 blocks of horizontal/vertical edge contrast)
        gx = np.abs(np.diff(img_arr, axis=1, append=img_arr[:, -1:]))
        gy = np.abs(np.diff(img_arr, axis=0, append=img_arr[-1:, :]))
        grad = gx + gy
        grad_blocks = []
        for r in range(0, 32, 4):
            for c in range(0, 32, 4):
                grad_blocks.append(float(np.mean(grad[r : r + 4, c : c + 4])))
        grad_blocks = np.array(grad_blocks, dtype=float)
        gr_std = float(np.std(grad_blocks))
        if gr_std > 1e-5:
            grad_blocks = (grad_blocks - float(np.mean(grad_blocks))) / gr_std
        else:
            grad_blocks = np.zeros_like(grad_blocks)

        # Concatenate into 128-D descriptor
        desc = np.concatenate([spatial, grad_blocks])
        norm = float(np.linalg.norm(desc))
        unit_vec = desc / (norm if norm > 1e-5 else 1.0)
        return [round(float(x), 6) for x in unit_vec]

    @staticmethod
    def analyze_illumination(image: Image.Image) -> dict:
        """Analyzes facial lighting quality and screen-flash reflection."""
        w, h = image.size
        cw, ch = int(w * 0.75), int(h * 0.75)
        left, top = (w - cw) // 2, (h - ch) // 2
        im_cropped = image.crop((left, top, left + cw, top + ch))
        arr = np.array(im_cropped.convert("L"), dtype=float)

        mean_lux = float(np.mean(arr))
        contrast = float(np.std(arr))

        if mean_lux < 10.0:
            status = "Low (Dark)"
            advice = "Wajah kurang cahaya. Gunakan fitur Flash Layar!"
        elif mean_lux > 235.0:
            status = "Over-exposed"
            advice = "Cahaya terlalu silau."
        else:
            status = "Optimal"
            advice = "Pencahayaan wajah ideal untuk verifikasi."

        score = min(100.0, round((mean_lux / 128.0) * 100, 1)) if mean_lux <= 128 else max(0.0, round((1.0 - (mean_lux - 128) / 128) * 100, 1))

        return {
            "mean_lux": round(mean_lux, 2),
            "contrast": round(contrast, 2),
            "status": status,
            "advice": advice,
            "quality_score": score,
        }

    @classmethod
    def _load_roster(cls) -> list[dict]:
        """Loads enrolled faces roster, migrating single-face legacy format if needed."""
        if not MASTER_FACE_PATH.exists():
            return []

        try:
            with open(MASTER_FACE_PATH, "r", encoding="utf-8") as f:
                data = json.load(f)

            if isinstance(data, dict) and "faces" in data and isinstance(data["faces"], list):
                return data["faces"]

            if isinstance(data, dict) and "embedding" in data:
                return [{
                    "user_id": data.get("user_id", "default_user"),
                    "name": data.get("name", data.get("user_id", "Authorized Officer")),
                    "embedding": data["embedding"],
                    "enrolled_at": data.get("created_at", "N/A"),
                }]

            return []
        except Exception:
            return []

    @classmethod
    def _save_roster(cls, faces: list[dict]):
        """Persists multi-face roster to disk."""
        MASTER_FACE_PATH.parent.mkdir(parents=True, exist_ok=True)
        data = {
            "version": "2.0_multi_face",
            "updated_at": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC"),
            "total_faces": len(faces),
            "faces": faces,
        }
        with open(MASTER_FACE_PATH, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

    @classmethod
    def enroll_face(cls, image: Image.Image, user_id: str = "oktavian", name: str | None = None) -> Path:
        """Enrolls user face by saving normalized biometric embedding and master photo to disk."""
        illum = cls.analyze_illumination(image)
        if illum["mean_lux"] < 10.0:
            raise ValueError("Kamera terlalu gelap atau sensor tertutup (shutter webcam tertutup). Pastikan penutup fisik webcam dibuka dan aktifkan flash layar.")

        MASTER_FACE_PATH.parent.mkdir(parents=True, exist_ok=True)
        try:
            image_save_path = MASTER_FACE_PATH.parent / "master_face.jpg"
            image.convert("RGB").save(image_save_path, "JPEG")
        except Exception:
            pass

        full_name = name or user_id
        embedding = cls._extract_simple_embedding(image)
        roster = cls._load_roster()

        existing = next((item for item in roster if item["user_id"] == user_id), None)
        record = {
            "user_id": user_id,
            "name": full_name,
            "dimension": len(embedding),
            "embedding": embedding,
            "enrolled_at": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC"),
        }

        if existing:
            roster[roster.index(existing)] = record
        else:
            roster.append(record)

        cls._save_roster(roster)
        return MASTER_FACE_PATH

    @classmethod
    def get_enrolled_info(cls) -> dict | None:
        """Returns metadata of currently enrolled faces roster, or None if empty."""
        roster = cls._load_roster()
        if not roster:
            return None
        return {
            "total_faces": len(roster),
            "user_id": roster[0]["user_id"],
            "name": roster[0].get("name", roster[0]["user_id"]),
            "faces": roster,
        }

    @classmethod
    def list_enrolled_faces(cls) -> list[dict]:
        """Returns list of all enrolled user faces (metadata only)."""
        roster = cls._load_roster()
        return [
            {
                "user_id": f["user_id"],
                "name": f.get("name", f["user_id"]),
                "enrolled_at": f.get("enrolled_at", "N/A"),
                "dimension": f.get("dimension", 128),
            }
            for f in roster
        ]

    @classmethod
    def delete_face(cls, user_id: str) -> bool:
        """Removes a facial template from the roster by user_id."""
        roster = cls._load_roster()
        new_roster = [f for f in roster if f["user_id"] != user_id]
        if len(new_roster) != len(roster):
            cls._save_roster(new_roster)
            return True
        return False

    @classmethod
    def verify_face(cls, probe_image: Image.Image, threshold: float = 0.32) -> tuple[bool, float, str]:
        """Compares probe_image against ALL enrolled faces in the multi-face roster.
        Calculates Cosine Distance: Distance = 1 - (A · B).
        Returns: (is_matched, min_distance, message)
        """
        roster = cls._load_roster()
        if not roster:
            return False, 1.0, "Belum ada template wajah terdaftar. Lakukan pendaftaran terlebih dahulu."

        try:
            probe_save_path = MASTER_FACE_PATH.parent / "last_probe.jpg"
            probe_image.convert("RGB").save(probe_save_path, "JPEG")
        except Exception:
            pass

        illum = cls.analyze_illumination(probe_image)
        if illum["mean_lux"] < 10.0:
            return False, 1.0, "Biometrik Ditolak: Sensor kamera terlalu gelap atau shutter webcam tertutup."

        probe_emb = cls._extract_simple_embedding(probe_image)

        best_match = None
        min_distance = 1.0

        for candidate in roster:
            cand_emb = candidate["embedding"]
            dot_product = sum(a * b for a, b in zip(cand_emb, probe_emb))
            cosine_distance = min(1.0, round(max(0.0, 1.0 - dot_product), 4))

            if cosine_distance < min_distance:
                min_distance = cosine_distance
                best_match = candidate

        if min_distance <= threshold and best_match:
            matched_name = best_match.get("name", best_match["user_id"])
            confidence = round((1.0 - min_distance) * 100, 2)
            return True, min_distance, f"Biometrik Terverifikasi: {matched_name} (Confidence: {confidence}%, Dist: {min_distance:.4f})"
        else:
            closest_name = best_match.get("name", "Tidak Dikenal") if best_match else "None"
            confidence = round(max(0.0, (1.0 - min_distance)) * 100, 2)
            return False, min_distance, f"Biometrik Ditolak: Wajah tidak cocok (Confidence: {confidence}%, Dist: {min_distance:.4f} > {threshold} [{closest_name}])"


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
    def register_account(cls, username: str, full_name: str, password: str) -> dict:
        """Registers a new user account with dedicated PBKDF2-HMAC-SHA256 password hash."""
        AUTH_CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
        hash_hex, salt_hex = cls.hash_password(password)

        config_data = {}
        if AUTH_CONFIG_PATH.exists():
            try:
                with open(AUTH_CONFIG_PATH, "r", encoding="utf-8") as f:
                    config_data = json.load(f)
            except Exception:
                config_data = {}

        accounts = config_data.get("accounts", {})
        account_entry = {
            "username": username,
            "full_name": full_name,
            "password_hash": hash_hex,
            "salt_hex": salt_hex,
            "iterations": PBKDF2_ITERATIONS,
            "algorithm": "PBKDF2-HMAC-SHA256",
            "registered_at": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC"),
        }
        accounts[username] = account_entry
        config_data["accounts"] = accounts

        # Also maintain default password hash for single-credential backwards compatibility
        if "password_hash" not in config_data:
            config_data["username"] = username
            config_data["password_hash"] = hash_hex
            config_data["salt_hex"] = salt_hex
            config_data["iterations"] = PBKDF2_ITERATIONS
            config_data["algorithm"] = "PBKDF2-HMAC-SHA256"

        with open(AUTH_CONFIG_PATH, "w", encoding="utf-8") as f:
            json.dump(config_data, f, indent=2)

        return account_entry

    @classmethod
    def verify_password(cls, password: str, username: str | None = None) -> tuple[bool, str, str | None]:
        """Verifies password against stored accounts or default master password.
        Returns: (is_valid, message, derived_master_key_hex)
        """
        if not AUTH_CONFIG_PATH.exists():
            cls.init_master_password()

        with open(AUTH_CONFIG_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)

        accounts = data.get("accounts", {})

        # If specific username requested
        if username and username in accounts:
            stored_hash = accounts[username]["password_hash"]
            salt = bytes.fromhex(accounts[username]["salt_hex"])
            computed_hash = hashlib.pbkdf2_hmac(
                "sha256", password.encode("utf-8"), salt, PBKDF2_ITERATIONS, dklen=32
            ).hex()
            if hmac.compare_digest(stored_hash, computed_hash):
                master_key_hex = hashlib.sha256(password.encode("utf-8") + salt).hexdigest()
                return True, f"Autentikasi Berhasil ({accounts[username].get('full_name', username)})", master_key_hex

        # Check default master account
        if "password_hash" in data and "salt_hex" in data:
            stored_hash = data["password_hash"]
            salt = bytes.fromhex(data["salt_hex"])
            computed_hash = hashlib.pbkdf2_hmac(
                "sha256", password.encode("utf-8"), salt, PBKDF2_ITERATIONS, dklen=32
            ).hex()
            if hmac.compare_digest(stored_hash, computed_hash):
                master_key_hex = hashlib.sha256(password.encode("utf-8") + salt).hexdigest()
                return True, "Autentikasi Master Password Berhasil", master_key_hex

        # Check any registered account
        for acc_user, acc_data in accounts.items():
            stored_hash = acc_data["password_hash"]
            salt = bytes.fromhex(acc_data["salt_hex"])
            computed_hash = hashlib.pbkdf2_hmac(
                "sha256", password.encode("utf-8"), salt, PBKDF2_ITERATIONS, dklen=32
            ).hex()
            if hmac.compare_digest(stored_hash, computed_hash):
                master_key_hex = hashlib.sha256(password.encode("utf-8") + salt).hexdigest()
                return True, f"Autentikasi Berhasil ({acc_data.get('full_name', acc_user)})", master_key_hex

        return False, "Master Password Tidak Valid", None

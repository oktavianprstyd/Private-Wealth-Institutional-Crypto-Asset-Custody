"""Super-Encryption Engine: Multi-Stage Integrated Pipeline
References:
- Materi 3: Caesar Cipher (Klasik Monoalfabetik Substitusi)
- Materi 4: Vigenère Cipher (Klasik Polialfabetik Substitusi)
- Materi 7: Vernam Stream Cipher (Modern Aliran Bitwise XOR)
- Materi 6 & 7: AES Block Cipher (Modern Blok 128-bit)

Authors & Responsibilities:
- Tahap 1 (Caesar): Grace Rianty Butar Butar (123240036)
- Tahap 2 (Vigenère): Mirwan Qolyubi (123240116)
- Tahap 3 (Vernam): Oktavian Prasetya Adi (123240135)
- Tahap 4 (AES-128): Adhafa Joan Putranto (123240069)
"""

import base64
import os
import hashlib
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.backends import default_backend

# Printable ASCII range: 32 (space) to 126 (~) -> 95 characters
ASCII_START = 32
ASCII_RANGE = 95


# =====================================================================
# TAHAP 1: CAESAR CIPHER (KLASIK MONOALFABETIK)
# Penanggung Jawab: Grace Rianty Butar Butar (123240036)
# =====================================================================

class CaesarCipher:
    """Caesar Cipher implementation:
    C = (P + k) mod 26
    P = (C - k) mod 26
    """

    @staticmethod
    def encrypt(plaintext: str, shift: int) -> tuple[str, list[dict]]:
        ciphertext = ""
        steps = []
        no = 1
        for char in plaintext:
            if char.isupper():
                old_pos = ord(char) - ord("A")
                new_pos = (old_pos + shift) % 26
                new_char = chr(new_pos + ord("A"))
                ciphertext += new_char
                steps.append({
                    "No": no,
                    "Karakter": char,
                    "Posisi": str(old_pos),
                    "Kalkulasi": f"({old_pos} + {shift}) mod 26",
                    "Hasil": new_char,
                })
                no += 1
            elif char.islower():
                old_pos = ord(char) - ord("a")
                new_pos = (old_pos + shift) % 26
                new_char = chr(new_pos + ord("a"))
                ciphertext += new_char
                steps.append({
                    "No": no,
                    "Karakter": char,
                    "Posisi": str(old_pos),
                    "Kalkulasi": f"({old_pos} + {shift}) mod 26",
                    "Hasil": new_char,
                })
                no += 1
            else:
                ciphertext += char
                steps.append({
                    "No": no,
                    "Karakter": char,
                    "Posisi": "-",
                    "Kalkulasi": "Tidak diubah",
                    "Hasil": char,
                })
                no += 1
        return ciphertext, steps

    @staticmethod
    def decrypt(ciphertext: str, shift: int) -> tuple[str, list[dict]]:
        plaintext = ""
        steps = []
        no = 1
        for char in ciphertext:
            if char.isupper():
                old_pos = ord(char) - ord("A")
                new_pos = (old_pos - shift) % 26
                new_char = chr(new_pos + ord("A"))
                plaintext += new_char
                steps.append({
                    "No": no,
                    "Karakter": char,
                    "Posisi": str(old_pos),
                    "Kalkulasi": f"({old_pos} - {shift}) mod 26",
                    "Hasil": new_char,
                })
                no += 1
            elif char.islower():
                old_pos = ord(char) - ord("a")
                new_pos = (old_pos - shift) % 26
                new_char = chr(new_pos + ord("a"))
                plaintext += new_char
                steps.append({
                    "No": no,
                    "Karakter": char,
                    "Posisi": str(old_pos),
                    "Kalkulasi": f"({old_pos} - {shift}) mod 26",
                    "Hasil": new_char,
                })
                no += 1
            else:
                plaintext += char
                steps.append({
                    "No": no,
                    "Karakter": char,
                    "Posisi": "-",
                    "Kalkulasi": "Tidak diubah",
                    "Hasil": char,
                })
                no += 1
        return plaintext, steps


# =====================================================================
# TAHAP 2: VIGENÈRE CIPHER (KLASIK POLIALFABETIK)
# Penanggung Jawab: Mirwan Qolyubi (123240116)
# =====================================================================

class VigenereCipher:
    """Implementation of Vigenère Cipher supporting full printable ASCII (32-126)
    and classic alphabetic mode.
    Formula: C_i = ((P_i - 32) + (K_i - 32)) mod 95 + 32
    """

    @staticmethod
    def encrypt(plaintext: str, key: str) -> str:
        if not key:
            raise ValueError("Vigenère key cannot be empty.")

        ciphertext = []
        key_len = len(key)
        for i, char in enumerate(plaintext):
            p_val = ord(char)
            if ASCII_START <= p_val <= 126:
                k_val = ord(key[i % key_len])
                if not (ASCII_START <= k_val <= 126):
                    k_val = ord("A")
                c_val = ((p_val - ASCII_START) + (k_val - ASCII_START)) % ASCII_RANGE + ASCII_START
                ciphertext.append(chr(c_val))
            else:
                ciphertext.append(char)
        return "".join(ciphertext)

    @staticmethod
    def decrypt(ciphertext: str, key: str) -> str:
        if not key:
            raise ValueError("Vigenère key cannot be empty.")

        plaintext = []
        key_len = len(key)
        for i, char in enumerate(ciphertext):
            c_val = ord(char)
            if ASCII_START <= c_val <= 126:
                k_val = ord(key[i % key_len])
                if not (ASCII_START <= k_val <= 126):
                    k_val = ord("A")
                p_val = ((c_val - ASCII_START) - (k_val - ASCII_START)) % ASCII_RANGE + ASCII_START
                plaintext.append(chr(p_val))
            else:
                plaintext.append(char)
        return "".join(plaintext)

    @staticmethod
    def encrypt_alpha(plaintext: str, key: str) -> tuple[str, list[dict]]:
        """Classic uppercase alphabetic Vigenère matching coursework module."""
        plaintext_clean = "".join(ch for ch in plaintext.upper() if ch.isalpha())
        key_clean = "".join(ch for ch in key.upper() if ch.isalpha())
        if not key_clean:
            key_clean = "KUNCI"

        ciphertext = ""
        steps = []
        for i, p_char in enumerate(plaintext_clean):
            k_char = key_clean[i % len(key_clean)]
            p_val = ord(p_char) - ord("A")
            k_val = ord(k_char) - ord("A")
            c_val = (p_val + k_val) % 26
            c_char = chr(c_val + ord("A"))
            ciphertext += c_char
            steps.append({
                "No": i + 1,
                "Plainteks": p_char,
                "Kunci": k_char,
                "P": p_val,
                "K": k_val,
                "Rumus": f"({p_val} + {k_val}) mod 26 = {c_val}",
                "Hasil": c_char,
            })
        return ciphertext, steps

    @staticmethod
    def decrypt_alpha(ciphertext: str, key: str) -> tuple[str, list[dict]]:
        ciphertext_clean = "".join(ch for ch in ciphertext.upper() if ch.isalpha())
        key_clean = "".join(ch for ch in key.upper() if ch.isalpha())
        if not key_clean:
            key_clean = "KUNCI"

        plaintext = ""
        steps = []
        for i, c_char in enumerate(ciphertext_clean):
            k_char = key_clean[i % len(key_clean)]
            c_val = ord(c_char) - ord("A")
            k_val = ord(k_char) - ord("A")
            p_val = (c_val - k_val + 26) % 26
            p_char = chr(p_val + ord("A"))
            plaintext += p_char
            steps.append({
                "No": i + 1,
                "Cipherteks": c_char,
                "Kunci": k_char,
                "C": c_val,
                "K": k_val,
                "Rumus": f"({c_val} - {k_val} + 26) mod 26 = {p_val}",
                "Hasil": p_char,
            })
        return plaintext, steps


# =====================================================================
# TAHAP 3: VERNAM STREAM CIPHER (MODERN ALIRAN BITWISE XOR)
# Penanggung Jawab: Oktavian Prasetya Adi (123240135)
# =====================================================================

class VernamCipher:
    """Vernam Stream Cipher implementation based on bitwise XOR:
    C_i = P_i ^ K_i
    P_i = C_i ^ K_i
    Involutory property: (P ^ K) ^ K = P
    """

    @staticmethod
    def encrypt(plaintext: str, key: str, mode: str = "repeat") -> tuple[bytes, str, list[dict]]:
        p_bytes = plaintext.encode("utf-8")
        k_bytes = key.encode("utf-8")
        if not k_bytes:
            raise ValueError("Kunci Vernam keystream tidak boleh kosong.")

        if mode == "repeat":
            keystream = bytearray(k_bytes[i % len(k_bytes)] for i in range(len(p_bytes)))
        else:
            keystream = k_bytes[: len(p_bytes)]

        c_bytes = bytearray()
        steps = []
        for i, (p_b, k_b) in enumerate(zip(p_bytes, keystream)):
            c_b = p_b ^ k_b
            c_bytes.append(c_b)
            steps.append({
                "No": i + 1,
                "P": chr(p_b) if 32 <= p_b <= 126 else f"\\x{p_b:02x}",
                "P_bin": format(p_b, "08b"),
                "K": chr(k_b) if 32 <= k_b <= 126 else f"\\x{k_b:02x}",
                "K_bin": format(k_b, "08b"),
                "XOR": f"{format(p_b, '08b')} ^ {format(k_b, '08b')}",
                "C_bin": format(c_b, "08b"),
                "Hex": f"{c_b:02X}",
            })

        hex_str = " ".join(f"{b:02X}" for b in c_bytes)
        return bytes(c_bytes), hex_str, steps

    @staticmethod
    def decrypt(cipher_hex: str, key: str, mode: str = "repeat") -> str:
        clean_hex = cipher_hex.replace("0x", "").replace(" ", "").replace(":", "").replace("-", "").strip()
        if not clean_hex:
            return ""

        c_bytes = bytes.fromhex(clean_hex)
        k_bytes = key.encode("utf-8")
        if not k_bytes:
            raise ValueError("Kunci Vernam keystream tidak boleh kosong.")

        if mode == "repeat":
            keystream = bytearray(k_bytes[i % len(k_bytes)] for i in range(len(c_bytes)))
        else:
            keystream = k_bytes[: len(c_bytes)]

        p_bytes = bytearray(c_b ^ k_b for c_b, k_b in zip(c_bytes, keystream))
        return p_bytes.decode("utf-8", errors="replace")


# =====================================================================
# TAHAP 4: AES BLOCK CIPHER (MODERN BLOK)
# Penanggung Jawab: Adhafa Joan Putranto (123240069)
# =====================================================================

class AESCBCEngine:
    """Modern AES-128 / AES-256 in CBC (Cipher Block Chaining) mode with PKCS7 padding."""

    @staticmethod
    def derive_key(passphrase: str, key_size: int = 32) -> bytes:
        """Derive 128-bit (16 bytes) or 256-bit (32 bytes) key using SHA-256."""
        h = hashlib.sha256(passphrase.encode("utf-8")).digest()
        return h[:key_size]

    @classmethod
    def encrypt(cls, plaintext: str, passphrase: str, key_size: int = 32) -> tuple[str, str]:
        key = cls.derive_key(passphrase, key_size=key_size)
        iv = os.urandom(16)

        padder = padding.PKCS7(128).padder()
        padded_data = padder.update(plaintext.encode("utf-8")) + padder.finalize()

        cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
        encryptor = cipher.encryptor()
        ciphertext = encryptor.update(padded_data) + encryptor.finalize()

        payload = iv + ciphertext
        return base64.b64encode(payload).decode("utf-8"), iv.hex()

    @classmethod
    def decrypt(cls, base64_payload: str, passphrase: str, key_size: int = 32) -> str:
        key = cls.derive_key(passphrase, key_size=key_size)
        raw_payload = base64.b64decode(base64_payload.encode("utf-8"))

        if len(raw_payload) < 32:
            raise ValueError("Invalid payload: payload shorter than minimum IV + block size.")

        iv = raw_payload[:16]
        ciphertext = raw_payload[16:]

        cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
        decryptor = cipher.decryptor()
        padded_data = decryptor.update(ciphertext) + decryptor.finalize()

        unpadder = padding.PKCS7(128).unpadder()
        plaintext_bytes = unpadder.update(padded_data) + unpadder.finalize()
        return plaintext_bytes.decode("utf-8")


# =====================================================================
# INTEGRATED PIPELINES: 4-STAGE COURSEWORK & 2-STAGE FAST
# =====================================================================

def super_encrypt_4stage(
    plaintext: str,
    caesar_shift: int = 8,
    vigenere_key: str = "KUNCI",
    vernam_key: str = "VERNAM",
    aes_key: str = "mysecretkey12345",
) -> dict:
    """Integrated 4-Stage Super-Encryption Pipeline from Coursework:
    Tahap 1: Caesar Cipher (Klasik Mono) - Grace Rianty Butar Butar (123240036)
    Tahap 2: Vigenère Cipher (Klasik Poli) - Mirwan Qolyubi (123240116)
    Tahap 3: Vernam Stream Cipher (Modern Aliran) - Oktavian Prasetya Adi (123240135)
    Tahap 4: AES-128 Block Cipher (Modern Blok) - Adhafa Joan Putranto (123240069)
    """
    # Tahap 1: Caesar
    c_out, c_steps = CaesarCipher.encrypt(plaintext, caesar_shift)

    # Tahap 2: Vigenere
    v_out, v_steps = VigenereCipher.encrypt_alpha(c_out, vigenere_key)

    # Tahap 3: Vernam Stream (Oktavian)
    c_bytes, vernam_hex, vernam_steps = VernamCipher.encrypt(v_out, vernam_key, mode="repeat")

    # Tahap 4: AES-128 CBC
    aes_b64, iv_hex = AESCBCEngine.encrypt(vernam_hex, aes_key, key_size=16)

    stages = [
        {"Tahap": 1, "Algoritma": "Caesar Cipher (Klasik Mono)", "Penanggung Jawab": "Grace Rianty Butar Butar (123240036)", "Hasil Transformasi": str(c_out)},
        {"Tahap": 2, "Algoritma": "Vigenère Cipher (Klasik Poli)", "Penanggung Jawab": "Mirwan Qolyubi (123240116)", "Hasil Transformasi": str(v_out)},
        {"Tahap": 3, "Algoritma": "Vernam Stream Cipher (Modern Aliran)", "Penanggung Jawab": "Oktavian Prasetya Adi (123240135)", "Hasil Transformasi": str(vernam_hex)},
        {"Tahap": 4, "Algoritma": "AES-128 Block Cipher (Modern Blok)", "Penanggung Jawab": "Adhafa Joan Putranto (123240069)", "Hasil Transformasi": str(aes_b64)},
    ]

    return {
        "plaintext": plaintext,
        "stages": stages,
        "caesar_shift": caesar_shift,
        "caesar_out": c_out,
        "vigenere_key": vigenere_key,
        "vigenere_out": v_out,
        "vernam_key": vernam_key,
        "vernam_hex": vernam_hex,
        "aes_key": aes_key,
        "aes_b64": aes_b64,
        "iv_hex": iv_hex,
        "final_cipher": aes_b64,
    }


def super_decrypt_4stage(
    ciphertext_input: str,
    caesar_shift: int = 8,
    vigenere_key: str = "KUNCI",
    vernam_key: str = "VERNAM",
    aes_key: str = "mysecretkey12345",
) -> dict:
    """Integrated 4-Stage Super-Decryption Pipeline (Pembalikan Sempurna):
    Tahap 4 Decrypt: AES-128 -> Heksadesimal Vernam
    Tahap 3 Decrypt: Vernam Stream -> Teks Vigenère
    Tahap 2 Decrypt: Vigenère -> Teks Caesar
    Tahap 1 Decrypt: Caesar -> Plainteks Asli
    """
    # 4. Pembalik AES-128
    vernam_recovered_hex = AESCBCEngine.decrypt(ciphertext_input.strip(), aes_key, key_size=16)

    # 3. Pembalik Vernam Stream
    vigenere_recovered = VernamCipher.decrypt(vernam_recovered_hex, vernam_key, mode="repeat")

    # 2. Pembalik Vigenère
    caesar_recovered, _ = VigenereCipher.decrypt_alpha(vigenere_recovered, vigenere_key)

    # 1. Pembalik Caesar
    final_plaintext, _ = CaesarCipher.decrypt(caesar_recovered, caesar_shift)

    stages_dec = [
        {"Tahap": "4 (Pembalik AES)", "Input": "Cipherteks Base64", "Output": vernam_recovered_hex},
        {"Tahap": "3 (Pembalik Vernam)", "Input": "Vernam Hex Stream", "Output": vigenere_recovered},
        {"Tahap": "2 (Pembalik Vigenère)", "Input": "Vigenère Cipher", "Output": caesar_recovered},
        {"Tahap": "1 (Pembalik Caesar)", "Input": "Caesar Cipher", "Output": final_plaintext},
    ]

    return {
        "final_plaintext": final_plaintext,
        "stages_dec": stages_dec,
        "vernam_recovered_hex": vernam_recovered_hex,
        "vigenere_recovered": vigenere_recovered,
        "caesar_recovered": caesar_recovered,
    }


def super_encrypt(plaintext: str, classical_key: str, modern_passphrase: str) -> dict:
    """Super-Encryption: Plaintext -> Vigenère (Classical) -> AES-256-CBC (Modern).
    Returns dictionary with all stages for UI inspection and verification.
    """
    vigenere_intermediate = VigenereCipher.encrypt(plaintext, classical_key)
    final_b64, iv_hex = AESCBCEngine.encrypt(vigenere_intermediate, modern_passphrase, key_size=32)

    return {
        "plaintext": plaintext,
        "classical_cipher": "Vigenère (ASCII 95)",
        "classical_key": classical_key,
        "vigenere_output": vigenere_intermediate,
        "modern_cipher": "AES-256-CBC (PKCS7)",
        "iv_hex": iv_hex,
        "final_ciphertext_base64": final_b64,
    }


def super_decrypt(ciphertext_base64: str, classical_key: str, modern_passphrase: str) -> dict:
    """Super-Decryption: Base64 -> AES-256-CBC Decrypt -> Vigenère Decrypt -> Plaintext."""
    aes_recovered = AESCBCEngine.decrypt(ciphertext_base64, modern_passphrase, key_size=32)
    final_plaintext = VigenereCipher.decrypt(aes_recovered, classical_key)

    return {
        "input_ciphertext_base64": ciphertext_base64,
        "aes_intermediate": aes_recovered,
        "final_plaintext": final_plaintext,
    }

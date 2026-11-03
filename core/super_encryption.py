"""Super-Encryption Engine: Classical Vigenère + Modern AES-256-CBC
References:
- Materi 4: Vigenère Cipher (Polialfabetik Substitution)
- Materi 6 & 7: Modern Block Cipher & AES (Rijndael) CBC Mode with PKCS7 Padding
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


class VigenereCipher:
    """Implementation of Vigenère Cipher supporting full printable ASCII range (32-126).
    This ensures punctuation, numbers, and spaces in secret text/keys are preserved.
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
                    k_val = ord('A')
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
                    k_val = ord('A')
                p_val = ((c_val - ASCII_START) - (k_val - ASCII_START)) % ASCII_RANGE + ASCII_START
                plaintext.append(chr(p_val))
            else:
                plaintext.append(char)
        return "".join(plaintext)


class AESCBCEngine:
    """Modern AES-256 in CBC (Cipher Block Chaining) mode with PKCS7 padding.
    Produces: IV (16 bytes) prepended to Ciphertext, returned as Base64.
    """

    @staticmethod
    def derive_key(passphrase: str) -> bytes:
        """Derive 256-bit (32 bytes) key using SHA-256 (Materi 8)."""
        return hashlib.sha256(passphrase.encode("utf-8")).digest()

    @classmethod
    def encrypt(cls, plaintext: str, passphrase: str) -> tuple[str, str]:
        """Encrypt plaintext using AES-256-CBC.
        Returns: (base64_encoded_payload, iv_hex)
        """
        key = cls.derive_key(passphrase)
        iv = os.urandom(16)
        
        # PKCS7 Padder (AES block size = 128 bits / 16 bytes)
        padder = padding.PKCS7(128).padder()
        padded_data = padder.update(plaintext.encode("utf-8")) + padder.finalize()
        
        cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
        encryptor = cipher.encryptor()
        ciphertext = encryptor.update(padded_data) + encryptor.finalize()
        
        # Prepend IV to ciphertext for self-contained transmission
        payload = iv + ciphertext
        return base64.b64encode(payload).decode("utf-8"), iv.hex()

    @classmethod
    def decrypt(cls, base64_payload: str, passphrase: str) -> str:
        """Decrypt Base64 payload containing IV + Ciphertext."""
        key = cls.derive_key(passphrase)
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


def super_encrypt(plaintext: str, classical_key: str, modern_passphrase: str) -> dict:
    """Super-Encryption: Plaintext -> Vigenère (Classical) -> AES-256-CBC (Modern).
    Returns dictionary with all stages for UI inspection and verification.
    """
    # Stage 1: Classical Vigenère
    vigenere_intermediate = VigenereCipher.encrypt(plaintext, classical_key)
    
    # Stage 2: Modern AES-256-CBC
    final_b64, iv_hex = AESCBCEngine.encrypt(vigenere_intermediate, modern_passphrase)
    
    return {
        "plaintext": plaintext,
        "classical_cipher": "Vigenère (ASCII 95)",
        "classical_key": classical_key,
        "vigenere_output": vigenere_intermediate,
        "modern_cipher": "AES-256-CBC (PKCS7)",
        "iv_hex": iv_hex,
        "final_ciphertext_base64": final_b64
    }


def super_decrypt(ciphertext_base64: str, classical_key: str, modern_passphrase: str) -> dict:
    """Super-Decryption: Base64 -> AES-256-CBC Decrypt -> Vigenère Decrypt -> Plaintext."""
    # Stage 1: Modern AES Decrypt
    aes_recovered = AESCBCEngine.decrypt(ciphertext_base64, modern_passphrase)
    
    # Stage 2: Classical Vigenère Decrypt
    final_plaintext = VigenereCipher.decrypt(aes_recovered, classical_key)
    
    return {
        "input_ciphertext_base64": ciphertext_base64,
        "aes_intermediate": aes_recovered,
        "final_plaintext": final_plaintext
    }

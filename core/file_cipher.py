"""File Encryption Engine: RC4 Stream Cipher (Rivest Cipher 4)
References:
- Materi 7: Algoritma Kriptografi Modern (Stream Cipher & RC4)
- Specification: File message encrypted with a different algorithm from text (Stream vs Block)
Features:
- Pure Python byte-exact implementation of KSA (Key Scheduling Algorithm) & PRGA
- Preserves original file metadata (filename, extension) in a compact encrypted envelope
"""

import struct


class RC4:
    """RC4 (Rivest Cipher 4) Stream Cipher Engine.
    Implements KSA (Key-Scheduling Algorithm) and PRGA (Pseudo-Random Generation Algorithm).
    """

    def __init__(self, key: bytes):
        if not key or len(key) == 0:
            raise ValueError("RC4 key cannot be empty.")
        if len(key) > 256:
            raise ValueError("RC4 key must be <= 256 bytes (8 to 2048 bits).")
        self.key = key
        self.S = self._ksa(key)
        self.i = 0
        self.j = 0

    def _ksa(self, key: bytes) -> list[int]:
        """Key-Scheduling Algorithm (KSA) - Materi 7 Slide 6-8:
        Inisialisasi larik S dengan permutasi identitas 0..255,
        kemudian acak S berdasarkan kunci.
        """
        key_len = len(key)
        S = list(range(256))
        j = 0
        for i in range(256):
            j = (j + S[i] + key[i % key_len]) % 256
            S[i], S[j] = S[j], S[i]
        return S

    def _prga(self) -> int:
        """Pseudo-Random Generation Algorithm (PRGA) - Materi 7 Slide 9-10:
        Membangkitkan 1 byte keystream secara kontinu.
        """
        self.i = (self.i + 1) % 256
        self.j = (self.j + self.S[self.i]) % 256
        self.S[self.i], self.S[self.j] = self.S[self.j], self.S[self.i]
        t = (self.S[self.i] + self.S[self.j]) % 256
        return self.S[t]

    def process(self, data: bytes) -> bytes:
        """Encrypt or Decrypt byte sequence via stream XOR:
        C = P ^ K  (Symmetric operation: Decrypt is identical to Encrypt).
        """
        output = bytearray(len(data))
        for idx, byte in enumerate(data):
            keystream_byte = self._prga()
            output[idx] = byte ^ keystream_byte
        return bytes(output)


MAGIC_HEADER = b"AEGIS_RC4_V1\x00"
LEGACY_MAGIC_HEADER = b"SNTX_RC4_V1\x00"


def encrypt_file_bytes(file_bytes: bytes, original_filename: str, key_passphrase: str) -> bytes:
    """Encrypts arbitrary binary file with RC4 and prepends a self-describing metadata envelope.
    Envelope Format:
    [13 bytes MAGIC] + [2 bytes filename_len] + [filename_bytes] + [RC4_ciphertext]
    """
    if not key_passphrase:
        raise ValueError("Encryption passphrase cannot be empty.")

    key_bytes = key_passphrase.encode("utf-8")
    if len(key_bytes) > 256:
        import hashlib
        key_bytes = hashlib.sha256(key_bytes).digest()

    rc4 = RC4(key_bytes)
    ciphertext = rc4.process(file_bytes)

    # Encode metadata
    fn_bytes = original_filename.encode("utf-8")
    header = MAGIC_HEADER + struct.pack("!H", len(fn_bytes)) + fn_bytes
    return header + ciphertext


def decrypt_file_bytes(envelope_bytes: bytes, key_passphrase: str) -> tuple[bytes, str]:
    """Decrypts RC4 envelope and extracts (decrypted_file_bytes, original_filename).
    If envelope lacks Aegis header, falls back to direct raw decryption.
    """
    if not key_passphrase:
        raise ValueError("Decryption passphrase cannot be empty.")

    key_bytes = key_passphrase.encode("utf-8")
    if len(key_bytes) > 256:
        import hashlib
        key_bytes = hashlib.sha256(key_bytes).digest()

    if envelope_bytes.startswith(MAGIC_HEADER):
        offset = len(MAGIC_HEADER)
        (fn_len,) = struct.unpack("!H", envelope_bytes[offset : offset + 2])
        offset += 2
        original_filename = envelope_bytes[offset : offset + fn_len].decode("utf-8", errors="replace")
        offset += fn_len
        ciphertext = envelope_bytes[offset:]
    elif envelope_bytes.startswith(LEGACY_MAGIC_HEADER):
        offset = len(LEGACY_MAGIC_HEADER)
        (fn_len,) = struct.unpack("!H", envelope_bytes[offset : offset + 2])
        offset += 2
        original_filename = envelope_bytes[offset : offset + fn_len].decode("utf-8", errors="replace")
        offset += fn_len
        ciphertext = envelope_bytes[offset:]
    else:
        original_filename = "decrypted_file.bin"
        ciphertext = envelope_bytes

    rc4 = RC4(key_bytes)
    decrypted_bytes = rc4.process(ciphertext)
    return decrypted_bytes, original_filename

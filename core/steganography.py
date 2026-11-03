"""Spatial Domain Image Steganography Engine: LSB (Least Significant Bit)
References:
- Materi 9: Steganografi (Prisoner’s Problem & LSB Substitution pada Citra RGB)
- Specification: Image messages protected using steganography concepts
Features:
- Encodes secret text into the least significant bit of RGB channels
- Exact 32-bit length prefix + delimiter for robust extraction
- Computes PSNR (Peak Signal-to-Noise Ratio) & MSE to prove visual imperceptibility
"""

import math
import struct
from PIL import Image

DELIMITER = "##SNTX##"


def _bytes_to_bits(data: bytes) -> list[int]:
    """Converts bytes into list of individual bits (MSB first)."""
    bits = []
    for b in data:
        for shift in range(7, -1, -1):
            bits.append((b >> shift) & 1)
    return bits


def _bits_to_bytes(bits: list[int]) -> bytes:
    """Converts list of bits into bytes (8 bits per byte)."""
    out = bytearray()
    for i in range(0, len(bits), 8):
        byte_bits = bits[i : i + 8]
        if len(byte_bits) < 8:
            break
        val = 0
        for b in byte_bits:
            val = (val << 1) | b
        out.append(val)
    return bytes(out)


def embed_secret_message(cover_image: Image.Image, secret_text: str) -> tuple[Image.Image, dict]:
    """Embeds secret_text into cover_image using LSB substitution on RGB channels.
    Returns: (stego_image, metrics_dict)
    """
    if cover_image.mode != "RGB":
        cover_image = cover_image.convert("RGB")

    width, height = cover_image.size
    total_slots = width * height * 3  # 3 channels (R, G, B)

    # Encode payload: [4 bytes length prefix] + [secret_text_utf8] + [delimiter]
    text_bytes = secret_text.encode("utf-8") + DELIMITER.encode("utf-8")
    payload = struct.pack("!I", len(text_bytes)) + text_bytes
    payload_bits = _bytes_to_bits(payload)

    if len(payload_bits) > total_slots:
        raise ValueError(
            f"Image too small! Max capacity is {total_slots // 8} bytes, but payload requires {len(payload)} bytes."
        )

    # Work directly with raw bytearray for maximum speed and compatibility
    raw_bytes = bytearray(cover_image.tobytes())
    for idx, bit in enumerate(payload_bits):
        raw_bytes[idx] = (raw_bytes[idx] & 0xFE) | bit

    stego_image = Image.frombytes("RGB", (width, height), bytes(raw_bytes))

    metrics = calculate_stego_metrics(cover_image, stego_image)
    metrics["payload_bytes"] = len(payload)
    metrics["capacity_bytes"] = total_slots // 8
    metrics["capacity_used_pct"] = round((len(payload_bits) / total_slots) * 100, 3)

    return stego_image, metrics


def extract_secret_message(stego_image: Image.Image) -> str:
    """Extracts hidden text from stego_image via LSB."""
    if stego_image.mode != "RGB":
        stego_image = stego_image.convert("RGB")

    raw_bytes = stego_image.tobytes()
    total_bytes = len(raw_bytes)

    # 1. Read first 32 bits to get payload length
    if total_bytes < 32:
        raise ValueError("Image data too small to contain stego header.")

    header_bits = [raw_bytes[i] & 1 for i in range(32)]
    (payload_len,) = struct.unpack("!I", _bits_to_bytes(header_bits))

    max_safe_len = total_bytes // 8
    if payload_len <= 0 or payload_len > max_safe_len:
        raise ValueError("No valid Sentix steganography header found in this image.")

    # 2. Read remaining payload bits
    target_bits = payload_len * 8
    if 32 + target_bits > total_bytes:
        raise ValueError("Steganography payload truncated or corrupted.")

    payload_bits = [raw_bytes[32 + i] & 1 for i in range(target_bits)]
    extracted_bytes = _bits_to_bytes(payload_bits)
    delim_bytes = DELIMITER.encode("utf-8")

    if extracted_bytes.endswith(delim_bytes):
        extracted_bytes = extracted_bytes[: -len(delim_bytes)]

    return extracted_bytes.decode("utf-8", errors="replace")


def calculate_stego_metrics(img1: Image.Image, img2: Image.Image) -> dict:
    """Calculates Mean Squared Error (MSE) and Peak Signal-to-Noise Ratio (PSNR).
    Higher PSNR (> 40-50 dB) indicates humanly imperceptible differences.
    """
    b1 = img1.tobytes()
    b2 = img2.tobytes()

    if len(b1) != len(b2):
        raise ValueError("Image dimensions do not match for metric calculation.")

    sum_sq_diff = sum((x - y) ** 2 for x, y in zip(b1, b2))
    mse = sum_sq_diff / len(b1)

    if mse == 0:
        psnr = 99.99  # Identical
    else:
        psnr = 10 * math.log10((255 ** 2) / mse)

    return {
        "mse": round(mse, 6),
        "psnr_db": round(psnr, 2),
        "visual_quality": "Imperceptible (PSNR > 50 dB)" if psnr > 50 else "High Quality",
    }

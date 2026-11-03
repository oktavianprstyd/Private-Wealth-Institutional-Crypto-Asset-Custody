"""CLI Utility: Enroll Master Facial Biometrics
Usage:
  python scripts/enroll_face.py --image path/to/face.jpg --user oktavian
"""

import sys
import argparse
from pathlib import Path
from PIL import Image

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from core.auth_3fa import BiometricVerifier
from config import MASTER_FACE_PATH


def main():
    parser = argparse.ArgumentParser(description="Sentix Digital Vault - Face Biometric Enrollment")
    parser.add_argument("--image", "-i", type=str, required=True, help="Path to master face photo (.jpg, .png)")
    parser.add_argument("--user", "-u", default="oktavian", help="User Identifier")
    args = parser.parse_args()

    img_path = Path(args.image)
    if not img_path.exists():
        print(f"[!] Error: File not found at {img_path}")
        sys.exit(1)

    try:
        img = Image.open(img_path)
        saved_path = BiometricVerifier.enroll_face(img, user_id=args.user)
        print("=" * 60)
        print("SENTIX BIOMETRIC ENROLLMENT ENGINE")
        print("=" * 60)
        print(f"[+] User ID        : {args.user}")
        print(f"[+] Master Image   : {img_path.resolve()}")
        print(f"[+] Feature Record : {saved_path.resolve()}")
        print(f"[+] Metric         : 128-D Normalized Cosine Embedding")
        print(f"[+] Status         : BIOMETRIC TEMPLATE STORED")
        print("=" * 60)
    except Exception as e:
        print(f"[!] Biometric Enrollment Failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()

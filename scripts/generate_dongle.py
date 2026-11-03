"""CLI Utility: Generate Hardware USB Dongle Key
Usage:
  python scripts/generate_dongle.py --output E:/
  python scripts/generate_dongle.py --virtual
"""

import sys
import argparse
from pathlib import Path

# Add project root to sys.path
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from core.auth_3fa import DongleVerifier
from config import DATA_DIR, DONGLE_FILENAME


def main():
    parser = argparse.ArgumentParser(description="Sentix Digital Vault - Dongle Generator")
    parser.add_argument("--output", "-o", type=str, help="Destination directory (e.g. USB drive letter 'E:/' or path)")
    parser.add_argument("--virtual", action="store_true", help="Generate virtual dongle in local data/dongle directory")
    parser.add_argument("--vault-id", default="VAULT-ALPHA-01", help="Custom Vault Identifier")
    args = parser.parse_args()

    if args.virtual or not args.output:
        target_dir = DATA_DIR / "dongle"
    else:
        target_dir = Path(args.output)

    target_file = DongleVerifier.write_dongle_to_path(target_dir, vault_id=args.vault_id)
    print("=" * 60)
    print("SENTIX HARDWARE DONGLE GENERATOR")
    print("=" * 60)
    print(f"[+] Dongle key successfully generated at:")
    print(f"    {target_file.resolve()}")
    print(f"[+] Vault ID    : {args.vault_id}")
    print(f"[+] Token Type  : HMAC-SHA256 Signed Security Token")
    print(f"[+] Status      : READY FOR 3FA AUTHENTICATION")
    print("=" * 60)


if __name__ == "__main__":
    main()

"""Comprehensive Test Suite for Aegis Cold Custody Cryptographic Engines
Validates all 6 core requirements from the Final Project Specification:
1. 3FA Authentication (Dongle USB + Biometric Face + Password Hash)
2. Super-Encryption (Classical Vigenère + Modern AES-256-CBC)
3. File Encryption (Stream Cipher RC4)
4. Database Encryption (SQLite + AES-256-GCM)
5. Image Steganography (Spatial LSB + PSNR Metric)
6. Blockchain Asset Integrity (Proof-of-Work + Tamper Detection)
"""

import unittest
import tempfile
import shutil
from pathlib import Path
from PIL import Image
import numpy as np

import sys
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from core.auth_3fa import DongleVerifier, BiometricVerifier, PasswordVerifier
from core.super_encryption import VigenereCipher, AESCBCEngine, super_encrypt, super_decrypt
from core.file_cipher import RC4, encrypt_file_bytes, decrypt_file_bytes
from core.database_vault import init_database, insert_secret, get_all_secrets_decrypted, get_raw_database_records
from core.steganography import embed_secret_message, extract_secret_message, calculate_stego_metrics
from core.blockchain import Blockchain, Transaction, Block


class TestAegisCryptoEngines(unittest.TestCase):

    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.test_path = Path(self.test_dir)
        self.auth_backup = Path("data/auth_config.json").read_bytes() if Path("data/auth_config.json").exists() else None
        self.face_backup = Path("data/master_face.json").read_bytes() if Path("data/master_face.json").exists() else None

    def tearDown(self):
        shutil.rmtree(self.test_dir)
        if self.auth_backup:
            Path("data/auth_config.json").write_bytes(self.auth_backup)
        if self.face_backup:
            Path("data/master_face.json").write_bytes(self.face_backup)

    # -------------------------------------------------------------
    # 1. 3FA AUTHENTICATION TESTS
    # -------------------------------------------------------------
    def test_01_dongle_generation_and_verification(self):
        """Test USB dongle token creation, verification, and tamper detection."""
        dongle_file = DongleVerifier.write_dongle_to_path(self.test_path)
        self.assertTrue(dongle_file.exists())

        # Valid verification
        valid, msg, payload = DongleVerifier.verify_dongle_path(dongle_file)
        self.assertTrue(valid)
        self.assertEqual(payload["vault_id"], "VAULT-ALPHA-01")

        # Tampering with dongle file
        with open(dongle_file, "w", encoding="utf-8") as f:
            f.write('{"payload": {"vault_id": "HACKED"}, "signature": "fake"}')
        valid, msg, _ = DongleVerifier.verify_dongle_path(dongle_file)
        self.assertFalse(valid)
        self.assertIn("Rejected", msg)

    def test_02_biometric_face_matching(self):
        """Test biometric face enrollment and cosine distance threshold."""
        # Create synthetic face image
        img1 = Image.new("RGB", (64, 64), color=(180, 150, 120))
        BiometricVerifier.enroll_face(img1, user_id="tester")

        # Probe identical face
        valid, dist, msg = BiometricVerifier.verify_face(img1)
        self.assertTrue(valid)
        self.assertLess(dist, 0.05)

        # Probe completely different image (black square)
        img_different = Image.new("RGB", (64, 64), color=(0, 0, 0))
        valid_diff, dist_diff, _ = BiometricVerifier.verify_face(img_different)
        self.assertFalse(valid_diff)
        self.assertGreater(dist_diff, 0.32)

    def test_02b_biometric_anti_spoofing_and_privacy(self):
        """Test anti-spoofing presentation attack detection and zero-raw-storage privacy."""
        # 1. Zero raw image storage check
        master_jpg = Path("data/master_face.jpg")
        probe_jpg = Path("data/last_probe.jpg")
        self.assertFalse(master_jpg.exists(), "Raw master_face.jpg must NOT be persisted on disk")
        self.assertFalse(probe_jpg.exists(), "Raw last_probe.jpg must NOT be persisted on disk")

        # Zero raw dongle key storage check (Zero-Raw Storage Enforcement)
        raw_keys = list(Path("data").glob("**/*.key"))
        self.assertEqual(len(raw_keys), 0, f"Raw dongle key files must NOT be stored inside data/: {raw_keys}")

        # 2. Non-human / grayscale / spoof rejection
        img_spoof = Image.new("RGB", (64, 64), color=(100, 100, 240))  # Unnatural blue hue
        liv_spoof = BiometricVerifier.analyze_liveness(img_spoof)
        self.assertFalse(liv_spoof["is_live"])
        self.assertEqual(liv_spoof["status"], "SPOOF_NON_SKIN")

        # 3. Too dark / shutter closed rejection
        img_dark = Image.new("RGB", (64, 64), color=(5, 5, 5))
        liv_dark = BiometricVerifier.analyze_liveness(img_dark)
        self.assertFalse(liv_dark["is_live"])
        self.assertEqual(liv_dark["status"], "TOO_DARK")

        # 4. Screen Replay bezel detection check
        arr_screen = np.full((64, 64, 3), 180, dtype=np.uint8)
        arr_screen[:, :10, :] = 10  # Dark bezel on left
        arr_screen[:, 54:, :] = 10  # Dark bezel on right
        img_screen = Image.fromarray(arr_screen)
        liv_screen = BiometricVerifier.analyze_liveness(img_screen)
        self.assertFalse(liv_screen["is_live"])
        self.assertIn("SPOOF", liv_screen["status"])

    def test_03_password_hash_and_key_derivation(self):
        """Test PBKDF2-HMAC-SHA256 password verification and session key generation."""
        PasswordVerifier.init_master_password("Testing123!")
        
        # Valid password
        valid, msg, key = PasswordVerifier.verify_password("Testing123!")
        self.assertTrue(valid)
        self.assertIsNotNone(key)
        self.assertEqual(len(key), 64)  # 256-bit hex

        # Invalid password
        invalid, _, key_none = PasswordVerifier.verify_password("WrongPassword")
        self.assertFalse(invalid)
        self.assertIsNone(key_none)

    # -------------------------------------------------------------
    # 2. SUPER-ENCRYPTION TESTS (Vigenère + AES-256-CBC)
    # -------------------------------------------------------------
    def test_04_super_encryption_roundtrip(self):
        """Test text super-encryption: Plaintext -> Vigenere -> AES -> Plaintext."""
        secret_text = "Aegis Secret Private Key: 0x9f8b4a72d1e0c354"
        classical_key = "UPNVETERAN2026"
        modern_passphrase = "MasterExecutivePassphrase!"

        result = super_encrypt(secret_text, classical_key, modern_passphrase)
        self.assertIn("final_ciphertext_base64", result)
        self.assertNotEqual(result["vigenere_output"], secret_text)

        decrypted = super_decrypt(result["final_ciphertext_base64"], classical_key, modern_passphrase)
        self.assertEqual(decrypted["final_plaintext"], secret_text)
        self.assertEqual(decrypted["aes_intermediate"], result["vigenere_output"])

    def test_04b_4stage_super_encryption_roundtrip(self):
        """Test integrated 4-stage pipeline from coursework: Caesar -> Vigenere -> Vernam -> AES."""
        from core.super_encryption import super_encrypt_4stage, super_decrypt_4stage
        plain = "BELAJAR KRIPTOGRAFI"
        res = super_encrypt_4stage(plain, caesar_shift=8, vigenere_key="KUNCI", vernam_key="VERNAM", aes_key="secretkey12345")
        self.assertIn("final_cipher", res)
        self.assertEqual(len(res["stages"]), 4)

        dec = super_decrypt_4stage(res["final_cipher"], caesar_shift=8, vigenere_key="KUNCI", vernam_key="VERNAM", aes_key="secretkey12345")
        self.assertEqual(dec["final_plaintext"], "BELAJARKRIPTOGRAFI")

    # -------------------------------------------------------------
    # 3. FILE ENCRYPTION TESTS (RC4 Stream Cipher)
    # -------------------------------------------------------------
    def test_05_file_rc4_roundtrip(self):
        """Test binary file encryption using RC4 Stream Cipher with metadata envelope."""
        dummy_file_content = b"%PDF-1.4 Fake Secret Financial Audit PDF Document Content \x00\xff\xee"
        original_name = "audit_report_q4.pdf"
        passphrase = "RC4VaultSecretKey"

        # Encrypt
        encrypted_envelope = encrypt_file_bytes(dummy_file_content, original_name, passphrase)
        self.assertNotEqual(encrypted_envelope, dummy_file_content)

        # Decrypt
        decrypted_bytes, recovered_name = decrypt_file_bytes(encrypted_envelope, passphrase)
        self.assertEqual(decrypted_bytes, dummy_file_content)
        self.assertEqual(recovered_name, original_name)

    # -------------------------------------------------------------
    # 4. DATABASE ENCRYPTION TESTS (SQLite + AES-256-GCM)
    # -------------------------------------------------------------
    def test_06_database_gcm_encryption(self):
        """Test database table storage: sensitive field encrypted on disk, decrypted with key."""
        db_file = self.test_path / "test_vault.db"
        master_key = "SuperSafeDBMasterKey"

        # Insert record
        rec_id = insert_secret(
            title="Cold Storage Wallet 1",
            category="SEED_PHRASE",
            plaintext_secret="abandon amount liar bacon lemon matrix ...",
            master_key=master_key,
            account_id="CLIENT-VVIP-007",
            db_path=db_file,
        )
        self.assertGreater(rec_id, 0)

        # Check raw records (must be encrypted ciphertext, NOT plaintext)
        raw_rows = get_raw_database_records(db_path=db_file)
        self.assertEqual(len(raw_rows), 1)
        self.assertNotIn("abandon amount", raw_rows[0]["ciphertext_base64"])
        self.assertTrue(len(raw_rows[0]["iv_hex"]) > 0)
        self.assertTrue(len(raw_rows[0]["tag_hex"]) > 0)

        # Check decrypted records
        decrypted_rows = get_all_secrets_decrypted(master_key, db_path=db_file)
        self.assertEqual(len(decrypted_rows), 1)
        self.assertEqual(decrypted_rows[0]["decryption_status"], "SUCCESS")
        self.assertIn("abandon amount liar", decrypted_rows[0]["decrypted_secret"])

        # Check decryption with wrong key
        wrong_rows = get_all_secrets_decrypted("WrongMasterKey", db_path=db_file)
        self.assertIn("FAILED", wrong_rows[0]["decryption_status"])

    # -------------------------------------------------------------
    # 5. IMAGE STEGANOGRAPHY TESTS (Spatial LSB)
    # -------------------------------------------------------------
    def test_07_steganography_lsb_roundtrip(self):
        """Test LSB embedding and extraction into RGB image + PSNR metric check."""
        cover = Image.new("RGB", (100, 100), color=(120, 200, 150))
        secret_message = "AEGIS:TransferAuthorization:Hash=0xABC123"

        stego_img, metrics = embed_secret_message(cover, secret_message)
        self.assertGreater(metrics["psnr_db"], 50.0)  # High imperceptible fidelity

        extracted = extract_secret_message(stego_img)
        self.assertEqual(extracted, secret_message)

    # -------------------------------------------------------------
    # 6. BLOCKCHAIN ASSET INTEGRITY TESTS (PoW + Tamper Detection)
    # -------------------------------------------------------------
    def test_08_blockchain_mining_and_tamper_detection(self):
        """Test PoW mining, block linkage, and automated tamper detection."""
        bc_file = self.test_path / "test_chain.json"
        bc = Blockchain(difficulty=2, storage_path=bc_file)

        # Initial chain has genesis block
        self.assertEqual(len(bc.chain), 1)
        valid, msg = bc.is_chain_valid()
        self.assertTrue(valid)

        # Add transaction and mine
        bc.add_transaction(
            sender="TREASURY_01",
            recipient="COLD_STORAGE_A",
            asset="ETH",
            amount=50.0,
            memo="Liquidity rebalancing",
        )
        mined_block = bc.mine_pending_transactions(miner_address="AUDITOR_NODE")
        self.assertEqual(mined_block.index, 1)
        self.assertTrue(mined_block.hash.startswith("00"))

        valid, msg = bc.is_chain_valid()
        self.assertTrue(valid)
        self.assertEqual(len(bc.chain), 2)

        # Inject deliberate tampering on Block #1
        bc.tamper_block_for_demo(1, 999999.0)
        tamper_valid, tamper_msg = bc.is_chain_valid()
        self.assertFalse(tamper_valid)
        self.assertIn("Tampered data detected in Block #1", tamper_msg)


if __name__ == "__main__":
    unittest.main()

"""Aegis Cold Custody - Air-Gapped BIP-39 Mnemonic Seed Vault & Hardware Key Custodian
Integrated Cryptographic Workstation for UPN "Veteran" Yogyakarta Final Project.

Tim Pengembang (Kelompok 3):
- Oktavian Prasetya Adi (123240135) - Security Architecture, 3FA Gatekeeper, Modern Ciphers (Vernam XOR, AES, RC4, Blockchain, GCM)
- Grace Rianty Butar Butar (123240036) - Frontend Mnemonic UX, Classical Ciphers (Caesar & Vigenere)

Arsitektur & Alur Sistem:
1. Alur Pengguna (User Flow):
   - Masuk (3FA Gatekeeper: Hardware Key USB HMAC-SHA256 + Biometrik Wajah 128-D + Password PBKDF2)
   - Registrasi Akun Petugas Baru (Nama, Password Hash PBKDF2, Perekaman Wajah, Unduh Kunci Dongle)
   - Dashboard Cold Custody:
     * Tab 1: BIP-39 Mnemonic Seed Phrase Armor (Super-Enkripsi 4-Tahap: Caesar -> Vigenere -> Vernam -> AES-128)
     * Tab 2: Keystore & Private Key Vault (Stream Cipher RC4)
     * Tab 3: Stego Paper Wallet & NFT Camouflage (Spatial LSB + PSNR/MSE)
     * Tab 4: Cold Wallet On-Chain Transaction Ledger (PoW Blockchain SHA-256 + Tamper Alert)
     * Tab 5: Whitelisted Address Book & UTXO Database (SQLite + AES-256-GCM AEAD)
2. Alur Pengembang (Developer Flow):
   - Sandbox Evaluasi Dosen (Matriks 7 Kriteria Kriptografi)
   - 1-Click Fast Testing Bypass (Mode Sandbox Terisolasi - Akses Data Riil Diblokir)
   - Inspektur Basis Data SQLite Fisik (Raw Ciphertext On-Disk)
"""

import streamlit as st
import time
import json
import hashlib
from pathlib import Path
from io import BytesIO
from PIL import Image

# Core Cryptographic Engines
from config import BASE_DIR, DATA_DIR, DONGLE_FILENAME, MASTER_FACE_PATH
from core.auth_3fa import DongleVerifier, BiometricVerifier, PasswordVerifier
from core.super_encryption import (
    super_encrypt,
    super_decrypt,
    super_encrypt_4stage,
    super_decrypt_4stage,
)
from core.file_cipher import encrypt_file_bytes, decrypt_file_bytes
from core.database_vault import (
    init_database,
    insert_secret,
    get_all_secrets_decrypted,
    get_raw_database_records,
    delete_record,
)
from core.steganography import embed_secret_message, extract_secret_message
from core.blockchain import Blockchain

# Streamlit Page Configuration
st.set_page_config(
    page_title="Aegis Cold Custody | Air-Gapped Seed Vault",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Institutional Cold Wallet Dark Theme CSS
st.markdown("""
<style>
    .stApp {
        background-color: #0B0F19;
        color: #E2E8F0;
    }
    .badge-pill {
        display: inline-block;
        padding: 4px 12px;
        font-size: 11px;
        font-weight: 700;
        letter-spacing: 0.05em;
        border-radius: 9999px;
        text-transform: uppercase;
        margin-right: 6px;
    }
    .badge-success {
        background-color: #064E3B;
        color: #34D399;
        border: 1px solid #059669;
    }
    .badge-warning {
        background-color: #78350F;
        color: #FBBF24;
        border: 1px solid #D97706;
    }
    .badge-danger {
        background-color: #7F1D1D;
        color: #F87171;
        border: 1px solid #DC2626;
    }
    .badge-info {
        background-color: #1E293B;
        color: #94A3B8;
        border: 1px solid #334155;
    }
    .badge-hsm {
        background-color: #312E81;
        color: #A5B4FC;
        border: 1px solid #6366F1;
    }
    .flow-card {
        background-color: #111827;
        border: 1px solid #1F2937;
        border-radius: 8px;
        padding: 16px;
        margin-bottom: 12px;
    }
</style>
""", unsafe_allow_html=True)


# Initialize Session State
if "dongle_verified" not in st.session_state:
    st.session_state.dongle_verified = False
if "biometric_verified" not in st.session_state:
    st.session_state.biometric_verified = False
if "authenticated_officer" not in st.session_state:
    st.session_state.authenticated_officer = "N/A"
if "password_verified" not in st.session_state:
    st.session_state.password_verified = False
if "master_session_key" not in st.session_state:
    st.session_state.master_session_key = None
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "is_dev_mode" not in st.session_state:
    st.session_state.is_dev_mode = False
if "blockchain" not in st.session_state:
    st.session_state.blockchain = Blockchain()


# =====================================================================
# FLOW 1: USER LOGIN GATEWAY (AIR-GAPPED 3FA GATEKEEPER)
# =====================================================================

def render_login_flow():
    col_info, col_gate = st.columns([1, 1.25], gap="large")

    with col_info:
        st.subheader("Protokol Akses Air-Gapped 3FA")
        st.markdown("""
        Workstation **Aegis Cold Custody** beroperasi dengan arsitektur **Zero-Trust Hardware Security (NIST SP 800-63B)**. 
        Kunci privat dan seed phrase dompet kripto hanya dapat diakses secara offline apabila seluruh 3 faktor fisik-fisiologis terpenuhi:
        
        * **Faktor 1 (What You Have — Hardware Key HSM):** Kunci fisik USB Flashdisk berisi file token kriptografis `sentix_dongle.key` bertanda tangan HMAC-SHA256.
        * **Faktor 2 (What You Are — Biometrik Wajah):** Pemindaian geometri wajah petugas berwenang (*128-D Cosine Distance* $\\le 0.32$), dieksekusi efisien pada CPU/iGPU tanpa beban server eksternal.
        * **Faktor 3 (What You Know — BIP-39 Key Derivation):** Master Passphrase diturunkan menggunakan PBKDF2-HMAC-SHA256 (100.000 iterasi + 16-byte salt) untuk mendekripsi Master Key sesi di RAM.
        """)

        with st.container(border=True):
            st.markdown("**Petugas Kustodi Terdaftar:**")
            roster = BiometricVerifier.list_enrolled_faces()
            if roster:
                for item in roster:
                    st.write(f"- **{item['name']}** (`{item['user_id']}`)")
            else:
                st.caption("Belum ada petugas terdaftar. Silakan daftarkan akun baru pada tab registrasi.")

            if not roster:
                st.markdown("---")
                if st.button("Daftarkan Akun Default Oktavian (Quickstart)", key="btn_quick_default"):
                    sample_face = Image.new("RGB", (64, 64), color=(180, 150, 120))
                    BiometricVerifier.enroll_face(sample_face, user_id="oktavian", name="Oktavian Prasetya Adi (123240135)")
                    PasswordVerifier.register_account("oktavian", "Oktavian Prasetya Adi (123240135)", "Sentix@2026!")
                    DongleVerifier.write_dongle_to_path(DATA_DIR / "dongle", holder_name="Oktavian Prasetya Adi (123240135)")
                    st.success("Akun default Oktavian berhasil didaftarkan!")
                    st.rerun()

    with col_gate:
        st.subheader("Verifikasi Autentikasi Cold Custody")

        # STEP 1: HARDWARE DONGLE
        with st.container(border=True):
            st.markdown("#### Tahap 1: Hardware USB Security Key (HSM)")
            scanned = DongleVerifier.scan_possible_dongle_locations()
            
            dongle_choice = None
            if scanned:
                st.caption(f"Terdeteksi {len(scanned)} file kunci USB dongle di sistem:")
                dongle_choice = st.selectbox("Pilih file kunci dongle:", [str(p) for p in scanned], label_visibility="collapsed", key="sel_dongle_path")
            else:
                st.caption("USB fisik belum terdeteksi otomatis. Masukkan path file atau upload file dongle:")
                up_dongle = st.file_uploader("Upload sentix_dongle.key:", type=["key", "json"], key="up_dongle_login")
                if up_dongle:
                    temp_p = DATA_DIR / "temp_dongle.key"
                    temp_p.parent.mkdir(parents=True, exist_ok=True)
                    with open(temp_p, "wb") as f:
                        f.write(up_dongle.read())
                    dongle_choice = str(temp_p)

            col_btn1, col_btn2 = st.columns([1.2, 1])
            with col_btn1:
                if st.button("Verifikasi Kunci Dongle", use_container_width=True, key="btn_verif_dongle"):
                    if dongle_choice:
                        ok, msg, payload = DongleVerifier.verify_dongle_path(dongle_choice)
                        if ok:
                            st.session_state.dongle_verified = True
                            st.success(msg)
                            st.rerun()
                        else:
                            st.error(msg)
                    else:
                        st.error("Tentukan atau upload file dongle terlebih dahulu.")
            with col_btn2:
                if st.button("Bypass Dongle (Dev Mode)", use_container_width=True, key="btn_bypass_dongle"):
                    st.session_state.dongle_verified = True
                    st.success("Hardware dongle bypassed untuk mode pengujian.")
                    st.rerun()

            col_ds1, col_ds2 = st.columns([2, 1])
            with col_ds1:
                if st.session_state.dongle_verified:
                    st.markdown("<span class='badge-pill badge-success'>STATUS DONGLE: TERHUBUNG</span>", unsafe_allow_html=True)
                else:
                    st.markdown("<span class='badge-pill badge-warning'>STATUS DONGLE: BELUM TERHUBUNG</span>", unsafe_allow_html=True)
            with col_ds2:
                if st.session_state.dongle_verified and st.button("Reset Dongle", key="btn_rst_dongle"):
                    st.session_state.dongle_verified = False
                    st.session_state.biometric_verified = False
                    st.session_state.password_verified = False
                    st.session_state.authenticated_officer = "N/A"
                    st.rerun()

        # STEP 2: BIOMETRIC FACE VERIFICATION (Clean Single Camera UI)
        with st.container(border=True):
            st.markdown("#### Tahap 2: Biometrik Wajah Petugas Kustodi")
            
            col_bs1, col_bs2 = st.columns([2, 1])
            with col_bs1:
                if st.session_state.biometric_verified:
                    st.markdown(f"<span class='badge-pill badge-success'>STATUS BIOMETRIK: TERVERIFIKASI</span> <small>{st.session_state.authenticated_officer}</small>", unsafe_allow_html=True)
                else:
                    st.markdown("<span class='badge-pill badge-warning'>STATUS BIOMETRIK: BELUM DIVERIFIKASI</span>", unsafe_allow_html=True)
            with col_bs2:
                if st.button("Reset Biometrik", key="btn_rst_biometric"):
                    st.session_state.biometric_verified = False
                    st.session_state.authenticated_officer = "N/A"
                    st.session_state.last_bio_result = None
                    st.session_state.last_cam_hash = None
                    st.session_state.last_up_hash = None
                    st.rerun()

            if not st.session_state.dongle_verified:
                st.caption("Selesaikan verifikasi Tahap 1 (Dongle USB) terlebih dahulu.")
            else:
                bio_method = st.radio("Metode Capture Wajah:", ["Webcam Live", "Upload Foto", "Simulasi Dev"], horizontal=True, key="bio_method_radio")

                if bio_method == "Webcam Live":
                    st.caption("Posisikan wajah menghadap webcam dengan pencahayaan memadai, lalu tekan tombol foto di bawah:")
                    cam_file = st.camera_input("Kamera Pemindaian Biometrik:", key="cam_login_input")

                    if cam_file is not None:
                        file_bytes = cam_file.getvalue()
                        photo_hash = hashlib.md5(file_bytes).hexdigest()
                        if st.session_state.get("last_cam_hash") != photo_hash:
                            st.session_state.last_cam_hash = photo_hash
                            probe_img = Image.open(cam_file)
                            ok, dist, msg = BiometricVerifier.verify_face(probe_img)
                            st.session_state.biometric_verified = ok
                            st.session_state.authenticated_officer = msg
                            st.session_state.last_bio_result = {"ok": ok, "dist": dist, "msg": msg}
                            st.rerun()
                    else:
                        if st.session_state.get("last_cam_hash") is not None:
                            st.session_state.last_cam_hash = None
                            st.session_state.biometric_verified = False
                            st.session_state.authenticated_officer = "N/A"
                            st.session_state.last_bio_result = None
                            st.rerun()

                elif bio_method == "Upload Foto":
                    up_file = st.file_uploader("Upload foto wajah:", type=["jpg", "jpeg", "png"], key="up_login_input")
                    if up_file is not None:
                        file_bytes = up_file.getvalue()
                        file_hash = hashlib.md5(file_bytes).hexdigest()
                        if st.session_state.get("last_up_hash") != file_hash:
                            st.session_state.last_up_hash = file_hash
                            probe_img = Image.open(up_file)
                            ok, dist, msg = BiometricVerifier.verify_face(probe_img)
                            st.session_state.biometric_verified = ok
                            st.session_state.authenticated_officer = msg
                            st.session_state.last_bio_result = {"ok": ok, "dist": dist, "msg": msg}
                            st.rerun()
                    else:
                        if st.session_state.get("last_up_hash") is not None:
                            st.session_state.last_up_hash = None
                            st.session_state.biometric_verified = False
                            st.session_state.authenticated_officer = "N/A"
                            st.session_state.last_bio_result = None
                            st.rerun()

                else:
                    if st.button("Verifikasi Biometrik (Simulasi Cocok - Dev Mode)", key="btn_sim_ok"):
                        st.session_state.biometric_verified = True
                        st.session_state.authenticated_officer = "Biometrik Terverifikasi: Oktavian Prasetya Adi (Simulasi)"
                        st.session_state.last_bio_result = {
                            "ok": True,
                            "dist": 0.05,
                            "msg": "Biometrik Terverifikasi: Oktavian Prasetya Adi (Mode Simulasi Pengujian)",
                        }
                        st.rerun()

                # Result Feedback Card
                if st.session_state.get("last_bio_result"):
                    res = st.session_state.last_bio_result
                    col_m1, col_m2 = st.columns(2)
                    with col_m1:
                        st.metric("Cosine Distance", f"{res['dist']:.4f}", help="Ambang Batas <= 0.32 untuk verifikasi valid")
                    with col_m2:
                        conf = max(0.0, round((1.0 - res['dist']) * 100, 2))
                        st.metric("Tingkat Kecocokan", f"{conf}%")

                    if res["ok"]:
                        st.success(res["msg"])
                    else:
                        st.error(res["msg"])

        # STEP 3: MASTER PASSWORD & KEY DERIVATION
        with st.container(border=True):
            st.markdown("#### Tahap 3: Master Password & BIP-39 Key Derivation")
            if not (st.session_state.dongle_verified and st.session_state.biometric_verified):
                st.caption("Selesaikan verifikasi Tahap 1 (Dongle) dan Tahap 2 (Biometrik) terlebih dahulu.")
            else:
                pwd_input = st.text_input("Master Password (Bawaan: `Sentix@2026!`):", type="password", key="master_pwd_input")
                if st.button("Otorisasi & Buka Aegis Cold Custody", use_container_width=True, key="btn_unlock_vault"):
                    ok, msg, master_key = PasswordVerifier.verify_password(pwd_input)
                    if ok:
                        st.session_state.password_verified = True
                        st.session_state.master_session_key = master_key
                        st.session_state.is_dev_mode = False
                        st.session_state.authenticated = True
                        st.success("Autentikasi 3FA Sempurna. Menginisialisasi workstation cold wallet...")
                        time.sleep(0.4)
                        st.rerun()
                    else:
                        st.error(f"Gagal: {msg}")


# =====================================================================
# FLOW 2: USER REGISTRATION (ONBOARDING FLOW)
# =====================================================================

def render_registration_flow():
    st.subheader("Registrasi Petugas Kustodi & Penerbitan Hardware Key HSM")
    st.markdown("""
    Alur pendaftaran resmi untuk petugas cold custody baru:
    Identitas Petugas $\\rightarrow$ Hash Password PBKDF2 $\\rightarrow$ Perekaman Biometrik Wajah $\\rightarrow$ Unduh Kunci Fisik USB Dongle.
    """)

    col_reg1, col_reg2 = st.columns([1.1, 1], gap="large")

    with col_reg1:
        with st.container(border=True):
            st.markdown("#### Langkah 1 & 2: Identitas & Password Petugas")
            reg_name = st.text_input("Nama Lengkap Petugas:", value="Oktavian Prasetya Adi (123240135)", key="reg_name_input")
            reg_uid = st.text_input("User ID Petugas (ID unik tanpa spasi):", value="oktavian", key="reg_uid_input")
            
            col_p1, col_p2 = st.columns(2)
            with col_p1:
                reg_pwd1 = st.text_input("Buat Master Password:", type="password", value="Sentix@2026!", key="reg_pwd1_input")
            with col_p2:
                reg_pwd2 = st.text_input("Konfirmasi Password:", type="password", value="Sentix@2026!", key="reg_pwd2_input")

        with st.container(border=True):
            st.markdown("#### Langkah 3: Perekaman Biometrik Wajah")
            st.caption("Posisikan wajah menghadap webcam dengan pencahayaan memadai, lalu ambil foto:")
            reg_cam_file = st.camera_input("Kamera Registrasi Biometrik Wajah:", key="reg_cam_input")

            # Fallback upload option
            with st.expander("Opsi Alternatif: Upload Citra Wajah"):
                reg_up_file = st.file_uploader("Pilih file foto wajah resmi (.jpg, .png):", type=["jpg", "jpeg", "png"], key="reg_up_input")

    with col_reg2:
        with st.container(border=True):
            st.markdown("#### Langkah 4: Finalisasi Pendaftaran & Unduh Dongle")
            st.caption("Setelah data terisi dan foto wajah diambil, klik tombol di bawah untuk menerbitkan akun dan kunci token USB:")

            face_source = None
            if reg_cam_file is not None:
                face_source = Image.open(reg_cam_file)
                st.info("Citra wajah dari webcam siap didaftarkan.")
            elif 'reg_up_file' in locals() and reg_up_file is not None:
                face_source = Image.open(reg_up_file)
                st.info("Citra wajah dari berkas upload siap didaftarkan.")
            else:
                st.warning("Silakan ambil foto wajah pada Langkah 3 terlebih dahulu.")

            if st.button("Daftarkan Akun & Terbitkan Kunci Dongle", use_container_width=True, key="btn_execute_registration"):
                if not reg_name or not reg_uid:
                    st.error("Nama Lengkap dan User ID wajib diisi.")
                elif not reg_pwd1 or reg_pwd1 != reg_pwd2:
                    st.error("Password tidak cocok atau kosong. Periksa kembali konfirmasi password.")
                elif face_source is None:
                    st.error("Foto wajah belum diambil! Silakan ambil foto wajah pada kamera di Langkah 3.")
                else:
                    try:
                        # 1. Enroll Face to Multi-Face Roster
                        BiometricVerifier.enroll_face(face_source, user_id=reg_uid, name=reg_name)

                        # 2. Register PBKDF2 Password Account
                        PasswordVerifier.register_account(reg_uid, reg_name, reg_pwd1)

                        # 3. Generate Hardware Dongle Token
                        dongle_token = DongleVerifier.generate_dongle_token(vault_id=f"AEGIS-{reg_uid.upper()}", holder_name=reg_name)
                        st.session_state.latest_registered_dongle = json.dumps(dongle_token, indent=2).encode("utf-8")
                        st.session_state.registration_success_info = f"Akun **{reg_name}** (`{reg_uid}`) berhasil didaftarkan ke sistem!"
                        st.rerun()
                    except Exception as e:
                        st.error(f"Pendaftaran gagal: {e}")

            if st.session_state.get("registration_success_info"):
                st.success(st.session_state["registration_success_info"])
                st.markdown("---")
                st.markdown("##### 🔑 Unduh Kunci Hardware Security Dongle (HSM):")
                st.caption("Unduh berkas di bawah dan simpan ke flashdisk USB Anda:")
                st.download_button(
                    label="⬇️ Unduh Kunci Dongle USB (sentix_dongle.key)",
                    data=st.session_state.get("latest_registered_dongle", b""),
                    file_name="sentix_dongle.key",
                    mime="application/json",
                    use_container_width=True,
                    key="btn_download_new_dongle"
                )

                st.info("Setelah mengunduh kunci, buka menu **'1. Masuk (Login 3FA)'** untuk login ke workstation.")


# =====================================================================
# FLOW 3: DEVELOPER & DOSEN EVALUATION SANDBOX
# =====================================================================

def render_developer_flow():
    st.subheader("Mode Pengembang & Sandbox Evaluasi Dosen")
    st.markdown("""
    Panel evaluasi akademis untuk pengujian sistem Tugas Akhir Kriptografi.
    Menampilkan pemenuhan 7 kriteria kurikulum, inspeksi basis data fisik di disk, dan pintasan pengujian cepat dalam lingkungan sandbox terisolasi.
    """)

    col_d1, col_d2 = st.columns([1.2, 1], gap="large")

    with col_d1:
        with st.container(border=True):
            st.markdown("#### Matriks Pemenuhan 7 Kriteria Tugas Akhir Kriptografi")
            matrix_data = [
                {"Kriteria Dosen": "1. Login Biometric & Hanya Hidup dengan Dongle", "Implementasi di Aegis Cold Custody": "Air-Gapped 3FA: USB Hardware Key (HMAC-SHA256) + Face Verification", "Silabus": "NIST SP 800-63B"},
                {"Kriteria Dosen": "2. Login Menggunakan Algoritma Kriptografi", "Implementasi di Aegis Cold Custody": "PBKDF2-HMAC-SHA256 (100.000 iterasi) untuk derivasi Master Key dari PIN", "Silabus": "Materi 8: Hash"},
                {"Kriteria Dosen": "3. Pesan Teks: Super Enkripsi (Klasik + Modern)", "Implementasi di Aegis Cold Custody": "BIP-39 Mnemonic Armor: Caesar -> Vigenere -> Vernam XOR -> AES-128 CBC", "Silabus": "Materi 3, 4, 6 & 7"},
                {"Kriteria Dosen": "4. Pesan File: Algoritma Beda dari Teks", "Implementasi di Aegis Cold Custody": "Keystore File (.json/.dat) dienkripsi Stream Cipher RC4 (KSA + PRGA)", "Silabus": "Materi 7: Stream RC4"},
                {"Kriteria Dosen": "5. Pesan Penting Dienkripsi pada Basisdata", "Implementasi di Aegis Cold Custody": "Whitelisted Address Book di SQLite dengan Authenticated AES-256-GCM AEAD", "Silabus": "Materi 6 & 7: Modern AEAD"},
                {"Kriteria Dosen": "6. Pesan Gambar Diamankan Steganografi", "Implementasi di Aegis Cold Custody": "Stego Paper Wallet / NFT Camouflage via Spatial LSB (PSNR > 65 dB & MSE)", "Silabus": "Materi 9: Steganografi"},
                {"Kriteria Dosen": "7. Aset Penting Diamankan Blockchain Sederhana", "Implementasi di Aegis Cold Custody": "Cold Wallet On-Chain Transaction Ledger SHA-256 PoW + Tamper Detection", "Silabus": "Materi 8: Hash & Chain"},
            ]
            st.table(matrix_data)

        with st.container(border=True):
            st.markdown("#### Inspektur Basis Data SQLite Fisik (Raw Ciphertext On-Disk)")
            st.caption("Membuktikan kepada dosen penguji bahwa record sensitif di SQLite tersimpan murni dalam bentuk terenkripsi AES-256-GCM:")
            raws = get_raw_database_records()
            if raws:
                st.table(raws)
            else:
                st.info("Database saat ini masih kosong.")

    with col_d2:
        with st.container(border=True):
            st.markdown("#### Pintasan Pengujian Cepat (1-Click Fast Bypass - Sandbox Mode)")
            st.caption("Gunakan tombol ini saat demonstrasi jika dosen ingin langsung menguji modul kriptografi tanpa proses pemindaian fisik:")
            
            if st.button("⚡ 1-Click Fast Bypass ke Dashboard Sandbox", use_container_width=True, key="dev_fast_bypass"):
                st.session_state.dongle_verified = True
                st.session_state.biometric_verified = True
                st.session_state.password_verified = True
                st.session_state.authenticated_officer = "Oktavian Prasetya Adi (Sandbox Mode)"
                st.session_state.master_session_key = hashlib.sha256(b"AegisSandboxBypassKey2026").hexdigest()
                st.session_state.is_dev_mode = True
                st.session_state.authenticated = True
                st.rerun()

            if st.button("🔄 Reset Seluruh Sesi & Status Auth", use_container_width=True, key="dev_full_reset"):
                st.session_state.dongle_verified = False
                st.session_state.biometric_verified = False
                st.session_state.password_verified = False
                st.session_state.authenticated_officer = "N/A"
                st.session_state.master_session_key = None
                st.session_state.is_dev_mode = False
                st.session_state.authenticated = False
                st.session_state.last_bio_result = None
                st.session_state.last_cam_hash = None
                st.session_state.last_up_hash = None
                st.rerun()

            st.markdown("---")
            st.markdown("##### Generator Virtual Dongle:")
            st.caption("Membuat file dongle virtual di `data/dongle/sentix_dongle.key` jika tidak menggunakan flashdisk fisik:")
            if st.button("Buat Virtual Dongle di Folder Lokal (data/dongle/)", use_container_width=True, key="dev_mk_dongle"):
                p = DongleVerifier.write_dongle_to_path(DATA_DIR / "dongle", holder_name="Oktavian Prasetya Adi & Grace Rianty Butar Butar")
                st.success(f"Virtual dongle berhasil dibuat di: `{p}`")
                st.rerun()


# =====================================================================
# MAIN AUTHENTICATED DASHBOARD (5 CRYPTO MODULES)
# =====================================================================

def render_main_dashboard():
    st.markdown("<h2 style='margin-bottom: 2px;'>AEGIS COLD CUSTODY &mdash; AIR-GAPPED WORKSTATION</h2>", unsafe_allow_html=True)
    st.caption("Status Sistem: Terkunci pada Hardware Token USB | Sesi Biometrik Terverifikasi | Enkripsi End-to-End Tugas Akhir Kriptografi")

    col_b1, col_b2, col_b3, col_b4 = st.columns([1.2, 1, 1, 1])
    with col_b1:
        officer_disp = st.session_state.authenticated_officer.split('(')[0].replace('Biometrik Terverifikasi:', '').strip()[:24]
        st.markdown(f"<span class='badge-pill badge-success'>OFFICER: {officer_disp}</span>", unsafe_allow_html=True)
    with col_b2:
        st.markdown("<span class='badge-pill badge-hsm'>HSM DONGLE: CONNECTED</span>", unsafe_allow_html=True)
    with col_b3:
        if st.session_state.get("is_dev_mode", False):
            st.markdown("<span class='badge-pill badge-warning'>MODE: SANDBOX ISOLATED</span>", unsafe_allow_html=True)
        else:
            st.markdown("<span class='badge-pill badge-success'>MODE: SECURE PRODUCTION</span>", unsafe_allow_html=True)
    with col_b4:
        if st.button("Kunci Workstation (Logout)", use_container_width=True, key="btn_logout_main"):
            st.session_state.authenticated = False
            st.session_state.dongle_verified = False
            st.session_state.biometric_verified = False
            st.session_state.password_verified = False
            st.session_state.master_session_key = None
            st.session_state.authenticated_officer = "N/A"
            st.session_state.is_dev_mode = False
            st.session_state.last_bio_result = None
            st.session_state.last_cam_hash = None
            st.session_state.last_up_hash = None
            st.rerun()

    if st.session_state.get("is_dev_mode", False):
        st.warning("⚠️ **MODE PENGEMBANG (SANDBOX AKTIF)**: Anda masuk melalui bypass evaluasi. Demi kepatuhan Zero-Trust Security, akses ke data riil produksi diblokir dan dialihkan ke mock data simulasi.")

    st.markdown("---")

    # 5 Core Cryptographic Tabs
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "1. Mnemonic Seed Armor (Super-Enkripsi)",
        "2. Keystore Vault (RC4)",
        "3. Stego Paper Wallet",
        "4. Blockchain Ledger Aset",
        "5. Whitelisted Address Book"
    ])

    # -----------------------------------------------------------------
    # TAB 1: MNEMONIC SEED ARMOR (SUPER ENKRIPSI 4-TAHAP)
    # -----------------------------------------------------------------
    with tab1:
        st.subheader("BIP-39 Mnemonic Seed Phrase Armor (Super-Enkripsi 4-Tahap)")
        st.info("""
        **Rujukan: Materi 3 (Caesar), Materi 4 (Vigenère), Materi 7 (Vernam Stream), dan Materi 6/7 (Block Cipher AES):**
        Menyandi 12/24 kata pemulihan dompet kripto (*BIP-39 Seed Phrase*) agar kebal terhadap malware pencuri memori clipboard.
        - **Tahap 1:** Caesar Cipher (Monoalfabetik) — *Grace Rianty Butar Butar (123240036)*
        - **Tahap 2:** Vigenère Cipher (Polialfabetik) — *Grace Rianty Butar Butar (123240036)*
        - **Tahap 3:** Vernam Stream Cipher (Bitwise XOR Keystream) — *Oktavian Prasetya Adi (123240135)*
        - **Tahap 4:** AES-128 Block Cipher (CBC Mode + PKCS7 Padding) — *Oktavian Prasetya Adi (123240135)*
        """)

        mode_super_pilihan = st.radio(
            "Pilih Skema Super-Enkripsi Seed Phrase:",
            [
                "Pipeline 4-Tahap Lengkap (Caesar ➔ Vigenère ➔ Vernam Stream ➔ AES-128)",
                "Super Enkripsi 2-Tahap Cepat (Vigenère + AES-256-CBC)",
            ],
            horizontal=True,
            key="rad_super_scheme",
        )

        if mode_super_pilihan.startswith("Pipeline 4-Tahap"):
            col_4enc, col_4dec = st.columns(2, gap="large")

            with col_4enc:
                with st.container(border=True):
                    st.markdown("#### Enkripsi 4-Tahap Seed Phrase")
                    st.caption("12 kata rahasia diproses melewati 4 lapisan kriptografi klasik dan modern:")
                    plain_4 = st.text_area(
                        "12 Kata Pemulihan Dompet (BIP-39 Seed):",
                        "witch collapse practice feed shame open despair creek road again ice cheese",
                        key="sup4_plain_in",
                        height=90
                    )

                    col_k_a, col_k_b = st.columns(2)
                    with col_k_a:
                        k_c_shift = st.number_input("1. Caesar Shift k (Grace):", min_value=1, max_value=25, value=8, key="k_c_shift_in")
                        k_v_key = st.text_input("2. Kunci Vigenère (Grace):", value="UPN2026", key="k_v_key_in")
                    with col_k_b:
                        k_vernam = st.text_input("3. Keystream Vernam (Okta):", value="VERNAM", key="k_vernam_in")
                        k_aes_key = st.text_input("4. Kunci AES-128 (Okta):", value="mysecretkey12345", key="k_aes_key_in")

                    if st.button("Eksekusi Pipeline 4-Tahap", use_container_width=True, key="btn_exec_4stage_enc"):
                        if plain_4 and k_v_key and k_vernam and k_aes_key:
                            try:
                                res4 = super_encrypt_4stage(plain_4, k_c_shift, k_v_key, k_vernam, k_aes_key)
                                st.success("Pipeline 4-Tahap Berhasil Mengamankan Seed Phrase!")

                                st.markdown("##### Tabel Transformasi Tiap Tahap:")
                                st.table(res4["stages"])

                                st.markdown("**Cipherteks Akhir (Base64 Armored Envelope):**")
                                st.code(res4["final_cipher"], language="text")
                            except Exception as e:
                                st.error(f"Gagal enkripsi: {e}")
                        else:
                            st.error("Lengkapi seluruh seed phrase dan parameter kunci.")

            with col_4dec:
                with st.container(border=True):
                    st.markdown("#### Pemulihan Dekripsi 4-Tahap")
                    st.caption("Pembalikan berurutan: AES-128 Decrypt ➔ Vernam XOR ➔ Vigenère Decrypt ➔ Caesar Decrypt:")
                    cipher_4_in = st.text_area("Cipherteks Input (Base64):", "", key="sup4_cipher_in", height=90)

                    col_dk_a, col_dk_b = st.columns(2)
                    with col_dk_a:
                        dk_c_shift = st.number_input("1. Caesar Shift k:", min_value=1, max_value=25, value=8, key="dk_c_shift_in")
                        dk_v_key = st.text_input("2. Kunci Vigenère:", value="UPN2026", key="dk_v_key_in")
                    with col_dk_b:
                        dk_vernam = st.text_input("3. Keystream Vernam:", value="VERNAM", key="dk_vernam_in")
                        dk_aes_key = st.text_input("4. Kunci AES-128:", value="mysecretkey12345", key="dk_aes_key_in")

                    if st.button("Eksekusi Pembalik 4-Tahap", use_container_width=True, key="btn_exec_4stage_dec"):
                        if cipher_4_in and dk_v_key and dk_vernam and dk_aes_key:
                            try:
                                dec4 = super_decrypt_4stage(cipher_4_in.strip(), dk_c_shift, dk_v_key, dk_vernam, dk_aes_key)
                                st.success("Seluruh 4 Tahap Pembalik Berhasil!")

                                st.markdown("##### Alur Rekonstruksi Tiap Tahap:")
                                st.table(dec4["stages_dec"])

                                st.markdown("**12 Kata Seed Phrase Asli Pulih Sempurna:**")
                                st.success(dec4["final_plaintext"])
                            except Exception as e:
                                st.error(f"Gagal Dekripsi: {e} (Format tidak valid atau parameter kunci salah)")
                        else:
                            st.error("Masukkan cipherteks dan parameter seluruh kunci.")

        else:
            col_enc, col_dec = st.columns(2, gap="large")

            with col_enc:
                with st.container(border=True):
                    st.markdown("#### Enkripsi 2-Tahap Ringkas")
                    plain_input = st.text_area("Plainteks Seed / Private Key:", "0x4f3edf983ac636a65a842ce7c78d9aa706d3b113bce9c46f30d7d21715b23b1d", key="se_plain_input")
                    col_k1, col_k2 = st.columns(2)
                    with col_k1:
                        k_classical = st.text_input("Kunci Vigenère (Grace):", "UPN2026", key="se_k_classical")
                    with col_k2:
                        k_modern = st.text_input("Passphrase AES-256 (Okta):", "AegisColdMasterPassphrase!", key="se_k_modern")

                    if st.button("Eksekusi Super-Enkripsi", use_container_width=True, key="btn_exec_super_enc"):
                        if plain_input and k_classical and k_modern:
                            res = super_encrypt(plain_input, k_classical, k_modern)
                            st.success("Enkripsi Dua Lapis Berhasil!")

                            st.markdown("**Tahap 1 &mdash; Output Vigenère:**")
                            st.code(res["vigenere_output"], language="text")

                            st.markdown("**Tahap 2 &mdash; Output Final AES-256-CBC:**")
                            st.code(res["final_ciphertext_base64"], language="text")
                            st.caption(f"IV (Hex): {res['iv_hex']}")
                        else:
                            st.error("Lengkapi seluruh kolom teks dan kunci.")

            with col_dec:
                with st.container(border=True):
                    st.markdown("#### Dekripsi 2-Tahap")
                    cipher_input = st.text_area("Cipherteks Base64:", "", key="se_cipher_input")
                    col_dk1, col_dk2 = st.columns(2)
                    with col_dk1:
                        dk_classical = st.text_input("Kunci Vigenère:", "UPN2026", key="dec_vig_input")
                    with col_dk2:
                        dk_modern = st.text_input("Passphrase AES-256:", "AegisColdMasterPassphrase!", key="dec_aes_input")

                    if st.button("Eksekusi Super-Dekripsi", use_container_width=True, key="btn_exec_super_dec"):
                        if cipher_input and dk_classical and dk_modern:
                            try:
                                dres = super_decrypt(cipher_input.strip(), dk_classical, dk_modern)
                                st.success("Dekripsi Berhasil!")
                                st.markdown("**Plainteks Asli Pulih:**")
                                st.success(dres["final_plaintext"])
                            except Exception as e:
                                st.error(f"Gagal Dekripsi: {e}")
                        else:
                            st.error("Masukkan cipherteks dan kedua kunci.")

    # -----------------------------------------------------------------
    # TAB 2: ENKRIPSI KEYSTORE FILE (RC4 Stream Cipher)
    # -----------------------------------------------------------------
    with tab2:
        st.subheader("Brankas Berkas Keystore: Stream Cipher RC4")
        st.info("""
        **Rujukan: Materi 7 (Stream Cipher & Algoritma RC4):**
        Spesifikasi mewajibkan enkripsi berkas menggunakan algoritma yang **berbeda dari teks**. 
        Berkas biner cadangan dompet (seperti `keystore.json`, `.dat`, atau `.key`) dienkripsi bit-per-byte menggunakan **RC4 (KSA + PRGA)**.
        """)

        file_mode = st.radio("Pilih Operasi Berkas Keystore:", ["Enkripsi Berkas Keystore", "Dekripsi Berkas Keystore (.enc)"], horizontal=True, key="file_mode_radio")

        if file_mode == "Enkripsi Berkas Keystore":
            with st.container(border=True):
                up_raw = st.file_uploader("Pilih Berkas Keystore / Private Key (.json, .dat, .key):", type=None, key="raw_file_uploader")
                rc4_pwd = st.text_input("Passphrase Kunci RC4:", "RC4ColdKeystoreProtectionKey!", key="rc4_enc_key")

                if up_raw and rc4_pwd:
                    if st.button("Enkripsi Berkas via RC4", use_container_width=True, key="btn_enc_rc4_file"):
                        raw_data = up_raw.read()
                        enc_data = encrypt_file_bytes(raw_data, up_raw.name, rc4_pwd)
                        st.success(f"Berkas keystore berhasil dienkripsi! Ukuran: {len(enc_data)} bytes.")
                        st.download_button(
                            label="Unduh Berkas Terenkripsi (.enc)",
                            data=enc_data,
                            file_name=f"{up_raw.name}.enc",
                            mime="application/octet-stream",
                            use_container_width=True
                        )
        else:
            with st.container(border=True):
                up_enc = st.file_uploader("Upload Berkas Terenkripsi (.enc):", type=None, key="enc_file_uploader")
                rc4_dec_pwd = st.text_input("Passphrase Kunci RC4:", "RC4ColdKeystoreProtectionKey!", key="rc4_dec_key")

                if up_enc and rc4_dec_pwd:
                    if st.button("Dekripsi Berkas via RC4", use_container_width=True, key="btn_dec_rc4_file"):
                        try:
                            enc_data = up_enc.read()
                            dec_bytes, orig_name = decrypt_file_bytes(enc_data, rc4_dec_pwd)
                            st.success(f"Berkas berhasil didekripsi! Nama asli dipulihkan: {orig_name}")
                            st.download_button(
                                label=f"Unduh Berkas Pulih ({orig_name})",
                                data=dec_bytes,
                                file_name=orig_name,
                                mime="application/octet-stream",
                                use_container_width=True
                            )
                        except Exception as e:
                            st.error(f"Gagal dekripsi berkas: {e}")

    # -----------------------------------------------------------------
    # TAB 3: STEGANOGRAFI PAPER WALLET (Spatial LSB)
    # -----------------------------------------------------------------
    with tab3:
        st.subheader("Stego Paper Wallet & NFT Camouflage (Spatial LSB)")
        st.info("""
        **Rujukan: Materi 9 (Steganografi Citra Digital - Spatial Domain):**
        Menyamarkan 12 kata seed phrase ke dalam bit terendah (LSB) kanal RGB avatar NFT atau kartu paper wallet.
        Dilengkapi pengujian rasio **PSNR > 65 dB** dan **MSE $\\approx 0$** untuk membuktikan bahwa penyamaran tidak menimbulkan distorsi kasat mata.
        """)

        stego_tab1, stego_tab2 = st.tabs(["Sisipkan Seed ke Gambar (Encode)", "Ekstrak Seed dari Gambar (Decode)"])

        with stego_tab1:
            col_s1, col_s2 = st.columns(2, gap="large")
            with col_s1:
                with st.container(border=True):
                    stego_cover = st.file_uploader("Pilih Gambar Sampul (Avatar NFT / Card):", type=["png", "bmp", "jpg"], key="stego_cover_up")
                    secret_msg = st.text_area(
                        "12 Kata Seed Phrase yang Disamarkan:",
                        "witch collapse practice feed shame open despair creek road again ice cheese",
                        key="stego_secret_text"
                    )
                    if stego_cover:
                        cov_img = Image.open(stego_cover)
                        st.image(cov_img, caption="Cover Image Asli", use_container_width=True)

            with col_s2:
                if stego_cover and secret_msg:
                    with st.container(border=True):
                        if st.button("Sisipkan Seed Phrase ke Citra (LSB)", use_container_width=True, key="btn_stego_embed"):
                            try:
                                cov_img = Image.open(stego_cover)
                                stego_res, metrics = embed_secret_message(cov_img, secret_msg)
                                st.success("Seed Phrase Berhasil Disamarkan ke Citra!")
                                st.image(stego_res, caption="Stego Paper Wallet (Hasil LSB)", use_container_width=True)

                                st.markdown("##### Metrik Kualitas Citra Akademis:")
                                st.write(f"- **PSNR:** `{metrics['psnr_db']} dB` ({metrics['visual_quality']})")
                                st.write(f"- **MSE:** `{metrics['mse']}`")
                                st.write(f"- **Kapasitas Terpakai:** `{metrics['capacity_used_pct']}%` ({metrics['payload_bytes']} bytes)")

                                buf = BytesIO()
                                stego_res.save(buf, format="PNG")
                                st.download_button(
                                    label="Unduh Stego Paper Wallet (PNG)",
                                    data=buf.getvalue(),
                                    file_name="stego_paper_wallet.png",
                                    mime="image/png",
                                    use_container_width=True
                                )
                            except Exception as e:
                                st.error(f"Gagal menyisipkan seed: {e}")

        with stego_tab2:
            with st.container(border=True):
                stego_probe = st.file_uploader("Upload Stego Paper Wallet (PNG):", type=["png", "bmp"], key="stego_probe_up")
                if stego_probe:
                    p_img = Image.open(stego_probe)
                    st.image(p_img, caption="Stego-Image Terpilih", width=300)
                    if st.button("Ekstrak Seed Phrase Tersembunyi", use_container_width=True, key="btn_stego_extract"):
                        try:
                            recovered_msg = extract_secret_message(p_img)
                            st.success("Seed Phrase Berhasil Dipulihkan dari Piksel Gambar!")
                            st.code(recovered_msg, language="text")
                        except Exception as e:
                            st.error(f"Gagal mengekstrak pesan: {e}")

    # -----------------------------------------------------------------
    # TAB 4: BLOCKCHAIN INTEGRITAS ASET (PoW)
    # -----------------------------------------------------------------
    with tab4:
        st.subheader("Buku Besar Transaksi Cold Wallet (SHA-256 Proof-of-Work)")
        st.info("""
        **Rujukan: Materi 8 (Fungsi Hash Satu-Arah & Rantai Blok):**
        Mencatat riwayat mutasi aset digital institusi menggunakan rantai blok terdesentralisasi SHA-256 dengan konsensus Proof-of-Work (PoW).
        Dilengkapi alat uji coba simulasi peretasan saldo untuk demonstrasi deteksi tamper otomatis.
        """)

        bc = st.session_state.blockchain

        col_chain_stat, col_audit = st.columns([1.5, 1])
        with col_chain_stat:
            st.metric("Total Blok Terdaftar di Ledger", len(bc.chain))
        with col_audit:
            if st.button("Audit Integritas Rantai Blok", use_container_width=True, key="btn_audit_bc"):
                is_valid, report = bc.is_chain_valid()
                if is_valid:
                    st.success(report)
                else:
                    st.error(report)

        # Form Transaksi Baru
        with st.expander("Catat Transaksi Cold-to-Hot Transfer Baru"):
            col_tx1, col_tx2, col_tx3 = st.columns(3)
            with col_tx1:
                tx_sender = st.text_input("Alamat Pengirim:", "0x123240135_COLD_CUSTODY", key="bc_tx_sender")
            with col_tx2:
                tx_recipient = st.text_input("Alamat Penerima:", "0x71C8364437a5674366B0D5D690EAbc7C3E8d4239", key="bc_tx_recipient")
            with col_tx3:
                tx_asset = st.selectbox("Aset Kripto:", ["BTC", "ETH", "USDT", "SOL"], key="bc_tx_asset")
            
            col_tx4, col_tx5 = st.columns([1, 2])
            with col_tx4:
                tx_amount = st.number_input("Jumlah Aset:", min_value=0.01, value=2.5, step=0.1, key="bc_tx_amount")
            with col_tx5:
                tx_memo = st.text_input("Memo Settlement:", "Cold reserve liquidity release", key="bc_tx_memo")

            if st.button("Kirim ke Antrian Blok", key="btn_queue_tx"):
                bc.add_transaction(tx_sender, tx_recipient, tx_asset, tx_amount, tx_memo)
                st.success(f"Transaksi masuk antrian. Pending transactions: {len(bc.pending_transactions)}")

        # Mining Panel
        if bc.pending_transactions:
            st.warning(f"Terdapat {len(bc.pending_transactions)} transaksi pending menunggu konfirmasi blok.")
            if st.button("Tambang Blok Baru (Proof-of-Work)", use_container_width=True, key="btn_mine_bc"):
                with st.spinner("Menambang blok dengan target kesulitan hash SHA-256..."):
                    new_b = bc.mine_pending_transactions(miner_address="AEGIS_VALIDATOR_NODE")
                    st.success(f"Blok #{new_b.index} berhasil ditambang! Hash: {new_b.hash[:20]}... Nonce: {new_b.nonce}")
                    st.rerun()

        # Chain Explorer
        st.markdown("#### Rantai Blok Saat Ini")
        for b in reversed(bc.chain):
            with st.container(border=True):
                col_h1, col_h2 = st.columns([1, 2])
                with col_h1:
                    st.markdown(f"### Blok #{b.index}")
                    st.caption(f"Nonce: `{b.nonce}` | Waktu: `{time.ctime(b.timestamp)}`")
                with col_h2:
                    st.code(f"Hash      : {b.hash}\nPrev Hash : {b.previous_hash}", language="text")
                st.json(b.transactions)

        # Educational Tamper Injection
        with st.expander("Simulasi Serangan Manipulasi Saldo (Tamper Injection Demo)"):
            st.caption("Uji coba mengubah nilai transaksi pada blok yang sudah ditambang untuk melihat respon deteksi otomatis:")
            if len(bc.chain) > 1:
                target_idx = st.number_input("Pilih Index Blok untuk Dimanipulasi:", min_value=1, max_value=len(bc.chain)-1, value=1, key="bc_tamper_idx")
                fake_amt = st.number_input("Ganti Jumlah Saldo Menjadi:", value=999999.0, key="bc_tamper_amt")
                if st.button("Manipulasi Nilai Blok (Inject Tamper)", key="btn_inject_tamper"):
                    bc.tamper_block_for_demo(target_idx, fake_amt)
                    st.error(f"Blok #{target_idx} telah dirusak secara ilegal! Klik 'Audit Integritas Rantai Blok' di atas untuk melihat respon.")
            else:
                st.caption("Tambang minimal 1 blok baru untuk mencoba fitur simulasi tampering.")

    # -----------------------------------------------------------------
    # TAB 5: WHITELISTED ADDRESS BOOK & UTXO (SQLite + AES-256-GCM AEAD)
    # -----------------------------------------------------------------
    with tab5:
        st.subheader("Whitelisted Address Book & UTXO Store (SQLite + AES-256-GCM)")
        st.info("""
        **Sesuai Spesifikasi: Pesan/data penting dienkripsi pada basisdata yang digunakan.**
        Menyimpan daftar alamat dompet tujuan terpercaya dan UTXO cadangan di basis data SQLite lokal (`sentix_vault.db`). 
        Seluruh record dilindungi oleh **Authenticated Encryption AES-256-GCM** (Ciphertext + 96-bit IV + 128-bit Auth Tag).
        """)

        # SECURITY ENFORCEMENT: ISOLATE DEV MODE FROM REAL DATABASE
        if st.session_state.get("is_dev_mode", False):
            st.error("🔒 **AKSES BASIS DATA PRODUKSI DIBLOKIR PADA MODE PENGEMBANG (SANDBOX ISOLATION)**")
            st.markdown("""
            Sesuai standar keamanan *Air-Gapped Cold Custody*, master key yang dihasilkan dari pintasan pengujian (*Developer Bypass*) 
            **tidak memiliki otoritas untuk membuka basis data riil**.
            
            Berikut adalah **Data Simulasi Sandbox (Mock Test Records)** yang disiapkan khusus untuk evaluasi demonstrasi sidang:
            """)

            mock_sandbox_records = [
                {
                    "ID": 101,
                    "Kategori": "WHITELIST_ADDRESS",
                    "Label Rekaman": "Binance Institutional Cold Storage",
                    "Status Enkripsi": "AES-256-GCM (Simulated AEAD)",
                    "Data Alamat / Kunci (Sandbox)": "0x3f5CE5FBFe3E9af3971dD833D26bA9b5C936f0bE"
                },
                {
                    "ID": 102,
                    "Kategori": "RESERVE_SEED_PHRASE",
                    "Label Rekaman": "BIP-39 Testnet Recovery Mnemonic",
                    "Status Enkripsi": "AES-256-GCM (Simulated AEAD)",
                    "Data Alamat / Kunci (Sandbox)": "abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon about"
                },
                {
                    "ID": 103,
                    "Kategori": "UTXO_SIGNING_KEY",
                    "Label Rekaman": "Bitcoin Multisig Signer #2 Key",
                    "Status Enkripsi": "AES-256-GCM (Simulated AEAD)",
                    "Data Alamat / Kunci (Sandbox)": "xprv9s21ZrQH143K3QTDL4LXw2F7HEK3wJUD2nw2nR26Sf6GsW537926"
                }
            ]
            st.table(mock_sandbox_records)

            st.info("💡 **Catatan untuk Dosen Penguji:** Untuk melihat, menambah, atau memodifikasi data produksi riil, silakan logout dan lakukan autentikasi 3FA penuh menggunakan Kunci USB HSM + Biometrik Wajah + Master Password asli.")

        else:
            # LEGITIMATE PRODUCTION ACCESS
            with st.expander("Tambah Alamat Whitelist / Rekaman Kunci Baru"):
                d_title = st.text_input("Label Dompet / Judul Rekaman:", "Hot Reserve Liquidity Whitelist", key="db_rec_title")
                d_cat = st.selectbox("Kategori Aset:", ["WHITELISTED_ADDRESS", "RECOVERY_SEED", "PRIVATE_KEY", "MULTISIG_CONFIG"], key="db_rec_cat")
                d_secret = st.text_area("Data Sensitif (Alamat / Kunci Privat):", "0x71C8364437a5674366B0D5D690EAbc7C3E8d4239", key="db_rec_secret")
                
                if st.button("Simpan Terenkripsi ke Database (AES-256-GCM)", key="btn_save_db_rec"):
                    if d_title and d_secret:
                        active_key = st.session_state.master_session_key or "AegisDefaultMasterKey"
                        rid = insert_secret(d_title, d_cat, d_secret, active_key)
                        st.success(f"Alamat berhasil disimpan secara terenkripsi di database dengan ID #{rid}!")
                        st.rerun()

            # Database View Toggle
            view_mode = st.radio("Pilih Tampilan Database:", ["Tampilan Terdekripsi (Akses Petugas Berwenang)", "Tampilan Raw SQLite Fisik (Apa yang Dilihat Peretas di Disk)"], horizontal=True, key="db_view_toggle")

            if view_mode.startswith("Tampilan Terdekripsi"):
                active_key = st.session_state.master_session_key or "AegisDefaultMasterKey"
                records = get_all_secrets_decrypted(active_key)
                if records:
                    for r in records:
                        with st.container(border=True):
                            col_r1, col_r2 = st.columns([3, 1])
                            with col_r1:
                                st.markdown(f"**[{r['category']}] {r['title']}** (ID: `{r['id']}` - {r['account_id']})")
                                st.caption(f"Dibuat: {r['created_at']} | Status Verifikasi Tag: {r['decryption_status']}")
                                st.success(r["decrypted_secret"])
                            with col_r2:
                                if st.button(f"Hapus #{r['id']}", key=f"del_{r['id']}"):
                                    delete_record(r['id'])
                                    st.rerun()
                else:
                    st.info("Belum ada rekaman alamat di database.")
            else:
                st.markdown("##### Tampilan Fisik Tabel `vault_records` di SQLite (Raw Ciphertext On-Disk):")
                raws = get_raw_database_records()
                if raws:
                    st.table(raws)
                else:
                    st.info("Database masih kosong.")


# =====================================================================
# MAIN APP ROUTING (USER FLOW VS DEVELOPER FLOW)
# =====================================================================

def main():
    if not st.session_state.authenticated:
        st.markdown("<h1 style='text-align: center; letter-spacing: 0.05em; margin-bottom: 2px;'>AEGIS COLD CUSTODY</h1>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center; color: #94A3B8; font-size: 14px;'>Air-Gapped BIP-39 Mnemonic Seed Vault & Hardware Key Custodian</p>", unsafe_allow_html=True)
        st.markdown("<div style='text-align: center; margin-bottom: 16px;'><span class='badge-pill badge-info'>UPN VETERAN YOGYAKARTA</span><span class='badge-pill badge-info'>INFORMATIKA IF-B</span><span class='badge-pill badge-warning'>SYSTEM LOCKED</span></div>", unsafe_allow_html=True)
        st.markdown("---")

        # Top Workflow Navigation: User Login vs User Registration vs Developer Sandbox
        nav_choice = st.radio(
            "Pilih Alur Kerja (Workflow):",
            ["1. Masuk (Login 3FA)", "2. Registrasi Petugas Kustodi", "3. Mode Pengembang & Evaluasi Dosen"],
            horizontal=True,
            label_visibility="collapsed",
            key="top_flow_nav"
        )
        st.markdown("<br>", unsafe_allow_html=True)

        if nav_choice.startswith("1."):
            render_login_flow()
        elif nav_choice.startswith("2."):
            render_registration_flow()
        else:
            render_developer_flow()

    else:
        render_main_dashboard()


if __name__ == "__main__":
    main()

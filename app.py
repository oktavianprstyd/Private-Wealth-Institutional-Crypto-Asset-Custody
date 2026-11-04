"""Sentix Digital Vault - Streamlit Interactive Frontend Application
Integrated Cryptographic Workstation for UPN "Veteran" Yogyakarta Final Project.

Architecture & Complete System Flows:
1. User Flow:
   - Registrasi Akun (Nama, Password PBKDF2, Foto Wajah + Flash 2s, Unduh Dongle USB HMAC)
   - Masuk (3FA Gatekeeper: Dongle + Biometrik Multi-Officer + Password)
   - Dashboard (Super Enkripsi, File RC4, Stego LSB, Blockchain PoW, Database GCM)
2. Developer Flow:
   - Sandbox Evaluasi Dosen (Matriks 7 Kriteria Kriptografi Materi 1-9)
   - 1-Click Fast Testing Bypass
   - Inspektur Roster Biometrik & Basis Data SQLite Mentah (Ciphertext On-Disk)
"""

import streamlit as st
import streamlit.components.v1 as components
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
from core.database_vault import init_database, insert_secret, get_all_secrets_decrypted, get_raw_database_records, delete_record
from core.steganography import embed_secret_message, extract_secret_message
from core.blockchain import Blockchain

# Streamlit Page Configuration
st.set_page_config(
    page_title="Sentix Digital Vault | Crypto Custody",
    page_icon="[SNTX]",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Enterprise FinTech CSS
st.markdown("""
<style>
    .stApp {
        background-color: #0E1117;
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
    .flow-card {
        background-color: #161B22;
        border: 1px solid #30363D;
        border-radius: 8px;
        padding: 16px;
        margin-bottom: 12px;
    }
</style>
""", unsafe_allow_html=True)


# =====================================================================
# INLINE JAVASCRIPT: SYNCHRONIZED SCREEN FLASH ATOMIC INJECTOR
# =====================================================================

def render_synchronized_flash_injector():
    """Injects a synchronized screen flash button right above every
    stCameraInputButton (below the video preview) on both Login and Register pages.
    Flash synchronization flow:
      t=0ms: Fullscreen blinding white overlay appears (#FFFFFF)
      t=1000ms: Camera shutter is triggered at peak illumination
      t=2000ms: White overlay fades out and cleans up smoothly
    """
    components.html("""
    <script>
    (function() {
        const parentDoc = window.parent.document;
        if (!parentDoc) return;

        function injectFlashButtons() {
            const camBtns = parentDoc.querySelectorAll('[data-testid="stCameraInputButton"]');
            camBtns.forEach(function(camBtn) {
                const parent = camBtn.parentElement;
                if (!parent) return;

                let flashBtn = parent.querySelector('.sentix-sync-flash-btn');
                if (!flashBtn) {
                    flashBtn = parentDoc.createElement('button');
                    flashBtn.className = 'sentix-sync-flash-btn';
                    flashBtn.innerHTML = 'AMBIL FOTO DENGAN FLASH LAYAR (2 DETIK)';
                    flashBtn.style.cssText = `
                        display: block !important;
                        width: 100% !important;
                        margin: 10px 0 10px 0 !important;
                        padding: 12px 20px !important;
                        background: linear-gradient(135deg, #1E40AF, #2563EB) !important;
                        color: #FFFFFF !important;
                        border: 1px solid #3B82F6 !important;
                        border-radius: 8px !important;
                        font-weight: 700 !important;
                        font-size: 13px !important;
                        letter-spacing: 0.05em !important;
                        cursor: pointer !important;
                        box-shadow: 0 4px 14px rgba(37, 99, 235, 0.4) !important;
                        transition: all 0.2s ease !important;
                    `;

                    flashBtn.addEventListener('click', function(e) {
                        e.preventDefault();
                        e.stopPropagation();

                        // 1. Fullscreen intense white overlay (#FFFFFF)
                        let overlay = parentDoc.getElementById('sentix-sync-flash-screen');
                        if (!overlay) {
                            overlay = parentDoc.createElement('div');
                            overlay.id = 'sentix-sync-flash-screen';
                            overlay.style.cssText = `
                                position: fixed !important;
                                top: 0 !important; left: 0 !important;
                                width: 100vw !important; height: 100vh !important;
                                background-color: #FFFFFF !important;
                                z-index: 2147483647 !important;
                                opacity: 1 !important;
                                pointer-events: none !important;
                                transition: opacity 0.25s ease !important;
                            `;
                            parentDoc.body.appendChild(overlay);
                        } else {
                            overlay.style.display = 'block';
                            overlay.style.opacity = '1';
                        }

                        // 2. Wait 1000ms for monitor white light to illuminate face and webcam sensor to adapt
                        setTimeout(function() {
                            camBtn.click(); // Trigger shutter at peak illumination!

                            // 3. Keep white flash for another 1000ms (Total 2000ms)
                            setTimeout(function() {
                                if (overlay) {
                                    overlay.style.opacity = '0';
                                    setTimeout(function() {
                                        if (overlay && overlay.parentNode) {
                                            overlay.parentNode.removeChild(overlay);
                                        }
                                    }, 250);
                                }
                            }, 1000);
                        }, 1000);
                    });

                    // Insert right above the Take Photo button!
                    parent.insertBefore(flashBtn, camBtn);
                }
            });
        }

        injectFlashButtons();
        if (!window.__sentixFlashInterval) {
            window.__sentixFlashInterval = setInterval(injectFlashButtons, 350);
        }
    })();
    </script>
    """, height=0, width=0)


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
if "blockchain" not in st.session_state:
    st.session_state.blockchain = Blockchain()


# =====================================================================
# FLOW 1: USER LOGIN GATEWAY (3FA GATEKEEPER)
# =====================================================================

def render_login_flow():
    render_synchronized_flash_injector()

    col_info, col_gate = st.columns([1, 1.25], gap="large")

    with col_info:
        st.subheader("Protokol Akses 3-Faktor (3FA)")
        st.markdown("""
        Workstation Sentix Vault beroperasi di bawah arsitektur **Zero-Trust (NIST SP 800-63B)**. Akses hanya dibuka jika seluruh 3 faktor autentikasi berjenjang terpenuhi:
        
        * **Faktor 1 (Something You Have):** Kunci fisik USB Flashdisk berisi file token `sentix_dongle.key` yang ditandatangani dengan HMAC-SHA256.
        * **Faktor 2 (Something You Are):** Pemindaian biometrik geometri wajah multi-officer (*Cosine Distance* $\\le 0.32$), kompatibel di seluruh CPU/iGPU Intel Gen 12+ maupun GPU. Dilengkapi **Synchronized Screen Flash 2 Detik** untuk pencahayaan optimal.
        * **Faktor 3 (Something You Know):** Master Password dengan fungsi hash satu-arah PBKDF2-HMAC-SHA256 (100.000 iterasi) untuk derivasi Master Key sesi di RAM.
        """)

        with st.container(border=True):
            st.markdown("**Petugas Terdaftar di Sistem:**")
            roster = BiometricVerifier.list_enrolled_faces()
            if roster:
                for item in roster:
                    st.write(f"- **{item['name']}** (`{item['user_id']}`)")
            else:
                st.caption("Belum ada petugas terdaftar. Silakan buka menu '2. Registrasi Akun Petugas' di atas.")

            if not roster:
                st.markdown("---")
                if st.button("Daftarkan Akun Default (Dev Quickstart)", key="btn_quick_default"):
                    sample_face = Image.new("RGB", (64, 64), color=(180, 150, 120))
                    BiometricVerifier.enroll_face(sample_face, user_id="oktavian", name="Oktavian Prasetya Adi (123240135)")
                    PasswordVerifier.register_account("oktavian", "Oktavian Prasetya Adi (123240135)", "Sentix@2026!")
                    DongleVerifier.write_dongle_to_path(DATA_DIR / "dongle", holder_name="Oktavian Prasetya Adi (123240135)")
                    st.success("Akun default Oktavian berhasil didaftarkan!")
                    st.rerun()

    with col_gate:
        st.subheader("Verifikasi Autentikasi Masuk")

        # STEP 1: HARDWARE DONGLE
        with st.container(border=True):
            st.markdown("#### Tahap 1: Hardware USB Dongle")
            scanned = DongleVerifier.scan_possible_dongle_locations()
            
            dongle_choice = None
            if scanned:
                st.caption(f"Terdeteksi {len(scanned)} file kunci USB dongle di sistem:")
                dongle_choice = st.selectbox("Pilih file kunci dongle:", [str(p) for p in scanned], label_visibility="collapsed", key="sel_dongle_path")
            else:
                st.caption("USB fisik tidak terdeteksi otomatis. Masukkan path file atau upload file dongle:")
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
                    st.success("Dongle bypassed untuk mode pengujian.")
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

        # STEP 2: BIOMETRIC MULTI-FACE WITH SYNCHRONIZED FLASH
        with st.container(border=True):
            st.markdown("#### Tahap 2: Biometrik Wajah Multi-Officer")
            
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
                st.caption("Selesaikan verifikasi Tahap 1 (Dongle) terlebih dahulu.")
            else:
                bio_method = st.radio("Metode Capture Wajah:", ["Webcam Live", "Upload Foto", "Simulasi Dev"], horizontal=True, key="bio_method_radio")

                if bio_method == "Webcam Live":
                    st.caption("Posisikan wajah Anda ke kamera laptop. Tombol flash layar diletakkan tepat di atas tombol Take Photo:")
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
                        st.metric("Cosine Distance", f"{res['dist']:.4f}", help="Ambang Batas <= 0.32 untuk diterima")
                    with col_m2:
                        conf = max(0.0, round((1.0 - res['dist']) * 100, 2))
                        st.metric("Tingkat Kecocokan", f"{conf}%")

                    if res["ok"]:
                        st.success(res["msg"])
                    else:
                        st.error(res["msg"])
                        if "gelap" in res["msg"].lower() or "shutter" in res["msg"].lower():
                            st.warning("Sensor kamera mendeteksi kegelapan: Buka penutup fisik webcam dan gunakan tombol Flash Layar 2 Detik di atas tombol Take Photo.")

        # STEP 3: MASTER PASSWORD & KEY DERIVATION
        with st.container(border=True):
            st.markdown("#### Tahap 3: Master Password Vault")
            if not (st.session_state.dongle_verified and st.session_state.biometric_verified):
                st.caption("Selesaikan verifikasi Tahap 1 (Dongle) dan Tahap 2 (Biometrik) terlebih dahulu.")
            else:
                pwd_input = st.text_input("Master Password (Bawaan: `Sentix@2026!`):", type="password", key="master_pwd_input")
                if st.button("Otorisasi dan Buka Sentix Vault", use_container_width=True, key="btn_unlock_vault"):
                    ok, msg, master_key = PasswordVerifier.verify_password(pwd_input)
                    if ok:
                        st.session_state.password_verified = True
                        st.session_state.master_session_key = master_key
                        st.session_state.authenticated = True
                        st.success("Autentikasi 3FA Sempurna. Menginisialisasi brankas...")
                        time.sleep(0.4)
                        st.rerun()
                    else:
                        st.error(f"Gagal: {msg}")


# =====================================================================
# FLOW 2: USER REGISTRATION (ONBOARDING FLOW)
# =====================================================================

def render_registration_flow():
    render_synchronized_flash_injector()

    st.subheader("Registrasi Akun Petugas & Penerbitan Kunci 3FA")
    st.markdown("""
    Alur pendaftaran mandiri untuk petugas baru. Sistem akan menerbitkan kredensial lengkap berstandar militer:
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
            st.markdown("#### Langkah 3: Perekaman Biometrik Wajah (Dengan Flash Layar)")
            st.caption("Posisikan wajah Anda menghadap kamera laptop. Gunakan tombol Flash Layar 2 Detik yang muncul tepat di atas tombol Take Photo:")
            
            reg_cam_file = st.camera_input("Kamera Registrasi Biometrik Wajah:", key="reg_cam_input")

            # Fallback upload option
            with st.expander("Opsi Alternatif: Upload Citra Wajah"):
                reg_up_file = st.file_uploader("Pilih file foto wajah resmi (.jpg, .png):", type=["jpg", "jpeg", "png"], key="reg_up_input")

    with col_reg2:
        with st.container(border=True):
            st.markdown("#### Langkah 4: Finalisasi Pendaftaran & Unduh Dongle")
            st.caption("Setelah data terisi dan wajah terjepret, klik tombol di bawah untuk menerbitkan akun dan mengunduh token dongle USB.")

            face_source = None
            if reg_cam_file is not None:
                face_source = Image.open(reg_cam_file)
                st.info("Citra wajah dari webcam siap didaftarkan.")
            elif 'reg_up_file' in locals() and reg_up_file is not None:
                face_source = Image.open(reg_up_file)
                st.info("Citra wajah dari berkas upload siap didaftarkan.")
            else:
                st.warning("Silakan jepret foto wajah Anda pada Langkah 3 terlebih dahulu.")

            if st.button("Daftarkan Akun & Terbitkan Kunci Dongle", use_container_width=True, key="btn_execute_registration"):
                if not reg_name or not reg_uid:
                    st.error("Nama Lengkap dan User ID wajib diisi.")
                elif not reg_pwd1 or reg_pwd1 != reg_pwd2:
                    st.error("Password tidak cocok atau kosong. Periksa kembali konfirmasi password.")
                elif face_source is None:
                    st.error("Wajah belum diambil! Silakan jepret foto wajah menggunakan tombol flash pada kamera.")
                else:
                    try:
                        # 1. Enroll Face to Multi-Face Roster
                        BiometricVerifier.enroll_face(face_source, user_id=reg_uid, name=reg_name)

                        # 2. Register PBKDF2 Password Account
                        PasswordVerifier.register_account(reg_uid, reg_name, reg_pwd1)

                        # 3. Generate Hardware Dongle Token
                        dongle_token = DongleVerifier.generate_dongle_token(vault_id=f"VAULT-{reg_uid.upper()}", holder_name=reg_name)
                        st.session_state.latest_registered_dongle = json.dumps(dongle_token, indent=2).encode("utf-8")
                        st.session_state.registration_success_info = f"Akun **{reg_name}** (`{reg_uid}`) berhasil didaftarkan ke sistem!"
                        st.rerun()
                    except Exception as e:
                        st.error(f"Pendaftaran gagal: {e}")

            if st.session_state.get("registration_success_info"):
                st.success(st.session_state["registration_success_info"])
                st.markdown("---")
                st.markdown("##### 🔑 Unduh Kunci Hardware Dongle USB:")
                st.caption("Unduh berkas di bawah dan simpan ke flashdisk USB Anda:")
                st.download_button(
                    label="⬇️ Unduh Kunci Dongle USB (sentix_dongle.key)",
                    data=st.session_state.get("latest_registered_dongle", b""),
                    file_name="sentix_dongle.key",
                    mime="application/json",
                    use_container_width=True,
                    key="btn_download_new_dongle"
                )

                st.info("Setelah mengunduh kunci, buka menu **'1. Masuk (Login 3FA)'** untuk menguji login akun baru Anda.")


# =====================================================================
# FLOW 3: DEVELOPER & DOSEN EVALUATION SANDBOX
# =====================================================================

def render_developer_flow():
    st.subheader("Mode Pengembang & Sandbox Evaluasi Dosen")
    st.markdown("""
    Panel khusus pengujian sistem, visualisasi arsitektur perkuliahan, dan pintasan demonstrasi evaluasi sidang Tugas Akhir Kriptografi.
    """)

    col_d1, col_d2 = st.columns([1.2, 1], gap="large")

    with col_d1:
        with st.container(border=True):
            st.markdown("#### Matriks Pemenuhan 7 Kriteria Tugas Akhir Kriptografi")
            matrix_data = [
                {"Kriteria Slide": "1. Login Biometric & Hanya Hidup dengan Dongle", "Implementasi": "3FA: Hardware USB (HMAC-SHA256) + Biometrik Wajah + Password", "Rujukan": "NIST SP 800-63B"},
                {"Kriteria Slide": "2. Login Menggunakan Algoritma Kriptografi", "Implementasi": "Salted PBKDF2-HMAC-SHA256 (100.000 iterasi) untuk derivasi Master Key", "Rujukan": "Materi 8: Fungsi Hash"},
                {"Kriteria Slide": "3. Pesan Teks: Super Enkripsi (Klasik + Modern)", "Implementasi": "Lapis 1: Vigenere Cipher (ASCII 95) + Lapis 2: AES-256-CBC (PKCS7)", "Rujukan": "Materi 4 & 6/7"},
                {"Kriteria Slide": "4. Pesan File: Algoritma Beda dari Teks", "Implementasi": "RC4 Stream Cipher (KSA + PRGA byte-exact) dengan amplop metadata", "Rujukan": "Materi 7: Stream Cipher"},
                {"Kriteria Slide": "5. Pesan Penting Dienkripsi pada Basisdata", "Implementasi": "SQLite Database (sentix_vault.db) dengan enkripsi field AES-256-GCM", "Rujukan": "Materi 6 & 7: AEAD"},
                {"Kriteria Slide": "6. Pesan Gambar Diamankan Steganografi", "Implementasi": "Spatial Domain LSB Substitution kanal RGB + Metrik Matematis PSNR & MSE", "Rujukan": "Materi 9: Steganografi"},
                {"Kriteria Slide": "7. Aset Penting Diamankan Blockchain Sederhana", "Implementasi": "Ledger Rantai Hash SHA-256 + Konsensus Proof-of-Work + Tamper Alert", "Rujukan": "Materi 8: Hash & Chain"},
            ]
            st.table(matrix_data)

        with st.container(border=True):
            st.markdown("#### Inspektur Basis Data SQLite Fisik (Raw Ciphertext On-Disk)")
            st.caption("Membuktikan kepada dosen penguji bahwa pesan di dalam SQLite tersimpan dalam kondisi terenkripsi AES-256-GCM:")
            raws = get_raw_database_records()
            if raws:
                st.table(raws)
            else:
                st.info("Database saat ini masih kosong.")

    with col_d2:
        with st.container(border=True):
            st.markdown("#### Pintasan Pengujian Cepat (1-Click Fast Bypass)")
            st.caption("Gunakan tombol ini saat demonstrasi jika dosen ingin langsung menguji modul enkripsi/stego/blockchain tanpa proses login berulang.")
            
            if st.button("⚡ 1-Click Fast Bypass ke Dashboard Utama", use_container_width=True, key="dev_fast_bypass"):
                st.session_state.dongle_verified = True
                st.session_state.biometric_verified = True
                st.session_state.password_verified = True
                st.session_state.authenticated_officer = "Oktavian Prasetya Adi (Dev Bypass)"
                st.session_state.master_session_key = hashlib.sha256(b"SentixMasterBypassKey2026").hexdigest()
                st.session_state.authenticated = True
                st.rerun()

            if st.button("🔄 Reset Seluruh Sesi & Status Auth", use_container_width=True, key="dev_full_reset"):
                st.session_state.dongle_verified = False
                st.session_state.biometric_verified = False
                st.session_state.password_verified = False
                st.session_state.authenticated_officer = "N/A"
                st.session_state.master_session_key = None
                st.session_state.authenticated = False
                st.session_state.last_bio_result = None
                st.session_state.last_cam_hash = None
                st.session_state.last_up_hash = None
                st.success("Seluruh sesi telah di-reset ke kondisi awal terkunci.")
                st.rerun()

        with st.container(border=True):
            st.markdown("#### Manajemen Kunci Dongle & Template")
            if st.button("Buat Virtual Dongle di Folder Lokal (data/dongle/)", use_container_width=True, key="dev_mk_dongle"):
                p = DongleVerifier.write_dongle_to_path(DATA_DIR / "dongle")
                st.success(f"Virtual dongle berhasil dibuat di: {p}")

            st.markdown("---")
            st.markdown("##### Roster Template Wajah Terdaftar:")
            roster = BiometricVerifier.list_enrolled_faces()
            if roster:
                for idx, r in enumerate(roster):
                    col_u1, col_u2 = st.columns([3, 1])
                    with col_u1:
                        st.write(f"**{r['name']}** (`{r['user_id']}`) | {r['enrolled_at']}")
                    with col_u2:
                        if st.button(f"Hapus", key=f"del_face_{r['user_id']}_{idx}"):
                            BiometricVerifier.delete_face(r["user_id"])
                            st.rerun()
            else:
                st.caption("Belum ada wajah terdaftar.")


# =====================================================================
# MAIN AUTHENTICATED DASHBOARD (5 CRYPTO MODULES)
# =====================================================================

def render_main_dashboard():
    st.markdown("<h2 style='margin-bottom: 2px;'>SENTIX DIGITAL VAULT &mdash; CUSTODY WORKSTATION</h2>", unsafe_allow_html=True)
    st.caption("Status Sistem: Terkunci pada Hardware Token USB | Sesi Biometrik Aktif | Enkripsi End-to-End Sesuai Materi Kriptografi IF-B")

    col_b1, col_b2, col_b3, col_b4 = st.columns([1.2, 1, 1, 1])
    with col_b1:
        st.markdown(f"<span class='badge-pill badge-success'>OFFICER: {st.session_state.authenticated_officer.split('(')[0].replace('Biometrik Terverifikasi:', '').strip()[:20]}</span>", unsafe_allow_html=True)
    with col_b2:
        st.markdown("<span class='badge-pill badge-success'>USB DONGLE: CONNECTED</span>", unsafe_allow_html=True)
    with col_b3:
        st.markdown("<span class='badge-pill badge-success'>PBKDF2 KEY: ACTIVE</span>", unsafe_allow_html=True)
    with col_b4:
        if st.button("Kunci Vault (Logout)", use_container_width=True, key="btn_logout_main"):
            st.session_state.authenticated = False
            st.session_state.dongle_verified = False
            st.session_state.biometric_verified = False
            st.session_state.password_verified = False
            st.session_state.master_session_key = None
            st.session_state.authenticated_officer = "N/A"
            st.session_state.last_bio_result = None
            st.session_state.last_cam_hash = None
            st.session_state.last_up_hash = None
            st.rerun()

    st.markdown("---")

    # 5 Core Cryptographic Tabs
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "1. Super-Enkripsi Teks",
        "2. File Vault (RC4)",
        "3. Steganografi Citra",
        "4. Blockchain Aset",
        "5. Database Vault"
    ])

    # -----------------------------------------------------------------
    # TAB 1: SUPER ENKRIPSI TEKS (MULTI-STAGE & COURSEWORK PIPELINE)
    # -----------------------------------------------------------------
    with tab1:
        st.subheader("Super-Enkripsi Pesan Teks Terpadu")
        st.info("""
        **Rujukan: Materi 3 (Caesar), Materi 4 (Vigenère), Materi 7 (Vernam Stream), dan Materi 6/7 (Block Cipher AES):**
        Modul ini mengintegrasikan pipeline super-enkripsi multi-tahap karya tim kuliah (Kelompok 3).
        Tersedia pilihan antara **Pipeline 4-Tahap Lengkap** (Caesar ➔ Vigenère ➔ Vernam ➔ AES-128) dan **Super Enkripsi 2-Tahap Cepat** (Vigenère + AES-256).
        """)

        mode_super_pilihan = st.radio(
            "Pilih Skema Super-Enkripsi:",
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
                    st.markdown("#### Enkripsi 4-Tahap Terpadu")
                    st.caption("Pesan diproses berurutan melewati 4 algoritma kriptografi klasik & modern:")
                    plain_4 = st.text_area("Plainteks Rahasia:", "TRANSFER 500 ETH COLD VAULT", key="sup4_plain_in", height=90)

                    col_k_a, col_k_b = st.columns(2)
                    with col_k_a:
                        k_c_shift = st.number_input("1. Caesar Shift k (Grace):", min_value=1, max_value=25, value=8, key="k_c_shift_in")
                        k_v_key = st.text_input("2. Kunci Vigenère (Mirwan):", value="KUNCI", key="k_v_key_in")
                    with col_k_b:
                        k_vernam = st.text_input("3. Keystream Vernam (Oktavian):", value="VERNAM", key="k_vernam_in")
                        k_aes_key = st.text_input("4. Kunci AES-128 (Adhafa):", value="mysecretkey12345", key="k_aes_key_in")

                    if st.button("Eksekusi Pipeline 4-Tahap", use_container_width=True, key="btn_exec_4stage_enc"):
                        if plain_4 and k_v_key and k_vernam and k_aes_key:
                            try:
                                res4 = super_encrypt_4stage(plain_4, k_c_shift, k_v_key, k_vernam, k_aes_key)
                                st.success("Pipeline 4-Tahap Berhasil Dieksekusi!")

                                st.markdown("##### Tabel Transformasi Tiap Tahap:")
                                st.table(res4["stages"])

                                st.markdown("**Cipherteks Akhir (Base64 Envelope):**")
                                st.code(res4["final_cipher"], language="text")
                            except Exception as e:
                                st.error(f"Gagal enkripsi: {e}")
                        else:
                            st.error("Lengkapi seluruh teks dan parameter kunci.")

            with col_4dec:
                with st.container(border=True):
                    st.markdown("#### Dekripsi Pembalik 4-Tahap")
                    st.caption("Pembalikan berurutan: AES-128 Decrypt ➔ Vernam XOR ➔ Vigenère Decrypt ➔ Caesar Decrypt:")
                    cipher_4_in = st.text_area("Cipherteks Input (Base64):", "", key="sup4_cipher_in", height=90)

                    col_dk_a, col_dk_b = st.columns(2)
                    with col_dk_a:
                        dk_c_shift = st.number_input("1. Caesar Shift k:", min_value=1, max_value=25, value=8, key="dk_c_shift_in")
                        dk_v_key = st.text_input("2. Kunci Vigenère:", value="KUNCI", key="dk_v_key_in")
                    with col_dk_b:
                        dk_vernam = st.text_input("3. Keystream Vernam:", value="VERNAM", key="dk_vernam_in")
                        dk_aes_key = st.text_input("4. Kunci AES-128:", value="mysecretkey12345", key="dk_aes_key_in")

                    if st.button("Eksekusi Pembalik 4-Tahap", use_container_width=True, key="btn_exec_4stage_dec"):
                        if cipher_4_in and dk_v_key and dk_vernam and dk_aes_key:
                            try:
                                dec4 = super_decrypt_4stage(cipher_4_in.strip(), dk_c_shift, dk_v_key, dk_vernam, dk_aes_key)
                                st.success("Seluruh 4 Tahap Pembalik Berhasil!")

                                st.markdown("##### Alur Pemulihan Tiap Tahap:")
                                st.table(dec4["stages_dec"])

                                st.markdown("**Plainteks Asli Pulih:**")
                                st.success(dec4["final_plaintext"])
                            except Exception as e:
                                st.error(f"Gagal Dekripsi: {e} (Format tidak valid atau parameter kunci salah)")
                        else:
                            st.error("Masukkan cipherteks dan parameter seluruh kunci.")

        else:
            col_enc, col_dec = st.columns(2, gap="large")

            with col_enc:
                with st.container(border=True):
                    st.markdown("#### Enkripsi Pesan Baru (2-Tahap)")
                    plain_input = st.text_area("Plainteks Rahasia (Memo / Seed Phrase):", "TRANSFER 500 ETH TO COLD_VAULT_ALPHA MEMO: URGENT RESERVES", key="se_plain_input")
                    col_k1, col_k2 = st.columns(2)
                    with col_k1:
                        k_classical = st.text_input("Kunci Vigenère (Klasik):", "UPN2026", key="se_k_classical")
                    with col_k2:
                        k_modern = st.text_input("Passphrase AES (Modern):", "SentixSuperSecretKey!", key="se_k_modern")

                    if st.button("Eksekusi Super-Enkripsi", use_container_width=True, key="btn_exec_super_enc"):
                        if plain_input and k_classical and k_modern:
                            res = super_encrypt(plain_input, k_classical, k_modern)
                            st.success("Enkripsi Dua Lapis Berhasil!")

                            st.markdown("**Tahap 1 &mdash; Output Klasik (Vigenère):**")
                            st.code(res["vigenere_output"], language="text")

                            st.markdown("**Tahap 2 &mdash; Output Final (AES-256-CBC Base64):**")
                            st.code(res["final_ciphertext_base64"], language="text")
                            st.caption(f"IV (Hex): {res['iv_hex']}")
                        else:
                            st.error("Lengkapi seluruh kolom teks dan kunci.")

            with col_dec:
                with st.container(border=True):
                    st.markdown("#### Dekripsi Pesan Cipher (2-Tahap)")
                    cipher_input = st.text_area("Cipherteks (Base64 Envelope):", "", key="se_cipher_input")
                    col_dk1, col_dk2 = st.columns(2)
                    with col_dk1:
                        dk_classical = st.text_input("Kunci Vigenère:", "UPN2026", key="dec_vig_input")
                    with col_dk2:
                        dk_modern = st.text_input("Passphrase AES:", "SentixSuperSecretKey!", key="dec_aes_input")

                    if st.button("Eksekusi Super-Dekripsi", use_container_width=True, key="btn_exec_super_dec"):
                        if cipher_input and dk_classical and dk_modern:
                            try:
                                dres = super_decrypt(cipher_input.strip(), dk_classical, dk_modern)
                                st.success("Dekripsi Berhasil!")
                                st.markdown("**Hasil Dekripsi AES (Plainteks Vigenère):**")
                                st.code(dres["aes_intermediate"], language="text")
                                st.markdown("**Plainteks Asli Pulih:**")
                                st.success(dres["final_plaintext"])
                            except Exception as e:
                                st.error(f"Gagal Dekripsi: {e} (Kunci salah atau cipherteks rusak)")
                        else:
                            st.error("Masukkan cipherteks dan kedua kunci.")

    # -----------------------------------------------------------------
    # TAB 2: ENKRIPSI FILE (RC4 Stream Cipher)
    # -----------------------------------------------------------------
    with tab2:
        st.subheader("Brankas Berkas: Stream Cipher RC4")
        st.info("""
        **Rujukan: Materi 7 (Stream Cipher & Algoritma RC4):**
        Spesifikasi mewajibkan algoritma berkas **berbeda dari teks**. 
        Berkas dienkripsi bit-per-byte menggunakan algoritma **RC4 (KSA + PRGA)** dengan amplop metadata nama berkas.
        """)

        file_mode = st.radio("Pilih Operasi Berkas:", ["Enkripsi Berkas", "Dekripsi Berkas (.enc)"], horizontal=True, key="file_mode_radio")

        if file_mode == "Enkripsi Berkas":
            with st.container(border=True):
                up_raw = st.file_uploader("Pilih Berkas Dokumen/Gambar/Arsip:", type=None, key="raw_file_uploader")
                rc4_pwd = st.text_input("Passphrase Kunci RC4:", "RC4VaultProtectionKey!", key="rc4_enc_key")

                if up_raw and rc4_pwd:
                    if st.button("Enkripsi Berkas via RC4", use_container_width=True, key="btn_enc_rc4_file"):
                        raw_data = up_raw.read()
                        enc_data = encrypt_file_bytes(raw_data, up_raw.name, rc4_pwd)
                        st.success(f"Berkas berhasil dienkripsi! Ukuran: {len(enc_data)} bytes.")
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
                rc4_dec_pwd = st.text_input("Passphrase Kunci RC4:", "RC4VaultProtectionKey!", key="rc4_dec_key")

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
    # TAB 3: STEGANOGRAFI GAMBAR (Spatial LSB)
    # -----------------------------------------------------------------
    with tab3:
        st.subheader("Steganografi Citra: LSB Insertion (Least Significant Bit)")
        st.info("""
        **Rujukan: Materi 9 (Steganografi Citra Digital - Spatial Domain):**
        Menyembunyikan pesan rahasia ke dalam bit terendah (LSB) kanal warna RGB citra digital.
        Dilengkapi pengujian **PSNR (Peak Signal-to-Noise Ratio)** dan **MSE** untuk membuktikan bahwa penyisipan pesan tidak kasat mata secara visual.
        """)

        stego_tab1, stego_tab2 = st.tabs(["Sisipkan Pesan (Encode)", "Ekstrak Pesan (Decode)"])

        with stego_tab1:
            col_s1, col_s2 = st.columns(2, gap="large")
            with col_s1:
                with st.container(border=True):
                    stego_cover = st.file_uploader("Pilih Gambar Sampul (Cover Image):", type=["png", "bmp", "jpg"], key="stego_cover_up")
                    secret_msg = st.text_area("Pesan Rahasia yang Disembunyikan:", "SENTIX_AUTHENTICATED_CERTIFICATE_NO_8849204_VAULT_SAFE", key="stego_secret_text")
                    if stego_cover:
                        cov_img = Image.open(stego_cover)
                        st.image(cov_img, caption="Cover Image Asli", use_container_width=True)

            with col_s2:
                if stego_cover and secret_msg:
                    with st.container(border=True):
                        if st.button("Sisipkan Pesan ke Citra (LSB)", use_container_width=True, key="btn_stego_embed"):
                            try:
                                cov_img = Image.open(stego_cover)
                                stego_res, metrics = embed_secret_message(cov_img, secret_msg)
                                st.success("Pesan Berhasil Disisipkan ke Citra!")
                                st.image(stego_res, caption="Stego-Image (Hasil LSB)", use_container_width=True)

                                st.markdown("##### Metrik Akademis Citra:")
                                st.write(f"- **PSNR:** `{metrics['psnr_db']} dB` ({metrics['visual_quality']})")
                                st.write(f"- **MSE:** `{metrics['mse']}`")
                                st.write(f"- **Kapasitas Terpakai:** `{metrics['capacity_used_pct']}%` ({metrics['payload_bytes']} bytes)")

                                buf = BytesIO()
                                stego_res.save(buf, format="PNG")
                                st.download_button(
                                    label="Unduh Stego-Image (PNG)",
                                    data=buf.getvalue(),
                                    file_name="stego_asset_image.png",
                                    mime="image/png",
                                    use_container_width=True
                                )
                            except Exception as e:
                                st.error(f"Gagal menyisipkan pesan: {e}")

        with stego_tab2:
            with st.container(border=True):
                stego_probe = st.file_uploader("Upload Stego-Image (PNG):", type=["png", "bmp"], key="stego_probe_up")
                if stego_probe:
                    p_img = Image.open(stego_probe)
                    st.image(p_img, caption="Stego-Image Terpilih", width=300)
                    if st.button("Ekstrak Pesan Tersembunyi", use_container_width=True, key="btn_stego_extract"):
                        try:
                            recovered_msg = extract_secret_message(p_img)
                            st.success("Pesan Berhasil Diekstrak!")
                            st.code(recovered_msg, language="text")
                        except Exception as e:
                            st.error(f"Gagal mengekstrak pesan: {e}")

    # -----------------------------------------------------------------
    # TAB 4: BLOCKCHAIN INTEGRITAS ASET (PoW)
    # -----------------------------------------------------------------
    with tab4:
        st.subheader("Ledger Blockchain Aset (Proof-of-Work & SHA-256)")
        st.info("""
        **Rujukan: Materi 8 (Fungsi Hash Satu-Arah & Rantai Blok):**
        Perlindungan integritas aset digital menggunakan struktur rantai hash SHA-256.
        Masing-masing blok terikat ke `previous_hash` dan memiliki nilai `nonce` yang ditambang via Proof-of-Work.
        """)

        bc = st.session_state.blockchain

        col_chain_stat, col_audit = st.columns([1.5, 1])
        with col_chain_stat:
            st.metric("Total Blok Terdaftar", len(bc.chain))
        with col_audit:
            if st.button("Audit Integritas Rantai Blok", use_container_width=True, key="btn_audit_bc"):
                is_valid, report = bc.is_chain_valid()
                if is_valid:
                    st.success(report)
                else:
                    st.error(report)

        # Form Transaksi Baru
        with st.expander("Tambah Transaksi Aset Baru"):
            col_tx1, col_tx2, col_tx3 = st.columns(3)
            with col_tx1:
                tx_sender = st.text_input("Pengirim:", "COLD_VAULT_01", key="bc_tx_sender")
            with col_tx2:
                tx_recipient = st.text_input("Penerima:", "HOT_RESERVE_ALPHA", key="bc_tx_recipient")
            with col_tx3:
                tx_asset = st.selectbox("Aset:", ["BTC", "ETH", "USDT", "IDR_STABLE"], key="bc_tx_asset")
            
            col_tx4, col_tx5 = st.columns([1, 2])
            with col_tx4:
                tx_amount = st.number_input("Jumlah:", min_value=0.01, value=10.0, step=0.5, key="bc_tx_amount")
            with col_tx5:
                tx_memo = st.text_input("Memo Audit:", "Settlement transfer", key="bc_tx_memo")

            if st.button("Kirim ke Antrian Blok", key="btn_queue_tx"):
                bc.add_transaction(tx_sender, tx_recipient, tx_asset, tx_amount, tx_memo)
                st.success(f"Transaksi masuk antrian. Pending transactions: {len(bc.pending_transactions)}")

        # Mining Panel
        if bc.pending_transactions:
            st.warning(f"Terdapat {len(bc.pending_transactions)} transaksi pending belum ditambang.")
            if st.button("Tambang Blok Baru (Proof-of-Work)", use_container_width=True, key="btn_mine_bc"):
                with st.spinner("Menambang blok dengan target kesulitan hash..."):
                    new_b = bc.mine_pending_transactions(miner_address="SENTIX_AUDIT_NODE")
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
        with st.expander("Simulasi Tampering (Uji Coba Serangan Manipulasi Blok)"):
            st.caption("Uji coba mengubah nilai transaksi pada blok yang sudah ditambang untuk melihat respon deteksi otomatis.")
            if len(bc.chain) > 1:
                target_idx = st.number_input("Pilih Index Blok untuk Dimanipulasi:", min_value=1, max_value=len(bc.chain)-1, value=1, key="bc_tamper_idx")
                fake_amt = st.number_input("Ganti Jumlah Menjadi:", value=999999.0, key="bc_tamper_amt")
                if st.button("Manipulasi Nilai Blok (Inject Tamper)", key="btn_inject_tamper"):
                    bc.tamper_block_for_demo(target_idx, fake_amt)
                    st.error(f"Blok #{target_idx} telah dirusak secara ilegal! Klik 'Audit Integritas Rantai Blok' di atas untuk melihat respon.")
            else:
                st.caption("Tambang minimal 1 blok baru untuk mencoba fitur simulasi tampering.")

    # -----------------------------------------------------------------
    # TAB 5: DATABASE ENCRYPTION INSPECTOR (SQLite + AES-256-GCM)
    # -----------------------------------------------------------------
    with tab5:
        st.subheader("Database Vault Inspector: Basis Data Terenkripsi")
        st.info("""
        **Sesuai Spesifikasi: Pesan penting dienkripsi pada basisdata yang digunakan.**
        Menggunakan database SQLite lokal (`sentix_vault.db`) di mana seluruh payload pesan sensitif disimpan dalam bentuk **AES-256-GCM (Ciphertext + Nonce 12B + Tag 16B)**.
        """)

        # Add Secret Form
        with st.expander("Tambah Rekaman Rahasia ke Basis Data"):
            d_title = st.text_input("Judul Rekaman:", "Recovery Mnemonic Vault-01", key="db_rec_title")
            d_cat = st.selectbox("Kategori:", ["SEED_PHRASE", "PRIVATE_KEY", "LEGAL_CONTRACT", "FINANCIAL_MEMO"], key="db_rec_cat")
            d_secret = st.text_area("Pesan Penting (Sensitif):", "apple banana cherry dog elephant fox grape horse igloo jaguar kite lemon", key="db_rec_secret")
            
            if st.button("Simpan Terenkripsi ke Database", key="btn_save_db_rec"):
                if d_title and d_secret:
                    active_key = st.session_state.master_session_key or "SentixDefaultMasterKey"
                    rid = insert_secret(d_title, d_cat, d_secret, active_key)
                    st.success(f"Rekaman tersimpan di database dengan ID #{rid}!")
                    st.rerun()

        # Database View Toggle
        view_mode = st.radio("Mode Tampilan Database:", ["Tampilan Terdekripsi (Akses Berwenang)", "Tampilan Raw SQLite Fisik (Apa yang Dilihat Peretas)"], horizontal=True, key="db_view_toggle")

        if view_mode.startswith("Tampilan Terdekripsi"):
            active_key = st.session_state.master_session_key or "SentixDefaultMasterKey"
            records = get_all_secrets_decrypted(active_key)
            if records:
                for r in records:
                    with st.container(border=True):
                        col_r1, col_r2 = st.columns([3, 1])
                        with col_r1:
                            st.markdown(f"**[{r['category']}] {r['title']}** (ID: `{r['id']}` - {r['account_id']})")
                            st.caption(f"Dibuat: {r['created_at']} | Status: {r['decryption_status']}")
                            st.success(r["decrypted_secret"])
                        with col_r2:
                            if st.button(f"Hapus #{r['id']}", key=f"del_{r['id']}"):
                                delete_record(r['id'])
                                st.rerun()
            else:
                st.info("Belum ada data rekaman di database.")
        else:
            st.markdown("##### Tampilan Fisik Tabel `vault_records` di SQLite (Ciphertext On-Disk):")
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
        st.markdown("<h1 style='text-align: center; letter-spacing: 0.05em; margin-bottom: 2px;'>SENTIX DIGITAL VAULT</h1>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center; color: #94A3B8; font-size: 14px;'>Institutional Multi-Factor Cold Custody & Secret Asset Management Workstation</p>", unsafe_allow_html=True)
        st.markdown("<div style='text-align: center; margin-bottom: 16px;'><span class='badge-pill badge-info'>UPN VETERAN YOGYAKARTA</span><span class='badge-pill badge-info'>INFORMATIKA IF-B</span><span class='badge-pill badge-warning'>SYSTEM LOCKED</span></div>", unsafe_allow_html=True)
        st.markdown("---")

        # Top Workflow Navigation: User Login vs User Registration vs Developer Sandbox
        nav_choice = st.radio(
            "Pilih Alur Kerja (Workflow):",
            ["1. Masuk (Login 3FA)", "2. Registrasi Akun Petugas", "3. Mode Pengembang & Evaluasi Dosen"],
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

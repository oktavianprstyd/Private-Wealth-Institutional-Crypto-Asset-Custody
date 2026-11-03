"""Sentix Digital Vault - Streamlit Interactive Frontend Application
Integrated Cryptographic Workstation for UPN "Veteran" Yogyakarta Final Project.
Demonstrating:
1. 3-Factor Authentication Gate (Dongle USB, Biometric Face, Password Hash)
2. Super-Encryption (Classical Vigenère + Modern AES-256-CBC)
3. Binary File Encryption (RC4 Stream Cipher)
4. Database Vault with Field-Level Encryption (SQLite + AES-256-GCM)
5. Image Steganography (Spatial LSB with PSNR / MSE Metrics)
6. Critical Asset Ledger (Proof-of-Work Blockchain with Tamper Detection)
"""

import streamlit as st
import time
from pathlib import Path
from io import BytesIO
from PIL import Image

# Core Modules
from config import BASE_DIR, DATA_DIR, DONGLE_FILENAME, MASTER_FACE_PATH
from core.auth_3fa import DongleVerifier, BiometricVerifier, PasswordVerifier
from core.super_encryption import super_encrypt, super_decrypt
from core.file_cipher import encrypt_file_bytes, decrypt_file_bytes
from core.database_vault import init_database, insert_secret, get_all_secrets_decrypted, get_raw_database_records, delete_record
from core.steganography import embed_secret_message, extract_secret_message
from core.blockchain import Blockchain

# Streamlit Page Config
st.set_page_config(
    page_title="Sentix Digital Vault | Crypto Custody",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize Session State
if "dongle_verified" not in st.session_state:
    st.session_state.dongle_verified = False
if "biometric_verified" not in st.session_state:
    st.session_state.biometric_verified = False
if "password_verified" not in st.session_state:
    st.session_state.password_verified = False
if "master_session_key" not in st.session_state:
    st.session_state.master_session_key = None
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "blockchain" not in st.session_state:
    st.session_state.blockchain = Blockchain()


# =====================================================================
# LOCKDOWN & 3FA AUTHENTICATION GATEWAY
# =====================================================================

def render_3fa_gateway():
    st.markdown("<h1 style='text-align: center; color: #E0E0E0;'>🛡️ SENTIX DIGITAL VAULT</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #888;'>Institutional Grade Multi-Factor Cold Custody & Secret Asset Manager</p>", unsafe_allow_html=True)
    st.markdown("---")

    col_info, col_gate = st.columns([1, 1.2], gap="large")

    with col_info:
        st.subheader("🔒 Multi-Factor Access Protocol (3FA)")
        st.info("""
        Berdasarkan spesifikasi keamanan tingkat tinggi, akses workstation membutuhkan **3 faktor autentikasi berjenjang**:
        1. **Something You Have (Hardware Dongle):** Kunci fisik USB bertanda tangan HMAC-SHA256.
        2. **Something You Are (Biometric Face):** Pemindaian biometrik geometri wajah dengan Cosine Distance $\le 0.32$.
        3. **Something You Know (Master Password):** Hash PBKDF2-HMAC-SHA256 (100.000 iterasi) untuk membuka kunci brankas.
        """)

        st.caption("Universitas Pembangunan Nasional 'Veteran' Yogyakarta | Tugas Akhir Kriptografi IF-B")

        # Developer Quick Setup
        with st.expander("🛠️ Developer / Testing Utility"):
            if st.button("Generate Virtual Dongle di Folder Lokal"):
                virtual_p = DongleVerifier.write_dongle_to_path(DATA_DIR / "dongle")
                st.success(f"Virtual dongle generated at: {virtual_p}")
            if st.button("Enroll Default Biometric Template"):
                sample_face = Image.new("RGB", (64, 64), color=(180, 150, 120))
                BiometricVerifier.enroll_face(sample_face, user_id="oktavian_default")
                st.success("Default face template enrolled successfully.")

    with col_gate:
        st.subheader("Verifikasi 3 Kunci Akses")

        # Step 1: Hardware Dongle
        with st.container(border=True):
            st.markdown("### 1️⃣ Faktor 1: Hardware USB Dongle")
            scanned = DongleVerifier.scan_possible_dongle_locations()
            
            dongle_choice = None
            if scanned:
                st.success(f"Terdeteksi {len(scanned)} file dongle:")
                dongle_choice = st.selectbox("Pilih lokasi USB Dongle:", [str(p) for p in scanned])
            else:
                st.warning("Tidak ada USB dongle terdeteksi secara otomatis.")
                custom_path = st.text_input("Atau masukkan path dongle manual / file picker:", str(DATA_DIR / "dongle" / DONGLE_FILENAME))
                if Path(custom_path).exists():
                    dongle_choice = custom_path

            col_btn1, col_btn2 = st.columns([1, 1])
            with col_btn1:
                if st.button("🔌 Verifikasi Hardware Dongle"):
                    if dongle_choice:
                        ok, msg, payload = DongleVerifier.verify_dongle_path(dongle_choice)
                        if ok:
                            st.session_state.dongle_verified = True
                            st.success(f"✅ {msg}")
                        else:
                            st.error(f"❌ {msg}")
                    else:
                        st.error("Pilih atau buat file dongle terlebih dahulu.")
            with col_btn2:
                if st.button("⚡ Bypass Dongle (Dev Mode)"):
                    st.session_state.dongle_verified = True
                    st.success("Dongle bypassed for testing.")

        # Step 2: Biometric Face
        with st.container(border=True):
            st.markdown("### 2️⃣ Faktor 2: Biometrik Wajah")
            if not st.session_state.dongle_verified:
                st.caption("⚠️ Selesaikan verifikasi Dongle terlebih dahulu.")
            else:
                bio_method = st.radio("Metode Capture Wajah:", ["Webcam Live", "Upload Foto", "Simulasi Dev"], horizontal=True)
                
                probe_img = None
                if bio_method == "Webcam Live":
                    cam_file = st.camera_input("Arahkan wajah ke webcam:")
                    if cam_file:
                        probe_img = Image.open(cam_file)
                elif bio_method == "Upload Foto":
                    up_file = st.file_uploader("Upload foto wajah:", type=["jpg", "jpeg", "png"])
                    if up_file:
                        probe_img = Image.open(up_file)
                else:
                    if st.button("⚡ Verifikasi Biometrik (Simulasi Cocok)"):
                        st.session_state.biometric_verified = True
                        st.success("✅ Biometrik Terverifikasi (Mode Simulasi Pengujian)")

                if probe_img:
                    if st.button("🔍 Cocokkan Biometrik"):
                        ok, dist, msg = BiometricVerifier.verify_face(probe_img)
                        if ok:
                            st.session_state.biometric_verified = True
                            st.success(f"✅ {msg}")
                        else:
                            st.error(f"❌ {msg}")
                            st.caption("Tips: Jika belum pernah mendaftar, lakukan enrollment wajah pada menu utility.")

        # Step 3: Password Hash
        with st.container(border=True):
            st.markdown("### 3️⃣ Faktor 3: Master Password Vault")
            if not (st.session_state.dongle_verified and st.session_state.biometric_verified):
                st.caption("⚠️ Selesaikan verifikasi Dongle dan Biometrik terlebih dahulu.")
            else:
                pwd_input = st.text_input("Masukkan Master Password (Default: `Sentix@2026!`):", type="password")
                if st.button("🔓 Buka Sentix Vault"):
                    ok, msg, master_key = PasswordVerifier.verify_password(pwd_input)
                    if ok:
                        st.session_state.password_verified = True
                        st.session_state.master_session_key = master_key
                        st.session_state.authenticated = True
                        st.success("✅ Seluruh 3 Kunci Terverifikasi! Membuka brankas...")
                        time.sleep(0.5)
                        st.rerun()
                    else:
                        st.error(f"❌ {msg}")


# =====================================================================
# MAIN AUTHENTICATED DASHBOARD
# =====================================================================

def render_main_dashboard():
    # Top Header & Status Badges
    st.markdown("<h2 style='margin-bottom: 0;'>🛡️ SENTIX DIGITAL VAULT — CUSTODY TERMINAL</h2>", unsafe_allow_html=True)
    st.caption("Status Sistem: Terkunci pada Hardware Token USB | Sesi Biometrik Aktif | Enkripsi End-to-End")

    col_b1, col_b2, col_b3, col_b4 = st.columns([1, 1, 1, 1])
    with col_b1:
        st.success("🔑 Dongle: CONNECTED")
    with col_b2:
        st.success("👤 Biometrics: VERIFIED")
    with col_b3:
        st.success("🔒 PBKDF2: ACTIVE")
    with col_b4:
        if st.button("🚨 Lock Vault (Logout)", use_container_width=True):
            st.session_state.authenticated = False
            st.session_state.dongle_verified = False
            st.session_state.biometric_verified = False
            st.session_state.password_verified = False
            st.session_state.master_session_key = None
            st.rerun()

    st.markdown("---")

    # Main Tabs Navigation
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "🔐 Super-Enkripsi Teks",
        "📁 File Vault (RC4)",
        "🖼️ Steganografi Citra",
        "⛓️ Blockchain Aset",
        "🗄️ Database Inspector"
    ])

    # -----------------------------------------------------------------
    # TAB 1: SUPER ENKRIPSI TEKS (Vigenere + AES-256-CBC)
    # -----------------------------------------------------------------
    with tab1:
        st.subheader("🔐 Super-Enkripsi Pesan Teks (Vigenère + AES-256-CBC)")
        st.info("""
        **Sesuai Materi 4 (Vigenère Cipher) & Materi 6/7 (Block Cipher AES):**
        Pesan teks dienkripsi dua lapis (*Super Encryption*).
        Tahap 1: Enkripsi klasik **Vigenère Cipher** (ASCII 95) dengan kunci klasik.
        Tahap 2: Enkripsi modern **AES-256-CBC** dengan padding PKCS7 dan IV acak.
        """)

        col_enc, col_dec = st.columns(2, gap="medium")

        with col_enc:
            st.markdown("#### Enkripsi Pesan Baru")
            plain_input = st.text_area("Plainteks Rahasia (Memo / Seed Phrase):", "TRANSFER 500 ETH TO COLD_VAULT_ALPHA MEMO: URGENT RESERVES")
            col_k1, col_k2 = st.columns(2)
            with col_k1:
                k_classical = st.text_input("Kunci Vigenère (Klasik):", "UPN2026")
            with col_k2:
                k_modern = st.text_input("Passphrase AES (Modern):", "SentixSuperSecretKey!")

            if st.button("🔒 Eksekusi Super-Enkripsi", use_container_width=True):
                if plain_input and k_classical and k_modern:
                    res = super_encrypt(plain_input, k_classical, k_modern)
                    st.success("Enkripsi Dua Lapis Berhasil!")
                    
                    st.markdown("**Tahap 1 — Output Klasik (Vigenère):**")
                    st.code(res["vigenere_output"], language="text")
                    
                    st.markdown("**Tahap 2 — Output Final (AES-256-CBC Base64):**")
                    st.code(res["final_ciphertext_base64"], language="text")
                    st.caption(f"IV (Hex): {res['iv_hex']}")
                else:
                    st.error("Harap isi seluruh field.")

        with col_dec:
            st.markdown("#### Dekripsi Pesan Cipher")
            cipher_input = st.text_area("Cipherteks (Base64 Envelope):", "")
            col_dk1, col_dk2 = st.columns(2)
            with col_dk1:
                dk_classical = st.text_input("Kunci Vigenère:", "UPN2026", key="dec_vig")
            with col_dk2:
                dk_modern = st.text_input("Passphrase AES:", "SentixSuperSecretKey!", key="dec_aes")

            if st.button("🔓 Eksekusi Super-Dekripsi", use_container_width=True):
                if cipher_input and dk_classical and dk_modern:
                    try:
                        dres = super_decrypt(cipher_input.strip(), dk_classical, dk_modern)
                        st.success("Dekripsi Berhasil!")
                        st.markdown("**Hasil Dekripsi AES (Plainteks Vigenère):**")
                        st.code(dres["aes_intermediate"], language="text")
                        st.markdown("**Plainteks Asli Akhir:**")
                        st.success(dres["final_plaintext"])
                    except Exception as e:
                        st.error(f"Gagal Dekripsi: {e} (Kunci salah atau cipherteks rusak)")
                else:
                    st.error("Harap isi cipherteks dan kedua kunci.")

    # -----------------------------------------------------------------
    # TAB 2: ENKRIPSI FILE (RC4 Stream Cipher)
    # -----------------------------------------------------------------
    with tab2:
        st.subheader("📁 Brankas Berkas: Stream Cipher RC4")
        st.info("""
        **Sesuai Materi 7 (Stream Cipher & Algoritma RC4):**
        Spesifikasi mewajibkan algoritma berkas **berbeda dari teks**. 
        Berkas dienkripsi bit-per-byte menggunakan algoritma **RC4 (KSA + PRGA)** dengan amplop metadata otomatis.
        """)

        file_mode = st.radio("Pilih Operasi File:", ["Enkripsi File", "Dekripsi File (.enc)"], horizontal=True)

        if file_mode == "Enkripsi File":
            up_raw = st.file_uploader("Pilih Berkas Dokumen/Gambar/Arsip:", type=None, key="raw_file_uploader")
            rc4_pwd = st.text_input("Passphrase Kunci RC4:", "RC4VaultProtectionKey!", key="rc4_enc_key")

            if up_raw and rc4_pwd:
                if st.button("🔒 Enkripsi Berkas via RC4", use_container_width=True):
                    raw_data = up_raw.read()
                    enc_data = encrypt_file_bytes(raw_data, up_raw.name, rc4_pwd)
                    st.success(f"Berkas berhasil dienkripsi! Ukuran: {len(enc_data)} bytes.")
                    st.download_button(
                        label="⬇️ Unduh Berkas Terenkripsi (.enc)",
                        data=enc_data,
                        file_name=f"{up_raw.name}.enc",
                        mime="application/octet-stream",
                        use_container_width=True
                    )
        else:
            up_enc = st.file_uploader("Upload Berkas Terenkripsi (.enc):", type=None, key="enc_file_uploader")
            rc4_dec_pwd = st.text_input("Passphrase Kunci RC4:", "RC4VaultProtectionKey!", key="rc4_dec_key")

            if up_enc and rc4_dec_pwd:
                if st.button("🔓 Dekripsi Berkas via RC4", use_container_width=True):
                    try:
                        enc_data = up_enc.read()
                        dec_bytes, orig_name = decrypt_file_bytes(enc_data, rc4_dec_pwd)
                        st.success(f"Berkas berhasil didekripsi! Nama asli dipulihkan: **{orig_name}**")
                        st.download_button(
                            label=f"⬇️ Unduh Berkas Pulih ({orig_name})",
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
        st.subheader("🖼️ Steganografi Citra: LSB Insertion (Least Significant Bit)")
        st.info("""
        **Sesuai Materi 9 (Steganografi Citra Digital - Spatial Domain):**
        Menyembunyikan pesan rahasia ke dalam bit terendah (LSB) kanal warna RGB.
        Dilengkapi pengujian **PSNR (Peak Signal-to-Noise Ratio)** dan **MSE** untuk membuktikan bahwa penyisipan pesan tidak kasat mata secara visual.
        """)

        stego_tab1, stego_tab2 = st.tabs(["Sisipkan Pesan (Encode)", "Ekstrak Pesan (Decode)"])

        with stego_tab1:
            col_s1, col_s2 = st.columns(2)
            with col_s1:
                stego_cover = st.file_uploader("Pilih Gambar Sampul (Cover Image):", type=["png", "bmp", "jpg"], key="stego_cover_up")
                secret_msg = st.text_area("Pesan Rahasia yang Ingin Disembunyikan:", "SENTIX_AUTHENTICATED_CERTIFICATE_NO_8849204_VAULT_SAFE")
                if stego_cover:
                    cov_img = Image.open(stego_cover)
                    st.image(cov_img, caption="Cover Image Asli", use_container_width=True)

            with col_s2:
                if stego_cover and secret_msg:
                    if st.button("🎨 Sisipkan Pesan ke Citra (LSB)", use_container_width=True):
                        try:
                            cov_img = Image.open(stego_cover)
                            stego_res, metrics = embed_secret_message(cov_img, secret_msg)
                            st.success("Pesan Berhasil Disisipkan ke Citra!")
                            st.image(stego_res, caption="Stego-Image (Hasil LSB)", use_container_width=True)

                            st.markdown("##### 📊 Metrik Akademis Citra:")
                            st.write(f"- **PSNR:** `{metrics['psnr_db']} dB` ({metrics['visual_quality']})")
                            st.write(f"- **MSE:** `{metrics['mse']}`")
                            st.write(f"- **Kapasitas Terpakai:** `{metrics['capacity_used_pct']}%` ({metrics['payload_bytes']} bytes)")

                            buf = BytesIO()
                            stego_res.save(buf, format="PNG")
                            st.download_button(
                                label="⬇️ Unduh Stego-Image (PNG)",
                                data=buf.getvalue(),
                                file_name="stego_asset_image.png",
                                mime="image/png",
                                use_container_width=True
                            )
                        except Exception as e:
                            st.error(f"Gagal menyisipkan pesan: {e}")

        with stego_tab2:
            stego_probe = st.file_uploader("Upload Stego-Image (PNG):", type=["png", "bmp"], key="stego_probe_up")
            if stego_probe:
                p_img = Image.open(stego_probe)
                st.image(p_img, caption="Stego-Image Terpilih", width=300)
                if st.button("🔍 Ekstrak Pesan Tersembunyi", use_container_width=True):
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
        st.subheader("⛓️ Ledger Blockchain Aset (Proof-of-Work & SHA-256)")
        st.info("""
        **Sesuai Materi 8 (Fungsi Hash Satu-Arah & Rantai Blok):**
        Perlindungan integritas aset digital menggunakan struktur rantai hash SHA-256.
        Masing-masing blok terikat ke `previous_hash` dan memiliki nilai `nonce` yang ditambang via Proof-of-Work.
        """)

        bc = st.session_state.blockchain

        col_chain_stat, col_audit = st.columns([1.5, 1])
        with col_chain_stat:
            st.metric("Total Blok Terdaftar", len(bc.chain))
        with col_audit:
            if st.button("🛡️ Audit Integritas Rantai Blok", use_container_width=True):
                is_valid, report = bc.is_chain_valid()
                if is_valid:
                    st.success(f"✅ {report}")
                else:
                    st.error(f"🚨 {report}")

        # Form Transaksi Baru
        with st.expander("➕ Tambah Transaksi Aset Baru"):
            col_tx1, col_tx2, col_tx3 = st.columns(3)
            with col_tx1:
                tx_sender = st.text_input("Pengirim:", "COLD_VAULT_01")
            with col_tx2:
                tx_recipient = st.text_input("Penerima:", "HOT_RESERVE_ALPHA")
            with col_tx3:
                tx_asset = st.selectbox("Aset:", ["BTC", "ETH", "USDT", "IDR_STABLE"])
            
            col_tx4, col_tx5 = st.columns([1, 2])
            with col_tx4:
                tx_amount = st.number_input("Jumlah:", min_value=0.01, value=10.0, step=0.5)
            with col_tx5:
                tx_memo = st.text_input("Memo Audit:", "Settlement transfer")

            if st.button("Kirim ke Antrian Blok"):
                bc.add_transaction(tx_sender, tx_recipient, tx_asset, tx_amount, tx_memo)
                st.success(f"Transaksi masuk antrian. Pending transactions: {len(bc.pending_transactions)}")

        # Mining Panel
        if bc.pending_transactions:
            st.warning(f"Terdapat {len(bc.pending_transactions)} transaksi pending belum ditambang.")
            if st.button("⛏️ Tambang Blok Baru (Proof-of-Work)", use_container_width=True):
                with st.spinner("Menambang blok dengan target kesulitan hash..."):
                    new_b = bc.mine_pending_transactions(miner_address="SENTIX_AUDIT_NODE")
                    st.success(f"Blok #{new_b.index} berhasil ditambang! Hash: {new_b.hash[:20]}... Nonce: {new_b.nonce}")
                    st.rerun()

        # Chain Explorer
        st.markdown("#### 🔗 Rantai Blok Saat Ini")
        for b in reversed(bc.chain):
            with st.container(border=True):
                col_h1, col_h2 = st.columns([1, 2])
                with col_h1:
                    st.markdown(f"### Blok #{b.index}")
                    st.caption(f"Nonce: `{b.nonce}` | Timestamp: `{time.ctime(b.timestamp)}`")
                with col_h2:
                    st.code(f"Hash      : {b.hash}\nPrev Hash : {b.previous_hash}", language="text")
                st.json(b.transactions)

        # Educational Tamper Injection
        with st.expander("⚠️ Demo Simulasi Tampering (Manipulasi Data Blok)"):
            st.caption("Uji coba mengubah nilai transaksi pada blok yang sudah ditambang untuk melihat respon deteksi otomatis.")
            if len(bc.chain) > 1:
                target_idx = st.number_input("Pilih Index Blok untuk Dimanipulasi:", min_value=1, max_value=len(bc.chain)-1, value=1)
                fake_amt = st.number_input("Ganti Jumlah Menjadi:", value=999999.0)
                if st.button("🚨 Racuni Data Blok (Inject Tamper)"):
                    bc.tamper_block_for_demo(target_idx, fake_amt)
                    st.error(f"Blok #{target_idx} telah dirusak secara ilegal! Klik 'Audit Integritas' di atas untuk melihat respon.")
            else:
                st.caption("Tambang minimal 1 blok baru untuk mencoba fitur simulasi tampering.")

    # -----------------------------------------------------------------
    # TAB 5: DATABASE ENCRYPTION INSPECTOR (SQLite + AES-256-GCM)
    # -----------------------------------------------------------------
    with tab5:
        st.subheader("🗄️ Database Vault Inspector: Basis Data Terenkripsi")
        st.info("""
        **Sesuai Spesifikasi: Pesan penting dienkripsi pada basisdata yang digunakan.**
        Menggunakan database SQLite lokal (`sentix_vault.db`) di mana seluruh payload pesan sensitif disimpan dalam bentuk **AES-256-GCM (Ciphertext + Nonce 12B + Tag 16B)**.
        """)

        # Add Secret Form
        with st.expander("➕ Tambah Rekaman Rahasia ke Basis Data"):
            d_title = st.text_input("Judul Rekaman:", "Recovery Mnemonic Vault-01")
            d_cat = st.selectbox("Kategori:", ["SEED_PHRASE", "PRIVATE_KEY", "LEGAL_CONTRACT", "FINANCIAL_MEMO"])
            d_secret = st.text_area("Pesan Penting (Sensitif):", "apple banana cherry dog elephant fox grape horse igloo jaguar kite lemon")
            
            if st.button("Simpan Terenkripsi ke Database"):
                if d_title and d_secret:
                    active_key = st.session_state.master_session_key or "SentixDefaultMasterKey"
                    rid = insert_secret(d_title, d_cat, d_secret, active_key)
                    st.success(f"Rekaman tersimpan di database dengan ID #{rid}!")
                    st.rerun()

        # Database View Toggle
        view_mode = st.radio("Mode Tampilan Database:", ["👁️ Decrypted View (Akses Berwenang)", "🔒 Raw SQLite Disk View (Tampilan Fisik Basis Data)"], horizontal=True)

        if view_mode.startswith("👁️"):
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
            st.markdown("##### 🔍 Tampilan Fisik Tabel `vault_records` di SQLite (Apa yang Dilihat Peretas):")
            raws = get_raw_database_records()
            if raws:
                st.table(raws)
            else:
                st.info("Database masih kosong.")


# =====================================================================
# MAIN ROUTING
# =====================================================================

def main():
    if not st.session_state.authenticated:
        render_3fa_gateway()
    else:
        render_main_dashboard()


if __name__ == "__main__":
    main()

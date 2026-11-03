# 🎨 Sentix Digital Vault — UI / Frontend Developer Guide

Panduan teknis ini disusun khusus untuk developer frontend / UI tim **Sentix Digital Vault** agar dapat dengan mudah melanjutkan, mempercantik, atau memodifikasi tampilan antarmuka aplikasi.

---

## 🏛️ 1. Arsitektur Frontend & Alur Navigasi

Aplikasi saat ini dibangun menggunakan **Streamlit (Python)**. Seluruh logika UI berada pada file:
`app.py`

### Diagram State & Alur Akses (State Machine):

```text
[ User Membuka App ]
        │
        ▼
[ Cek: st.session_state.authenticated? ]
   ├── FALSE ──► Tampilkan: render_3fa_gateway() (Layar Gembok 3FA)
   │                ├── 1. Hardware Dongle USB (Validasi HMAC-SHA256)
   │                ├── 2. Biometrik Wajah (Webcam / Upload Foto)
   │                └── 3. Master Password (PBKDF2-HMAC-SHA256)
   │
   └── TRUE  ──► Tampilkan: render_main_dashboard() (5 Tab Navigasi)
                    ├── Tab 1: 🔐 Super-Enkripsi Teks (Vigenère + AES-CBC)
                    ├── Tab 2: 📁 File Vault Encryptor (RC4 Stream Cipher)
                    ├── Tab 3: 🖼️ Steganografi Citra (Spatial LSB)
                    ├── Tab 4: ⛓️ Blockchain Aset Ledger (PoW Mining & Tamper)
                    └── Tab 5: 🗄️ Database Inspector (AES-GCM SQLite View)
```

---

## 🔑 2. Session State Management (`st.session_state`)

Berikut daftar variabel session global yang mengontrol UI:

| Key State | Tipe Data | Deskripsi |
| :--- | :--- | :--- |
| `dongle_verified` | `bool` | `True` jika USB Dongle berhasil divalidasi |
| `biometric_verified`| `bool` | `True` jika biometrik wajah terverifikasi |
| `password_verified` | `bool` | `True` jika master password valid |
| `authenticated` | `bool` | `True` jika ketiga faktor di atas sukses (Membuka dashboard) |
| `master_session_key`| `str` (hex)| Kunci derivasi 256-bit di RAM untuk decrypt DB & vault |
| `blockchain` | `Blockchain`| Instance singleton rantai blok untuk transaksi & mining |

> **Tips untuk Frontend Dev:**
> Jika ingin melakukan testing langsung ke dashboard utama tanpa perlu login berulang-ulang, kamu bisa set nilai awal di paling atas `app.py`:
> ```python
> if "authenticated" not in st.session_state:
>     st.session_state.authenticated = True # Ganti sementara jadi True saat styling
> ```

---

## 🧩 3. Pemetaan Fungsi Modul Backend ke Komponen UI

Seluruh fungsi backend sudah modular dan tinggal dipanggil:

### A. Super-Enkripsi Teks
* **File Modul:** `core/super_encryption.py`
* **Fungsi Enkripsi:** `super_encrypt(plaintext, classical_key, modern_passphrase)`
  * Mengembalikan `dict`:
    - `res["vigenere_output"]` (Plainteks klasik)
    - `res["final_ciphertext_base64"]` (Cipherteks modern akhir)
    - `res["iv_hex"]` (IV acak 16 byte)
* **Fungsi Dekripsi:** `super_decrypt(ciphertext_base64, classical_key, modern_passphrase)`
  * Mengembalikan `dict`:
    - `dres["aes_intermediate"]`
    - `dres["final_plaintext"]`

### B. Enkripsi Berkas (File Vault)
* **File Modul:** `core/file_cipher.py`
* **Fungsi Enkripsi:** `encrypt_file_bytes(file_bytes, filename, passphrase)` $\to$ `bytes`
* **Fungsi Dekripsi:** `decrypt_file_bytes(envelope_bytes, passphrase)` $\to$ `(decrypted_bytes, original_filename)`

### C. Steganografi Gambar (LSB)
* **File Modul:** `core/steganography.py`
* **Fungsi Sisip (Encode):** `embed_secret_message(cover_pil_image, secret_text)` $\to$ `(stego_pil_image, metrics_dict)`
  * `metrics_dict` berisi: `psnr_db`, `mse`, `capacity_used_pct`.
* **Fungsi Ekstrak (Decode):** `extract_secret_message(stego_pil_image)` $\to$ `str`

### D. Blockchain Aset
* **File Modul:** `core/blockchain.py`
* **Instance:** `bc = st.session_state.blockchain`
* **Tambah Transaksi:** `bc.add_transaction(sender, recipient, asset, amount, memo)`
* **Mining Blok:** `bc.mine_pending_transactions(miner_address)`
* **Audit Validasi:** `is_valid, msg = bc.is_chain_valid()`
* **Simulasi Tamper:** `bc.tamper_block_for_demo(block_index, new_amount)`

### E. Basis Data Terenkripsi (Database Vault)
* **File Modul:** `core/database_vault.py`
* **Simpan Rahasia:** `insert_secret(title, category, sensitive_text, master_key)`
* **Lihat Terdekripsi:** `get_all_secrets_decrypted(master_key)`
* **Lihat Raw Cipher:** `get_raw_database_records()`

---

## 🎨 4. Panduan Styling & Desain (Design Tokens)

Untuk memberikan nuansa **FinTech / Institutional Cold Custody Vault**, gunakan acuan warna berikut:

| Token | Warna Hex | Penggunaan |
| :--- | :--- | :--- |
| **Primary Background** | `#0E1117` | Latar belakang gelap |
| **Card / Container** | `#1A1D24` | Background container atau widget box |
| **Accent Gold / Bronze** | `#D4AF37` / `#F3BA2F` | Judul, branding Sentix, token highlight |
| **Success Emerald** | `#00C853` | Status valid, transaksi approved, dongle connected |
| **Danger Crimson** | `#D50000` | Alert tampering, hardware disconnect, password salah |
| **Text Primary** | `#FFFFFF` | Heading dan label penting |
| **Text Muted** | `#8E9297` | Subtitle, metadata, timestamp |

### Cara Menambahkan Custom CSS:
Kamu bisa menyuntikkan CSS kustom ke Streamlit melalui `st.markdown`:

```python
st.markdown("""
<style>
    /* Styling Card Container */
    [data-testid="stVerticalBlock"] > div:has(div.stAlert) {
        border-radius: 12px;
    }
    
    /* Tombol Utama */
    .stButton>button {
        background: linear-gradient(135deg, #1f2937, #111827);
        color: #f3ba2f;
        border: 1px solid #374151;
        border-radius: 8px;
        font-weight: 600;
        transition: all 0.2s ease;
    }
    .stButton>button:hover {
        border-color: #f3ba2f;
        box-shadow: 0 0 10px rgba(243, 186, 47, 0.3);
    }
</style>
""", unsafe_allow_html=True)
```

---

## 📋 5. Checklist Task untuk Frontend Developer

Berikut hal-hal yang bisa kamu kembangkan berikutnya:
- [ ] **Restyling 3FA Stepper:** Buat tampilan 3 kotak autentikasi (Dongle, Biometrik, Password) memiliki efek progress visual (misal: Step 1 Hijau $\to$ Step 2 Kuning $\to$ Step 3 Abu-abu).
- [ ] **Grafik Visualisasi Blockchain:** Gunakan library visual (seperti `graphviz` atau visual box bertingkat) untuk menampilkan diagram balok rantai blok yang saling terhubung panah hash.
- [ ] **Preview Berkas Terdekripsi:** Pada Tab File Vault, tambahkan preview langsung jika file yang didekripsi berupa citra (`.png`, `.jpg`) atau teks (`.txt`).
- [ ] **Badge Status Real-time:** Percantik indikator status di pojok kanan atas dashboard.
- [ ] **Animasi Liveness:** Tambahkan visual panduan saat user mengarahkan wajah ke kamera (misal overlay lingkaran target wajah).

Jika ada pertanyaan mengenai logika backend atau error tipe data, hubungi tim backend (Oktavian Prasetya). Selamat berkreasi! 🚀

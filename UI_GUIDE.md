# Sentix Digital Vault — Frontend & UI Developer Guide

Panduan teknis ini disusun khusus untuk developer frontend / UI tim **Sentix Digital Vault** agar dapat dengan mudah melanjutkan, mempercantik, atau memodifikasi tampilan antarmuka aplikasi.

---

## 1. Arsitektur Frontend & Alur Navigasi

Aplikasi dibangun menggunakan **Streamlit (Python)**. Seluruh antarmuka berada pada file:
`app.py`

### Diagram State & Alur Akses (State Machine):

```text
[ User Membuka App ]
        │
        ▼
[ Cek: st.session_state.authenticated? ]
   ├── FALSE ──► Tampilkan: render_3fa_gateway() (Layar Gembok 3FA)
   │                ├── Tahap 1: Hardware Dongle USB (Validasi HMAC-SHA256)
   │                ├── Tahap 2: Biometrik Wajah Multi-Officer (Synchronized Screen Flash 2s + Auto-Verify)
   │                └── Tahap 3: Master Password (PBKDF2-HMAC-SHA256)
   │
   └── TRUE  ──► Tampilkan: render_main_dashboard() (5 Tab Navigasi)
                    ├── Tab 1: Super-Enkripsi Teks (Vigenère + AES-CBC)
                    ├── Tab 2: File Vault Encryptor (RC4 Stream Cipher)
                    ├── Tab 3: Steganografi Citra (Spatial LSB)
                    ├── Tab 4: Blockchain Aset Ledger (PoW Mining & Tamper Alert)
                    └── Tab 5: Database Vault (AES-GCM SQLite View)
```

---

## 2. Fitur Baru: Synchronized Screen Flash 2 Detik + Multi-Face Roster

### A. Synchronized Screen Flash (2 Detik Otomatis)
- **Problem Sebelumnya:** Tombol flash menyala tetapi pemotretan tidak sinkron (lampu flash mati sebelum user klik jepret).
- **Solusi Sekarang:** Tombol `[ AMBIL FOTO DENGAN FLASH LAYAR (2 DETIK) ]`:
  1. `T = 0ms`: Layar monitor berubah menjadi putih terang solid 100% (`#FFFFFF`) menutupi seluruh layar (berfungsi sebagai ring light / softbox).
  2. `T = 1000ms`: Tepat di tengah kilatan cahaya (saat sensor kamera sudah menyesuaikan auto-exposure terhadap cahaya putih), JavaScript otomatis menjepret foto (`camBtn.click()`).
  3. `T = 2000ms`: Layar putih padam secara halus.
  4. Streamlit langsung memproses foto yang tertangkap dalam kondisi pencahayaan terang benderang.

### B. Multi-Face Roster (Dukungan Banyak Wajah Petugas)
- Mengizinkan banyak wajah terdaftar dalam satu sistem (misal: Oktavian, Rekan 1, Rekan 2).
- Disimpan di `data/master_face.json` dalam format roster JSON:
  ```json
  {
    "version": "2.0_multi_face",
    "faces": [
      {
        "user_id": "oktavian",
        "name": "Oktavian Prasetya Adi (123240135)",
        "embedding": [...]
      }
    ]
  }
  ```
- Saat pemindaian biometrik berlangsung, wajah yang terdeteksi dicocokkan ke seluruh anggota roster. Jika cocok dengan salah satu anggota ($D_c \le 0.32$), sistem menampilkan nama petugas yang bersangkutan:  
  `Biometrik Terverifikasi: Oktavian Prasetya Adi (123240135)`

### C. Kompatibilitas CPU / iGPU Non-GPU (Intel Gen 12+)
- Ekstraksi fitur menggunakan **Multi-Scale Spatial-Gradient Biometric Descriptor (128-D)** dengan zero-mean centering dan edge energy normalization.
- Berjalan dalam **< 2 milidetik** di CPU Intel Gen 12 (Core i3/i5/i7) atau Iris Xe iGPU tanpa butuh CUDA, PyTorch, dlib, atau kompilasi C++.

---

## 3. Session State Management (`st.session_state`)

Berikut daftar variabel session global yang mengontrol alur UI:

| Key State | Tipe Data | Deskripsi |
| :--- | :--- | :--- |
| `dongle_verified` | `bool` | `True` jika USB Dongle berhasil divalidasi |
| `biometric_verified`| `bool` | `True` jika biometrik wajah terverifikasi |
| `authenticated_officer` | `str` | Nama petugas/officer yang terverifikasi biometrik |
| `password_verified` | `bool` | `True` jika master password valid |
| `authenticated` | `bool` | `True` jika ketiga faktor sukses (Membuka dashboard) |
| `master_session_key`| `str` (hex)| Kunci derivasi 256-bit di RAM untuk decrypt DB & vault |
| `blockchain` | `Blockchain`| Instance singleton rantai blok untuk transaksi & mining |

> **Tips Cepat untuk Styling Frontend:**
> Jika kamu ingin langsung menata tab dashboard utama tanpa perlu melalui login 3FA berulang-ulang, ubah sementara nilai di baris inisialisasi `app.py`:
> ```python
> if "authenticated" not in st.session_state:
>     st.session_state.authenticated = True  # Ubah jadi True saat mendesain UI
> ```

---

## 4. Pemetaan Fungsi Modul Backend ke Komponen UI

### A. Super-Enkripsi Teks (Dual Scheme)
* **File Modul:** `core/super_encryption.py`
* **Skema 1 (Pipeline 4-Tahap Coursework):**
  - **Enkripsi:** `super_encrypt_4stage(plaintext, caesar_shift, vigenere_key, vernam_key, aes_key)`
    * Tahap 1: Caesar Cipher (k) — Grace Rianty Butar Butar (123240036)
    * Tahap 2: Vigenère Cipher (Keyword) — Mirwan Qolyubi (123240116)
    * Tahap 3: Vernam Stream Cipher (Bitwise XOR) — Oktavian Prasetya Adi (123240135)
    * Tahap 4: AES-128 Block Cipher (CBC) — Adhafa Joan Putranto (123240069)
  - **Dekripsi:** `super_decrypt_4stage(ciphertext_b64, caesar_shift, vigenere_key, vernam_key, aes_key)`
* **Skema 2 (Super-Enkripsi 2-Tahap Cepat):**
  - **Enkripsi:** `super_encrypt(plaintext, classical_key, modern_passphrase)`
  - **Dekripsi:** `super_decrypt(ciphertext_base64, classical_key, modern_passphrase)`

### B. Enkripsi Berkas (File Vault)
* **File Modul:** `core/file_cipher.py`
* **Enkripsi:** `encrypt_file_bytes(file_bytes, filename, passphrase)` $\to$ `bytes`
* **Dekripsi:** `decrypt_file_bytes(envelope_bytes, passphrase)` $\to$ `(decrypted_bytes, original_filename)`

### C. Steganografi Citra (LSB)
* **File Modul:** `core/steganography.py`
* **Sisipkan (Encode):** `embed_secret_message(cover_pil_image, secret_text)` $\to$ `(stego_pil_image, metrics_dict)`
* **Ekstrak (Decode):** `extract_secret_message(stego_pil_image)` $\to$ `str`

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

## 5. Panduan Styling & Desain (Design Tokens)

Gunakan standar FinTech / Institutional Vault tanpa emoji berlebih:

| Token | Warna Hex | Penggunaan |
| :--- | :--- | :--- |
| **Primary Background** | `#0E1117` | Latar belakang gelap aplikasi |
| **Card / Container** | `#1A1D24` | Background container atau box widget |
| **Border Subdued** | `#334155` | Garis tepi container |
| **Success Emerald** | `#059669` / `#34D399` | Status valid, token connected, lolos verifikasi |
| **Warning Amber** | `#D97706` / `#FBBF24` | Status pending, peringatan sistem |
| **Danger Crimson** | `#DC2626` / `#F87171` | Alert manipulasi data / tampering, ditolak |
| **Text Primary** | `#FFFFFF` | Heading dan label penting |
| **Text Muted** | `#94A3B8` | Subtitle, metadata, timestamp |

---

## 6. Checklist Tugas untuk Frontend Developer

- [ ] **Desain Card 3FA Stepper:** Percantik tata letak progress 3 langkah (Dongle $\to$ Biometrik $\to$ Password) agar lebih intuitif.
- [ ] **Visualisasi Diagram Rantai Blok:** Tampilkan grafis balok rantai blok yang saling terhubung panah hash di Tab Blockchain.
- [ ] **Preview Berkas Terdekripsi:** Tambahkan penampil langsung jika berkas yang didekripsi adalah dokumen gambar atau teks.
- [ ] **Status Bar Header:** Sesuaikan ukuran font dan pill badges pada bar status atas.

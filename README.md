# SENTIX DIGITAL VAULT
### Institutional-Grade Multi-Factor Crypto Custody & Secret Asset Manager

> **Tugas Akhir Mata Kuliah Kriptografi**  
> Program Studi Informatika (PJJ IF-B) — Universitas Pembangunan Nasional "Veteran" Yogyakarta  
> **Anggota Pengembang:** Oktavian Prasetya Adi (NIM: 123240135) & Tim

---

## 1. Latar Belakang & Arsitektur Sistem

**Sentix Digital Vault** adalah sistem brankas keamanan aset digital tingkat institusi (*institutional cold-storage custody*) yang dirancang untuk melindungi aset bernilai tinggi, *seed phrase*, dokumen audit rahasia, serta rekaman transaksi terdistribusi.

Aplikasi ini mengintegrasikan seluruh materi kuliah Kriptografi (Materi 1–9) ke dalam skenario dunia nyata (*FinTech & Web3 Security*), mencakup autentikasi multi-faktor berbasis perangkat keras fisik, biometrik fisiologis multi-petugas dengan *Synchronized Screen Flash 2 Detik*, super-enkripsi teks, enkripsi berkas berbasis stream, steganografi citra digital, hingga integritas buku besar terdesentralisasi (*blockchain*).

---

## 2. Alur Aplikasi: User Flow vs Developer Flow

Aplikasi membagi alur kerja secara tegas antara pengguna operasional (*User*) dan evaluator akademis (*Developer/Dosen*):

```text
                                [ SENTIX DIGITAL VAULT ]
                                           │
         ┌─────────────────────────────────┼─────────────────────────────────┐
         ▼                                 ▼                                 ▼
┌──────────────────┐             ┌──────────────────┐             ┌──────────────────┐
│  1. USER LOGIN   │             │ 2. USER REGISTER │             │  3. DEV SANDBOX  │
├──────────────────┤             ├──────────────────┤             ├──────────────────┤
│ 1. Colok Dongle  │             │ 1. Nama & UserID │             │ 1. Matriks 7     │
│    USB (HMAC)    │             │                  │             │    Kriteria TA   │
│ 2. Scan Wajah    │             │ 2. Set Password  │             │ 2. 1-Click Fast  │
│    (Flash 2s)    │             │    PBKDF2 Hash   │             │    Bypass Demo   │
│ 3. Master Pwd    │             │ 3. Rekam Wajah   │             │ 3. Inspektur DB  │
│    (PBKDF2 Key)  │             │    (Flash 2s)    │             │    Cipher SQLite │
└────────┬─────────┘             │ 4. Unduh Dongle  │             │ 4. Roster Multi  │
         │                       │    sentix.key    │             │    Face Manager  │
         ▼                       └────────┬─────────┘             └──────────────────┘
┌─────────────────────────────────────────┴──────────────────────────────────────────┐
│                           DASHBOARD UTAMA BRANKAS                                  │
│ 1. Super-Enkripsi Teks (Vigenère + AES) │ 4. Blockchain Aset Ledger (PoW Mining)   │
│ 2. File Vault Berkas (Stream RC4)       │ 5. Database Vault Terenkripsi (AES-GCM)  │
│ 3. Steganografi Citra (Spatial LSB)     │                                          │
└────────────────────────────────────────────────────────────────────────────────────┘
```

### A. Alur Kerja Pengguna (User Flow)
1. **Registrasi Akun Baru (Onboarding):**
   - Masukkan Nama Lengkap dan User ID Petugas.
   - Tentukan Master Password (di-hash dengan fungsi *Salted PBKDF2-HMAC-SHA256* 100.000 iterasi).
   - Rekam geometri biometrik wajah menggunakan kamera dengan bantuan **Synchronized Screen Flash 2 Detik** (tombol diletakkan tepat di atas tombol Take Photo).
   - Terbitkan dan unduh berkas kunci fisik `sentix_dongle.key` yang bertanda tangan HMAC-SHA256 ke flashdisk USB.
2. **Masuk ke Sistem (3FA Gatekeeper):**
   - **Faktor 1 (Dongle):** Hubungkan flashdisk USB atau unggah berkas `sentix_dongle.key`.
   - **Faktor 2 (Biometrik):** Posisikan wajah ke webcam $\rightarrow$ klik tombol flash 2 detik $\rightarrow$ sistem otomatis mencocokkan ke roster wajah resmi.
   - **Faktor 3 (Password):** Masukkan Master Password $\rightarrow$ sistem menurunkan kunci enkripsi sesi (*Master Session Key*) di RAM.
3. **Operasi Brankas:** Akses penuh ke 5 modul keamanan digital (Super Enkripsi, File Vault, Stegano LSB, Blockchain Ledger, dan Database Vault).

### B. Alur Pengembang & Sidang Dosen (Developer & Evaluation Flow)
1. **Matriks Pembuktian Akademis:** Menampilkan tabel pemetaan 7 kriteria tugas akhir langsung terhadap slide silabus perkuliahan (Materi 1–9).
2. **1-Click Fast Bypass:** Pintasan sekali klik untuk langsung membuka dashboard utama tanpa proses pemindaian berulang saat demonstrasi di depan dosen penguji.
3. **Inspektur Basis Data Fisik:** Menampilkan isi tabel `vault_records` SQLite dalam bentuk raw ciphertext + nonce + tag untuk membuktikan field penting terenkripsi di harddisk.
4. **Simulasi Tampering Blockchain:** Uji coba merusak nilai transaksi pada blok yang sudah ditambang untuk membuktikan algoritma deteksi manipulasi otomatis (*tamper alert*).

---

## 3. Pemenuhan Spesifikasi Kriteria Tugas Akhir

| Kriteria di Slide Dosen | Implementasi Teknis di Sentix Vault | Rujukan Materi Kuliah |
| :--- | :--- | :--- |
| **1. Login Biometric & Hanya Hidup dengan Bantuan Dongle** | **Faktor 1:** Kunci fisik USB Flashdisk bertanda tangan HMAC-SHA256.<br>**Faktor 2:** Verifikasi biometrik wajah multi-officer (*Cosine Distance* $\le 0.32$).<br>**Faktor 3:** Master Password. (Aplikasi terkunci total jika dongle/biometrik tidak valid). | Slide Spek & NIST SP 800-63B |
| **2. Login Menggunakan Algoritma Kriptografi** | Menggunakan algoritma fungsi hash **PBKDF2-HMAC-SHA256** (100.000 iterasi) dengan garam (*salt*) kriptografis 16-byte untuk menghasilkan kunci derivasi master. | **Materi 8:** Algoritma Fungsi Hash Satu-Arah |
| **3. Pesan Teks Dienkripsi Super Enkripsi (Klasik + Modern)** | **Lapis 1 (Klasik):** Vigenère Cipher (Polialfabetik substitusi ASCII 95).<br>**Lapis 2 (Modern):** AES-256-CBC (*Cipher Block Chaining*) dengan padding PKCS7 dan IV acak. | **Materi 4:** Vigenère Cipher<br>**Materi 6 & 7:** Cipher Blok & AES |
| **4. Pesan File Dienkripsi Algoritma Beda dari Teks** | Enkripsi berkas biner sembarang (`.pdf`, `.docx`, `.zip`, `.png`) menggunakan **RC4 Stream Cipher** (implementasi byte-level KSA & PRGA). Berbeda fundamental dari AES (Block vs Stream). | **Materi 7:** Contoh Implementasi Stream Cipher (RC4) |
| **5. Pesan Penting Dienkripsi pada Basis Data** | Basis data SQLite lokal (`sentix_vault.db`) mengamankan field sensitif menggunakan enkripsi terotentikasi **AES-256-GCM** (*Galois/Counter Mode*). | **Materi 6 & 7:** Mode Operasi Modern (AEAD) |
| **6. Pesan Gambar Diamankan Konsep Steganografi** | Penyisipan pesan rahasia ke dalam bit terendah (*Spatial Domain LSB Substitution*) kanal warna RGB citra digital, dilengkapi perhitungan matematis **PSNR** ($> 50\text{ dB}$) dan **MSE**. | **Materi 9:** Steganografi Citra Digital (*Prisoner's Problem*) |
| **7. Aset Penting Diamankan Teknologi Blockchain Sederhana** | Buku besar (*ledger*) aset berbasis rantai blok hash SHA-256 terhubung, mekanisme konsensus **Proof-of-Work (PoW)**, dan deteksi otomatis perusakan rantai (*tamper detection*). | **Materi 8:** Fungsi Hash & Blockchain Ledger |

---

## 4. Struktur Direktori Proyek

```text
sentix-digital-vault/
├── README.md               # Dokumentasi utama proyek & laporan arsitektur
├── UI_GUIDE.md             # Panduan pengembang frontend untuk rekan tim
├── requirements.txt        # Daftar dependensi Python
├── .gitignore              # Konfigurasi filter repositori Git
├── app.py                  # Entrypoint antarmuka pengguna interaktif (Streamlit)
├── config.py               # Konfigurasi konstanta, path, dan parameter kriptografi
│
├── core/                   # Modul mesin kriptografi backend
│   ├── __init__.py
│   ├── auth_3fa.py         # Mesin 3FA: Dongle USB, Biometrik Multi-Face, & PBKDF2
│   ├── super_encryption.py # Vigenère Cipher (Klasik) + AES-256-CBC (Modern)
│   ├── file_cipher.py      # RC4 Stream Cipher (KSA & PRGA) untuk berkas
│   ├── database_vault.py   # Brankas basis data SQLite + AES-256-GCM
│   ├── steganography.py    # LSB Image Steganography + Analisis Metrik PSNR/MSE
│   └── blockchain.py       # Rantai Blok Aset PoW + Deteksi Manipulasi Data
│
├── tests/                  # Pengujian unit otomatis (Automated Unit Tests)
│   ├── __init__.py
│   └── test_crypto_engines.py # Pengujian end-to-end 8 skenario pengujian
│
├── scripts/                # Perkakas CLI pendukung
│   ├── generate_dongle.py  # Script pembuat kunci USB Dongle fisik/virtual
│   └── enroll_face.py      # Script pendaftaran master wajah biometrik
│
└── data/                   # Direktori penyimpanan lokal (DB, kunci, ledger)
```

---

## 5. Panduan Menjalankan & Pengujian

### Langkah 1: Siapkan Lingkungan Virtual
```bash
python -m venv venv

# Windows (PowerShell):
.\venv\Scripts\Activate.ps1
# Linux / macOS:
source venv/bin/activate
```

### Langkah 2: Pasang Dependensi
```bash
pip install -r requirements.txt
```

### Langkah 3: Jalankan Automated Test Suite
```bash
python tests/test_crypto_engines.py
```
*Output: `Ran 8 tests in 0.298s ... OK`*

### Langkah 4: Jalankan Aplikasi Sentix Vault
```bash
streamlit run app.py
```
Buka browser pada alamat: `http://localhost:8501`.

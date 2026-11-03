# 🛡️ SENTIX DIGITAL VAULT
### *Institutional-Grade Multi-Factor Crypto Custody & Secret Asset Manager*

> **Tugas Akhir Mata Kuliah Kriptografi**  
> Program Studi Informatika (PJJ IF-B) — Universitas Pembangunan Nasional "Veteran" Yogyakarta  
> **Anggota Pengembang:** Oktavian Prasetya Adi (NIM: 123240135) & Tim

---

## 📌 1. Latar Belakang & Tema Aplikasi

**Sentix Digital Vault** adalah sistem brankas keamanan aset digital tingkat institusi (*institutional cold-storage custody*) yang dirancang untuk melindungi aset bernilai tinggi, *seed phrase*, dokumen audit rahasia, serta rekaman transaksi terdistribusi.

Aplikasi ini mengintegrasikan seluruh materi kuliah Kriptografi (Materi 1–9) ke dalam skenario dunia nyata (*FinTech & Web3 Security*), mencakup autentikasi multi-faktor berbasis perangkat keras fisik, biometrik fisiologis, super-enkripsi teks, enkripsi berkas berbasis stream, steganografi citra digital, hingga integritas buku besar terdesentralisasi (*blockchain*).

---

## 🎯 2. Pemenuhan Spesifikasi Kriteria Tugas Akhir

| Kriteria di Slide Dosen | Implementasi Teknis di Sentix Vault | Rujukan Materi Kuliah |
| :--- | :--- | :--- |
| **1. Login Biometric & Hanya Hidup dengan Bantuan Dongle** | **Faktor 1:** Kunci fisik USB Flashdisk bertanda tangan HMAC-SHA256.<br>**Faktor 2:** Verifikasi biometrik wajah (*Cosine Distance* $\le 0.32$).<br>**Faktor 3:** Master Password. (Aplikasi terkunci total jika dongle/biometrik tidak valid). | Slide Spek & NIST SP 800-63B |
| **2. Login Menggunakan Algoritma Kriptografi** | Menggunakan algoritma fungsi hash **PBKDF2-HMAC-SHA256** (100.000 iterasi) dengan garam (*salt*) kriptografis 16-byte untuk menghasilkan kunci derivasi master. | **Materi 8:** Algoritma Fungsi Hash Satu-Arah |
| **3. Pesan Teks Dienkripsi Super Enkripsi (Klasik + Modern)** | **Lapis 1 (Klasik):** Vigenère Cipher (Polialfabetik substitusi ASCII 95).<br>**Lapis 2 (Modern):** AES-256-CBC (*Cipher Block Chaining*) dengan padding PKCS7 dan IV acak. | **Materi 4:** Vigenère Cipher<br>**Materi 6 & 7:** Cipher Blok & AES |
| **4. Pesan File Dienkripsi Algoritma Beda dari Teks** | Enkripsi berkas biner sembarang (`.pdf`, `.docx`, `.zip`, `.png`) menggunakan **RC4 Stream Cipher** (implementasi byte-level KSA & PRGA). Berbeda fundamental dari AES (Block vs Stream). | **Materi 7:** Contoh Implementasi Stream Cipher (RC4) |
| **5. Pesan Penting Dienkripsi pada Basis Data** | Basis data SQLite lokal (`sentix_vault.db`) mengamankan field sensitif menggunakan enkripsi terotentikasi **AES-256-GCM** (*Galois/Counter Mode*). | **Materi 6 & 7:** Mode Operasi Modern (AEAD) |
| **6. Pesan Gambar Diamankan Konsep Steganografi** | Penyisipan pesan rahasia ke dalam bit terendah (*Spatial Domain LSB Substitution*) kanal warna RGB citra digital, dilengkapi perhitungan matematis **PSNR** ($> 50\text{ dB}$) dan **MSE**. | **Materi 9:** Steganografi Citra Digital (*Prisoner's Problem*) |
| **7. Aset Penting Diamankan Teknologi Blockchain Sederhana** | Buku besar (*ledger*) aset berbasis rantai blok hash SHA-256 terhubung, mekanisme konsensus **Proof-of-Work (PoW)**, dan deteksi otomatis perusakan rantai (*tamper detection*). | **Materi 8:** Fungsi Hash & Blockchain Ledger |

---

## 📂 3. Struktur Direktori Proyek

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
│   ├── auth_3fa.py         # Mesin 3FA: Dongle USB, Biometrik Wajah, & PBKDF2
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

## 🚀 4. Panduan Instalasi & Menjalankan Aplikasi

### Langkah 1: Klon / Siapkan Lingkungan Virtual
Pastikan Python 3.10+ telah terpasang di sistem operasi Anda (Windows, Linux, atau macOS).

```bash
# Buat virtual environment
python -m venv venv

# Aktifkan virtual environment
# Windows (PowerShell):
.\venv\Scripts\Activate.ps1
# Windows (CMD):
.\venv\Scripts\activate.bat
# Linux / macOS:
source venv/bin/activate
```

### Langkah 2: Pasang Dependensi
```bash
pip install -r requirements.txt
```

### Langkah 3: Jalankan Automated Test Suite
Pastikan seluruh 8 pengujian kriptografi lulus 100%:
```bash
python tests/test_crypto_engines.py
```
*Output yang diharapkan: `Ran 8 tests in X.Xs ... OK`*

### Langkah 4: Jalankan Aplikasi Sentix Vault
```bash
streamlit run app.py
```
Aplikasi akan otomatis terbuka pada browser Anda di alamat: `http://localhost:8501`.

---

## 🔑 5. Panduan Penggunaan Fitur 3FA & Login

### Akun & Kredensial Bawaan:
- **Master Password:** `Sentix@2026!`
- **Hardware Dongle:**
  - *Cara 1 (USB Fisik):* Colok flashdisk, jalankan `python scripts/generate_dongle.py --output E:/` (sesuaikan huruf drive USB Anda).
  - *Cara 2 (Virtual Dongle untuk Pengujian):* Pada layar login, klik tombol **"⚡ Bypass Dongle (Dev Mode)"** atau klik **"Generate Virtual Dongle di Folder Lokal"**.
- **Biometrik Wajah:**
  - Arahkan wajah ke webcam lalu klik **"🔍 Cocokkan Biometrik"**, atau gunakan tombol **"⚡ Verifikasi Biometrik (Simulasi Cocok)"** untuk pengujian cepat tanpa webcam.

---

## 🐙 6. Panduan Publikasi ke GitHub (Untuk Tim)

Untuk mengunggah proyek ini ke repositori GitHub pribadi/organisasi kelompok:

```bash
# 1. Inisialisasi Git
git init

# 2. Tambahkan seluruh berkas
git add .

# 3. Buat commit pertama
git commit -m "feat: initial release of Sentix Digital Vault with 3FA and complete cryptographic engines"

# 4. Ganti nama branch utama menjadi main
git branch -M main

# 5. Hubungkan ke repositori GitHub Anda
# (Ganti URL di bawah dengan URL repo GitHub yang Anda buat)
git remote add origin https://github.com/username-anda/sentix-digital-vault.git

# 6. Push kode ke GitHub
git push -u origin main
```

Jika Anda menggunakan AI coding agent lokal (seperti Hermes Agent, Cursor, atau Copilot), agen lokal dapat langsung membaca `UI_GUIDE.md` untuk memahami seluruh arsitektur dan melanjutkan perombakan desain secara otomatis.

---

## ⚖️ 7. Lisensi & Etika Akademis
Proyek ini dikembangkan secara orisinal untuk memenuhi syarat Tugas Akhir Mata Kuliah Kriptografi UPN "Veteran" Yogyakarta Tahun Akademik 2026. Seluruh implementasi matematis algoritma dapat dipertanggungjawabkan secara ilmiah di hadapan dosen penguji.

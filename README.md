# AEGIS COLD CUSTODY
### Air-Gapped BIP-39 Mnemonic Seed Vault & Hardware Key Custodian Workstation

**Tugas Akhir Mata Kuliah Kriptografi**  
Program Studi Informatika, Jurusan Informatika, FTI  
Universitas Pembangunan Nasional "Veteran" Yogyakarta  

**Tim Pengembang (Kelompok 3):**  
1. **Oktavian Prasetya Adi** (NIM: 123240135) — *Security Architecture, 3FA Gatekeeper, Modern Ciphers (Vernam Stream, Block AES-128, RC4, PoW Blockchain, AES-256-GCM AEAD)*  
2. **Grace Rianty Butar Butar** (NIM: 123240036) — *Frontend Mnemonic UX, Classical Ciphers (Caesar & Vigenère)*  

---

## 1. Latar Belakang & Diferensiasi Proyek

**Aegis Cold Custody** adalah sistem *cryptographic workstation* kelas institusional yang dirancang dengan prinsip **Air-Gapped Cold Storage** untuk mengamankan aset digital bernilai tinggi, *BIP-39 Mnemonic Recovery Seed Phrase*, berkas *Keystore/Private Key*, serta buku besar transaksi *on-chain*.

Berbeda dari brankas dokumen kantoran biasa, Aegis Cold Custody mengadaptasi arsitektur **Hardware Security Module (HSM)** dan standar industri Web3/FinTech:
* **Zero-Trust Physical Gatekeeper:** Seluruh workstation terkunci secara fisik dan kriptografis; tidak dapat dibuka tanpa kombinasi token perangkat keras USB, verifikasi biometrik fisiologis, dan *Master Key Derivation*.
* **BIP-39 Mnemonic Armor:** 12/24 kata pemulihan dompet kripto dilindungi melalui pipeline super-enkripsi multi-lapis klasik dan modern untuk menangkal serangan *memory scraping* maupun pencurian fisik.
* **Tampilan Terpusat & Intuitif:** Mengusung antarmuka gelap modern (*Centered Card Layout* ~760px) dengan visualisasi tahapan kriptografi, telemetri anti-spoofing, dan metrik kualitas citra steganografi.

---

## 2. Alur Sistem: User Flow vs Developer Flow

```text
                           [ AEGIS COLD CUSTODY ]
                                      │
     ┌────────────────────────────────┼────────────────────────────────┐
     ▼                                ▼                                ▼
┌──────────────────┐        ┌──────────────────┐        ┌──────────────────────┐
│  1. MASUK (3FA)  │        │  2. REGISTRASI   │        │ 3. EVALUASI DOSEN    │
├──────────────────┤        ├──────────────────┤        ├──────────────────────┤
│ 1. Kunci Fisik   │        │ 1. Data Petugas  │        │ 1. Matriks 7         │
│    USB (HMAC)    │        │    (User ID)     │        │    Kriteria Dosen    │
│ 2. Wajah 128-D   │        │ 2. Master PIN    │        │ 2. 1-Click Fast      │
│    Anti-Spoofing │        │    (PBKDF2 Hash) │        │    Testing Bypass    │
│ 3. PIN PBKDF2    │        │ 3. Rekam Wajah   │        │ 3. Lab Uji Spoofing  │
│    Session Key   │        │ 4. Terbitkan Kunci│       │    Foto Layar HP     │
└────────┬─────────┘        │    USB Dongle    │        │ 4. Inspektur Raw     │
         │                  └────────┬─────────┘        │    Ciphertext DB     │
         ▼                           │                  └──────────────────────┘
┌────────────────────────────────────┴─────────────────────────────────────────┐
│                     DASHBOARD UTAMA WORKSTATION (5 MODUL)                    │
│                                                                              │
│ 1. BIP-39 Mnemonic Seed Armor      │ 4. Cold Ledger (PoW Blockchain)         │
│    (Caesar ➔ Vigenère ➔ Vernam     │    (SHA-256 Mining + Tamper Simulator)  │
│     ➔ AES-128 CBC)                 │                                         │
│ 2. Keystore Vault (Stream RC4)     │ 5. Whitelisted Address Book             │
│    (Enkripsi Berkas Dompet Biner)  │    (SQLite AES-256-GCM AEAD)            │
│ 3. Stego Paper Wallet (LSB)        │                                         │
│    (NFT Camouflage + PSNR/MSE)     │                                         │
└──────────────────────────────────────────────────────────────────────────────┘
```

### A. Alur Kerja Pengguna (User Flow)
1. **Registrasi Petugas Kustodi:**
   - Masukkan identitas resmi petugas kustodi dan User ID.
   - Tetapkan Master Passphrase (diamankan menggunakan *Salted PBKDF2-HMAC-SHA256* 100.000 iterasi).
   - Rekam geometri biometrik wajah secara langsung melalui kamera.
   - Terbitkan dan unduh token hardware `sentix_dongle.key` yang telah ditandatangani secara kriptografis (*HMAC-SHA256 signature*).
2. **Autentikasi 3FA Gatekeeper (NIST SP 800-63B AAL3):**
   - **Langkah 1 (What You Have):** Verifikasi keabsahan token HMAC pada flashdisk USB (pemindaian otomatis drive D:–Z: atau unggah file kunci).
   - **Langkah 2 (Who You Are):** Verifikasi biometrik wajah 128-D Cosine Distance ($\le 0.32$) yang diperkuat dengan **Active Liveness Detection** (deteksi bezel layar smartphone, pantulan cahaya, dan krominansi kulit YCbCr).
   - **Langkah 3 (What You Know):** Masukkan Master Passphrase untuk menurunkan *Master Session Key* sementara di memori RAM.
3. **Operasi Brankas Cold Custody:** Akses penuh ke 5 modul cold wallet untuk mengamankan aset kripto institusi.

### B. Alur Pengembang & Evaluasi Dosen (Developer Flow)
1. **Matriks 7 Kriteria Dosen:** Tabulasi komprehensif yang memetakan kriteria silabus perkuliahan secara terinci ke fitur cold wallet.
2. **1-Click Fast Bypass:** Akses langsung ke seluruh modul tanpa perangkat keras fisik untuk mempercepat proses demonstrasi di hadapan dosen penguji.
3. **Lab Pengujian Anti-Spoofing:** Alat uji skenario peretasan untuk membuktikan bahwa foto statis, hasil cetak, atau tampilan layar HP ditolak oleh sistem.
4. **Inspektur Basis Data Fisik:** Menampilkan isi fisik tabel `vault_records` di file SQLite dalam bentuk ciphertext mentah, membuktikan data tersimpan terenkripsi di disk.

---

## 3. Pemenuhan 7 Kriteria Dosen & Rujukan Materi Kuliah

| No | Kriteria di Silabus Dosen | Implementasi Teknis di Aegis Cold Custody | Rujukan Materi Kuliah |
| :---: | :--- | :--- | :--- |
| **1** | **Login Biometrik & USB Dongle Wajib** | **Faktor 1:** Kunci fisik USB Flashdisk bertanda tangan HMAC-SHA256.<br>**Faktor 2:** Verifikasi biometrik wajah 128-D Cosine Distance dengan proteksi Anti-Spoofing.<br>**Faktor 3:** Master Passphrase PBKDF2. | Slide Spek Tugas Akhir & NIST SP 800-63B |
| **2** | **Login Memakai Algoritma Kriptografi** | Penurunan Master Session Key dari passphrase menggunakan **PBKDF2-HMAC-SHA256** (100.000 iterasi + 16-byte random salt). | **Materi 8:** Algoritma Fungsi Hash Satu-Arah |
| **3** | **Pesan Teks Dienkripsi Super Enkripsi (Klasik + Modern)** | **Mnemonic Seed Armor:** 12/24 kata BIP-39 diproses melalui pipeline 4-tahap bertingkat:<br>$\text{Caesar} \rightarrow \text{Vigenère} \rightarrow \text{Vernam Stream (XOR)} \rightarrow \text{AES-128-CBC}$. | **Materi 3:** Caesar Cipher<br>**Materi 4:** Vigenère Cipher<br>**Materi 6 & 7:** Vernam & Block Cipher AES |
| **4** | **Pesan File Dienkripsi Algoritma Beda dari Teks** | **Keystore File Encryptor:** Enkripsi berkas cadangan dompet biner (`.json`, `.dat`, `.key`, `.wallet`) menggunakan **RC4 Stream Cipher** (KSA 256-byte + PRGA), berbeda fundamental dari cipher blok pada teks. | **Materi 7:** Contoh Implementasi Stream Cipher (RC4) |
| **5** | **Pesan Penting Dienkripsi pada Basis Data** | **Whitelisted Address Book & UTXO Store:** Basis data SQLite mengamankan alamat penarikan dan master key cadangan menggunakan authenticated encryption **AES-256-GCM AEAD** (Field-Level Encryption + 128-bit Auth Tag). | **Materi 6 & 7:** Mode Operasi Modern (AEAD GCM) |
| **6** | **Pesan Gambar Menggunakan Steganografi** | **Stego Paper Wallet & NFT Camouflage:** Menyembunyikan 12 kata seed phrase ke dalam kanal warna citra digital via **Spatial LSB Substitution**, dilengkapi analisis objektif **PSNR** ($> 65\text{ dB}$) dan **MSE** ($\approx 0$). | **Materi 9:** Steganografi Citra Digital (*Spatial LSB*) |
| **7** | **Aset Penting Diamankan Blockchain Sederhana** | **Cold Wallet Transaction Ledger:** Rantai blok pencatatan transfer saldo (BTC/ETH/USDT) berbasis hash SHA-256 berantai dengan konsensus **Proof-of-Work (PoW)** serta simulasi deteksi manipulasi (*tamper alert*). | **Materi 8:** Fungsi Hash & Blockchain Ledger |

---

## 4. Struktur Direktori Proyek

```text
sentix-digital-vault/
├── README.md               # Dokumentasi utama proyek & arsitektur sistem
├── requirements.txt        # Daftar dependensi modul Python
├── run.bat                 # Launcher otomatis 1-klik untuk Windows (cek dependensi & jalankan)
├── app.py                  # Antarmuka Streamlit (Centered Layout, Cold Wallet Workstation)
├── config.py               # Konstanta sistem, parameter kriptografi, & direktori
│
├── core/                   # Modul mesin kriptografi backend
│   ├── __init__.py
│   ├── auth_3fa.py         # Mesin 3FA: USB Dongle HMAC, Biometrik 128-D + Anti-Spoofing, PBKDF2
│   ├── super_encryption.py # Pipeline 4-Tahap: Caesar, Vigenère, Vernam XOR, AES-128
│   ├── file_cipher.py      # Stream Cipher RC4 (KSA & PRGA) untuk berkas keystore
│   ├── database_vault.py   # Brankas basis data SQLite + Field-Level AES-256-GCM AEAD
│   ├── steganography.py    # Spatial LSB Steganography + Evaluasi Ilmiah PSNR/MSE
│   └── blockchain.py       # Rantai Blok Transaksi PoW SHA-256 + Tamper Detection
│
├── tests/                  # Automated Unit Testing Suite
│   ├── __init__.py
│   └── test_crypto_engines.py # Pengujian end-to-end 10 skenario pengujian
│
├── scripts/                # Perkakas CLI pendukung
│   ├── generate_dongle.py  # Script CLI pembuat token kunci USB fisik/virtual
│   └── enroll_face.py      # Script CLI perekaman embedding biometrik wajah
│
└── data/                   # Penyimpanan lokal terlindungi (Database SQLite, Master Face, Ledger)
```

---

## 5. Panduan Menjalankan & Pengujian

### ⚡ Cara Termudah (Windows — 1-Klik Langsung Jalan)
Cukup **klik dua kali berkas `run.bat`**.  
Skrip ini akan otomatis mendeteksi Python di PATH, memverifikasi dependensi `requirements.txt` (menginstal pustaka yang belum lengkap), dan langsung membuka aplikasi Aegis Cold Custody di browser default (`http://localhost:8501`).

---

### Cara Manual via Terminal:

#### 1. Siapkan Lingkungan Virtual
```bash
python -m venv venv

# Windows (PowerShell):
.\venv\Scripts\Activate.ps1
# Linux / macOS:
source venv/bin/activate
```

#### 2. Pasang Dependensi
```bash
pip install -r requirements.txt
```

#### 3. Jalankan Pengujian Unit Otomatis (Automated Tests)
```bash
python -m unittest tests/test_crypto_engines.py
```
*Output Verifikasi:*
```text
..........
----------------------------------------------------------------------
Ran 10 tests in 0.443s

OK
```
*(Seluruh 10 skenario pengujian kriptografi, 3FA, Anti-Spoofing, dan Database lulus 100%).*

#### 4. Jalankan Aplikasi
```bash
streamlit run app.py
```
Akses aplikasi melalui peramban di: `http://localhost:8501`.

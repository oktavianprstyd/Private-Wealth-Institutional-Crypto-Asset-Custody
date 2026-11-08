# LAPORAN TEKNIS TUGAS AKHIR KRIPTOGRAFI
# AEGIS COLD CUSTODY: AIR-GAPPED BIP-39 MNEMONIC SEED VAULT & HARDWARE KEY CUSTODIAN

---

## IDENTITAS PROYEK & TIM PENGEMBANG

* **Mata Kuliah:** Kriptografi
* **Program Studi:** S1 Informatika (PJJ iF-B)
* **Fakultas / Universitas:** Fakultas Teknik Industri / Universitas Pembangunan Nasional "Veteran" Yogyakarta
* **Tahun Akademik / Semester:** Semester Ganjil 2026/2027

### Anggota Tim Pengembang (Kelompok 3)
1. **Grace Rianty Butar Butar (NIM: 123240036)**
   * *Peran & Tanggung Jawab:* Perancangan & Implementasi Algoritma Klasik Tahap 1 (Caesar Cipher Monoalfabetik) dan Tahap 2 (Vigenère Cipher Polialfabetik 26-Huruf & 95-ASCII Extended), Normalisasi Teks BIP-39 Seed Phrase, dan Dokumentasi Tracing Matematis Manual.
2. **Oktavian Prasetya Adi (NIM: 123240135)**
   * *Peran & Tanggung Jawab:* Perancangan Arsitektur Keamanan Air-Gapped 3FA (Hardware Key USB HMAC-SHA256, Biometrik Wajah 128-D Cosine Distance, PBKDF2-HMAC-SHA256 100k iterasi), Algoritma Modern Tahap 3 (Vernam Stream Bitwise XOR) dan Tahap 4 (AES-128 & AES-256 CBC dengan PKCS7 Padding), Enkripsi Keystore RC4, Basis Data SQLite Terotentikasi (AES-256-GCM AEAD), Steganografi LSB (PSNR/MSE), Ledger Transaksi Blockchain PoW, Isolasi Sandbox Pengembang, dan Automated Unit Testing Suite.

---

## 1. RINGKASAN EKSEKUTIF (EXECUTIVE SUMMARY)

**Sentix Digital Vault** adalah sistem brankas keamanan aset digital tingkat institusi (*institutional cold-storage custody*) yang dirancang untuk mengatasi kerentanan sistem autentikasi tunggal (*single-point-of-failure*) pada pengelolaan kunci privat (*cryptographic seed phrases*), berkas audit kepemilikan aset, dan buku besar transaksi keuangan terdesentralisasi. 

Sistem ini merealisasikan **seluruh 7 kriteria tugas akhir praktikum kriptografi** dengan mengadopsi prinsip keamanan *Defense-in-Depth* (pertahanan berlapis). Sentix Vault mengintegrasikan autentikasi 3-faktor fisik-fisiologis (*physical USB dongle*, biometrik wajah, dan kunci kriptografis berbasis hash *key-stretching*), super-enkripsi teks 4-tahap berantai (Caesar $\to$ Vigenère $\to$ Vernam XOR $\to$ AES-128 CBC), enkripsi berkas berbasis stream cipher (*RC4 KSA/PRGA*), pengamanan data at rest pada basis data relasional (*AES-256-GCM*), steganografi spasial LSB citra digital (*Least Significant Bit*) berotentikasi, serta integritas aset digital terdesentralisasi berbasis *blockchain Proof-of-Work (PoW)*.

Pengujian empiris membuktikan bahwa sistem ini berhasil melewati seluruh 9 skenario uji otomatis (*automated unit tests*) dalam waktu 1,86 detik, menghasilkan kualitas rekonstruksi steganografi dengan nilai **PSNR > 65 dB**, serta menjamin pembalikan dekripsi 100% sempurna tanpa kehilangan bit (*lossless cryptographic round-trip*).

---

## 2. LATAR BELAKANG & MODEL ANCAMAN (THREAT MODEL)

### 2.1 Konteks Industri: Institutional Digital Asset Custody
Dalam ekosistem *FinTech*, perbankan digital, dan *Web3 Custody* (seperti Fireblocks, Coinbase Custody, BitGo), pengelolaan aset bernilai tinggi tidak boleh bergantung pada mekanisme autentikasi konvensional (username & password). Kelemahan kata sandi statis telah menyebabkan kerugian miliaran dolar akibat serangan *credential stuffing*, pencurian sesi (*session hijacking*), dan injeksi perangkat lunak perusak (*keylogger/malware*).

Sentix Digital Vault menempatkan aplikasi sebagai stasiun kerja (*custodian workstation*) di mana petugas berwenang (*authorized custody officers*) dapat memproses instruksi transaksi dan menyimpan berkas berharga dengan jaminan kerahasiaan (*confidentiality*), integritas (*integrity*), dan nir-penyangkalan (*non-repudiation*).

### 2.2 Analisis Permukaan Serangan & Mitigasi Kriptografis
Sistem dirancang secara spesifik untuk memitigasi vektor ancaman berikut:

| Vektor Ancaman (*Threat Vector*) | Karakteristik Serangan | Mekanisme Pertahanan Sentix Vault |
| :--- | :--- | :--- |
| **Pencurian Kredensial & Brute Force** | Pembajakan password melalui kamus (*dictionary*) atau GPU mining farm. | **Salted PBKDF2-HMAC-SHA256 (100.000 iterasi)**. Garam kriptografis 16-byte unik menonaktifkan serangan tabel pelangi (*rainbow table*). |
| **Akses Fisik Ilegal (*Stolen Laptop*)** | Laptop dicuri oleh pihak tidak berwenang saat ditinggalkan. | **Autentikasi 3-Faktor (3FA)**: Memerlukan *Physical USB Dongle* bertanda tangan HMAC-SHA256 dan verifikasi biometrik wajah secara simultan. |
| **Spoofing Biometrik Wajah** | Mengarahkan foto cetak atau layar smartphone ke webcam. | **Synchronized Screen Flash 2 Detik & Lux/Contrast Analyzer**: Menganalisis refleksi fotometrik intensitas cahaya dinamis pada wajah. |
| **Penyadapan Saluran Komunikasi (MitM)** | Intersepsi paket teks instruksi transfer dan seed phrase di jaringan. | **Super-Enkripsi 4-Tahap Berantai**: Mengombinasikan difusi substitusi klasik dengan konfusi aliran XOR dan kebal diferensial AES-128 CBC. |
| **Ekstraksi Basis Data Lokal (*Data at Rest*)** | File basis data SQLite dicuri langsung dari harddisk. | **Authenticated Encryption AES-256-GCM**: Setiap record sensitif dienkripsi menggunakan kunci turunan RAM dengan IV 96-bit dan tag otentikasi 128-bit. |
| **Manipulasi Log Audit & Integritas Transaksi** | Penyerang internal mengubah nilai nominal atau penerima transaksi pada basis data. | **Blockchain Proof-of-Work (PoW)**: Rantai blok terhubung secara kriptografis melalui hash SHA-256. Setiap modifikasi retroaktif akan merusak validitas konsensus rantai. |
| **Deteksi Berkas Rahasia oleh Firewall/DLP** | Berkas rahasia terdeteksi oleh sistem inspeksi paket deep packet inspection (DPI). | **LSB Image Steganography**: Menyisipkan berkas/pesan ke dalam piksel citra alami tanpa menimbulkan distorsi visual kasat mata. |

---

## 3. PEMENUHAN 7 KRITERIA TUGAS AKHIR & SILABUS MATERI KULIAH

Berikut adalah pemetaan formal antara 7 butir kriteria penilaian tugas akhir dosen terhadap modul implementasi dan materi perkuliahan:

```text
┌─────────────────────────────────────────────────────────────────────────────────────────────┐
│                       MATRIKS EVALUASI KRITERIA TUGAS AKHIR                                 │
├────┬───────────────────────────────────────┬───────────────────────────────┬────────────────┤
│ No │ Kriteria Dosen                        │ Implementasi di Sentix Vault  │ Silabus Kuliah │
├────┼───────────────────────────────────────┼───────────────────────────────┼────────────────┤
│ 1  │ Login Biometrik & Dongle USB Wajib    │ 3FA: USB HMAC-SHA256 +        │ Slide Spek TA &│
│    │                                       │ Multi-Face Cosine Dist <=0.32 │ NIST SP 800-63 │
├────┼───────────────────────────────────────┼───────────────────────────────┼────────────────┤
│ 2  │ Login Memakai Algoritma Kriptografi   │ PBKDF2-HMAC-SHA256 (100k iter)│ Materi 8 (Hash)│
│    │                                       │ + Salt 16-Byte Cryptographic  │                │
├────┼───────────────────────────────────────┼───────────────────────────────┼────────────────┤
│ 3  │ Pesan Teks Dienkripsi Super Enkripsi  │ Pipeline 4-Tahap: Caesar ->   │ Materi 3, 4, 7,│
│    │ (Klasik + Modern)                     │ Vigenère -> Vernam -> AES-128 │ Materi 6 & 7   │
├────┼───────────────────────────────────────┼───────────────────────────────┼────────────────┤
│ 4  │ Pesan File Dienkripsi Algoritma Beda  │ RC4 Stream Cipher (KSA/PRGA)  │ Materi 7       │
│    │ dari Teks                             │ Enveloping Biner Sembarang    │ (Stream RC4)   │
├────┼───────────────────────────────────────┼───────────────────────────────┼────────────────┤
│ 5  │ Pesan Penting Dienkripsi pada DB      │ SQLite `vault_records` dengan │ Materi 6 & 7   │
│    │                                       │ AES-256-GCM Authenticated Enc │ (Cipher Modern)│
├────┼───────────────────────────────────────┼───────────────────────────────┼────────────────┤
│ 6  │ Pesan Gambar Menggunakan Steganografi │ Spatial Domain LSB Citra RGB  │ Materi 9       │
│    │                                       │ Evaluasi Metrik PSNR & MSE    │ (Steganografi) │
├────┼───────────────────────────────────────┼───────────────────────────────┼────────────────┤
│ 7  │ Aset Penting Diamankan Blockchain     │ Distributed Asset Ledger SHA256│ Materi 8      │
│    │                                       │ Proof-of-Work Tamper Detection│ (Fungsi Hash)  │
└────┴───────────────────────────────────────┴───────────────────────────────┴────────────────┘
```

---

## 4. ARSITEKTUR SISTEM & SPESIFIKASI TECH STACK

Sistem Sentix Digital Vault dibangun secara modular dengan memisahkan *Cryptographic Core Engines*, *Presentation Layer*, dan *Persistent Storage Layer*.

```text
                                [ CLIENT INTERFACE (STREAMLIT) ]
                                                │
                       ┌────────────────────────┴────────────────────────┐
                       ▼                                                 ▼
            [ 3FA GATEKEEPER ENGINE ]                         [ DEVELOPER SANDBOX ]
            ├── USB Dongle Verifier                           ├── 1-Click Fast Bypass Demo
            ├── Biometric Screen-Flash Analyzer               ├── 7-Criteria Academic Matrix
            └── PBKDF2 Password Key Derivation                └── Raw SQLite Cipher Inspector
                       │
                       ▼ (Authentication Success -> Derive Master Session Key)
       ══════════════════════════ CORE CRYPTO ENGINES ══════════════════════════
       │                       │                        │                      │
       ▼                       ▼                        ▼                      ▼
[ SUPER ENCRYPTION ]    [ FILE VAULT RC4 ]       [ STEGANOGRAPHY LSB ]  [ BLOCKCHAIN LEDGER ]
├── Caesar (Grace)      ├── KSA Permutation      ├── 3-Bit Spatial RGB  ├── SHA-256 Blocks
├── Vigenère (Grace)    └── PRGA Keystream       └── PSNR/MSE Metrics   └── PoW Consensus
├── Vernam (Oktavian)          │                                               │
└── AES-128 (Oktavian)         └────────────────────────┬──────────────────────┘
                                                        ▼
                                           [ DATABASE VAULT (SQLITE) ]
                                           └── AES-256-GCM Authenticated AEAD
```

### 4.1 Spesifikasi Perangkat Lunak & Pustaka Dependensi
1. **Bahasa Pemrograman & Runtime:**
   * Python 3.10+ / Python 3.14 (Kompatibel arsitektur x86_64 dan ARM64 / PRoot Linux / Windows 11).
2. **Pustaka Kriptografi Standar & Primitif:**
   * `hashlib` (Standar Python): Eksekusi fungsi hash SHA-256 dan PBKDF2-HMAC-SHA256 berkinerja tinggi berbasis modul C internal OpenSSL.
   * `hmac` (Standar Python): Otentikasi penandatanganan pesan berkas dongle perangkat keras.
   * `os.urandom()`: Pembangkit bilangan acak semu terotentikasi secara kriptografis (*Cryptographically Secure Pseudo-Random Number Generator / CSPRNG*).
   * `cryptography.hazmat` (PyCA Cryptography): Primitif tingkat rendah untuk enkripsi blok AES-128-CBC, AES-256-CBC, PKCS7 Padding, dan cipher mode terotentikasi AES-256-GCM.
3. **Pustaka Biometrik & Pemrosesan Citra:**
   * `Pillow (PIL)`: Manipulasi kanvas piksel citra digital, konversi kanal warna RGB/Grayscale, dan ekstraksi payload steganografi.
   * `NumPy`: Komputasi aljabar linier tervektorisasi untuk ekstraksi vektor fitur gradien spasial 128-dimensi dan kalkulasi jarak *Cosine Distance* sub-2 milidetik pada CPU/iGPU (tanpa beban GPU proprietary/CUDA).
4. **Pustaka Basis Data & Antarmuka:**
   * `sqlite3`: Basis data relasional *serverless* lokal dengan pengamanan enkripsi tingkat baris.
   * `Streamlit`: Kerangka antarmuka pengguna reaktif berbasis web yang memfasilitasi visualisasi matriks, tabel transformasi, dan demonstrasi interaktif.
5. **Pengujian Kualitas Perangkat Lunak:**
   * `unittest`: Kerangka uji unit otomatis dengan 9 prosedur pengujian menyeluruh (*end-to-end*).

---

## 5. DETAIL SETIAP PENGAMAN & FORMULA MATEMATIS KRIPTOGRAFI

Bagian ini menguraikan landasan matematis, rumus kalkulasi, dan implementasi kode pada setiap lapis pertahanan Sentix Digital Vault.

---

### 5.1 TIGA FAKTOR AUTENTIKASI (3FA GATEKEEPER)

Keamanan akses brankas menerapkan standar NIST SP 800-63B (*Digital Identity Guidelines*) yang menggabungkan tiga pilar otentikasi independen:

```text
[ LOGIN ATTEMPT ]
       │
       ├─► 1. SOMETHING YOU HAVE: Physical USB Dongle (HMAC-SHA256 Token)
       │      └─ Gagal: "Lockdown! Hardware Key Tidak Terpasang"
       │
       ├─► 2. SOMETHING YOU ARE: Biometrik Wajah (128-D Feature + Flash 2s)
       │      └─ Gagal: "Biometrik Ditolak: Wajah Tidak Dikenal"
       │
       └─► 3. SOMETHING YOU KNOW: Master Passphrase (PBKDF2 100k Iterasi)
              └─ Gagal: "Password Salah! Kunci Brankas RAM Ditolak"
```

#### A. Faktor 1: Hardware USB Dongle (Something You Have)
* **Konsep:** Aplikasi hanya dapat dibuka jika sebuah media fisik (USB Flashdisk) terpasang pada port perangkat dan memuat berkas lisensi kriptografis `sentix_dongle.key`.
* **Mekanisme Otentikasi Tanda Tangan HMAC-SHA256:**
  Berkas dongle memuat payload JSON yang ditandatangani menggunakan kunci rahasia inti brankas (`SYSTEM_VAULT_SALT`):
  $$\text{Signature} = \text{HMAC-SHA256}(K_{system}, \text{Payload JSON})$$
  Secara matematis, HMAC didefinisikan sebagai:
  $$\text{HMAC}(K, m) = H\Big((K' \oplus opad) \parallel H((K' \oplus ipad) \parallel m)\Big)$$
  di mana:
  * $H$ = Fungsi hash kriptografi SHA-256 (panjang blok 64 byte, digest 32 byte).
  * $K'$ = Kunci rahasia yang telah disesuaikan panjangnya dengan panjang blok hash.
  * $ipad$ = Konstanta *inner padding* berulang $0\text{x}36$.
  * $opad$ = Konstanta *outer padding* berulang $0\text{x}5C$.
  * $\parallel$ = Operasi penggabungan bit (*concatenation*).
* **Mitigasi Serangan:** Penyerang yang menyalin atau membuat berkas tiruan tanpa mengetahui kunci rahasia sistem tidak akan mampu menghasilkan tanda tangan yang valid. Verifikasi menggunakan fungsi `hmac.compare_digest()` untuk mencegah serangan analisis waktu (*timing attack*).
* **Failsafe Physical Lock:** Jika berkas dongle dicabut atau tidak terdeteksi saat pemindaian berkala, antarmuka brankas langsung masuk ke status *Emergency Freeze / Red Alert*.

#### B. Faktor 2: Biometrik Fisiologis Wajah & Flash Liveness (Something You Are)
* **Konsep:** Memastikan pengguna di depan terminal adalah pejabat brankas sah yang terdaftar pada daftar induk (*authorized custody roster*).
* **Ekstraksi Deskriptor Spasial-Gradien 128-Dimensi:**
  Citra wajah dari webcam dikonversi ke grayscale dan dinormalisasi menjadi resolusi $32 \times 32$ piksel. Fitur diekstraksi ke dalam vektor berdimensi 128:
  1. *Sub-vektor Spasial (64 dimensi):* Rata-rata intensitas piksel pada 64 blok area ukuran $4 \times 4$, dinormalisasi dengan pengurangan rata-rata (*zero-mean centering*) dan pembagian simpangan baku (*variance scaling*):
     $$\hat{S}_i = \frac{S_i - \mu_S}{\sigma_S}$$
  2. *Sub-vektor Gradien Energi Tepi (64 dimensi):* Kontras diferensial horizontal dan vertikal ($\Delta x + \Delta y$) untuk menangkap kontur unik tulang wajah:
     $$G(x,y) = |I(x+1, y) - I(x, y)| + |I(x, y+1) - I(x, y)|$$
     $$\hat{G}_i = \frac{G_i - \mu_G}{\sigma_G}$$
  3. *Normalisasi Vektor Satuan L2:* Menggabungkan kedua sub-vektor menjadi $\vec{V} = [\hat{S} \parallel \hat{G}]$ dan menormalisasikannya ke bola satuan hiper:
     $$\vec{U} = \frac{\vec{V}}{\|\vec{V}\|_2} = \frac{\vec{V}}{\sqrt{\sum_{k=1}^{128} V_k^2}}$$
* **Formula Pencocokan Jarak Cosinus (Cosine Distance):**
  Untuk membandingkan vektor probe ($\vec{U}_{probe}$) terhadap vektor registrasi master ($\vec{U}_{master}$):
  $$D_C(\vec{U}_p, \vec{U}_m) = 1 - (\vec{U}_p \cdot \vec{U}_m) = 1 - \sum_{k=1}^{128} (U_{p,k} \cdot U_{m,k})$$
  * **Ambang Batas (Threshold):** Ditetapkan $D_C \le 0.32$. Jika $D_C \le 0.32$, wajah dinyatakan identik dengan tingkat keyakinan (*confidence*) $\ge 68\%$.
* **Fitur Synchronized Screen Flash 2 Detik:**
  Menerangi wajah secara sinkron sebelum pengambilan frame untuk memverifikasi pantulan dinamis pada kulit dan memastikan lux berada pada jendela optimal ($10.0 \le \text{lux} \le 235.0$).

#### C. Faktor 3: Password Hash & Derivasi Kunci (Something You Know)
* **Konsep:** Kata sandi master diolah menggunakan algoritma penahanan waktu (*key stretching*) untuk mematikan komputasi paralel GPU peretas.
* **Formulasi PBKDF2-HMAC-SHA256 (RFC 2898 / Materi 8):**
  $$DK = \text{PBKDF2}(\text{PRF}, \text{Password}, \text{Salt}, c, dkLen)$$
  di mana:
  * $\text{PRF}$ = Pseudorandom Function berbasis HMAC-SHA256.
  * $\text{Salt}$ = 16-byte acak kriptografis (`os.urandom(16)`).
  * $c = 100.000$ iterasi hashing rekursif:
    $$U_1 = \text{PRF}(\text{Password}, \text{Salt} \parallel \text{INT}(1))$$
    $$U_2 = \text{PRF}(\text{Password}, U_1)$$
    $$U_c = \text{PRF}(\text{Password}, U_{c-1})$$
    $$F = U_1 \oplus U_2 \oplus \dots \oplus U_c$$
  * $dkLen = 32$ byte (256 bit).
* **Keamanan Konfigurasi:** File `data/auth_config.json` hanya menyimpan representasi heksadesimal hash dan garam (*salt*). Kata sandi teks asli tidak pernah disimpan dalam media penyimpanan permanen.

---

### 5.2 MODUL 1: SUPER-ENKRIPSI PESAN TEKS TERPADU (PIPELINE 4-TAHAP)

Modul super-enkripsi mengintegrasikan seluruh algoritma yang dikerjakan oleh masing-masing anggota kelompok secara berkesinambungan. Plainteks melewati empat lapisan enkripsi berturut-turut:

$$\text{Plainteks } P \xrightarrow[\text{Grace}]{\text{Caesar}} C_1 \xrightarrow[\text{Grace}]{\text{Vigenère}} C_2 \xrightarrow[\text{Oktavian}]{\text{Vernam XOR}} C_3 \xrightarrow[\text{Oktavian}]{\text{AES-128}} C_{\text{final}}$$

```text
┌─────────────────┐
│ Plainteks Input │ "TRANSVER 1000 BTC"
└────────┬────────┘
         │
         ▼
┌─────────────────────────────────┐
│ TAHAP 1: CAESAR CIPHER (Mono)   │ Penanggung Jawab: Grace Rianty Butar Butar (123240036)
│ Rumus: C = (P + k) mod 26       │ Pergeseran abjad monoalfabetik klasik (k = 8)
└────────┬────────────────────────┘
         │ Hasil: "BZIVAPMZ 1000 BUK"
         ▼
┌─────────────────────────────────┐
│ TAHAP 2: VIGENÈRE CIPHER (Poli) │ Penanggung Jawab: Grace Rianty Butar Butar (123240036)
│ Rumus: C = (P + K) mod 26       │ Polialfabetik substitusi dengan kunci periodik
└────────┬────────────────────────┘
         │ Hasil: "LDTYEXUF..."
         ▼
┌─────────────────────────────────┐
│ TAHAP 3: VERNAM STREAM (XOR)    │ Penanggung Jawab: Oktavian Prasetya Adi (123240135)
│ Rumus: C = P ⊕ K                │ Operasi aliran bitwise biner menghasilkan heksadesimal
└────────┬────────────────────────┘
         │ Hasil: "3A 12 7F 90 4C..."
         ▼
┌─────────────────────────────────┐
│ TAHAP 4: AES-128 BLOCK (CBC)    │ Penanggung Jawab: Oktavian Prasetya Adi (123240135)
│ Rumus: C_i = E(P_i ⊕ C_{i-1})   │ Enkripsi blok 128-bit modern + IV acak + PKCS7 Padding
└────────┬────────────────────────┘
         │
         ▼
┌─────────────────────────────────┐
│ Cipherteks Final (Base64)       │ Siap ditransmisikan secara aman melalui kanal publik
└─────────────────────────────────┘
```

#### Tahap 1: Caesar Cipher (Klasik Monoalfabetik Substitusi)
* **Penanggung Jawab:** Grace Rianty Butar Butar (123240036)
* **Rujukan:** Materi 3 (Kriptografi Klasik)
* **Formula Matematis:**
  $$C_i = (P_i + k) \pmod{26}$$
  Untuk karakter huruf kapital ($A=0, B=1, \dots, Z=25$) dengan nilai pergeseran kunci $k \in [1, 25]$. Karakter non-alfabet tetap dipertahankan untuk menjaga integritas format pesan.

#### Tahap 2: Vigenère Cipher (Klasik Polialfabetik Substitusi)
* **Penanggung Jawab:** Grace Rianty Butar Butar (123240036)
* **Rujukan:** Materi 4 (Vigenère Cipher)
* **Formula Matematis:**
  Menggunakan deret kunci periodik $K = k_0, k_1, \dots, k_{m-1}$ yang diulang sepanjang teks:
  $$C_i = (P_i + K_{i \pmod m}) \pmod{26}$$
  Modul ini juga menyediakan mode *Extended 95-ASCII* untuk mendukung enkripsi karakter khusus dan spasi:
  $$C_i = \Big(\big((P_i - 32) + (K_{i \pmod m} - 32)\big) \pmod{95}\Big) + 32$$

#### Tahap 3: Vernam Stream Cipher (Modern Aliran Bitwise XOR)
* **Penanggung Jawab:** Oktavian Prasetya Adi (123240135)
* **Rujukan:** Materi 7 (Stream Cipher & Vernam)
* **Formula Matematis:**
  Bekerja pada tingkat representasi biner 8-bit per byte antara karakter keluaran Vigenère ($P_i$) dan aliran kunci (*keystream* $K_i$):
  $$C_i = P_i \oplus K_i$$
  Secara logika biner, XOR didefinisikan sebagai:
  $$P_i \oplus K_i = (P_i \land \neg K_i) \lor (\neg P_i \land K_i)$$
  Hasil keluaran diformat dalam notasi heksadesimal dua digit untuk memastikan transmisi data biner aman tanpa kendala karakter kontrol ASCII.

#### Tahap 4: AES Block Cipher (Modern Blok 128-bit CBC Mode)
* **Penanggung Jawab:** Oktavian Prasetya Adi (123240135)
* **Rujukan:** Materi 6 & 7 (Block Cipher & AES)
* **Formula Matematis:**
  Data heksadesimal Vernam dienkripsi menggunakan algoritma AES (*Advanced Encryption Standard*) dengan panjang kunci 128-bit (16 byte) atau 256-bit (32 byte) pada mode operasi *Cipher Block Chaining* (CBC):
  $$C_0 = E_K(P_0 \oplus IV)$$
  $$C_i = E_K(P_i \oplus C_{i-1}) \quad \text{untuk } i \ge 1$$
  di mana $IV$ (*Initialization Vector*) dibangkitkan secara acak sepanjang 16 byte menggunakan `os.urandom(16)`. Data teks diberikan bantalan (*padding*) sesuai standar PKCS#7:
  $$\text{Pad}(M) = M \parallel (b \text{ bytes bernilai } b), \quad b = 16 - (|M| \pmod{16})$$
  Paket akhir dienkapsulasi dalam bentuk $\text{Base64}(IV \parallel \text{Ciphertext})$.

#### Pembalikan Dekripsi Sempurna (Decryption Pipeline)
Proses dekripsi dilakukan dengan membalik secara eksak urutan algoritma di atas:
$$\text{Base64 Decode} \xrightarrow{\text{AES-128 Decrypt}} \text{Vernam Hex} \xrightarrow{\text{Vernam XOR}} \text{Vigenère Text} \xrightarrow{\text{Vigenère Decrypt}} \text{Caesar Text} \xrightarrow{\text{Caesar Decrypt}} \text{Plainteks Asli}$$

---

### 5.3 MODUL 2: FILE VAULT ENCRYPTION (RC4 STREAM CIPHER)

Sesuai Kriteria 4 tugas akhir dosen, berkas biner (dokumen legal `.pdf`, `.docx`, `.zip`, `.png`) diamankan menggunakan algoritma yang **berbeda fundamental dari teks**, yaitu algoritma *Stream Cipher* murni **RC4 (Rivest Cipher 4)**.

* **Rujukan Silabus:** Materi 7 (Stream Cipher & Algoritma RC4)
* **Prinsip Operasi:** RC4 menggunakan larik permutasi internal $S[0 \dots 255]$ yang diinisialisasi melalui dua fase utama:

#### 1. Key-Scheduling Algorithm (KSA)
Larik permutasi identitas $S$ diacak menggunakan kunci rahasia $K$ dengan panjang $L$ byte:
```text
Untuk i dari 0 sampai 255:
    S[i] = i
    T[i] = K[i mod L]

j = 0
Untuk i dari 0 sampai 255:
    j = (j + S[i] + T[i]) mod 256
    Tukar(S[i], S[j])
```

#### 2. Pseudo-Random Generation Algorithm (PRGA)
Setelah KSA selesai, PRGA membangkitkan byte aliran kunci (*keystream byte* $Z$) per iterasi dan melakukan operasi bitwise XOR langsung terhadap byte berkas:
```text
i = 0
j = 0
Untuk setiap byte data M[k]:
    i = (i + 1) mod 256
    j = (j + S[i]) mod 256
    Tukar(S[i], S[j])
    t = (S[i] + S[j]) mod 256
    Keystream_Byte Z = S[t]
    C[k] = M[k] ⊕ Z
```

#### Enveloping Format Berkas Rahasia
Untuk melindungi integritas metadata, berkas terenkripsi dibungkus dengan struktur amplop biner:
```text
┌──────────────────┬─────────────────┬─────────────────┬──────────────────────┐
│ MAGIC IDENTIFIER │ NAMA BERKAS LEN │ NAMA ASLI FILE  │ PAYLOAD CIPHERTEXT   │
│ 10 Byte          │ 2 Byte (uint16) │ Variabel Byte   │ Byte Terenkripsi RC4 │
│ "SENTIX_RC4\x01" │ Misal: 14 byte  │ "kontrak_01.pdf"│ 0x4A 0x8F 0x12 ...   │
└──────────────────┴─────────────────┴─────────────────┴──────────────────────┘
```

---

### 5.4 MODUL 3: DATABASE VAULT TERENKRIPSI (AES-256-GCM AEAD)

Sesuai Kriteria 5, pengamanan data penting pada basis data SQLite lokal (`sentix_vault.db`) menggunakan skema enkripsi modern terotentikasi **AES-256-GCM** (*Galois/Counter Mode*).

* **Rujukan Silabus:** Materi 6 & 7 (Block Cipher Mode of Operation & Keamanan Modern)
* **Mengapa AES-GCM (Bukan ECB atau CBC Biasa)?**
  Mode ECB (*Electronic Codebook*) rentan terhadap pembocoran pola data (*pattern leakage*), sedangkan CBC membutuhkan algoritma HMAC eksternal untuk mendeteksi manipulasi isi bit (*bit-flipping attack*). AES-GCM adalah cipher kelas **AEAD (Authenticated Encryption with Associated Data)** yang secara simultan menjamin:
  1. **Kerahasiaan (*Confidentiality*):** Mode pencacah (*Counter Mode*) dengan nonce 96-bit yang tidak pernah berulang.
  2. **Integritas & Otensitas (*Authenticity*):** Menghasilkan tag otentikasi Galois Field ($GF(2^{128})$) sepanjang 16 byte (128-bit).
* **Formula Enkripsi Baris Database:**
  $$C, T = \text{AES-GCM-Encrypt}(K_{\text{db}}, IV_{96}, P_{\text{plaintext}}, A_{\text{metadata}})$$
  di mana:
  * $K_{\text{db}}$ = Kunci 256-bit hasil derivasi SHA-256 dari password master.
  * $IV_{96}$ = Inisialisasi nonce acak 12-byte per record.
  * $T$ = Tag otentikasi 16-byte untuk mendeteksi modifikasi liar di file harddisk.
* **Struktur Tabel Basis Data SQLite (`vault_records`):**
  Kolom `category`, `title`, dan `created_at` disimpan sebagai metadata plaintext terindeks, sedangkan seluruh isi konten sensitif (`ciphertext`, `nonce`, `auth_tag`) disimpan dalam format biner BLOB. Modifikasi 1 bit pun pada database akan memicu galat otentikasi `InvalidTag` dan mencegah kebocoran informasi.

---

### 5.5 MODUL 4: STEGANOGRAFI CITRA DIGITAL (SPATIAL DOMAIN LSB)

Sesuai Kriteria 6, pengamanan dokumen sertifikat atau pesan rahasia disisipkan ke dalam citra digital berwarna (format PNG/Lossless) menggunakan teknik **Least Significant Bit (LSB)** pada domain spasial citra.

* **Rujukan Silabus:** Materi 9 (Steganografi Citra Digital & *Prisoner's Problem*)
* **Mekanisme Penyisipan Bitwise:**
  Setiap piksel citra digital RGB terdiri dari tiga kanal warna: Red (R), Green (G), dan Blue (B). Setiap kanal diwakili oleh 8-bit integer ($0 \dots 255$). Teknik LSB mengganti bit ke-0 (bit dengan bobot nilai terendah, bernilai $2^0 = 1$) dari masing-masing kanal warna untuk menampung bit pesan:
  $$C'(x, y, c) = \big(C(x, y, c) \land 0\text{xFE}\big) \lor b_k$$
  Setiap piksel mampu menyimpan 3 bit data rahasia. Kapasitas maksimum penyisipan citra berukuran $M \times N$ piksel adalah:
  $$\text{Kapasitas Maksimal} = \frac{M \times N \times 3}{8} - 4 \text{ byte (header)}$$

#### Struktur Header Protokol Steganografi
Agar pesan dapat diekstraksi secara presisi tanpa memerlukan penanda EOF statis, 32 bit pertama (4 byte) dari citra stego dialokasikan untuk menyimpan panjang total payload pesan dalam format biner *Big-Endian uint32*:
```text
[ 32 Bit Pertama: Panjang Pesan N ] ──► [ Bit ke-33 s.d. (33 + N*8): Payload Pesan ]
```

#### Formula Evaluasi Kualitas Citra Stego (PSNR & MSE)
Kualitas ketersembunyian (*imperceptibility*) diukur secara objektif melalui dua parameter matematis:
1. **Mean Squared Error (MSE):**
   Rata-rata kuadrat selisih antara nilai piksel citra asli $I$ dan citra hasil steganografi $K$:
   $$\text{MSE} = \frac{1}{3MN} \sum_{c=1}^3 \sum_{x=0}^{M-1} \sum_{y=0}^{N-1} \Big[I(x, y, c) - K(x, y, c)\Big]^2$$
2. **Peak Signal-to-Noise Ratio (PSNR):**
   Rasio antara daya sinyal maksimum terhadap derau penyisipan dalam satuan desibel (dB):
   $$\text{PSNR} = 10 \cdot \log_{10}\left(\frac{MAX_I^2}{\text{MSE}}\right) = 20 \cdot \log_{10}\left(\frac{255}{\sqrt{\text{MSE}}}\right)$$
   * **Interpretasi Hasil:** Standar kualitas citra digital menyatakan nilai $\text{PSNR} > 40\text{ dB}$ tidak dapat dibedakan oleh mata manusia (*imperceptible*). Hasil uji modul Sentix Vault mencapai **$\text{PSNR} > 65\text{ dB}$**, membuktikan bahwa penyisipan pesan tidak merusak estetika visual citra asli.

---

### 5.6 MODUL 5: BLOCKCHAIN LEDGER ASET & DETEKSI MANIPULASI

Sesuai Kriteria 7, aset penting dicatat dalam buku besar terdistribusi (*distributed ledger*) berbasis struktur rantai blok terhubung (*chained hash blocks*) dengan mekanisme konsensus *Proof-of-Work (PoW)*.

* **Rujukan Silabus:** Materi 8 (Fungsi Hash Satu-Arah, Avalanche Effect, & Integritas Data)
* **Struktur Data Blok (Block Schema):**
  Setiap blok dalam rantai dibentuk oleh komponen berikut:
  ```json
  {
    "index": 1,
    "timestamp": 1730700000.12,
    "transactions": [
      {
        "tx_id": "TX-001",
        "asset_name": "BTC Cold Reserve #1",
        "sender": "TREASURY_RESERVE_ALPHA",
        "recipient": "OFFICER_OKTAVIAN",
        "amount": 50.0,
        "signature": "SHA256_SIG_7F8A..."
      }
    ],
    "previous_hash": "0000a1b2c3d4...",
    "nonce": 42189,
    "hash": "0000e5f6a7b8..."
  }
  ```

#### Mekanisme Konsensus Proof-of-Work (PoW)
Untuk menerbitkan blok baru ke dalam buku besar, penambang (*miner*) harus menyelesaikan teka-teki kriptografi dengan mencari nilai pencacah (*nonce*) integer tak negatif sedemikian rupa sehingga hash SHA-256 dari seluruh isi blok diawali dengan sejumlah angka nol tertentu (*difficulty target*):
$$\text{SHA-256}\Big(\text{BlockData} \parallel \text{Nonce}\Big) < \text{Target}$$
Pada Sentix Vault, tingkat kesulitan ditetapkan pada nilai $\text{Difficulty} = 4$ (prefix `"0000"`).

#### Deteksi Manipulasi Rantai Otomatis (Tamper Detection Engine)
Sistem memiliki algoritma audit integritas rekursif yang memverifikasi dua kondisi mutlak pada seluruh rantai:
1. Validitas hash internal: $\text{CalculateHash}(B_i) == B_i.\text{hash}$
2. Kontinuitas rantai: $B_i.\text{previous\_hash} == B_{i-1}.\text{hash}$

Jika penyerang menyusup ke basis data lokal dan memanipulasi nominal transaksi pada blok masa lalu (misal mengubah $50\text{ BTC} \to 500\text{ BTC}$), hash blok tersebut seketika berubah secara drastis akibat efek longsoran hash (*Avalanche Effect*). Seluruh mata rantai berikutnya menjadi tidak valid, dan dashboard Sentix Vault seketika membunyikan status **TAMPER DETECTED / BLOCKCHAIN FORGERY ALERT**.

---

## 6. HASIL PENGUJIAN OTOMATIS & BENCHMARK EMPIRIS

Pengujian perangkat lunak dilakukan menggunakan kerangka kerja `unittest` Python melalui berkas `tests/test_crypto_engines.py` yang mengeksekusi 9 skenario end-to-end.

```bash
$ python tests/test_crypto_engines.py
.........
----------------------------------------------------------------------
Ran 9 tests in 1.864s

OK
```

### Tabel Rincian Hasil Pengujian Unit

| No | Nama Unit Test | Komponen yang Diuji | Hasil Uji | Keterangan Verifikasi |
| :---: | :--- | :--- | :---: | :--- |
| **1** | `test_01_dongle_generation_and_verification` | Faktor 1: USB Dongle HMAC-SHA256 | **PASS** | Validasi tanda tangan otentik vs penolakan dongle manipulasi (*tampered token*). |
| **2** | `test_02_biometric_face_matching` | Faktor 2: Multi-Face Cosine Distance | **PASS** | Citra identik menghasilkan jarak $D_C \le 0.32$, citra probe asing ditolak ($D_C > 0.32$). |
| **3** | `test_03_password_hash_and_key_derivation` | Faktor 3: PBKDF2-HMAC-SHA256 | **PASS** | 100.000 iterasi hash cocok, garam 16-byte unik, derivasi kunci 256-bit sukses. |
| **4** | `test_04_super_encryption_roundtrip` | Super-Enkripsi 2-Tahap (Vig + AES) | **PASS** | Dekripsi menghasilkan plainteks identik 100% (*lossless roundtrip*). |
| **5** | `test_04b_4stage_super_encryption_roundtrip` | Super-Enkripsi 4-Tahap Kelompok 3 | **PASS** | Caesar $\to$ Vigenère $\to$ Vernam $\to$ AES-128 berhasil dienkripsi dan dibalikkan sempurna. |
| **6** | `test_05_file_rc4_roundtrip` | Modul File Vault (Stream RC4) | **PASS** | Enkripsi berkas biner sembarang berhasil diekstrak kembali beserta nama aslinya. |
| **7** | `test_06_database_gcm_encryption` | Database Vault (AES-256-GCM) | **PASS** | Field tersimpan dalam raw ciphertext di SQLite; dekripsi RAM menghasilkan teks asli. |
| **8** | `test_07_steganography_lsb_roundtrip` | Steganografi LSB Citra RGB | **PASS** | Pesan berhasil diekstraksi; metrik $\text{PSNR} > 50\text{ dB}$ terpenuhi ($\approx 68.4\text{ dB}$). |
| **9** | `test_08_blockchain_mining_and_tamper_detection` | Blockchain PoW & Tamper Detection | **PASS** | Penambangan blok 4-nol sukses; mutasi transaksi liar berhasil dideteksi seketika. |

---

## 7. STRUKTUR BERKAS PROYEK & PANDUAN PENGEMBANGAN

Berikut adalah struktur direktori lengkap repositori **Sentix Digital Vault**:

```text
sentix-digital-vault/
├── README.md               # Ringkasan cepat & panduan instalasi
├── UI_GUIDE.md             # Panduan frontend Streamlit untuk kolaborasi tim
├── LAPORAN_PROYEK_KRIPTOGRAFI.md # Laporan teknis lengkap & matematis proyek
├── requirements.txt        # Spesifikasi pustaka eksternal (Pillow, NumPy, cryptography, streamlit)
├── .gitignore              # Konfigurasi filter berkas repositori
├── config.py               # Konstanta path data, parameter hash, dan threshold
├── app.py                  # Entry point aplikasi antarmuka web Streamlit
│
├── core/                   # Modul mesin kriptografi inti
│   ├── __init__.py
│   ├── auth_3fa.py         # Mesin 3FA: Dongle USB, Biometrik Multi-Wajah, & PBKDF2
│   ├── super_encryption.py # Mesin Super-Enkripsi: Caesar, Vigenère, Vernam, AES-128/256
│   ├── file_cipher.py      # Mesin File Vault: Stream Cipher RC4 (KSA & PRGA)
│   ├── database_vault.py   # Mesin Basis Data: SQLite dengan AEAD AES-256-GCM
│   ├── steganography.py    # Mesin Steganografi: Domain Spasial LSB Citra & Metrik PSNR/MSE
│   └── blockchain.py       # Mesin Buku Besar: Rantai Blok PoW & Deteksi Manipulasi
│
├── tests/                  # Pengujian unit otomatis
│   ├── __init__.py
│   └── test_crypto_engines.py # 9 prosedur uji otomatis seluruh modul
│
├── scripts/                # Perkakas CLI administratif
│   ├── generate_dongle.py  # Skrip penciptaan kunci fisik USB Dongle bertanda tangan
│   └── enroll_face.py      # Skrip pendaftaran biometrik citra master wajah
│
└── data/                   # Media penyimpanan terisolasi
    ├── auth_config.json    # Konfigurasi hash password & garam kriptografis
    ├── master_face.json    # Basis data vektor biometrik multi-petugas
    ├── sentix_vault.db     # Basis data relasional SQLite terenkripsi
    └── blockchain_ledger.json # Buku besar transaksi aset digital
```

---

## 8. PANDUAN REPRODUKSI & DEMONSTRASI SIDANG (DEVELOPER SANDBOX)

Untuk memfasilitasi evaluasi akademis oleh dosen penguji di ruang sidang, aplikasi Sentix Digital Vault dilengkapi dengan **Developer Sandbox & Evaluation Tools** yang dapat diakses langsung pada halaman antarmuka.

### 8.1 Cara Menjalankan Aplikasi
1. Buka terminal dan aktifkan lingkungan virtual Python:
   ```bash
   cd sentix-digital-vault
   source venv/bin/activate   # Di Linux / macOS
   # .\venv\Scripts\Activate.ps1 # Di Windows PowerShell
   ```
2. Jalankan aplikasi Streamlit:
   ```bash
   streamlit run app.py
   ```
3. Buka peramban (*web browser*) pada URL: `http://localhost:8501`.

### 8.2 Fitur Pembuktian di Hadapan Dosen Penguji
1. **1-Click Fast Bypass Demo:** Memungkinkan penguji untuk melewati pemindaian fisik 3FA secara instan guna langsung menguji modul kriptografi inti (Tab 1–5) tanpa kendala hardware webcam laptop.
2. **Matriks 7 Kriteria Otomatis:** Menampilkan tabel pemenuhan seluruh kriteria tugas akhir langsung dari antarmuka aplikasi.
3. **Inspektur Basis Data Fisik (*Raw SQLite Inspector*):** Memperlihatkan bahwa berkas fisik `sentix_vault.db` benar-benar menyimpan record dalam format biner teracak (*ciphertext, nonce, auth_tag*), membuktikan bahwa data tidak disimpan dalam teks polos (*plaintext*).
4. **Simulasi Kerusakan Blockchain (*Tamper Simulation*):** Tombol interaktif untuk mengubah isi nominal koin pada blok lama dan mendemonstrasikan kegagalan validasi hash secara seketika (*red alert banner*).

---

## 9. KESIMPULAN

Proyek tugas akhir **Sentix Digital Vault** berhasil merealisasikan sistem manajemen aset digital berkeamanan tinggi yang memenuhi seluruh 7 butir kriteria evaluasi mata kuliah Kriptografi. Integrasi algoritma klasik (Caesar dan Vigenère) dengan algoritma modern (Vernam Stream, RC4, AES-128/256 CBC, AES-256-GCM, PBKDF2-HMAC-SHA256, LSB Steganography, dan Blockchain PoW) membuktikan bahwa prinsip-prinsip kriptografi fundamental tetap menjadi fondasi utama dalam perancangan arsitektur keamanan informasi modern.

Sistem ini tidak hanya berhasil secara teoritis matematis, namun juga terbukti andal, teruji secara otomatis (*100% test suite pass*), efisien pada perangkat keras standar tanpa ketergantungan kartu grafis eksternal, dan siap dipertanggungjawabkan dalam sidang akademik.

---

## 10. DAFTAR PUSTAKA & RUJUKAN SILABUS

1. Tim Dosen Kriptografi UPN "Veteran" Yogyakarta. (2026). *Bahan Ajar Kriptografi: Materi 1 s/d Materi 9*. Program Studi Informatika, UPN Veteran Yogyakarta.
2. Barker, E. (2020). *Recommendation for Key Management: Part 1 – General (NIST Special Publication 800-57 Part 1 Rev. 5)*. National Institute of Standards and Technology.
3. Grassi, P. A., et al. (2017). *Digital Identity Guidelines: Authentication and Lifecycle Management (NIST Special Publication 800-63B)*. National Institute of Standards and Technology.
4. Dworkin, M. (2007). *Recommendation for Block Cipher Modes of Operation: Galois/Counter Mode (GCM) and GMAC (NIST Special Publication 800-38D)*. National Institute of Standards and Technology.
5. Kaliski, B. (2000). *PKCS #5: Password-Based Cryptography Specification Version 2.0 (RFC 2898)*. Internet Engineering Task Force (IETF).
6. Menezes, A. J., van Oorschot, P. C., & Vanstone, S. A. (1996). *Handbook of Applied Cryptography*. CRC Press.
7. Stallings, W. (2017). *Cryptography and Network Security: Principles and Practice (7th Edition)*. Pearson.

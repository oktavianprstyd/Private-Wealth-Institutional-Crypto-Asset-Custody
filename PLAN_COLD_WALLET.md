# PLAN IMPLEMENTASI: AEGIS COLD CUSTODY (AIR-GAPPED SEED VAULT)
## Reposisi Proyek Tugas Akhir Kriptografi — Tim Oktavian & Grace

---

## 1. Executive Summary & Brand Repositioning

* **Topik Resmi:** *Aegis Air-Gapped Cold Wallet & Cryptographic Seed Custody Workstation*
* **Diferensiasi Terhadap Kelompok Adhafa & Mirwan:**
  * **Adhafa & Mirwan:** *General Enterprise Document & Secret Vault* (Brankas file/password generik kantoran).
  * **Oktavian & Grace:** *Web3 Air-Gapped Cold Wallet & Private Key Custody* (Perangkat lunak penandatangan transaksi offline khusus BIP-39 Mnemonic Seed Phrase, Keystore Wallet, dan On-Chain Transaction Ledger).
* **Target Repositori:** `/root/sentix-digital-vault` (direfaktor menjadi arsitektur Aegis Cold Wallet).

---

## 2. Pemetaan Konkret 7 Kriteria Dosen ke Fitur Cold Wallet

```text
┌────┬───────────────────────────────────────┬────────────────────────────────────────────────────────┐
│ No │ 7 Kriteria Dosen                      │ Fitur Implementasi di Aegis Cold Wallet                │
├────┼───────────────────────────────────────┼────────────────────────────────────────────────────────┤
│ 1  │ Login Biometrik & USB Dongle Wajib    │ Air-Gapped HSM Gatekeeper:                             │
│    │                                       │ - USB Physical Hardware Key (HMAC-SHA256 signature)    │
│    │                                       │ - Biometrik Wajah 128-D Cosine (Screen Flash Blitz 2s) │
├────┼───────────────────────────────────────┼────────────────────────────────────────────────────────┤
│ 2  │ Login Memakai Algoritma Kriptografi   │ BIP-39 Key Derivation Function:                        │
│    │                                       │ - PBKDF2-HMAC-SHA256 (100.000 iterasi + 16-byte salt)  │
│    │                                       │   untuk menurunkan Master Encryption Key dari PIN      │
├────┼───────────────────────────────────────┼────────────────────────────────────────────────────────┤
│ 3  │ Pesan Teks Dienkripsi Super Enkripsi  │ Mnemonic Seed Phrase Armor:                            │
│    │ (Klasik + Modern)                     │ - 12/24 Kata Pemulihan Dompet disandi 4 lapis:         │
│    │                                       │   Caesar -> Vigenere -> Vernam XOR -> AES-128 CBC      │
├────┼───────────────────────────────────────┼────────────────────────────────────────────────────────┤
│ 4  │ Pesan File Dienkripsi Algoritma Beda  │ Keystore File Encryptor (.json / .dat):                │
│    │ dari Teks                             │ - Enkripsi berkas biner private key menggunakan        │
│    │                                       │   RC4 Stream Cipher (KSA 256-byte + PRGA)              │
├────┼───────────────────────────────────────┼────────────────────────────────────────────────────────┤
│ 5  │ Pesan Penting Dienkripsi pada DB      │ Whitelisted Address Book & UTXO Database:              │
│    │                                       │ - Tabel kontak & mutasi saldo di SQLite dienkripsi     │
│    │                                       │   Field-Level via Authenticated AES-256-GCM AEAD       │
├────┼───────────────────────────────────────┼────────────────────────────────────────────────────────┤
│ 6  │ Pesan Gambar Menggunakan Steganografi │ Stego Paper Wallet & NFT Camouflage:                   │
│    │                                       │ - Menyisipkan seed phrase ke dalam citra avatar NFT    │
│    │                                       │   lewat LSB Spasial (Evaluasi PSNR > 65 dB & MSE)      │
├────┼───────────────────────────────────────┼────────────────────────────────────────────────────────┤
│ 7  │ Aset Penting Diamankan Blockchain     │ Native On-Chain Transaction Ledger:                    │
│    │                                       │ - Rantai blok transaksi SHA-256 Proof-of-Work (PoW)    │
│    │                                       │ - Panel interaktif simulasi tamper manipulasi saldo    │
└────┴───────────────────────────────────────┴────────────────────────────────────────────────────────┘
```

---

## 3. Pembagian Tanggung Jawab Anggota (Role Breakdown)

### A. Grace Rianty Butar Butar (NIM: 123240036) — *Frontend & Classical Crypto Engineer*
1. **Frontend Input & Mnemonic Generator:**
   * Antarmuka input 12 kata BIP-39 Seed Phrase di Streamlit.
   * Visualisasi status keabsahan checksum kata pemulihan dompet.
2. **Mesin Kriptografi Klasik (Tahap 1 & 2):**
   * **Caesar Cipher:** Pergeseran nilai alfabet monoalfabetik pada blok kata seed phrase ($C_i = (P_i + k) \pmod{26}$).
   * **Vigenère Cipher:** Substitusi polialfabetik berbasis passphrase dompet ($C_i = (P_i + K_i) \pmod{26}$ dan mode ASCII 95-karakter).
   * Visualisasi tabel bujursangkar Vigenère (*Tabula Recta*) pada antarmuka.
3. **Dokumentasi & Laporan Bab Transformasi Klasik:**
   * Penyusunan tabel tracing contoh perhitungan matematis manual enkripsi/dekripsi kalimat seed phrase.

### B. Oktavian Prasetya Adi (NIM: 123240135) — *Security Architecture & Modern Crypto Engineer*
1. **Air-Gapped 3FA Gatekeeper:**
   * Implementasi verifikasi USB Physical Dongle (HMAC-SHA256 signature matching).
   * Engine biometrik multi-wajah berbasis NumPy 128-D Cosine Distance dengan mekanisme *Synchronized Screen Flash 2 Detik*.
   * Derivasi Master Session Key via PBKDF2-HMAC-SHA256 (100.000 iterasi).
2. **Mesin Kriptografi Modern (Tahap 3, 4, & Pendukung):**
   * **Vernam Stream Cipher (Tahap 3):** Operasi bitwise XOR aliran bit data terhadap keystream acak.
   * **AES-128-CBC (Tahap 4):** Cipher blok modern dengan PKCS7 padding untuk mengunci akhir seed phrase.
   * **RC4 File Engine:** Enkripsi/dekripsi biner keystore dompet kripto menggunakan permutasi KSA dan PRGA.
   * **SQLite AES-256-GCM AEAD:** Proteksi database address book dengan verifikasi 128-bit authentication tag.
   * **LSB Steganography Engine:** Penyisipan bit ke kanal citra dan kalkulasi otomatis rasio PSNR/MSE.
   * **Proof-of-Work Blockchain Engine:** Validasi rantai blok SHA-256 dan deteksi tamper manipulasi riwayat koin.
3. **Automated Testing & Integration:**
   * Memastikan seluruh 9 skenario unit tests tetap berstatus PASS 100%.

---

## 4. Rencana Kerja Refaktor Teknis (Execution Roadmap)

### Fase 1: Perubahan Salinan UI & Nomenklatur Aplikasi (`app.py`)
* **Ubah Judul & Branding:**
  * Ubah `Sentix Digital Vault` $\to$ `Aegis Cold Custody | Air-Gapped Mnemonic & Seed Vault`.
  * Ubah ikon gembok biasa menjadi perisai/hardware security dongle 🛡️ 🗝️.
* **Sesuaikan Copywriting Tiap Tab:**
  * **Tab 1:** Dari "Super-Enkripsi Teks Umum" $\to$ "BIP-39 Mnemonic Seed Phrase Armor" (placeholder contoh: `witch collapse practice feed shame open despair creek road again ice cheese`).
  * **Tab 2:** Dari "File Vault" $\to$ "Keystore / Private Key Backup Vault (.json, .dat, .key)".
  * **Tab 3:** Dari "Steganografi Umum" $\to$ "Stego Paper Wallet / NFT Camouflage".
  * **Tab 4:** Dari "Database Vault" $\to$ "Whitelisted Wallet Address Book & UTXO Store".
  * **Tab 5:** Dari "Blockchain Ledger" $\to$ "Cold Wallet On-Chain Transaction & Balance Ledger".
* **Pertahankan Fitur Unggulan:**
  * *1-Click Fast Demo Bypass* tetap dipertahankan untuk kemudahan dosen penguji.
  * *Screen Flash 2 Detik* tetap aktif pada tab autentikasi biometrik.

### Fase 2: Sinkronisasi Skrip CLI & Data Mock
* Update `scripts/generate_dongle.py` agar metadata dongle mencantumkan label `AEGIS-COLD-KEY-HSM`.
* Update data mock awal di SQLite agar berisi sample alamat kripto dummy (misal format `0x71C...` atau `bc1q...`).

### Fase 3: Pembaruan Dokumen Laporan Teknis (`LAPORAN_PROYEK_KRIPTOGRAFI.md`)
* Ganti judul dokumen menjadi:  
  **LAPORAN TEKNIS TUGAS AKHIR KRIPTOGRAFI: AEGIS COLD CUSTODY — AIR-GAPPED CRYPTOGRAPHIC SEED VAULT & HARDWARE KEY CUSTODIAN**.
* Perbarui susunan tim pengembang menjadi formasi 2 orang: **Grace Rianty Butar Butar & Oktavian Prasetya Adi**.
* Sesuaikan Bab Latar Belakang ke skenario kehilangan dana kripto akibat kebocoran seed phrase dan serangan malware clipboard.
* Perbarui diagram alir data (*dataflow diagram*) dan matriks 7 kriteria.

### Fase 4: Ekspor Dokumen Final ke PDF Standar UPN
* Kompilasi naskah markdown menjadi berkas PDF resmi:
  * Margin: 4-3-3-3 cm (Kiri 4 cm, Kanan 3 cm, Atas 3 cm, Bawah 3 cm).
  * Tipografi: Times New Roman 12pt (Judul 14pt Bold).
  * Format: Standar naskah akademik monokrom/resmi 2 kolom untuk bab isi.

---

## 5. Skenario Demonstrasi Sidang di Hadapan Dosen (5 Menit)

1. **Menit 00:00 - 01:00 (Pembukaan & Problem Statement oleh Grace):**
   * Menyampaikan bahaya menyimpan seed phrase 12 kata di komputer online.
   * Menunjukkan arsitektur *Aegis Cold Custody* yang bekerja secara offline (*air-gapped*).
2. **Menit 01:00 - 02:00 (Uji Autentikasi 3FA oleh Okta):**
   * Menunjukkan hardware key USB tertancap (HMAC-SHA256 valid).
   * Mendemonstrasikan *Synchronized Screen Flash 2 Detik* saat kamera mendeteksi wajah petugas.
   * Menjelaskan fungsi derivasi kunci PBKDF2 (100.000 iterasi).
3. **Menit 02:00 - 03:00 (Super-Enkripsi Seed Phrase oleh Grace & Okta):**
   * Input 12 kata seed phrase.
   * Menampilkan tahap demi tahap: Caesar $\to$ Vigenère $\to$ Vernam XOR $\to$ AES-128.
   * Membuktikan pembalikan dekripsi menghasilkan 12 kata yang identik 100%.
4. **Menit 03:00 - 04:00 (Stego NFT & Keystore RC4 oleh Okta):**
   * Memasukkan seed phrase ke dalam gambar avatar NFT via LSB.
   * Menampilkan metrik PSNR 68.4 dB (kualitas gambar sempurna).
   * Menunjukkan file keystore terenkripsi dengan RC4.
5. **Menit 04:00 - 05:00 (Database GCM & Simulasi Tamper Blockchain oleh Okta):**
   * Menunjukkan database SQLite yang tersimpan dalam format ciphertext AES-256-GCM.
   * Klik tombol simulasi peretasan saldo blockchain: sistem langsung memicu alarm merah (*Tamper Detected*).
   * Penutupan tegas dan siap tanya jawab.

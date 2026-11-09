@echo off
setlocal enabledelayedexpansion
title AEGIS COLD CUSTODY - Workstation Launcher
color 0B
cls
cd /d "%~dp0"

echo =====================================================================
echo              AEGIS COLD CUSTODY - CRYPTO WORKSTATION
echo       Institutional Multi-Factor Digital Asset Management
echo =====================================================================
echo.

:: 1. Verifikasi instalasi Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    color 0C
    echo [ERROR] Python tidak terdeteksi di sistem PATH!
    echo Silakan unduh dan install Python 3.10+ dari: https://www.python.org/downloads/
    echo PENTING: Centang opsi "Add Python to PATH" saat instalasi.
    echo.
    pause
    exit /b 1
)

:: Tampilkan versi Python yang terdeteksi
for /f "tokens=*" %%v in ('python --version 2^>^&1') do set PYTHON_VER=%%v
echo [OK] Python terdeteksi: !PYTHON_VER!

:: 2. Cek apakah ada virtual environment (venv)
if exist "venv\Scripts\activate.bat" (
    echo [INFO] Mengaktifkan virtual environment [venv]...
    call "venv\Scripts\activate.bat"
) else (
    :: Cek apakah modul utama (streamlit) sudah terpasang
    python -c "import streamlit" >nul 2>&1
    if !errorlevel% neq 0 (
        echo [INFO] Menyiapkan environment baru untuk instalasi dependensi...
        python -m venv venv >nul 2>&1
        if exist "venv\Scripts\activate.bat" (
            call "venv\Scripts\activate.bat"
            echo [INFO] Menginstal dependensi dari requirements.txt ke venv...
            python -m pip install --upgrade pip >nul 2>&1
            pip install -r requirements.txt
        ) else (
            echo [INFO] Menginstal dependensi dari requirements.txt ke environment aktif...
            pip install -r requirements.txt
        )
    )
)

:: 3. Verifikasi pustaka yang dibutuhkan dari requirements.txt
echo [INFO] Memeriksa kelengkapan pustaka (streamlit, cryptography, pillow, numpy)...
python -c "import streamlit, cryptography, PIL, numpy" >nul 2>&1
if %errorlevel% neq 0 (
    echo [WARNING] Ditemukan dependensi yang belum terinstal. Mengunduh dari requirements.txt...
    pip install -r requirements.txt
) else (
    echo [OK] Seluruh dependensi requirements.txt terverifikasi lengkap!
)

:: 4. Jalankan aplikasi Aegis Cold Custody
echo.
echo =====================================================================
echo  [SUKSES] Seluruh sistem siap! Membuka Aegis Cold Custody di browser...
echo  Local URL: http://localhost:8501
echo  Master Password Bawaan: Aegis@2026!
echo.
echo  (Tutup jendela ini atau tekan Ctrl + C untuk mematikan server)
echo =====================================================================
echo.

python -m streamlit run app.py

if %errorlevel% neq 0 (
    echo.
    echo [NOTICE] Aplikasi ditutup.
    pause
)

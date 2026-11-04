@echo off
setlocal enabledelayedexpansion
title SENTIX DIGITAL VAULT - Workstation Launcher
color 0B
cls
cd /d "%~dp0"

echo =====================================================================
echo              SENTIX DIGITAL VAULT - CRYPTO CUSTODY
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

:: Tampilkan versi Python
for /f "tokens=*" %%v in ('python --version 2^>^&1') do set PYTHON_VER=%%v
echo [OK] Menggunakan: !PYTHON_VER!

:: 2. Cek apakah ada virtual environment (venv)
if exist "venv\Scripts\activate.bat" (
    echo [INFO] Mengaktifkan virtual environment (venv)...
    call "venv\Scripts\activate.bat"
) else (
    :: Cek apakah streamlit sudah terpasang
    python -c "import streamlit" >nul 2>&1
    if !errorlevel! neq 0 (
        echo [INFO] Dependensi belum ditemukan. Menyiapkan virtual environment...
        python -m venv venv
        if exist "venv\Scripts\activate.bat" (
            call "venv\Scripts\activate.bat"
            echo [INFO] Menginstal dependensi dari requirements.txt...
            python -m pip install --upgrade pip
            pip install -r requirements.txt
        ) else (
            echo [WARNING] Tidak dapat membuat venv. Menginstal langsung ke Python global...
            pip install -r requirements.txt
        )
    )
)

:: 3. Verifikasi pustaka kriptografi
python -c "import streamlit, cryptography, PIL, numpy" >nul 2>&1
if %errorlevel% neq 0 (
    echo [INFO] Mengunduh dependensi kriptografi yang belum lengkap...
    pip install -r requirements.txt
)

:: 4. Jalankan aplikasi Sentix Vault
echo.
echo =====================================================================
echo  [SUKSES] Seluruh sistem siap! Membuka Sentix Vault di browser...
echo  Local URL: http://localhost:8501
echo  Master Password Bawaan: Sentix@2026!
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

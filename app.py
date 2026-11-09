"""Aegis Cold Custody - Air-Gapped BIP-39 Mnemonic Seed Vault & Hardware Key Custodian
Streamlit Workstation untuk Proyek Akhir Kriptografi, UPN "Veteran" Yogyakarta.

Tim Pengembang (Kelompok 3):
- Oktavian Prasetya Adi (123240135) - Arsitektur Keamanan, 3FA Gatekeeper, Cipher Modern (Vernam XOR, AES-128, RC4, PoW Blockchain, AES-256-GCM)
- Grace Rianty Butar Butar (123240036) - Antarmuka Mnemonic UX, Cipher Klasik (Caesar & Vigenère)

Alur Sistem (Centered UI Design):
1. Masuk      : Stepper 3FA (Kunci Fisik USB Dongle -> Biometrik Wajah 128-D -> PIN PBKDF2), dilengkapi bypass cepat dosen
2. Registrasi : Pendaftaran Petugas Kustodi -> Perekaman Wajah -> Unduh Kunci Dongle Hardware
3. Developer  : Matriks 7 Kriteria Dosen, Lab Pengujian Anti-Spoofing Foto HP, dan Inspektur Basis Data Mentah
4. Dashboard  : 5 Modul Cold Wallet (Mnemonic Armor, Keystore RC4, Stego Paper Wallet, PoW Ledger, Whitelist UTXO)
"""

import streamlit as st
import streamlit.components.v1 as components
import time
import json
import hashlib
from io import BytesIO
from PIL import Image

from config import DATA_DIR, DONGLE_FILENAME
from core.auth_3fa import DongleVerifier, BiometricVerifier, PasswordVerifier
from core.super_encryption import (
    super_encrypt,
    super_decrypt,
    super_encrypt_4stage,
    super_decrypt_4stage,
)
from core.file_cipher import encrypt_file_bytes, decrypt_file_bytes
from core.database_vault import (
    init_database,
    insert_secret,
    get_all_secrets_decrypted,
    get_raw_database_records,
    delete_record,
)
from core.steganography import embed_secret_message, extract_secret_message
from core.blockchain import Blockchain

# Konfigurasi Halaman: Layout Terpusat (Centered) yang Rapi & Proporsional
st.set_page_config(
    page_title="Aegis Cold Custody | Air-Gapped Seed Vault",
    page_icon="🛡️",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# =====================================================================
# STYLE: TEMA DARK MODE INSTITUSIONAL TERPUSAT (SENTIX V3 CLEAN STYLE)
# =====================================================================
st.markdown("""
<style>
    :root {
        --bg:#0B0F17; --card:#121824; --card2:#0F1520; --line:#222C3E;
        --text:#E6EAF2; --muted:#8B97AB; --accent:#3B82F6; --accent2:#2563EB;
        --ok:#34D399; --okbg:#06382B; --warn:#FBBF24; --warnbg:#3A2A08;
    }
    .stApp { background:var(--bg); color:var(--text); }

    /* Bersihkan toolbar & chrome bawaan Streamlit */
    #MainMenu, footer, [data-testid="stToolbar"], [data-testid="stDecoration"] { display:none !important; }
    [data-testid="stHeader"] { background:transparent; height:0; }

    /* Ukuran kontainer terpusat rapi (~760px) */
    .block-container { max-width:760px; padding-top:2.5rem; padding-bottom:5rem; padding-left:1.5rem; padding-right:1.5rem; }
    [data-testid="stVerticalBlock"] { gap:1.4rem; }
    [data-testid="stHorizontalBlock"] { gap:1.15rem; }
    div[data-testid="stVerticalBlockBorderWrapper"] [data-testid="stVerticalBlock"] { gap:1rem; }

    /* Iframe flash 0px agar tidak memakan ruang visual */
    [data-testid="stElementContainer"]:has(iframe[height="0"]),
    [data-testid="element-container"]:has(iframe[height="0"]) { display:none !important; }

    /* Tipografi */
    h1,h2,h3,h4 { letter-spacing:-0.02em; margin:0 !important; padding:0 !important; }
    p { margin:0; }
    .muted { color:var(--muted); font-size:.92rem; line-height:1.5; }
    .center { text-align:center; }
    .eyebrow { font-size:11px; letter-spacing:.14em; text-transform:uppercase; color:var(--accent); font-weight:700; }
    .ctitle { font-size:1.3rem; font-weight:700; margin:6px 0 6px 0; }

    /* Menu atas: rata tengah */
    .st-key-top_flow_nav,
    .st-key-top_flow_nav > div,
    .st-key-top_flow_nav [data-testid="stButtonGroup"],
    .st-key-top_flow_nav div[role="radiogroup"] {
        display:flex !important; justify-content:center !important; width:100%;
    }

    /* Pilihan aktif pada segmented control: aksen biru */
    [data-testid="stBaseButton-segmented_controlActive"] {
        background:rgba(59,130,246,.18) !important;
        border-color:#3B82F6 !important;
        color:#93C5FD !important;
    }

    /* Hero header */
    .hero { text-align:center; padding:8px 0 16px 0; }
    .hero .logo {
        width:56px; height:56px; margin:0 auto 14px auto; border-radius:16px;
        display:flex; align-items:center; justify-content:center; font-size:28px;
        background:linear-gradient(135deg,#1D4ED8,#3B82F6); box-shadow:0 8px 24px rgba(37,99,235,.35);
    }
    .hero h1 { font-size:1.85rem; font-weight:800; line-height:1.2; letter-spacing: -0.01em; }
    .hero p  { color:var(--muted); margin-top:6px; font-size:.92rem; }

    /* Kartu bertingkat */
    div[data-testid="stVerticalBlockBorderWrapper"] {
        background:var(--card); border:1px solid var(--line) !important;
        border-radius:16px !important; padding:1.25rem 1.25rem;
    }
    div[data-testid="stVerticalBlockBorderWrapper"] div[data-testid="stVerticalBlockBorderWrapper"] {
        background:var(--card2); border-radius:12px !important;
    }

    /* Tombol */
    .stButton > button, .stDownloadButton > button {
        border-radius:10px; min-height:44px; font-weight:600; transition:all .15s ease;
    }
    button[kind="primary"] { background:var(--accent2); border:0; color:#fff; }
    button[kind="primary"]:hover { background:var(--accent); }
    button[kind="secondary"] { background:#182131; border:1px solid var(--line); color:var(--text); }
    button[kind="secondary"]:hover { border-color:var(--accent); color:#fff; }

    /* Input text & select */
    div[data-baseweb="input"], div[data-baseweb="textarea"], div[data-baseweb="select"] > div {
        background:var(--card2) !important; border-radius:10px !important;
    }
    label p { font-size:.85rem !important; color:var(--muted) !important; }

    /* Tab bar */
    div[data-baseweb="tab-list"] { gap:6px; border-bottom:1px solid var(--line); }
    button[data-baseweb="tab"] { font-weight:600; padding:10px 14px; }

    /* Tabel */
    [data-testid="stTable"] table { width:100%; border-collapse:collapse; }
    [data-testid="stTable"] th { background:#182131; color:var(--muted); text-align:left; font-size:.8rem; text-transform:uppercase; letter-spacing:.06em; }
    [data-testid="stTable"] td, [data-testid="stTable"] th { padding:10px 12px; border-color:var(--line); }

    /* Metrik */
    [data-testid="stMetric"] { background:var(--card2); border:1px solid var(--line); border-radius:12px; padding:14px 16px; }

    /* Pill badge */
    .pill { display:inline-block; padding:4px 12px; font-size:12px; font-weight:650; border-radius:999px; }
    .pill.ok   { background:var(--okbg); color:var(--ok); border:1px solid #0B7A5A; }
    .pill.wait { background:#182131; color:var(--muted); border:1px solid var(--line); }
    .pill.warn { background:var(--warnbg); color:var(--warn); border:1px solid #8A6414; }

    /* Stepper login */
    .stepper { display:flex; align-items:center; justify-content:center; padding:10px 0 6px 0; }
    .step { display:flex; align-items:center; gap:8px; font-size:13px; font-weight:600; color:var(--muted); white-space:nowrap; }
    .step .dot {
        width:28px; height:28px; border-radius:50%; display:flex; align-items:center; justify-content:center;
        font-size:12px; background:#182131; border:1px solid var(--line);
    }
    .step.now  { color:var(--text); }
    .step.now .dot  { background:var(--accent2); border-color:var(--accent); color:#fff; box-shadow:0 0 0 4px rgba(59,130,246,.18); }
    .step.done { color:var(--text); }
    .step.done .dot { background:var(--okbg); border-color:#0B7A5A; color:var(--ok); }
    .stepper .line { flex:0 0 36px; height:2px; background:var(--line); margin:0 12px; }
    .stepper .line.done { background:#0B7A5A; }

    /* Bar dashboard */
    .brand { display:flex; align-items:center; gap:12px; }
    .brand .logo {
        width:40px; height:40px; border-radius:12px; display:flex; align-items:center; justify-content:center;
        font-size:20px; background:linear-gradient(135deg,#1D4ED8,#3B82F6);
    }
    .brand .name { font-weight:800; font-size:1.1rem; line-height:1.2; }
</style>
""", unsafe_allow_html=True)


# =====================================================================
# FLASH LAYAR UNTUK KAMERA (LIVENESS 2S ANTI-SPOOFING)
# =====================================================================
def render_flash_injector():
    components.html("""
    <script>
    (function() {
        const doc = window.parent.document;
        if (!doc) return;
        function inject() {
            doc.querySelectorAll('[data-testid="stCameraInputButton"]').forEach(function(camBtn) {
                const parent = camBtn.parentElement;
                if (!parent || parent.querySelector('.sentix-flash-btn')) return;
                const b = doc.createElement('button');
                b.className = 'sentix-flash-btn';
                b.innerHTML = '☀️ Ambil foto dengan flash layar (2s Flash Anti-Spoofing)';
                b.style.cssText = 'display:block;width:100%;margin:8px 0;padding:12px 16px;' +
                    'background:linear-gradient(135deg, #2563EB, #1D4ED8);color:#fff;border:0;border-radius:10px;' +
                    'font-weight:700;font-size:13px;cursor:pointer;box-shadow:0 4px 12px rgba(37,99,235,0.3);';
                b.addEventListener('click', function(e) {
                    e.preventDefault(); e.stopPropagation();
                    let o = doc.getElementById('sentix-flash-screen');
                    if (!o) {
                        o = doc.createElement('div');
                        o.id = 'sentix-flash-screen';
                        o.style.cssText = 'position:fixed;top:0;left:0;width:100vw;height:100vh;' +
                            'background:#ffffff;z-index:2147483647;pointer-events:none;' +
                            'display:flex;align-items:center;justify-content:center;transition:opacity .2s ease;';
                        let lbl = doc.createElement('div');
                        lbl.style.cssText = 'font-family:sans-serif;font-weight:800;font-size:24px;color:#1e293b;background:rgba(255,255,255,0.85);padding:16px 28px;border-radius:16px;box-shadow:0 10px 25px rgba(0,0,0,0.1);';
                        lbl.innerHTML = '☀️ Memindai Liveness Wajah (Flash 2s)...';
                        o.appendChild(lbl);
                        doc.body.appendChild(o);
                    }
                    o.style.opacity = '1';
                    setTimeout(function() {
                        camBtn.click();
                        setTimeout(function() {
                            o.style.opacity = '0';
                            setTimeout(function() { if (o.parentNode) o.parentNode.removeChild(o); }, 250);
                        }, 1200);
                    }, 1200);
                });
                parent.insertBefore(b, camBtn);
            });
        }
        inject();
        if (!window.__sentixFlashInterval) {
            window.__sentixFlashInterval = setInterval(inject, 350);
        }
    })();
    </script>
    """, height=0, width=0)


# =====================================================================
# SESSION STATE & HELPER
# =====================================================================
DEFAULTS = {
    "dongle_verified": False,
    "dongle_user_id": None,
    "dongle_holder_name": None,
    "biometric_verified": False,
    "authenticated_officer": "N/A",
    "password_verified": False,
    "master_session_key": None,
    "authenticated": False,
    "last_bio_result": None,
    "last_cam_hash": None,
    "last_up_hash": None,
}

for _k, _v in DEFAULTS.items():
    if _k not in st.session_state:
        st.session_state[_k] = _v
if "blockchain" not in st.session_state:
    st.session_state.blockchain = Blockchain()


def reset_auth():
    for k, v in DEFAULTS.items():
        st.session_state[k] = v


def officer_name():
    raw = st.session_state.authenticated_officer or "N/A"
    raw = raw.split("(")[0].replace("Biometrik Terverifikasi:", "").strip()
    return raw or "Petugas Kustodi"


def pill(text, kind):
    return f"<span class='pill {kind}'>{text}</span>"


def seg(options, key, label="Pilihan"):
    """Kontrol pilihan bergaya segmented (fallback ke radio di Streamlit lama)."""
    if hasattr(st, "segmented_control"):
        v = st.segmented_control(
            label, options, default=options[0], key=key, label_visibility="collapsed"
        )
        return v or options[0]
    return st.radio(label, options, horizontal=True, key=key, label_visibility="collapsed")


def card_head(eyebrow, title, desc=None):
    html = f"<div class='eyebrow'>{eyebrow}</div><div class='ctitle'>{title}</div>"
    if desc:
        html += f"<div class='muted'>{desc}</div>"
    st.markdown(html, unsafe_allow_html=True)


def page_head(title, desc=None):
    html = f"<div class='ctitle' style='font-size:1.5rem'>{title}</div>"
    if desc:
        html += f"<div class='muted'>{desc}</div>"
    st.markdown(html, unsafe_allow_html=True)


# =====================================================================
# 1. ALUR MASUK (3FA GATEKEEPER STEPPER)
# =====================================================================
def render_login_flow():
    render_flash_injector()

    d_ok = st.session_state.dongle_verified
    b_ok = st.session_state.biometric_verified
    current = 1 if not d_ok else (2 if not b_ok else 3)

    labels = ["Kunci USB", "Wajah", "PIN PBKDF2"]
    done = [d_ok, b_ok, False]
    parts = []
    for i, label in enumerate(labels, start=1):
        if done[i - 1]:
            cls, mark = "done", "✓"
        elif i == current:
            cls, mark = "now", str(i)
        else:
            cls, mark = "", str(i)
        parts.append(f"<div class='step {cls}'><span class='dot'>{mark}</span>{label}</div>")
        if i < len(labels):
            parts.append(f"<div class='line {'done' if done[i - 1] else ''}'></div>")
    st.markdown(f"<div class='stepper'>{''.join(parts)}</div>", unsafe_allow_html=True)

    # ---------- Langkah 1: Kunci USB Dongle ----------
    if current == 1:
        with st.container(border=True):
            card_head("Langkah 1 dari 3", "Kunci Fisik USB Dongle", "Verifikasi token kriptografis HMAC-SHA256 pada flashdisk hardware.")

            scanned = DongleVerifier.scan_possible_dongle_locations()
            dongle_choice = None
            if scanned:
                dongle_choice = st.selectbox(
                    "Token terdeteksi pada drive:",
                    scanned,
                    format_func=lambda p: f"{p.drive}\\ (Drive Removable) - {p.name}",
                    key="sel_dongle_path",
                )

            uploaded = st.file_uploader(
                "Atau telusuri file kunci manual (.key / .json):",
                type=["key", "json"],
                key="up_dongle_file",
            )

            if st.button("Verifikasi Kunci USB", use_container_width=True, type="primary", key="btn_verify_dongle"):
                raw_bytes = None
                if uploaded is not None:
                    raw_bytes = uploaded.read()
                elif dongle_choice is not None:
                    try:
                        raw_bytes = dongle_choice.read_bytes()
                    except Exception as e:
                        st.error(f"Gagal membaca drive: {e}")

                if raw_bytes is None:
                    st.error("Colokkan flashdisk berisi file kunci atau unggah file kunci manual.")
                else:
                    ok, msg, payload = DongleVerifier.verify_dongle_token(raw_bytes)
                    if ok:
                        uid = DongleVerifier.resolve_user_id_from_payload(payload)
                        holder = (payload or {}).get("issued_to", "Petugas Terotorisasi")
                        st.session_state.dongle_verified = True
                        st.session_state.dongle_user_id = uid
                        st.session_state.dongle_holder_name = holder
                        st.session_state.authenticated_officer = holder
                        st.rerun()
                    else:
                        st.error(f"Kunci tidak valid: {msg}")

        with st.container(border=True):
            card_head("Pengujian Cepat", "Bypass Evaluasi Dosen", "Gunakan opsi ini jika ingin langsung melihat seluruh modul cold wallet.")
            if st.button("Masuk Langsung (Mode Evaluasi)", use_container_width=True, key="btn_skip_step1"):
                st.session_state.dongle_verified = True
                st.session_state.dongle_user_id = "oktavian"
                st.session_state.dongle_holder_name = "Oktavian Prasetya Adi (123240135)"
                st.session_state.biometric_verified = True
                st.session_state.password_verified = True
                st.session_state.authenticated_officer = "Oktavian Prasetya Adi (123240135)"
                st.session_state.master_session_key = hashlib.sha256(b"AegisMasterSessionKey2026").hexdigest()
                st.session_state.authenticated = True
                st.rerun()

    # ---------- Langkah 2: Biometrik Wajah 128-D ----------
    elif current == 2:
        target_uid = st.session_state.get("dongle_user_id")
        target_holder = st.session_state.get("dongle_holder_name") or "Petugas Terotorisasi"

        with st.container(border=True):
            card_head(
                "Langkah 2 dari 3",
                "Biometrik Wajah 128-D",
                f"Kunci USB terikat pada: <b style='color:#E6EAF2'>{target_holder}</b>. Wajah di depan kamera wajib cocok dengan pemilik kunci.",
            )

            cam = st.camera_input("Kamera Biometrik", key="cam_login_input", label_visibility="collapsed")
            if cam is not None:
                img_bytes = cam.getvalue()
                h = hashlib.sha256(img_bytes).hexdigest()
                if st.session_state.last_cam_hash != h:
                    st.session_state.last_cam_hash = h
                    img_input = Image.open(cam)
                    ok, dist, msg = BiometricVerifier.verify_face(
                        img_input, check_liveness=True, expected_user_id=target_uid
                    )
                    liv_data = BiometricVerifier.analyze_liveness(img_input)
                    st.session_state.biometric_verified = ok
                    st.session_state.authenticated_officer = msg
                    st.session_state.last_bio_result = {
                        "ok": ok, "dist": dist, "msg": msg, "liv": liv_data, "source": "cam"
                    }
                    if ok:
                        st.rerun()

            with st.expander("Atau unggah foto (Mode Pengujian Lab)"):
                up_face = st.file_uploader("Pilih file foto wajah", type=["jpg", "jpeg", "png"], key="up_face_login")
                if up_face is not None:
                    u_bytes = up_face.getvalue()
                    uh = hashlib.sha256(u_bytes).hexdigest()
                    if st.session_state.last_up_hash != uh:
                        st.session_state.last_up_hash = uh
                        img_up = Image.open(up_face)
                        ok, dist, msg = BiometricVerifier.verify_face(
                            img_up, check_liveness=True, expected_user_id=target_uid
                        )
                        liv_data = BiometricVerifier.analyze_liveness(img_up)
                        st.session_state.biometric_verified = ok
                        st.session_state.authenticated_officer = msg
                        st.session_state.last_bio_result = {
                            "ok": ok, "dist": dist, "msg": msg, "liv": liv_data, "source": "upload"
                        }
                        if ok:
                            st.rerun()

            res = st.session_state.last_bio_result
            if res:
                if res["ok"]:
                    st.success(f"{res['msg']} (Cosine dist: {res['dist']:.4f})")
                else:
                    st.error(res["msg"])

                with st.expander("Telemetri Evaluasi Anti-Spoofing (Liveness)", expanded=not res["ok"]):
                    liv = res.get("liv", {})
                    st.markdown(f"**Status Liveness:** `{'Lolos (LIVE)' if liv.get('is_live') else 'Ditolak (SPOOF / SCREEN DETECTED)'}`")
                    st.markdown(f"**Liveness Score:** `{liv.get('liveness_score', 0)}%` (Ambang batas minimum: 50%)")
                    st.markdown(f"**Rasio Pigmen Kulit:** `{liv.get('skin_ratio', 0)}%` (YCbCr)")
                    st.markdown(f"**Kontras & Pantulan Layar:** `{liv.get('contrast', 0)}`")
                    st.markdown(f"**Alasan Evaluasi:** *{liv.get('reason', '-')}*")

        c1, c2 = st.columns(2)
        with c1:
            if st.button("← Ganti Kunci USB", use_container_width=True, key="btn_rst_dongle"):
                st.session_state.dongle_verified = False
                st.session_state.dongle_user_id = None
                st.session_state.dongle_holder_name = None
                st.rerun()
        with c2:
            if st.button("Bypass Langkah Biometrik", use_container_width=True, key="btn_skip_step2"):
                st.session_state.biometric_verified = True
                st.session_state.authenticated_officer = st.session_state.get("dongle_holder_name") or "Oktavian Prasetya Adi (123240135)"
                st.rerun()

    # ---------- Langkah 3: Password / PIN PBKDF2 ----------
    else:
        target_uid = st.session_state.get("dongle_user_id")
        target_holder = st.session_state.get("dongle_holder_name") or officer_name()

        with st.container(border=True):
            card_head("Langkah 3 dari 3", "Master Passphrase / PIN", f"Masukkan passphrase untuk petugas: <b style='color:#E6EAF2'>{target_holder}</b>")
            st.markdown(
                f"<div class='muted'>Petugas Terverifikasi: <b style='color:#E6EAF2'>{target_holder}</b></div>",
                unsafe_allow_html=True,
            )
            pwd = st.text_input("Master Passphrase / PIN Kustodi", type="password", key="master_pwd_input")
            if st.button("Buka Workstation Cold Custody", use_container_width=True, type="primary", key="btn_unlock_vault"):
                ok, msg, master_key = PasswordVerifier.verify_password(pwd, username=target_uid)
                if ok:
                    st.session_state.password_verified = True
                    st.session_state.master_session_key = master_key
                    st.session_state.authenticated = True
                    st.rerun()
                else:
                    st.error(f"Autentikasi Gagal: {msg}")

        c1, c2 = st.columns(2)
        with c1:
            if st.button("← Ulangi Verifikasi Wajah", use_container_width=True, key="btn_rst_biometric"):
                st.session_state.biometric_verified = False
                st.session_state.authenticated_officer = "N/A"
                st.session_state.last_bio_result = None
                st.session_state.last_cam_hash = None
                st.session_state.last_up_hash = None
                st.rerun()
        with c2:
            if st.button("Mulai dari Awal", use_container_width=True, key="btn_rst_all"):
                reset_auth()
                st.rerun()


# =====================================================================
# 2. ALUR REGISTRASI PETUGAS KUSTODI
# =====================================================================
def render_registration_flow():
    render_flash_injector()

    with st.container(border=True):
        card_head("Langkah 1 dari 3", "Data Petugas Kustodi")
        c1, c2 = st.columns(2)
        with c1:
            reg_name = st.text_input("Nama Lengkap Petugas", key="reg_name_input")
        with c2:
            reg_uid = st.text_input("User ID Kustodi (tanpa spasi)", key="reg_uid_input")
        c3, c4 = st.columns(2)
        with c3:
            reg_pwd1 = st.text_input("Master Passphrase", type="password", key="reg_pwd1_input")
        with c4:
            reg_pwd2 = st.text_input("Ulangi Passphrase", type="password", key="reg_pwd2_input")

    with st.container(border=True):
        card_head("Langkah 2 dari 3", "Perekaman Wajah Biometrik", "Posisikan wajah di depan kamera dan ambil foto.")
        reg_cam_file = st.camera_input("Kamera Perekaman", key="reg_cam_input", label_visibility="collapsed")
        reg_up_file = None
        with st.expander("Atau unggah foto wajah"):
            reg_up_file = st.file_uploader("File foto wajah", type=["jpg", "jpeg", "png"], key="reg_up_input")

    face_source = None
    if reg_cam_file is not None:
        face_source = Image.open(reg_cam_file)
    elif reg_up_file is not None:
        face_source = Image.open(reg_up_file)

    with st.container(border=True):
        card_head("Langkah 3 dari 3", "Penerbitan Hardware Token Kunci USB")
        if face_source is None:
            st.markdown(pill("Foto wajah belum direkam", "warn"), unsafe_allow_html=True)
        else:
            st.markdown(pill("Foto wajah siap diproses", "ok"), unsafe_allow_html=True)

        if st.button("Daftarkan Petugas & Terbitkan Kunci USB", use_container_width=True, type="primary", key="btn_execute_registration"):
            if not reg_name or not reg_uid:
                st.error("Nama dan User ID wajib diisi.")
            elif " " in reg_uid:
                st.error("User ID tidak boleh mengandung spasi.")
            elif not reg_pwd1 or reg_pwd1 != reg_pwd2:
                st.error("Password kosong atau tidak cocok.")
            elif face_source is None:
                st.error("Ambil atau unggah foto wajah terlebih dahulu.")
            else:
                try:
                    BiometricVerifier.enroll_face(face_source, user_id=reg_uid, name=reg_name)
                    PasswordVerifier.register_account(reg_uid, reg_name, reg_pwd1)
                    token = DongleVerifier.generate_dongle_token(
                        vault_id=f"AEGIS-{reg_uid.upper()}", holder_name=reg_name, user_id=reg_uid
                    )
                    st.session_state.latest_registered_dongle = json.dumps(token, indent=2).encode("utf-8")
                    st.session_state.registration_success_info = f"Petugas {reg_name} ({reg_uid}) berhasil didaftarkan."
                    st.rerun()
                except Exception as e:
                    st.error(f"Pendaftaran gagal: {e}")

        if st.session_state.get("registration_success_info"):
            st.success(st.session_state["registration_success_info"])
            st.download_button(
                f"Unduh Kunci USB Hardware ({DONGLE_FILENAME})",
                data=st.session_state.get("latest_registered_dongle", b""),
                file_name=DONGLE_FILENAME,
                mime="application/json",
                use_container_width=True,
                key="btn_download_new_dongle",
            )
            st.caption("Pindahkan file ini ke flashdisk USB Anda, lalu gunakan menu Masuk.")


# =====================================================================
# 3. ALUR PENGEMBANG & EVALUASI DOSEN
# =====================================================================
def render_developer_flow():
    t1, t2, t3 = st.tabs(["Alat Uji & Lab Liveness", "Matriks 7 Kriteria Dosen", "Basis Data Fisik Disk"])

    with t1:
        with st.container(border=True):
            card_head("Pintasan Pengujian", "1-Click Fast Demo Bypass", "Masuk langsung ke dashboard cold custody tanpa melewati perangkat keras.")
            if st.button("Masuk Langsung ke Dashboard", use_container_width=True, type="primary", key="dev_fast_bypass"):
                st.session_state.dongle_verified = True
                st.session_state.biometric_verified = True
                st.session_state.password_verified = True
                st.session_state.authenticated_officer = "Oktavian Prasetya Adi (123240135)"
                st.session_state.master_session_key = hashlib.sha256(b"AegisMasterSessionKey2026").hexdigest()
                st.session_state.authenticated = True
                st.rerun()
            if st.button("Reset Semua Sesi Aktif", use_container_width=True, key="dev_full_reset"):
                reset_auth()
                st.rerun()

        with st.container(border=True):
            card_head("Kunci USB Hardware", "Penerbitan Token Dongle (Zero-Raw Storage)", "Unduh token kriptografis HMAC-SHA256 langsung ke flashdisk USB fisik Anda. Sistem menerapkan Zero-Raw Storage sehingga tidak pernah menyimpan file kunci mentah di folder data/ laptop.")
            sample_token = DongleVerifier.generate_dongle_token(
                vault_id="AEGIS-HSM-DEMO", holder_name="Oktavian Prasetya Adi (123240135)"
            )
            st.download_button(
                f"Unduh Token Kunci USB ({DONGLE_FILENAME})",
                data=json.dumps(sample_token, indent=2).encode("utf-8"),
                file_name=DONGLE_FILENAME,
                mime="application/json",
                use_container_width=True,
                key="btn_dev_download_dongle",
            )
            if st.button("Bersihkan Sisa File Kunci di Disk (Zero-Storage Audit)", use_container_width=True, key="btn_clean_keys"):
                cleaned = 0
                for f in DATA_DIR.glob("**/*.key"):
                    try:
                        f.unlink()
                        cleaned += 1
                    except Exception:
                        pass
                st.success(f"Audit Keamanan: {cleaned} file kunci mentah telah dibersihkan dari disk.")

        with st.container(border=True):
            card_head("Basis Data Wajah", "Daftar Petugas Terdaftar")
            roster = BiometricVerifier.list_enrolled_faces()
            if not roster:
                st.caption("Belum ada wajah terdaftar.")
            for idx, r in enumerate(roster):
                c1, c2 = st.columns([4, 1])
                with c1:
                    st.markdown(
                        f"**{r['name']}**<br><span class='muted'>ID: `{r['user_id']}` · Terdaftar: {r['enrolled_at']}</span>",
                        unsafe_allow_html=True,
                    )
                with c2:
                    if st.button("Hapus", key=f"del_face_{r['user_id']}_{idx}", use_container_width=True):
                        BiometricVerifier.delete_face(r["user_id"])
                        st.rerun()

        with st.container(border=True):
            card_head(
                "Lab Pengujian Anti-Spoofing",
                "Uji Ketahanan Terhadap Foto Ponsel / Layar",
                "Simulasikan skenario peretas yang menemukan foto target dan mencoba menampilkannya lewat layar smartphone.",
            )
            dev_up = st.file_uploader("Unggah foto uji (simulasi serangan layar / kertas statis):", type=["jpg", "jpeg", "png"], key="dev_photo_spoof_test")
            if dev_up is not None:
                img_test = Image.open(dev_up)
                c_test1, c_test2 = st.columns([1, 2])
                with c_test1:
                    st.image(img_test, caption="Foto Uji", use_container_width=True)
                with c_test2:
                    l_res = BiometricVerifier.analyze_liveness(img_test)
                    match_ok, m_dist, m_msg = BiometricVerifier.verify_face(img_test, check_liveness=True)
                    st.markdown(f"**Status Liveness:** `{'Lolos (LIVE)' if l_res['is_live'] else 'Ditolak (SPOOF / SCREEN DETECTED)'}`")
                    st.markdown(f"**Liveness Score:** `{l_res['liveness_score']}%`")
                    st.markdown(f"**Pigmen Kulit Alami:** `{l_res['skin_ratio']}%`")
                    st.markdown(f"**Iluminasi Rata-rata:** `{l_res['mean_lux']} Lux`")
                    st.markdown(f"**Kontras & Pantulan Layar:** `{l_res['contrast']}`")
                    st.markdown(f"**Alasan Evaluasi:** *{l_res['reason']}*")
                    if match_ok:
                        st.success(f"Hasil Verifikasi Biometrik: {m_msg} (Dist: {m_dist:.4f})")
                    else:
                        st.error(f"Hasil Verifikasi Biometrik: {m_msg}")

    with t2:
        card_head("Kriteria Tugas Akhir", "Pemetaan 7 Kriteria Dosen ke Ekosistem Cold Wallet")
        st.table([
            {"No": "1", "7 Kriteria Dosen": "Login Biometrik & USB Dongle Wajib", "Implementasi Cold Custody": "Air-Gapped 3FA: USB Physical Key (HMAC-SHA256) + Wajah 128-D Cosine (Flash Blitz 2s)"},
            {"No": "2", "7 Kriteria Dosen": "Login Memakai Algoritma Kriptografi", "Implementasi Cold Custody": "BIP-39 KDF: PBKDF2-HMAC-SHA256 (100.000 iterasi + 16-byte salt)"},
            {"No": "3", "7 Kriteria Dosen": "Pesan Teks Dienkripsi Super Enkripsi", "Implementasi Cold Custody": "Mnemonic Seed Armor 4-Tahap: Caesar -> Vigenère -> Vernam -> AES-128"},
            {"No": "4", "7 Kriteria Dosen": "Pesan File Dienkripsi Algoritma Beda", "Implementasi Cold Custody": "Keystore File Encryptor: RC4 Stream Cipher (KSA 256-byte + PRGA)"},
            {"No": "5", "7 Kriteria Dosen": "Pesan Penting Dienkripsi pada DB", "Implementasi Cold Custody": "Whitelisted Address Book SQLite: Authenticated AES-256-GCM AEAD"},
            {"No": "6", "7 Kriteria Dosen": "Pesan Gambar Menggunakan Steganografi", "Implementasi Cold Custody": "Stego Paper Wallet / NFT Camouflage: Spatial LSB (Evaluasi Ilmiah PSNR > 65 dB & MSE)"},
            {"No": "7", "7 Kriteria Dosen": "Aset Penting Diamankan Blockchain", "Implementasi Cold Custody": "Cold Wallet Ledger: SHA-256 Proof-of-Work (PoW) + Panel Simulasi Tamper Mutasi Saldo"},
        ])

    with t3:
        card_head("Inspeksi Fisik Disk", "Tabel vault_records SQLite (Raw Ciphertext)", "Membuktikan bahwa data sensitif di hard drive tersimpan dalam bentuk teracak.")
        raws = get_raw_database_records()
        if raws:
            st.table(raws)
        else:
            st.info("Database masih kosong.")


# =====================================================================
# 4. DASHBOARD UTAMA COLD CUSTODY (5 TAB DOMAIN SPESIFIK)
# =====================================================================

# ----- TAB 1: MNEMONIC ARMOR (BIP-39 SUPER-ENKRIPSI 4-TAHAP) -----
def tab_mnemonic_armor():
    page_head("BIP-39 Mnemonic Seed Armor", "Super-enkripsi 4-tahap untuk melindungi 12/24 kata pemulihan dompet dari malware memory scraper.")

    c1, c2 = st.columns(2)
    with c1:
        st.caption("Skema Enkripsi")
        scheme = seg(["Pipeline 4-Tahap", "2-Tahap Ringkas"], "rad_super_scheme", "Skema")
    with c2:
        st.caption("Tindakan")
        action = seg(["Enkripsi", "Dekripsi"], "rad_msg_action", "Tindakan")

    with st.container(border=True):
        if scheme == "Pipeline 4-Tahap":
            card_head("Pipeline 4-Tahap Lengkap", "Caesar ➔ Vigenère ➔ Vernam ➔ AES-128")

            if action == "Enkripsi":
                col_btn_demo, _ = st.columns([1.5, 2])
                with col_btn_demo:
                    if st.button("Muat Contoh 12 Kata BIP-39", key="btn_load_sample_mnemonic"):
                        st.session_state.sup4_plain_in = "witch collapse practice feed shame open despair creek road again ice cheese"
                        st.rerun()

                text = st.text_area(
                    "12 Kata Pemulihan Dompet (BIP-39 Seed Phrase):",
                    st.session_state.get("sup4_plain_in", "witch collapse practice feed shame open despair creek road again ice cheese"),
                    height=90,
                    key="sup4_plain_in",
                )
            else:
                text = st.text_area("Cipherteks Armored Envelope (Base64):", "", height=90, key="sup4_cipher_in")

            ka, kb = st.columns(2)
            with ka:
                shift = st.number_input("1. Caesar Shift k:", min_value=1, max_value=25, value=8, key="k_c_shift_in")
                vig = st.text_input("2. Kunci Vigenère:", value="UPN2026", key="k_v_key_in")
            with kb:
                vern = st.text_input("3. Keystream Vernam:", value="VERNAM", key="k_vernam_in")
                aes = st.text_input("4. Kunci AES-128:", value="mysecretkey12345", key="k_aes_key_in")

            if st.button(f"{action} Seed Phrase", use_container_width=True, type="primary", key="btn_exec_4stage"):
                if not (text and vig and vern and aes):
                    st.error("Lengkapi seed phrase dan seluruh parameter kunci.")
                else:
                    try:
                        if action == "Enkripsi":
                            r = super_encrypt_4stage(text, shift, vig, vern, aes)
                            st.success("12 Kata Seed Phrase Berhasil Diamankan Lewat 4 Lapis Enkripsi!")
                            st.caption("Hasil Akhir (Base64 Armored Envelope):")
                            st.code(r["final_cipher"], language="text")
                            with st.expander("Tabel Transformasi Tahapan Kriptografi", expanded=True):
                                st.table(r["stages"])
                        else:
                            r = super_decrypt_4stage(text.strip(), shift, vig, vern, aes)
                            st.success("Seluruh 4 Tahap Dekripsi Berhasil Memulihkan Seed Phrase!")
                            st.caption("12 Kata Seed Phrase Asli:")
                            st.code(r["final_plaintext"], language="text")
                            with st.expander("Tabel Alur Rekonstruksi Dekripsi", expanded=True):
                                st.table(r["stages_dec"])
                    except Exception as e:
                        st.error(f"Operasi Gagal: {e}")

        else:
            card_head("Super-Enkripsi 2-Tahap Ringkas", "Vigenère ➔ AES-256-CBC")
            if action == "Enkripsi":
                text = st.text_area(
                    "Plainteks Kunci Privat / Seed Phrase:",
                    "0x4f3edf983ac636a65a842ce7c78d9aa706d3b113bce9c46f30d7d21715b23b1d",
                    height=90,
                    key="se_plain_input",
                )
            else:
                text = st.text_area("Cipherteks Base64:", "", height=90, key="se_cipher_input")

            ka, kb = st.columns(2)
            with ka:
                vig2 = st.text_input("Kunci Vigenère:", value="UPN2026", key="se_k_classical")
            with kb:
                aes2 = st.text_input("Passphrase AES-256:", value="AegisMasterPassphrase2026!", key="se_k_modern")

            if st.button(f"{action} 2-Tahap", use_container_width=True, type="primary", key="btn_exec_2stage"):
                if not (text and vig2 and aes2):
                    st.error("Lengkapi input teks dan seluruh kunci.")
                else:
                    try:
                        if action == "Enkripsi":
                            r = super_encrypt(text, vig2, aes2)
                            st.success("Enkripsi Dua Lapis Berhasil!")
                            st.caption("Tahap 1 - Output Vigenère:")
                            st.code(r["vigenere_output"], language="text")
                            st.caption("Tahap 2 - Output Final AES-256-CBC (Base64):")
                            st.code(r["final_ciphertext_base64"], language="text")
                            st.caption(f"IV (Hex): {r['iv_hex']}")
                        else:
                            r = super_decrypt(text.strip(), vig2, aes2)
                            st.success("Dekripsi Dua Lapis Berhasil!")
                            st.caption("Plainteks Asli:")
                            st.code(r["final_plaintext"], language="text")
                    except Exception as e:
                        st.error(f"Gagal Dekripsi: {e}")


# ----- TAB 2: KEYSTORE VAULT (RC4 STREAM CIPHER) -----
def tab_keystore_vault():
    page_head("Brankas Berkas Keystore", "Enkripsi file dompet (.json, .dat, .key, .wallet) menggunakan Stream Cipher RC4 (KSA + PRGA).")
    action = seg(["Enkripsi Berkas", "Dekripsi Berkas (.enc)"], "file_mode_radio", "Tindakan")

    with st.container(border=True):
        if action.startswith("Enkripsi"):
            up = st.file_uploader("Pilih Berkas Keystore Dompet (.json, .dat, .key, .wallet):", type=None, key="raw_file_uploader")
            pwd = st.text_input("Passphrase Kunci RC4:", "RC4ColdKeystoreProtectionKey!", key="rc4_enc_key")
            if st.button("Enkripsi Berkas via RC4", use_container_width=True, type="primary", key="btn_enc_rc4_file"):
                if not (up and pwd):
                    st.error("Pilih file keystore dan masukkan passphrase kunci RC4.")
                else:
                    data = encrypt_file_bytes(up.read(), up.name, pwd)
                    st.success(f"Berkas keystore berhasil dienkripsi! Ukuran: {len(data)} bytes.")
                    st.download_button(
                        "Unduh Berkas Terenkripsi (.enc)",
                        data=data,
                        file_name=f"{up.name}.enc",
                        mime="application/octet-stream",
                        use_container_width=True,
                    )
        else:
            up = st.file_uploader("Pilih Berkas Terenkripsi (.enc):", type=None, key="enc_file_uploader")
            pwd = st.text_input("Passphrase Kunci RC4:", "RC4ColdKeystoreProtectionKey!", key="rc4_dec_key")
            if st.button("Dekripsi Berkas via RC4", use_container_width=True, type="primary", key="btn_dec_rc4_file"):
                if not (up and pwd):
                    st.error("Unggah berkas .enc dan masukkan passphrase kunci RC4.")
                else:
                    try:
                        dec, name = decrypt_file_bytes(up.read(), pwd)
                        st.success(f"Berkas berhasil didekripsi! Nama asli dipulihkan: {name}")
                        st.download_button(
                            f"Unduh Berkas Pulih ({name})",
                            data=dec,
                            file_name=name,
                            mime="application/octet-stream",
                            use_container_width=True,
                        )
                    except Exception as e:
                        st.error(f"Gagal dekripsi berkas: {e}")


# ----- TAB 3: STEGO PAPER WALLET (SPATIAL LSB) -----
def tab_stego_paper_wallet():
    page_head("Stego Paper Wallet & NFT Camouflage", "Sembunyikan 12 kata seed phrase ke dalam piksel citra kartu paper wallet atau avatar NFT via Spatial LSB.")
    action = seg(["Sisipkan Seed (Encode)", "Ekstrak Seed (Decode)"], "stego_action", "Tindakan")

    with st.container(border=True):
        if action.startswith("Sisipkan"):
            cover = st.file_uploader("Gambar Sampul (Avatar NFT / Kartu Paper Wallet):", type=["png", "bmp", "jpg"], key="stego_cover_up")
            secret = st.text_area(
                "12 Kata Seed Phrase yang Disamarkan:",
                "witch collapse practice feed shame open despair creek road again ice cheese",
                key="stego_secret_text",
            )
            if cover:
                st.image(Image.open(cover), caption="Cover Image Asli", use_container_width=True)

            if st.button("Sisipkan Seed Phrase ke Citra (LSB)", use_container_width=True, type="primary", key="btn_stego_embed"):
                if not (cover and secret):
                    st.error("Pilih gambar sampul dan masukkan seed phrase.")
                else:
                    try:
                        result, m = embed_secret_message(Image.open(cover), secret)
                        st.success("Seed Phrase Berhasil Disamarkan ke Citra Paper Wallet!")
                        st.image(result, caption="Stego Paper Wallet (Hasil Spatial LSB)", use_container_width=True)
                        st.table([
                            {"Metrik Kualitas Citra": "Peak Signal-to-Noise Ratio (PSNR)", "Nilai Evaluasi": f"{m['psnr_db']} dB ({m['visual_quality']})"},
                            {"Metrik Kualitas Citra": "Mean Squared Error (MSE)", "Nilai Evaluasi": str(m["mse"])},
                            {"Metrik Kualitas Citra": "Kapasitas Terpakai", "Nilai Evaluasi": f"{m['capacity_used_pct']}% ({m['payload_bytes']} bytes)"},
                        ])
                        buf = BytesIO()
                        result.save(buf, format="PNG")
                        st.download_button(
                            "Unduh Stego Paper Wallet (PNG)",
                            data=buf.getvalue(),
                            file_name="stego_paper_wallet.png",
                            mime="image/png",
                            use_container_width=True,
                        )
                    except Exception as e:
                        st.error(f"Gagal menyisipkan: {e}")
        else:
            probe = st.file_uploader("Unggah Stego Paper Wallet (PNG):", type=["png", "bmp"], key="stego_probe_up")
            if probe:
                img = Image.open(probe)
                st.image(img, caption="Stego Image Terpilih", width=300)
                if st.button("Ekstrak Seed Phrase dari Citra", use_container_width=True, type="primary", key="btn_stego_extract"):
                    try:
                        recovered = extract_secret_message(img)
                        st.success("Seed Phrase Berhasil Dipulihkan dari Piksel Gambar!")
                        st.code(recovered, language="text")
                    except Exception as e:
                        st.error(f"Gagal membaca stego image: {e}")


# ----- TAB 4: COLD WALLET LEDGER (POW BLOCKCHAIN) -----
def tab_cold_ledger():
    page_head("Buku Besar Transaksi Cold Custody", "Rantai blok Proof-of-Work (PoW SHA-256) untuk mutasi aset institusi dan simulasi deteksi manipulasi integritas.")
    bc = st.session_state.blockchain

    c1, c2 = st.columns(2)
    with c1:
        st.metric("Total Blok Terdaftar di Ledger", len(bc.chain))
    with c2:
        st.metric("Transaksi Masuk Antrian (Pending)", len(bc.pending_transactions))

    with st.container(border=True):
        card_head("Transfer Saldo Baru", "Catat Transaksi Cold-to-Hot Transfer")
        a, b = st.columns(2)
        with a:
            sender = st.text_input("Alamat Pengirim (Cold Vault):", "0x123240135_COLD_CUSTODY", key="bc_tx_sender")
        with b:
            recipient = st.text_input("Alamat Penerima (Hot Liquidity):", "0x71C8364437a5674366B0D5D690EAbc7C3E8d4239", key="bc_tx_recipient")
        c, d = st.columns(2)
        with c:
            asset = st.selectbox("Aset Digital:", ["BTC", "ETH", "USDT", "SOL"], key="bc_tx_asset")
        with d:
            amount = st.number_input("Jumlah Aset:", min_value=0.01, value=2.5, step=0.1, key="bc_tx_amount")
        memo = st.text_input("Memo Settlement Kustodi:", "Cold reserve liquidity release", key="bc_tx_memo")
        if st.button("Kirim Transaksi ke Antrian Blok", use_container_width=True, key="btn_queue_tx"):
            bc.add_transaction(sender, recipient, asset, amount, memo)
            st.success(f"Transaksi masuk antrian. Pending: {len(bc.pending_transactions)}")
            st.rerun()

    col_m, col_a = st.columns(2)
    with col_m:
        if st.button("Tambang Blok Baru (PoW Mining)", use_container_width=True, type="primary",
                     disabled=not bc.pending_transactions, key="btn_mine_bc"):
            with st.spinner("Menambang blok dengan SHA-256 Proof-of-Work..."):
                new_b = bc.mine_pending_transactions(miner_address="0x123240135_CUSTODY_NODE")
            st.success(f"Blok #{new_b.index} Berhasil Ditambang! Hash: {new_b.hash[:20]}...")
            st.rerun()
    with col_a:
        if st.button("Audit Integritas Rantai Blok", use_container_width=True, key="btn_audit_bc"):
            valid, report = bc.is_chain_valid()
            (st.success if valid else st.error)(report)

    st.markdown("<div class='eyebrow'>Riwayat Blok Terverifikasi</div>", unsafe_allow_html=True)
    shown = list(reversed(bc.chain))[:5]
    for b in shown:
        with st.expander(f"Blok #{b.index} · {time.strftime('%d %b %Y %H:%M:%S', time.localtime(b.timestamp))}"):
            st.table([
                {"Parameter": "Blok Hash (SHA-256)", "Nilai": b.hash},
                {"Parameter": "Previous Hash", "Nilai": b.previous_hash},
                {"Parameter": "Nonce PoW", "Nilai": str(b.nonce)},
            ])
            st.json(b.transactions)
    if len(bc.chain) > len(shown):
        st.caption(f"Menampilkan 5 blok terbaru dari total {len(bc.chain)} blok.")

    with st.expander("Panel Uji Manipulasi Saldo (Tamper Simulation)"):
        st.caption("Demonstrasikan ketahanan blockchain: ubah jumlah transfer pada blok lama, lalu jalankan Audit Integritas.")
        if len(bc.chain) > 1:
            idx = st.number_input("Nomor Blok Sasaran:", min_value=1, max_value=len(bc.chain) - 1, value=1, key="bc_tamper_idx")
            fake = st.number_input("Jumlah Aset Palsu:", value=999999.0, key="bc_tamper_amt")
            if st.button("Suntikkan Manipulasi ke Blok", key="btn_inject_tamper"):
                bc.tamper_block_for_demo(idx, fake)
                st.warning(f"Blok #{idx} telah dimanipulasi! Klik 'Audit Integritas Rantai Blok' untuk melihat deteksi pelanggaran.")
        else:
            st.caption("Tambang minimal 1 blok transaksi terlebih dahulu.")


# ----- TAB 5: WHITELISTED ADDRESS BOOK & UTXO (SQLITE AES-256-GCM AEAD) -----
def tab_address_book():
    page_head("Buku Alamat Whitelist & UTXO", "Penyimpanan basis data field-level terenkripsi AES-256-GCM AEAD dengan verifikasi 128-bit authentication tag.")
    key = st.session_state.master_session_key or "AegisDefaultMasterKey2026"

    with st.expander("Tambah Alamat / Data Sensitif Baru"):
        title = st.text_input("Label / Nama Entitas:", "Reserve Liquidity Whitelist", key="db_rec_title")
        cat = st.selectbox("Kategori Aset:", ["WHITELISTED_ADDRESS", "RECOVERY_SEED", "PRIVATE_KEY", "MULTISIG_CONFIG"], key="db_rec_cat")
        secret = st.text_area("Data Sensitif (Alamat / Kunci Privat / Seed):", "0x71C8364437a5674366B0D5D690EAbc7C3E8d4239", key="db_rec_secret")
        if st.button("Simpan Terenkripsi ke Basis Data (AES-256-GCM)", use_container_width=True, type="primary", key="btn_save_db_rec"):
            if title and secret:
                rid = insert_secret(title, cat, secret, key)
                st.success(f"Alamat berhasil disimpan secara terenkripsi dengan ID #{rid}.")
                st.rerun()
            else:
                st.error("Label dan data sensitif wajib diisi.")

    view = seg(["Alamat Terdekripsi (Petugas)", "Tampilan Raw SQLite di Disk"], "db_view_toggle", "Tampilan")

    if view.startswith("Alamat Terdekripsi"):
        records = get_all_secrets_decrypted(key)
        if not records:
            st.info("Belum ada rekaman alamat tersimpan.")
        for r in records:
            with st.container(border=True):
                c1, c2 = st.columns([4, 1])
                with c1:
                    st.markdown(f"**[{r['category']}] {r['title']}** &nbsp; {pill(r['decryption_status'], 'ok')}", unsafe_allow_html=True)
                    st.caption(f"ID: #{r['id']} · Ditambahkan: {r['created_at']}")
                    st.code(r["decrypted_secret"], language="text")
                with c2:
                    if st.button("Hapus", key=f"del_{r['id']}", use_container_width=True):
                        delete_record(r["id"])
                        st.rerun()
    else:
        st.caption("Isi fisik tabel `vault_records` di file SQLite (Raw Ciphertext - Apa yang dilihat peretas di disk):")
        raws = get_raw_database_records()
        if raws:
            st.table(raws)
        else:
            st.info("Basis data masih kosong.")


# =====================================================================
# RENDER MAIN DASHBOARD
# =====================================================================
def render_main_dashboard():
    try:
        c1, c2 = st.columns([3, 1], vertical_alignment="center")
    except TypeError:
        c1, c2 = st.columns([3, 1])
    with c1:
        st.markdown(
            "<div class='brand'><div class='logo'>🛡️</div><div>"
            "<div class='name'>Aegis Cold Custody</div>"
            f"<div class='muted'>{pill('● Sesi Aktif', 'ok')} &nbsp;{officer_name()[:28]}</div>"
            "</div></div>",
            unsafe_allow_html=True,
        )
    with c2:
        if st.button("Kunci Workstation", use_container_width=True, key="btn_logout_main"):
            reset_auth()
            st.rerun()

    t1, t2, t3, t4, t5 = st.tabs([
        "Mnemonic Armor",
        "Keystore Vault",
        "Stego Paper Wallet",
        "Ledger Aset",
        "Address Book"
    ])
    with t1:
        tab_mnemonic_armor()
    with t2:
        tab_keystore_vault()
    with t3:
        tab_stego_paper_wallet()
    with t4:
        tab_cold_ledger()
    with t5:
        tab_address_book()


# =====================================================================
# MAIN ROUTING (TOP LEVEL)
# =====================================================================
def main():
    try:
        init_database()
    except Exception:
        pass

    if not st.session_state.authenticated:
        st.markdown(
            "<div class='hero'><div class='logo'>🛡️</div>"
            "<h1>Aegis Cold Custody</h1>"
            "<p>Air-Gapped BIP-39 Mnemonic Seed Vault & Hardware Key Custodian<br>"
            "<span style='font-size:12px;color:#64748B;'>Enterprise Multi-Factor Digital Asset Custodian</span></p></div>",
            unsafe_allow_html=True,
        )

        _, mid, _ = st.columns([1, 4, 1])
        with mid:
            nav = seg(["Masuk", "Registrasi", "Developer"], "top_flow_nav", "Menu")

        if nav == "Masuk":
            render_login_flow()
        elif nav == "Registrasi":
            render_registration_flow()
        else:
            render_developer_flow()
    else:
        render_main_dashboard()


if __name__ == "__main__":
    main()

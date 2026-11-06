"""Sentix Digital Vault - Streamlit Frontend (desain v3)
Proyek Akhir Kriptografi, UPN "Veteran" Yogyakarta.

Alur:
1. Masuk      : wizard 3 langkah (Kunci USB -> Wajah -> Password), ada mode simulasi
2. Registrasi : data akun -> foto wajah -> unduh kunci USB
3. Developer  : alat uji, kriteria tugas, database mentah
4. Dashboard  : Pesan, File, Gambar, Aset, Rahasia

Letakkan juga config.toml di folder .streamlit/ (tema warna biru).
"""

import streamlit as st
import streamlit.components.v1 as components
import time
import json
import hashlib
from io import BytesIO
from PIL import Image

from config import DATA_DIR
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

st.set_page_config(
    page_title="Sentix Digital Vault",
    page_icon="🔐",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# =====================================================================
# STYLE
# =====================================================================
st.markdown("""
<style>
    :root {
        --bg:#0B0F17; --card:#121824; --card2:#0F1520; --line:#222C3E;
        --text:#E6EAF2; --muted:#8B97AB; --accent:#3B82F6; --accent2:#2563EB;
        --ok:#34D399; --okbg:#06382B; --warn:#FBBF24; --warnbg:#3A2A08;
    }
    .stApp { background:var(--bg); color:var(--text); }

    /* bersihkan chrome bawaan Streamlit */
    #MainMenu, footer, [data-testid="stToolbar"], [data-testid="stDecoration"] { display:none !important; }
    [data-testid="stHeader"] { background:transparent; height:0; }

    .block-container { max-width:760px; padding-top:3rem; padding-bottom:5rem; padding-left:1.5rem; padding-right:1.5rem; }
    [data-testid="stVerticalBlock"] { gap:1.5rem; }
    [data-testid="stHorizontalBlock"] { gap:1.25rem; }
    div[data-testid="stVerticalBlockBorderWrapper"] [data-testid="stVerticalBlock"] { gap:1.1rem; }

    /* iframe flash (tinggi 0) tidak boleh memakan ruang */
    [data-testid="stElementContainer"]:has(iframe[height="0"]),
    [data-testid="element-container"]:has(iframe[height="0"]) { display:none !important; }

    /* tipografi */
    h1,h2,h3,h4 { letter-spacing:-0.02em; margin:0 !important; padding:0 !important; }
    p { margin:0; }
    .muted { color:var(--muted); font-size:.92rem; line-height:1.5; }
    .center { text-align:center; }
    .eyebrow { font-size:11px; letter-spacing:.14em; text-transform:uppercase; color:var(--accent); font-weight:700; }
    .ctitle { font-size:1.3rem; font-weight:700; margin:6px 0 6px 0; }

    /* menu atas: rata tengah */
    .st-key-top_flow_nav,
    .st-key-top_flow_nav > div,
    .st-key-top_flow_nav [data-testid="stButtonGroup"],
    .st-key-top_flow_nav div[role="radiogroup"] {
        display:flex !important; justify-content:center !important; width:100%;
    }

    /* pilihan aktif pada segmented control: biru */
    [data-testid="stBaseButton-segmented_controlActive"] {
        background:rgba(59,130,246,.18) !important;
        border-color:#3B82F6 !important;
        color:#93C5FD !important;
    }

    /* hero */
    .hero { text-align:center; padding:8px 0 16px 0; }
    .hero .logo {
        width:56px; height:56px; margin:0 auto 14px auto; border-radius:16px;
        display:flex; align-items:center; justify-content:center; font-size:28px;
        background:linear-gradient(135deg,#1D4ED8,#3B82F6); box-shadow:0 8px 24px rgba(37,99,235,.35);
    }
    .hero h1 { font-size:1.9rem; font-weight:800; line-height:1.2; }
    .hero p  { color:var(--muted); margin-top:6px; font-size:.95rem; }

    /* kartu */
    div[data-testid="stVerticalBlockBorderWrapper"] {
        background:var(--card); border:1px solid var(--line) !important;
        border-radius:16px !important; padding:1.25rem 1.25rem;
    }
    div[data-testid="stVerticalBlockBorderWrapper"] div[data-testid="stVerticalBlockBorderWrapper"] {
        background:var(--card2); border-radius:12px !important;
    }

    /* tombol */
    .stButton > button, .stDownloadButton > button {
        border-radius:10px; min-height:44px; font-weight:600; transition:all .15s ease;
    }
    button[kind="primary"] { background:var(--accent2); border:0; color:#fff; }
    button[kind="primary"]:hover { background:var(--accent); }
    button[kind="secondary"] { background:#182131; border:1px solid var(--line); color:var(--text); }
    button[kind="secondary"]:hover { border-color:var(--accent); color:#fff; }

    /* input */
    div[data-baseweb="input"], div[data-baseweb="textarea"], div[data-baseweb="select"] > div {
        background:var(--card2) !important; border-radius:10px !important;
    }
    label p { font-size:.85rem !important; color:var(--muted) !important; }

    /* tab */
    div[data-baseweb="tab-list"] { gap:6px; border-bottom:1px solid var(--line); }
    button[data-baseweb="tab"] { font-weight:600; padding:10px 14px; }

    /* tabel */
    [data-testid="stTable"] table { width:100%; border-collapse:collapse; }
    [data-testid="stTable"] th { background:#182131; color:var(--muted); text-align:left; font-size:.8rem; text-transform:uppercase; letter-spacing:.06em; }
    [data-testid="stTable"] td, [data-testid="stTable"] th { padding:10px 12px; border-color:var(--line); }

    /* metrik */
    [data-testid="stMetric"] { background:var(--card2); border:1px solid var(--line); border-radius:12px; padding:14px 16px; }

    /* pill */
    .pill { display:inline-block; padding:4px 12px; font-size:12px; font-weight:650; border-radius:999px; }
    .pill.ok   { background:var(--okbg); color:var(--ok); border:1px solid #0B7A5A; }
    .pill.wait { background:#182131; color:var(--muted); border:1px solid var(--line); }
    .pill.warn { background:var(--warnbg); color:var(--warn); border:1px solid #8A6414; }

    /* stepper */
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

    /* bar dashboard */
    .brand { display:flex; align-items:center; gap:12px; }
    .brand .logo {
        width:40px; height:40px; border-radius:12px; display:flex; align-items:center; justify-content:center;
        font-size:20px; background:linear-gradient(135deg,#1D4ED8,#3B82F6);
    }
    .brand .name { font-weight:800; font-size:1.1rem; line-height:1.2; }
</style>
""", unsafe_allow_html=True)


# =====================================================================
# FLASH LAYAR UNTUK KAMERA
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
                b.innerHTML = '☀️ Ambil foto dengan flash layar';
                b.style.cssText = 'display:block;width:100%;margin:8px 0;padding:10px 16px;' +
                    'background:#2563EB;color:#fff;border:0;border-radius:10px;' +
                    'font-weight:600;font-size:13px;cursor:pointer;';
                b.addEventListener('click', function(e) {
                    e.preventDefault(); e.stopPropagation();
                    let o = doc.getElementById('sentix-flash-screen');
                    if (!o) {
                        o = doc.createElement('div');
                        o.id = 'sentix-flash-screen';
                        o.style.cssText = 'position:fixed;top:0;left:0;width:100vw;height:100vh;' +
                            'background:#fff;z-index:2147483647;pointer-events:none;' +
                            'transition:opacity .25s ease;';
                        doc.body.appendChild(o);
                    }
                    o.style.opacity = '1';
                    setTimeout(function() {
                        camBtn.click();
                        setTimeout(function() {
                            o.style.opacity = '0';
                            setTimeout(function() { if (o.parentNode) o.parentNode.removeChild(o); }, 250);
                        }, 1000);
                    }, 1000);
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
    return raw or "Petugas"


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
# 1. MASUK
# =====================================================================
def render_login_flow():
    render_flash_injector()

    d_ok = st.session_state.dongle_verified
    b_ok = st.session_state.biometric_verified
    current = 1 if not d_ok else (2 if not b_ok else 3)

    labels = ["Kunci USB", "Wajah", "Password"]
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

    # ---------- Langkah 1 ----------
    if current == 1:
        with st.container(border=True):
            card_head("Langkah 1 dari 3", "Kunci USB", "Pilih file kunci dongle milik Anda.")

            scanned = DongleVerifier.scan_possible_dongle_locations()
            dongle_choice = None
            if scanned:
                dongle_choice = st.selectbox(
                    "File kunci", [str(p) for p in scanned], key="sel_dongle_path"
                )
            else:
                st.info("Kunci USB tidak terdeteksi. Unggah file kunci Anda.")
                up = st.file_uploader("File dongle (.key / .json)", type=["key", "json"], key="up_dongle_login")
                if up:
                    temp_p = DATA_DIR / "temp_dongle.key"
                    temp_p.parent.mkdir(parents=True, exist_ok=True)
                    with open(temp_p, "wb") as f:
                        f.write(up.read())
                    dongle_choice = str(temp_p)

            if st.button("Verifikasi kunci", use_container_width=True, type="primary", key="btn_verif_dongle"):
                if not dongle_choice:
                    st.error("Pilih atau unggah file dongle terlebih dahulu.")
                else:
                    ok, msg, _ = DongleVerifier.verify_dongle_path(dongle_choice)
                    if ok:
                        st.session_state.dongle_verified = True
                        st.rerun()
                    else:
                        st.error(msg)

        with st.expander("Mode simulasi (untuk demo)"):
            st.caption("Lewati pemeriksaan kunci USB.")
            if st.button("Lewati verifikasi kunci", use_container_width=True, key="btn_bypass_dongle"):
                st.session_state.dongle_verified = True
                st.rerun()

    # ---------- Langkah 2 ----------
    elif current == 2:
        with st.container(border=True):
            card_head("Langkah 2 dari 3", "Verifikasi wajah", "Hadap kamera dengan pencahayaan yang cukup.")

            method = seg(["Kamera", "Unggah foto", "Simulasi"], "bio_method_radio", "Metode")

            if method == "Kamera":
                cam = st.camera_input("Kamera", key="cam_login_input", label_visibility="collapsed")
                if cam is not None:
                    h = hashlib.md5(cam.getvalue()).hexdigest()
                    if st.session_state.last_cam_hash != h:
                        st.session_state.last_cam_hash = h
                        ok, dist, msg = BiometricVerifier.verify_face(Image.open(cam))
                        st.session_state.biometric_verified = ok
                        st.session_state.authenticated_officer = msg
                        st.session_state.last_bio_result = {"ok": ok, "dist": dist, "msg": msg}
                        st.rerun()
                elif st.session_state.last_cam_hash is not None:
                    st.session_state.last_cam_hash = None
                    st.session_state.biometric_verified = False
                    st.session_state.last_bio_result = None
                    st.rerun()

            elif method == "Unggah foto":
                up = st.file_uploader("Foto wajah", type=["jpg", "jpeg", "png"], key="up_login_input")
                if up is not None:
                    h = hashlib.md5(up.getvalue()).hexdigest()
                    if st.session_state.last_up_hash != h:
                        st.session_state.last_up_hash = h
                        ok, dist, msg = BiometricVerifier.verify_face(Image.open(up))
                        st.session_state.biometric_verified = ok
                        st.session_state.authenticated_officer = msg
                        st.session_state.last_bio_result = {"ok": ok, "dist": dist, "msg": msg}
                        st.rerun()
                elif st.session_state.last_up_hash is not None:
                    st.session_state.last_up_hash = None
                    st.session_state.biometric_verified = False
                    st.session_state.last_bio_result = None
                    st.rerun()

            else:  # Simulasi
                st.info("Mode simulasi: wajah dianggap cocok tanpa pemindaian.")
                if st.button("Jalankan simulasi cocok", use_container_width=True, type="primary", key="btn_sim_ok"):
                    st.session_state.biometric_verified = True
                    st.session_state.authenticated_officer = "Biometrik Terverifikasi: Oktavian Prasetya Adi (Simulasi)"
                    st.session_state.last_bio_result = {
                        "ok": True, "dist": 0.05, "msg": "Wajah terverifikasi (mode simulasi).",
                    }
                    st.rerun()

            res = st.session_state.last_bio_result
            if res and not res["ok"]:
                st.error(res["msg"])
                low = res["msg"].lower()
                if "gelap" in low or "shutter" in low:
                    st.warning("Foto terlalu gelap. Buka penutup webcam dan pakai tombol flash layar.")
                with st.expander("Detail teknis"):
                    st.write(f"Cosine distance: `{res['dist']:.4f}` (diterima jika ≤ 0.32)")

        if st.button("← Kembali ke langkah 1", key="btn_back_1"):
            reset_auth()
            st.rerun()

    # ---------- Langkah 3 ----------
    else:
        with st.container(border=True):
            card_head("Langkah 3 dari 3", "Master password")
            st.markdown(
                f"<div class='muted'>Wajah terverifikasi: <b style='color:#E6EAF2'>{officer_name()}</b></div>",
                unsafe_allow_html=True,
            )
            pwd = st.text_input("Password", type="password", key="master_pwd_input")
            if st.button("Buka vault", use_container_width=True, type="primary", key="btn_unlock_vault"):
                ok, msg, master_key = PasswordVerifier.verify_password(pwd)
                if ok:
                    st.session_state.password_verified = True
                    st.session_state.master_session_key = master_key
                    st.session_state.authenticated = True
                    st.rerun()
                else:
                    st.error(f"Gagal: {msg}")

        c1, c2 = st.columns(2)
        with c1:
            if st.button("← Ulangi verifikasi wajah", use_container_width=True, key="btn_rst_biometric"):
                st.session_state.biometric_verified = False
                st.session_state.authenticated_officer = "N/A"
                st.session_state.last_bio_result = None
                st.session_state.last_cam_hash = None
                st.session_state.last_up_hash = None
                st.rerun()
        with c2:
            if st.button("Mulai dari awal", use_container_width=True, key="btn_rst_all"):
                reset_auth()
                st.rerun()


# =====================================================================
# 2. REGISTRASI
# =====================================================================
def render_registration_flow():
    render_flash_injector()

    with st.container(border=True):
        card_head("Langkah 1 dari 3", "Data akun")
        c1, c2 = st.columns(2)
        with c1:
            reg_name = st.text_input("Nama lengkap", key="reg_name_input")
        with c2:
            reg_uid = st.text_input("User ID (tanpa spasi)", key="reg_uid_input")
        c3, c4 = st.columns(2)
        with c3:
            reg_pwd1 = st.text_input("Master password", type="password", key="reg_pwd1_input")
        with c4:
            reg_pwd2 = st.text_input("Ulangi password", type="password", key="reg_pwd2_input")

    with st.container(border=True):
        card_head("Langkah 2 dari 3", "Foto wajah", "Hadap kamera, lalu ambil foto.")
        reg_cam_file = st.camera_input("Kamera", key="reg_cam_input", label_visibility="collapsed")
        reg_up_file = None
        with st.expander("Atau unggah foto"):
            reg_up_file = st.file_uploader("Foto wajah", type=["jpg", "jpeg", "png"], key="reg_up_input")

    face_source = None
    if reg_cam_file is not None:
        face_source = Image.open(reg_cam_file)
    elif reg_up_file is not None:
        face_source = Image.open(reg_up_file)

    with st.container(border=True):
        card_head("Langkah 3 dari 3", "Selesaikan pendaftaran")
        if face_source is None:
            st.markdown(pill("Foto wajah belum ada", "warn"), unsafe_allow_html=True)
        else:
            st.markdown(pill("Foto wajah siap", "ok"), unsafe_allow_html=True)

        if st.button("Daftar dan buat kunci USB", use_container_width=True, type="primary", key="btn_execute_registration"):
            if not reg_name or not reg_uid:
                st.error("Nama dan User ID wajib diisi.")
            elif " " in reg_uid:
                st.error("User ID tidak boleh mengandung spasi.")
            elif not reg_pwd1 or reg_pwd1 != reg_pwd2:
                st.error("Password kosong atau tidak sama.")
            elif face_source is None:
                st.error("Ambil atau unggah foto wajah terlebih dahulu.")
            else:
                try:
                    BiometricVerifier.enroll_face(face_source, user_id=reg_uid, name=reg_name)
                    PasswordVerifier.register_account(reg_uid, reg_name, reg_pwd1)
                    token = DongleVerifier.generate_dongle_token(
                        vault_id=f"VAULT-{reg_uid.upper()}", holder_name=reg_name
                    )
                    st.session_state.latest_registered_dongle = json.dumps(token, indent=2).encode("utf-8")
                    st.session_state.registration_success_info = f"Akun {reg_name} ({reg_uid}) berhasil dibuat."
                    st.rerun()
                except Exception as e:
                    st.error(f"Pendaftaran gagal: {e}")

        if st.session_state.get("registration_success_info"):
            st.success(st.session_state["registration_success_info"])
            st.download_button(
                "Unduh kunci USB (sentix_dongle.key)",
                data=st.session_state.get("latest_registered_dongle", b""),
                file_name="sentix_dongle.key",
                mime="application/json",
                use_container_width=True,
                key="btn_download_new_dongle",
            )
            st.caption("Simpan file ini ke flashdisk, lalu buka menu Masuk.")


# =====================================================================
# 3. DEVELOPER
# =====================================================================
def render_developer_flow():
    t1, t2, t3 = st.tabs(["Alat uji", "Kriteria tugas", "Database"])

    with t1:
        with st.container(border=True):
            card_head("Pintasan", "Demo cepat", "Lewati login untuk menguji modul langsung.")
            if st.button("Masuk langsung ke dashboard", use_container_width=True, type="primary", key="dev_fast_bypass"):
                st.session_state.dongle_verified = True
                st.session_state.biometric_verified = True
                st.session_state.password_verified = True
                st.session_state.authenticated_officer = "Oktavian Prasetya Adi (Dev Bypass)"
                st.session_state.master_session_key = hashlib.sha256(b"SentixMasterBypassKey2026").hexdigest()
                st.session_state.authenticated = True
                st.rerun()
            if st.button("Reset semua sesi", use_container_width=True, key="dev_full_reset"):
                reset_auth()
                st.rerun()

        with st.container(border=True):
            card_head("Dongle", "Dongle virtual")
            if st.button("Buat dongle di data/dongle/", use_container_width=True, key="dev_mk_dongle"):
                p = DongleVerifier.write_dongle_to_path(DATA_DIR / "dongle")
                st.success(f"Dongle dibuat di: {p}")

        with st.container(border=True):
            card_head("Biometrik", "Wajah terdaftar")
            roster = BiometricVerifier.list_enrolled_faces()
            if not roster:
                st.caption("Belum ada wajah terdaftar.")
            for idx, r in enumerate(roster):
                c1, c2 = st.columns([4, 1])
                with c1:
                    st.markdown(
                        f"**{r['name']}**<br><span class='muted'>`{r['user_id']}` · {r['enrolled_at']}</span>",
                        unsafe_allow_html=True,
                    )
                with c2:
                    if st.button("Hapus", key=f"del_face_{r['user_id']}_{idx}", use_container_width=True):
                        BiometricVerifier.delete_face(r["user_id"])
                        st.rerun()

    with t2:
        st.table([
            {"No": 1, "Kriteria": "Login biometrik + dongle", "Implementasi": "3FA: USB + wajah + password"},
            {"No": 2, "Kriteria": "Login dengan kriptografi", "Implementasi": "PBKDF2-HMAC-SHA256"},
            {"No": 3, "Kriteria": "Pesan: super enkripsi", "Implementasi": "Vigenère, Vernam, AES"},
            {"No": 4, "Kriteria": "File: algoritma beda", "Implementasi": "RC4 stream cipher"},
            {"No": 5, "Kriteria": "Pesan penting di basis data", "Implementasi": "SQLite + AES-256-GCM"},
            {"No": 6, "Kriteria": "Gambar: steganografi", "Implementasi": "LSB RGB + PSNR & MSE"},
            {"No": 7, "Kriteria": "Aset: blockchain", "Implementasi": "SHA-256 + Proof-of-Work"},
        ])

    with t3:
        st.caption("Isi tabel di disk (ciphertext, belum didekripsi).")
        raws = get_raw_database_records()
        if raws:
            st.table(raws)
        else:
            st.info("Database masih kosong.")


# =====================================================================
# 4. DASHBOARD
# =====================================================================
def tab_pesan():
    page_head("Pesan", "Enkripsi atau dekripsi teks dengan beberapa lapis algoritma.")

    c1, c2 = st.columns(2)
    with c1:
        st.caption("Skema")
        scheme = seg(["4 tahap", "2 tahap"], "rad_super_scheme", "Skema")
    with c2:
        st.caption("Tindakan")
        action = seg(["Enkripsi", "Dekripsi"], "rad_msg_action", "Tindakan")

    with st.container(border=True):
        if scheme == "4 tahap":
            card_head("Skema 4 tahap", "Caesar → Vigenère → Vernam → AES-128")
            if action == "Enkripsi":
                text = st.text_area("Pesan", "Pesan rahasia untuk dienkripsi", height=90, key="sup4_plain_in")
            else:
                text = st.text_area("Pesan terenkripsi", "", height=90, key="sup4_cipher_in")

            ka, kb = st.columns(2)
            with ka:
                shift = st.number_input("Caesar shift", min_value=1, max_value=25, value=8, key="k_c_shift_in")
                vig = st.text_input("Kunci Vigenère", value="KUNCI", key="k_v_key_in")
            with kb:
                vern = st.text_input("Keystream Vernam", value="VERNAM", key="k_vernam_in")
                aes = st.text_input("Kunci AES-128", value="mysecretkey12345", key="k_aes_key_in")

            if st.button(f"{action} pesan", use_container_width=True, type="primary", key="btn_exec_4stage"):
                if not (text and vig and vern and aes):
                    st.error("Lengkapi pesan dan semua kunci.")
                else:
                    try:
                        if action == "Enkripsi":
                            r = super_encrypt_4stage(text, shift, vig, vern, aes)
                            st.success("Pesan berhasil dienkripsi.")
                            st.caption("Hasil (Base64)")
                            st.code(r["final_cipher"], language="text")
                            with st.expander("Lihat tahapan"):
                                st.table(r["stages"])
                        else:
                            r = super_decrypt_4stage(text.strip(), shift, vig, vern, aes)
                            st.success("Pesan berhasil dibuka.")
                            st.caption("Pesan asli")
                            st.code(r["final_plaintext"], language="text")
                            with st.expander("Lihat tahapan"):
                                st.table(r["stages_dec"])
                    except Exception as e:
                        st.error(f"Gagal: {e}. Periksa format pesan dan kunci.")
        else:
            card_head("Skema 2 tahap", "Vigenère → AES-256-CBC")
            if action == "Enkripsi":
                text = st.text_area("Pesan", "Pesan rahasia untuk dienkripsi", height=90, key="se_plain_input")
            else:
                text = st.text_area("Pesan terenkripsi", "", height=90, key="se_cipher_input")

            ka, kb = st.columns(2)
            with ka:
                vig = st.text_input("Kunci Vigenère", "UPN2026", key="se_k_classical")
            with kb:
                aes = st.text_input("Passphrase AES", "SentixSuperSecretKey!", key="se_k_modern")

            if st.button(f"{action} pesan", use_container_width=True, type="primary", key="btn_exec_super"):
                if not (text and vig and aes):
                    st.error("Lengkapi pesan dan semua kunci.")
                else:
                    try:
                        if action == "Enkripsi":
                            r = super_encrypt(text, vig, aes)
                            st.success("Pesan berhasil dienkripsi.")
                            st.caption("Hasil (Base64)")
                            st.code(r["final_ciphertext_base64"], language="text")
                            with st.expander("Lihat tahapan"):
                                st.caption("Output Vigenère")
                                st.code(r["vigenere_output"], language="text")
                                st.caption(f"IV (hex): {r['iv_hex']}")
                        else:
                            r = super_decrypt(text.strip(), vig, aes)
                            st.success("Pesan berhasil dibuka.")
                            st.caption("Pesan asli")
                            st.code(r["final_plaintext"], language="text")
                            with st.expander("Lihat tahapan"):
                                st.caption("Hasil dekripsi AES")
                                st.code(r["aes_intermediate"], language="text")
                    except Exception as e:
                        st.error(f"Gagal: {e}. Kunci salah atau pesan rusak.")


def tab_file():
    page_head("File", "Enkripsi file dengan RC4. Hasilnya berformat .enc.")
    action = seg(["Enkripsi", "Dekripsi"], "file_mode_radio", "Tindakan")

    with st.container(border=True):
        if action == "Enkripsi":
            up = st.file_uploader("File yang diamankan", type=None, key="raw_file_uploader")
            pwd = st.text_input("Kunci", "RC4VaultProtectionKey!", key="rc4_enc_key")
            if st.button("Enkripsi file", use_container_width=True, type="primary", key="btn_enc_rc4_file"):
                if not (up and pwd):
                    st.error("Pilih file dan isi kunci.")
                else:
                    data = encrypt_file_bytes(up.read(), up.name, pwd)
                    st.success(f"File dienkripsi ({len(data)} bytes).")
                    st.download_button(
                        "Unduh file terenkripsi (.enc)",
                        data=data, file_name=f"{up.name}.enc",
                        mime="application/octet-stream", use_container_width=True,
                    )
        else:
            up = st.file_uploader("File terenkripsi (.enc)", type=None, key="enc_file_uploader")
            pwd = st.text_input("Kunci", "RC4VaultProtectionKey!", key="rc4_dec_key")
            if st.button("Dekripsi file", use_container_width=True, type="primary", key="btn_dec_rc4_file"):
                if not (up and pwd):
                    st.error("Pilih file dan isi kunci.")
                else:
                    try:
                        dec, name = decrypt_file_bytes(up.read(), pwd)
                        st.success(f"File dipulihkan: {name}")
                        st.download_button(
                            f"Unduh {name}", data=dec, file_name=name,
                            mime="application/octet-stream", use_container_width=True,
                        )
                    except Exception as e:
                        st.error(f"Gagal dekripsi: {e}")


def tab_gambar():
    page_head("Gambar", "Sembunyikan pesan di dalam gambar (steganografi LSB).")
    action = seg(["Sisipkan pesan", "Baca pesan"], "stego_action", "Tindakan")

    with st.container(border=True):
        if action == "Sisipkan pesan":
            cover = st.file_uploader("Gambar sampul", type=["png", "bmp", "jpg"], key="stego_cover_up")
            secret = st.text_area("Pesan rahasia", "Pesan rahasia yang ingin disembunyikan", key="stego_secret_text")
            if cover:
                st.image(Image.open(cover), caption="Gambar asli", use_container_width=True)

            if st.button("Sisipkan pesan", use_container_width=True, type="primary", key="btn_stego_embed"):
                if not (cover and secret):
                    st.error("Pilih gambar dan isi pesan.")
                else:
                    try:
                        result, m = embed_secret_message(Image.open(cover), secret)
                        st.success("Pesan berhasil disisipkan.")
                        st.image(result, caption="Hasil", use_container_width=True)
                        st.table([
                            {"Metrik": "PSNR", "Nilai": f"{m['psnr_db']} dB ({m['visual_quality']})"},
                            {"Metrik": "MSE", "Nilai": str(m["mse"])},
                            {"Metrik": "Kapasitas terpakai", "Nilai": f"{m['capacity_used_pct']}% ({m['payload_bytes']} bytes)"},
                        ])
                        buf = BytesIO()
                        result.save(buf, format="PNG")
                        st.download_button(
                            "Unduh gambar (PNG)", data=buf.getvalue(),
                            file_name="stego_asset_image.png", mime="image/png",
                            use_container_width=True,
                        )
                    except Exception as e:
                        st.error(f"Gagal menyisipkan: {e}")
        else:
            probe = st.file_uploader("Gambar hasil steganografi", type=["png", "bmp"], key="stego_probe_up")
            if probe:
                img = Image.open(probe)
                st.image(img, width=300)
                if st.button("Baca pesan", use_container_width=True, type="primary", key="btn_stego_extract"):
                    try:
                        st.success("Pesan ditemukan.")
                        st.code(extract_secret_message(img), language="text")
                    except Exception as e:
                        st.error(f"Gagal membaca pesan: {e}")


def tab_aset():
    page_head("Aset", "Catat transaksi dan periksa apakah riwayatnya masih utuh.")
    bc = st.session_state.blockchain

    c1, c2 = st.columns(2)
    with c1:
        st.metric("Jumlah blok", len(bc.chain))
    with c2:
        st.metric("Transaksi pending", len(bc.pending_transactions))

    with st.container(border=True):
        card_head("Transaksi", "Tambah transaksi baru")
        a, b = st.columns(2)
        with a:
            sender = st.text_input("Pengirim", "COLD_VAULT_01", key="bc_tx_sender")
        with b:
            recipient = st.text_input("Penerima", "HOT_RESERVE_ALPHA", key="bc_tx_recipient")
        c, d = st.columns(2)
        with c:
            asset = st.selectbox("Aset", ["BTC", "ETH", "USDT", "IDR_STABLE"], key="bc_tx_asset")
        with d:
            amount = st.number_input("Jumlah", min_value=0.01, value=10.0, step=0.5, key="bc_tx_amount")
        memo = st.text_input("Catatan", "Settlement transfer", key="bc_tx_memo")
        if st.button("Tambah ke antrian", use_container_width=True, key="btn_queue_tx"):
            bc.add_transaction(sender, recipient, asset, amount, memo)
            st.rerun()

    col_m, col_a = st.columns(2)
    with col_m:
        if st.button("Tambang blok baru", use_container_width=True, type="primary",
                     disabled=not bc.pending_transactions, key="btn_mine_bc"):
            with st.spinner("Menambang blok..."):
                new_b = bc.mine_pending_transactions(miner_address="SENTIX_AUDIT_NODE")
            st.success(f"Blok #{new_b.index} berhasil ditambang.")
            st.rerun()
    with col_a:
        if st.button("Periksa integritas", use_container_width=True, key="btn_audit_bc"):
            valid, report = bc.is_chain_valid()
            (st.success if valid else st.error)(report)

    st.markdown("<div class='eyebrow'>Riwayat blok</div>", unsafe_allow_html=True)
    shown = list(reversed(bc.chain))[:5]
    for b in shown:
        with st.expander(f"Blok #{b.index} · {time.strftime('%d %b %Y %H:%M', time.localtime(b.timestamp))}"):
            st.table([
                {"Item": "Hash", "Nilai": b.hash},
                {"Item": "Hash sebelumnya", "Nilai": b.previous_hash},
                {"Item": "Nonce", "Nilai": str(b.nonce)},
            ])
            st.json(b.transactions)
    if len(bc.chain) > len(shown):
        st.caption(f"Menampilkan 5 blok terbaru dari {len(bc.chain)}.")

    with st.expander("Simulasi manipulasi data"):
        st.caption("Ubah jumlah di blok lama, lalu klik Periksa integritas.")
        if len(bc.chain) > 1:
            idx = st.number_input("Nomor blok", min_value=1, max_value=len(bc.chain) - 1, value=1, key="bc_tamper_idx")
            fake = st.number_input("Jumlah palsu", value=999999.0, key="bc_tamper_amt")
            if st.button("Manipulasi blok", key="btn_inject_tamper"):
                bc.tamper_block_for_demo(idx, fake)
                st.warning(f"Blok #{idx} diubah. Jalankan pemeriksaan integritas.")
        else:
            st.caption("Tambang minimal 1 blok dulu.")


def tab_rahasia():
    page_head("Data rahasia", "Disimpan terenkripsi AES-256-GCM di database.")
    key = st.session_state.master_session_key or "SentixDefaultMasterKey"

    with st.expander("Tambah data rahasia"):
        title = st.text_input("Judul", "Catatan Rahasia", key="db_rec_title")
        cat = st.selectbox("Kategori", ["SEED_PHRASE", "PRIVATE_KEY", "LEGAL_CONTRACT", "FINANCIAL_MEMO"], key="db_rec_cat")
        secret = st.text_area("Isi rahasia", "", key="db_rec_secret")
        if st.button("Simpan terenkripsi", use_container_width=True, type="primary", key="btn_save_db_rec"):
            if title and secret:
                rid = insert_secret(title, cat, secret, key)
                st.success(f"Tersimpan dengan ID #{rid}.")
                st.rerun()
            else:
                st.error("Judul dan isi wajib diisi.")

    view = seg(["Data rahasia", "Tampilan teknis"], "db_view_toggle", "Tampilan")

    if view == "Data rahasia":
        records = get_all_secrets_decrypted(key)
        if not records:
            st.info("Belum ada data.")
        for r in records:
            with st.container(border=True):
                c1, c2 = st.columns([4, 1])
                with c1:
                    st.markdown(f"**{r['title']}** &nbsp; {pill(r['category'], 'wait')}", unsafe_allow_html=True)
                    st.caption(f"ID {r['id']} · {r['created_at']} · {r['decryption_status']}")
                    st.code(r["decrypted_secret"], language="text")
                with c2:
                    if st.button("Hapus", key=f"del_{r['id']}", use_container_width=True):
                        delete_record(r["id"])
                        st.rerun()
    else:
        st.caption("Isi tabel `vault_records` di disk (ciphertext).")
        raws = get_raw_database_records()
        if raws:
            st.table(raws)
        else:
            st.info("Database masih kosong.")


def render_main_dashboard():
    try:
        c1, c2 = st.columns([3, 1], vertical_alignment="center")
    except TypeError:  # Streamlit versi lama
        c1, c2 = st.columns([3, 1])
    with c1:
        st.markdown(
            "<div class='brand'><div class='logo'>🔐</div><div>"
            "<div class='name'>Sentix Digital Vault</div>"
            f"<div class='muted'>{pill('● Sesi aktif', 'ok')} &nbsp;{officer_name()[:28]}</div>"
            "</div></div>",
            unsafe_allow_html=True,
        )
    with c2:
        if st.button("Kunci vault", use_container_width=True, key="btn_logout_main"):
            reset_auth()
            st.rerun()

    t1, t2, t3, t4, t5 = st.tabs(["Pesan", "File", "Gambar", "Aset", "Rahasia"])
    with t1:
        tab_pesan()
    with t2:
        tab_file()
    with t3:
        tab_gambar()
    with t4:
        tab_aset()
    with t5:
        tab_rahasia()


# =====================================================================
# ROUTING
# =====================================================================
def main():
    try:
        init_database()
    except Exception:
        pass

    if not st.session_state.authenticated:
        st.markdown(
            "<div class='hero'><div class='logo'>🔐</div>"
            "<h1>Sentix Digital Vault</h1>"
            "<p>Brankas digital dengan verifikasi 3 lapis</p></div>",
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

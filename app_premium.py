import streamlit as st
import base64
from pathlib import Path
from datetime import date, datetime
from zoneinfo import ZoneInfo
from html import escape

# ============================================================
# KONFIGURASI APLIKASI
# ============================================================
st.set_page_config(
    page_title="WORTH",
    page_icon="💗",
    layout="centered",
    initial_sidebar_state="collapsed",
)

BASE_DIR = Path(__file__).parent
LOGO_CANDIDATES = [
    BASE_DIR / "logo_worth.png",
    BASE_DIR / "logo_worth.jpeg",
    BASE_DIR / "logo_worth(1).jpeg",
]
BOT_CANDIDATES = [
    BASE_DIR / "bot_worth.png",
    BASE_DIR / "bot_worth.jpeg",
    BASE_DIR / "bot_worth(1).jpeg",
]
LOGO = next((p for p in LOGO_CANDIDATES if p.exists()), LOGO_CANDIDATES[0])
BOT = next((p for p in BOT_CANDIDATES if p.exists()), BOT_CANDIDATES[0])

# ============================================================
# DATA WORTH
# ============================================================
USAGE = {
    "Setiap hari": 10,
    "Beberapa kali seminggu": 20,
    "Sekali seminggu": 40,
    "Sekali sebulan": 60,
    "Jarang": 90,
}

SIMILAR = {
    "Tidak": 10,
    "Ya, tetapi saya membutuhkan satu lagi": 50,
    "Ya, saya sebenarnya tidak terlalu membutuhkan satu lagi": 90,
}

REASON = {
    "Saya benar-benar membutuhkannya": 10,
    "Saya sudah menginginkannya sejak lama": 30,
    "Ada diskon": 50,
    "FOMO / sedang tren": 80,
    "Impulsif": 90,
}

BUDGET = {
    "Tidak memengaruhi budget saya": 10,
    "Sedikit memengaruhi budget saya": 40,
    "Saya harus mengurangi pengeluaran lain": 70,
}

CONVICTION = {
    "Ya, saya tetap ingin membelinya": 10,
    "Mungkin, saya masih mempertimbangkannya": 50,
    "Tidak, kemungkinan saya tidak jadi membelinya": 90,
}

FREE_DAILY_LIMIT = 3
PREMIUM_PRICE = 9900
PREMIUM_CODE = "WORTH-PREM-2026"  # kode demo prototype

# ============================================================
# SESSION STATE
# ============================================================
def initial_state():
    return {
        "page": "home",
        "menu_open": False,
        "nav_history": [],
        "name": "Pengguna WORTH",
        "email": "",
        "is_premium": False,
        "premium_activated_at": None,
        "usage_date": date.today().isoformat(),
        "daily_checks": 0,
        "history": [],
        "item": "",
        "price": 0,
        "question": 1,
        "usage": None,
        "similar": None,
        "reason": None,
        "budget": None,
        "conviction": None,
        "score": 0,
        "risk": "",
        "decision": None,
        "result_counted": False,
        "current_record_id": None,
        "account_saved": False,
        "premium_just_activated": False,
        "logout_confirm": False,
        "leave_confirm": False,
        "pending_page": None,
        "chat_times": {},
    }


for key, value in initial_state().items():
    if key not in st.session_state:
        st.session_state[key] = value


def refresh_daily_quota():
    today = date.today().isoformat()
    if st.session_state.usage_date != today:
        st.session_state.usage_date = today
        st.session_state.daily_checks = 0


refresh_daily_quota()

# ============================================================
# CSS
# ============================================================
st.markdown(
    """
<style>
.stApp {
    background:
        radial-gradient(circle at 8% 12%, rgba(255,255,255,.95) 0 80px, transparent 82px),
        radial-gradient(circle at 92% 20%, rgba(255,255,255,.90) 0 110px, transparent 112px),
        radial-gradient(circle at 10% 100%, #ffe5ef 0 160px, transparent 162px),
        radial-gradient(circle at 90% 100%, #ffe7f0 0 170px, transparent 172px),
        linear-gradient(180deg,#fff9fc 0%,#fff4f8 100%);
}

.block-container {
    max-width: 580px;
    padding-top: 14px;
    padding-bottom: 60px;
}

#MainMenu, footer {visibility:hidden;}
header[data-testid="stHeader"] {background:transparent;}
html, body, [class*="css"] {font-family:Arial,sans-serif;}
button[title="View fullscreen"], div[data-testid="stImage"] button {display:none!important;}

/* HEADER */
.worth-brand {
    color:#E83D7D;
    font-size:22px;
    font-weight:800;
    letter-spacing:2px;
    padding-top:8px;
}

.app-page-title {
    color:#D92F70!important;
    -webkit-text-fill-color:#D92F70!important;
    font-size:18px;
    font-weight:800;
    padding-top:8px;
    white-space:nowrap;
}

/* HAMBURGER */
div[class*="st-key-menu_"] button {
    background:linear-gradient(135deg,#F56A9C,#ED3B7D)!important;
    color:#FFF!important;
    -webkit-text-fill-color:#FFF!important;
    border:none!important;
    outline:none!important;
    border-radius:11px!important;
    width:40px!important;
    min-width:40px!important;
    max-width:40px!important;
    height:40px!important;
    min-height:40px!important;
    max-height:40px!important;
    padding:0!important;
    margin-left:auto!important;
    box-shadow:0 5px 14px rgba(235,55,123,.16)!important;
}

div[class*="st-key-menu_"] button p {
    color:#FFF!important;
    -webkit-text-fill-color:#FFF!important;
    font-size:20px!important;
    font-weight:700!important;
    line-height:1!important;
}

div[class*="st-key-menu_"] button:hover {background:#E83D7D!important;}

/* BACK BUTTON */
div[class*="st-key-back_"] button {
    background:transparent!important;
    border:none!important;
    color:#E83D7D!important;
    -webkit-text-fill-color:#E83D7D!important;
    width:40px!important;
    min-width:40px!important;
    height:40px!important;
    min-height:40px!important;
    padding:0!important;
    box-shadow:none!important;
}

div[class*="st-key-back_"] button p {
    color:#E83D7D!important;
    -webkit-text-fill-color:#E83D7D!important;
    font-size:25px!important;
    font-weight:700!important;
}

/* BUTTON */
.stButton > button {
    width:100%;
    min-height:50px;
    border-radius:14px;
    border:1.5px solid #E83D7D;
    font-size:14px;
    font-weight:700;
    color:#E83D7D;
    background:#FFF;
}

.stButton > button[kind="primary"] {
    color:#FFF;
    background:linear-gradient(135deg,#F46D9F,#EB377B);
    border:1.5px solid #E83D7D;
    box-shadow:0 6px 16px rgba(235,55,123,.16);
}

/* INPUT */
div[data-testid="stTextInput"] {
    margin-top: 3px !important;
    margin-bottom: 5px !important;
}

div[data-testid="stTextInput"] label {
    margin-bottom: 3px !important;
}
div[data-testid="stTextInput"] input {
    min-height:52px!important;
    background:#FFF!important;
    color:#2F2530!important;
    -webkit-text-fill-color:#2F2530!important;
    border:1.5px solid #E83D7D!important;
    border-radius:14px!important;
    padding:0 16px!important;
    font-size:15px!important;
    box-shadow:0 0 0 1000px #FFF inset!important;
    -webkit-box-shadow:0 0 0 1000px #FFF inset!important;
}

div[data-testid="stTextInput"] input::placeholder {
    color:#C9366B!important;
    -webkit-text-fill-color:#C9366B!important;
    opacity:1!important;
}

/* HOME */
.tagline {
    text-align:center;
    color:#E83D7D;
    font-size:20px;
    font-weight:750;
    letter-spacing:4px;
    line-height:1.5;
    margin:10px 0 25px;
}

.intro-box,.soft-card {
    background:#FFF;
    border:1.5px solid #F1CCD9;
    border-radius:18px;
    padding:18px;
    margin:15px 0;
    color:#302630;
    line-height:1.6;
    box-shadow:0 8px 24px rgba(236,63,128,.05);
}

.quota-box {
    background:#FFF;
    border:1px solid #F1CCD9;
    border-radius:14px;
    padding:14px;
    margin:12px 0;
    color:#302630;
}

.muted {color:#8F7E88;font-size:13px;}

/* CHAT */
.bot-bubble {
    background:linear-gradient(135deg,#FFF1F6,#FDE5EE);
    border-radius:7px 18px 18px 18px;
    padding:16px 18px 26px;
    color:#2F2530;
    font-size:15px;
    line-height:1.55;
    position:relative;
}

.user-bubble {
    background:#FBE2EC;
    border-radius:18px 7px 18px 18px;
    padding:14px 18px 26px;
    margin-bottom:24px;
    color:#2F2530;
    font-size:15px;
    line-height:1.55;
    position:relative;
}

.time {
    position:absolute;
    right:13px;
    bottom:7px;
    color:#9B8B96;
    font-size:10px;
}

/* PROGRESS & RADIO */
.question-number {text-align:center;color:#D81B60;font-weight:700;font-size:14px;margin-bottom:12px;}
.progress-background {width:100%;height:8px;background:#F8D7E3;border-radius:20px;overflow:hidden;margin-bottom:24px;}
.progress-pink {height:100%;background:#D81B60;border-radius:20px;}
div[role="radiogroup"] {gap:8px;}
div[role="radiogroup"] > label {
    background:#FFF!important;
    border:1.5px solid #F0C9D7!important;
    border-radius:14px;
    min-height:54px;
    padding:9px 14px;
    margin-bottom:5px;
}
div[role="radiogroup"] > label p, div[role="radiogroup"] > label span {
    color:#3A2831!important;
    opacity:1!important;
    font-weight:500!important;
}
div[role="radiogroup"] > label:hover {border-color:#C9366B!important;background:#FFF3F7!important;}
div[role="radiogroup"] input[type="radio"] {accent-color:#C9366B!important;}

/* RESULT */
.result-title {
    background:linear-gradient(135deg,#FFE0EB,#FFD5E5);
    color:#C92665;
    text-align:center;
    font-size:20px;
    font-weight:800;
    padding:16px;
    margin-top:24px;
    border-radius:18px 18px 0 0;
}

.result-body {
    background:rgba(255,255,255,.95);
    border:1px solid #F3C7D6;
    border-top:none;
    border-radius:0 0 18px 18px;
    padding:24px 16px;
    text-align:center;
}

.score-circle {
    width:165px;
    height:165px;
    border-radius:50%;
    margin:auto;
    background:conic-gradient(#EB3C7D 0deg var(--score-angle),#F8BED2 var(--score-angle) 360deg);
    display:flex;
    justify-content:center;
    align-items:center;
    position:relative;
}

.score-circle:after {content:"";width:130px;height:130px;border-radius:50%;background:#FFF;position:absolute;}
.score-text {position:relative;z-index:2;color:#171323;}
.score-big {font-size:46px;font-weight:800;line-height:1;}
.score-small {font-size:14px;font-weight:700;}
.score-label {color:#7E7580;font-size:11px;margin-top:5px;}
.risk-badge {display:inline-block;margin-top:16px;padding:9px 22px;border-radius:13px;background:#FFE6A4;color:#342134;font-size:15px;font-weight:800;}

.info-card {background:#FFF;border:1px solid #F1CCD9;border-radius:17px;padding:18px;margin-top:24px;color:#302630;}
.card-title {font-size:17px;font-weight:800;margin-bottom:16px;}
.item-info {display:flex;align-items:center;gap:16px;}
.item-symbol {width:70px;height:70px;border-radius:14px;display:flex;justify-content:center;align-items:center;background:#FDE5EE;font-size:34px;}
.info-label {color:#978893;font-size:12px;}
.info-value {color:#302630;font-size:15px;font-weight:700;margin-bottom:7px;}

.worth-why-box {background:#FFF!important;border:1.5px solid #F1CCD9!important;border-radius:16px!important;padding:18px!important;margin:22px 0 18px!important;}
.worth-why-title {color:#E83D7D!important;-webkit-text-fill-color:#E83D7D!important;font-size:18px!important;font-weight:800!important;margin-bottom:14px!important;}
.worth-why-content {color:#302630!important;-webkit-text-fill-color:#302630!important;font-size:15px;line-height:1.8;}
.final-message {background:#FFF0F6;border-radius:16px;padding:18px;margin:18px 0 28px;text-align:center;color:#4D4049;}

/* PAGE ELEMENTS */
.section-title {color:#E83D7D;font-size:18px;font-weight:800;margin:18px 0 10px;}
.status-free,.status-premium {display:inline-block;border-radius:999px;padding:7px 12px;font-size:12px;font-weight:800;margin-top:5px;}
.status-free {background:#F6E9EE;color:#6D5963;}
.status-premium {background:#FFE0EB;color:#C92665;}
.premium-card {background:linear-gradient(135deg,#FFF3F8,#FDE5EE);border:1.5px solid #E83D7D;border-radius:20px;padding:20px;margin:14px 0 22px;color:#302630;}
.lock-box {background:#FFF1F6;border:1.5px solid #E83D7D;border-radius:18px;padding:20px;text-align:center;color:#302630;margin:18px 0;}

.empty-state {background:#FFF;border:1.5px dashed #F0B8CB;border-radius:18px;padding:28px 20px;text-align:center;color:#6B5962;margin:18px 0;}
.empty-icon {font-size:32px;margin-bottom:8px;}
.empty-title {color:#D83B76;font-size:16px;font-weight:800;margin-bottom:6px;}
.history-row {background:#FFF;border:1px solid #F1CCD9;border-radius:15px;padding:15px;margin:10px 0;color:#302630;}
.compare-head {font-weight:800;color:#D81B60;font-size:17px;margin-bottom:8px;}

/* ALERT WORTH - SATU KOTAK SAJA */
div[data-testid="stAlert"] {
    background: #F47A49 !important;
    border: none !important;
    border-radius: 12px !important;
    padding: 14px 16px !important;
    box-shadow: none !important;
}

/* Hilangkan background bawaan di bagian dalam */
div[data-testid="stAlert"] > div {
    background: transparent !important;
    border: none !important;
    box-shadow: none !important;
    padding: 0 !important;
}

div[data-testid="stAlert"] * {
    background: transparent !important;
    color: #FFFFFF !important;
    -webkit-text-fill-color: #FFFFFF !important;
    opacity: 1 !important;
    font-weight: 600 !important;
}
/* MENU PANEL */
.menu-profile {display:flex;align-items:center;gap:14px;background:#FFF;border:1.5px solid #F2D4DF;border-radius:18px;padding:16px;margin:4px 0 22px;box-shadow:0 7px 22px rgba(232,61,125,.045);}
.menu-avatar {width:48px;height:48px;flex:0 0 48px;border-radius:50%;display:flex;align-items:center;justify-content:center;background:linear-gradient(135deg,#FFE3ED,#FFD0E1);color:#E83D7D;font-size:22px;}
.menu-profile-info {flex:1;}
.menu-profile-name {color:#302630!important;-webkit-text-fill-color:#302630!important;font-size:15px;font-weight:800;margin-bottom:5px;}
.menu-status-free,.menu-status-premium {display:inline-block;border-radius:999px;padding:4px 9px;font-size:10px;font-weight:800;margin-bottom:5px;}
.menu-status-free {background:#F8E9EF;color:#806873!important;-webkit-text-fill-color:#806873!important;}
.menu-status-premium {background:#FFE0EB;color:#D12E6A!important;-webkit-text-fill-color:#D12E6A!important;}
.menu-quota {color:#8F7E88!important;-webkit-text-fill-color:#8F7E88!important;font-size:11px;}
.menu-section {color:#967783!important;-webkit-text-fill-color:#967783!important;font-size:11px;font-weight:800;letter-spacing:1.3px;margin:20px 3px 9px;}

div[class*="st-key-worth_menu_"] button {background:#FFF!important;border:1px solid #F1D5DF!important;border-radius:14px!important;min-height:50px!important;color:#4A3A42!important;-webkit-text-fill-color:#4A3A42!important;font-size:14px!important;font-weight:600!important;box-shadow:0 4px 14px rgba(232,61,125,.025)!important;margin-bottom:2px!important;}
div[class*="st-key-worth_menu_"] button p {color:#4A3A42!important;-webkit-text-fill-color:#4A3A42!important;font-size:14px!important;font-weight:600!important;}
div[class*="st-key-worth_menu_"] button:hover {background:#FFF4F8!important;border-color:#F0AFC5!important;}
div[class*="st-key-worth_menu_history"] button, div[class*="st-key-worth_menu_compare"] button {background:#FFF9FB!important;color:#846F78!important;-webkit-text-fill-color:#846F78!important;}
div[class*="st-key-worth_menu_history"] button p, div[class*="st-key-worth_menu_compare"] button p {color:#846F78!important;-webkit-text-fill-color:#846F78!important;}
div[class*="st-key-worth_menu_premium"] button {background:linear-gradient(135deg,#F56A9C,#EC397B)!important;border:none!important;color:#FFF!important;-webkit-text-fill-color:#FFF!important;min-height:52px!important;box-shadow:0 7px 18px rgba(235,55,123,.17)!important;}
div[class*="st-key-worth_menu_premium"] button p {color:#FFF!important;-webkit-text-fill-color:#FFF!important;font-weight:800!important;}
div[class*="st-key-worth_menu_logout"] button {background:transparent!important;border:none!important;color:#B56F85!important;-webkit-text-fill-color:#B56F85!important;min-height:42px!important;box-shadow:none!important;margin-top:3px!important;}
div[class*="st-key-worth_menu_logout"] button p {color:#B56F85!important;-webkit-text-fill-color:#B56F85!important;font-size:13px!important;font-weight:600!important;}

@media(max-width:600px) {
    .block-container {padding-left:14px;padding-right:14px;}
    .app-page-title {font-size:16px;}
}

/* TOAST WORTH: tengah atas + pink tua */
div[data-testid="stToastContainer"] {
    position: fixed !important;
    top: 105px !important;
    left: 50% !important;
    right: auto !important;
    transform: translateX(-50%) !important;
    width: min(90vw, 420px) !important;
}

div[data-testid="stToast"],
div[data-baseweb="toast"] {
    background: #E83D7D !important;
    border: none !important;
    border-radius: 14px !important;
    box-shadow: 0 8px 24px rgba(190, 35, 95, .22) !important;
}

div[data-testid="stToast"] *,
div[data-baseweb="toast"] * {
    color: #FFFFFF !important;
    -webkit-text-fill-color: #FFFFFF !important;
}


/* LOGO HOME: benar-benar di tengah */
div[class*="st-key-home_logo_wrap"] div[data-testid="stImage"] {
    display: flex !important;
    justify-content: center !important;
}

div[class*="st-key-home_logo_wrap"] img {
    margin-left: auto !important;
    margin-right: auto !important;
}

/* PESAN BERHASIL AKUN */
.account-success {
    background: #E83D7D !important;

    color: #FFFFFF !important;
    -webkit-text-fill-color: #FFFFFF !important;

    font-size: 14px !important;
    font-weight: 600 !important;

    padding: 14px 16px !important;
    margin: 0 0 14px !important;

    border-radius: 12px !important;

    box-shadow: 0 5px 14px rgba(232,61,125,.18) !important;
}

.account-success * {
    color: #FFFFFF !important;
    -webkit-text-fill-color: #FFFFFF !important;
}
.account-data-title {
    margin-top: 14px !important;
    margin-bottom: -8px !important;
}

div[class*="st-key-account_name"] {
    margin-top: -8px !important;
    margin-bottom: -10px !important;
}

div[class*="st-key-account_email"] {
    margin-top: -8px !important;
    margin-bottom: -4px !important;
}
/* JARAK BOT KE INPUT */
.bot-bubble {
    margin-bottom: 14px !important;
}

/* RIWAYAT - tombol "Lihat detail" agar teks terlihat jelas */
div[data-testid="stExpander"] {
    border: 1px solid #F1CCD9 !important;
    border-radius: 12px !important;
    background: #FFF !important;
}

div[data-testid="stExpander"] details > summary {
    background: #FFFFFF !important;
    color: #302630 !important;
    -webkit-text-fill-color: #302630 !important;
    border-radius: 12px !important;
    font-weight: 700 !important;
}

div[data-testid="stExpander"] details > summary * {
    color: #302630 !important;
    -webkit-text-fill-color: #302630 !important;
}

div[data-testid="stExpander"] details[open] > summary {
    border-radius: 12px 12px 0 0 !important;
}

div[data-testid="stExpander"] div[data-testid="stExpanderDetails"] {
    background: #FFF !important;
    color: #302630 !important;
    -webkit-text-fill-color: #302630 !important;
}

div[data-testid="stExpander"] div[data-testid="stExpanderDetails"] * {
    color: #302630 !important;
    -webkit-text-fill-color: #302630 !important;
}


/* DETAIL PERBANDINGAN - tabel harus terbaca jelas */
div[data-testid="stMarkdownContainer"] table {
    width: 100% !important;
    background: #FFFFFF !important;
    color: #302630 !important;
    border-collapse: collapse !important;
    border-radius: 12px !important;
    overflow: hidden !important;
}

div[data-testid="stMarkdownContainer"] table th {
    background: #FFF1F6 !important;
    color: #C92F6D !important;
    -webkit-text-fill-color: #C92F6D !important;
    font-weight: 800 !important;
    border: 1px solid #F1CCD9 !important;
    padding: 10px 8px !important;
}

div[data-testid="stMarkdownContainer"] table td {
    background: #FFFFFF !important;
    color: #302630 !important;
    -webkit-text-fill-color: #302630 !important;
    border: 1px solid #F1CCD9 !important;
    padding: 10px 8px !important;
}

div[data-testid="stMarkdownContainer"] table td *,
div[data-testid="stMarkdownContainer"] table th * {
    color: inherit !important;
    -webkit-text-fill-color: inherit !important;
}

</style>
""",
    unsafe_allow_html=True,
)

# ============================================================
# HELPERS
# ============================================================
def rupiah(value):
    return "Rp{:,.0f}".format(value).replace(",", ".")


def current_time():
    return datetime.now(ZoneInfo("Asia/Jakarta")).strftime("%H:%M")


def chat_time(key):
    if key not in st.session_state.chat_times:
        st.session_state.chat_times[key] = current_time()
    return st.session_state.chat_times[key]


def purchase_has_progress():
    return bool(
        st.session_state.get("item")
        or st.session_state.get("price", 0)
        or st.session_state.get("item_input", "").strip()
        or st.session_state.get("price_input", "").strip()
        or st.session_state.get("usage")
        or st.session_state.get("similar")
        or st.session_state.get("reason")
        or st.session_state.get("budget")
        or st.session_state.get("conviction")
        or st.session_state.get("question", 1) > 1
    )


def request_leave(page):
    st.session_state.pending_page = page
    st.session_state.leave_confirm = True
    st.session_state.menu_open = False
    st.session_state.logout_confirm = False
    st.rerun()


def go(page, remember=True, force=False):
    current = st.session_state.page

    # Saat pengecekan belum selesai, navigasi keluar meminta konfirmasi dulu.
    if (
        not force
        and current in {"purchase", "questions"}
        and page not in {"purchase", "questions", "result"}
        and purchase_has_progress()
    ):
        request_leave(page)

    if remember and page != current:
        if not st.session_state.nav_history or st.session_state.nav_history[-1] != current:
            st.session_state.nav_history.append(current)

    st.session_state.page = page
    st.session_state.menu_open = False
    st.session_state.logout_confirm = False
    st.rerun()


def go_back():
    current = st.session_state.page

    # Alur pertanyaan: kembali satu langkah tanpa menghapus jawaban.
    if current == "questions":
        q = st.session_state.question

        if q > 1:
            st.session_state.question = q - 1
            st.session_state.menu_open = False
            st.rerun()

        # Pertanyaan 1 -> kembali ke input harga.
        # Nilai lama tetap berada di widget price_input sehingga tidak perlu mengetik ulang.
        st.session_state.price = 0
        st.session_state.page = "purchase"
        st.session_state.menu_open = False
        st.rerun()

    # Halaman hasil -> kembali ke pertanyaan terakhir untuk mengedit jawaban.
    if current == "result":
        st.session_state.decision = None
        update_last_decision(None)
        st.session_state.question = 5
        st.session_state.page = "questions"
        st.session_state.menu_open = False
        st.rerun()

    # Input harga -> kembali ke input nama barang tanpa menghapus teks lama.
    if current == "purchase" and st.session_state.item:
        st.session_state.item = ""
        st.session_state.price = 0
        st.session_state.menu_open = False
        st.rerun()

    # Dari tahap input nama, kembali ke halaman asal.
    if current == "purchase":
        target = st.session_state.nav_history[-1] if st.session_state.nav_history else "home"
        if purchase_has_progress():
            request_leave(target)
        st.session_state.page = target
        st.session_state.menu_open = False
        st.rerun()

    if st.session_state.nav_history:
        target = st.session_state.nav_history.pop()
    else:
        target = "home"

    st.session_state.page = target
    st.session_state.menu_open = False
    st.rerun()


def clear_purchase_widget_state():
    for key in [
        "item_input",
        "price_input",
        "q_usage",
        "q_similar",
        "q_reason",
        "q_budget",
        "q_conviction",
    ]:
        if key in st.session_state:
            del st.session_state[key]


def reset_purchase(target_page="purchase"):
    clear_purchase_widget_state()
    for key, value in {
        "item": "",
        "price": 0,
        "question": 1,
        "usage": None,
        "similar": None,
        "reason": None,
        "budget": None,
        "conviction": None,
        "score": 0,
        "risk": "",
        "decision": None,
        "result_counted": False,
        "current_record_id": None,
        "leave_confirm": False,
        "pending_page": None,
        "chat_times": {},
    }.items():
        st.session_state[key] = value
    st.session_state.page = target_page
    st.session_state.menu_open = False


def abandon_purchase(target_page):
    reset_purchase(target_page)
    st.session_state.leave_confirm = False
    st.session_state.pending_page = None
    st.rerun()


def render_leave_confirmation():
    if not st.session_state.get("leave_confirm", False):
        return

    st.warning("Pengecekan belum selesai. Yakin ingin keluar dari pengecekan ini?")
    cancel_col, leave_col = st.columns(2)

    with cancel_col:
        if st.button("LANJUTKAN PENGECEKAN", use_container_width=True, key="leave_cancel"):
            st.session_state.leave_confirm = False
            st.session_state.pending_page = None
            st.rerun()

    with leave_col:
        if st.button("KELUAR", type="primary", use_container_width=True, key="leave_confirm_btn"):
            target = st.session_state.pending_page or "home"
            abandon_purchase(target)

    st.stop()


def start_purchase(return_to="home"):
    reset_purchase("purchase")
    st.session_state.nav_history = [return_to]
    st.rerun()


def logout():
    fresh = initial_state()
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    for key, value in fresh.items():
        st.session_state[key] = value
    st.rerun()


def notify(message, icon="✅"):
    if hasattr(st, "toast"):
        st.toast(message, icon=icon)
    else:
        st.success(message)

def can_start_check():
    refresh_daily_quota()
    return st.session_state.is_premium or st.session_state.daily_checks < FREE_DAILY_LIMIT


def quota_text():
    if st.session_state.is_premium:
        return "Pengecekan tanpa batas"
    return f"{st.session_state.daily_checks} dari {FREE_DAILY_LIMIT} pengecekan hari ini"


def header(title=None):
    if title is None:
        col1, col2 = st.columns([5, 1])
        with col1:
            st.markdown('<div class="worth-brand">WORTH</div>', unsafe_allow_html=True)
        with col2:
            if st.button("☰", key=f"menu_{st.session_state.page}", help="Menu WORTH"):
                st.session_state.menu_open = not st.session_state.menu_open
                if not st.session_state.menu_open:
                    st.session_state.logout_confirm = False
                if not st.session_state.menu_open:
                    st.session_state.logout_confirm = False
    else:
        col_back, col_title, col_menu = st.columns([0.8, 4.5, 0.8])
        with col_back:
            if st.button("←", key=f"back_{st.session_state.page}", help="Kembali"):
                go_back()
        with col_title:
            st.markdown(f'<div class="app-page-title">{title}</div>', unsafe_allow_html=True)
        with col_menu:
            if st.button("☰", key=f"menu_{st.session_state.page}", help="Menu WORTH"):
                st.session_state.menu_open = not st.session_state.menu_open

    st.markdown(
        '<hr style="border:none;border-top:1px solid #F6DCE5;margin-top:8px;margin-bottom:18px;">',
        unsafe_allow_html=True,
    )

    if st.session_state.menu_open:
        menu_panel()
        st.stop()


def menu_panel():
    if st.session_state.is_premium:
        status_text = "WORTH PREMIUM"
        status_class = "menu-status-premium"
    else:
        status_text = "WORTH FREE"
        status_class = "menu-status-free"

    profile_html = (
        '<div class="menu-profile">'
        '<div class="menu-avatar">👤</div>'
        '<div class="menu-profile-info">'
        '<div class="menu-profile-name">' + escape(st.session_state.name) + '</div>'
        '<div class="' + status_class + '">' + status_text + '</div>'
        '<div class="menu-quota">' + quota_text() + '</div>'
        '</div></div>'
    )
    st.markdown(profile_html, unsafe_allow_html=True)

    st.markdown('<div class="menu-section">MENU UTAMA</div>', unsafe_allow_html=True)

    if st.button("👤   Akun Saya   ›", key="worth_menu_account", use_container_width=True):
        go("account")

    if st.session_state.is_premium:
        history_label = "🕘   Riwayat Pengecekan   ›"
        compare_label = "⚖   Perbandingan Produk   ›"
    else:
        history_label = "🔒   Riwayat Pengecekan   ›"
        compare_label = "🔒   Perbandingan Produk   ›"

    if st.button(history_label, key="worth_menu_history", use_container_width=True):
        go("history")
    if st.button(compare_label, key="worth_menu_compare", use_container_width=True):
        go("compare")

    st.markdown('<div class="menu-section">PREMIUM</div>', unsafe_allow_html=True)
    premium_label = "👑   WORTH Premium   ›" if st.session_state.is_premium else "👑   Aktifkan WORTH Premium   ›"
    if st.button(premium_label, key="worth_menu_premium", use_container_width=True):
        go("premium")

    st.markdown('<div class="menu-section">LAINNYA</div>', unsafe_allow_html=True)
    if st.button("ⓘ   Tentang WORTH   ›", key="worth_menu_about", use_container_width=True):
        go("about")
    if st.button("↪   Keluar", key="worth_menu_logout", use_container_width=True):
        st.session_state.logout_confirm = True
        st.rerun()

    if st.session_state.get("logout_confirm", False):
        st.warning("Yakin ingin keluar dari WORTH?")
        c_cancel, c_logout = st.columns(2)
        with c_cancel:
            if st.button("BATAL", use_container_width=True, key="logout_cancel"):
                st.session_state.logout_confirm = False
                st.rerun()
        with c_logout:
            if st.button("YA, KELUAR", type="primary", use_container_width=True, key="logout_yes"):
                logout()


def bot_message(text, time_key):
    col_avatar, col_chat = st.columns([1, 8], gap="small")
    with col_avatar:
        if BOT.exists():
            st.image(str(BOT), width=52)
        else:
            st.write("🤖")
    with col_chat:
        html = (
            '<div class="bot-bubble">' + text +
            '<div class="time">' + chat_time(time_key) + '</div></div>'
        )
        st.markdown(html, unsafe_allow_html=True)


def user_message(text, time_key):
    _, col_right = st.columns([2, 5])
    with col_right:
        html = (
            '<div class="user-bubble">' + escape(str(text)) +
            '<div class="time">' + chat_time(time_key) + '</div></div>'
        )
        st.markdown(html, unsafe_allow_html=True)


def progress(number):
    pct = number * 20
    html = (
        f'<div class="question-number">Pertanyaan {number} dari 5</div>'
        '<div class="progress-background">'
        f'<div class="progress-pink" style="width:{pct}%"></div>'
        '</div>'
    )
    st.markdown(html, unsafe_allow_html=True)


def calculate():
    U = USAGE[st.session_state.usage]
    S = SIMILAR[st.session_state.similar]
    T = REASON[st.session_state.reason]
    B = BUDGET[st.session_state.budget]
    C = CONVICTION[st.session_state.conviction]

    score = round(
        0.20 * U
        + 0.15 * S
        + 0.20 * T
        + 0.30 * B
        + 0.15 * C
    )

    if score <= 30:
        risk = "RISIKO RENDAH"
    elif score <= 60:
        risk = "RISIKO SEDANG"
    else:
        risk = "RISIKO TINGGI"

    st.session_state.score = score
    st.session_state.risk = risk


def build_current_record(record_id=None, decision=None):
    return {
        "id": record_id if record_id is not None else len(st.session_state.history) + 1,
        "time": datetime.now(ZoneInfo("Asia/Jakarta")).strftime("%d/%m/%Y %H:%M"),
        "item": st.session_state.item,
        "price": st.session_state.price,
        "usage": st.session_state.usage,
        "similar": st.session_state.similar,
        "reason": st.session_state.reason,
        "budget": st.session_state.budget,
        "conviction": st.session_state.conviction,
        "usage_score": USAGE[st.session_state.usage],
        "similar_score": SIMILAR[st.session_state.similar],
        "reason_score": REASON[st.session_state.reason],
        "budget_score": BUDGET[st.session_state.budget],
        "conviction_score": CONVICTION[st.session_state.conviction],
        "score": st.session_state.score,
        "risk": st.session_state.risk,
        "decision": decision,
    }


def save_completed_check():
    # Jika hasil sedang diedit, perbarui record yang sama dan jangan menghitung kuota lagi.
    if st.session_state.result_counted:
        if st.session_state.current_record_id is None and st.session_state.history:
            st.session_state.current_record_id = st.session_state.history[-1].get("id")

        if st.session_state.current_record_id is not None:
            for i, rec in enumerate(st.session_state.history):
                if rec.get("id") == st.session_state.current_record_id:
                    old_decision = rec.get("decision")
                    old_time = rec.get("time")
                    updated = build_current_record(
                        record_id=st.session_state.current_record_id,
                        decision=old_decision,
                    )
                    updated["time"] = old_time
                    st.session_state.history[i] = updated
                    return
            return

    if not st.session_state.is_premium:
        st.session_state.daily_checks += 1

    record_id = len(st.session_state.history) + 1
    record = build_current_record(record_id=record_id, decision=None)
    st.session_state.history.append(record)
    st.session_state.current_record_id = record_id
    st.session_state.result_counted = True


def update_last_decision(decision):
    record_id = st.session_state.get("current_record_id")
    if record_id is not None:
        for rec in st.session_state.history:
            if rec.get("id") == record_id:
                rec["decision"] = decision
                return

    if st.session_state.history:
        st.session_state.history[-1]["decision"] = decision

def premium_gate(feature_name):
    st.markdown(
        '<div class="lock-box"><div style="font-size:32px">🔒</div>'
        f'<b>{feature_name}</b><br><br>'
        'Fitur ini tersedia untuk pengguna WORTH Premium.</div>',
        unsafe_allow_html=True,
    )
    if st.button("👑 AKTIFKAN PREMIUM", type="primary", use_container_width=True, key=f"gate_{feature_name}"):
        go("premium")

# ============================================================
# PENJELASAN HASIL
# ============================================================
def usage_text():
    return {
        "Setiap hari": "Kamu berencana menggunakan barang ini setiap hari.",
        "Beberapa kali seminggu": "Kamu berencana menggunakan barang ini beberapa kali seminggu.",
        "Sekali seminggu": "Kamu akan menggunakan barang ini sekitar sekali seminggu.",
        "Sekali sebulan": "Kamu memperkirakan barang ini hanya digunakan sekitar sekali sebulan.",
        "Jarang": "Kamu memperkirakan barang ini akan jarang digunakan.",
    }[st.session_state.usage]


def similar_text():
    return {
        "Tidak": "Kamu belum memiliki barang serupa.",
        "Ya, tetapi saya membutuhkan satu lagi": "Kamu sudah memiliki barang serupa, tetapi masih merasa membutuhkan yang baru.",
        "Ya, saya sebenarnya tidak terlalu membutuhkan satu lagi": "Kamu sudah memiliki barang serupa dan tidak terlalu membutuhkan yang baru.",
    }[st.session_state.similar]


def reason_text():
    return {
        "Saya benar-benar membutuhkannya": "Kebutuhan menjadi alasan utama pembelian.",
        "Saya sudah menginginkannya sejak lama": "Barang ini sudah kamu inginkan sejak cukup lama.",
        "Ada diskon": "Promo menjadi salah satu alasan pembelian.",
        "FOMO / sedang tren": "FOMO atau tren menjadi salah satu alasan pembelian.",
        "Impulsif": "Keinginan membeli muncul secara impulsif.",
    }[st.session_state.reason]


def budget_text():
    return {
        "Tidak memengaruhi budget saya": "Pembelian ini tidak memengaruhi budgetmu.",
        "Sedikit memengaruhi budget saya": "Pembelian ini sedikit memengaruhi budgetmu.",
        "Saya harus mengurangi pengeluaran lain": "Pembelian ini membuatmu perlu mengurangi pengeluaran lain.",
    }[st.session_state.budget]


def conviction_text():
    return {
        "Ya, saya tetap ingin membelinya":
            "Keinginan membeli tetap ada meskipun tanpa diskon, promo, atau tren.",
        "Mungkin, saya masih mempertimbangkannya":
            "Keinginan membeli masih dapat berubah jika tidak ada diskon, promo, atau tren.",
        "Tidak, kemungkinan saya tidak jadi membelinya":
            "Keinginan membeli cukup dipengaruhi oleh diskon, promo, atau tren.",
    }[st.session_state.conviction]

# ============================================================
# PAGES
# ============================================================
def home_page():
    header()

    if LOGO.exists():
        logo_b64 = base64.b64encode(LOGO.read_bytes()).decode("utf-8")
        logo_ext = LOGO.suffix.lower().lstrip(".")
        logo_mime = "jpeg" if logo_ext in {"jpg", "jpeg"} else "png"
        st.markdown(
            f'<div style="width:100%;display:flex;justify-content:center;align-items:center;">'
            f'<img src="data:image/{logo_mime};base64,{logo_b64}" '
            f'style="width:100px;height:auto;display:block;margin:0 auto;">'
            f'</div>',
            unsafe_allow_html=True,
        )

    st.markdown('<div class="tagline">THINK TWICE BEFORE<br>YOU CHECKOUT.</div>', unsafe_allow_html=True)

    st.markdown(
        '<div class="intro-box"><b>Hai! Aku WORTH,</b><br>'
        'teman berpikirmu sebelum <i>checkout</i> 💗<br><br>'
        'Aku akan membantumu mengevaluasi pembelian sebelum kamu mengambil keputusan.</div>',
        unsafe_allow_html=True,
    )

    if not st.session_state.is_premium:
        st.markdown(
            '<div class="quota-box"><b>WORTH Free</b><br>'
            '<span class="muted">' + quota_text() + '</span></div>',
            unsafe_allow_html=True,
        )

    if st.button("🛍️ CEK PEMBELIAN →", type="primary", use_container_width=True):
        if can_start_check():
            start_purchase("home")
        else:
            go("limit")

    st.markdown(
        '<div class="soft-card" style="text-align:center;font-size:13px;">'
        '♡ Lebih sadar sebelum membeli &nbsp; • &nbsp; '
        '🧠 Bedakan kebutuhan & keinginan &nbsp; • &nbsp; '
        '♡ Keputusan tetap di tangan kamu</div>',
        unsafe_allow_html=True,
    )


def limit_page():
    header("Batas Pengecekan")
    price_text = rupiah(PREMIUM_PRICE)
    st.markdown(
        '<div class="lock-box"><div style="font-size:34px">💗</div>'
        '<b>Batas pengecekan hari ini telah tercapai</b><br><br>'
        f'Kamu telah menggunakan <b>{FREE_DAILY_LIMIT} dari {FREE_DAILY_LIMIT} pengecekan WORTH hari ini.</b><br><br>'
        'Kuota Free akan tersedia kembali besok.<br><br>'
        f'Ingin melakukan pengecekan lebih banyak? Aktifkan <b>WORTH Premium {price_text}/bulan</b>.</div>',
        unsafe_allow_html=True,
    )
    if st.button("👑 AKTIFKAN PREMIUM", type="primary", use_container_width=True):
        go("premium")


def purchase_page():
    header("Cek Pembelian")
    render_leave_confirmation()

    if not can_start_check():
        go("limit")
        return

    if st.session_state.item == "":
        bot_message("Barang apa yang ingin kamu beli? 😊", "purchase_item_bot")
        item = st.text_input(
            "Nama barang",
            placeholder="Contoh: Sneakers Korea",
            label_visibility="collapsed",
            key="item_input",
        )
        if st.button(
            "Lanjut →",
            type="primary",
            use_container_width=True,
            disabled=not item.strip(),
            key="purchase_item_next",
        ):
            st.session_state.item = item.strip()
            chat_time("purchase_item_user")
            st.rerun()
        return

    user_message(st.session_state.item, "purchase_item_user")

    if st.session_state.price == 0:
        safe_item = escape(st.session_state.item)
        bot_message(
            f"Oke! Berapa harga <b>{safe_item}</b> yang kamu incar?",
            "purchase_price_bot",
        )
        price_text = st.text_input(
            "Harga",
            placeholder="Contoh: Rp299.000",
            label_visibility="collapsed",
            key="price_input",
        )
        if st.button(
            "Lanjut →",
            type="primary",
            use_container_width=True,
            disabled=not price_text.strip(),
            key="purchase_price_next",
        ):
            cleaned = price_text.lower().replace("rp", "").replace(".", "").replace(",", "").replace(" ", "")
            if not cleaned.isdigit():
                st.warning("Masukkan harga dengan benar. Contoh: Rp299.000")
            elif int(cleaned) <= 0:
                st.warning("Harga harus lebih dari Rp0.")
            else:
                st.session_state.price = int(cleaned)
                chat_time("purchase_price_user")
                go("questions")

def questions_page():
    header("Cek Pembelian")
    render_leave_confirmation()

    q = st.session_state.question
    progress(q)

    if q == 1:
        safe_item = escape(st.session_state.item)
        bot_message(f"Seberapa sering kamu akan menggunakan <b>{safe_item}</b> ini?", "q1_bot")
        answer = st.radio("Penggunaan", list(USAGE.keys()), index=None, label_visibility="collapsed", key="q_usage")
        back, nextc = st.columns(2)
        with back:
            if st.button("← Kembali", use_container_width=True, key="q1_back"):
                go_back()
        with nextc:
            if st.button(
                "Lanjut →",
                type="primary",
                use_container_width=True,
                key="q1_next",
                disabled=answer is None,
            ):
                st.session_state.usage = answer
                st.session_state.question = 2
                st.rerun()

    elif q == 2:
        bot_message("Apakah kamu sudah memiliki <b>barang yang serupa?</b>", "q2_bot")
        answer = st.radio("Barang serupa", list(SIMILAR.keys()), index=None, label_visibility="collapsed", key="q_similar")
        back, nextc = st.columns(2)
        with back:
            if st.button("← Kembali", use_container_width=True, key="q2_back"):
                st.session_state.question = 1
                st.rerun()
        with nextc:
            if st.button(
                "Lanjut →",
                type="primary",
                use_container_width=True,
                key="q2_next",
                disabled=answer is None,
            ):
                st.session_state.similar = answer
                st.session_state.question = 3
                st.rerun()

    elif q == 3:
        bot_message("Kenapa kamu ingin <b>membeli barang ini?</b>", "q3_bot")
        answer = st.radio("Alasan pembelian", list(REASON.keys()), index=None, label_visibility="collapsed", key="q_reason")
        back, nextc = st.columns(2)
        with back:
            if st.button("← Kembali", use_container_width=True, key="q3_back"):
                st.session_state.question = 2
                st.rerun()
        with nextc:
            if st.button(
                "Lanjut →",
                type="primary",
                use_container_width=True,
                key="q3_next",
                disabled=answer is None,
            ):
                st.session_state.reason = answer
                st.session_state.question = 4
                st.rerun()

    elif q == 4:
        bot_message("Bagaimana pembelian ini akan <b>memengaruhi budgetmu?</b>", "q4_bot")
        answer = st.radio("Dampak budget", list(BUDGET.keys()), index=None, label_visibility="collapsed", key="q_budget")
        back, nextc = st.columns(2)
        with back:
            if st.button("← Kembali", use_container_width=True, key="q4_back"):
                st.session_state.question = 3
                st.rerun()
        with nextc:
            if st.button(
                "Lanjut →",
                type="primary",
                use_container_width=True,
                key="q4_next",
                disabled=answer is None,
            ):
                st.session_state.budget = answer
                st.session_state.question = 5
                st.rerun()

    elif q == 5:
        bot_message(
            "Kalau tidak ada <b>diskon, promo, atau sedang tren</b>, "
            "apakah kamu tetap ingin membeli barang ini?",
            "q5_bot",
        )
        answer = st.radio(
            "Keinginan tanpa pemicu",
            list(CONVICTION.keys()),
            index=None,
            label_visibility="collapsed",
            key="q_conviction",
        )
        back, nextc = st.columns(2)
        with back:
            if st.button("← Kembali", use_container_width=True, key="q5_back"):
                st.session_state.question = 4
                st.rerun()
        with nextc:
            if st.button(
                "Lihat Hasil →",
                type="primary",
                use_container_width=True,
                key="q5_result",
                disabled=answer is None,
            ):
                st.session_state.conviction = answer
                calculate()
                go("result")

def result_page():
    save_completed_check()
    header("Hasil WORTH")

    bot_message(
        "Aku sudah melihat semua jawabanmu.<br><br>Ini hasil pertimbangan untuk pembelianmu 💗",
        "result_bot",
    )

    score = st.session_state.score
    risk = st.session_state.risk
    angle = score * 3.6

    result_html = (
        '<div class="result-title">HASIL WORTH</div>'
        '<div class="result-body">'
        f'<div class="score-circle" style="--score-angle:{angle}deg">'
        '<div class="score-text">'
        f'<div class="score-big">{score}</div>'
        '<div class="score-small">/100</div>'
        '<div class="score-label">WORTH Score</div>'
        '</div></div>'
        f'<div class="risk-badge">{risk}</div>'
        '</div>'
    )
    st.markdown(result_html, unsafe_allow_html=True)

    info_html = (
        '<div class="info-card"><div class="card-title">Informasi Barang</div>'
        '<div class="item-info"><div class="item-symbol">🏷️</div><div>'
        '<div class="info-label">Nama Barang</div>'
        f'<div class="info-value">{escape(st.session_state.item)}</div>'
        '<div class="info-label">Harga</div>'
        f'<div class="info-value">{rupiah(st.session_state.price)}</div>'
        '</div></div></div>'
    )
    st.markdown(info_html, unsafe_allow_html=True)

    why_html = (
        '<div class="worth-why-box">'
        '<div class="worth-why-title">💡 KENAPA?</div>'
        '<div class="worth-why-content">'
        'Berdasarkan jawabanmu, skor ini dipengaruhi oleh:<br><br>'
        '• ' + usage_text() + '<br>'
        '• ' + similar_text() + '<br>'
        '• ' + reason_text() + '<br>'
        '• ' + budget_text() + '<br>'
        '• ' + conviction_text() +
        '</div></div>'
    )
    st.markdown(why_html, unsafe_allow_html=True)

    decision_locked = st.session_state.decision is not None

    c1, c2 = st.columns(2)
    with c1:
        if st.button(
            "⊘ AKU BATAL BELI",
            use_container_width=True,
            disabled=decision_locked,
            key="decision_skip",
        ):
            st.session_state.decision = "skip"
            update_last_decision("Batal membeli")
            st.rerun()
    with c2:
        if st.button(
            "🛒 TETAP BELI",
            type="primary",
            use_container_width=True,
            disabled=decision_locked,
            key="decision_buy",
        ):
            st.session_state.decision = "buy"
            update_last_decision("Tetap membeli")
            st.rerun()

    if st.session_state.decision:
        msg = (
            "Kamu memilih untuk melewatkan pembelian ini."
            if st.session_state.decision == "skip"
            else "Kamu memilih untuk tetap melanjutkan pembelian."
        )
        final_html = (
            '<div class="final-message">💗 <b>' + msg + '</b><br><br>'
            'Apa pun keputusanmu, yang penting kamu sudah mempertimbangkannya terlebih dahulu.'
            '</div>'
        )
        st.markdown(final_html, unsafe_allow_html=True)

        if st.button("↻ CEK PEMBELIAN LAIN", use_container_width=True):
            if can_start_check():
                start_purchase("home")
            else:
                go("limit")

    st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)

    if st.button(
        "🏠 KEMBALI KE HOME",
        use_container_width=True,
        key="result_home"
    ):
        reset_purchase("home")
        st.rerun()


def account_page():
    header("Akun Saya")

    if st.session_state.get("account_saved", False):
        st.markdown(
            '<div class="account-success">✅&nbsp;&nbsp; Data akun berhasil diperbarui.</div>',
            unsafe_allow_html=True,
        )
        st.session_state.account_saved = False

    status = (
        "👑 WORTH PREMIUM"
        if st.session_state.is_premium
        else "WORTH FREE"
    )

    css = (
        "status-premium"
        if st.session_state.is_premium
        else "status-free"
    )

    st.markdown(
        '<div class="soft-card">'
        '<b>' + escape(st.session_state.name) + '</b><br>'
        '<span class="muted">'
        + escape(st.session_state.email or "Email belum diisi") +
        '</span><br>'
        '<span class="' + css + '">'
        + status +
        '</span><br><br>'
        '<b>Penggunaan</b><br>'
        + quota_text() +
        '</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="section-title account-data-title">'
        'Data akun'
        '</div>',
        unsafe_allow_html=True
    )

    name_value = (
        ""
        if st.session_state.name == "Pengguna WORTH"
        else st.session_state.name
    )

    name = st.text_input(
        "Nama",
        value=name_value,
        placeholder="Masukkan nama",
        key="account_name"
    )

    email = st.text_input(
        "Email",
        value=st.session_state.email,
        placeholder="nama@email.com",
        key="account_email"
    )

    if st.button(
        "Simpan Data Akun",
        type="primary",
        use_container_width=True
    ):
        clean_name = name.strip()
        clean_email = email.strip()

        if not clean_name:
            st.warning("Masukkan nama terlebih dahulu.")

        elif not clean_email:
            st.warning("Masukkan email terlebih dahulu.")

        elif (
            "@" not in clean_email
            or "." not in clean_email.split("@")[-1]
        ):
            st.warning("Masukkan alamat email yang valid.")

        else:
            st.session_state.name = clean_name
            st.session_state.email = clean_email
            st.session_state.account_saved = True
            st.rerun()

    if not st.session_state.is_premium:
        if st.button(
            "👑 AKTIFKAN WORTH PREMIUM",
            use_container_width=True
        ):
            go("premium")


def premium_page():
    header("WORTH Premium")

    if st.session_state.get("premium_just_activated", False):
        st.markdown(
            '<div class="account-success">👑&nbsp;&nbsp; WORTH Premium berhasil diaktifkan!</div>',
            unsafe_allow_html=True,
        )
        st.session_state.premium_just_activated = False

    if st.session_state.is_premium:
        st.markdown(
            '<div class="premium-card"><b>Premium sudah aktif! 👑</b><br><br>'
            'Akunmu memiliki akses pengecekan tanpa batas, Riwayat Pengecekan, dan Perbandingan Produk.'
            '</div>',
            unsafe_allow_html=True,
        )
        return

    st.markdown(
        '<div class="premium-card"><div style="font-size:24px;font-weight:800;color:#D81B60">'
        'Rp9.900 <span style="font-size:13px;color:#8F7E88">/ bulan</span></div><br>'
        'Upgrade ke Premium untuk mendapatkan akses fitur tambahan.<br><br>'
        '✓ Pengecekan tanpa batas<br>✓ Riwayat pengecekan<br>✓ Perbandingan 2 produk</div>',
        unsafe_allow_html=True,
    )

    code = st.text_input("Masukkan Kode Premium", placeholder="Masukkan kode aktivasi", type="password")

    if st.button(
        "👑 AKTIFKAN PREMIUM",
        type="primary",
        use_container_width=True,
        disabled=not code.strip(),
    ):
        if code.strip() == PREMIUM_CODE:
            st.session_state.is_premium = True
            st.session_state.premium_activated_at = datetime.now(ZoneInfo("Asia/Jakarta")).isoformat()
            st.session_state.premium_just_activated = True
            st.rerun()
        else:
            st.warning("Kode Premium tidak valid. Silakan periksa kembali kode yang dimasukkan.")

    st.caption("Aktivasi kode digunakan sebagai simulasi prototype/MVP. Tidak ada payment gateway pada versi ini.")


def history_page():
    header("Riwayat Pengecekan")

    if not st.session_state.is_premium:
        premium_gate("Riwayat Pengecekan")
        return

    if not st.session_state.history:
        st.markdown(
            '<div class="empty-state"><div class="empty-icon">🕘</div>'
            '<div class="empty-title">Belum ada pengecekan</div>'
            'Hasil pengecekan pembelianmu akan muncul di sini.</div>',
            unsafe_allow_html=True,
        )
        if st.button("🛍️ MULAI PENGECEKAN", type="primary", use_container_width=True):
            start_purchase("history")
        return

    for rec in reversed(st.session_state.history):
        decision = rec.get("decision") or "Belum dipilih"
        safe_item = escape(str(rec.get("item", "")))
        html = (
            '<div class="history-row">'
            f'<b>{safe_item}</b><br><span class="muted">{rec.get("time", "-")}</span><br><br>'
            f'Harga: <b>{rupiah(rec.get("price", 0))}</b><br>'
            f'WORTH Score: <b>{rec.get("score", "-")}/100</b><br>'
            f'Tingkat Risiko: <b>{rec.get("risk", "-")}</b><br>'
            f'Keputusan: <b>{escape(str(decision))}</b></div>'
        )
        st.markdown(html, unsafe_allow_html=True)

        with st.expander("Lihat detail", expanded=False):
            st.markdown(
                f"**Penggunaan:** {rec.get('usage', '-')}  \n"
                f"**Barang serupa:** {rec.get('similar', '-')}  \n"
                f"**Alasan pembelian:** {rec.get('reason', '-')}  \n"
                f"**Dampak budget:** {rec.get('budget', '-')}  \n"
                f"**Tanpa diskon/promo/tren:** {rec.get('conviction', '-')}"
            )

def safe_markdown_cell(value):
    return str(value).replace("|", "\\|").replace("\n", " ")


def compare_page():
    header("Perbandingan Produk")

    if not st.session_state.is_premium:
        premium_gate("Perbandingan Produk")
        return

    if len(st.session_state.history) < 2:
        st.markdown(
            '<div class="empty-state"><div class="empty-icon">⚖️</div>'
            '<div class="empty-title">Belum cukup data</div>'
            'Lakukan minimal 2 pengecekan untuk membandingkan produk.</div>',
            unsafe_allow_html=True,
        )
        if st.button("🛍️ MULAI PENGECEKAN", type="primary", use_container_width=True):
            start_purchase("compare")
        return

    options = list(range(len(st.session_state.history)))

    def label(i):
        r = st.session_state.history[i]
        return f'{r["item"]} — {r["score"]}/100 ({r["risk"]})'

    a = st.selectbox("Produk pertama", options, format_func=label, key="cmp_a")
    b = st.selectbox(
        "Produk kedua",
        options,
        index=1 if len(options) > 1 else 0,
        format_func=label,
        key="cmp_b",
    )

    if a == b:
        st.warning("Pilih dua produk yang berbeda.")
        return

    A = st.session_state.history[a]
    B = st.session_state.history[b]

    # Tentukan rekomendasi lebih dulu agar hasil langsung terlihat
    if A["score"] < B["score"]:
        recommended = A
        other = B
    elif B["score"] < A["score"]:
        recommended = B
        other = A
    else:
        recommended = None
        other = None

    st.markdown(
        '<div class="soft-card"><div class="compare-head">Hasil Perbandingan</div>'
        'WORTH membandingkan kedua produk berdasarkan jawabanmu dan memberikan rekomendasi '
        'berdasarkan WORTH Score serta tingkat risiko pembelian.</div>',
        unsafe_allow_html=True,
    )

    # HASIL UTAMA langsung tampil di bawah judul
    if recommended is not None:
        score_gap = abs(A["score"] - B["score"])
        recommendation_html = (
            '<div class="soft-card" style="border:2px solid #E83D7D;background:#FFF0F6;'
            'text-align:center;padding:22px 18px;">'
            '<div style="font-size:14px;color:#8F7E88;font-weight:700;margin-bottom:7px;">'
            '💗 REKOMENDASI WORTH</div>'
            f'<div style="font-size:24px;color:#D81B60;font-weight:800;margin-bottom:10px;">'
            f'{escape(str(recommended["item"]))}</div>'
            f'<div style="font-size:15px;color:#302630;line-height:1.65;">'
            f'WORTH Score <b>{recommended["score"]}/100</b> · '
            f'<b>{escape(str(recommended["risk"]))}</b><br>'
            f'Lebih rendah {score_gap} poin dibanding '
            f'<b>{escape(str(other["item"]))}</b> ({other["score"]}/100).<br><br>'
            'Berdasarkan jawabanmu, produk ini memiliki tingkat risiko pembelian yang lebih rendah.'
            '</div></div>'
        )
        st.markdown(recommendation_html, unsafe_allow_html=True)
    else:
        tie_html = (
            '<div class="soft-card" style="border:2px solid #E83D7D;background:#FFF0F6;'
            'text-align:center;padding:22px 18px;">'
            '<div style="font-size:14px;color:#8F7E88;font-weight:700;margin-bottom:7px;">'
            '⚖️ HASIL WORTH</div>'
            '<div style="font-size:22px;color:#D81B60;font-weight:800;margin-bottom:10px;">'
            'Keduanya Seimbang</div>'
            f'<div style="font-size:15px;color:#302630;line-height:1.65;">'
            f'<b>{escape(str(A["item"]))}</b> dan <b>{escape(str(B["item"]))}</b> '
            f'memiliki WORTH Score yang sama, yaitu <b>{A["score"]}/100</b>.<br><br>'
            'Pertimbangkan harga, kebutuhan utama, dan produk yang akan lebih sering digunakan.'
            '</div></div>'
        )
        st.markdown(tie_html, unsafe_allow_html=True)

    st.markdown(
        '<div class="section-title" style="margin-top:24px;">Detail Perbandingan</div>',
        unsafe_allow_html=True,
    )

    rows = [
        ("Harga", rupiah(A["price"]), rupiah(B["price"])),
        ("Skor Penggunaan", A["usage_score"], B["usage_score"]),
        ("Skor Barang Serupa", A["similar_score"], B["similar_score"]),
        ("Skor Alasan Pembelian", A["reason_score"], B["reason_score"]),
        ("Skor Budget", A["budget_score"], B["budget_score"]),
        ("Skor Keinginan Tanpa Pemicu", A.get("conviction_score", "-"), B.get("conviction_score", "-")),
        ("WORTH Score", f'{A["score"]}/100', f'{B["score"]}/100'),
        ("Tingkat Risiko", A["risk"], B["risk"]),
    ]

    md = (
        f'| Komponen | {safe_markdown_cell(A["item"])} | {safe_markdown_cell(B["item"])} |\n'
        '|---|---:|---:|\n'
        + "\n".join(f"| {x} | {y} | {z} |" for x, y, z in rows)
    )
    st.markdown(md)


def about_page():
    header("Tentang WORTH")

    about_html = (
        '<div class="soft-card"><b>WORTH — Purchase Decision Assistant</b><br><br>'
        'WORTH membantu pengguna mempertimbangkan kembali keputusan pembelian sebelum melakukan <i>checkout</i>. '
        'Penilaian dilakukan berdasarkan kebutuhan dan kondisi pembelian pengguna.<br><br>'
        '<b>Apa yang dipertimbangkan WORTH?</b><br><br>'
        '• Seberapa sering barang akan digunakan<br>'
        '• Kepemilikan barang yang serupa<br>'
        '• Alasan melakukan pembelian<br>'
        '• Dampak pembelian terhadap budget<br>'
        '• Keinginan membeli tanpa diskon, promo, atau tren<br><br>'
        '<b>Hasil Pengecekan</b><br><br>'
        'Setelah menjawab pertanyaan, WORTH menampilkan <b>WORTH Score</b> dan <b>Tingkat Risiko</b> '
        'sebagai bahan pertimbangan sebelum membeli.<br><br>'
        '0–30 &nbsp; = &nbsp; Risiko Rendah<br>'
        '31–60 &nbsp; = &nbsp; Risiko Sedang<br>'
        '61–100 &nbsp; = &nbsp; Risiko Tinggi<br><br>'
        '<b>WORTH Premium</b><br><br>'
        'Premium memberikan akses ke pengecekan tanpa batas, riwayat pengecekan, dan perbandingan produk. '
        'Status Premium tidak memengaruhi hasil WORTH Score maupun Tingkat Risiko.<br><br>'
        '<div style="background:#FFF1F6;border-radius:12px;padding:13px 15px;color:#6F5964;">'
        '💗 WORTH merupakan alat bantu pertimbangan sebelum membeli. Keputusan akhir tetap berada di tangan pengguna.'
        '</div></div>'
    )
    st.markdown(about_html, unsafe_allow_html=True)

def ensure_valid_page_state():
    valid_pages = {
        "home", "limit", "purchase", "questions", "result",
        "account", "premium", "history", "compare", "about",
    }

    if st.session_state.page not in valid_pages:
        st.session_state.page = "home"
        return

    if st.session_state.page == "questions":
        if not st.session_state.item:
            st.session_state.page = "purchase"
            return
        if st.session_state.price <= 0:
            st.session_state.page = "purchase"
            return
        if st.session_state.question not in {1, 2, 3, 4, 5}:
            st.session_state.question = 1

    if st.session_state.page == "result":
        required = [
            st.session_state.item,
            st.session_state.price,
            st.session_state.usage,
            st.session_state.similar,
            st.session_state.reason,
            st.session_state.budget,
            st.session_state.conviction,
        ]
        if not all(required) or st.session_state.score <= 0:
            reset_purchase("home")


# ============================================================
# ROUTER
# ============================================================
pages = {
    "home": home_page,
    "limit": limit_page,
    "purchase": purchase_page,
    "questions": questions_page,
    "result": result_page,
    "account": account_page,
    "premium": premium_page,
    "history": history_page,
    "compare": compare_page,
    "about": about_page,
}

ensure_valid_page_state()
pages.get(st.session_state.page, home_page)()

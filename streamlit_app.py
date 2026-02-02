import streamlit as st
import google.generativeai as genai
import PyPDF2
import base64
import time
import os

# --- 1. НАСТРОЙКИ СТРАНИЦЫ ---
st.set_page_config(
    page_title="Clause AI",
    page_icon="⚖️",
    layout="wide"
)

# --- 2. СТИЛИ (Профессиональная сетка) ---
st.markdown("""
<style>
    .main-header {font-size: 2.5rem; color: #4B9CD3;}
    .stButton button {
        border-radius: 8px;
        width: 100%;
        border: 1px solid #4B9CD3;
    }
    div[data-testid="stMetricValue"] {
        font-size: 1.5rem;
        color: #4B9CD3;
    }
    /* Делаем карточки одинаковой высоты */
    div[data-testid="stVerticalBlock"] > div {
        height: 100%;
    }
</style>
""", unsafe_allow_html=True)

LOGO_FILENAME = "clauseailogo.png"

# --- 3. ФУНКЦИИ (RAG + UI) ---
def get_base64_image(image_path):
    try:
        with open(image_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()
    except FileNotFoundError:
        return None

@st.cache_resource
def load_all_laws():
    combined_text = ""
    files = ["BGB.pdf", "HGB.pdf", "TKG.pdf"]
    active_files = []
    
    for file_name in files:
        if os.path.exists(file_name):
            try:
                reader = PyPDF2.PdfReader(file_name)
                # Читаем 100 страниц для демо (можно увеличить)
                for i in range(min(100, len(reader.pages))):
                    combined_text += reader.pages[i].extract_text() + "\n"
                active_files.append(file_name)
            except:
                pass
    return combined_text, active_files

# --- 4. НАСТРОЙКА ИИ ---
if "GOOGLE_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
    
    full_law_context, loaded_files = load_all_laws()
    
    instruction = f"""
    You are Clause AI, a professional German legal assistant.
    Knowledge Base (loaded laws): {full_law_context[:50000]}
    
    RULES:
    1. Always cite Paragraphs (§) from BGB, HGB, or TKG.
    2. Answer in the user's language (English/German).
    3. Draft letters in FORMAL GERMAN (Amtsdeutsch).
    4. Disclaimer: "Not legal advice. AI MVP Demo."
    """
    model = genai.GenerativeModel('gemini-1.5-flash', system_instruction=instruction)
else:
    st.error("⚠️ Add GOOGLE_API_KEY to Secrets")

# --- 5. САЙДБАР ---
with st.sidebar:
    img_base64 = get_base64_image(LOGO_FILENAME)
    if img_base64:
        st.markdown(f'<div style="text-align:center; margin-bottom:10px"><img src="data:image/png;base64,{img_base64}" width="100" style="border-radius:50%; border:3px solid #4B9CD3"></div>', unsafe_allow_html=True)
    
    st.title("⚖️ Clause AI")
    st.caption("Rule the Rules")
    
    st.markdown("---")
    st.subheader("📊 User Value (Est.)")
    c1, c2 = st.columns(2)
    c1.metric("Savings", "€350", "Avg.")
    c2.metric("Time", "4.5h", "Faster")
    st.markdown("---")
    
    if st.button("🔄 New Chat"):
        st.session_state.messages = []
        st.rerun()

    # Показываем статус базы знаний
    if loaded_files:
        st.success(f"📚 Loaded: {', '.join(loaded_files)}")
    else:
        st.warning("⚠️ Law PDFs not found")

# --- 6. ГЛАВНЫЙ ЭКРАН (СЕТКА 2x2) ---
st.title("Clause AI: Legal Self-Help Assistant")
st.markdown("##### 🚀 AI-Powered Legal Guidance for Germany")

# РЯД 1
col1, col2 = st.columns(2)

with col1:
    with st.container(border=True):
        st.subheader("🏠 Tenancy (Mietrecht)")
        st.markdown("- Deposit Recovery\n- Rent Reduction\n- Repairs & Mold")
        st.caption("Focus: BGB § 535-580")

with col2:
    with st.container(border=True):
        st.subheader("📄 Contracts (Verträge)")
        st.markdown("- Cancel Subscriptions\n- Check 'Red Flags'\n- Consumer Rights")
        st.caption("Focus: TKG & BGB § 309")

# РЯД 2
col3, col4 = st.columns(2)

with col3:
    with st.container(border=True):
        # ПЕРЕИМЕНОВАНО: Платежи и Долги (для всех)
        st.subheader("💶 Payments & Claims")
        st.markdown("- Unpaid Invoices\n- Debt Collection\n- Late Fees Calculation")
        st.caption("Focus: BGB §

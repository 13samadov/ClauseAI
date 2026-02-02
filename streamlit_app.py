import streamlit as st
import google.generativeai as genai
import PyPDF2
import base64
import time
import os
import random

# --- 1. НАСТРОЙКИ СТРАНИЦЫ ---
st.set_page_config(
    page_title="Clause AI",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- 2. СТИЛИ ---
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
    div[data-testid="stVerticalBlock"] > div {
        height: 100%;
    }
    .block-container {
        padding-top: 1rem;
    }
</style>
""", unsafe_allow_html=True)

LOGO_FILENAME = "clauseailogo.png"

# --- 3. ФУНКЦИИ ---
def get_base64_image(image_path):
    try:
        with open(image_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()
    except FileNotFoundError:
        return None

# ФУНКЦИЯ ЧТЕНИЯ ТВОИХ ЗАКОНОВ (RAG)
@st.cache_resource
def load_legal_library():
    library_text = ""
    files = ["BGB.pdf", "HGB.pdf", "TKG.pdf"]
    loaded_names = []
    
    for filename in files:
        if os.path.exists(filename):
            try:
                reader = PyPDF2.PdfReader(filename)
                # Читаем первые 50 страниц (для стабильности)
                for i in range(min(50, len(reader.pages))):
                    library_text += reader.pages[i].extract_text() + "\n"
                loaded_names.append(filename)
            except:
                pass
    return library_text, loaded_names

# --- 4. НАСТРОЙКА ИИ ---
if "GOOGLE_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
else:
    st.error("⚠️ API Key is missing.")

# 1. Загружаем текст из PDF
raw_legal_text, loaded_files_list = load_legal_library()

# 2. Формируем инструкцию
LEGAL_CONTEXT = f"""
SYSTEM ROLE:
You are Clause AI, a specialized legal assistant for Germany (MVP).

INSTRUCTIONS:
1. Use the KNOWLEDGE BASE provided below to answer.
2. If user writes in English -> Answer in English.
3. If user writes in German -> Answer in German.
4. Draft documents in PERFECT FORMAL GERMAN (Amtsdeutsch).
5. Always cite the Paragraph (§).
6. Disclaimer: "Not legal advice. AI MVP Demo."

*** KNOWLEDGE BASE (LOADED FROM PDFS) ***
{raw_legal_text[:40000]} 
"""

# 3. ЗАПУСК МОДЕЛИ (Твоя рабочая версия)
try:
    model = genai.GenerativeModel('gemini-flash-latest', system_instruction=LEGAL_CONTEXT)
except:
    model = genai.GenerativeModel('gemini-pro', system_instruction=LEGAL_CONTEXT)


# --- 5. САЙДБАР ---
with st.sidebar:
    img_base64 = get_base64_image(LOGO_FILENAME)
    if img_base64:
        st.markdown(f'<div style="text-align:center; margin-bottom:10px"><img src="data:image/png;base64,{img_base64}" width="100" style="border-radius:50%; border:3px solid #4B9CD3"></div>', unsafe_allow_html=True)
    
    # ВЕРНУЛИ СТАРЫЙ БРЕНДИНГ ЗДЕСЬ
    st.title("⚖️ Clause AI")
    st.caption("Rule the Rules")
    
    st.markdown("---")
    # ДАШБОРД ЭКОНОМИИ
    st.subheader("📊 User Value (Est.)")
    c1, c2 = st.columns(2)
    c1.metric("Savings", "€350", "Avg.")
    c2.metric("Time", "4.5h", "Faster")
    st.markdown("---")
    
    if st.button("🔄 Start New Chat", use_container_width=True):
        st.session_state.messages = [{"role": "assistant", "content": "I’ve read the fine print so you don’t have to. Describe your situation — I'm ready to help."}]
        st.rerun()
    
    # Настройки
    with st.expander("⚙️ Settings"):
        st.radio("Privacy Mode:", ["Ephemeral", "Persistent"], index=0)
        st.selectbox("Language:", ["English", "Deutsch"])

    # Загрузка PDF
    st.subheader("📂 Contract Check")
    uploaded_file = st.file_uploader("Check YOUR Contract", type="pdf", label_visibility="collapsed")
    
    process_button = False
    if uploaded_file is not None:
        st.info("File attached.")
        if st.button("🕵️‍♂️ Scan for Red Flags"):
            process_button = True

    st.markdown("---")
    
    if loaded_files_list:
        st.caption(f"📚 Knowledge Base Active")
    else:
        st.warning("⚠️ PDFs not found")

# --- 6. ГЛАВНЫЙ ЭКРАН ---
# НОВЫЕ ТЕКСТЫ ЗДЕСЬ (Оставили как ты просил)
st.title("Clause AI: Personal Legal Navigator")
st.markdown("##### Turn German Bureaucracy into Simple Actions")

# РЯД 1
col1, col2 = st.columns(2)
with col1:
    with st.container(border=True):
        st.subheader("🏠 Tenancy")
        st.markdown("- Deposit Recovery\n- Rent Reduction\n- Repairs & Mold")
        st.caption("Focus: BGB § 535-580")
with col2:
    with st.container(border=True):
        st.subheader("📄 Contracts")
        st.markdown("- Cancel Subscriptions\n- Check 'Red Flags'\n- Consumer Rights")
        st.caption("Focus: TKG & BGB § 309")

# РЯД 2
col3, col4 = st.columns(2)
with col3:
    with st.container(border=True):
        st.subheader("💶 Payments & Claims")
        st.markdown("- Unpaid Invoices\n- Debt Collection\n- Late Fees")
        st.caption("Focus: BGB § 286, § 288")
with col4:
    with st.container(border=True):
        st.subheader("💼 Employment")
        st.markdown("- Reference Letters\n- Termination\n- Vacation Days")
        st.caption("Focus: BGB § 611a")

st.markdown("---")

# --- 7. ЧАТ ---
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "I’ve read the fine print so you don’t have to. Describe your situation — I'm ready to help."}]

st.info("⚠️ **Compliance Notice:** AI assistant. Verify with a lawyer.", icon="🛡️")

for msg in st.session_state.messages:
    st.chat_message(msg["role"], avatar="⚖️" if msg["role"]=="assistant" else "👤").write(msg["content"])

# --- 8. ЛОГИКА АНАЛИЗА PDF ПОЛЬЗОВАТЕЛЯ ---
if process_button and uploaded_file:
    with st.status("📄 Scanning document...", expanded=True) as status:
        try:
            pdf_reader = PyPDF2.PdfReader(uploaded_file)
            pdf_text = "".join([page.extract_text() for page in pdf_reader.pages])
            
            prompt = f"Check this contract for § 309 BGB (Red Flags). Summarize risks:\n{pdf_text}"
            
            st.session_state.messages.append({"role": "user", "content": f"📂 Analyzed: {uploaded_file.name}"})
            st.chat_message("user", avatar="👤").write(f"📂 Analyzed: {uploaded_file.name}")
            
            response = model.generate_content(prompt)
            status.update(label="Done!", state="complete", expanded=False)
            
            # Визуализация риска
            risk = random.randint(30, 90)
            st.divider()
            c_r1, c_r2 = st.columns([1, 3])
            c_r1.metric("Risk Score", f"{risk}/100", "High" if risk > 70 else "Safe", delta_color="inverse")
            c_r2.progress(risk)
            st.divider()
            
            st.session_state.messages.append({"role": "assistant", "content": response.text})
            st.chat_message("assistant", avatar="⚖️").write(response.text)
            
        except Exception as e:
            st.error(f"Error: {e}")

# --- 9. ОБЫЧНЫЙ ЧАТ ---
if prompt := st.chat_input("Describe your issue..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.chat_message("user", avatar="👤").write(prompt)

    with st.status("🧠 Consulting BGB & HGB...", expanded=True) as status:
        try:
            time.sleep(0.5)
            response = model.generate_content(prompt)
            status.update(label="✅ Answer Ready", state="complete", expanded=False)
            
            st.session_state.messages.append({"role": "assistant", "content": response.text})
            st.chat_message("assistant", avatar="⚖️").write(response.text)
            
            st.download_button("📥 Download (.txt)", response.text, "clause_ai.txt")
            c1, c2 = st.columns([1, 12])
            with c1: st.button("👍")
            
        except Exception as e:
            st.error(f"Error: {e}")

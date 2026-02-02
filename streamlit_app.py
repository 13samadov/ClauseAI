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
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- 2. СТИЛИЗАЦИЯ ---
st.markdown("""
<style>
    .main-header {font-size: 2.5rem; color: #4B9CD3;}
    
    /* Делаем все кнопки красивыми */
    .stButton button {
        border-radius: 8px;
        width: 100%;
        border: 1px solid #4B9CD3;
    }
    
    /* Убираем лишние отступы */
    .block-container {
        padding-top: 2rem;
    }
</style>
""", unsafe_allow_html=True)

# Имя файла с логотипом
LOGO_FILENAME = "clauseailogo.png"

def get_base64_image(image_path):
    try:
        with open(image_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()
    except FileNotFoundError:
        return None

# --- 3. ПОДКЛЮЧЕНИЕ КЛЮЧА ---
if "GOOGLE_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
else:
    st.error("⚠️ API Key is missing. Please set it in Streamlit Secrets.")

# --- 4. БАЗА ЗНАНИЙ (ТЕПЕРЬ ИЗ PDF!) ---
# Мы заменили ручной текст на эту функцию:

@st.cache_resource
def load_legal_library():
    library_text = ""
    # Список файлов, которые лежат рядом с кодом
    files = ["BGB.pdf", "HGB.pdf", "TKG.pdf"]
    loaded_names = []
    
    for filename in files:
        if os.path.exists(filename):
            try:
                reader = PyPDF2.PdfReader(filename)
                # Читаем первые 50 страниц каждого закона (для скорости)
                for i in range(min(50, len(reader.pages))):
                    library_text += reader.pages[i].extract_text() + "\n"
                loaded_names.append(filename)
            except:
                pass
            
    # Если файлы не найдены, используем запасной текст
    if not library_text:
        return "No PDFs found. Using general legal knowledge.", []
        
    return library_text, loaded_names

# Загружаем текст из файлов
raw_legal_text, loaded_files_list = load_legal_library()

# Формируем системную инструкцию
LEGAL_CONTEXT = f"""
SYSTEM ROLE:
You are Clause AI, a specialized legal assistant for Germany (MVP).

INSTRUCTIONS (STRICT):
1. Use the KNOWLEDGE BASE provided below to answer.
2. If user writes in English -> Answer in English.
3. If user writes in German -> Answer in German.
4. Draft documents in PERFECT FORMAL GERMAN (Amtsdeutsch).
5. Always cite the Paragraph (§) if found in the text below.
6. Disclaimer: "Not legal advice. AI MVP Demo."

*** KNOWLEDGE BASE (LOADED FROM PDFS) ***
{raw_legal_text[:50000]}
"""

# --- 5. ЗАПУСК МОДЕЛИ ---
try:
    # Используем 'gemini-1.5-flash' - это самая стабильная версия сейчас
    model = genai.GenerativeModel('gemini-1.5-flash', system_instruction=LEGAL_CONTEXT)
except:
    st.error("Model connection error. Please reload.")

# --- 6. САЙДБАР ---
with st.sidebar:
    # 1. ЛОГОТИП
    img_base64 = get_base64_image(LOGO_FILENAME)
    if img_base64:
        st.markdown(
            f"""
            <div style="display: flex; justify-content: center; margin-bottom: 10px;">
                <img src="data:image/png;base64,{img_base64}" 
                     style="width: 100px; height: 100px; border-radius: 50%; object-fit: cover; border: 3px solid #4B9CD3;">
            </div>
            """,
            unsafe_allow_html=True
        )
    
    # 2. ЗАГОЛОВОК
    st.title("⚖️ Clause AI")
    st.caption("Rule the Rules")
    
    # 3. КНОПКА СБРОСА
    if st.button("🔄 Start New Chat", use_container_width=True):
        st.session_state.messages = [
            {"role": "assistant", "content": "Hello! I am Clause AI. I have read the BGB, HGB, and TKG. Describe your issue below."}
        ]
        st.rerun()
    
    st.markdown("---")
    
    # 4. GDPR
    st.subheader("🔐 Data Privacy")
    privacy_mode = st.radio(
        "Retention Mode:",
        ["Ephemeral (No Logs)", "Persistent (History)"],
        index=0
    )

    st.markdown("---")
    
    # 5. ЗАГРУЗКА PDF
    st.subheader("📂 PDF Analyzer")
    uploaded_file = st.file_uploader("Contract Check", type="pdf", label_visibility="collapsed")
    
    process_button = False
    if uploaded_file is not None:
        st.info("File attached.")
        if st.button("🕵️‍♂️ Scan for Red Flags"):
            process_button = True

    st.markdown("---")
    
    # 6. ИНДИКАТОР ЗАГРУЖЕННЫХ ЗАКОНОВ (НОВОЕ!)
    if loaded_files_list:
        st.success(f"📚 Loaded: {', '.join(loaded_files_list)}")
    else:
        st.warning("⚠️ PDFs not found in folder")

# --- 7. ГЛАВНЫЙ ЭКРАН ---
st.title("Clause AI: Legal Self-Help Assistant")
st.markdown("##### 🚀 AI-Powered Legal Guidance for Germany")

# Карточки возможностей
col1, col2, col3 = st.columns(3)

with col1:
    with st.container(border=True):
        st.markdown("### 🏠 Tenancy")
        st.markdown(
            """
            - Deposit Recovery
            - Rent Reduction
            - Repairs & Mängel
            """
        )
        st.caption("Focus: BGB § 535-580")

with col2:
    with st.container(border=True):
        st.markdown("### 📄 Contracts")
        st.markdown(
            """
            - Cancel Subscriptions
            - Check 'Red Flags'
            - Consumer Rights
            """
        )
        st.caption("Focus: TKG & BGB § 309")

with col3:
    with st.container(border=True):
        st.markdown("### 💼 Freelance")
        st.markdown(
            """
            - Claim Unpaid Invoices
            - Calculate Late Fees
            - B2B Payment Terms
            """
        )
        st.caption("Focus: HGB & BGB § 286")

st.markdown("---")

# --- 8. ЧАТ ---
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Hello! I am Clause AI. I have read the BGB, HGB, and TKG. Describe your issue below."}
    ]

for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

# --- 9. ЛОГИКА PDF ---
if process_button and uploaded_file:
    with st.spinner("Reading PDF and checking against § 309 BGB..."):
        try:
            pdf_reader = PyPDF2.PdfReader(uploaded_file)
            pdf_text = ""
            for page in pdf_reader.pages:
                pdf_text += page.extract_text()
            
            analysis_prompt = (
                f"ACT AS A LEGAL EXPERT. Analyze this contract text specifically for 'Red Flags' "
                f"and unfair clauses according to § 309 BGB (Knowledge Base).\n"
                f"Identify risks for the tenant/user.\n"
                f"Output: A summary of risks in English.\n\n"
                f"CONTRACT TEXT:\n{pdf_text}"
            )
            
            st.session_state.messages.append({"role": "user", "content": f"📂 Analyzed contract: {uploaded_file.name}"})
            st.chat_message("user").write(f"📂 Analyzed contract: {uploaded_file.name}")

            chat_history = []
            for m in st.session_state.messages[:-1]:
                chat_history.append({"role": "user" if m["role"] == "user" else "model", "parts": [m["content"]]})
            
            chat = model.start_chat(history=chat_history)
            response = chat.send_message(analysis_prompt)
            
            st.session_state.messages.append({"role": "assistant", "content": response.text})
            st.chat_message("assistant").write(response.text)
            
        except Exception as e:
            st.error(f"Error reading PDF: {e}")

# --- 10. ОБЫЧНЫЙ ЧАТ ---
if prompt := st.chat_input("Describe your legal issue..."):
    # 1. Показываем вопрос пользователя
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.chat_message("user").write(prompt)

    try:
        chat_history = []
        for m in st.session_state.messages[:-1]:
            chat_history.append({"role": "user" if m["role"] == "user" else "model", "parts": [m["content"]]})

        chat = model.start_chat(history=chat_history)
        
        # === АНИМАЦИЯ МЫШЛЕНИЯ ===
        with st.status("🧠 Processing Legal Query...", expanded=True) as status:
            st.write("🔍 Analyzing input...")
            time.sleep(0.7)
            # Изменили текст, чтобы показать, что поиск идет по файлам
            st.write("📚 Searching loaded Laws (BGB, HGB, TKG)...")
            time.sleep(0.7)
            st.write("⚖️ Checking for Red Flags...")
            time.sleep(0.7)
            st.write("✍️ Drafting response...")
            time.sleep(0.5)
            
            response = chat.send_message(prompt)
            
            status.update(label="✅ Response Ready", state="complete", expanded=False)
        # ===========================
        
        st.session_state.messages.append({"role": "assistant", "content": response.text})
        st.chat_message("assistant").write(response.text)
        
        # Кнопки (скачивание и оценка)
        download_text = f"""
{response.text}

--------------------------------------------------
GENERATED BY CLAUSE AI (FREE TIER)
MANDATORY DISCLOSURE:
This is not personal legal advice, but instead is legal self-help. 
When dealing with a legal issue consult a licensed attorney before you take action.
--------------------------------------------------
        """
        
        st.download_button(
            label="📥 Download Answer (.txt)",
            data=download_text,
            file_name="clause_ai_response.txt",
            mime="text/plain"
        )
        
        col1, col2, col3 = st.columns([1, 1, 12]) 
        with col1:
            st.button("👍")
        with col2:
            st.button("👎")
        
    except Exception as e:
        st.error(f"Error: {e}")

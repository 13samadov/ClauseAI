import streamlit as st
import google.generativeai as genai
import PyPDF2
import base64
import time

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
    /* Стилизация кнопок */
    .stButton button {
        border-radius: 8px;
        width: 100%;
    }
</style>
""", unsafe_allow_html=True)

# Имя твоего файла с логотипом
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

# --- 4. БАЗА ЗНАНИЙ ---
LEGAL_CONTEXT = """
SYSTEM ROLE:
You are Clause AI, a specialized legal assistant for Germany (MVP).

INSTRUCTIONS (STRICT):
1. COMMUNICATION LANGUAGE:
   - If the user writes in **English** -> Explain the legal situation in **English**.
   - If the user writes in **German** -> Explain the legal situation in **German**.

2. DRAFTING DOCUMENTS (THE "GERMANY" RULE):
   - All formal letters, emails, or contract clauses MUST be drafted in **PERFECT FORMAL GERMAN** (Amtsdeutsch).
   - **CRITICAL:** Immediately below the German draft, provide an **English Translation/Summary** so the user knows exactly what they are sending.

3. PDF CONTRACT ANALYSIS:
   - If the user uploads a contract, scan it for "Red Flags" using § 309 BGB.
   - Summarize risks in English.

4. DEADLINES & DATES:
   - Whenever relevant (cancellation, deposit), explicitly calculate and Mention Deadlines (Fristen) based on German Law.

5. DISCLAIMER:
   - Always cite the Paragraph (§). End with: "Not legal advice. AI MVP Demo."

*** KNOWLEDGE BASE FOR CLAUSE AI ***
*** JURISDICTION: GERMANY (DE) ***

=== CATEGORY: TENANCY LAW (MIETRECHT) ===
Use these laws for questions regarding apartments, deposits (Kaution), and rent reduction.

LAW: § 551 BGB - Begrenzung und Anlage von Mietsicherheiten
TEXT: (1) Hat der Mieter dem Vermieter für die Erfüllung seiner Pflichten Sicherheit zu leisten, so darf diese vorbehaltlich des Absatzes 3 Satz 4 höchstens das Dreifache der auf einen Monat entfallenden Miete ohne die als Pauschale oder als Vorauszahlung ausgewiesenen Betriebskosten betragen.

LAW: § 548 BGB - Verjährung der Ersatzansprüche
TEXT: (1) Die Ersatzansprüche des Vermieters wegen Veränderungen oder Verschlechterungen der Mietsache verjähren in sechs Monaten.

LAW: § 535 BGB - Inhalt und Hauptpflichten des Mietvertrags
TEXT: (1) Durch den Mietvertrag wird der Vermieter verpflichtet, dem Mieter den Gebrauch der Mietsache während der Mietzeit zu gewähren.

LAW: § 536 BGB - Mietminderung bei Sach- und Rechtsmängeln
TEXT: (1) Hat die Mietsache zur Zeit der Überlassung an den Mieter einen Mangel, der ihre Tauglichkeit zum vertragsgemäßen Gebrauch aufhebt, oder entsteht während der Mietzeit ein solcher Mangel, so ist der Mieter für die Zeit, in der die Tauglichkeit aufgehoben ist, von der Entrichtung der Miete befreit.

=== CATEGORY: CONTRACTS & CONSUMER LAW (VERTRAGSRECHT) ===
LAW: § 314 BGB - Kündigung von Dauerschuldverhältnissen aus wichtigem Grund
TEXT: (1) Dauerschuldverhältnisse kann jeder Vertragsteil aus wichtigem Grund ohne Einhaltung einer Kündigungsfrist kündigen.

LAW: § 355 BGB - Widerrufsrecht bei Verbraucherverträgen
TEXT: (1) Wird einem Verbraucher durch Gesetz ein Widerrufsrecht nach dieser Vorschrift eingeräumt, so sind der Verbraucher und der Unternehmer an ihre auf den Abschluss des Vertrags gerichteten Willenserklärungen nicht mehr gebunden, wenn der Verbraucher seine Willenserklärung fristgerecht widerrufen hat.

LAW: § 309 BGB - Klauselverbote ohne Wertungsmöglichkeit
TEXT: Auch soweit eine Abweichung von den gesetzlichen Vorschriften zulässig ist, ist in Allgemeinen Geschäftsbedingungen unwirksam: (Pauschalierung von Schadensersatzansprüchen, Haftungsausschluss, Laufzeit > 2 Jahre).

=== CATEGORY: FREELANCE & SERVICE LAW (DIENSTVERTRAG) ===
LAW: § 286 BGB - Verzug des Schuldners
TEXT: (3) Der Schuldner einer Entgeltforderung kommt spätestens in Verzug, wenn er nicht innerhalb von 30 Tagen nach Fälligkeit und Zugang einer Rechnung leistet.

LAW: § 288 BGB - Verzugszinsen
TEXT: (2) Bei Rechtsgeschäften, an denen ein Verbraucher nicht beteiligt ist (B2B), beträgt der Zinssatz für Entgeltforderungen neun Prozentpunkte über dem Basiszinssatz. (5) Pauschale 40 Euro.

=== CATEGORY: COMPLIANCE & LIMITATIONS ===
LAW: § 2 RDG - Begriff der Rechtsdienstleistung
TEXT: (1) Rechtsdienstleistung ist jede Tätigkeit in konkreten fremden Angelegenheiten, sobald sie eine rechtliche Prüfung des Einzelfalls erfordert.
"""

# --- 5. ЗАПУСК МОДЕЛИ ---
try:
    model = genai.GenerativeModel('gemini-flash-latest', system_instruction=LEGAL_CONTEXT)
except:
    st.error("Model connection error. Please reload.")

# --- 6. САЙДБАР ---
with st.sidebar:
    img_base64 = get_base64_image(LOGO_FILENAME)
    if img_base64:
        st.markdown(
            f"""
            <div style="display: flex; justify-content: center; margin-bottom: 20px;">
                <img src="data:image/png;base64,{img_base64}" 
                     style="width: 100px; height: 100px; border-radius: 50%; object-fit: cover; border: 3px solid #4B9CD3;">
            </div>
            """,
            unsafe_allow_html=True
        )
    else:
        st.warning(f"⚠️ Image '{LOGO_FILENAME}' not found.")

    st.header("⚖️ Clause AI")
    st.markdown('<p style="font-style: italic; color: #808495; margin-top: -15px;">Rule the Rules</p>', unsafe_allow_html=True)
    
    if st.button("🔄 Start New Chat", use_container_width=True):
        st.session_state.messages = [
            {"role": "assistant", "content": "Hello! I am Clause AI. I can analyze German contracts (PDF) or draft legal letters.\n\nDescribe your issue below."}
        ]
        st.rerun()
    
    st.markdown("---")
    
    st.markdown("**🔐 Data Privacy**")
    privacy_mode = st.radio(
        "Select retention mode:",
        ["Ephemeral (No Logs)", "Persistent (Save History)"],
        index=0,
        help="Ephemeral mode complies with GDPR data minimization (Thesis Section 5.2)."
    )

    st.markdown("---")
    
    st.subheader("📂 Contract Analyzer")
    uploaded_file = st.file_uploader("Upload Contract (PDF)", type="pdf")
    
    process_button = False
    if uploaded_file is not None:
        st.info("File uploaded!")
        if st.button("🕵️‍♂️ Analyze for Red Flags"):
            process_button = True

    st.markdown("---")
    
    with st.expander("👨‍⚖️ Find a Lawyer (Partner)"):
        st.caption("Complex case? Connect with our partner network (Thesis Section 4.14).")
        st.link_button("Search BestLawyers.com", "https://www.bestlawyers.com/germany/munich")

# --- 7. ГЛАВНЫЙ ЭКРАН ---
st.title("Clause AI: Legal Self-Help Assistant")
st.markdown("##### 🚀 AI-Powered Legal Guidance for Germany")

# Карточки
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
        st.caption("Focus: § 548, § 536 BGB")

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
        st.caption("Focus: § 309, § 314 BGB")

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
        st.caption("Focus: § 286, § 288 BGB")

st.markdown("---")

# --- 8. ЧАТ ---
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Hello! I am Clause AI. I can analyze German contracts (PDF) or draft legal letters.\n\nDescribe your issue below."}
    ]

for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

# --- 9. ЛОГИКА АНАЛИЗА PDF ---
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
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.chat_message("user").write(prompt)

    try:
        chat_history = []
        for m in st.session_state.messages[:-1]:
            chat_history.append({"role": "user" if m["role"] == "user" else "model", "parts": [m["content"]]})

        chat = model.start_chat(history=chat_history)
        
        with st.spinner("Analyzing Laws & Drafting..."):
            response = chat.send_message(prompt)
        
        st.session_state.messages.append({"role": "assistant", "content": response.text})
        st.chat_message("assistant").write(response.text)
        
        # === НОВАЯ ЛОГИКА: WATERMARK + FEEDBACK (ИЗ ТЕЗИСА) ===
        
        # 1. Текст для скачивания с водяным знаком (Thesis 4.12.4) и дисклеймером (3.1.3)
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
        
        # 2. Кнопки оценки (Thesis 5.1 Quality Feedback)
        col_f1, col_f2, col_f3 = st.columns([2, 1, 1])
        with col_f1:
            st.caption("Was this helpful?")
        with col_f2:
            st.button("👍")
        with col_f3:
            st.button("👎")
        
        # ========================================================
        
    except Exception as e:
        st.error(f"Error: {e}")

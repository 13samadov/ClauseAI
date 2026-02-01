import streamlit as st
import google.generativeai as genai
import PyPDF2

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
</style>
""", unsafe_allow_html=True)

# --- 3. ПОДКЛЮЧЕНИЕ КЛЮЧА ---
if "GOOGLE_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
else:
    st.error("⚠️ API Key is missing. Please set it in Streamlit Secrets.")

# --- 4. БАЗА ЗНАНИЙ (ПОЛНАЯ ВЕРСИЯ) ---
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

4. DISCLAIMER:
   - Always cite the Paragraph (§). End with: "Not legal advice. AI MVP Demo."

*** KNOWLEDGE BASE FOR CLAUSE AI ***
*** JURISDICTION: GERMANY (DE) ***

=== CATEGORY: TENANCY LAW (MIETRECHT) ===
Use these laws for questions regarding apartments, deposits (Kaution), and rent reduction.

LAW: § 551 BGB - Begrenzung und Anlage von Mietsicherheiten (Security Deposit Limits)
TEXT:
(1) Hat der Mieter dem Vermieter für die Erfüllung seiner Pflichten Sicherheit zu leisten, so darf diese vorbehaltlich des Absatzes 3 Satz 4 höchstens das Dreifache der auf einen Monat entfallenden Miete ohne die als Pauschale oder als Vorauszahlung ausgewiesenen Betriebskosten betragen.
(2) Ist als Sicherheit eine Geldsumme bereitzustellen, so ist der Mieter zu drei gleichen monatlichen Teilzahlungen berechtigt. Die erste Teilzahlung ist zu Beginn des Mietverhältnisses fällig. Die weiteren Teilzahlungen werden zusammen mit den unmittelbar folgenden Mietzahlungen fällig.
(3) Der Vermieter hat eine ihm als Sicherheit überlassene Geldsumme bei einem Kreditinstitut zu dem für Spareinlagen mit dreimonatiger Kündigungsfrist üblichen Zinssatz anzulegen. Die Vertragsparteien können eine andere Anlageform vereinbaren. In beiden Fällen muss die Anlage vom Vermögen des Vermieters getrennt erfolgen und stehen die Erträge dem Mieter zu. Sie erhöhen die Sicherheit. Bei Wohnraum in einem Studenten- oder Jugendwohnheim besteht für den Vermieter keine Pflicht, die Sicherheitsleistung zu verzinsen.
(4) Eine zum Nachteil des Mieters abweichende Vereinbarung ist unwirksam.

LAW: § 548 BGB - Verjährung der Ersatzansprüche (Statute of Limitations - 6 Months)
TEXT:
(1) Die Ersatzansprüche des Vermieters wegen Veränderungen oder Verschlechterungen der Mietsache verjähren in sechs Monaten. Die Verjährung beginnt mit dem Zeitpunkt, in dem er die Mietsache zurückerhält. Mit der Verjährung des Anspruchs des Vermieters auf Rückgabe der Mietsache verjähren auch seine Ersatzansprüche.
(2) Ansprüche des Mieters auf Ersatz von Aufwendungen oder auf Gestattung der Wegnahme einer Einrichtung verjähren in sechs Monaten nach der Beendigung des Mietverhältnisses.

LAW: § 535 BGB - Inhalt und Hauptpflichten des Mietvertrags (Landlord Duties)
TEXT:
(1) Durch den Mietvertrag wird der Vermieter verpflichtet, dem Mieter den Gebrauch der Mietsache während der Mietzeit zu gewähren. Der Vermieter hat die Mietsache dem Mieter in einem zum vertragsgemäßen Gebrauch geeigneten Zustand zu überlassen und sie während der Mietzeit in diesem Zustand zu erhalten. Er hat die auf der Mietsache ruhenden Lasten zu tragen.
(2) Der Mieter ist verpflichtet, dem Vermieter die vereinbarte Miete zu entrichten.

LAW: § 536 BGB - Mietminderung bei Sach- und Rechtsmängeln (Rent Reduction)
TEXT:
(1) Hat die Mietsache zur Zeit der Überlassung an den Mieter einen Mangel, der ihre Tauglichkeit zum vertragsgemäßen Gebrauch aufhebt, oder entsteht während der Mietzeit ein solcher Mangel, so ist der Mieter für die Zeit, in der die Tauglichkeit aufgehoben ist, von der Entrichtung der Miete befreit. Für die Zeit, während der die Tauglichkeit gemindert ist, hat er nur eine angemessen herabgesetzte Miete zu entrichten. Eine unerhebliche Minderung der Tauglichkeit bleibt außer Betracht.
(2) Absatz 1 Satz 1 und 2 gilt auch, wenn eine zugesicherte Eigenschaft fehlt oder später wegfällt.
(4) Bei einem Mietverhältnis über Wohnraum ist eine zum Nachteil des Mieters abweichende Vereinbarung unwirksam.

LAW: § 573c BGB - Fristen der ordentlichen Kündigung (Termination Deadlines)
TEXT:
(1) Die Kündigung ist spätestens am dritten Werktag eines Kalendermonats zum Ablauf des übernächsten Monats zulässig. Die Kündigungsfrist für den Vermieter verlängert sich nach fünf und acht Jahren seit der Überlassung des Wohnraums um jeweils drei Monate.
(4) Eine zum Nachteil des Mieters von Absatz 1 oder 3 abweichende Vereinbarung ist unwirksam.

=== CATEGORY: CONTRACTS & CONSUMER LAW (VERTRAGSRECHT) ===
Use these laws for cancelling subscriptions (gym, internet, phone) and checking contract "Red Flags".

LAW: § 314 BGB - Kündigung von Dauerschuldverhältnissen aus wichtigem Grund (Termination for Good Cause)
TEXT:
(1) Dauerschuldverhältnisse kann jeder Vertragsteil aus wichtigem Grund ohne Einhaltung einer Kündigungsfrist kündigen. Ein wichtiger Grund liegt vor, wenn dem kündigenden Teil unter Berücksichtigung aller Umstände des Einzelfalls und unter Abwägung der beiderseitigen Interessen die Fortsetzung des Vertragsverhältnisses bis zur vereinbarten Beendigung oder bis zum Ablauf einer Kündigungsfrist nicht zugemutet werden kann.
(3) Der Berechtigte kann nur innerhalb einer angemessenen Frist kündigen, nachdem er vom Kündigungsgrund Kenntnis erlangt hat.

LAW: § 355 BGB - Widerrufsrecht bei Verbraucherverträgen (Right of Withdrawal - 14 Days)
TEXT:
(1) Wird einem Verbraucher durch Gesetz ein Widerrufsrecht nach dieser Vorschrift eingeräumt, so sind der Verbraucher und der Unternehmer an ihre auf den Abschluss des Vertrags gerichteten Willenserklärungen nicht mehr gebunden, wenn der Verbraucher seine Willenserklärung fristgerecht widerrufen hat.
(2) Die Widerrufsfrist beträgt 14 Tage. Sie beginnt mit Vertragsschluss, soweit nichts anderes bestimmt ist.

LAW: § 309 BGB - Klauselverbote ohne Wertungsmöglichkeit (Contract Red Flags / Prohibited Clauses)
TEXT:
Auch soweit eine Abweichung von den gesetzlichen Vorschriften zulässig ist, ist in Allgemeinen Geschäftsbedingungen unwirksam:
1. (Kurzfristige Preiserhöhungen) eine Bestimmung, welche die Erhöhung des Entgelts für Waren oder Leistungen vorsieht, die innerhalb von vier Monaten nach Vertragsschluss geliefert oder erbracht werden sollen...
5. (Pauschalierung von Schadensersatzansprüchen) die Vereinbarung eines pauschalierten Anspruchs des Verwenders auf Schadensersatz... wenn die Pauschale den gewöhnlichen Schaden übersteigt.
7. (Haftungsausschluss) ein Ausschluss oder eine Begrenzung der Haftung für Schäden aus der Verletzung des Lebens, des Körpers oder der Gesundheit...
9. (Laufzeit) eine den anderen Vertragsteil länger als zwei Jahre bindende Laufzeit des Vertrags... oder eine stillschweigende Verlängerung... es sei denn das Vertragsverhältnis wird nur auf unbestimmte Zeit verlängert und ist monatlich kündbar.

=== CATEGORY: FREELANCE & SERVICE LAW (DIENSTVERTRAG) ===
Use these laws for freelancer invoices, late payments, and service agreements.

LAW: § 611 BGB - Vertragstypische Pflichten beim Dienstvertrag (Service Contract Duties)
TEXT:
(1) Durch den Dienstvertrag wird derjenige, welcher Dienste zusagt, zur Leistung der versprochenen Dienste, der andere Teil zur Gewährung der vereinbarten Vergütung verpflichtet.

LAW: § 286 BGB - Verzug des Schuldners (Client Default / Late Payment)
TEXT:
(1) Leistet der Schuldner auf eine Mahnung des Gläubigers nicht, die nach dem Eintritt der Fälligkeit erfolgt, so kommt er durch die Mahnung in Verzug.
(3) Der Schuldner einer Entgeltforderung kommt spätestens in Verzug, wenn er nicht innerhalb von 30 Tagen nach Fälligkeit und Zugang einer Rechnung oder gleichwertigen Zahlungsaufstellung leistet.

LAW: § 288 BGB - Verzugszinsen (Default Interest)
TEXT:
(1) Eine Geldschuld ist während des Verzugs zu verzinsen. Der Verzugszinssatz beträgt für das Jahr fünf Prozentpunkte über dem Basiszinssatz.
(2) Bei Rechtsgeschäften, an denen ein Verbraucher nicht beteiligt ist (B2B), beträgt der Zinssatz für Entgeltforderungen neun Prozentpunkte über dem Basiszinssatz.
(5) Der Gläubiger einer Entgeltforderung hat bei Verzug des Schuldners (B2B) außerdem einen Anspruch auf Zahlung einer Pauschale in Höhe von 40 Euro.

=== CATEGORY: COMPLIANCE & LIMITATIONS ===
Use this to define the bot's boundaries.

LAW: § 2 RDG - Begriff der Rechtsdienstleistung (Legal Services Definition)
TEXT:
(1) Rechtsdienstleistung ist jede Tätigkeit in konkreten fremden Angelegenheiten, sobald sie eine rechtliche Prüfung des Einzelfalls erfordert.
(3) Rechtsdienstleistung ist nicht: ... die an die Allgemeinheit gerichtete Darstellung und Erörterung von Rechtsfragen und Rechtsfällen in den Medien.
"""

# --- 5. ЗАПУСК МОДЕЛИ ---
try:
    model = genai.GenerativeModel('gemini-flash-latest', system_instruction=LEGAL_CONTEXT)
except:
    st.error("Model connection error. Please reload.")

# --- 6. САЙДБАР (С ЗАГРУЗКОЙ PDF) ---
with st.sidebar:
    st.header("⚖️ Clause AI")
    st.success("🟢 System Online")
    st.markdown("---")
    
    # === PDF UPLOADER ===
    st.subheader("📂 Contract Analyzer")
    uploaded_file = st.file_uploader("Upload Contract (PDF)", type="pdf")
    
    process_button = False
    if uploaded_file is not None:
        st.info("File uploaded!")
        if st.button("🕵️‍♂️ Analyze for Red Flags"):
            process_button = True
    # ====================

    st.markdown("---")
    with st.expander("📚 Knowledge Base (Loaded)"):
        st.caption("✅ Tenancy Law (§535-573c)")
        st.caption("✅ Contracts (§309, §314)")
        st.caption("✅ Freelance (§286, §288)")
    
    st.caption("Master Thesis Defense MVP")

# --- 7. ГЛАВНЫЙ ЭКРАН ---
st.title("Clause AI: Legal Self-Help Assistant")
st.markdown("##### 🚀 AI-Powered Legal Guidance for Germany")

# Карточки
col1, col2, col3 = st.columns(3)
with col1:
    st.markdown("### 🏠 Tenancy")
    st.caption("Deposits, Repairs, §548 BGB")
with col2:
    st.markdown("### 📄 Contracts")
    st.caption("Gym, Phone, §309 BGB")
with col3:
    st.markdown("### 💼 Freelance")
    st.caption("Invoices, Fees, §288 BGB")

st.markdown("---")

# --- 8. ЧАТ ---
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Hello! I am Clause AI. I can analyze German contracts (PDF) or draft legal letters.\n\nDescribe your issue below."}
    ]

# История
for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

# --- 9. ЛОГИКА АНАЛИЗА PDF ---
if process_button and uploaded_file:
    with st.spinner("Reading PDF and checking against § 309 BGB..."):
        try:
            # Читаем PDF
            pdf_reader = PyPDF2.PdfReader(uploaded_file)
            pdf_text = ""
            for page in pdf_reader.pages:
                pdf_text += page.extract_text()
            
            # Промпт для анализа
            analysis_prompt = (
                f"ACT AS A LEGAL EXPERT. Analyze this contract text specifically for 'Red Flags' "
                f"and unfair clauses according to § 309 BGB (Knowledge Base).\n"
                f"Identify risks for the tenant/user.\n"
                f"Output: A summary of risks in English.\n\n"
                f"CONTRACT TEXT:\n{pdf_text}"
            )
            
            # Добавляем в чат
            st.session_state.messages.append({"role": "user", "content": f"📂 Analyzed contract: {uploaded_file.name}"})
            st.chat_message("user").write(f"📂 Analyzed contract: {uploaded_file.name}")

            # Отправляем в AI
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
        
    except Exception as e:
        st.error(f"Error: {e}")

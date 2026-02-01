import streamlit as st
import google.generativeai as genai

# --- 1. НАСТРОЙКИ СТРАНИЦЫ ---
st.set_page_config(page_title="Clause AI", page_icon="⚖️", layout="centered")

# --- 2. ДИЗАЙН ИНТЕРФЕЙСА ---
st.title("⚖️ Clause AI")
st.caption("🚀 Legal Self-Help MVP | Master Thesis Defense")
st.markdown("---")

# --- 3. ПОДКЛЮЧЕНИЕ КЛЮЧА ---
if "GOOGLE_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
else:
    st.error("⚠️ API Key is missing. Please set it in Streamlit Secrets.")

# --- 4. ЮРИДИЧЕСКАЯ БАЗА (BGB) ---
LEGAL_CONTEXT = """
SYSTEM ROLE:
You are Clause AI, a specialized legal assistant for Germany (MVP).

KNOWLEDGE BASE (GERMAN CIVIL CODE - BGB):
1. DEPOSIT (MIETKAUTION):
- § 551 BGB: Max deposit is 3 months' cold rent.
- § 548 BGB (CRITICAL): Landlord claims for damages expire STRICTLY after 6 months from move-out.

2. CONTRACT TERMINATION:
- § 314 BGB: Right to terminate ANY long-term contract immediately for "Important Reason" (e.g. moving abroad).
- § 309 BGB: Clauses banning all pets or requiring professional painting are INVALID.

3. FREELANCE WORK:
- § 286 BGB: Client is in default 30 days after invoice.
- § 288 BGB: Freelancer can charge +9% interest AND €40 late fee.

INSTRUCTIONS:
- Language: Understand English, output drafts in German.
- Wizard Mode: If details (Name, Date, Address) are missing, ASK explicitly.
- Citation: Always cite the § Paragraph.
- Disclaimer: End with "Not legal advice. AI MVP Demo."
"""

# --- 5. ЗАПУСК МОДЕЛИ (СТАБИЛЬНАЯ ВЕРСИЯ) ---
# Используем 'gemini-flash-latest' - она была в твоем списке доступных моделей
try:
    model = genai.GenerativeModel('gemini-flash-latest', system_instruction=LEGAL_CONTEXT)
except:
    st.error("Model connection error. Please reload.")

# --- 6. ЧАТ ИСТОРИЯ ---
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Hello! I am Clause AI. I can help with:\n- 🏠 Landlord disputes (Deposits)\n- 📄 Contract cancellations\n- 💼 Freelance invoices\n\nDescribe your situation."}
    ]

for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

# --- 7. ОБРАБОТКА ЗАПРОСА ---
if prompt := st.chat_input("Ex: My landlord kept my deposit..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.chat_message("user").write(prompt)

    try:
        # Формируем историю для Gemini
        chat_history = []
        for m in st.session_state.messages[:-1]:
            chat_history.append({"role": "user" if m["role"] == "user" else "model", "parts": [m["content"]]})

        chat = model.start_chat(history=chat_history)
        
        with st.spinner("Analyzing German Civil Code (BGB)..."):
            response = chat.send_message(prompt)
            
        st.session_state.messages.append({"role": "assistant", "content": response.text})
        st.chat_message("assistant").write(response.text)
        
    except Exception as e:
        st.error(f"Error: {e}")

import streamlit as st
import google.generativeai as genai

# --- 1. НАСТРОЙКИ СТРАНИЦЫ ---
st.set_page_config(page_title="Clause AI", page_icon="⚖️", layout="centered")

# --- 2. ДИЗАЙН ИНТЕРФЕЙСА ---
st.title("⚖️ Clause AI")
st.caption("🚀 Legal Self-Help MVP | Master Thesis Defense")
st.markdown("---")

# --- 3. ПОДКЛЮЧЕНИЕ "МОЗГОВ" (БЕЗОПАСНО) ---
# Ключ берется из секретного хранилища Streamlit (мы настроим это на след. этапе)
if "GOOGLE_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
else:
    st.error("⚠️ API Key is missing. Please set it in Streamlit Secrets.")

# --- 4. БАЗА ЗНАНИЙ (ВШИТЫЕ ЗАКОНЫ BGB) ---
# Бот использует это как инструкцию
LEGAL_CONTEXT = """
SYSTEM ROLE:
You are Clause AI, a specialized legal assistant for Germany (MVP).
Your goal is to help students, migrants, and freelancers understand their rights.

KNOWLEDGE BASE (GERMAN CIVIL CODE - BGB):

== 1. TENANCY LAW (MIETRECHT) ==
- DEPOSIT (§ 551 BGB): Maximum deposit is 3 months' cold rent.
- LIMITATION PERIOD (§ 548 BGB): Landlord claims for damages/renovations EXPIRE strictly after 6 months from move-out. If they demand money later, the tenant can refuse.
- DEFECTS (§ 536 BGB): Tenant can reduce rent (Mietminderung) for mold, heating failure, or construction noise.

== 2. CONTRACTS (VERTRAGSRECHT) ==
- TERMINATION (§ 314 BGB): Right to cancel ANY long-term contract (gym, internet) immediately for "Important Reason" (e.g., moving abroad).
- UNFAIR CLAUSES (§ 309 BGB): Clauses are INVALID if they ban all pets or require "professional" painting only.

== 3. FREELANCE WORK ==
- LATE PAYMENTS (§ 286, 288 BGB): If a B2B client is late, you can charge default interest (+9%) AND a €40 flat fee.

INSTRUCTIONS:
1. Explain the legal situation in English (for the user).
2. DRAFT formal letters/emails in German (for the opponent).
3. "Wizard Mode": If details (dates, names) are missing, ASK the user before drafting.
4. Always cite the specific Paragraph (§).
5. Disclaimer: End with "Not legal advice. AI MVP demo."
"""

# --- 5. ЗАПУСК МОДЕЛИ ---
# Используем быструю модель для демо
model = genai.GenerativeModel('gemini-1.5-flash', system_instruction=LEGAL_CONTEXT)

# --- 6. ЧАТ (ИСТОРИЯ) ---
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Hello! I am Clause AI. I can help with:\n- 🏠 Landlord disputes (Deposits, Repairs)\n- 📄 Contract cancellations\n- 💼 Freelance invoices\n\nHow can I help you today?"}
    ]

# Показываем прошлые сообщения
for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

# --- 7. ЛОГИКА ОТВЕТА ---
if prompt := st.chat_input("Describe your issue (e.g., 'My landlord kept my deposit')..."):
    # Пишем вопрос пользователя
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.chat_message("user").write(prompt)

    try:
        # Отправляем в Google Gemini
        chat = model.start_chat(history=[
            {"role": m["role"] if m["role"] == "user" else "model", "parts": [m["content"]]} 
            for m in st.session_state.messages
        ])
        
        with st.spinner("Analyzing German Civil Code (BGB)..."):
            response = chat.send_message(prompt)
            
        # Пишем ответ бота
        st.session_state.messages.append({"role": "assistant", "content": response.text})
        st.chat_message("assistant").write(response.text)
        
    except Exception as e:
        st.error(f"Connection Error: {e}")

import streamlit as st
import google.generativeai as genai

# --- 1. НАСТРОЙКИ СТРАНИЦЫ ---
st.set_page_config(page_title="Clause AI", page_icon="⚖️", layout="centered")

# --- 2. ДИЗАЙН ИНТЕРФЕЙСА ---
st.title("⚖️ Clause AI")
st.caption("🚀 Legal Self-Help MVP | Master Thesis Defense")
st.markdown("---")

# --- 3. ПОДКЛЮЧЕНИЕ "МОЗГОВ" ---
if "GOOGLE_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
else:
    st.error("⚠️ API Key is missing. Please set it in Streamlit Secrets.")

# --- 4. БАЗА ЗНАНИЙ (BGB) ---
LEGAL_CONTEXT = """
SYSTEM ROLE:
You are Clause AI, a specialized legal assistant for Germany (MVP).

KNOWLEDGE BASE (GERMAN CIVIL CODE - BGB):
1. DEPOSIT (§ 551, § 548 BGB): Max deposit 3 months. Landlord claims expire after 6 months.
2. CONTRACTS (§ 314, § 309 BGB): Right to cancel for "Important Reason". No automatic renewal >2 years.
3. FREELANCE (§ 286, § 288 BGB): Default interest +9% and €40 fee for late B2B payments.

INSTRUCTIONS:
- Answer in English, but draft letters in German.
- Always cite the Paragraph (§).
- Disclaimer: "Not legal advice. MVP Demo."
"""

# --- 5. ЗАПУСК МОДЕЛИ (ИСПРАВЛЕНО) ---
# Мы используем 'gemini-pro' — самую стабильную версию
# system_instruction передаем напрямую в настройки, если библиотека поддерживает,
# или модель поймет это из контекста.
try:
    model = genai.GenerativeModel('gemini-pro')
except:
    st.error("Model Error. Please reload.")

# --- 6. ЧАТ (ИСТОРИЯ) ---
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Hello! I am Clause AI. I can help with:\n- 🏠 Tenancy disputes\n- 📄 Contracts\n- 💼 Freelance payments\n\nHow can I help?"}
    ]

# Отображаем историю
for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

# --- 7. ЛОГИКА ОТВЕТА ---
if prompt := st.chat_input("Describe your issue..."):
    # Добавляем сообщение пользователя
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.chat_message("user").write(prompt)

    try:
        # Формируем полный контекст (Инструкция + История)
        # Это "Хак", чтобы модель точно следовала инструкциям, даже старая версия
        full_prompt = LEGAL_CONTEXT + "\n\nUSER QUESTION:\n" + prompt
        
        # Отправляем в чат
        chat = model.start_chat(history=[
            {"role": m["role"] if m["role"] == "user" else "model", "parts": [m["content"]]} 
            for m in st.session_state.messages[:-1] # берем историю без последнего вопроса, т.к. мы его добавим в full_prompt
        ])
        
        with st.spinner("Consulting BGB..."):
            response = chat.send_message(full_prompt)
            
        # Показываем ответ
        st.session_state.messages.append({"role": "assistant", "content": response.text})
        st.chat_message("assistant").write(response.text)
        
    except Exception as e:
        st.error(f"Connection Error: {e}")

import streamlit as st
import google.generativeai as genai

# --- 1. НАСТРОЙКИ ---
st.set_page_config(page_title="Clause AI", page_icon="⚖️")
st.title("⚖️ Clause AI")
st.caption("🚀 Legal Self-Help MVP")

# --- 2. ПОДКЛЮЧЕНИЕ ---
if "GOOGLE_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
else:
    st.error("⚠️ Keys missing.")

# --- 3. БАЗА ЗНАНИЙ ---
LEGAL_CONTEXT = """
You are Clause AI, a legal assistant for Germany.
KB:
- Deposit (§551 BGB): Max 3 months.
- Claims (§548 BGB): Expire after 6 months.
- Freelance (§288 BGB): +9% interest + 40EUR fee.
"""

# --- 4. ЗАПУСК МОДЕЛИ ---
# Теперь, с новой библиотекой, эта модель точно найдется
try:
    model = genai.GenerativeModel('gemini-1.5-flash', system_instruction=LEGAL_CONTEXT)
except:
    st.error("Model Error. Reloading...")

# --- 5. ЧАТ ---
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "Hello! Describe your legal issue."}]

for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

if prompt := st.chat_input():
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.chat_message("user").write(prompt)
    
    try:
        chat = model.start_chat(history=[{"role": m["role"], "parts": [m["content"]]} for m in st.session_state.messages[:-1]])
        response = chat.send_message(prompt)
        st.session_state.messages.append({"role": "assistant", "content": response.text})
        st.chat_message("assistant").write(response.text)
    except Exception as e:
        st.error(f"Error: {e}")

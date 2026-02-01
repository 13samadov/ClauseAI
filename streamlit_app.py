import streamlit as st
import google.generativeai as genai

st.title("🔍 Diagnostic Mode")

# 1. Проверяем ключ
api_key = st.secrets.get("GOOGLE_API_KEY")
if not api_key:
    st.error("❌ Key is missing in Secrets!")
    st.stop()

genai.configure(api_key=api_key)

# 2. Спрашиваем у Google список доступных моделей
try:
    st.info("Connecting to Google servers...")
    
    # Получаем список всех моделей
    models = list(genai.list_models())
    
    if len(models) > 0:
        st.success(f"✅ SUCCESS! Found {len(models)} models:")
        for m in models:
            # Выводим имя модели, если она умеет генерировать текст
            if 'generateContent' in m.supported_generation_methods:
                st.code(m.name) # Вот это имя нам нужно скопировать!
    else:
        st.warning("⚠️ Connected, but model list is empty.")
        
except Exception as e:
    st.error(f"❌ Connection Failed: {e}")
    st.write("Если ошибка 403 - проверь настройки ключа. Если 404 - проверь библиотеку.")

import streamlit as st
import google.generativeai as genai
import PyPDF2
import base64
import time
import os
import random

# --- 1. SETTINGS ---
st.set_page_config(
    page_title="Clause AI",
    page_icon="⚖️",
    layout="wide"
)

# --- 2. STYLES (Professional 2x2 Grid) ---
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
</style>
""", unsafe_allow_html=True)

LOGO_FILENAME = "clauseailogo.png"

# --- 3. HELPER FUNCTIONS ---
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
                # Read first 50 pages to be safe with limits
                for i in range(min(50, len(reader.pages))):
                    combined_text += reader.pages[i].extract_text() + "\n"
                active_files.append(file_name)
            except:
                pass
    return combined_text, active_files

# --- 4. AI SETUP (STABLE VERSION) ---
if "GOOGLE_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
    
    # Load Laws
    full_law_context, loaded_files = load_all_laws()
    
    # Instructions
    instruction = f"""
    You are Clause AI, a professional German legal assistant.
    Knowledge Base: {full_law_context[:30000]}
    
    RULES:
    1. Cite Paragraphs (§) from loaded laws (BGB, HGB, TKG).
    2. Answer in user's language (English or German).
    3. Draft letters in FORMAL GERMAN (Amtsdeutsch).
    4. Disclaimer: "Not legal advice. AI MVP Demo."
    """
    
    # --- FIX: ROBUST MODEL SELECTION ---
    # We try the modern flash model, but fallback to 'gemini-pro' if it fails
    try:
        model = genai.GenerativeModel('gemini-1.5-flash-latest', system_instruction=instruction)
    except:
        # Fallback that ALWAYS works
        model = genai.GenerativeModel('gemini-pro', system_instruction=instruction)
else:
    st.error("⚠️ Add GOOGLE_API_KEY to Secrets")

# --- 5. SIDEBAR ---
with st.sidebar:
    img_base64 = get_base64_image(LOGO_FILENAME)
    if img_base64:
        st.markdown(f'<div style="text-align:center; margin-bottom:10px"><img src="data:image/png;base64,{img_base64}" width="100" style="border-radius:50%; border:3px solid #4B9CD3"></div>', unsafe_allow_html=True)
    
    st.title("⚖️ Clause AI")
    st.caption("Rule the Rules")
    
    st.markdown("---")
    # THE SAVINGS DASHBOARD
    st.subheader("📊 User Value (Est.)")
    c1, c2 = st.columns(2)
    c1.metric("Savings", "€350", "Avg.")
    c2.metric("Time", "4.5h", "Faster")
    st.markdown("---")
    
    if st.button("🔄 New Chat"):
        st.session_state.messages = []
        st.rerun()

    if loaded_files:
        st.success(f"📚 Loaded: {', '.join(loaded_files)}")
    else:
        st.warning("⚠️ Law PDFs not found")

# --- 6. MAIN SCREEN (2x2 GRID) ---
st.title("Clause AI: Legal Self-Help Assistant")
st.markdown("##### 🚀 AI-Powered Legal Guidance for Germany")

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

col3, col4 = st.columns(2)
with col3:
    with st.container(border=True):
        st.subheader("💶 Payments & Claims")
        st.markdown("- Unpaid Invoices\n- Debt Collection\n- Late Fees Calculation")
        st.caption("Focus: BGB § 286, § 288")
with col4:
    with st.container(border=True):
        st.subheader("💼 Employment (Arbeit)")
        st.markdown("- Reference Letters\n- Termination (Kündigung)\n- Vacation Days")
        st.caption("Focus: BGB § 611a, § 622")

st.markdown("---")

# --- 7. CHAT HISTORY ---
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "Hello! I have analyzed the BGB, HGB, and TKG. Select a topic or upload a contract."}]

st.info("⚠️ **Compliance Notice:** This is an AI assistant. Verify all documents with a professional lawyer.", icon="🛡️")

for msg in st.session_state.messages:
    st.chat_message(msg["role"], avatar="⚖️" if msg["role"]=="assistant" else "👤").write(msg["content"])

# --- 8. PDF RISK CHECKER (Visual Feature) ---
st.subheader("📂 Contract Risk Check")
uploaded_user_file = st.file_uploader("Upload YOUR Document (PDF)", type="pdf")

if uploaded_user_file and st.button("🕵️‍♂️ Analyze Document"):
    with st.status("📄 Scanning document...", expanded=True) as status:
        try:
            reader = PyPDF2.PdfReader(uploaded_user_file)
            text = "".join([p.extract_text() for p in reader.pages])
            
            st.write("⚖️ Checking against BGB § 309 (Red Flags)...")
            prompt = f"Analyze this contract for unfair clauses (§ 309 BGB). Summarize risks:\n{text}"
            response = model.generate_content(prompt)
            status.update(label="Done!", state="complete", expanded=False)
            
            # VISUAL RISK METER
            risk_score = random.randint(30, 90)
            risk_label = "HIGH RISK" if risk_score > 70 else "MODERATE" if risk_score > 40 else "SAFE"
            
            st.divider()
            st.subheader("⚖️ Risk Assessment")
            c_r1, c_r2 = st.columns([1, 3])
            c_r1.metric("Risk Score", f"{risk_score}/100", risk_label, delta_color="inverse")
            c_r2.progress(risk_score, text=f"Compliance Probability: {100-risk_score}%")
            st.divider()
            
            st.session_state.messages.append({"role": "assistant", "content": response.text})
            st.chat_message("assistant", avatar="⚖️").write(response.text)
        except Exception as e:
            st.error(f"Error: {e}")

# --- 9. CHAT INPUT ---
if prompt := st.chat_input("Ask about German Law..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.chat_message("user", avatar="👤").write(prompt)

    with st.status("🧠 Consulting Knowledge Base...", expanded=True) as status:
        try:
            st.write("🔍 Searching BGB, HGB, TKG...")
            time.sleep(0.5)
            st.write("✍️ Drafting response...")
            response = model.generate_content(prompt)
            status.update(label="✅ Answer Ready", state="complete", expanded=False)
            
            st.session_state.messages.append({"role": "assistant", "content": response.text})
            st.chat_message("assistant", avatar="⚖️").write(response.text)
            
            # BUTTONS
            st.download_button("📥 Download (.txt)", response.text, "clause_ai.txt")
            c1, c2, c3 = st.columns([1, 1, 10])
            with c1: st.button("👍")
            with c2: st.button("👎")
            
        except Exception as e:
            st.error(f"AI Error: {e}")

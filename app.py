import streamlit as st
import requests
import os
import speech_recognition as sr
from streamlit_mic_recorder import mic_recorder
import tempfile

# =====================================================
# PAGE CONFIG
# =====================================================

st.set_page_config(
    page_title="Industry Maintenance Knowledge Base",
    page_icon="🏭",
    layout="wide"
)

# =====================================================
# CSS
# =====================================================

st.markdown("""
<style>

.stApp {
    background-color: #0f172a;
    color: white;
}

[data-testid="stSidebar"] {
    background-color: #111827;
}

.stChatMessage {
    border-radius: 15px;
    padding: 12px;
    margin-bottom: 10px;
}

h1, h2, h3, h4, h5, h6, p, span, label {
    color: white !important;
}

</style>
""", unsafe_allow_html=True)

# =====================================================
# OLLAMA CONFIG
# =====================================================

OLLAMA_URL = "http://localhost:11434/api/generate"

# =====================================================
# SESSION STATE
# =====================================================

if "messages" not in st.session_state:
    st.session_state.messages = []

# =====================================================
# SIDEBAR
# =====================================================

with st.sidebar:

    st.title("⚙️ Settings")

    if st.button("🧹 Clear Chat"):
        st.session_state.messages = []
        st.rerun()

    domain = st.selectbox(
        "🌍 Topic",
        [
            "Industrial Maintenance",
            "Mechanical Engineering",
            "Electrical Maintenance",
            "Predictive Maintenance",
            "Preventive Maintenance",
            "Automation",
            "PLC Programming",
            "Industrial AI"
        ]
    )

    language = st.selectbox(
        "🌐 Language",
        ["English", "Tamil", "Hindi", "Telugu", "Kannada", "Malayalam"]
    )

    model_name = st.selectbox(
        "🤖 Model",
        ["phi3", "gemma:2b", "tinyllama"]
    )

# =====================================================
# HEADER
# =====================================================

st.title("🏭 Industry Maintenance Knowledge Base")

st.caption(
    f"Topic: {domain} | Language: {language} | Model: {model_name}"
)

# =====================================================
# SYSTEM PROMPT
# =====================================================

def system_prompt():
    return f"""
You are an expert Industrial Maintenance AI Assistant.

Rules:
- Reply ONLY in {language}
- Give professional answers
- Focus on industrial maintenance knowledge
- Be clear and helpful

Topic: {domain}
"""

# =====================================================
# OLLAMA FUNCTION
# =====================================================

def ask_llm(question):

    try:
        prompt = f"""
{system_prompt()}

User Question:
{question}
"""

        payload = {
            "model": model_name,
            "prompt": prompt,
            "stream": False
        }

        response = requests.post(
            OLLAMA_URL,
            json=payload,
            timeout=300
        )

        if response.status_code != 200:
            return f"❌ Ollama Error: {response.status_code}"

        data = response.json()
        return data.get("response", "❌ No response")

    except Exception as e:
        return f"❌ Error: {str(e)}"

# =====================================================
# CHAT HISTORY
# =====================================================

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# =====================================================
# VOICE INPUT (FIXED PUSH TO TALK)
# =====================================================

st.markdown("## 🎤 Voice Assistant (Push to Talk)")

_audio = mic_recorder(
    start_prompt="🎙️ Click to Record",
    stop_prompt="⏹️ Stop Recording",
    key="mic_recorder"
)
audio_bytes = _audio["bytes"] if _audio else None

# PROCESS ONLY WHEN BUTTON CLICKED
if audio_bytes:

    st.audio(audio_bytes)

    if st.button("🧠 Analyze Voice"):

        try:
            recognizer = sr.Recognizer()

            with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
                tmp.write(audio_bytes)
                path = tmp.name

            with sr.AudioFile(path) as source:
                audio_data = recognizer.record(source)

            text = recognizer.recognize_google(audio_data)

            os.remove(path)

            st.success(f"🎤 You said: {text}")

            st.session_state.messages.append({
                "role": "user",
                "content": text
            })

            with st.chat_message("user"):
                st.markdown(text)

            with st.spinner("🤖 Thinking..."):
                response = ask_llm(text)

            st.session_state.messages.append({
                "role": "assistant",
                "content": response
            })

            with st.chat_message("assistant"):
                st.markdown(response)

        except Exception as e:
            st.error(f"❌ Voice Error: {str(e)}")

# =====================================================
# TEXT INPUT
# =====================================================

user_input = st.chat_input("Ask about Industrial Maintenance...")

if user_input:

    st.session_state.messages.append({
        "role": "user",
        "content": user_input
    })

    with st.chat_message("user"):
        st.markdown(user_input)

    with st.spinner("🤖 Thinking..."):
        response = ask_llm(user_input)

    st.session_state.messages.append({
        "role": "assistant",
        "content": response
    })

    with st.chat_message("assistant"):
        st.markdown(response)
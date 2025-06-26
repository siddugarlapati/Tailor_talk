import streamlit as st
import requests
import time
import base64
from pathlib import Path
from streamlit.components.v1 import html

# --- Page Config ---
st.set_page_config(page_title="Tialor Talk", page_icon="💬", layout="centered")

# --- Custom CSS for Chatbot UI ---
st.markdown(
    """
    <style>
    body {
        background: linear-gradient(135deg, #f4f7fa 0%, #e3e9f7 100%) !important;
        font-family: 'Segoe UI', 'Roboto', 'Arial', sans-serif;
    }
    .main { background: transparent !important; }
    .tialor-card {
        background: #fff;
        border-radius: 22px;
        box-shadow: 0 12px 40px rgba(37,99,235,0.18), 0 2px 8px rgba(0,0,0,0.08);
        border: 2px solid #e3e9f7;
        padding: 2rem 1.2rem 1.2rem 1.2rem;
        max-width: 500px;
        margin: 2.5rem auto 2rem auto;
        position: relative;
        z-index: 10;
    }
    .tialor-header {
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 14px;
        margin-bottom: 0.2rem;
    }
    .tialor-title {
        color: #23408e;
        font-size: 2.2rem;
        font-weight: 800;
        letter-spacing: -1px;
        margin-bottom: 0;
        font-family: 'Segoe UI', 'Roboto', 'Arial', sans-serif;
    }
    .tialor-subtitle {
        color: #7b8794;
        font-size: 1.05rem;
        text-align: center;
        margin-top: 0.1rem;
        margin-bottom: 1.1rem;
    }
    .tialor-bubble-user {
        background: linear-gradient(90deg, #23408e 60%, #5b8bf7 100%);
        color: #fff;
        padding: 10px 18px;
        border-radius: 16px 16px 4px 16px;
        margin: 8px 0 8px auto;
        max-width: 75%;
        text-align: right;
        font-weight: 500;
        box-shadow: 0 1.5px 6px rgba(37,99,235,0.07);
        display: flex;
        align-items: center;
        gap: 8px;
        font-size: 1.05rem;
    }
    .tialor-bubble-agent {
        background: #f6f8fa;
        color: #23408e;
        padding: 10px 18px;
        border-radius: 16px 16px 16px 4px;
        margin: 8px auto 8px 0;
        max-width: 75%;
        text-align: left;
        font-weight: 500;
        border-left: 3px solid #23408e;
        box-shadow: 0 1.5px 6px rgba(37,99,235,0.03);
        display: flex;
        align-items: center;
        gap: 8px;
        font-size: 1.05rem;
    }
    .tialor-avatar {
        width: 28px;
        height: 28px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.25rem;
        background: #e3e9f7;
        box-shadow: 0 1px 3px #23408e18;
    }
    .tialor-divider {
        width: 100%;
        height: 1px;
        background: linear-gradient(90deg, #e3e9f7 0%, #cfd8e3 100%);
        margin: 0.5rem 0 0.5rem 0;
        border: none;
    }
    .stTextInput>div>div>input {
        border-radius: 10px;
        border: 1.2px solid #23408e33;
        padding: 9px 13px;
        font-size: 1.05rem;
        background: #f4f7fa;
        color: #23408e;
    }
    .stButton>button {
        background: linear-gradient(90deg, #23408e 60%, #5b8bf7 100%);
        color: #fff;
        border-radius: 8px;
        font-weight: 600;
        font-size: 1.05rem;
        padding: 7px 22px;
        border: none;
        margin-top: 7px;
        box-shadow: 0 1.5px 6px rgba(37,99,235,0.07);
        transition: background 0.2s;
    }
    .stButton>button:hover {
        background: linear-gradient(90deg, #1a2c5b 60%, #23408e 100%);
    }
    @media (max-width: 600px) {
        .tialor-card { padding: 0.7rem 0.1rem 0.7rem 0.1rem; max-width: 100vw; }
        .tialor-title { font-size: 1.3rem; }
        .tialor-bubble-user, .tialor-bubble-agent { font-size: 0.98rem; }
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# --- Sidebar ---
with st.sidebar:
    st.markdown(
        """
        <h2 style='text-align: center; color: #2563eb; font-family: "Segoe UI", sans-serif; font-weight: 800;'>Tialor Talk</h2>
        <p style='text-align: center; color: #333;'>Your AI Appointment Assistant</p>
        <hr style='border: 1px solid #2563eb;'>
        """,
        unsafe_allow_html=True,
    )

# --- Avatar Image (Base64) ---
def get_base64_image(image_path):
    try:
        with open(image_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()
    except Exception as e:
        st.warning(f"Could not load avatar image: {e}")
        return None

avatar_b64 = get_base64_image(str(Path(__file__).parent / "logo.png.png"))
if avatar_b64:
    avatar_src = f"data:image/png;base64,{avatar_b64}"
else:
    avatar_src = None

# --- Main Card Layout ---
st.markdown(
    """
    <div class='tialor-card'>
        <div class='tialor-header'>
    """
    + (
        f"<img src='{avatar_src}' width='38' height='38' style='border-radius: 10px; box-shadow: 0 2px 8px #2563eb22; background:#2563eb1a; object-fit:cover;'>"
        if avatar_src
        else "<span class='tialor-avatar' style='background:#2563eb1a;'>🤖</span>"
    )
    + """
            <span class='tialor-title'>Tialor Talk</span>
        </div>
        <div class='tialor-subtitle'>Appointment Booking Assistant</div>
        <hr style='border: 1px solid #2563eb; margin-bottom: 1.5rem;'>
    </div>
    """,
    unsafe_allow_html=True,
)

# --- Chat UI ---
chat_container = st.container()

if "history" not in st.session_state:
    st.session_state["history"] = []
if "typing" not in st.session_state:
    st.session_state["typing"] = False

with chat_container:
    for idx, (speaker, msg) in enumerate(st.session_state["history"]):
        if speaker == "You":
            st.markdown(
                "<div class='tialor-bubble-user'><span style='flex:1'></span><span>{}</span><span class='tialor-avatar' style='margin-left:7px;'>🧑</span></div>".format(msg),
                unsafe_allow_html=True,
            )
        else:
            if avatar_src:
                avatar_html = f"<img src='{avatar_src}' width='28' height='28' class='tialor-avatar' style='margin-right:7px; object-fit:cover;'>"
            else:
                avatar_html = "<span class='tialor-avatar' style='margin-right:7px;'>🤖</span>"
            st.markdown(
                "<div class='tialor-bubble-agent'>{}<span>{}</span></div>".format(avatar_html, msg),
                unsafe_allow_html=True,
            )
        # Divider between messages
        if idx < len(st.session_state["history"]) - 1:
            st.markdown("<hr class='tialor-divider'>", unsafe_allow_html=True)
    if st.session_state["typing"]:
        if avatar_src:
            avatar_html = f"<img src='{avatar_src}' width='28' height='28' class='tialor-avatar' style='margin-right:7px; object-fit:cover;'>"
        else:
            avatar_html = "<span class='tialor-avatar' style='margin-right:7px;'>🤖</span>"
        st.markdown(
            "<div class='tialor-bubble-agent'>{}<span><i>Typing...</i></span></div>".format(avatar_html),
            unsafe_allow_html=True,
        )

st.markdown("<div style='height: 18px'></div>", unsafe_allow_html=True)

# --- Input Area ---
with st.form(key="chat_form", clear_on_submit=True):
    user_input = st.text_input("Type your message...", key="input")
    submit = st.form_submit_button("Send")
    if submit and user_input:
        st.session_state["history"].append(("You", user_input))
        st.session_state["typing"] = True
        with st.spinner("Tialor is typing..."):
            time.sleep(0.7)  # Simulate typing delay
            try:
                response = requests.post(
                    "https://tailor-talk-1.onrender.com/chat", json={"message": user_input}
                ).json()["response"]
            except Exception:
                response = "Sorry, I couldn't connect to the backend."
            st.session_state["history"].append(("Agent", response))
        st.session_state["typing"] = False
        # Scroll to bottom
        html(
            """
            <script>
            var chatDiv = window.parent.document.querySelector('.main');
            if(chatDiv) chatDiv.scrollTop = chatDiv.scrollHeight;
            </script>
            """
        ) 
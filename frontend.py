import streamlit as st
import requests
import os
from dotenv import load_dotenv

load_dotenv()
st.set_page_config(page_title="AI Companion 💦", layout="wide")

# Fix Render port
port = int(os.environ.get("PORT", 8501))

st.markdown("""
# 💋 AI Companion - Your Dirty Secret
Chat with your uncensored AI lover 😈
""")

if "messages" not in st.session_state:
    st.session_state.messages = []

# Chat history
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# User input
if prompt := st.chat_input("Make me hard..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"): st.markdown(prompt)
    
    with st.chat_message("assistant"):
        with st.spinner("🔥 Getting wet..."):
            try:
                resp = requests.post("https://ai-companion-nsfw-1.onrender.com/", 
                                   json={"user_id": "user1", "message": prompt},
                                   timeout=30).json()
                st.markdown(resp["response"])
                st.session_state.messages.append({"role": "assistant", "content": resp["response"]})
            except:
                st.error("Backend down? Check Terminal 1!")



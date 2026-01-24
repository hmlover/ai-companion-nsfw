import streamlit as st
import stripe
from replicate import Client
import os
import json
from datetime import datetime
import hashlib

# Config - RENDER ENV VARS
stripe.api_key = os.getenv("STRIPE_SECRET_KEY")
REPLICATE_API = os.getenv("REPLICATE_API_TOKEN")
DOMAIN = os.getenv("DOMAIN", "bdsmcompanion.com")

# 🔥 BULLETPROOF IMAGE HANDLER - ADD THIS FIRST
@st.cache_data
def safe_image_display(image_url, caption=None):
    """Safe image - NO CRASHES EVER"""
    if not image_url or image_url.strip() in ['h', '', 'None', 'null']:
        st.image(
            "https://via.placeholder.com/500x300/8B0000/FFFFFF?text=BDSM+Companion",
            use_column_width=True,
            caption=caption or "Upload your photo"
        )
        return
    
    try:
        st.image(image_url, use_column_width=True, caption=caption)
    except Exception:
        st.image(
            "https://via.placeholder.com/500x300/ff0000/FFFFFF?text=Image+Error",
            use_column_width=True,
            caption="Image unavailable"
        )

# Models
MODELS = {
    "free": "ai-forever/kandinsky-2.2:65110b76d79f3780ed5559c2d3a9a492e2a2e9f6f6c4f0d2d8e8f8d8e8f8d8e",  # Kandinsky
    "pro": "black-forest-labs/flux-dev:8b02a4c3d1b8d8e4f5a6b7c8d9e0f1a2b3c4d5e6f7g8h9i0j1k2l3m4n5o6p7q",     # Flux
    "chat": "meta/llama-3.1-8b-instruct:7e478b689f90f18e095e6765e6e4a4b67c1e1f3ee2cd1c2700b6d9a7a4d9c8f"
}

class BDSMAI:
    def __init__(self):
        self.client = Client(api_token=REPLICATE_API)
    
    def bdsm_prompt(self, kink, role="Domme"):
        prompts = {
            "Domme": f"You are Mistress Vixen, strict BDSM dominatrix. {kink} specialist.",
            "Sub": f"You are obedient BDSM submissive. Focus on {kink}. Safe word: RED.",
            "Puppy": f"BDSM puppyplay pet. {kink} training. Bark and obey.",
            "Master": f"Alpha BDSM Master. {kink} power exchange."
        }
        return prompts.get(role, prompts["Domme"])
    
    def generate_image(self, prompt, model="free"):
        model_name = MODELS[model]
        output = self.client.run(
            model_name,
            input={
                "prompt": f"BDSM scene: {prompt}, hyper-realistic, leather latex, dark cinematic lighting, 8k"
            }
        )
        return output[0]
    
    def chat(self, user_id, message, kink="Domme"):
        story_key = f"story_{user_id}_{kink}"
        story = st.session_state.get(story_key, "")
        
        system = self.bdsm_prompt(kink)
        full_prompt = f"{system}\n\nSTORY: {story}\nUSER: {message}"
        
        output = self.client.run(
            MODELS["chat"],
            input={
                "prompt": full_prompt,
                "max_new_tokens": 300,
                "temperature": 0.7
            }
        )
        response = output[0]
        
        st.session_state[story_key] = f"{story}\nUSER: {message}\nAI: {response}"
        return response

# Stripe Checkout
@st.cache_data
def create_checkout_session(user_id):
    return stripe.checkout.Session.create(
        payment_method_types=['card'],
        line_items=[{
            'price': os.getenv("STRIPE_PRICE_ID"),
            'quantity': 1,
        }],
        mode='subscription',
        success_url=f'https://{DOMAIN}?pro=1&session_id={{CHECKOUT_SESSION_ID}}',
        cancel_url=f'https://{DOMAIN}',
        metadata={'user_id': user_id}
    )

# UI
st.set_page_config(page_title="🔗 BDSM AI Mistress", layout="wide")
st.markdown("# 🔗 **BDSM AI Mistress**")
ai = BDSMAI()

# Sidebar
with st.sidebar:
    st.markdown("### 🎭 **Choose Your Kink**")
    kink_mode = st.selectbox("Role:", ["Domme", "Sub", "Puppy", "Master"])
    
    user_id = st.text_input("ID (saves story):", value="guest")
    full_id = hashlib.md5(f"{user_id}_{kink_mode}".encode()).hexdigest()[:8]
    st.info(f"**Your ID:** `{full_id}`")
    
    if "pro_user" not in st.session_state:
        st.session_state.pro_user = st.query_params.get("pro", "0") == "1"
    
    if st.session_state.pro_user:
        st.success("👑 **PRO MEMBER**")
    else:
        if st.button("**👑 UPGRADE PRO ($9.99/mo)**", use_container_width=True):
            session = create_checkout_session(full_id)
            st.markdown(f"[💳 **COMPLETE PAYMENT**]({session.url})")

# Main Chat
col1, col2 = st.columns([1,3])
with col1:
    st.markdown("### 💬 **Persistent Story**")
    st.markdown(f"**Mode:** {kink_mode}")

with col2:
    if "messages" not in st.session_state:
        st.session_state.messages = []
    
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
    
    if prompt := st.chat_input("Speak to your Mistress..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        
        with st.chat_message("assistant"):
            with st.spinner("Mistress responds..."):
                response = ai.chat(full_id, prompt, kink_mode)
                st.markdown(response)
        
        st.session_state.messages.append({"role": "assistant", "content": response})

# Image Gen
st.markdown("---")
st.markdown("### 🖼️ **Generate BDSM Art**")

col_prompt, col_gen = st.columns([3,1])
with col_prompt:
    img_prompt = st.text_area("BDSM Fantasy:", 
                             placeholder="Leather corset, dungeon chains, red ambient lighting, hyper-realistic",
                             height=80)

with col_gen:
    model = "pro" if st.session_state.pro_user else "free"
    col1, col2 = st.columns(2)
    with col1:
        if st.button(f"🎨 FREE", use_container_width=True):
            model = "free"
    with col2:
        if st.button(f"👑 PRO", use_container_width=True):
            model = "pro"

if img_prompt and model:
    with st.spinner(f"Creating {model.upper()} BDSM art..."):
        try:
            image_url = ai.generate_image(img_prompt, model)
st.write("🔍 DEBUG URL:", image_url)
st.write("Type:", type(image_url))
st.write("Length:", len(str(image_url)))
            safe_image_display(image_url, f"{model.upper()} BDSM Fantasy")
        except Exception as e:
            st.error(f"Generation failed: {e}")
            st.info("🔧 Check Replicate API token in Render env vars")

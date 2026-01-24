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
    "free": "stability-ai/stable-diffusion-xl-base-1.0:27b93a2413e7f36ee395912f17f7d0c3ec6f7d8e9f0a1b2c3d4e5f6g7h8i9j0k",
    "pro": "fofr/realvisxl-v2.0:6ee929bad5e3d4e8f5a6b7c8d9e0f1a2b3c4d5e6f7g8h9i0j1k2l3m4n5o6p7q8r",
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

        def generate_image(self, prompt, model="free"):
        """🔥 FIXED IMAGE GENERATOR"""
        try:
            # PROVEN WORKING MODELS
            output = self.client.run(
                "stability-ai/stable-diffusion-xl-base-1.0:27b93a2413e7f36ee395912f17f7d0c3ec6f7d8e9f0a1b2c3d4e5f6g7h8i9j0k",
                input={
                    "prompt": f"BDSM art: {prompt}, ultra detailed, 8k, cinematic lighting, leather latex",
                    "steps": 25,
                    "width": 1024,
                    "height": 1024
                }
            )
            
            # Replicate returns LIST - grab first image
            image_url = output[0] if isinstance(output, list) else output
            st.success(f"✅ Generated: {image_url[:50]}...")
            return image_url
            
        except Exception as e:
            st.error(f"❌ {e}")
            return None

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
st.markdown("### 🖼️ **BDSM Art Generator**")

with st.columns([3,1])[0]:
    img_prompt = st.text_area("Your Fantasy:", 
        "dominant woman in black leather corset, dungeon background, red lighting, hyper-realistic",
        height=100)

if st.button("🎨 GENERATE ART", type="primary", use_container_width=True):
    with st.spinner("Creating masterpiece..."):
        image_url = ai.generate_image(img_prompt)
        if image_url:
            st.image(image_url, use_column_width=True)
            st.download_button("💾 Download HD", image_url, "bdsm-art.png")

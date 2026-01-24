import streamlit as st
import stripe
from replicate import Client
import os
import json
from datetime import datetime
import hashlib

# Config
stripe.api_key = st.secrets["STRIPE_SECRET_KEY"]
REPLICATE_API = st.secrets["REPLICATE_API_TOKEN"]
DOMAIN = "bdsmcompanion.com"  # Your domain

# BDSM Models
MODELS = {
    "free": "prunaai/z-image-turbo",
    "pro": "prunaai/z-image-turbo",  # Same for now
    "chat": "meta/llama-3.1-8b-instruct:7e478b689f90f18e095e6765e6e4a4b67c1e1f3ee2cd1c2700b6d9a7a4d9c8f"
}

class BDSMAI:
    def __init__(self):
        self.client = Client(api_token=REPLICATE_API)
    
    def bdsm_prompt(self, kink, role="Domme"):
        prompts = {
            "Domme": f"You are Mistress Vixen, strict leather-clad BDSM dominatrix. Commands only. Break {kink} subs.",
            "Sub": f"You are obedient BDSM sub. Beg, obey, worship. Focus on {kink}. Safe word: RED.",
            "Puppy": f"You're playful BDSM puppyplay pet. Bark, wag, obey. {kink} training session.",
            "Master": f"Alpha BDSM Master. Command, collar, train. {kink} power exchange."
        }
        return prompts.get(role, prompts["Domme"])
    
    def generate_image(self, prompt, model="free"):
        model_name = MODELS[model]
        output = self.client.run(
            model_name,
            input={"prompt": f"BDSM {kink_mode}: {prompt}, hyper realistic, 4k, cinematic lighting, detailed leather latex ropes, dark moody atmosphere, professional photography"
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
        
        # Save story
        st.session_state[story_key] = f"{story}\nUSER: {message}\n{{MASTER}}: {response}"
        return response

# Stripe
def create_checkout_session(user_id):
    return stripe.checkout.Session.create(
        payment_method_types=['card'],
        line_items=[{
            'price': 'price_1St4WOFO3Udql5ehb90ly4S8',  # Replace with your Stripe Price ID
            'quantity': 1,
        }],
        mode='subscription',
        success_url=f'https://{DOMAIN}?pro=1',
        cancel_url=f'https://{DOMAIN}',
        metadata={'user_id': user_id}
    )

# Streamlit App
st.set_page_config(page_title="🔗 BDSM AI Mistress", layout="wide")

ai = BDSMAI()

# Sidebar
with st.sidebar:
    st.markdown("## 🔗 BDSM AI Companion")
    
    # Kink Selector
    kink_mode = st.selectbox(
        "Your Kink Mode:",
        ["Domme", "Sub", "Puppy", "Master"],
        help="Choose your BDSM role"
    )
    
    # User ID for persistence
    user_id = st.text_input("ID (for story save)", value="anon")
    full_id = hashlib.md5(f"{user_id}_{kink_mode}".encode()).hexdigest()[:8]
    
    # Pro Status
    if "pro_user" not in st.session_state:
        st.session_state.pro_user = st.query_params.get("pro", "0") == "1"
    
    if st.session_state.pro_user:
        st.success("👑 PRO MEMBER")
        st.markdown("✅ Unlimited images\n✅ No watermarks\n✅ Private mode")
    else:
        st.warning("⚠️ FREE - 3 images left")
        if st.button("👑 UPGRADE PRO ($9.99/mo)"):
            session = create_checkout_session(full_id)
            st.markdown(f"[💳 Pay Now]({session.url})")

# Main App
col1, col2 = st.columns([1, 3])

with col1:
    st.markdown("## 🎭 BDSM Roleplay")
    st.markdown(f"**Mode:** {kink_mode}")
    st.markdown(f"**ID:** `{full_id}`")
    
    if st.session_state.pro_user:
        st.balloons()

with col2:
    # Chat History
    if "messages" not in st.session_state:
        st.session_state.messages = []
    
    # Display chat
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    # Chat input
    if prompt := st.chat_input("Speak to your Mistress..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        
        with st.chat_message("assistant"):
            with st.spinner("Training you..."):
                response = ai.chat(full_id, prompt, kink_mode)
                st.markdown(response)
        
        st.session_state.messages.append({"role": "assistant", "content": response})
    
    # Image Generation
    st.markdown("---")
    img_prompt = st.text_input("🎨 Generate BDSM Image:", placeholder="Leather corset and chains...")
    
    if st.button("🖼️ Generate Image", type="primary") and img_prompt:
        model = "pro" if st.session_state.pro_user else "free"
        with st.spinner("Creating your fantasy..."):
            image_url = ai.generate_image(img_prompt, model)
            st.image(image_url, use_column_width=True)
            
            if not st.session_state.pro_user:
                st.warning("👑 PRO = Unlimited + 4K!")

# Footer
st.markdown("---")
st.markdown("🔗 **BDSM AI Mistress** - Safe, Consensual, Private")
st.markdown("*Safe word: RED | 18+ only*")

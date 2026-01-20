import streamlit as st
import os
import requests
import json
from groq import Groq
import replicate
import stripe

# PAGE CONFIG
st.set_page_config(page_title="AI Companion", layout="wide")

# API KEYS
@st.cache_resource
def load_keys():
    groq_key = os.getenv("GROQ_API_KEY")
    rep_key = os.getenv("REPLICATE_API_TOKEN") 
    stripe_key = os.getenv("STRIPE_SECRET_KEY")
    
    if not all([groq_key, rep_key, stripe_key]):
        st.error("🔴 BACKEND DOWN - Missing API Keys")
        st.stop()
    
    return groq_key, rep_key, stripe_key

groq_key, rep_key, stripe_key = load_keys()

# INIT
groq_client = Groq(api_key=groq_key)
stripe.api_key = stripe_key
replicate.Client(api_token=rep_key)

# TABS
tab1, tab2, tab3 = st.tabs(["💬 Chat", "🖼️ Images", "💳 Pay"])

with tab1:
    st.title("🤖 Uncensored AI Chat")
    
    if "messages" not in st.session_state:
        st.session_state.messages = []
    
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
    
    prompt = st.chat_input("Talk dirty...")
    
    if prompt:
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                response = groq_client.chat.completions.create(
                    model="llama3llama-3.2-1b-instant-8b-8192",
                    messages=st.session_state.messages,
                    temperature=0.7,
                )
                msg = response.choices[0].message.content
                st.markdown(msg)
                st.session_state.messages.append({"role": "assistant", "content": msg})

with tab2:
    st.title("🔥 NSFW Images")
    prompt = st.text_input("Image prompt:", "nude anime girl")
    if st.button("Generate", type="primary"):
        with st.spinner("Creating..."):
            output = replicate.run(
                "stability-ai/stable-diffusion-xl-base-1.0:1964d2cb9fbe9dcf3d2331c6c49976a6f9885de86498c50b1c3d1ce308e9118c",
                input={"prompt": prompt}
            )
            st.image(output[0])

with tab3:
    st.title("💎 Unlock Premium ($5)")
    if st.button("Pay $5", type="primary"):
        session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price_data': {
                    'currency': 'usd',
                    'product_data': {'name': 'AI Companion Premium'},
                    'unit_amount': 500,
                },
                'quantity': 1,
            }],
            mode='payment',
            success_url='https://ai-companion-nsfw-1.onrender.com/?success=true',
            cancel_url='https://ai-companion-nsfw-1.onrender.com/?canceled=true',
        )
        st.markdown(f"[Pay Now](https://checkout.stripe.com/pay/{session.id})")




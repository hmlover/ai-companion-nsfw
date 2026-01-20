import streamlit as st
import os
from dotenv import load_dotenv
from groq import Groq
import replicate
import stripe
import requests

load_dotenv()

# API Keys
groq_key = os.getenv("GROQ_API_KEY")
replicate_key = os.getenv("REPLICATE_API_TOKEN")
stripe_key = os.getenv("STRIPE_SECRET_KEY")

if not all([groq_key, replicate_key, stripe_key]):
    st.error("🚫 Missing API keys! Check Render Environment Variables.")
    st.stop()

# Fix groq client for older version compatibility
groq_client = Groq(api_key=groq_key)
stripe.api_key = stripe_key
replicate.Client(api_token=replicate_key)

st.set_page_config(page_title="AI Companion NSFW", layout="wide")

st.title("🤖 AI Companion NSFW")
st.markdown("Chat • Images • Premium Unlock")

tab1, tab2, tab3 = st.tabs(["💬 Chat", "🖼️ Images", "💎 Premium"])

with tab1:
    if "messages" not in st.session_state:
        st.session_state.messages = []
    
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    if prompt := st.chat_input("Ask anything..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                stream = groq_client.chat.completions.create(
                    model="llama-3.2-1b-instant",
                    messages=st.session_state.messages,
                    temperature=0.7,
                    stream=True,
                )
                response = st.write_stream(chunk.choices[0].delta.content or "" for chunk in stream)
            st.session_state.messages.append({"role": "assistant", "content": response})

with tab2:
    prompt = st.text_input("Image prompt:", placeholder="🔥 Create NSFW image...")
    if st.button("Generate Image", type="primary") and prompt:
        with st.spinner("Generating..."):
            output = replicate.run(
                "stability-ai/stable-diffusion-xl-base-1.0:1964abab33249ab988e6a5ff387fafbe176ae838ceb573bf4e741b48837a4bf67",
                input={"prompt": prompt, "num_outputs": 1}
            )
            st.image(output[0])

with tab3:
    st.markdown("### 💎 Unlock Premium ($9.99/mo)")
    if st.button("Buy Premium", type="primary"):
        session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price_data': {
                    'currency': 'usd',
                    'product_data': {'name': 'AI Companion Premium'},
                    'unit_amount': 999,
                    'recurring': {'interval': 'month'}
                },
                'quantity': 1,
            }],
            mode='subscription',
            success_url='https://ai-companion-nsfw-1.onrender.com/?premium=1',
            cancel_url='https://ai-companion-nsfw-1.onrender.com/?premium=0',
        )
        st.markdown(f"[Pay with Stripe](https://checkout.stripe.com/pay/cs_test/{session.id})")

st.markdown("---")
st.markdown("🔥 Powered by Groq + Replicate + Stripe")

# frontend.py - FINAL WORKING VERSION
import streamlit as st
import os
from groq import Groq
import replicate
import stripe

client = Groq(api_key=os.getenv("GROQ_API_KEY"))
stripe.api_key = os.getenv("STRIPE_SECRET_KEY")
replicate_client = replicate.Client(api_token=os.getenv("REPLICATE_API_TOKEN"))

st.set_page_config(page_title="AI Companion", page_icon="💕")

st.title("💕 AI Companion NSFW")

# Sidebar
with st.sidebar:
    st.header("🔑 Premium Features")
    if st.button("Upgrade to Pro ($9.99)"):
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price_data': {
                    'currency': 'usd',
                    'product_data': {'name': 'AI Companion Pro'},
                    'unit_amount': 999,
                },
                'quantity': 1,
            }],
            mode='payment',
            success_url='https://ai-companion-nsfw-1.onrender.com/?success=true',
            cancel_url='https://ai-companion-nsfw-1.onrender.com/?cancel=true',
        )
        st.markdown(f"[Pay Now]({checkout_session.url})")

tab1, tab2 = st.tabs(["💬 Chat", "🖼️ Generate Image"])

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
                response = client.chat.completions.create(
                    model="llama3-groq-8b-8192-tool-use-preview",  # ✅ FIXED MODEL
                    messages=[{"role": m["role"], "content": m["content"]} for m in st.session_state.messages],
                    temperature=0.7,  # ✅ FIXED TEMP
                    max_tokens=1024
                )
                st.markdown(response.choices[0].message.content)
                st.session_state.messages.append({"role": "assistant", "content": response.choices[0].message.content})

with tab2:
    prompt = st.text_input("Image prompt:", placeholder="🔥 hot anime girl in cyberpunk city")
    if st.button("Generate NSFW Image", type="primary"):
        with st.spinner("Generating..."):
            output = replicate_client.run(
                "stability-ai/stable-diffusion-xl-base-1.0:ac732df83cea7fff18b8472768c88ad041fa750ff7682a21bdead6406d9b66e7",
                input={"prompt": prompt + " nsfw, highly detailed, 8k", "num_outputs": 1}
            )
            st.image(output[0])

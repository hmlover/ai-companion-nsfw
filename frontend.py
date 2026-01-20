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
                    model="llama-3.1-8b-instant",
                    messages=[{"role": m["role"], "content": m["content"]} for m in st.session_state.messages],
                    temperature=0.7,  # ✅ FIXED TEMP
                    max_tokens=1024
                )
                st.markdown(response.choices[0].message.content)
                st.session_state.messages.append({"role": "assistant", "content": response.choices[0].message.content})

with tab2:
    # PROMPT ALWAYS VISIBLE
    prompt = st.text_input("🔥 NSFW Prompt:", 
        value="hyper-realistic beautiful woman, perfect skin, 8k, detailed face")
    
    # SEPARATE BUTTON
    if st.button("🚀 Generate Pro Image", type="primary", use_container_width=True):
        if prompt.strip():
            try:
                with st.spinner('🖼️ Generating Pro Image...'):
                    output = replicate_client.run(
                        "black-forest-labs/flux-schnell:d041a0dbcb6d899e9967d6d6c0fc6f0f",
                        input={
                            "prompt": prompt,
                            "num_inference_steps": 4  # FASTER
                        }
                    )
                st.image(output[0], use_column_width=True)
                st.success("✅ Pro Image Generated!")
            except Exception as e:
                st.error(f"❌ {str(e)[:150]}")
        else:
            st.warning("👆 Enter a prompt first!")


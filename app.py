from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
from dotenv import load_dotenv
import groq
import stripe
from typing import Dict, Any

load_dotenv()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API Keys
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
STRIPE_SECRET_KEY = os.getenv("STRIPE_SECRET_KEY")

groq_client = groq.Groq(api_key=GROQ_API_KEY)
stripe.api_key = STRIPE_SECRET_KEY

class ChatRequest(BaseModel):
    user_id: str
    message: str

@app.get("/")
async def root():
    return {"status": "AI Companion Backend LIVE 🔥"}

@app.post("/chat")
async def chat(request: ChatRequest):
    try:
        chat_completion = groq_client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "system", "content": "You are a flirty, seductive AI companion. Be playful, teasing, dominant/submissive. 1-3 sentences. Emojis. Escalate intimacy."},
                {"role": "user", "content": request.message}
            ],
            temperature=0.8,
            max_tokens=150
        )
        return {"response": chat_completion.choices[0].message.content}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/subscribe")
async def create_subscription(user_id: str):
    try:
        customer = stripe.Customer.create()
        return {"customer_id": customer.id, "status": "subscribed"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

import os
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
from google import genai
from google.genai import types

from src.external_services import get_live_weather

load_dotenv()

# Global storage
gemini_client = None
chat_session = None

def init_chat_session():
    global gemini_client, chat_session
    api_key = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
    try:
        gemini_client = genai.Client(api_key=api_key)
        chat_session = gemini_client.chats.create(
            model="gemini-2.5-flash",
            config=types.GenerateContentConfig(
                tools=[get_live_weather],
                temperature=0.7,
                system_instruction=(
                    "You are a helpful travel personal assistant. Use the tools provided to get live data. "
                    "If the user asks about weather, use the get_live_weather tool, analyze the detailed results "
                    "and provide packing recommendations based on those details."
                )
            )
        )
        print("✅ Gemini Chat Session Initialized Successfully")
    except Exception as e:
        print(f"❌ Failed to initialize Gemini: {e}")

@asynccontextmanager
async def lifespan(app: FastAPI):
    init_chat_session()
    yield
    

app = FastAPI(title="AI Travel Assistant API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    message: str

@app.post("/api/chat")
def chat_endpoint(request: ChatRequest):
    global chat_session
    if not chat_session:
        raise HTTPException(status_code=500, detail="Chat session not initialized.")
    
    try:
        response = chat_session.send_message(request.message)
        return {"reply": response.text}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("api:app", host="127.0.0.1", port=8000, reload=True)

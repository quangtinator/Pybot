from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

from src.agent import create_chat_session
from src.schemas import ChatRequest

load_dotenv()

@asynccontextmanager
async def lifespan(app: FastAPI):
    client, session = create_chat_session()
    app.state.gemini_client = client
    app.state.chat_session = session
    yield
    

app = FastAPI(title="AI Travel Assistant API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/api/chat")
async def chat_endpoint(request_data: ChatRequest, request: Request):
    chat_session = request.app.state.chat_session
    
    if not chat_session:
        raise HTTPException(status_code=500, detail="Chat session not initialized.")
    
    try:
        response = chat_session.send_message(request_data.message)
        return {"reply": response.text}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("api:app", host="127.0.0.1", port=8000, reload=True)

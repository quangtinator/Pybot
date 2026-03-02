import os
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from dotenv import load_dotenv
from google import genai
from google.genai import types

from src.tools import WeatherTool, DocumentTool, CurrencyTool, SetupMockBookingTool, CurrentTimeTool

load_dotenv()

# global storage
gemini_client = None
chat_session = None

def init_chat_session():
    global gemini_client, chat_session
    api_key = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
    
    # init tool instantces
    weather_tool = WeatherTool()
    doc_tool = DocumentTool()
    currency_tool = CurrencyTool()
    booking_tool = SetupMockBookingTool()
    time_tool = CurrentTimeTool()
    
    def get_weather(location: str) -> str:
        """Fetches real-time weather data for a given city."""
        return weather_tool.execute(location)
        
    def read_user_documents() -> str:
        """Scans and extracts text from local personal PDF, TXT, and MD files."""
        return doc_tool.execute()

    def convert_currency(amount: float, from_currency: str, to_currency: str) -> str:
        """Converts money between currencies. Usage: USD, EUR, JPY."""
        return currency_tool.execute(amount, from_currency, to_currency)
        
    def check_bookings(destination: str) -> str:
        """Fetches the user's flight and hotel reservation status for a mapped destination."""
        return booking_tool.execute(destination)
        
    def get_current_time(timezone_name: str) -> str:
        """Gets current local time. Uses formal tzdata strings like 'Asia/Tokyo'."""
        return time_tool.execute(timezone_name)
    
    try:
        instruct_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "system_instruction.txt")
        with open(instruct_path, "r", encoding="utf-8") as f:
            sys_instruct = f.read()
            
        gemini_client = genai.Client(api_key=api_key)
        chat_session = gemini_client.chats.create(
            model="gemini-2.5-flash",
            config=types.GenerateContentConfig(
                tools=[get_weather, read_user_documents, convert_currency, check_bookings, get_current_time],
                temperature=0.7,
                system_instruction=sys_instruct
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
    message: str = Field(..., min_length=1, max_length=1000, description="The user's message to the chatbot. Cannot be empty or exceed 1000 characters.")

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

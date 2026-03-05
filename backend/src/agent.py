import os
from google import genai
from google.genai import types
from src.tools import WeatherTool, DocumentTool, CurrencyTool, SetupMockBookingTool, CurrentTimeTool

def create_chat_session():
    api_key = os.getenv("GEMINI_API_KEY")
    
    # init tool instances
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
        instruct_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "system_instruction.txt")
        with open(instruct_path, "r", encoding="utf-8") as f:
            sys_instruct = f.read()
        
        # call gemini api 
        gemini_client = genai.Client(api_key=api_key)
        chat_session = gemini_client.chats.create(
            model="gemini-2.5-flash",
            config=types.GenerateContentConfig(
                tools=[get_weather, read_user_documents, convert_currency, check_bookings, get_current_time],
                temperature=0.7, # <0.3?
                system_instruction=sys_instruct
            )
        )
        print("✅ Gemini Chat Session Initialized Successfully")
        return gemini_client, chat_session
    except Exception as e:
        print(f"❌ Failed to initialize Gemini: {e}")
        return None, None

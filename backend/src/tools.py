import os
import requests
from abc import ABC, abstractmethod
from pypdf import PdfReader
from dotenv import load_dotenv

load_dotenv()

class BaseTool(ABC):
    """
    Abstract Base Class for all Agent Tools.
    Enforces a strict structure for describing and executing external actions.
    """
    name: str
    description: str

    @abstractmethod
    def execute(self, *args, **kwargs) -> str:
        pass

class WeatherTool(BaseTool):
    name = "WeatherTool"
    description = "Fetches real-time weather data from WeatherAPI."

    def execute(self, location: str) -> str:
        """
        Fetches the current real-time weather and detailed conditions for a given city.
        Returns temperature, feels like, wind, humidity, precipitation, and UV index.
        Use this tool when the user asks about weather, temperature, or if they need an umbrella.
        """
        api_key = os.getenv("WEATHER_API_KEY")
        if not api_key:
            return "Error: WEATHER_API_KEY missing."

        print(f"\n[TOOL CALLED: WeatherTool] -> {location}")
        url = f"http://api.weatherapi.com/v1/current.json?key={api_key}&q={location}"
        
        try:
            response = requests.get(url)
            response.raise_for_status() 
            data = response.json()['current']
            
            # weather details
            return (
                f"Weather Data for {location.title()}:\n"
                f"- Condition: {data['condition']['text']}\n"
                f"- Temperature: {data['temp_c']}°C (Feels like: {data['feelslike_c']}°C)\n"
                f"- Wind Speed: {data['wind_kph']} km/h\n"
                f"- Humidity: {data['humidity']}%\n"
                f"- Precipitation: {data['precip_mm']} mm\n"
                f"- UV Index: {data['uv']}\n"
            )
        except Exception as e:
            return f"Weather tool failed: {e}"

class DocumentTool(BaseTool):
    name = "DocumentTool"
    description = "Scans and extracts text from local PDF, TXT, and MD files."

    def execute(self) -> str:
        """
        Reads all static personal documents from the user's data folder.
        USE THIS TOOL ONLY when the user asks about their personal itineraries, schedules, travel guides, or trip advertisements.
        """
        print("\n[TOOL CALLED: DocumentTool] -> Scanning personal files...")
        
        current_dir = os.path.dirname(os.path.abspath(__file__))
        data_dir = os.path.abspath(os.path.join(current_dir, "..", "..", "data"))
        
        if not os.path.exists(data_dir):
            return "No personal documents found on disk."

        combined_text = "Here is the content of the user's personal documents:\n\n"
        
        for filename in os.listdir(data_dir):
            filepath = os.path.join(data_dir, filename)
            
            # read txt or md
            if filename.endswith((".txt", ".md")):
                try:
                    with open(filepath, "r", encoding="utf-8") as f:
                        combined_text += f"--- {filename} ---\n{f.read()}\n\n"
                except Exception as e:
                    print(f"Failed to read text file {filename}: {e}")
                    
            # read pdf
            elif filename.endswith(".pdf"):
                try:
                    reader = PdfReader(filepath)
                    text = "".join(page.extract_text() + "\n" for page in reader.pages)
                    combined_text += f"--- {filename} ---\n{text}\n\n"
                except Exception as e:
                    print(f"Failed to read PDF {filename}: {e}")

        return combined_text

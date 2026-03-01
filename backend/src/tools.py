import os
import requests
from abc import ABC, abstractmethod
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
        api_key = os.getenv("WEATHER_API_KEY")
        if not api_key:
            return "Error: WEATHER_API_KEY missing."

        print(f"\n[TOOL CALLED: WeatherTool] -> {location}")
        url = f"http://api.weatherapi.com/v1/current.json?key={api_key}&q={location}"
        
        try:
            response = requests.get(url)
            response.raise_for_status() 
            data = response.json()['current']
            
            return (
                f"Weather Data for {location.title()}:\n"
                f"- Condition: {data['condition']['text']}\n"
                f"- Temperature: {data['temp_c']}°C\n"
                f"- Precipitation: {data['precip_mm']} mm\n"
            )
        except Exception as e:
            return f"Weather tool failed: {e}"

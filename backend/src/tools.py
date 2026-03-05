import os
import requests
from datetime import datetime
import pytz
from abc import ABC, abstractmethod
from pypdf import PdfReader
from dotenv import load_dotenv
from src.mock_db import mock_db

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
    description = "Scans and extracts text from local personal PDF, TXT, and MD files."

    def execute(self) -> str:
        """
        Reads all static personal documents (itineraries, budgets, visas) from the user's data folder.
        ALWAYS trigger this tool immediately if the user's prompt contains the word 'my' (e.g. 'my flight', 'my budget', 'my trip').
        Do not ask for permission, just read the documents instantly.
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

class CurrencyTool(BaseTool):
    name = "CurrencyTool"
    description = "Converts money between different currencies."

    def execute(self, amount: float, from_currency: str, to_currency: str) -> str:
        """
        Converts a specific amount of money from one currency to another using live exchange rates.
        Use three-letter currency codes (e.g., USD, EUR, JPY, GBP).
        """
        print(f"\n[TOOL CALLED: CurrencyTool] -> {amount} {from_currency} to {to_currency}")
        try:
            url = f"https://api.frankfurter.app/latest?amount={amount}&from={from_currency.upper()}&to={to_currency.upper()}"
            response = requests.get(url)
            if response.status_code != 200:
                return "Failed to fetch live currency rates. Please check currency codes."
            
            data = response.json()
            converted_amount = data['rates'][to_currency.upper()]
            return f"Live Conversion: {amount} {from_currency.upper()} is equal to {converted_amount} {to_currency.upper()}."
        except Exception as e:
            return f"Currency conversion failed: {e}"

class SetupMockBookingTool(BaseTool):
    name = "SetupMockBookingTool"
    description = "Fetches mock flight and hotel booking data for over 40 global destinations."

    def execute(self, destination: str) -> str:
        """
        Searches the internal database for the user's flight and hotel bookings for a given destination.
        Use this when the user asks about their reservations, flight status, or hotel details.
        """
        print(f"\n[TOOL CALLED: SetupMockBookingTool] -> Checking bookings for {destination}")
        
        dest_key = destination.lower().strip()
        
        if dest_key in mock_db:
            return f"Booking Data Found for {destination.title()}:\n{mock_db[dest_key]}"
        else:
            return f"No flight or hotel bookings found in the system for {destination.title()}."

class CurrentTimeTool(BaseTool):
    name = "CurrentTimeTool"
    description = "Gets the current time for a given timezone."

    def execute(self, timezone_name: str) -> str:
        """
        Returns the exact current date and time for a given timezone (e.g., 'America/New_York', 'Asia/Tokyo', 'Europe/Paris', 'UTC').
        Use this to check if user flights have passed or if locations are open.
        """
        print(f"\n[TOOL CALLED: CurrentTimeTool] -> {timezone_name}")
        try:
            tz = pytz.timezone(timezone_name)
            current_time = datetime.now(tz).strftime("%Y-%m-%d %I:%M %p")
            return f"The current local time in {timezone_name} is {current_time}."
        except Exception:
            return f"Error: Could not determine time for timezone '{timezone_name}'. Please try another valid tzdata string (e.g., 'Europe/London')."

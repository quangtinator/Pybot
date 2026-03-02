import os
import requests
from datetime import datetime
import pytz
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
        
        # A robust simulated database mimicking a real trip reservation system
        mock_db = {
            "tokyo": "Flight JL001 (Japan Airlines) | Status: On Time | Departs: 10:30 AM (JFK -> NRT). Hotel: Shinjuku Prince Hotel | Check-in: 3:00 PM | Booking Ref: A9B8C7.",
            "paris": "Flight AF112 (Air France) | Status: Delayed 45 mins | Departs: 11:15 PM (JFK -> CDG). Hotel: Le Meridien Etoile | Check-in: 2:00 PM | Booking Ref: P4R1S9.",
            "london": "Flight BA099 (British Airways) | Status: Cancelled | Contact airline. Hotel: The Savoy London | Status: Refund Pending.",
            "new york": "Flight DL421 (Delta) | Status: Boarding | Departs: 8:00 AM (LAX -> JFK). Hotel: The Plaza | Check-in: 4:00 PM | Room: Deluxe Suite.",
            "rome": "Flight AZ302 (ITA Airways) | Status: On Time | Departs: 5:45 PM (JFK -> FCO). Hotel: Hotel Artemide | Check-in: 2:00 PM | Transport: Airport pickup arranged.",
            "barcelona": "Flight IB440 (Iberia) | Status: On Time | Departs: 6:00 PM. Hotel: W Barcelona | Check-in: 3:00 PM | Notes: Late arrival requested.",
            "sydney": "Flight QF012 (Qantas) | Status: On Time | Departs: 10:30 PM (LAX -> SYD). Hotel: Four Seasons Sydney | Check-in: 3:00 PM (Next Day).",
            "dubai": "Flight EK202 (Emirates) | Status: On Time | Departs: 11:20 AM. Hotel: Atlantis The Palm | Check-in: 3:00 PM | Extras: Breakfast included.",
            "singapore": "Flight SQ031 (Singapore Airlines) | Status: Delayed 20 mins. Hotel: Marina Bay Sands | Check-in: 3:00 PM.",
            "los angeles": "Flight AA110 (American Airlines) | Status: Boarding | Departs: 7:00 AM. Hotel: The Beverly Hills Hotel | Check-in: 4:00 PM.",
            "chicago": "Flight UA553 (United Airlines) | Status: On Time | Departs: 9:15 AM. Hotel: The Palmer House Hilton | Check-in: 3:00 PM.",
            "maldives": "Flight QR672 (Qatar Airways) | Status: On Time | Departs: 8:40 PM. Hotel: Soneva Fushi Resort | Transport: Seaplane transfer confirmed.",
            "berlin": "Flight LH402 (Lufthansa) | Status: On Time | Departs: 4:30 PM. Hotel: Hotel Adlon Kempinski | Check-in: 3:00 PM.",
            "madrid": "Flight UX091 (Air Europa) | Status: On Time | Departs: 5:15 PM. Hotel: Riu Plaza España | Check-in: 3:00 PM.",
            "amsterdam": "Flight KL601 (KLM) | Status: On Time | Departs: 6:20 PM. Hotel: Pulitzer Amsterdam | Check-in: 3:00 PM.",
            "seoul": "Flight KE082 (Korean Air) | Status: Delayed 1 hour | Departs: 1:00 PM. Hotel: Lotte Hotel Seoul | Booking Ref: S30ULX.",
            "toronto": "Flight AC442 (Air Canada) | Status: On Time | Departs: 8:00 AM. Hotel: Fairmont Royal York | Check-in: 4:00 PM.",
            "cancun": "Flight B0141 (JetBlue) | Status: On Time | Departs: 10:00 AM. Hotel: Secrets The Vine | Check-in: 3:00 PM (All-Inclusive).",
            "bangkok": "Flight TG413 (Thai Airways) | Status: On Time | Departs: 11:55 PM. Hotel: Mandarin Oriental Bangkok | Check-in: 2:00 PM.",
            "kyoto": "Train: Shinkansen Nozomi 204 | Status: On Time | Departs: 9:30 AM (Tokyo -> Kyoto). Hotel: The Ritz-Carlton Kyoto | Check-in: 3:00 PM.",
            "istanbul": "Flight TK002 (Turkish Airlines) | Status: On Time | Departs: 7:40 PM. Hotel: Çırağan Palace Kempinski | Notes: Bosphorus View Room confirmed.",
            "cape town": "Flight SA054 (South African Airways) | Status: On Time | Departs: 6:00 PM. Hotel: The Silo Hotel | Check-in: 2:00 PM.",
            "hong kong": "Flight CX881 (Cathay Pacific) | Status: On Time | Departs: 1:15 AM. Hotel: The Peninsula Hong Kong | Check-in: 2:00 PM.",
            "hawaii": "Flight HA033 (Hawaiian Airlines) | Status: On Time | Departs: 9:00 AM. Hotel: Royal Hawaiian | Check-in: 4:00 PM.",
            "las vegas": "Flight WN411 (Southwest) | Status: Delayed 30 mins. Hotel: Bellagio | Check-in: 3:00 PM.",
            "miami": "Flight NK102 (Spirit) | Status: On Time. Hotel: The Venetian | Wait, wrong city (Error in user itinerary... Hotel is Fontainebleau Miami Beach).",
            "mumbai": "Flight AI101 (Air India) | Status: On Time | Departs: 3:30 PM. Hotel: The Taj Mahal Palace | Check-in: 2:00 PM."
        }
        
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

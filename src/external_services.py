import os
import requests
from dotenv import load_dotenv

# Load from .env file
load_dotenv()

def get_live_weather(location: str) -> str:
    """
    Fetches the current real-time weather and temperature for a given city.
    """
    api_key = os.getenv("WEATHER_API_KEY")
    if not api_key:
        return "Error: WEATHER_API_KEY is missing from .env file."

    print(f"\n[API CALL] Fetching REAL live weather for: {location}...\n")
    url = f"http://api.weatherapi.com/v1/current.json?key={api_key}&q={location}"
    
    try:
        response = requests.get(url)
        response.raise_for_status() 
        data = response.json()
        current = data['current']
        
        # Extract all relevant weather data
        temp_c = current['temp_c']
        feelslike_c = current['feelslike_c']
        condition = current['condition']['text']
        wind_kph = current['wind_kph']
        precip_mm = current['precip_mm']
        humidity = current['humidity']
        uv_index = current['uv']
        dewpoint_c = current.get('dewpoint_c', 'N/A')
        
        # Format as string to read and evaluate
        weather_report = (
            f"Weather Data for {location.title()}:\n"
            f"- Condition: {condition}\n"
            f"- Temperature: {temp_c}°C\n"
            f"- Feels Like: {feelslike_c}°C\n"
            f"- Wind Speed: {wind_kph} km/h\n"
            f"- Precipitation: {precip_mm} mm\n"
            f"- Humidity: {humidity}%\n"
            f"- Dew Point: {dewpoint_c}°C\n"
            f"- UV Index: {uv_index}\n"
        )
        return weather_report
        
    except requests.exceptions.RequestException as e:
        return f"Sorry, I couldn't reach the weather service. Error: {e}"

if __name__ == "__main__":
    test_city = "Aachen"
    result = get_live_weather(test_city)
    print("Result:", result)
    
    test_city_2 = "Cologne"
    result_2 = get_live_weather(test_city_2)
    print("Result:", result_2)
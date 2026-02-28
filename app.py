from google import genai
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Initialize the Gemini client
client = genai.Client()

response = client.models.generate_content(
    model="gemini-2.5-flash", contents="Explain how AI works in a few words"
)

print(response.text)
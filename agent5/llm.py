import os
from dotenv import load_dotenv
from google import genai

# Load variables from the .env file into the environment
load_dotenv()

# Read the Gemini API key from environment variables
api_key = os.getenv("GEMINI_API_KEY")

# Create the Gemini client with our API key
client = genai.Client(api_key=api_key)


def generate_response(prompt):
    """
    Sends a prompt to Gemini and returns the text response.
    """
    response = client.models.generate_content(
        model="gemini-flash-latest",
        contents=prompt
    )
    return response.text
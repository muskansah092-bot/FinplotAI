"""agent5/llm_config.py"""
import os
from dotenv import load_dotenv
from google import genai

load_dotenv()

_API_KEY = os.getenv("GEMINI_API_KEY")

if not _API_KEY:
    raise EnvironmentError(
        "GEMINI_API_KEY not found. Add it to your .env file."
    )

_client = genai.Client(api_key=_API_KEY)

MODEL_NAME = "gemini-flash-latest"


def get_llm_response(prompt: str, system_instruction: str = None) -> str:
    """
    Single entry point for all Gemini calls made by Agent 5.

    Every other Agent 5 module (intent classifier, orchestrator,
    RAG, response generator) should call this function rather
    than instantiating its own client.
    """
    config = {}
    if system_instruction:
        config["system_instruction"] = system_instruction

    response = _client.models.generate_content(
        model=MODEL_NAME,
        contents=prompt,
        config=config if config else None,
    )

    text = response.text

    if not text:
        raise ValueError("Gemini returned an empty response.")

    return text.strip()
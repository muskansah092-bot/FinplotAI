"""agent5/llm_config.py"""
import os
import time
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

# How many times to retry a call that fails due to rate limiting
# before giving up, and how long to wait before each retry (seconds).
# Waits grow each attempt (2s, then 5s, then 10s) since a rate-limit
# window needs real time to pass, not an instant retry.
_MAX_RETRIES = 3
_RETRY_DELAYS = [2, 5, 10]

_RATE_LIMIT_MARKERS = ("429", "rate limit", "resource_exhausted", "quota")


def _is_rate_limit_error(exc: Exception) -> bool:
    message = str(exc).lower()
    return any(marker in message for marker in _RATE_LIMIT_MARKERS)


def get_llm_response(prompt: str, system_instruction: str = None) -> str:
    """
    Single entry point for all Gemini calls made by Agent 5.

    Every other Agent 5 module (intent classifier, orchestrator,
    RAG, response generator) should call this function rather
    than instantiating its own client.

    Automatically retries on rate-limit errors (free-tier Gemini
    keys are limited to roughly 10-15 requests/minute, and a single
    chat turn can make more than one call here, so this is easy to
    hit during quick back-to-back testing). If all retries are
    exhausted, raises a clear, user-facing error instead of letting
    the raw Gemini exception bubble up as an unexplained 500.
    """
    config = {}
    if system_instruction:
        config["system_instruction"] = system_instruction

    last_error = None

    for attempt in range(_MAX_RETRIES + 1):
        try:
            response = _client.models.generate_content(
                model=MODEL_NAME,
                contents=prompt,
                config=config if config else None,
            )

            text = response.text
            if not text:
                raise ValueError("Gemini returned an empty response.")

            return text.strip()

        except Exception as exc:
            last_error = exc

            if not _is_rate_limit_error(exc):
                # Not a rate-limit issue — no point retrying, raise immediately.
                raise

            if attempt < _MAX_RETRIES:
                delay = _RETRY_DELAYS[attempt]
                print(
                    f"[llm_config] Gemini rate limit hit (attempt {attempt + 1}/"
                    f"{_MAX_RETRIES + 1}). Retrying in {delay}s..."
                )
                time.sleep(delay)

    raise RuntimeError(
        "Finplot AI is getting rate-limited by Gemini's free tier "
        "(too many requests too quickly). Please wait about a minute "
        "and try again."
    ) from last_error
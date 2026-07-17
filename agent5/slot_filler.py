"""agent5/slot_filler.py"""
from agent5.llm_config import get_llm_response
from agent5.prompts import SLOT_EXTRACTION_PROMPT

FIELD_DESCRIPTIONS = {
    "goal": "The name of the financial goal the user is saving for.",
    "target_amount": "The total amount of money the user wants to save, as a number.",
    "timeline_months": "The duration in months the user wants to achieve this goal in.",
}


def extract_field(field_name: str, user_reply: str):
    """
    Extract a single field's value from the user's free-text reply.

    Returns:
        - str for "goal"
        - float for "target_amount"
        - int for "timeline_months"
        - None if extraction failed or the LLM couldn't find a value
    """
    prompt = SLOT_EXTRACTION_PROMPT.format(
        field_name=field_name,
        field_description=FIELD_DESCRIPTIONS.get(field_name, field_name),
        user_reply=user_reply.strip(),
    )

    raw = get_llm_response(prompt).strip()

    if raw.lower() in ("null", "none", ""):
        return None

    if field_name == "target_amount":
        try:
            cleaned = raw.replace(",", "").replace("₹", "").strip()
            return float(cleaned)
        except ValueError:
            return None

    if field_name == "timeline_months":
        try:
            cleaned = "".join(ch for ch in raw if ch.isdigit())
            return int(cleaned) if cleaned else None
        except ValueError:
            return None

    # "goal" — return as-is, trimmed
    return raw
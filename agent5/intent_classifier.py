"""agent5/intent_classifier.py"""
from agent5.llm_config import get_llm_response
from agent5.prompts import INTENT_CLASSIFIER_PROMPT

VALID_INTENTS = {
    "financial_analysis",
    "goal_planning",
    "investment_advice",
    "general_question",
}


def classify_intent(user_message: str, context: str = "") -> str:
    """
    Detect the user's intent from their message.

    Returns one of: "financial_analysis", "goal_planning",
    "investment_advice", "general_question".

    Falls back to "general_question" if the LLM response is
    unparseable, so the orchestrator always has a safe default
    rather than crashing.
    """
    prompt = INTENT_CLASSIFIER_PROMPT.format(
        context=context.strip() if context else "None",
        message=user_message.strip(),
    )

    raw_response = get_llm_response(prompt)

    cleaned = raw_response.strip().lower()

    # Defensive parsing: the LLM might wrap the word in
    # punctuation or extra whitespace despite instructions.
    for intent in VALID_INTENTS:
        if intent in cleaned:
            return intent

    # Safe fallback — never let intent classification break the flow.
    return "general_question"
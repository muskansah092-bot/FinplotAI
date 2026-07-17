"""agent5/response_generator.py"""
import json
from agent5.llm_config import get_llm_response
from agent5.prompts import RESPONSE_GENERATOR_PROMPT


def generate_response(intent: str, data: dict) -> str:
    """
    Convert raw agent-chain output into a natural conversational reply.

    Args:
        intent: one of "financial_analysis", "goal_planning", "investment_advice"
        data: the raw dict from orchestrator._run_agent_chain()
              (keys: transactions, agent2, agent3, agent4 — some may be None
              depending on intent)

    Returns:
        A natural-language string ready to show the user.
    """
    # Only include the pieces relevant to this intent, so the LLM
    # isn't fed irrelevant None fields.
    relevant_data = {"agent2": data.get("agent2")}

    if intent in ("goal_planning", "investment_advice"):
        relevant_data["agent3"] = data.get("agent3")

    if intent == "investment_advice":
        relevant_data["agent4"] = data.get("agent4")

    prompt = RESPONSE_GENERATOR_PROMPT.format(
        intent=intent,
        data=json.dumps(relevant_data, indent=2),
    )

    return get_llm_response(prompt)
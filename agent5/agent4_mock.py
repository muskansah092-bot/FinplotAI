"""agent5/agent4_mock.py"""

"""
TEMPORARY MOCK for Agent 4 (Investment Recommendation Agent).

Replace this module with the real agent4 package once your
teammate completes it. The function signature below is the
CONTRACT Agent 5 relies on — keep it identical in the real
implementation so no orchestrator code needs to change.

Real Agent 4 will use: Agent 1 output + Agent 2 output +
Agent 3 output -> LLM + RAG over an investment knowledge base
-> structured investment recommendations JSON.
"""


def run_agent4_pipeline(agent1_data, agent2_data, agent3_data) -> dict:
    """
    Mock investment recommendation generator.

    Args:
        agent1_data: Agent 1's transaction list (or summary dict)
        agent2_data: Agent 2's financial health output
        agent3_data: Agent 3's savings/goal plan output

    Returns:
        dict matching the shape the real Agent 4 is expected to produce.
    """
    health_level = agent2_data.get("health_level", "Unknown")
    financial_score = agent2_data.get("financial_score", 0)
    disposable_income = agent3_data.get("recommended_saving", 0)

    # Very simple rule-based mock — NOT real investment logic.
    # Just enough structure for Agent 5 to build/test its
    # response-generation flow against.
    if financial_score >= 75:
        risk_profile = "Moderate to Aggressive"
        suggestions = [
            {
                "instrument": "Index Mutual Funds (Equity)",
                "allocation_percent": 50,
                "reasoning": "Strong financial health supports higher equity exposure.",
            },
            {
                "instrument": "SIP in Diversified Equity Fund",
                "allocation_percent": 30,
                "reasoning": "Disciplined monthly investing to build long-term wealth.",
            },
            {
                "instrument": "Liquid Fund / Emergency Reserve",
                "allocation_percent": 20,
                "reasoning": "Maintain liquidity buffer alongside growth investments.",
            },
        ]
    elif financial_score >= 50:
        risk_profile = "Moderate"
        suggestions = [
            {
                "instrument": "Balanced/Hybrid Mutual Funds",
                "allocation_percent": 40,
                "reasoning": "Balances growth with reduced volatility given current financial health.",
            },
            {
                "instrument": "Recurring Deposit / Debt Fund",
                "allocation_percent": 40,
                "reasoning": "Stable, low-risk option while savings habits improve.",
            },
            {
                "instrument": "Emergency Fund (Savings Account)",
                "allocation_percent": 20,
                "reasoning": "Priority given moderate financial score.",
            },
        ]
    else:
        risk_profile = "Conservative"
        suggestions = [
            {
                "instrument": "High-Interest Savings Account",
                "allocation_percent": 60,
                "reasoning": "Focus on building an emergency fund before investing.",
            },
            {
                "instrument": "Recurring Deposit",
                "allocation_percent": 40,
                "reasoning": "Low-risk habit building given current financial health score.",
            },
        ]

    return {
        "risk_profile": risk_profile,
        "based_on_financial_score": financial_score,
        "based_on_health_level": health_level,
        "monthly_investable_amount_estimate": disposable_income,
        "recommendations": suggestions,
        "disclaimer": (
            "This is a MOCK output from a placeholder Agent 4. "
            "Not real financial advice. Will be replaced by the "
            "actual RAG-based investment agent."
        ),
        "is_mock": True,
    }
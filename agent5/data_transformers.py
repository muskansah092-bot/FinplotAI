"""agent5/data_transformers.py"""


def transactions_to_agent3_input(transactions: list) -> dict:
    """
    Convert Agent 1's raw transaction list into the summarized
    shape Agent 3's run_agent3_pipeline() expects as agent1_json.

    This mirrors the transformation logic originally written inline
    inside agent3/test_agent3.py, extracted here so it's reusable
    and doesn't need to live inside a test script.

    ATM withdrawals are split proportionally into food/shopping
    as a rough cash-spend approximation, same as the original logic.
    """
    income = 0.0
    total_expenses = 0.0
    food_expenses = 0.0
    shopping_expenses = 0.0
    atm_expenses = 0.0

    for txn in transactions:
        amount = float(txn.get("amount", 0))
        category = txn.get("category", "")
        txn_type = txn.get("type", "")

        if txn_type == "Credit":
            income += amount
        elif txn_type == "Debit":
            total_expenses += amount
            if category == "Food":
                food_expenses += amount
            elif category == "Shopping":
                shopping_expenses += amount
            elif category == "ATM Withdrawal":
                atm_expenses += amount

    return {
        "income": round(income, 2),
        "expense": round(total_expenses, 2),
        "food": round(food_expenses + (atm_expenses * 0.15), 2),
        "shopping": round(shopping_expenses + (atm_expenses * 0.20), 2),
        "subscriptions": 0.0,
        "emi": 0.0,
        "disposable_income": round(income - total_expenses, 2),
    }


def unwrap_crew_output(raw_output) -> dict:
    """
    Extract a clean dict from Agent 3's CrewAI output object.

    Agent 3's pipeline returns a CrewOutput wrapper, not plain JSON.
    This mirrors the fallback-chain logic from agent3/test_agent3.py:
    try json_dict -> try parsing .raw as JSON -> handle plain dict ->
    handle plain string -> give up and return an error dict.
    """
    import json

    # Case 1: CrewOutput object with json_dict attribute
    if hasattr(raw_output, "json_dict") and raw_output.json_dict:
        return raw_output.json_dict

    # Case 2: CrewOutput object with .raw string attribute
    if hasattr(raw_output, "raw") and isinstance(raw_output.raw, str):
        try:
            return json.loads(raw_output.raw)
        except json.JSONDecodeError:
            pass

    # Case 3: already a plain dict
    if isinstance(raw_output, dict):
        if raw_output.get("json_dict"):
            return raw_output["json_dict"]
        if isinstance(raw_output.get("raw"), str):
            try:
                return json.loads(raw_output["raw"])
            except json.JSONDecodeError:
                pass
        return raw_output

    # Case 4: a raw JSON string
    if isinstance(raw_output, str):
        try:
            return json.loads(raw_output)
        except json.JSONDecodeError:
            pass

    # Give up gracefully rather than crashing the orchestrator
    return {
        "error": "Could not parse Agent 3 output",
        "raw": str(raw_output),
    }
# main.py

from transaction_parser import categorize_transactions
from financial_health import get_financial_health


def run_agent2(transactions):
    # Step 1: Parse transactions
    data = categorize_transactions(transactions)

    # Step 2: Get financial health
    result = get_financial_health(
        income=data["income"],
        expenses=data["expenses"],
        shopping=data["shopping"],
        subscriptions=data["subscriptions"],
        food=data["food"],
        emi=data["emi"],
        bnpl=data["bnpl"]
    )

    return result
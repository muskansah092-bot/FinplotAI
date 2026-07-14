# financial_health.py

from metrics import calculate_metrics
from scoring import calculate_financial_score


def get_financial_health(
    income,
    expenses,
    shopping,
    subscriptions,
    food,
    emi,
    bnpl
):
    # 🧮 Step 1: Get all ratios from metrics
    metrics = calculate_metrics(
        income,
        expenses,
        shopping,
        subscriptions,
        food,
        emi,
        bnpl
    )

    # 🧠 Step 2: Score
    score, strengths, weaknesses = calculate_financial_score(
        metrics["savings_rate"],
        metrics["expense_ratio"],
        metrics["shopping_ratio"],
        metrics["subscription_ratio"],
        metrics["emi_ratio"],
        metrics["bnpl_ratio"]
    )

    # 🏷️ Step 3: Health category
    if score >= 90:
        health = "Excellent"
    elif score >= 75:
        health = "Good"
    elif score >= 60:
        health = "Average"
    elif score >= 40:
        health = "Needs Improvement"
    else:
        health = "Critical"

    # 📦 Final Output
    result = {
        "financial_score": score,
        "health_level": health,
        **metrics,
        "strengths": strengths,
        "weaknesses": weaknesses
    }

    return result
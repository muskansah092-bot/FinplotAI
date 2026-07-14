# scoring.py

def calculate_financial_score(
    savings_rate,
    expense_ratio,
    shopping_ratio,
    subscription_ratio,
    emi_ratio,
    bnpl_ratio
):
    score = 100
    weaknesses = []
    strengths = []

    # ❌ Deductions
    if savings_rate < 20:
        score -= 20
        weaknesses.append("Low savings")
    else:
        strengths.append("Good savings habit")

    if expense_ratio > 80:
        score -= 15
        weaknesses.append("High expenses")
    else:
        strengths.append("Controlled expenses")

    if emi_ratio > 40:
        score -= 15
        weaknesses.append("High EMI burden")
    else:
        strengths.append("Low EMI")

    if bnpl_ratio > 10:
        score -= 10
        weaknesses.append("Frequent BNPL usage")

    if shopping_ratio > 20:
        score -= 10
        weaknesses.append("High shopping")

    if subscription_ratio > 5:
        score -= 10
        weaknesses.append("Too many subscriptions")

    # ✅ Clamp score
    score = max(score, 0)

    return score, strengths, weaknesses
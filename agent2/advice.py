# advice.py

def generate_advice(savings_rate, expense_ratio, disposable_income):
    advice = []

    # Savings advice
    if savings_rate < 0.2:
        advice.append("Your savings rate is low. Try to save at least 20% of your income.")
    elif savings_rate >= 0.4:
        advice.append("Excellent savings habit! Keep it up.")

    # Expense advice
    if expense_ratio > 0.7:
        advice.append("Your expenses are too high. Consider cutting unnecessary spending.")
    elif expense_ratio <= 0.5:
        advice.append("Great control over expenses!")

    # Disposable income advice
    if disposable_income <= 0:
        advice.append("You are spending more than you earn. Immediate action needed!")
    else:
        advice.append("You have positive disposable income. Consider investing it wisely.")

    return advice
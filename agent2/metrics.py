# metrics.py

def clamp(value, min_val=-100, max_val=100):
    return max(min(value, max_val), min_val)


def calculate_metrics(income, expenses, shopping, subscriptions, food, emi, bnpl):
    
    # 🛑 Handle zero or invalid income
    if income <= 0:
        savings_rate = 0
        expense_ratio = 0
    else:
        savings_rate = ((income - expenses) / income) * 100
        expense_ratio = (expenses / income) * 100

    # ✅ Clamp extreme values (very important)
    savings_rate = clamp(savings_rate)
    expense_ratio = clamp(expense_ratio)

    # 🧮 Category ratios (safe division)
    def safe_ratio(value):
        if income <= 0:
            return 0
        return (value / income) * 100

    shopping_ratio = clamp(safe_ratio(shopping))
    subscription_ratio = clamp(safe_ratio(subscriptions))
    food_ratio = clamp(safe_ratio(food))
    emi_ratio = clamp(safe_ratio(emi))
    bnpl_ratio = clamp(safe_ratio(bnpl))

    return {
        "savings_rate": round(savings_rate, 2),
        "expense_ratio": round(expense_ratio, 2),
        "shopping_ratio": round(shopping_ratio, 2),
        "subscription_ratio": round(subscription_ratio, 2),
        "food_ratio": round(food_ratio, 2),
        "emi_ratio": round(emi_ratio, 2),
        "bnpl_ratio": round(bnpl_ratio, 2),
    }
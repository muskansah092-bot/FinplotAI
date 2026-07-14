# transaction_parser.py

def categorize_transactions(transactions):
    income = 0
    expenses = 0

    shopping = 0
    food = 0
    subscriptions = 0
    emi = 0
    bnpl = 0

    for txn in transactions:
        # Get raw values
        amount_raw = txn.get("amount")
        txn_type = txn.get("type", "").strip().lower()
        merchant = txn.get("merchant", "").lower()

        # Skip invalid entries
        if not amount_raw or not txn_type:
            continue

        # Convert amount safely
        try:
            amount = float(amount_raw)
        except:
            continue

        # CREDIT → Income
        if txn_type == "credit":
            income += amount
            continue

        # DEBIT → Expense
        if txn_type == "debit":
            expenses += amount

            # Categorization (basic rules)
            if "amazon" in merchant or "flipkart" in merchant:
                shopping += amount

            elif "swiggy" in merchant or "zomato" in merchant:
                food += amount

            elif "netflix" in merchant or "spotify" in merchant or "subscription" in merchant:
                subscriptions += amount

            elif "emi" in merchant:
                emi += amount

            elif "paylater" in merchant or "bnpl" in merchant:
                bnpl += amount

    # 🔍 DEBUG PRINT (important)
    print("Parsed Data:", {
        "income": income,
        "expenses": expenses,
        "shopping": shopping,
        "food": food,
        "subscriptions": subscriptions,
        "emi": emi,
        "bnpl": bnpl
    })

    return {
        "income": income,
        "expenses": expenses,
        "shopping": shopping,
        "food": food,
        "subscriptions": subscriptions,
        "emi": emi,
        "bnpl": bnpl
    }
import json
import os
from financial_health import get_financial_health


# 🔁 Step 1: Convert transactions → summary
def summarize_transactions(transactions):
    summary = {
        "income": 0,
        "expenses": 0,
        "shopping": 0,
        "subscriptions": 0,
        "food": 0,
        "emi": 0,
        "bnpl": 0
    }

    for t in transactions:
        amount = t.get("amount", 0)
        category = t.get("category", "").lower()
        t_type = t.get("type", "").lower()

        # 💰 Income vs Expense
        if t_type == "credit":
            summary["income"] += amount
        else:
            summary["expenses"] += amount

            # 🧠 Basic category mapping
            if "shopping" in category:
                summary["shopping"] += amount
            elif "food" in category:
                summary["food"] += amount
            elif "subscription" in category:
                summary["subscriptions"] += amount
            elif "emi" in category:
                summary["emi"] += amount
            elif "bnpl" in category:
                summary["bnpl"] += amount

    return summary


# 🚀 Main runner
def run_agent2():
    # 📥 Step 2: Read transactions.json (Agent1 output)
    input_path = os.path.join(
        os.path.dirname(__file__),
        "..",
        "outputs",
        "transactions.json"
    )

    with open(input_path, "r") as f:
        transactions = json.load(f)

    

    # 🔁 Step 3: Convert to financial summary
    data = summarize_transactions(transactions)

    

    # 📊 Step 4: Run financial health
    result = get_financial_health(
        income=data.get("income", 0),
        expenses=data.get("expenses", 0),
        shopping=data.get("shopping", 0),
        subscriptions=data.get("subscriptions", 0),
        food=data.get("food", 0),
        emi=data.get("emi", 0),
        bnpl=data.get("bnpl", 0)
    )

    print("📈 Result:", result)

    # 💾 Step 5: Save output
    output_path = os.path.join(
        os.path.dirname(__file__),
        "..",
        "outputs",
        "agent2_output.json"
    )

    with open(output_path, "w") as f:
        json.dump(result, f, indent=4)

    print(f"✅ Saved at: {output_path}")

    return result


if __name__ == "__main__":
    run_agent2()
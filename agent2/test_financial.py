from financial_health import get_financial_health

result = get_financial_health(
    income=10000,
    expenses=7000,
    shopping=1500,
    subscriptions=300,
    food=2000,
    emi=1000,
    bnpl=500
)

print(result)
from transaction_parser import categorize_transactions
from financial_health import get_financial_health

transactions = [
    {'date': '24 Jun 19', 'merchant': 'BALANCE FORWARD', 'amount': '330.00', 'type': 'Credit'},
    {'date': '24 Jun 19', 'merchant': 'UPI/917412529088/', 'amount': '797.00', 'type': 'Credit'},
    {'date': '25 Jun 19', 'merchant': 'CRRAJAGURU', 'amount': '14.00', 'type': 'Credit'},
    {'date': '27 Jun 19', 'merchant': 'SEASON TICKET', 'amount': '500.00', 'type': 'Debit'},
    {'date': '28 Jun 19', 'merchant': 'TRANSFER', 'amount': '1000.00', 'type': 'Debit'},
    {'date': '29 Jun 19', 'merchant': 'UPI PAYMENT', 'amount': '120.00', 'type': 'Debit'},
    {'date': '02 Jul 19', 'merchant': 'NETFLIX', 'amount': '399.00', 'type': 'Debit'},
    {'date': '04 Jul 19', 'merchant': 'AMAZON', 'amount': '1800.00', 'type': 'Debit'},
    {'date': '', 'merchant': 'ATM WITHDRAWAL', 'amount': '14000.00', 'type': 'Debit'}
]

data = categorize_transactions(transactions)

result = get_financial_health(
    income=data["income"],
    expenses=data["expenses"],
    shopping=data["shopping"],
    subscriptions=data["subscriptions"],
    food=data["food"],
    emi=data["emi"],
    bnpl=data["bnpl"]
)

print("\nFinal Result:\n", result)
from metrics import calculate_savings_rate, calculate_expense_ratio, calculate_disposable_income

income = 10000
expenses = 7000

print("Savings Rate:", calculate_savings_rate(income, expenses))
print("Expense Ratio:", calculate_expense_ratio(expenses, income))
print("Disposable Income:", calculate_disposable_income(income, expenses))
from scoring import score_savings_rate, score_expense_ratio, score_disposable_income, calculate_overall_score

savings_score = score_savings_rate(0.3)
expense_score = score_expense_ratio(0.6)
disposable_score = score_disposable_income(3000)

overall = calculate_overall_score(savings_score, expense_score, disposable_score)

print("Savings Score:", savings_score)
print("Expense Score:", expense_score)
print("Disposable Score:", disposable_score)
print("Overall Score:", overall)
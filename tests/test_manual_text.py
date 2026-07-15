from agent1.extractor import StatementExtractor

manual_text = """
Paid to Swiggy
₹450
02 Jan 2025

Salary Credit
₹50,000
01 Jan 2025

Amazon
₹1,250
05 Jan 2025
"""

extractor = StatementExtractor(
    file_type="manual",
    manual_data=manual_text
)

raw_text = extractor.extract()

print("===== MANUAL RAW TEXT =====")
print(raw_text)
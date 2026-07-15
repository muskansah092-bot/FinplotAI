from agent1.extractor import StatementExtractor

extractor = StatementExtractor(
    file_path="data/sample_statement.csv",
    file_type="csv"
)

raw_text = extractor.extract()

print("===== RAW TEXT =====")
print(raw_text)
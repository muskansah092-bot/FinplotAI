from agent1.extractor import StatementExtractor

extractor = StatementExtractor(
    file_path="data/Sample Bank statement.pdf",
    file_type="pdf"
)

raw_text = extractor.extract()

print("===== RAW TEXT =====")
print(raw_text)
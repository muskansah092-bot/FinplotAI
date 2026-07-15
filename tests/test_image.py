from agent1.extractor import StatementExtractor

extractor = StatementExtractor(
    file_path="data/image.png",
    file_type="image"
)

raw_text = extractor.extract()

print("===== OCR RAW TEXT =====")
print(raw_text)
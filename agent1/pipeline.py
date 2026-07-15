from agent1.parser import StatementParser
from agent1.extractor import StatementExtractor
from agent1.llm_parser import LLMParser
from agent1.utils import save_json


class Agent1Pipeline:
    """
    Complete Agent-1 pipeline.

    Flow:
        Input File
            ↓
        Detect File Type
            ↓
        Extract Raw Text
            ↓
        Parse using LLM
            ↓
        Save JSON
            ↓
        Return Transactions
    """

    def __init__(self, llm):
        self.llm = llm

    def process(self, file_path, output_path="outputs/transactions.json"):

        # Step 1: Detect file type
        parser = StatementParser(file_path)
        file_type = parser.parse()

        # Step 2: Extract raw text
        extractor = StatementExtractor(
            file_path=file_path,
            file_type=file_type
        )

        raw_text = extractor.extract()

        # Step 3: Convert raw text to structured JSON
        llm_parser = LLMParser(self.llm)

        transactions = llm_parser.parse(raw_text)

        # Step 4: Save output
        save_json(transactions, output_path)

        return transactions
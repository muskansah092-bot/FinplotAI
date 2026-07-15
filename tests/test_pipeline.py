import json

from agent1.pipeline import Agent1Pipeline
from agent1.llm_config import llm

pipeline = Agent1Pipeline(llm)

transactions = pipeline.process(
    file_path="data/Sample Bank statement.pdf"
)

print(json.dumps(transactions, indent=4))
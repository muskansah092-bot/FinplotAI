"""agent5/integrations.py"""
import os
import sys

# ---------------------------------------------------------
# Path setup — see Step 6 explanation for why this is needed.
# No files inside agent2/ or agent3/ are modified.
# ---------------------------------------------------------
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
AGENT2_DIR = os.path.join(PROJECT_ROOT, "agent2")
AGENT3_DIR = os.path.join(PROJECT_ROOT, "agent3")

for path in (PROJECT_ROOT, AGENT2_DIR, AGENT3_DIR):
    if path not in sys.path:
        sys.path.insert(0, path)

from agent1.pipeline import Agent1Pipeline
from agent1.llm_config import llm as agent1_llm
from agent1.extractor import StatementExtractor
from agent1.llm_parser import LLMParser
from agent1.utils import save_json, ensure_directory

from agent2.main import run_agent2 as _run_agent2

from agent3.savings_planner import run_agent3_pipeline

from agent5.data_transformers import transactions_to_agent3_input, unwrap_crew_output
from agent5.agent4_mock import run_agent4_pipeline as _run_agent4_mock

OUTPUTS_DIR = os.path.join(PROJECT_ROOT, "outputs")
TRANSACTIONS_PATH = os.path.join(OUTPUTS_DIR, "transactions.json")
AGENT5_OUTPUT_PATH = os.path.join(OUTPUTS_DIR, "agent5_output.json")


# ---------------------------------------------------------
# Agent 1
# ---------------------------------------------------------

def run_agent1_from_file(file_path: str) -> list:
    """Run Agent 1 on an uploaded PDF/image/CSV/Excel file."""
    pipeline = Agent1Pipeline(agent1_llm)
    return pipeline.process(file_path, output_path=TRANSACTIONS_PATH)


def run_agent1_from_manual(manual_data) -> list:
    """
    Run Agent 1 on manually entered transaction text.
    Uses Agent 1's own extractor/parser classes directly since
    Agent1Pipeline doesn't support the manual case (see note above).
    """
    extractor = StatementExtractor(file_type="manual", manual_data=manual_data)
    raw_text = extractor.extract()

    llm_parser = LLMParser(agent1_llm)
    transactions = llm_parser.parse(raw_text)

    save_json(transactions, TRANSACTIONS_PATH)
    return transactions


# ---------------------------------------------------------
# Agent 2
# ---------------------------------------------------------

def run_agent2() -> dict:
    """Agent 2 reads/writes outputs/*.json itself — no args needed."""
    return _run_agent2()


# ---------------------------------------------------------
# Agent 3
# ---------------------------------------------------------

def run_agent3(transactions: list, agent2_output: dict, goal_data: dict) -> dict:
    """
    goal_data must contain: goal, target_amount, timeline_months
    (matches Agent 3's GoalInputSchema field names exactly).
    """
    agent1_summary = transactions_to_agent3_input(transactions)

    raw_output = run_agent3_pipeline(
        agent1_json=agent1_summary,
        agent2_json=agent2_output,
        user_goal_json=goal_data,
    )

    return unwrap_crew_output(raw_output)


# ---------------------------------------------------------
# Agent 4 (mock for now — swap this import when the real one lands)
# ---------------------------------------------------------

def run_agent4(agent1_data, agent2_data, agent3_data) -> dict:
    return _run_agent4_mock(agent1_data, agent2_data, agent3_data)


# ---------------------------------------------------------
# Agent 5 output
# ---------------------------------------------------------

def save_agent5_output(data: dict):
    ensure_directory(OUTPUTS_DIR)
    save_json(data, AGENT5_OUTPUT_PATH)
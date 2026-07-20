"""agent5/integrations.py"""
import os
import sys

# ---------------------------------------------------------
# Path setup.
#
# Agent 2, Agent 3, and Agent 4 all use bare, non-package-style
# imports internally — e.g. agent2/agent2/main.py does
# `from financial_health import get_financial_health`, not
# `from agent2.financial_health import ...`. That only resolves if
# each agent's *inner* code folder is directly on sys.path, not just
# its outer project folder. So each agent needs BOTH its outer
# folder (for the `import agent2.main` style imports done in this
# file) AND its inner folder (for the bare imports inside their own
# files) added to sys.path.
#
# No files inside agent2/, agent3/, or agent4/ are modified for
# this — it's purely path setup done from the integration layer.
# ---------------------------------------------------------
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

AGENT2_DIR = os.path.join(PROJECT_ROOT, "agent2")
AGENT2_INNER = os.path.join(AGENT2_DIR, "agent2")

AGENT3_DIR = os.path.join(PROJECT_ROOT, "agent3")
AGENT3_INNER = os.path.join(AGENT3_DIR, "agent3")

AGENT4_DIR = os.path.join(PROJECT_ROOT, "agent4")
AGENT4_INNER = os.path.join(AGENT4_DIR, "agent4")

for _path in (
    PROJECT_ROOT,
    AGENT2_DIR, AGENT2_INNER,
    AGENT3_DIR, AGENT3_INNER,
    AGENT4_DIR, AGENT4_INNER,
):
    if _path not in sys.path:
        sys.path.insert(0, _path)

from agent1.pipeline import Agent1Pipeline
from agent1.llm_config import llm as agent1_llm
from agent1.extractor import StatementExtractor
from agent1.llm_parser import LLMParser
from agent1.utils import save_json, ensure_directory

# Agent 2 exposes summarize_transactions() and (via its own bare
# import, now resolvable thanks to AGENT2_INNER above)
# get_financial_health() as attributes of agent2.main. We call both
# directly rather than using agent2's own run_agent2(), because
# run_agent2() reads/writes outputs/transactions.json at a path
# relative to *agent2's own folder* (agent2/outputs/transactions.json)
# — a different file than the one Agent 1's output actually gets
# saved to (outputs/transactions.json at the project root — see
# TRANSACTIONS_PATH below). Calling the two functions directly with
# the transactions already in memory sidesteps that mismatch
# entirely instead of relying on disk state / file paths lining up.
import agent2.main as agent2_main

from agent3.savings_planner import run_agent3_pipeline

from agent4.investment_agent import run_agent4_pipeline as _run_agent4_real

from agent5.data_transformers import transactions_to_agent3_input, unwrap_crew_output

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
    Agent1Pipeline doesn't support the manual case.
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

def run_agent2(transactions: list) -> dict:
    """
    Summarize Agent 1's transactions and run Agent 2's financial
    health scoring, called directly on the in-memory transaction
    list rather than via Agent 2's own run_agent2() (see note above
    about the outputs/ file-path mismatch).
    """
    summary = agent2_main.summarize_transactions(transactions)
    return agent2_main.get_financial_health(
        income=summary.get("income", 0),
        expenses=summary.get("expenses", 0),
        shopping=summary.get("shopping", 0),
        subscriptions=summary.get("subscriptions", 0),
        food=summary.get("food", 0),
        emi=summary.get("emi", 0),
        bnpl=summary.get("bnpl", 0),
    )


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
# Agent 4 (now wired to the real implementation, no longer the mock)
# ---------------------------------------------------------

_ENV_KEYS_AGENT4_TOUCHES = (
    "GOOGLE_API_KEY",
    "GOOGLE_APPLICATION_CREDENTIALS",
    "VERTEXAI_API_KEY",
    "OPENAI_API_KEY",
)


def run_agent4(transactions: list, agent2_data: dict, agent3_data: dict) -> dict:
    """
    Real Agent 4 expects agent1_json as a summarized dict with
    "income"/"disposable_income" keys (the same shape Agent 3 uses),
    not the raw transaction list — so we reuse the same transformer.

    Agent 4's own code also deletes GOOGLE_API_KEY /
    GOOGLE_APPLICATION_CREDENTIALS / VERTEXAI_API_KEY from the
    process environment and sets OPENAI_API_KEY, to make LiteLLM
    talk to Gemini's OpenAI-compatible endpoint. That's fine in
    isolation, but this server is long-running and Agent 1 needs
    GOOGLE_API_KEY for *other* sessions/requests too — so we
    snapshot and restore those variables around the call instead of
    letting Agent 4 permanently mutate the process environment.
    """
    agent1_summary = transactions_to_agent3_input(transactions)

    saved_env = {key: os.environ.get(key) for key in _ENV_KEYS_AGENT4_TOUCHES}
    try:
        return _run_agent4_real(agent1_summary, agent2_data, agent3_data)
    finally:
        for key, value in saved_env.items():
            if value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = value


# ---------------------------------------------------------
# Agent 5 output
# ---------------------------------------------------------

def save_agent5_output(data: dict):
    ensure_directory(OUTPUTS_DIR)
    save_json(data, AGENT5_OUTPUT_PATH)
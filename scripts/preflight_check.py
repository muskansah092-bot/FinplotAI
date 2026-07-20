"""
scripts/preflight_check.py

Run this BEFORE starting the server. It checks the things most
likely to go wrong — missing packages, missing API keys, broken
imports in any one agent — and tells you exactly which one, instead
of a confusing crash halfway through a chat message.

Run it from the project root (the folder containing agent1/, agent2/,
etc.):

    python scripts/preflight_check.py
"""
import os
import sys

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
os.chdir(PROJECT_ROOT)
sys.path.insert(0, PROJECT_ROOT)

CHECKS_PASSED = 0
CHECKS_FAILED = 0


def check(label, fn):
    global CHECKS_PASSED, CHECKS_FAILED
    print(f"  Checking: {label} ... ", end="", flush=True)
    try:
        fn()
        print("OK")
        CHECKS_PASSED += 1
    except Exception as e:
        print(f"FAILED\n      -> {type(e).__name__}: {e}")
        CHECKS_FAILED += 1


print("=" * 60)
print("Finplot AI — pre-flight check")
print("=" * 60)

# ---------------------------------------------------------
# 1. .env / API keys
# ---------------------------------------------------------
print("\n[1] Environment variables")


def check_env():
    from dotenv import load_dotenv
    load_dotenv(os.path.join(PROJECT_ROOT, ".env"))
    google_key = os.getenv("GOOGLE_API_KEY")
    gemini_key = os.getenv("GEMINI_API_KEY")
    if not google_key:
        raise RuntimeError("GOOGLE_API_KEY is missing from .env")
    if not gemini_key:
        raise RuntimeError("GEMINI_API_KEY is missing from .env")
    if "your_gemini_api_key_here" in (google_key, gemini_key):
        raise RuntimeError("You still have the placeholder value — paste your real key into .env")


check(".env file has real API keys", check_env)

# ---------------------------------------------------------
# 2. Third-party packages
# ---------------------------------------------------------
print("\n[2] Installed packages (pip install -r requirements.txt)")

PACKAGES = [
    "fastapi", "uvicorn", "multipart", "pydantic", "dotenv",
    "pandas", "openpyxl", "pdfplumber", "PyPDF2", "cv2", "easyocr",
    "langchain_google_genai", "crewai", "sentence_transformers",
    "numpy", "google.genai",
]

for pkg in PACKAGES:
    check(f"import {pkg}", lambda p=pkg: __import__(p))

# ---------------------------------------------------------
# 3. Each agent's own code actually imports
# ---------------------------------------------------------
print("\n[3] Each agent's code (catches broken imports/paths)")


def check_agent1():
    from agent1.pipeline import Agent1Pipeline  # noqa: F401
    from agent1.llm_config import llm  # noqa: F401


def check_agent2():
    sys.path.insert(0, os.path.join(PROJECT_ROOT, "agent2"))
    sys.path.insert(0, os.path.join(PROJECT_ROOT, "agent2", "agent2"))
    import agent2.main as agent2_main
    assert hasattr(agent2_main, "summarize_transactions")
    assert hasattr(agent2_main, "get_financial_health")


def check_agent3():
    sys.path.insert(0, os.path.join(PROJECT_ROOT, "agent3"))
    sys.path.insert(0, os.path.join(PROJECT_ROOT, "agent3", "agent3"))
    from agent3.savings_planner import run_agent3_pipeline  # noqa: F401


def check_agent4():
    sys.path.insert(0, os.path.join(PROJECT_ROOT, "agent4"))
    sys.path.insert(0, os.path.join(PROJECT_ROOT, "agent4", "agent4"))
    from agent4.investment_agent import run_agent4_pipeline  # noqa: F401


def check_agent5():
    from agent5.integrations import (
        run_agent1_from_file, run_agent2, run_agent3, run_agent4,
    )  # noqa: F401
    from agent5.orchestrator import handle_message  # noqa: F401


check("agent1 imports", check_agent1)
check("agent2 imports (via the integration path fix)", check_agent2)
check("agent3 imports (via the integration path fix)", check_agent3)
check("agent4 imports (via the integration path fix)", check_agent4)
check("agent5 orchestrator + integrations.py", check_agent5)

# ---------------------------------------------------------
# 4. A real (tiny, cheap) call to Gemini, to confirm the key works
# ---------------------------------------------------------
print("\n[4] A real Gemini API call (confirms your key actually works)")


def check_live_call():
    from agent5.llm_config import get_llm_response
    reply = get_llm_response("Reply with exactly one word: OK")
    if not reply:
        raise RuntimeError("Got an empty response from Gemini")


check("live call to Gemini", check_live_call)

# ---------------------------------------------------------
# Summary
# ---------------------------------------------------------
print("\n" + "=" * 60)
print(f"Result: {CHECKS_PASSED} passed, {CHECKS_FAILED} failed")
print("=" * 60)

if CHECKS_FAILED == 0:
    print("\nEverything looks good — you can start the server now:")
    print("  uvicorn agent5.agent5.main:app --reload --port 8000")
else:
    print("\nFix the FAILED item(s) above first (top to bottom — later")
    print("checks often fail as a side effect of an earlier one), then")
    print("re-run this script. Paste me the output if you're stuck.")
    sys.exit(1)
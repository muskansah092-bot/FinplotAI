"""agent5/rag/knowledge_base.py"""

# Lightweight static knowledge base for general finance questions.
# Each entry: keywords (for matching) + a concise explanation
# (kept LLM-friendly, not user-facing verbatim — the LLM will
# rephrase this using the response prompt).

KNOWLEDGE_BASE = [
    {
        "topic": "Mutual Funds",
        "keywords": ["mutual fund", "mutual funds", "nav", "fund house", "amc"],
        "content": (
            "A mutual fund pools money from many investors and is managed "
            "by a professional fund manager who invests it in stocks, "
            "bonds, or other assets. Returns are not guaranteed and depend "
            "on market performance. Categorized broadly into equity, debt, "
            "and hybrid funds based on risk level."
        ),
    },
    {
        "topic": "SIP",
        "keywords": ["sip", "systematic investment plan", "monthly investment"],
        "content": (
            "A Systematic Investment Plan (SIP) lets an investor put a "
            "fixed amount into a mutual fund at regular intervals (usually "
            "monthly) instead of a lump sum. It encourages disciplined "
            "investing and benefits from rupee-cost averaging over time."
        ),
    },
    {
        "topic": "Emergency Fund",
        "keywords": ["emergency fund", "rainy day fund", "safety net"],
        "content": (
            "An emergency fund is money set aside to cover 3-6 months of "
            "essential living expenses, kept in a liquid, easily accessible "
            "account. It should be built before pursuing other financial "
            "goals or investments."
        ),
    },
    {
        "topic": "Compound Interest",
        "keywords": ["compound interest", "compounding"],
        "content": (
            "Compound interest is interest calculated on both the original "
            "principal and the accumulated interest from previous periods. "
            "Over long time horizons, this creates exponential rather than "
            "linear growth, which is why starting to invest early matters."
        ),
    },
    {
        "topic": "Credit Score",
        "keywords": ["credit score", "cibil", "credit rating"],
        "content": (
            "A credit score is a numeric measure (typically 300-900 in "
            "India, via CIBIL) representing creditworthiness based on "
            "repayment history, credit utilization, and loan/credit card "
            "usage. Higher scores generally mean easier loan approval and "
            "better interest rates."
        ),
    },
    {
        "topic": "EMI",
        "keywords": ["emi", "equated monthly installment", "loan installment"],
        "content": (
            "An EMI (Equated Monthly Installment) is a fixed monthly "
            "payment made to repay a loan, covering both principal and "
            "interest. Early EMIs in a loan tenure are interest-heavy, "
            "shifting toward principal repayment over time."
        ),
    },
    {
        "topic": "Inflation",
        "keywords": ["inflation", "purchasing power", "cost of living"],
        "content": (
            "Inflation is the rate at which prices for goods and services "
            "rise over time, reducing the purchasing power of money. "
            "Savings that don't grow faster than inflation effectively "
            "lose value over the long run."
        ),
    },
    {
        "topic": "Diversification",
        "keywords": ["diversification", "diversify", "asset allocation"],
        "content": (
            "Diversification means spreading investments across different "
            "asset classes (equity, debt, gold, real estate) or sectors to "
            "reduce risk, since different assets don't move identically in "
            "response to market events."
        ),
    },
    {
        "topic": "Fixed Deposit",
        "keywords": ["fixed deposit", "fd", "term deposit"],
        "content": (
            "A Fixed Deposit (FD) is a low-risk investment where a lump sum "
            "is deposited with a bank for a fixed tenure at a predetermined "
            "interest rate, offering guaranteed but modest returns compared "
            "to equity investments."
        ),
    },
    {
        "topic": "50-30-20 Rule",
        "keywords": ["50/30/20", "50-30-20", "budgeting rule"],
        "content": (
            "The 50/30/20 rule is a simple budgeting framework: allocate "
            "50% of net income to needs, 30% to wants, and 20% to savings "
            "and financial goals."
        ),
    },
]


def get_all_topics() -> list:
    return [entry["topic"] for entry in KNOWLEDGE_BASE]
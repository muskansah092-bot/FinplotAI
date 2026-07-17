"""agent5/rag/simple_rag.py"""
from agent5.llm_config import get_llm_response
from agent5.prompts import RAG_ANSWER_PROMPT
from agent5.rag.knowledge_base import KNOWLEDGE_BASE


def _score_entry(query: str, entry: dict) -> int:
    """
    Simple keyword-overlap scoring — counts how many of the
    entry's keywords appear as substrings in the lowercased query.
    """
    query_lower = query.lower()
    return sum(1 for kw in entry["keywords"] if kw in query_lower)


def retrieve(query: str, top_k: int = 2) -> list:
    """
    Return the top_k most relevant knowledge base entries for the query.
    Entries with zero keyword matches are excluded entirely.
    """
    scored = [
        (entry, _score_entry(query, entry))
        for entry in KNOWLEDGE_BASE
    ]

    scored = [pair for pair in scored if pair[1] > 0]
    scored.sort(key=lambda pair: pair[1], reverse=True)

    return [entry for entry, score in scored[:top_k]]


def answer_general_question(query: str) -> str:
    """
    Answer a general finance question, using retrieved knowledge
    base context when available, falling back to the LLM's own
    general knowledge when nothing matches.
    """
    matches = retrieve(query)

    if matches:
        context = "\n\n".join(
            f"{entry['topic']}: {entry['content']}" for entry in matches
        )
    else:
        context = "No specific reference material found for this query."

    prompt = RAG_ANSWER_PROMPT.format(query=query, context=context)

    return get_llm_response(prompt)
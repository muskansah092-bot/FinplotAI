import os
from threading import Lock

from embeddings import EmbeddingEngine
from vector_db import LocalVectorDB

_default_knowledge_chunks = [
    "RBI Financial Literacy Rules: Short-term investment timelines below 12 months should favor capital preservation via Liquid Funds or high-yield Fixed Deposits over equity asset exposure.",
    "SEBI Investor Education Guidelines: Market-linked instruments like Equity SIPs and Index Funds offer higher compounding returns but carry principal variance risks, demanding a 3 to 5 year horizon.",
    "PPF and Government Savings Schemes: Public Provident Funds (PPF) offer absolute secure risk mitigation backed by the government, featuring a long-term fixed lock-in structure.",
    "AMFI Advisory Principles: Maintain liquid safety allocations to buffer emergency funds before allocating discretionary income pools into volatile small-cap or sectoral assets."
]

_embedding_engine = None
_vector_db = None
_index_lock = Lock()


def _ensure_index():
    global _embedding_engine, _vector_db

    if _embedding_engine is None:
        with _index_lock:
            if _embedding_engine is None:
                embedding_engine = EmbeddingEngine()
                vector_db = LocalVectorDB()
                chunk_vectors = embedding_engine.get_embeddings(_default_knowledge_chunks)
                vector_db.insert_documents(_default_knowledge_chunks, chunk_vectors)
                _embedding_engine = embedding_engine
                _vector_db = vector_db

def retrieve_knowledge(query_text: str, top_k: int = 2) -> str:
    """
    Exposes a unified retrieval interface to query compliance and financial data.
    """
    try:
        _ensure_index()
        query_vector = _embedding_engine.get_query_embedding(query_text)
        matched_chunks = _vector_db.similarity_search(query_vector, k=top_k)
        
        if not matched_chunks:
            return "No matching regulatory documentation found in the local index store."
            
        return "\n---\n".join([chunk["text"] for chunk in matched_chunks])
    except Exception as e:
        return f"RAG Search interface encountered a data loading fault: {str(e)}"
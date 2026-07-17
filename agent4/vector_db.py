import numpy as np
from typing import List, Dict, Any

class LocalVectorDB:
    """
    A lightweight vector database management layer for semantic knowledge document tracking.
    """
    def __init__(self):
        self.vector_store: List[np.ndarray] = []
        self.documents: List[Dict[str, Any]] = []

    def insert_documents(self, docs: List[str], embeddings: List[List[float]], metadata: List[Dict[str, Any]] = None):
        """
        Inserts knowledge document strings alongside their pre-calculated vector representations.
        """
        for i, doc in enumerate(docs):
            self.vector_store.append(np.array(embeddings[i]))
            meta = metadata[i] if metadata else {}
            self.documents.append({"text": doc, "metadata": meta})

    def similarity_search(self, query_embedding: List[float], k: int = 3) -> List[Dict[str, Any]]:
        """
        Executes a basic cosine similarity math search across indices to pull top matching segments.
        """
        if not self.vector_store:
            return []

        q_vec = np.array(query_embedding)
        scores = []

        for idx, doc_vec in enumerate(self.vector_store):
            # Compute raw dot product metrics over normalized vector bounds
            dot_product = np.dot(q_vec, doc_vec)
            norm_q = np.linalg.norm(q_vec)
            norm_doc = np.linalg.norm(doc_vec)
            
            similarity = dot_product / (norm_q * norm_doc) if norm_q > 0 and norm_doc > 0 else 0.0
            scores.append((similarity, self.documents[idx]))

        # Sort values descending by similarity threshold match scores
        scores.sort(key=lambda x: x[0], reverse=True)
        return [item[1] for item in scores[:k]]
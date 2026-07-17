from typing import List
import importlib


def _import_sentence_transformer():
    """Lazy import to provide a clearer error if the package is missing."""
    try:
        return importlib.import_module("sentence_transformers").SentenceTransformer
    except Exception as e:
        raise ImportError(
            "The 'sentence_transformers' package is required for EmbeddingEngine. "
            "Install it with: pip install sentence-transformers"
        ) from e

class EmbeddingEngine:
    """
    Manages vector generation for knowledge base strings using sentence transformers.
    """
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        # Load the sentence transformer model as established by the team workflow
        SentenceTransformer = _import_sentence_transformer()
        self.model = SentenceTransformer(model_name)

    def get_embeddings(self, texts: List[str]) -> List[List[float]]:
        """
        Converts a list of text strings into vector arrays.
        """
        if not texts:
            return []
        embeddings = self.model.encode(texts, show_progress_bar=False)
        # handle numpy arrays or lists
        if hasattr(embeddings, "tolist"):
            return embeddings.tolist()
        return list(map(lambda v: list(v), embeddings))

    def get_query_embedding(self, text: str) -> List[float]:
        """
        Converts a single query string into a vector array.
        """
        emb = self.model.encode(text, show_progress_bar=False)
        if hasattr(emb, "tolist"):
            return emb.tolist()
        return list(emb)
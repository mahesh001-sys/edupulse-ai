"""Create the sentence-transformer embedding function for EduPulse AI."""

from chromadb.utils.embedding_functions import (
    SentenceTransformerEmbeddingFunction,
)


def create_embedding_function() -> SentenceTransformerEmbeddingFunction:
    """Return the embedding function used for PDF chunks and queries."""
    return SentenceTransformerEmbeddingFunction(
        model_name="all-MiniLM-L6-v2"
    )
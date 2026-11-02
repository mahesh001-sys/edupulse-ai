"""Retrieve relevant PDF chunks for a question."""

from typing import Optional

from src.vectordb.vector_store import VectorStore


class Retriever:
    """Find relevant chunks from the vector database."""

    def __init__(self, vector_store: Optional[VectorStore] = None) -> None:
        self.vector_store = vector_store or VectorStore()

    def retrieve(
        self,
        question: str,
        document_id: str,
        n_results: int = 4,
    ) -> list[dict]:
        """Return the most relevant chunks for a question."""
        return self.vector_store.search(
            query=question,
            n_results=n_results,
            document_id=document_id,
        )
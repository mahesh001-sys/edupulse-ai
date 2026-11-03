"""Retrieve relevant PDF chunks for a question."""

from typing import Optional

from src.vectordb.vector_store import VectorStore


class Retriever:
    """Find relevant chunks from the vector database."""

    # Initial cutoff based on the project's current sample tests.
    # Recalibrate this with more supported and unsupported questions.
    MAX_DISTANCE = 0.80

    def __init__(
        self,
        vector_store: Optional[VectorStore] = None,
        max_distance: Optional[float] = MAX_DISTANCE,
    ) -> None:
        if max_distance is not None and max_distance < 0:
            raise ValueError("max_distance must be non-negative or None.")

        self.vector_store = vector_store or VectorStore()
        self.max_distance = max_distance

    def retrieve(
        self,
        question: str,
        document_id: str,
        n_results: int = 4,
    ) -> list[dict]:
        """Return chunks whose retrieval distance passes the cutoff."""
        results = self.vector_store.search(
            query=question,
            n_results=n_results,
            document_id=document_id,
        )

        if self.max_distance is None:
            return results

        return [
            item
            for item in results
            if item.get("distance") is not None
            and item["distance"] <= self.max_distance
        ]
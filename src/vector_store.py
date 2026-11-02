"""ChromaDB vector storage and semantic search for EduPulse AI."""

import hashlib
from pathlib import Path
from typing import List, Optional

import chromadb
from chromadb.utils.embedding_functions import (
    SentenceTransformerEmbeddingFunction,
)

from src.pdf_processor import DocumentChunk


class VectorStore:
    """Store PDF chunks and retrieve relevant passages."""

    def __init__(
        self,
        db_path: str = "chroma_db",
        collection_name: str = "edupulse_documents",
    ):
        self.db_path = Path(db_path)
        self.db_path.mkdir(parents=True, exist_ok=True)

        self.embedding_function = SentenceTransformerEmbeddingFunction(
            model_name="all-MiniLM-L6-v2"
        )

        self.client = chromadb.PersistentClient(
            path=str(self.db_path)
        )

        self.collection = self.client.get_or_create_collection(
            name=collection_name,
            embedding_function=self.embedding_function,
            metadata={"hnsw:space": "cosine"},
        )

    @staticmethod
    def create_document_id(pdf_bytes: bytes) -> str:
        """Generate a stable ID for an uploaded PDF."""
        return hashlib.sha256(pdf_bytes).hexdigest()

    def add_chunks(
        self,
        chunks: List[DocumentChunk],
        document_id: str,
    ) -> int:
        """Store chunks with their original PDF page numbers."""
        if not document_id.strip():
            raise ValueError("document_id cannot be empty.")

        if not chunks:
            raise ValueError("No chunks were provided.")

        ids = []
        documents = []
        metadatas = []

        for index, chunk in enumerate(chunks):
            if not chunk.text.strip():
                continue

            ids.append(f"{document_id}_{index}")
            documents.append(chunk.text)
            metadatas.append(
                {
                    "document_id": document_id,
                    "page_number": chunk.page_number,
                    "chunk_index": index,
                }
            )

        if not documents:
            raise ValueError("No non-empty chunks were provided.")

        self.collection.upsert(
            ids=ids,
            documents=documents,
            metadatas=metadatas,
        )

        return len(documents)

    def search(
        self,
        query: str,
        n_results: int = 4,
        document_id: Optional[str] = None,
    ) -> List[dict]:
        """Retrieve the most relevant chunks for a question."""
        if not query.strip():
            raise ValueError("Search query cannot be empty.")

        if n_results < 1:
            raise ValueError("n_results must be at least 1.")

        if self.collection.count() == 0:
            return []

        search_args = {
            "query_texts": [query],
            "n_results": min(n_results, self.collection.count()),
            "include": ["documents", "metadatas", "distances"],
        }

        if document_id:
            search_args["where"] = {"document_id": document_id}

        results = self.collection.query(**search_args)

        documents = results["documents"][0]
        metadatas = results["metadatas"][0]
        distances = results["distances"][0]

        return [
            {
                "text": text,
                "page_number": metadata["page_number"],
                "document_id": metadata["document_id"],
                "distance": distance,
            }
            for text, metadata, distance in zip(
                documents,
                metadatas,
                distances,
            )
        ]

    def delete_document(self, document_id: str) -> None:
        """Delete all stored chunks for one PDF."""
        self.collection.delete(
            where={"document_id": document_id}
        )

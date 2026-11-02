"""RAG pipeline for EduPulse AI."""

import os
from typing import Optional

from openai import OpenAI

from src.pdf_processor import chunk_pdf_pages, extract_pdf_pages
from src.vector_store import VectorStore


class RAGPipeline:
    """Retrieve PDF context and generate answers with citations."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = "gpt-4o-mini",
        db_path: str = "chroma_db",
    ):
        api_key = api_key or os.getenv("OPENAI_API_KEY")

        if not api_key:
            raise ValueError(
                "Missing OpenAI API key. Set OPENAI_API_KEY."
            )

        self.client = OpenAI(api_key=api_key)
        self.model = model
        self.vector_store = VectorStore(db_path=db_path)

    def index_pdf(self, pdf_bytes: bytes) -> str:
        """Extract, chunk, and store a PDF."""
        pages = extract_pdf_pages(pdf_bytes)
        chunks = chunk_pdf_pages(pages)

        document_id = self.vector_store.create_document_id(pdf_bytes)
        self.vector_store.add_chunks(chunks, document_id)

        return document_id

    def answer_question(
        self,
        question: str,
        document_id: str,
        n_results: int = 4,
    ) -> dict:
        """Answer a question using retrieved PDF passages."""
        if not question.strip():
            raise ValueError("Question cannot be empty.")

        results = self.vector_store.search(
            query=question,
            n_results=n_results,
            document_id=document_id,
        )

        if not results:
            return {
                "answer": "I couldn't find relevant information in this PDF.",
                "sources": [],
            }

        context = "\n\n".join(
            f"[Page {item['page_number']}]\n{item['text']}"
            for item in results
        )

        response = self.client.chat.completions.create(
            model=self.model,
            temperature=0,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "Answer the user's question using only the "
                        "provided PDF context. If the answer is not "
                        "supported by the context, say you cannot "
                        "find it in the document. Cite sources using "
                        "the exact format [Page N]."
                    ),
                },
                {
                    "role": "user",
                    "content": (
                        f"PDF context:\n{context}\n\n"
                        f"Question: {question}"
                    ),
                },
            ],
        )

        answer = response.choices[0].message.content or ""

        return {
            "answer": answer,
            "sources": [
                {
                    "page_number": item["page_number"],
                    "text": item["text"],
                }
                for item in results
            ],
        }

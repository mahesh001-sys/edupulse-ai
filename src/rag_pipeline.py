
"""RAG pipeline for EduPulse AI."""

import os
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv
from openai import OpenAI

from src.ingestion.loader import extract_pdf_pages
from src.chunking.text_chunker import chunk_pdf_pages
from src.llm.answer_generator import AnswerGenerator
from src.retrieval.retriever import Retriever
from src.vectordb.vector_store import VectorStore

# Load the project's .env file, located one folder above src/.
PROJECT_ROOT = Path(__file__).resolve().parent.parent
ENV_FILE = PROJECT_ROOT / ".env"
load_dotenv(dotenv_path=ENV_FILE)


class RAGPipeline:
    """Index PDF content and answer questions using retrieved context."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = "gpt-4o-mini",
        db_path: str = "chroma_db",
    ) -> None:
        resolved_api_key = api_key or os.getenv("OPENAI_API_KEY")

        if not resolved_api_key:
            raise ValueError(
                "Missing OpenAI API key. Add OPENAI_API_KEY to the "
                "project-root .env file, then restart Streamlit."
            )

        self.client = OpenAI(api_key=resolved_api_key)
        self.model = model
        self.vector_store = VectorStore(db_path=db_path)
        self.retriever = Retriever(self.vector_store)
        self.answer_generator = AnswerGenerator(self.client, self.model)

    def index_pdf(self, pdf_bytes: bytes) -> str:
        """Extract and chunk a PDF, then store its chunks."""
        if not pdf_bytes:
            raise ValueError("The uploaded PDF is empty.")

        pages = extract_pdf_pages(pdf_bytes)
        if not pages:
            raise ValueError(
                "No readable text was found in the PDF. "
                "It may be scanned or image-only."
            )

        chunks = chunk_pdf_pages(pages)
        if not chunks:
            raise ValueError("No text chunks could be created from the PDF.")

        document_id = self.vector_store.create_document_id(pdf_bytes)
        self.vector_store.add_chunks(chunks, document_id)

        return document_id

    def answer_question(
        self,
        question: str,
        document_id: str,
        n_results: int = 4,
    ) -> dict:
        """Answer a question using matching PDF chunks."""
        if not question or not question.strip():
            raise ValueError("Question cannot be empty.")

        if not document_id:
            raise ValueError("A processed PDF is required.")

        if (
            isinstance(n_results, bool)
            or not isinstance(n_results, int)
            or n_results <= 0
        ):
            raise ValueError(
                "n_results must be a positive integer."
            )

        results = self.retriever.retrieve(
            question=question,
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

        answer = self.answer_generator.generate(context, question)

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

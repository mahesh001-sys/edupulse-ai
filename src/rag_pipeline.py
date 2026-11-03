"""RAG pipeline for EduPulse AI."""

import os
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv
from openai import OpenAI

from src.ingestion.loader import extract_pdf_pages
from src.chunking.text_chunker import chunk_pdf_pages
from src.llm.answer_generator import AnswerGenerator
from src.llm.study_material_generator import StudyMaterialGenerator
from src.retrieval.retriever import Retriever
from src.vectordb.vector_store import VectorStore

# Load the project's .env file, located one folder above src/.
PROJECT_ROOT = Path(__file__).resolve().parent.parent
ENV_FILE = PROJECT_ROOT / ".env"
load_dotenv(dotenv_path=ENV_FILE)


class RAGPipeline:
    """Index PDF content and generate PDF-grounded study material."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = "gpt-4o-mini",
        db_path: str = "chroma_db",
    ) -> None:
        resolved_api_key = api_key or os.getenv("OPENAI_API_KEY")

        self.model = model
        self.vector_store = VectorStore(db_path=db_path)
        self.retriever = Retriever(self.vector_store)

        # Retrieval works without an API key. OpenAI is only needed for
        # generating answers, quizzes, and flashcards.
        self.client = OpenAI(api_key=resolved_api_key) if resolved_api_key else None

        self.answer_generator = (
            AnswerGenerator(self.client, self.model)
            if self.client is not None
            else None
        )
        self.study_material_generator = (
            StudyMaterialGenerator(self.client, self.model)
            if self.client is not None
            else None
        )

    @staticmethod
    def _validate_n_results(n_results: int) -> None:
        """Validate the number of chunks requested from retrieval."""
        if (
            isinstance(n_results, bool)
            or not isinstance(n_results, int)
            or n_results <= 0
        ):
            raise ValueError("n_results must be a positive integer.")

    @staticmethod
    def _format_context(results: list[dict]) -> str:
        """Format retrieved chunks with their PDF page numbers."""
        return "\n\n".join(
            f"[Page {item['page_number']}]\n{item['text']}"
            for item in results
        )

    @staticmethod
    def _format_sources(results: list[dict]) -> list[dict]:
        """Return retrieved text and page numbers for display as sources."""
        return [
            {
                "page_number": item["page_number"],
                "text": item["text"],
            }
            for item in results
        ]

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

    def retrieve_only(
        self,
        question: str,
        document_id: str,
        n_results: int = 4,
    ) -> dict:
        """Retrieve relevant PDF passages without calling an LLM."""
        if not question or not question.strip():
            raise ValueError("Question cannot be empty.")

        if not document_id:
            raise ValueError("A processed PDF is required.")

        self._validate_n_results(n_results)

        results = self.retriever.retrieve(
            question=question,
            n_results=n_results,
            document_id=document_id,
        )

        return {
            "results": results,
            "sources": self._format_sources(results),
            "message": (
                ""
                if results
                else "I couldn't find relevant information in this PDF."
            ),
        }

    def answer_question(
        self,
        question: str,
        document_id: str,
        n_results: int = 4,
    ) -> dict:
        """Answer a question using matching PDF chunks."""
        retrieved = self.retrieve_only(
            question=question,
            document_id=document_id,
            n_results=n_results,
        )
        results = retrieved["results"]

        if not results:
            return {
                "answer": "I couldn't find relevant information in this PDF.",
                "sources": [],
            }

        if self.answer_generator is None:
            return {
                "answer": (
                    "Relevant PDF passages were retrieved, but answer "
                    "generation needs an OpenAI API key and available credits. "
                    "Use retrieve_only() to test retrieval without the API."
                ),
                "sources": retrieved["sources"],
            }

        context = self._format_context(results)
        answer = self.answer_generator.generate(context, question)

        return {
            "answer": answer,
            "sources": retrieved["sources"],
        }

    def generate_quiz(
        self,
        document_id: str,
        num_questions: int = 5,
    ) -> dict:
        """Generate quiz questions from retrieved chunks of the active PDF."""
        if not document_id:
            raise ValueError("A processed PDF is required.")

        if (
            isinstance(num_questions, bool)
            or not isinstance(num_questions, int)
            or not 1 <= num_questions <= 10
        ):
            raise ValueError("num_questions must be between 1 and 10.")

        results = self.retriever.retrieve(
            question=(
                "Key facts, concepts, definitions, processes, and important "
                "details for a study quiz"
            ),
            n_results=10,
            document_id=document_id,
        )

        if not results:
            return {
                "questions": [],
                "message": "I couldn't find relevant information in this PDF.",
            }

        if self.study_material_generator is None:
            return {
                "questions": [],
                "message": (
                    "Relevant PDF passages were retrieved, but quiz "
                    "generation needs an OpenAI API key and available credits."
                ),
                "sources": self._format_sources(results),
            }

        context = self._format_context(results)
        questions = self.study_material_generator.generate_quiz(
            context=context,
            num_questions=num_questions,
        )

        return {"questions": questions, "message": ""}

    def generate_flashcards(
        self,
        document_id: str,
        num_cards: int = 5,
    ) -> dict:
        """Generate flashcards from retrieved chunks of the active PDF."""
        if not document_id:
            raise ValueError("A processed PDF is required.")

        if (
            isinstance(num_cards, bool)
            or not isinstance(num_cards, int)
            or not 1 <= num_cards <= 10
        ):
            raise ValueError("num_cards must be between 1 and 10.")

        results = self.retriever.retrieve(
            question=(
                "Key terms, definitions, concepts, facts, and explanations "
                "useful for study flashcards"
            ),
            n_results=10,
            document_id=document_id,
        )

        if not results:
            return {
                "flashcards": [],
                "message": "I couldn't find relevant information in this PDF.",
            }

        if self.study_material_generator is None:
            return {
                "flashcards": [],
                "message": (
                    "Relevant PDF passages were retrieved, but flashcard "
                    "generation needs an OpenAI API key and available credits."
                ),
                "sources": self._format_sources(results),
            }

        context = self._format_context(results)
        flashcards = self.study_material_generator.generate_flashcards(
            context=context,
            num_cards=num_cards,
        )

        return {"flashcards": flashcards, "message": ""}
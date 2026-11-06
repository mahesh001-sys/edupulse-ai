from unittest.mock import Mock

from src import rag_pipeline


def test_answer_question_returns_answer_and_page_sources(monkeypatch, tmp_path):
    vector_store = Mock()
    retriever = Mock()
    answer_generator = Mock()

    monkeypatch.setattr(
        rag_pipeline,
        "VectorStore",
        lambda db_path: vector_store,
    )
    monkeypatch.setattr(
        rag_pipeline,
        "Retriever",
        lambda store: retriever,
    )
    monkeypatch.setattr(
        rag_pipeline,
        "AnswerGenerator",
        lambda client, model: answer_generator,
    )

    retriever.retrieve.return_value = [
        {
            "text": "The deadline is Friday.",
            "page_number": 2,
            "document_id": "sample-pdf",
            "distance": 0.1,
        }
    ]
    answer_generator.generate.return_value = "The deadline is Friday."

    pipeline = rag_pipeline.RAGPipeline(
        api_key="test-key",
        db_path=str(tmp_path / "test_chroma"),
    )

    result = pipeline.answer_question(
        question="What is the deadline?",
        document_id="sample-pdf",
    )

    assert result["answer"] == "The deadline is Friday."
    assert result["sources"] == [
        {
            "page_number": 2,
            "text": "The deadline is Friday.",
        }
    ]

    retriever.retrieve.assert_called_once_with(
        question="What is the deadline?",
        n_results=4,
        document_id="sample-pdf",
    )
    answer_generator.generate.assert_called_once_with(
        "[Page 2]\nThe deadline is Friday.",
        "What is the deadline?",
    )


def test_index_pdf_extracts_chunks_and_stores_them(monkeypatch, tmp_path):
    vector_store = Mock()
    vector_store.create_document_id.return_value = "sample-pdf-id"

    monkeypatch.setattr(
        rag_pipeline,
        "VectorStore",
        lambda db_path: vector_store,
    )
    monkeypatch.setattr(
        rag_pipeline,
        "extract_pdf_pages",
        lambda pdf_bytes: [{"page_number": 1, "text": "Sample PDF text."}],
    )

    expected_chunks = [Mock(text="Sample PDF text.", page_number=1)]
    monkeypatch.setattr(
        rag_pipeline,
        "chunk_pdf_pages",
        lambda pages: expected_chunks,
    )

    pipeline = rag_pipeline.RAGPipeline(
        api_key="test-key",
        db_path=str(tmp_path / "test_chroma"),
    )

    document_id = pipeline.index_pdf(b"fake PDF bytes")

    assert document_id == "sample-pdf-id"
    vector_store.create_document_id.assert_called_once_with(b"fake PDF bytes")
    vector_store.add_chunks.assert_called_once_with(
        expected_chunks,
        "sample-pdf-id",
    )
import pytest

@pytest.mark.parametrize(
    "question",
    ["", " ", "\n\t"],
)
def test_answer_question_rejects_blank_questions(question):
    pipeline = rag_pipeline.RAGPipeline.__new__(
        rag_pipeline.RAGPipeline
    )

    with pytest.raises(ValueError, match="Question cannot be empty"):
        pipeline.answer_question(question, "sample-pdf")


def test_answer_question_rejects_missing_document_id():
    pipeline = rag_pipeline.RAGPipeline.__new__(
        rag_pipeline.RAGPipeline
    )

    with pytest.raises(ValueError, match="processed PDF is required"):
        pipeline.answer_question("What is the deadline?", "")


@pytest.mark.parametrize("n_results", [0, -1, -5])
def test_answer_question_rejects_invalid_result_count(n_results):
    pipeline = rag_pipeline.RAGPipeline.__new__(
        rag_pipeline.RAGPipeline
    )

    with pytest.raises(ValueError, match="n_results must be a positive integer"):
        pipeline.answer_question(
            question="What is the deadline?",
            document_id="sample-pdf",
            n_results=n_results,
        )

def test_generate_quiz_bypasses_retrieval_threshold(monkeypatch, tmp_path):
    vector_store = Mock()
    retriever = Mock()
    study_generator = Mock()

    monkeypatch.setattr(rag_pipeline, "VectorStore", lambda db_path: vector_store)
    monkeypatch.setattr(rag_pipeline, "Retriever", lambda store: retriever)
    monkeypatch.setattr(
        rag_pipeline,
        "StudyMaterialGenerator",
        lambda client, model: study_generator,
    )

    retriever.retrieve.return_value = [{
        "text": "Mars is called the Red Planet.",
        "page_number": 1,
        "document_id": "sample-pdf",
        "distance": 0.8917,
    }]
    study_generator.generate_quiz.return_value = [{"question": "Why is Mars red?"}]

    pipeline = rag_pipeline.RAGPipeline(
        api_key="test-key",
        db_path=str(tmp_path / "test_chroma"),
    )

    result = pipeline.generate_quiz("sample-pdf", num_questions=1)

    assert len(result["questions"]) == 1
    assert result["message"] == ""
    retriever.retrieve.assert_called_once_with(
        question=(
            "Key facts, concepts, definitions, processes, and important "
            "details for a study quiz"
        ),
        n_results=10,
        document_id="sample-pdf",
        apply_threshold=False,
    )
    study_generator.generate_quiz.assert_called_once_with(
        context="[Page 1]\nMars is called the Red Planet.",
        num_questions=1,
    )


def test_generate_flashcards_bypasses_retrieval_threshold(monkeypatch, tmp_path):
    vector_store = Mock()
    retriever = Mock()
    study_generator = Mock()

    monkeypatch.setattr(rag_pipeline, "VectorStore", lambda db_path: vector_store)
    monkeypatch.setattr(rag_pipeline, "Retriever", lambda store: retriever)
    monkeypatch.setattr(
        rag_pipeline,
        "StudyMaterialGenerator",
        lambda client, model: study_generator,
    )

    retriever.retrieve.return_value = [{
        "text": "Mars has two moons: Phobos and Deimos.",
        "page_number": 1,
        "document_id": "sample-pdf",
        "distance": 0.9464,
    }]
    study_generator.generate_flashcards.return_value = [{
        "front": "What are the moons of Mars?",
        "back": "Phobos and Deimos.",
    }]

    pipeline = rag_pipeline.RAGPipeline(
        api_key="test-key",
        db_path=str(tmp_path / "test_chroma"),
    )

    result = pipeline.generate_flashcards("sample-pdf", num_cards=1)

    assert len(result["flashcards"]) == 1
    assert result["message"] == ""
    retriever.retrieve.assert_called_once_with(
        question=(
            "Key terms, definitions, concepts, facts, and explanations "
            "useful for study flashcards"
        ),
        n_results=10,
        document_id="sample-pdf",
        apply_threshold=False,
    )
    study_generator.generate_flashcards.assert_called_once_with(
        context="[Page 1]\nMars has two moons: Phobos and Deimos.",
        num_cards=1,
    )

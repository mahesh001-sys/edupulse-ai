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
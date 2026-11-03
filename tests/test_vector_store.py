import pytest

from src.chunking.text_chunker import DocumentChunk
from src.vectordb.vector_store import VectorStore


@pytest.fixture
def vector_store(tmp_path):
    return VectorStore(
        db_path=str(tmp_path / "test_chroma"),
        collection_name="test_documents",
    )


def test_store_and_retrieve_chunks(vector_store):
    chunks = [
        DocumentChunk(
            text="Java is an object-oriented programming language.",
            page_number=2,
        ),
        DocumentChunk(
            text="Python is widely used for data science.",
            page_number=5,
        ),
    ]

    document_id = "test_document"

    count = vector_store.add_chunks(chunks, document_id)

    assert count == 2

    results = vector_store.search(
        query="What is Java?",
        n_results=1,
        document_id=document_id,
    )

    assert len(results) == 1
    assert results[0]["page_number"] == 2
    assert "Java" in results[0]["text"]


def test_empty_search_returns_no_results(vector_store):
    results = vector_store.search("What is Java?")

    assert results == []


def test_empty_query_is_rejected(vector_store):
    with pytest.raises(ValueError, match="empty"):
        vector_store.search("")


def test_delete_document(vector_store):
    chunks = [
        DocumentChunk(
            text="EduPulse AI uses ChromaDB.",
            page_number=1,
        )
    ]

    vector_store.add_chunks(chunks, "delete_test")
    vector_store.delete_document("delete_test")

    results = vector_store.search(
        "What does EduPulse AI use?",
        document_id="delete_test",
    )

    assert results == []


@pytest.mark.parametrize("n_results", [0, -1, -5, True, 1.5, "2"])
def test_invalid_n_results_is_rejected(vector_store, n_results):
    with pytest.raises(ValueError, match="n_results"):
        vector_store.search(
            query="What is Java?",
            n_results=n_results,
        )


def test_missing_document_id_returns_no_results(vector_store):
    vector_store.add_chunks(
        [
            DocumentChunk(
                text="Java is an object-oriented programming language.",
                page_number=2,
            )
        ],
        document_id="existing_document",
    )

    results = vector_store.search(
        query="What is Java?",
        document_id="missing_document",
    )

    assert results == []


def test_document_filter_does_not_return_other_documents(vector_store):
    vector_store.add_chunks(
        [
            DocumentChunk(
                text="Java is an object-oriented programming language.",
                page_number=2,
            )
        ],
        document_id="document_a",
    )
    vector_store.add_chunks(
        [
            DocumentChunk(
                text="Java is a programming language.",
                page_number=8,
            )
        ],
        document_id="document_b",
    )

    results = vector_store.search(
        query="What is Java?",
        n_results=4,
        document_id="document_a",
    )

    assert results
    assert all(result["document_id"] == "document_a" for result in results)
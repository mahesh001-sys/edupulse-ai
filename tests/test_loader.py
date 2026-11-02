from io import BytesIO

import pytest
from pypdf import PdfWriter

from src.ingestion.loader import extract_pdf_pages
from src.chunking.text_chunker import chunk_pdf_pages


def create_test_pdf() -> bytes:
    """Create a small PDF for testing."""
    writer = PdfWriter()
    writer.add_blank_page(width=300, height=300)

    buffer = BytesIO()
    writer.write(buffer)

    return buffer.getvalue()


def test_empty_pdf_is_rejected():
    with pytest.raises(ValueError, match="empty"):
        extract_pdf_pages(b"")


def test_pdf_without_text_is_rejected():
    pdf_bytes = create_test_pdf()

    with pytest.raises(ValueError, match="No readable text"):
        extract_pdf_pages(pdf_bytes)


def test_chunking_preserves_page_numbers():
    pages = [
        {
            "page_number": 3,
            "text": "A" * 1000,
        }
    ]

    chunks = chunk_pdf_pages(
        pages,
        chunk_size=400,
        chunk_overlap=100,
    )

    assert len(chunks) == 4
    assert all(chunk.page_number == 3 for chunk in chunks)
    assert all(len(chunk.text) <= 400 for chunk in chunks)


def test_chunking_rejects_invalid_overlap():
    with pytest.raises(ValueError, match="smaller"):
        chunk_pdf_pages(
            [{"page_number": 1, "text": "Hello"}],
            chunk_size=100,
            chunk_overlap=100,
        )


def test_empty_page_is_skipped():
    pages = [
        {"page_number": 1, "text": ""},
        {"page_number": 2, "text": "Hello EduPulse"},
    ]

    chunks = chunk_pdf_pages(pages)

    assert len(chunks) == 1
    assert chunks[0].page_number == 2
    assert chunks[0].text == "Hello EduPulse"

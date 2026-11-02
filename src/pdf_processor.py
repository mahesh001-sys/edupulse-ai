"""PDF extraction and text chunking for EduPulse AI."""

from dataclasses import dataclass
from io import BytesIO
from typing import List

from pypdf import PdfReader


@dataclass(frozen=True)
class DocumentChunk:
    """A text chunk with its original PDF page number."""

    text: str
    page_number: int


def extract_pdf_pages(pdf_bytes: bytes) -> List[dict]:
    """
    Extract text from a PDF.

    Args:
        pdf_bytes: The uploaded PDF file as bytes.

    Returns:
        A list of dictionaries containing page_number and text.

    Raises:
        ValueError: If the PDF is invalid, encrypted, or has no text.
    """
    if not pdf_bytes:
        raise ValueError("The uploaded PDF is empty.")

    try:
        reader = PdfReader(BytesIO(pdf_bytes))

        if reader.is_encrypted:
            raise ValueError(
                "This PDF is password-protected. "
                "Please upload an unlocked PDF."
            )

        pages = []

        for page_number, page in enumerate(reader.pages, start=1):
            text = page.extract_text() or ""
            text = " ".join(text.split())

            if text:
                pages.append(
                    {
                        "page_number": page_number,
                        "text": text,
                    }
                )

        if not pages:
            raise ValueError(
                "No readable text was found. "
                "The PDF may contain scanned images."
            )

        return pages

    except ValueError:
        raise
    except Exception as exc:
        raise ValueError(
            "Unable to read this PDF. "
            "Please upload a valid PDF file."
        ) from exc


def chunk_pdf_pages(
    pages: List[dict],
    chunk_size: int = 800,
    chunk_overlap: int = 150,
) -> List[DocumentChunk]:
    """
    Split extracted page text into overlapping chunks.

    Chunk sizes and overlap are measured in characters.

    Each chunk retains its original PDF page number.
    """
    if chunk_size <= 0:
        raise ValueError("chunk_size must be greater than zero.")

    if chunk_overlap < 0:
        raise ValueError("chunk_overlap cannot be negative.")

    if chunk_overlap >= chunk_size:
        raise ValueError("chunk_overlap must be smaller than chunk_size.")

    chunks = []
    step = chunk_size - chunk_overlap

    for page in pages:
        text = page.get("text", "").strip()
        page_number = page.get("page_number")

        if not text:
            continue

        if not isinstance(page_number, int) or page_number < 1:
            raise ValueError("Each page must have a valid page number.")

        for start in range(0, len(text), step):
            chunk_text = text[start : start + chunk_size].strip()

            if chunk_text:
                chunks.append(
                    DocumentChunk(
                        text=chunk_text,
                        page_number=page_number,
                    )
                )

    return chunks

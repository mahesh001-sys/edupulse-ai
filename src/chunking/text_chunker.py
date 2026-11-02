"""Split extracted PDF page text into overlapping chunks."""

from dataclasses import dataclass
from typing import List


@dataclass(frozen=True)
class DocumentChunk:
    """A text chunk with its original PDF page number."""

    text: str
    page_number: int


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
"""PDF text extraction for EduPulse AI."""

from io import BytesIO
from typing import List

from pypdf import PdfReader


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
"""PDF parser extracting text with pypdf, falling back to raw bytes for scanned pages."""
from __future__ import annotations

import io
from typing import Tuple, Union
import pypdf


def extract_pdf(pdf_bytes: bytes) -> Tuple[str, Union[bytes, None]]:
    """Extract text from PDF. If text density < 200 chars/page, return raw bytes for OCR."""
    try:
        reader = pypdf.PdfReader(io.BytesIO(pdf_bytes))
        num_pages = len(reader.pages)
        if num_pages == 0:
            return "", pdf_bytes

        page_texts = []
        total_chars = 0
        for page in reader.pages:
            txt = page.extract_text() or ""
            page_texts.append(txt)
            total_chars += len(txt.strip())

        avg_chars_per_page = total_chars / max(1, num_pages)
        extracted = "\n\n--- Page Break ---\n\n".join(page_texts).strip()

        if avg_chars_per_page < 200:
            # Scanned or image-heavy PDF, pass raw PDF bytes to vision model
            return extracted, pdf_bytes

        return extracted, None
    except Exception:
        # If extraction fails (e.g. corrupt or scanned), return raw bytes for OCR
        return "", pdf_bytes

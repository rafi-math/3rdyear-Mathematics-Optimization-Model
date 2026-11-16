"""DOCX parser extracting paragraphs and tables into structured markdown."""
from __future__ import annotations

import io
from docx import Document


def extract_docx(docx_bytes: bytes) -> str:
    """Extract paragraphs and tables from a Word document as markdown text."""
    doc = Document(io.BytesIO(docx_bytes))
    parts = []

    for block in doc.element.body:
        tag = block.tag.split("}")[-1]
        if tag == "p":
            text = block.text.strip()
            if text:
                parts.append(text)
        elif tag == "tbl":
            # Convert table to markdown
            for row in block.findall(".//{http://schemas.openxmlformats.org/wordprocessingml/2006/main}tr"):
                cells = [
                    "".join(cell.itertext()).strip()
                    for cell in row.findall(".//{http://schemas.openxmlformats.org/wordprocessingml/2006/main}tc")
                ]
                if cells:
                    parts.append("| " + " | ".join(cells) + " |")

    return "\n\n".join(parts)

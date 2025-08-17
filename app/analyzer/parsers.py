import io
from typing import Optional

from PyPDF2 import PdfReader
from docx import Document


def _extract_text_from_pdf_bytes(data: bytes) -> str:
    reader = PdfReader(io.BytesIO(data))
    texts = []
    for page in reader.pages:
        try:
            texts.append(page.extract_text() or "")
        except Exception:
            texts.append("")
    return "\n".join(texts)


def _extract_text_from_docx_bytes(data: bytes) -> str:
    doc = Document(io.BytesIO(data))
    return "\n".join(p.text for p in doc.paragraphs)


def _extract_text_from_txt_bytes(data: bytes) -> str:
    for encoding in ("utf-8", "latin-1", "utf-16"):
        try:
            return data.decode(encoding)
        except Exception:
            continue
    return data.decode(errors="ignore")


def extract_text_from_bytes(filename: Optional[str], data: bytes) -> str:
    name = (filename or "uploaded").lower()
    if name.endswith(".pdf"):
        return _extract_text_from_pdf_bytes(data)
    if name.endswith(".docx"):
        return _extract_text_from_docx_bytes(data)
    if name.endswith(".txt"):
        return _extract_text_from_txt_bytes(data)
    # Best-effort default
    return _extract_text_from_txt_bytes(data)
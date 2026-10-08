from __future__ import annotations

from pathlib import Path

from docx import Document as DocxDocument
from pypdf import PdfReader


def extract_text_from_file(file_path: str | Path) -> str:
    file_path = Path(file_path)
    suffix = file_path.suffix.lower()

    if suffix == ".docx":
        return _extract_docx(file_path)
    if suffix == ".pdf":
        return _extract_pdf(file_path)
    if suffix == ".txt":
        return _extract_txt(file_path)

    raise ValueError("Faqat .txt, .docx yoki .pdf fayllari qabul qilinadi.")


def _extract_docx(file_path: Path) -> str:
    doc = DocxDocument(str(file_path))
    paragraphs = [p.text.strip() for p in doc.paragraphs if p.text.strip()]
    return "\n".join(paragraphs)


def _extract_pdf(file_path: Path) -> str:
    reader = PdfReader(str(file_path))
    pages: list[str] = []
    for page in reader.pages:
        text = page.extract_text() or ""
        if text:
            pages.append(text)
    text = "\n".join(pages).strip()
    if not text:
        raise ValueError("PDF dan matn o'qib bo'lmadi. Skan qilingan PDF bo'lsa, OCR kerak bo'ladi.")
    return text


def _extract_txt(file_path: Path) -> str:
    return file_path.read_text(encoding="utf-8", errors="replace")

from __future__ import annotations


def chunk_text(text: str, max_chars: int = 3500) -> list[str]:
    if not text:
        return []

    paragraphs = [p.strip() for p in text.splitlines() if p.strip()]
    chunks: list[str] = []
    current = ""

    for para in paragraphs:
        if len(current) + len(para) + 1 <= max_chars:
            current = f"{current}\n{para}" if current else para
        else:
            if current:
                chunks.append(current.strip())
            if len(para) > max_chars:
                for part in _split_long_paragraph(para, max_chars):
                    chunks.append(part)
                current = ""
            else:
                current = para

    if current:
        chunks.append(current.strip())

    return [chunk for chunk in chunks if chunk]


def _split_long_paragraph(paragraph: str, max_chars: int) -> list[str]:
    words = paragraph.split()
    parts: list[str] = []
    current = ""
    for word in words:
        if len(current) + len(word) + 1 <= max_chars:
            current = f"{current} {word}".strip()
        else:
            if current:
                parts.append(current)
            current = word
    if current:
        parts.append(current)
    return parts

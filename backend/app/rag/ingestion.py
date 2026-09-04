"""Safe text ingestion for the local knowledge retriever."""

from pathlib import Path
from uuid import uuid4

from app.rag.retrieval import add_chunks

ALLOWED_EXTENSIONS = {".txt", ".md", ".csv"}


def _chunk_text(text: str, chunk_size: int = 900) -> list[str]:
    paragraphs = [part.strip() for part in text.replace("\r\n", "\n").split("\n\n")]
    chunks: list[str] = []
    current = ""
    for paragraph in (part for part in paragraphs if part):
        if current and len(current) + len(paragraph) + 2 > chunk_size:
            chunks.append(current)
            current = paragraph
        else:
            current = f"{current}\n\n{paragraph}".strip()
    if current:
        chunks.append(current)
    return chunks


def ingest_document(bot_id: str, file_name: str, content: bytes, max_bytes: int) -> tuple[str, int]:
    suffix = Path(file_name).suffix.lower()
    if suffix not in ALLOWED_EXTENSIONS:
        raise ValueError("Only .txt, .md, and .csv knowledge files are accepted in the MVP.")
    if not content or len(content) > max_bytes:
        raise ValueError(f"Knowledge files must contain between 1 and {max_bytes} bytes.")
    try:
        text = content.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise ValueError("Knowledge files must use UTF-8 encoding.") from exc

    chunks = _chunk_text(text)
    if not chunks:
        raise ValueError("The knowledge file does not contain readable text.")
    source_id = f"{Path(file_name).stem[:32]}-{uuid4().hex[:8]}"
    add_chunks(bot_id, source_id, chunks)
    return source_id, len(chunks)

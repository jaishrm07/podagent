import re
import unicodedata
from pathlib import Path
from typing import Iterable, List, Tuple
import json


def slugify(value: str) -> str:
    """
    Create a filesystem-friendly slug from a filename/title.
    """
    value = (
        unicodedata.normalize("NFKD", value)
        .encode("ascii", "ignore")
        .decode("ascii")
    )
    value = re.sub(r"[^\w\s-]", "", value).strip().lower()
    value = re.sub(r"[-\s]+", "-", value)
    return value


def clean_transcript_text(text: str) -> str:
    """
    Basic transcript cleaning: strip boilerplate, collapse whitespace, and
    keep timestamp markers if present.
    """
    lines = text.splitlines()
    cleaned: List[str] = []
    in_toc = False
    for line in lines:
        stripped = line.strip()
        if not stripped:
            continue
        low = stripped.lower()

        # Drop obvious boilerplate markers and header fluff
        header_phrases = [
            "source:",
            "this is a transcript of",
            "timestamps in the transcript",
            "please note that the transcript",
            "useful links",
            "full youtube version",
            "watch the full youtube",
            "this episode’s main page",
            "this episode's main page",
            "go back to",
            "table of contents",
            "here are the loose",
            "click link to jump",
        ]
        if any(h in low for h in header_phrases):
            # Enter TOC block if we see a table of contents marker
            if "table of contents" in low:
                in_toc = True
            continue

        # Skip table-of-contents timestamp bullets
        if in_toc:
            if re.match(r"^\d{1,2}:\d{2}(?::\d{2})?\s*[–—-]", stripped):
                continue
            if re.match(r"^\d{1,2}:\d{2}(?::\d{2})?$", stripped):
                continue
            if "chapter" in low or "jump" in low:
                continue
            # end of TOC block once we hit non-timestamp text
            in_toc = False

        cleaned.append(stripped)

    text = " ".join(cleaned)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def sentence_split(text: str) -> List[str]:
    """
    Lightweight sentence splitter based on punctuation.
    """
    parts = re.split(r"(?<=[.!?])\s+", text)
    return [p.strip() for p in parts if p.strip()]


def chunk_text(
    text: str,
    max_words: int = 400,
    overlap_words: int = 120,
) -> List[Tuple[int, str]]:
    """
    Split long text into overlapping word-based chunks using a streaming tokenizer
    to avoid loading all words into memory at once.

    Returns a list of (chunk_id, chunk_text).
    """
    if max_words <= 0:
        return []
    if overlap_words >= max_words:
        overlap_words = max_words // 2

    chunks: List[Tuple[int, str]] = []
    window: List[str] = []
    chunk_id = 0

    for match in re.finditer(r"\S+", text):
        window.append(match.group())
        if len(window) >= max_words:
            chunk_text = " ".join(window)
            chunks.append((chunk_id, chunk_text))
            chunk_id += 1
            # Keep only the overlap from the current window
            if overlap_words > 0:
                window = window[-overlap_words :]
            else:
                window = []

    # Flush remainder
    if window:
        chunks.append((chunk_id, " ".join(window)))

    return chunks


def read_jsonl(path: Path) -> List[dict]:
    records: List[dict] = []
    if not path.exists():
        return records
    for line in path.read_text().splitlines():
        line = line.strip()
        if not line:
            continue
        records.append(json.loads(line))
    return records


def write_jsonl(path: Path, rows: Iterable[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")

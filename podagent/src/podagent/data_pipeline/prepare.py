import re
from pathlib import Path
from typing import Dict, List, Optional

from podagent import config
from podagent.utils import clean_transcript_text, chunk_text, slugify, write_jsonl


def extract_title(path: Path) -> str:
    """
    Use filename (sans extension) as the title.
    """
    return path.stem


def read_transcript(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="ignore")


def process_single_transcript(
    path: Path,
    max_words: int = 400,
    overlap_words: int = 120,
) -> Dict[str, List[dict]]:
    """
    Clean and chunk one transcript file into a list of chunk dicts.
    """
    raw_text = read_transcript(path)
    cleaned = clean_transcript_text(raw_text)
    chunks = chunk_text(cleaned, max_words=max_words, overlap_words=overlap_words)

    episode_id = slugify(extract_title(path))
    chunk_rows: List[dict] = []
    for idx, ctext in chunks:
        chunk_rows.append(
            {
                "episode_id": episode_id,
                "chunk_id": idx,
                "text": ctext,
                "start_time": None,
                "end_time": None,
                "speakers": [],
                "source_path": str(path),
            }
        )

    return {"episode_id": episode_id, "chunks": chunk_rows}


def process_all_transcripts(
    transcripts_dir: Optional[Path] = None,
    output_dir: Optional[Path] = None,
    max_words: int = 400,
    overlap_words: int = 120,
) -> Path:
    """
    Process every transcript under `transcripts_dir` into per-episode JSONL files and
    a manifest. Returns the manifest path.
    """
    transcripts_dir = transcripts_dir or config.TRANSCRIPTS_DIR
    output_dir = output_dir or config.INTERIM_DIR
    config.ensure_directories()

    transcript_files = sorted(
        [p for p in transcripts_dir.glob("*.txt") if p.is_file()]
    )
    manifest: List[dict] = []

    for path in transcript_files:
        result = process_single_transcript(
            path, max_words=max_words, overlap_words=overlap_words
        )
        episode_id = result["episode_id"]
        chunks = result["chunks"]
        out_path = output_dir / f"{episode_id}.jsonl"
        write_jsonl(out_path, chunks)
        manifest.append(
            {
                "episode_id": episode_id,
                "num_chunks": len(chunks),
                "source_file": str(path),
                "chunk_file": str(out_path),
            }
        )

    manifest_path = output_dir / "manifest.jsonl"
    write_jsonl(manifest_path, manifest)
    return manifest_path

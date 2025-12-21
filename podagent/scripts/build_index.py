#!/usr/bin/env python3
"""
Build an embedding index over chunked transcripts.
"""
import argparse
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT / "src"))

from podagent import config  # noqa: E402
from podagent.retriever import build_index_from_chunks  # noqa: E402


def main():
    parser = argparse.ArgumentParser(description="Build FAISS index for transcript chunks.")
    parser.add_argument(
        "--interim-dir",
        type=Path,
        default=config.INTERIM_DIR,
        help="Directory with chunked JSONL files.",
    )
    parser.add_argument(
        "--model-name",
        type=str,
        default="sentence-transformers/all-MiniLM-L6-v2",
        help="SentenceTransformer model name.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=config.PROCESSED_DIR / "chunks.index",
        help="Where to save FAISS index.",
    )
    args = parser.parse_args()

    retriever = build_index_from_chunks(interim_dir=args.interim_dir, model_name=args.model_name)
    retriever.save(args.output)
    print(f"Saved index to {args.output}")


if __name__ == "__main__":
    main()

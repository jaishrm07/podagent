#!/usr/bin/env python3
"""
Ingest and chunk all raw transcripts.
"""
import argparse
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT / "src"))

from podagent.data_pipeline.prepare import process_all_transcripts  # noqa: E402
from podagent import config  # noqa: E402


def main():
    parser = argparse.ArgumentParser(description="Ingest and chunk raw transcripts.")
    parser.add_argument(
        "--transcripts-dir",
        type=Path,
        default=config.TRANSCRIPTS_DIR,
        help="Directory containing raw transcript .txt files.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=config.INTERIM_DIR,
        help="Where to write chunked JSONL files.",
    )
    parser.add_argument("--max-words", type=int, default=400, help="Words per chunk.")
    parser.add_argument(
        "--overlap-words", type=int, default=120, help="Word overlap between chunks."
    )
    args = parser.parse_args()

    manifest = process_all_transcripts(
        transcripts_dir=args.transcripts_dir,
        output_dir=args.output_dir,
        max_words=args.max_words,
        overlap_words=args.overlap_words,
    )
    print(f"Wrote manifest: {manifest}")


if __name__ == "__main__":
    main()

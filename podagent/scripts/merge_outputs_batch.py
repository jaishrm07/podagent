#!/usr/bin/env python3
"""
Merge multiple summarization outputs (from scripts/summarize.py --output-json)
into the frontend podcasts.json as separate summary entries for the same episode.

Usage:
  PYTHONPATH=podagent/src python podagent/scripts/merge_outputs_batch.py \
    --outputs output1_1.json output1_2.json output1_3.json \
    --podcasts-json podagent/src/web/frontend/src/data/podcasts.json \
    --podcast-key transcript-for-adam-frank-alien-civilizations-and-the-search-for-extraterrestrial-life-lex-fridman

Each output file becomes its own summary object (abstract, outline, quotes, q_and_a,
keywords/tags) keyed by the supplied labels (default: filename stems). Top-level tags
are the de-duplicated union of all keywords.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Dict, List


def _read_output(path: Path) -> Dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if "episode_id" not in data:
        raise ValueError(f"{path} is missing episode_id")
    return data


def _dedup_list(items: List[str]) -> List[str]:
    seen = set()
    out = []
    for it in items:
        if it not in seen:
            seen.add(it)
            out.append(it)
    return out


def main() -> None:
    parser = argparse.ArgumentParser(description="Merge multiple output.json files into podcasts.json.")
    parser.add_argument("--outputs", nargs="+", required=True, help="List of output JSON files to merge.")
    parser.add_argument("--labels", nargs="*", help="Optional labels matching --outputs; defaults to filename stems.")
    parser.add_argument("--podcasts-json", type=Path, required=True, help="Path to frontend podcasts.json.")
    parser.add_argument(
        "--podcast-key",
        type=str,
        default=None,
        help="Entry key to use in podcasts.json (defaults to episode_id from first output).",
    )
    parser.add_argument("--title", type=str, default=None, help="Optional override for title.")
    parser.add_argument("--host", type=str, default=None, help="Optional override for host.")
    parser.add_argument("--date", type=str, default="", help="Optional date string.")
    parser.add_argument("--duration", type=str, default="", help="Optional duration string.")
    args = parser.parse_args()

    outputs: List[Dict[str, Any]] = []
    labels: List[str] = []
    for i, p in enumerate(args.outputs):
        path = Path(p)
        data = _read_output(path)
        outputs.append(data)
        if args.labels and i < len(args.labels):
            labels.append(args.labels[i])
        else:
            labels.append(path.stem)

    if not outputs:
        raise SystemExit("No outputs loaded.")

    episode_id = outputs[0]["episode_id"]
    podcast_key = args.podcast_key or episode_id

    summaries: Dict[str, Any] = {}
    all_keywords: List[str] = []

    for label, data in zip(labels, outputs):
        if data.get("episode_id") != episode_id:
            raise SystemExit(f"Episode mismatch: {label} has {data.get('episode_id')} expected {episode_id}")
        summaries[label] = {
            "abstract": data.get("abstract", ""),
            "outline": data.get("outline", []) or [],
            "quotes": data.get("quotes", []) or [],
            "q_and_a": data.get("q_and_a", []) or [],
            "keywords": data.get("keywords", []) or [],
            "tags": data.get("keywords", []) or [],
        }
        all_keywords.extend(data.get("keywords", []) or [])

    tags = _dedup_list([str(k) for k in all_keywords if str(k).strip()])

    existing: Dict[str, Any] = {}
    if args.podcasts_json.exists():
        existing = json.loads(args.podcasts_json.read_text(encoding="utf-8"))

    entry = existing.get(podcast_key) if isinstance(existing.get(podcast_key), dict) else {}
    entry_title = args.title or entry.get("title") or episode_id
    entry_host = args.host or entry.get("host") or ""

    entry.update(
        {
            "title": entry_title,
            "host": entry_host,
            "date": args.date or entry.get("date", ""),
            "duration": args.duration or entry.get("duration", ""),
            "tags": tags,
            "summaries": summaries,
            "transcript": entry.get("transcript", ""),
        }
    )

    existing[podcast_key] = entry
    args.podcasts_json.parent.mkdir(parents=True, exist_ok=True)
    args.podcasts_json.write_text(json.dumps(existing, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Updated {args.podcasts_json} with {len(outputs)} summaries (key={podcast_key}).")


if __name__ == "__main__":
    main()

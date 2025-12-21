#!/usr/bin/env python3
"""
Merge a saved summarization output JSON (from scripts/summarize.py --output-json)
into the frontend's podcasts.json format used by the web UI.

Example:
  PYTHONPATH=podagent/src python podagent/scripts/merge_output_into_podcasts.py \
    output.json \
    --podcasts-json podagent/src/web/frontend/src/data/podcasts.json \
    --podcast-key adam-frank-lex-fridman
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional


ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT / "src"))

from podagent import config  # noqa: E402
from podagent.models.agent import load_chunks_for_episode  # noqa: E402


def _clean_title_from_filename(stem: str) -> str:
    title = stem.strip()
    if title.lower().startswith("transcript for "):
        title = title[len("Transcript for ") :].strip()
    # remove repeated whitespace
    title = " ".join(title.split())
    return title


def _infer_transcript_and_title(episode_id: str) -> tuple[str, str]:
    chunks = load_chunks_for_episode(episode_id)
    if chunks:
        source_path = chunks[0].get("source_path")
        if source_path:
            p = Path(source_path)
            try:
                transcript = p.read_text(encoding="utf-8", errors="ignore")
            except Exception:
                transcript = ""
            title = _clean_title_from_filename(p.stem)
            return transcript, title

        # Fallback: stitch together the stored chunk texts
        transcript = "\n\n".join((c.get("text") or "").strip() for c in chunks if c.get("text"))
        return transcript, episode_id

    return "", episode_id


def _infer_host(title: str, episode_id: str) -> str:
    combined = f"{title} {episode_id}".lower()
    if "lex fridman" in combined or "lex-fridman" in combined:
        return "Lex Fridman"
    return ""


def _as_list_of_strings(value: Any) -> List[str]:
    if not value:
        return []
    if isinstance(value, list):
        return [str(v) for v in value if str(v).strip()]
    return [str(value)]


def main() -> None:
    parser = argparse.ArgumentParser(description="Merge saved output.json into podcasts.json.")
    parser.add_argument("output_json", type=Path, help="Path to output.json from scripts/summarize.py.")
    parser.add_argument("--podcasts-json", type=Path, required=True, help="Path to frontend podcasts.json.")
    parser.add_argument("--podcast-key", type=str, default=None, help="Entry key to use (defaults to episode_id).")
    parser.add_argument("--model-label", type=str, default="GPT-4o", help="Key to use under `summaries`.")
    parser.add_argument("--title", type=str, default=None, help="Override title.")
    parser.add_argument("--host", type=str, default=None, help="Override host.")
    parser.add_argument("--date", type=str, default="", help="Date string (optional).")
    parser.add_argument("--duration", type=str, default="", help="Duration string (optional).")
    args = parser.parse_args()

    if not args.output_json.exists():
        raise SystemExit(f"Not found: {args.output_json}")

    data: Dict[str, Any] = json.loads(args.output_json.read_text(encoding="utf-8"))
    episode_id = str(data.get("episode_id") or "").strip()
    if not episode_id:
        raise SystemExit("output_json is missing `episode_id`.")

    transcript, inferred_title = _infer_transcript_and_title(episode_id)
    title = args.title or inferred_title or episode_id
    host = args.host or _infer_host(title, episode_id)

    keywords = _as_list_of_strings(data.get("keywords"))
    outline = _as_list_of_strings(data.get("outline"))
    quotes = _as_list_of_strings(data.get("quotes"))
    q_and_a = data.get("q_and_a") or []

    if not isinstance(q_and_a, list):
        q_and_a = _as_list_of_strings(q_and_a)

    entry_key = args.podcast_key or episode_id

    existing: Dict[str, Any] = {}
    if args.podcasts_json.exists():
        existing = json.loads(args.podcasts_json.read_text(encoding="utf-8"))

    # Keep existing summaries if present, then upsert our model label.
    existing_summaries = (existing.get(entry_key, {}).get("summaries") if isinstance(existing.get(entry_key), dict) else None) or {}
    if not isinstance(existing_summaries, dict):
        existing_summaries = {}
    existing_summaries[args.model_label] = data.get("abstract", "") or ""

    existing[entry_key] = {
        "title": title,
        "host": host,
        "date": args.date,
        "duration": args.duration,
        "tags": keywords,
        "summaries": existing_summaries,
        # Extra fields (webapp can ignore these until you render them)
        "outline": outline,
        "quotes": quotes,
        "q_and_a": q_and_a,
        "transcript": transcript,
    }

    args.podcasts_json.parent.mkdir(parents=True, exist_ok=True)
    args.podcasts_json.write_text(json.dumps(existing, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Updated: {args.podcasts_json} (key={entry_key}, model={args.model_label})")


if __name__ == "__main__":
    main()


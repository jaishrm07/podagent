#!/usr/bin/env python3
"""
Summarize a single episode using the agentic pipeline.
"""
import argparse
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT / "src"))

from podagent import config  # noqa: E402
from podagent.models import OpenAISummarizer, PodcastSummarizer, TogetherSummarizer  # noqa: E402
from podagent.models.agent import load_chunks_for_episode  # noqa: E402
from podagent.retriever import EmbeddingRetriever  # noqa: E402


def main():
    parser = argparse.ArgumentParser(description="Summarize a podcast episode.")
    parser.add_argument("episode_id", type=str, help="Slug of the episode (from chunk filename).")
    parser.add_argument(
        "--query",
        type=str,
        default=None,
        help="Optional focus question; triggers retrieval if provided.",
    )
    parser.add_argument(
        "--mode",
        choices=["openai", "together"],
        default="openai",
        help="Summarizer provider: OpenAI gpt-4o or Together-hosted models.",
    )
    parser.add_argument(
        "--model-name",
        type=str,
        default=None,
        help="Model name (defaults: openai=gpt-4o, together=meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo).",
    )
    parser.add_argument(
        "--index",
        type=Path,
        default=None,
        help="Path to a saved FAISS index; if provided, enables retrieval.",
    )
    parser.add_argument(
        "--context-chunks",
        type=int,
        default=5,
        help="Number of chunks to use as context when not running hierarchical mode.",
    )
    parser.add_argument(
        "--hierarchical",
        action="store_true",
        help="Enable two-pass summarization over the full transcript (summarize chunk groups, then summarize the summaries).",
    )
    parser.add_argument(
        "--group-size",
        type=int,
        default=8,
        help="How many chunks per group in hierarchical mode.",
    )
    parser.add_argument(
        "--structured",
        action="store_true",
        help="Ask the LLM (openai mode) to return structured sections (abstract, outline, quotes, Q&A, keywords) instead of local heuristics.",
    )
    parser.add_argument(
        "--output-json",
        type=Path,
        default=None,
        help="Write the raw summary output JSON to this path (episode_id, abstract, outline, quotes, q_and_a, keywords).",
    )
    parser.add_argument(
        "--podcasts-json",
        type=Path,
        default=None,
        help="Update a webapp-style podcasts.json file (see src/web/frontend/src/data/podcasts.json).",
    )
    parser.add_argument(
        "--podcast-key",
        type=str,
        default=None,
        help="Key to use when writing into --podcasts-json (defaults to episode_id).",
    )
    parser.add_argument(
        "--summary-label",
        type=str,
        default=None,
        help="Key to use under `summaries` in podcasts.json (defaults: GPT-4o for openai, Llama3-8B for together).",
    )
    parser.add_argument("--title", type=str, default=None, help="Optional display title.")
    parser.add_argument("--host", type=str, default=None, help="Optional host name.")
    parser.add_argument("--date", type=str, default=None, help="Optional date string (e.g., 2024-08-04).")
    parser.add_argument("--duration", type=str, default=None, help="Optional duration string (e.g., 42m).")
    parser.add_argument(
        "--intermediate-min-words",
        type=int,
        default=180,
        help="Minimum words for each intermediate (group) summary in hierarchical mode.",
    )
    parser.add_argument(
        "--intermediate-max-words",
        type=int,
        default=300,
        help="Maximum words for each intermediate (group) summary in hierarchical mode.",
    )
    parser.add_argument(
        "--final-target-words",
        type=int,
        default=700,
        help="Target words for the final structured summary.",
    )
    parser.add_argument(
        "--final-max-tokens",
        type=int,
        default=1800,
        help="Max tokens allowed for the final structured summary response.",
    )
    args = parser.parse_args()

    try:
        if args.mode == "together":
            summarizer = TogetherSummarizer(
                model=args.model_name or "meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo"
            )
        else:
            summarizer = OpenAISummarizer(model=args.model_name or "gpt-4o")
    except Exception as exc:
        print(f"Failed to initialize summarizer: {exc}", file=sys.stderr)
        if args.mode == "together":
            print("Tip: export `TOGETHER_API_KEY` before running.", file=sys.stderr)
        else:
            print("Tip: export `OPENAI_API_KEY` before running.", file=sys.stderr)
        raise SystemExit(1) from exc

    retriever = None
    if args.index:
        try:
            retriever = EmbeddingRetriever.load(args.index)
        except Exception as exc:
            print(f"Could not load index; continuing without retrieval. Error: {exc}")

    agent = PodcastSummarizer(
        summarizer=summarizer,
        retriever=retriever,
        max_context_chunks=args.context_chunks,
    )
    try:
        result = agent.summarize_episode(
            args.episode_id,
            query=args.query,
            hierarchical=args.hierarchical,
            group_size=args.group_size,
            structured=args.structured,
            intermediate_min_words=args.intermediate_min_words,
            intermediate_max_words=args.intermediate_max_words,
            final_target_words=args.final_target_words,
            final_max_tokens=args.final_max_tokens,
        )
    except Exception as exc:
        print(f"Summarization failed: {exc}", file=sys.stderr)
        if args.mode == "together":
            print("Tip: ensure `TOGETHER_API_KEY` is set and reachable when using `--mode together`.", file=sys.stderr)
        else:
            print("Tip: ensure `OPENAI_API_KEY` is set and reachable when using `--mode openai`.", file=sys.stderr)
        raise SystemExit(1) from exc

    raw_output = {
        "episode_id": result.episode_id,
        "abstract": result.abstract,
        "outline": result.outline,
        "quotes": result.quotes,
        "q_and_a": result.q_and_a,
        "keywords": result.keywords,
        "evidence": [{"chunk": r.chunk, "score": r.score} for r in (result.evidence or [])],
    }

    if args.output_json:
        args.output_json.parent.mkdir(parents=True, exist_ok=True)
        args.output_json.write_text(json.dumps(raw_output, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"Wrote JSON: {args.output_json}")

    if args.podcasts_json:
        chunks = load_chunks_for_episode(args.episode_id)
        source_path = (chunks[0].get("source_path") if chunks else None) or None
        transcript = ""
        inferred_title = args.episode_id
        inferred_host = ""
        if source_path:
            try:
                p = Path(source_path)
                inferred_title = p.stem.strip()
                if inferred_title.lower().startswith("transcript for "):
                    inferred_title = inferred_title[len("Transcript for ") :].strip()
                transcript = p.read_text(encoding="utf-8", errors="ignore")
            except Exception:
                transcript = ""
        if "lex fridman" in inferred_title.lower() or "lex-fridman" in args.episode_id.lower():
            inferred_host = "Lex Fridman"

        podcast_key = args.podcast_key or args.episode_id
        summary_label = args.summary_label or ("Llama3-8B" if args.mode == "together" else "GPT-4o")
        existing = {}
        if args.podcasts_json.exists():
            existing = json.loads(args.podcasts_json.read_text(encoding="utf-8"))

        existing_entry = existing.get(podcast_key) if isinstance(existing.get(podcast_key), dict) else {}
        existing_summaries = (existing_entry.get("summaries") if isinstance(existing_entry, dict) else None) or {}
        if not isinstance(existing_summaries, dict):
            existing_summaries = {}
        existing_summaries[summary_label] = result.abstract

        existing[podcast_key] = {
            "title": args.title or inferred_title,
            "host": args.host or inferred_host,
            "date": args.date or "",
            "duration": args.duration or "",
            "tags": result.keywords,
            "summaries": existing_summaries,
            "outline": result.outline,
            "quotes": result.quotes,
            "q_and_a": result.q_and_a,
            "transcript": transcript,
        }
        args.podcasts_json.parent.mkdir(parents=True, exist_ok=True)
        args.podcasts_json.write_text(json.dumps(existing, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"Updated podcasts JSON: {args.podcasts_json} (key={podcast_key})")

    if not args.output_json and not args.podcasts_json:
        print("Abstract:\n", result.abstract, "\n")
        print("Keywords:", ", ".join(result.keywords))
        print("\nOutline:")
        for bullet in result.outline:
            print(f"- {bullet}")
        print("\nQuotes:")
        for q in result.quotes:
            print(f"- {q}")
        print("\nQ&A:")
        for qa in result.q_and_a:
            print(f"- {qa}")


if __name__ == "__main__":
    main()

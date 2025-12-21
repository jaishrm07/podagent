#!/usr/bin/env python3
"""
Minimal smoke test for calling the Together API.

Usage:
  TOGETHER_API_KEY=... python podagent/scripts/together_smoke.py
  TOGETHER_API_KEY=... python podagent/scripts/together_smoke.py --json
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from typing import Any, Dict


def _require_env(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise SystemExit(f"Missing required env var: {name}")
    return value


def main() -> None:
    parser = argparse.ArgumentParser(description="Together model smoke test.")
    parser.add_argument(
        "--model",
        type=str,
        default="meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo",
        help="Together model name.",
    )
    parser.add_argument("--message", type=str, default="Reply with exactly: pong", help="User prompt.")
    parser.add_argument(
        "--json",
        action="store_true",
        help="Ask for a JSON object response (prints the JSON returned by the model).",
    )
    args = parser.parse_args()

    _require_env("TOGETHER_API_KEY")

    try:
        from together import Together
    except Exception as exc:
        raise SystemExit(f"Missing dependency: together ({exc})") from exc

    client = Together(api_key=os.getenv("TOGETHER_API_KEY"))

    messages = [{"role": "user", "content": args.message}]
    if args.json:
        messages = [
            {"role": "system", "content": "Return ONLY valid JSON with keys: ok (boolean), message (string)."},
            {"role": "user", "content": args.message},
        ]

    request: Dict[str, Any] = {
        "model": args.model,
        "messages": messages,
        "temperature": 0.0,
        "max_tokens": 200,
    }

    try:
        if args.json:
            resp = client.chat.completions.create(**request, response_format={"type": "json_object"})
        else:
            resp = client.chat.completions.create(**request)
    except TypeError:
        resp = client.chat.completions.create(**request)
    except Exception as exc:
        raise SystemExit(f"Together request failed: {exc}") from exc

    content = (resp.choices[0].message.content or "").strip()
    if not content:
        raise SystemExit("Together returned empty content.")

    if args.json:
        try:
            data = json.loads(content)
        except json.JSONDecodeError:
            print(content)
            raise SystemExit("Model did not return valid JSON.")
        print(json.dumps(data, ensure_ascii=False, indent=2))
    else:
        print(content)


if __name__ == "__main__":
    main()


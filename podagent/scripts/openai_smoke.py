#!/usr/bin/env python3
"""
Minimal smoke test for calling the OpenAI API with the gpt-4o model.

Usage:
  OPENAI_API_KEY=... python podagent/scripts/openai_smoke.py
  OPENAI_API_KEY=... python podagent/scripts/openai_smoke.py --message "Say pong"
  OPENAI_API_KEY=... python podagent/scripts/openai_smoke.py --json
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
    parser = argparse.ArgumentParser(description="OpenAI gpt-4o smoke test.")
    parser.add_argument("--message", type=str, default="Reply with exactly: pong", help="User prompt.")
    parser.add_argument(
        "--json",
        action="store_true",
        help="Ask for a JSON object response (prints the JSON returned by the model).",
    )
    args = parser.parse_args()

    _require_env("OPENAI_API_KEY")

    try:
        from openai import OpenAI
    except Exception as exc:
        raise SystemExit(f"Missing dependency: openai ({exc})") from exc

    client = OpenAI()

    messages = [{"role": "user", "content": args.message}]
    if args.json:
        messages = [
            {
                "role": "system",
                "content": "Return ONLY valid JSON with keys: ok (boolean), message (string).",
            },
            {"role": "user", "content": args.message},
        ]

    request: Dict[str, Any] = {
        "model": "gpt-4o",
        "messages": messages,
        "temperature": 0.0,
        "max_tokens": 200,
    }

    try:
        # Newer OpenAI clients support enforcing JSON output this way.
        if args.json:
            resp = client.chat.completions.create(**request, response_format={"type": "json_object"})
        else:
            resp = client.chat.completions.create(**request)
    except TypeError:
        # Fallback for older clients that don't accept response_format.
        resp = client.chat.completions.create(**request)
    except Exception as exc:
        raise SystemExit(f"OpenAI request failed: {exc}") from exc

    content = (resp.choices[0].message.content or "").strip()
    if not content:
        raise SystemExit("OpenAI returned empty content.")

    if args.json:
        # Print pretty JSON if possible.
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


from typing import Any, Dict
import json
import os
import sys


class BaseSummarizer:
    def summarize(self, text: str, max_length: int = 256, min_length: int = 64) -> str:
        raise NotImplementedError


class TogetherSummarizer(BaseSummarizer):
    """
    Together API-based summarizer.
    Requires TOGETHER_API_KEY in the environment.
    """

    def __init__(self, model: str = "meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo"):
        try:
            from together import Together
        except Exception as exc:  # pragma: no cover - optional dependency
            raise ImportError(
                "together is required for TogetherSummarizer. Install with `pip install together`."
            ) from exc

        api_key = os.getenv("TOGETHER_API_KEY")
        if not api_key:
            raise RuntimeError("TOGETHER_API_KEY environment variable is not set.")

        self.model = model
        self.client = Together(api_key=api_key)

    def summarize(self, text: str, max_length: int = 220, min_length: int = 80) -> str:
        prompt = (
            "You are summarizing a podcast transcript snippet. "
            "Write a detailed summary in roughly three paragraphs, totaling about 500 words. "
            "Keep it faithful to the source, avoid speculation, and maintain coherence.\n\n"
            "Transcript:\n"
            f"{text}"
        )
        resp = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
            max_tokens=1200,
        )
        return (resp.choices[0].message.content or "").strip()

    def _parse_json_object(self, content: str) -> Dict[str, Any]:
        try:
            return json.loads(content)
        except json.JSONDecodeError:
            start = content.find("{")
            end = content.rfind("}")
            if start != -1 and end != -1 and end > start:
                return json.loads(content[start : end + 1])
            raise

    def summarize_structured(
        self,
        text: str,
        target_words: int = 500,
        max_tokens: int = 3000,
    ) -> Dict[str, Any]:
        if not text.strip():
            return {"abstract": "", "outline": [], "quotes": [], "q_and_a": [], "keywords": []}

        system = (
        "You are a rigorous podcast summarizer. You MUST stay grounded in the transcript. "
        "Do not invent facts, numbers, names, or claims. If something is not explicitly in the transcript, "
        "write 'unknown' or omit it.\n\n"

        "Return ONLY valid JSON with exactly these keys:\n"
        f"- abstract: string (~{target_words} words total; write the conclusion in a separate paragraph, separate paragraphs with \\n\\n)\n"
       "- outline: list of 5–8 short bullets (each <= 12 words)\n"
       "- quotes: list of 3–6 objects with keys {text, timestamp}. "
        "The quote text must be <= 25 words and must appear verbatim in the transcript. "
        "timestamp must match the transcript format; if no timestamps exist, use null.\n"
        "- q_and_a: list of 3–5 objects with keys {question, answer, evidence}. "
        "Questions should be answerable from the transcript. "
        "Answers must be concise (2–4 sentences). "
        "evidence is a list of 1–3 short supporting snippets from the transcript (<= 20 words each) "
        "and include timestamps if present.\n"
        "- keywords: list of 7–12 short topic/tag phrases (2–5 words each)\n\n"

        "Method (follow strictly):\n"
        "1) First, identify the main segments/themes and any claims that include numbers, comparisons, or strong conclusions.\n"
        "2) Then write the abstract and Q&A using only those grounded points.\n"
        "3) Prefer concrete details over vague phrasing. Avoid filler like 'thought-provoking'.\n"
        "4) If the transcript is incomplete, say so implicitly by limiting claims (do not speculate).\n\n"

        "Output formatting rules:\n"
        "- Output ONLY JSON. No markdown, no extra text.\n"
        "- Use straight quotes in JSON strings. Ensure valid escaping.\n"
        )
        print(f"system: {system}")
        request = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": f"Transcript:\n{text}"},
            ],
            "temperature": 0.0,
            "max_tokens": max_tokens,
        }

        try:
            resp = self.client.chat.completions.create(
                **request,
                response_format={"type": "json_object"},
            )


        except TypeError:
            resp = self.client.chat.completions.create(**request)

        content = (resp.choices[0].message.content or "").strip()
        print(f"response: {content}")
        if os.getenv("PODAGENT_DEBUG_TOGETHER_RESPONSE") == "1":
            print(f"[podagent] Together response:\n{content}", file=sys.stderr)
        if not content:
            raise RuntimeError("Together returned empty content for structured summary.")

        try:
            data = self._parse_json_object(content)
        except Exception as exc:
            if os.getenv("PODAGENT_DEBUG_TOGETHER") == "1":
                print(f"[podagent] Failed to parse Together JSON. Raw content:\n{content}", file=sys.stderr)
            raise RuntimeError(f"Failed to parse structured JSON from Together: {exc}") from exc

        return {
            "abstract": data.get("abstract", ""),
            "outline": data.get("outline", []) or [],
            "quotes": data.get("quotes", []) or [],
            "q_and_a": data.get("q_and_a", []) or [],
            "keywords": data.get("keywords", []) or [],
        }


class OpenAISummarizer(BaseSummarizer):
    """
    OpenAI API-based abstractive summarizer (default: GPT-5).
    Requires OPENAI_API_KEY in the environment.
    """

    def __init__(self, model: str = "gpt-5"):
        try:
            from openai import OpenAI
        except Exception as exc:  # pragma: no cover - optional dependency
            raise ImportError(
                "openai package is required for OpenAISummarizer. Install with `pip install openai`."
            ) from exc
        self.model = model
        self.client = OpenAI()

    def summarize(self, text: str, max_length: int = 220, min_length: int = 80) -> str:
        prompt = (
            "You are summarizing a podcast transcript snippet. "
            "Write a detailed summary in roughly three paragraphs, totaling about 500 words. "
            "Keep it faithful to the source, avoid speculation, and maintain coherence.\n\n"
            "Transcript:\n"
            f"{text}"
        )
        resp = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
            max_tokens=1200,
        )
        return (resp.choices[0].message.content or "").strip()

    def _parse_json_object(self, content: str) -> Dict[str, Any]:
        try:
            return json.loads(content)
        except json.JSONDecodeError:
            # Common failure mode: JSON wrapped in markdown fences or extra text.
            start = content.find("{")
            end = content.rfind("}")
            if start != -1 and end != -1 and end > start:
                return json.loads(content[start : end + 1])
            raise

    def summarize_structured(
        self,
        text: str,
        target_words: int = 1000,
        max_tokens: int = 10000,
    ) -> Dict[str, Any]:
        """
        Ask the model to return a structured JSON with abstract, outline, quotes, q_and_a, and keywords.
        """
        if not text.strip():
            return {"abstract": "", "outline": [], "quotes": [], "q_and_a": [], "keywords": []}

        system = (
        "You are a rigorous podcast summarizer. You MUST stay grounded in the transcript. "
        "Do not invent facts, numbers, names, or claims. If something is not explicitly in the transcript, "
        "write 'unknown' or omit it.\n\n"

        "Return ONLY valid JSON with exactly these keys:\n"
        "abstract: at total of 2000 words; atleast 4 paragraphs; before conclusion mention 4 bullets that summarize the main points, then write the conclusion in a separate paragraph, separate paragraphs with \\n\\n)\n"
        "- outline: list of 5–8 short bullets (each <= 12 words)\n"
        "- quotes: list of 3–6 objects with keys {text, timestamp}. "
        "The quote text must be <= 25 words and must appear verbatim in the transcript. "
        "timestamp must match the transcript format; if no timestamps exist, use null.\n"
        "- q_and_a: list of 3–5 objects with keys {question, answer, evidence}. "
        "Questions should be answerable from the transcript. "
        "Answers must be concise (2–4 sentences). "
        "evidence is a list of 1–3 short supporting snippets from the transcript (<= 20 words each) "
        "and include timestamps if present.\n"
        "- keywords: list of 7–12 short topic/tag phrases (2–5 words each)\n\n"

        "Method (follow strictly):\n"
        "1) First, identify the main segments/themes and any claims that include numbers, comparisons, or strong conclusions.\n"
        "2) Then write the abstract and Q&A using only those grounded points.\n"
        "3) Prefer concrete details over vague phrasing. Avoid filler like 'thought-provoking'.\n"
        "4) If the transcript is incomplete, say so implicitly by limiting claims (do not speculate).\n\n"

        "Output formatting rules:\n"
        "- Output ONLY JSON. No markdown, no extra text.\n"
        "- Use straight quotes in JSON strings. Ensure valid escaping.\n"
        )

        request = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": f"Transcript:\n{text}"},
            ],
            "temperature": 0.3,
            "max_tokens": max_tokens,
        }

        try:
            resp = self.client.chat.completions.create(
                **request,
                response_format={"type": "json_object"},
            )
        except TypeError:
            # Older OpenAI client versions may not support response_format in chat.completions.
            resp = self.client.chat.completions.create(**request)

        content = (resp.choices[0].message.content or "").strip()
        print(f"response: {content}")
        if not content:
            raise RuntimeError("OpenAI returned empty content for structured summary.")

        try:
            data = self._parse_json_object(content)
        except Exception as exc:
            if os.getenv("PODAGENT_DEBUG_OPENAI") == "1":
                print(f"[podagent] Failed to parse JSON. Raw content:\n{content}", file=sys.stderr)
            raise RuntimeError(f"Failed to parse structured JSON from OpenAI: {exc}") from exc

        return {
            "abstract": data.get("abstract", ""),
            "outline": data.get("outline", []) or [],
            "quotes": data.get("quotes", []) or [],
            "q_and_a": data.get("q_and_a", []) or [],
            "keywords": data.get("keywords", []) or [],
        }

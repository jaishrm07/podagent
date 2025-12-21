from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional, Sequence

from podagent import config
from podagent.retriever import EmbeddingRetriever, RetrievalResult
from podagent.utils import read_jsonl

from .summarizer import BaseSummarizer, OpenAISummarizer


def load_chunks_for_episode(episode_id: str, interim_dir: Optional[Path] = None) -> List[dict]:
    interim_dir = interim_dir or config.INTERIM_DIR
    path = interim_dir / f"{episode_id}.jsonl"
    return read_jsonl(path)


@dataclass
class SummaryOutput:
    episode_id: str
    abstract: str
    outline: List[str]
    quotes: List[str]
    q_and_a: List[str]
    keywords: List[str]
    evidence: List[RetrievalResult]


class PodcastSummarizer:
    """
    Minimal agentic summarizer: retrieves relevant chunks and composes a structured
    summary using a base summarizer.
    """

    def __init__(
        self,
        summarizer: Optional[BaseSummarizer] = None,
        retriever: Optional[EmbeddingRetriever] = None,
        max_context_chunks: int = 5,
    ):
        self.summarizer = summarizer or OpenAISummarizer()
        self.retriever = retriever
        self.max_context_chunks = max_context_chunks

    def _select_context(
        self,
        episode_chunks: Sequence[dict],
        episode_id: str,
        query: Optional[str],
    ) -> List[dict]:
        """
        If a retriever is available, limit results to the current episode_id;
        otherwise take evenly spaced chunks across the episode to avoid only
        summarizing the intro.
        """
        if self.retriever and query:
            results = self.retriever.search(query, k=self.max_context_chunks * 3)
            filtered = [r.chunk for r in results if r.chunk.get("episode_id") == episode_id]
            if filtered:
                return filtered[: self.max_context_chunks]

        # No retriever or no matches: pick evenly spaced chunks across the episode
        if not episode_chunks:
            return []
        k = max(1, self.max_context_chunks)
        if len(episode_chunks) <= k:
            return list(episode_chunks)

        idxs = []
        for i in range(k):
            # spread indices from start to end
            idx = round(i * (len(episode_chunks) - 1) / max(1, k - 1))
            idxs.append(int(idx))
        # ensure unique and sorted
        idxs = sorted(set(idxs))
        return [episode_chunks[i] for i in idxs]

    def summarize_episode(
        self,
        episode_id: str,
        interim_dir: Optional[Path] = None,
        query: Optional[str] = None,
        hierarchical: bool = False,
        group_size: int = 8,
        structured: bool = False,
        intermediate_min_words: int = 180,
        intermediate_max_words: int = 300,
        final_target_words: int = 700,
        final_max_tokens: int = 1800,
    ) -> SummaryOutput:
        chunks = load_chunks_for_episode(episode_id, interim_dir=interim_dir)
        if not chunks:
            raise FileNotFoundError(f"No chunks found for episode_id={episode_id}")

        if hierarchical:
            # Two-pass: summarize groups of chunks, then summarize the summaries.
            group_size = max(1, group_size)
            group_summaries: List[str] = []
            for i in range(0, len(chunks), group_size):
                group_text = "\n\n".join(c["text"] for c in chunks[i : i + group_size])
                summary = self.summarizer.summarize(
                    group_text,
                    max_length=intermediate_max_words,
                    min_length=intermediate_min_words,
                )
                if summary:
                    group_summaries.append(summary)
            combined_text = "\n\n".join(group_summaries)
            if structured and hasattr(self.summarizer, "summarize_structured"):
                out = self.summarizer.summarize_structured(
                    combined_text,
                    target_words=final_target_words,
                    max_tokens=final_max_tokens,
                )
                abstract = out.get("abstract", "")
                outline = out.get("outline", []) or []
                quotes = out.get("quotes", []) or []
                q_and_a = out.get("q_and_a", []) or []
                keywords = out.get("keywords", []) or []
            else:
                abstract = self.summarizer.summarize(
                    combined_text, max_length=final_target_words, min_length=final_target_words // 2
                )
                outline = group_summaries[:6]
                quotes = self._extract_quotes(chunks[: self.max_context_chunks])
                q_and_a = [f"Block {i+1}: {s}" for i, s in enumerate(group_summaries[:3])]
                keywords = self._extract_keywords("\n\n".join(group_summaries))
            evidence: List[RetrievalResult] = []
        else:
            context_chunks = self._select_context(chunks, episode_id=episode_id, query=query)
            context_text = "\n\n".join(c["text"] for c in context_chunks)

            # Generate pieces of the structured summary.
            if structured and hasattr(self.summarizer, "summarize_structured"):
                out = self.summarizer.summarize_structured(
                    context_text, target_words=final_target_words, max_tokens=final_max_tokens
                )
                abstract = out.get("abstract", "")
                outline = out.get("outline", []) or []
                quotes = out.get("quotes", []) or []
                q_and_a = out.get("q_and_a", []) or []
                keywords = out.get("keywords", []) or []
            else:
                abstract = self.summarizer.summarize(
                    context_text, max_length=final_target_words, min_length=final_target_words // 2
                )
                outline = self._generate_outline(context_chunks)
                quotes = self._extract_quotes(context_chunks)
                q_and_a = self._generate_q_and_a(context_chunks)
                keywords = self._extract_keywords(context_text)

            evidence: List[RetrievalResult] = []
            if self.retriever and query:
                evidence = [
                    r
                    for r in self.retriever.search(query, k=self.max_context_chunks * 3)
                    if r.chunk.get("episode_id") == episode_id
                ][: self.max_context_chunks]

        return SummaryOutput(
            episode_id=episode_id,
            abstract=abstract,
            outline=outline,
            quotes=quotes,
            q_and_a=q_and_a,
            keywords=keywords,
            evidence=evidence,
        )

    def _generate_outline(self, context_chunks: Sequence[dict], max_items: int = 6) -> List[str]:
        outline: List[str] = []
        for chunk in context_chunks[:max_items]:
            sentences = chunk["text"].split(". ")
            if sentences:
                outline.append(sentences[0].strip())
        return outline

    def _extract_quotes(self, context_chunks: Sequence[dict], max_quotes: int = 5) -> List[str]:
        quotes: List[str] = []
        for chunk in context_chunks:
            text = chunk["text"]
            sentences = text.split(". ")
            for s in sentences:
                if len(s.split()) > 6 and len(quotes) < max_quotes:
                    quotes.append(s.strip())
            if len(quotes) >= max_quotes:
                break
        return quotes

    def _generate_q_and_a(self, context_chunks: Sequence[dict], max_items: int = 3) -> List[str]:
        qas: List[str] = []
        for i, chunk in enumerate(context_chunks[:max_items]):
            prompt = f"Q{i+1}: What is a key idea?\nA: {chunk['text'][:200]}..."
            qas.append(prompt)
        return qas

    def _extract_keywords(self, text: str, max_keywords: int = 12) -> List[str]:
        """
        Very simple keyword extractor based on word frequency, filtering short/stop words.
        """
        import re
        from collections import Counter

        tokens = re.findall(r"[A-Za-z][A-Za-z0-9'-]+", text.lower())
        stop = {
            "the",
            "and",
            "for",
            "with",
            "that",
            "this",
            "from",
            "they",
            "have",
            "you",
            "but",
            "are",
            "was",
            "not",
            "all",
            "can",
            "had",
            "her",
            "his",
            "she",
            "him",
            "its",
            "our",
            "your",
            "their",
            "who",
            "what",
            "when",
            "where",
            "why",
            "how",
            "into",
            "about",
            "over",
            "after",
            "before",
            "because",
            "then",
            "than",
            "also",
            "there",
            "them",
            "been",
            "will",
            "would",
            "could",
            "should",
            "may",
            "might",
            "one",
            "two",
            "three",
        }
        filtered = [t for t in tokens if len(t) > 3 and t not in stop]
        counts = Counter(filtered)
        common = [w for w, _ in counts.most_common(max_keywords)]
        return common

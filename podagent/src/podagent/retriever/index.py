from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional, Sequence

import numpy as np

from podagent import config
from podagent.utils import read_jsonl


try:
    import faiss  # type: ignore
except Exception:  # pragma: no cover - optional dependency
    faiss = None

try:
    from sentence_transformers import SentenceTransformer
except Exception:  # pragma: no cover - optional dependency
    SentenceTransformer = None


@dataclass
class RetrievalResult:
    chunk: dict
    score: float


class EmbeddingRetriever:
    """
    Simple FAISS-backed retriever over transcript chunks.
    """

    def __init__(
        self,
        chunks: Sequence[dict],
        model_name: str = "sentence-transformers/all-MiniLM-L6-v2",
        index_path: Optional[Path] = None,
    ):
        if SentenceTransformer is None:
            raise ImportError(
                "sentence-transformers is not installed. "
                "Install from requirements.txt before using the retriever."
            )
        if faiss is None:
            raise ImportError(
                "faiss is not installed. Install faiss-cpu from requirements.txt."
            )

        self.model_name = model_name
        self.model = SentenceTransformer(model_name)
        self.chunks = list(chunks)
        self.index_path = index_path

        # Build embeddings
        texts = [c["text"] for c in self.chunks]
        embeddings = self.model.encode(texts, convert_to_numpy=True, normalize_embeddings=True)
        self.index = self._build_index(embeddings)

        # Optionally persist index
        if self.index_path:
            self.save(self.index_path)

    def _build_index(self, embeddings: np.ndarray):
        dim = embeddings.shape[1]
        index = faiss.IndexFlatIP(dim)
        index.add(embeddings.astype(np.float32))
        return index

    def search(self, query: str, k: int = 5) -> List[RetrievalResult]:
        query_vec = self.model.encode([query], convert_to_numpy=True, normalize_embeddings=True)
        scores, idxs = self.index.search(query_vec.astype(np.float32), k)
        results: List[RetrievalResult] = []
        for score, idx in zip(scores[0], idxs[0]):
            if idx == -1:
                continue
            results.append(RetrievalResult(chunk=self.chunks[idx], score=float(score)))
        return results

    def save(self, path: Path) -> None:
        """
        Persist FAISS index and chunk metadata next to it.
        """
        if faiss is None:
            raise ImportError("faiss is required to save or load indices.")
        path.parent.mkdir(parents=True, exist_ok=True)
        faiss.write_index(self.index, str(path))
        meta_path = path.with_suffix(".chunks.jsonl")
        from podagent.utils import write_jsonl

        write_jsonl(meta_path, self.chunks)

    @classmethod
    def load(
        cls,
        index_path: Path,
        model_name: str = "sentence-transformers/all-MiniLM-L6-v2",
    ) -> "EmbeddingRetriever":
        if SentenceTransformer is None:
            raise ImportError("sentence-transformers is not installed.")
        if faiss is None:
            raise ImportError("faiss is not installed.")
        model = SentenceTransformer(model_name)
        index = faiss.read_index(str(index_path))
        meta_path = index_path.with_suffix(".chunks.jsonl")
        chunks = read_jsonl(meta_path)
        retriever = cls.__new__(cls)
        retriever.model_name = model_name
        retriever.model = model
        retriever.index_path = index_path
        retriever.index = index
        retriever.chunks = chunks
        return retriever


def build_index_from_chunks(
    interim_dir: Optional[Path] = None,
    model_name: str = "sentence-transformers/all-MiniLM-L6-v2",
) -> EmbeddingRetriever:
    """
    Convenience helper: load all chunks from JSONL files under interim_dir and
    return an EmbeddingRetriever instance.
    """
    interim_dir = interim_dir or config.INTERIM_DIR
    chunk_files = [p for p in interim_dir.glob("*.jsonl") if p.name != "manifest.jsonl"]
    chunks: List[dict] = []
    for cf in chunk_files:
        chunks.extend(read_jsonl(cf))

    return EmbeddingRetriever(chunks=chunks, model_name=model_name)

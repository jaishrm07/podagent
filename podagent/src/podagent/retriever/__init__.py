"""
Embedding-based retrieval utilities.
"""

from .index import EmbeddingRetriever, RetrievalResult, build_index_from_chunks

__all__ = ["EmbeddingRetriever", "RetrievalResult", "build_index_from_chunks"]

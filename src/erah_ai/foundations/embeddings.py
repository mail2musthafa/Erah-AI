"""Embedding math, vector similarity, and in-memory semantic search engine."""

from __future__ import annotations
import numpy as np
from typing import Any, Dict, List, Tuple


def cosine_similarity(v1: np.ndarray, v2: np.ndarray) -> float:
    """Compute cosine similarity between two vectors."""
    norm1 = np.linalg.norm(v1)
    norm2 = np.linalg.norm(v2)
    if norm1 == 0.0 or norm2 == 0.0:
        return 0.0
    return float(np.dot(v1, v2) / (norm1 * norm2))


def batch_cosine_similarity(query_vector: np.ndarray, matrix: np.ndarray) -> np.ndarray:
    """Compute cosine similarities between a query vector and a 2D matrix of embeddings."""
    q_norm = np.linalg.norm(query_vector)
    if q_norm == 0:
        return np.zeros(matrix.shape[0])
    q_unit = query_vector / q_norm

    mat_norms = np.linalg.norm(matrix, axis=1, keepdims=True)
    mat_norms[mat_norms == 0] = 1e-10
    mat_unit = matrix / mat_norms

    return np.dot(mat_unit, q_unit)


def euclidean_distance(v1: np.ndarray, v2: np.ndarray) -> float:
    """Compute Euclidean distance between two vectors."""
    return float(np.linalg.norm(v1 - v2))


def dot_product(v1: np.ndarray, v2: np.ndarray) -> float:
    """Compute standard dot product between two vectors."""
    return float(np.dot(v1, v2))


class SemanticSearchEngine:
    """A lightweight in-memory semantic search engine without external vector DB dependencies.

    Uses TF-IDF + Character/Word N-gram Dense vectors or dense embeddings to demonstrate
    similarity search, Top-K ranking, and retrieval for Phase 01.
    """

    def __init__(self, embedding_dim: int = 64):
        self.embedding_dim = embedding_dim
        self.documents: list[dict[str, Any]] = []
        self.embedding_matrix: np.ndarray | None = None
        self.vocab: dict[str, int] = {}

    def _generate_synthetic_dense_vector(self, text: str) -> np.ndarray:
        """Create a deterministic dense embedding representation for text based on char-grams & hash projection."""
        vec = np.zeros(self.embedding_dim, dtype=np.float32)
        words = text.lower().split()
        for i, word in enumerate(words):
            # Deterministic pseudo-random seed per word
            seed = sum((idx + 1) * ord(c) for idx, c in enumerate(word))
            rng = np.random.RandomState(seed % (2**31 - 1))
            word_vector = rng.randn(self.embedding_dim).astype(np.float32)
            # Position decay
            weight = 1.0 / (1.0 + 0.1 * i)
            vec += weight * word_vector

        # L2 Normalize
        norm = np.linalg.norm(vec)
        if norm > 0:
            vec /= norm
        return vec

    def add_document(self, doc_id: str, text: str, metadata: dict[str, Any] | None = None) -> None:
        """Add a document and compute its embedding vector."""
        vector = self._generate_synthetic_dense_vector(text)
        doc = {
            "id": doc_id,
            "text": text,
            "metadata": metadata or {},
            "vector": vector,
        }
        self.documents.append(doc)
        self._rebuild_matrix()

    def add_documents(self, docs: list[tuple[str, str, dict[str, Any]]]) -> None:
        """Batch add documents (id, text, metadata)."""
        for doc_id, text, meta in docs:
            vector = self._generate_synthetic_dense_vector(text)
            self.documents.append({
                "id": doc_id,
                "text": text,
                "metadata": meta,
                "vector": vector,
            })
        self._rebuild_matrix()

    def _rebuild_matrix(self) -> None:
        if self.documents:
            self.embedding_matrix = np.stack([d["vector"] for d in self.documents])
        else:
            self.embedding_matrix = None

    def search(self, query: str, top_k: int = 3) -> list[dict[str, Any]]:
        """Search the corpus and return Top-K matches sorted by cosine similarity."""
        if not self.documents or self.embedding_matrix is None:
            return []

        query_vec = self._generate_synthetic_dense_vector(query)
        scores = batch_cosine_similarity(query_vec, self.embedding_matrix)

        top_indices = np.argsort(scores)[::-1][:top_k]
        results = []
        for idx in top_indices:
            results.append({
                "id": self.documents[idx]["id"],
                "text": self.documents[idx]["text"],
                "score": float(scores[idx]),
                "metadata": self.documents[idx]["metadata"],
            })
        return results

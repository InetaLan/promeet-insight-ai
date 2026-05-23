from __future__ import annotations

from typing import Iterable
import numpy as np


def _cosine(a, b) -> float:
    denom = (np.linalg.norm(a) * np.linalg.norm(b))
    if denom == 0:
        return 0.0
    return float(np.dot(a, b) / denom)


class SimilarityEngine:
    def __init__(self):
        self.mode = "tfidf"
        self.model = None
        try:
            from sentence_transformers import SentenceTransformer
            self.model = SentenceTransformer("sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2")
            self.mode = "sentence-transformer"
        except Exception:
            self.model = None

    def max_similarity(self, text: str, candidates: Iterable[str]) -> float:
        candidates = [c for c in candidates if c]
        if not text or not candidates:
            return 0.0

        if self.model is not None:
            vectors = self.model.encode([text] + candidates)
            base = vectors[0]
            return max(_cosine(base, v) for v in vectors[1:])

        from sklearn.feature_extraction.text import TfidfVectorizer
        matrix = TfidfVectorizer().fit_transform([text] + candidates)
        base = matrix[0].toarray()[0]
        return max(_cosine(base, matrix[i].toarray()[0]) for i in range(1, matrix.shape[0]))

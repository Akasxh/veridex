"""Extractive summarization using TF-IDF based TextRank."""

from __future__ import annotations

import re
from dataclasses import dataclass

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


def _split_sentences(text: str) -> list[str]:
    """Split text into sentences using regex."""
    raw = re.split(r"(?<=[.!?])\s+", text)
    sentences = [s.strip() for s in raw if len(s.strip()) > 15]
    return sentences


@dataclass
class SummaryResult:
    """Result of summarization."""

    summary: str
    key_sentences: list[str]
    sentence_count: int
    compression_ratio: float


@dataclass
class Summarizer:
    """TF-IDF based extractive summarizer using TextRank-style scoring."""

    max_sentences: int = 7
    min_sentence_length: int = 20

    def summarize(self, text: str, max_sentences: int | None = None) -> SummaryResult:
        """Extract the most important sentences from text."""
        n = max_sentences or self.max_sentences
        sentences = _split_sentences(text)

        if len(sentences) <= n:
            return SummaryResult(
                summary=text,
                key_sentences=sentences,
                sentence_count=len(sentences),
                compression_ratio=1.0,
            )

        # Build TF-IDF matrix
        try:
            vectorizer = TfidfVectorizer(stop_words="english", max_features=5000)
            tfidf_matrix = vectorizer.fit_transform(sentences)
        except ValueError:
            # Not enough content to vectorize
            return SummaryResult(
                summary=text[:2000],
                key_sentences=sentences[:n],
                sentence_count=len(sentences[:n]),
                compression_ratio=min(1.0, 2000 / max(len(text), 1)),
            )

        # Compute similarity matrix (TextRank-style)
        sim_matrix = cosine_similarity(tfidf_matrix)

        # Score each sentence: sum of similarities to all others
        scores = sim_matrix.sum(axis=1)

        # Also boost sentences that appear early (position bias)
        position_weight = np.array([1.0 / (1.0 + 0.1 * i) for i in range(len(sentences))])
        scores = scores * position_weight

        # Get top-N sentence indices, maintaining original order
        top_indices = sorted(
            np.argsort(scores)[-n:][::-1].tolist()
        )

        key_sentences = [sentences[i] for i in top_indices]
        summary = " ".join(key_sentences)

        return SummaryResult(
            summary=summary,
            key_sentences=key_sentences,
            sentence_count=len(key_sentences),
            compression_ratio=len(summary) / max(len(text), 1),
        )

    def multi_document_summarize(
        self, texts: list[str], max_sentences: int | None = None
    ) -> SummaryResult:
        """Summarize across multiple documents."""
        combined = "\n\n".join(texts)
        return self.summarize(combined, max_sentences=max_sentences)

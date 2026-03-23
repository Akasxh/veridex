"""Tests for summarizer module."""

from __future__ import annotations

import pytest

from src.summarizer import Summarizer, SummaryResult, _split_sentences


class TestSplitSentences:
    def test_basic_split(self) -> None:
        text = "First sentence here is long enough. Second sentence is also long enough. Third one too is long enough."
        sentences = _split_sentences(text)
        assert len(sentences) == 3

    def test_filters_short_sentences(self) -> None:
        text = "Ok. This is a properly long sentence for testing. No."
        sentences = _split_sentences(text)
        # Only the long sentence passes the >15 char filter
        assert len(sentences) == 1
        assert "properly long" in sentences[0]


class TestSummarizer:
    def test_short_text_returns_all(self) -> None:
        """When text has fewer sentences than max, return everything."""
        summarizer = Summarizer(max_sentences=5)
        text = "This is a test sentence that is long enough. Another sentence that also passes the length check."
        result = summarizer.summarize(text, max_sentences=5)

        assert isinstance(result, SummaryResult)
        assert result.compression_ratio == 1.0
        assert result.summary == text

    def test_long_text_tfidf_path(self) -> None:
        """When text has more sentences than max, TF-IDF path runs."""
        sentences = [
            f"Sentence number {i} discusses the important topic of machine learning in healthcare applications."
            for i in range(20)
        ]
        text = " ".join(sentences)
        summarizer = Summarizer()
        result = summarizer.summarize(text, max_sentences=3)

        assert isinstance(result, SummaryResult)
        assert result.sentence_count == 3
        assert len(result.key_sentences) == 3
        assert result.compression_ratio < 1.0

    def test_multi_document_summarize(self) -> None:
        doc1 = "Artificial intelligence is transforming healthcare delivery worldwide. " * 5
        doc2 = "Machine learning models are improving diagnostic accuracy significantly. " * 5
        doc3 = "Deep learning neural networks achieve remarkable results in medical imaging tasks. " * 5

        summarizer = Summarizer()
        result = summarizer.multi_document_summarize([doc1, doc2, doc3], max_sentences=3)

        assert isinstance(result, SummaryResult)
        assert len(result.summary) > 0
        assert result.sentence_count <= 3

    def test_empty_input(self) -> None:
        summarizer = Summarizer()
        result = summarizer.summarize("", max_sentences=3)
        assert isinstance(result, SummaryResult)
        # Empty text -> 0 sentences after split -> returns as-is
        assert result.compression_ratio == 1.0

    @pytest.mark.parametrize("max_sent", [1, 3, 5])
    def test_respects_max_sentences(self, max_sent: int) -> None:
        sentences = [
            f"This is unique sentence {i} about a very different and interesting topic number {i}."
            for i in range(15)
        ]
        text = " ".join(sentences)
        summarizer = Summarizer()
        result = summarizer.summarize(text, max_sentences=max_sent)
        assert result.sentence_count <= max_sent

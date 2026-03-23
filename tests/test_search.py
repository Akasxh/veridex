"""Tests for search module."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from src.search import SearchEngine, SearchResult


class TestSearchResult:
    def test_creation_with_all_fields(self) -> None:
        sr = SearchResult(
            title="Test Title",
            url="https://example.com",
            snippet="A snippet",
            source="example.com",
        )
        assert sr.title == "Test Title"
        assert sr.url == "https://example.com"
        assert sr.snippet == "A snippet"
        assert sr.source == "example.com"

    def test_default_source_is_empty(self) -> None:
        sr = SearchResult(title="T", url="https://x.com", snippet="S")
        assert sr.source == ""


class TestSearchEngine:
    def test_default_rate_limit_delay(self) -> None:
        engine = SearchEngine()
        assert engine.rate_limit_delay == 1.5
        assert engine.max_results == 10

    def test_custom_rate_limit_delay(self) -> None:
        engine = SearchEngine(rate_limit_delay=3.0, max_results=5)
        assert engine.rate_limit_delay == 3.0
        assert engine.max_results == 5

    @patch("src.search.DDGS")
    def test_search_returns_results(self, mock_ddgs_cls: MagicMock) -> None:
        mock_ctx = MagicMock()
        mock_ctx.text.return_value = [
            {"title": "Result 1", "href": "https://example.com/1", "body": "Body 1"},
            {"title": "Result 2", "href": "https://example.com/2", "body": "Body 2"},
        ]
        mock_ddgs_cls.return_value.__enter__ = MagicMock(return_value=mock_ctx)
        mock_ddgs_cls.return_value.__exit__ = MagicMock(return_value=False)

        engine = SearchEngine(rate_limit_delay=0.0)
        engine._last_request_time = 0.0
        results = engine.search("test query", max_results=2)

        assert len(results) == 2
        assert results[0].title == "Result 1"
        assert results[0].url == "https://example.com/1"
        assert results[1].source == "example.com"

    @patch("src.search.DDGS")
    def test_search_handles_exception(self, mock_ddgs_cls: MagicMock) -> None:
        mock_ddgs_cls.return_value.__enter__ = MagicMock(
            side_effect=RuntimeError("Network error")
        )
        mock_ddgs_cls.return_value.__exit__ = MagicMock(return_value=False)

        engine = SearchEngine(rate_limit_delay=0.0)
        engine._last_request_time = 0.0
        results = engine.search("fail query")
        assert results == []

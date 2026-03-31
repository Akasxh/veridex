"""Tests for search module."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from src.search import SearchEngine, SearchResult, TavilySearchEngine, get_search_engine


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


class TestTavilySearchEngine:
    @patch("tavily.TavilyClient")
    def test_search_returns_results(self, mock_client_cls: MagicMock) -> None:
        mock_client = MagicMock()
        mock_client.search.return_value = {
            "results": [
                {"title": "Tavily 1", "url": "https://example.com/t1", "content": "Content 1"},
                {"title": "Tavily 2", "url": "https://example.com/t2", "content": "Content 2"},
            ]
        }
        mock_client_cls.return_value = mock_client

        engine = TavilySearchEngine(api_key="tvly-test")
        results = engine.search("test query", max_results=2)

        assert len(results) == 2
        assert results[0].title == "Tavily 1"
        assert results[0].url == "https://example.com/t1"
        assert results[0].snippet == "Content 1"
        assert results[1].source == "example.com"
        mock_client.search.assert_called_once_with("test query", max_results=2, search_depth="basic")

    @patch("tavily.TavilyClient")
    def test_search_news_uses_news_topic(self, mock_client_cls: MagicMock) -> None:
        mock_client = MagicMock()
        mock_client.search.return_value = {
            "results": [
                {"title": "News 1", "url": "https://news.com/1", "content": "Breaking news"},
            ]
        }
        mock_client_cls.return_value = mock_client

        engine = TavilySearchEngine(api_key="tvly-test")
        results = engine.search_news("latest news", max_results=1)

        assert len(results) == 1
        assert results[0].title == "News 1"
        mock_client.search.assert_called_once_with("latest news", max_results=1, topic="news")

    @patch("tavily.TavilyClient")
    def test_search_handles_exception(self, mock_client_cls: MagicMock) -> None:
        mock_client = MagicMock()
        mock_client.search.side_effect = RuntimeError("API error")
        mock_client_cls.return_value = mock_client

        engine = TavilySearchEngine(api_key="tvly-test")
        results = engine.search("fail query")
        assert results == []

    @patch("tavily.TavilyClient")
    def test_search_news_handles_exception(self, mock_client_cls: MagicMock) -> None:
        mock_client = MagicMock()
        mock_client.search.side_effect = RuntimeError("API error")
        mock_client_cls.return_value = mock_client

        engine = TavilySearchEngine(api_key="tvly-test")
        results = engine.search_news("fail query")
        assert results == []


class TestGetSearchEngine:
    @patch.dict("os.environ", {"TAVILY_API_KEY": "tvly-test"}, clear=False)
    @patch("tavily.TavilyClient")
    def test_auto_returns_tavily_when_key_present(self, mock_client_cls: MagicMock) -> None:
        engine = get_search_engine()
        assert isinstance(engine, TavilySearchEngine)

    @patch.dict("os.environ", {}, clear=False)
    def test_auto_returns_ddg_when_no_key(self) -> None:
        import os
        os.environ.pop("TAVILY_API_KEY", None)
        os.environ.pop("VERIDEX_SEARCH_PROVIDER", None)
        engine = get_search_engine()
        assert isinstance(engine, SearchEngine)

    @patch.dict("os.environ", {"VERIDEX_SEARCH_PROVIDER": "ddg", "TAVILY_API_KEY": "tvly-test"}, clear=False)
    def test_ddg_provider_ignores_tavily_key(self) -> None:
        engine = get_search_engine()
        assert isinstance(engine, SearchEngine)

    @patch.dict("os.environ", {"VERIDEX_SEARCH_PROVIDER": "tavily", "TAVILY_API_KEY": "tvly-test"}, clear=False)
    @patch("tavily.TavilyClient")
    def test_tavily_provider_explicit(self, mock_client_cls: MagicMock) -> None:
        engine = get_search_engine()
        assert isinstance(engine, TavilySearchEngine)

    @patch.dict("os.environ", {"VERIDEX_SEARCH_PROVIDER": "tavily"}, clear=False)
    def test_tavily_provider_without_key_falls_back(self) -> None:
        import os
        os.environ.pop("TAVILY_API_KEY", None)
        engine = get_search_engine()
        assert isinstance(engine, SearchEngine)

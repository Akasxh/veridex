"""Search engine wrappers with rate limiting."""

from __future__ import annotations

import logging
import os
import time
from dataclasses import dataclass, field
from urllib.parse import urlparse

from ddgs import DDGS

logger = logging.getLogger(__name__)


@dataclass
class SearchResult:
    """A single search result."""

    title: str
    url: str
    snippet: str
    source: str = ""


@dataclass
class SearchEngine:
    """DuckDuckGo search with rate limiting and retry logic."""

    max_results: int = 10
    rate_limit_delay: float = 1.5
    _last_request_time: float = field(default=0.0, init=False, repr=False)

    def _wait_for_rate_limit(self) -> None:
        elapsed = time.monotonic() - self._last_request_time
        if elapsed < self.rate_limit_delay:
            time.sleep(self.rate_limit_delay - elapsed)
        self._last_request_time = time.monotonic()

    def search(self, query: str, max_results: int | None = None) -> list[SearchResult]:
        """Search DuckDuckGo and return structured results."""
        n = max_results or self.max_results
        self._wait_for_rate_limit()

        results: list[SearchResult] = []
        try:
            with DDGS() as ddgs:
                raw = ddgs.text(query, max_results=n)
                for item in raw:
                    results.append(
                        SearchResult(
                            title=item.get("title", ""),
                            url=item.get("href", ""),
                            snippet=item.get("body", ""),
                            source=urlparse(item.get("href", "")).netloc if item.get("href") else "",
                        )
                    )
        except Exception as e:
            logger.error("Error searching for '%s': %s", query, e)

        return results

    def search_news(self, query: str, max_results: int | None = None) -> list[SearchResult]:
        """Search DuckDuckGo news."""
        n = max_results or self.max_results
        self._wait_for_rate_limit()

        results: list[SearchResult] = []
        try:
            with DDGS() as ddgs:
                raw = ddgs.news(query, max_results=n)
                for item in raw:
                    results.append(
                        SearchResult(
                            title=item.get("title", ""),
                            url=item.get("url", ""),
                            snippet=item.get("body", ""),
                            source=item.get("source", ""),
                        )
                    )
        except Exception as e:
            logger.error("Error searching news for '%s': %s", query, e)

        return results


@dataclass
class TavilySearchEngine:
    """Tavily search engine with the same interface as SearchEngine."""

    max_results: int = 10
    api_key: str = field(default="", repr=False)

    def __post_init__(self) -> None:
        from tavily import TavilyClient as _TavilyClient

        key = self.api_key or os.environ.get("TAVILY_API_KEY", "")
        self._client = _TavilyClient(api_key=key)

    def search(self, query: str, max_results: int | None = None) -> list[SearchResult]:
        """Search via Tavily and return structured results."""
        n = max_results or self.max_results
        results: list[SearchResult] = []
        try:
            response = self._client.search(query, max_results=n, search_depth="basic")
            for item in response.get("results", []):
                results.append(
                    SearchResult(
                        title=item.get("title", ""),
                        url=item.get("url", ""),
                        snippet=item.get("content", ""),
                        source=urlparse(item.get("url", "")).netloc if item.get("url") else "",
                    )
                )
        except Exception as e:
            logger.error("Tavily search error for '%s': %s", query, e)
        return results

    def search_news(self, query: str, max_results: int | None = None) -> list[SearchResult]:
        """Search Tavily news and return structured results."""
        n = max_results or self.max_results
        results: list[SearchResult] = []
        try:
            response = self._client.search(query, max_results=n, topic="news")
            for item in response.get("results", []):
                results.append(
                    SearchResult(
                        title=item.get("title", ""),
                        url=item.get("url", ""),
                        snippet=item.get("content", ""),
                        source=urlparse(item.get("url", "")).netloc if item.get("url") else "",
                    )
                )
        except Exception as e:
            logger.error("Tavily news search error for '%s': %s", query, e)
        return results


def get_search_engine() -> SearchEngine | TavilySearchEngine:
    """Factory that returns the appropriate search engine based on env config.

    Uses VERIDEX_SEARCH_PROVIDER (auto|ddg|tavily) and TAVILY_API_KEY to decide.
    Default provider is "auto", which picks Tavily when TAVILY_API_KEY is set.
    """
    provider = os.environ.get("VERIDEX_SEARCH_PROVIDER", "auto").lower()
    tavily_key = os.environ.get("TAVILY_API_KEY", "")

    if provider == "tavily":
        if not tavily_key:
            logger.warning("VERIDEX_SEARCH_PROVIDER=tavily but TAVILY_API_KEY is not set, "
                           "falling back to DuckDuckGo.")
            return SearchEngine()
        return TavilySearchEngine(api_key=tavily_key)

    if provider == "ddg":
        return SearchEngine()

    # auto: prefer Tavily when key is available
    if tavily_key:
        return TavilySearchEngine(api_key=tavily_key)

    return SearchEngine()

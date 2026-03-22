"""DuckDuckGo search wrapper with rate limiting."""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import TYPE_CHECKING
from urllib.parse import urlparse

from ddgs import DDGS

if TYPE_CHECKING:
    pass


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
            print(f"[search] Error searching for '{query}': {e}")

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
            print(f"[search] Error searching news for '{query}': {e}")

        return results

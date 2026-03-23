"""Web scraping with robots.txt awareness and rate limiting."""

from __future__ import annotations

import logging
import time
from dataclasses import dataclass, field
from typing import Any
from urllib.parse import urlparse
from urllib.robotparser import RobotFileParser

import requests
from bs4 import BeautifulSoup, Tag

logger = logging.getLogger(__name__)

_HEADERS = {
    "User-Agent": (
        "Veridex/1.0 (Educational Research Agent; "
        "+https://github.com/akash/veridex) Python/requests"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
}

_REMOVE_TAGS = {"script", "style", "nav", "footer", "header", "aside", "form", "noscript", "svg"}


@dataclass
class ScrapedPage:
    """Parsed web page content."""

    url: str
    title: str
    text: str
    meta_description: str
    headings: list[str]
    links: list[str]
    word_count: int
    success: bool
    error: str = ""


@dataclass
class WebScraper:
    """Respectful web scraper with robots.txt checking."""

    timeout: int = 15
    rate_limit_delay: float = 2.0
    max_content_length: int = 5_000_000  # 5MB
    _robots_cache: dict[str, RobotFileParser] = field(default_factory=dict, init=False, repr=False)
    _last_request: dict[str, float] = field(default_factory=dict, init=False, repr=False)

    def _get_robots_parser(self, url: str) -> RobotFileParser:
        parsed = urlparse(url)
        base = f"{parsed.scheme}://{parsed.netloc}"
        if base not in self._robots_cache:
            rp = RobotFileParser()
            rp.set_url(f"{base}/robots.txt")
            try:
                rp.read()
            except (OSError, UnicodeDecodeError) as e:
                logger.debug("Could not read robots.txt for %s: %s", base, e)
            self._robots_cache[base] = rp
        return self._robots_cache[base]

    def _can_fetch(self, url: str) -> bool:
        rp = self._get_robots_parser(url)
        try:
            return rp.can_fetch(_HEADERS["User-Agent"], url)
        except (AttributeError, KeyError, TypeError) as e:
            logger.debug("robots.txt check failed for %s: %s", url, e)
            return True

    def _rate_limit(self, url: str) -> None:
        domain = urlparse(url).netloc
        last = self._last_request.get(domain, 0.0)
        elapsed = time.monotonic() - last
        if elapsed < self.rate_limit_delay:
            time.sleep(self.rate_limit_delay - elapsed)
        self._last_request[domain] = time.monotonic()

    def _extract_text(self, soup: BeautifulSoup) -> str:
        for tag_name in _REMOVE_TAGS:
            for tag in soup.find_all(tag_name):
                tag.decompose()

        # Try main content areas first
        main = (
            soup.find("main")
            or soup.find("article")
            or soup.find(attrs={"role": "main"})
            or soup.find("div", class_=lambda c: c and "content" in str(c).lower())
        )
        target: Any = main if main else soup.body if soup.body else soup

        paragraphs: list[str] = []
        for el in target.find_all(["p", "li", "h1", "h2", "h3", "h4", "h5", "h6", "td", "th", "blockquote"]):
            text = el.get_text(separator=" ", strip=True)
            if len(text) > 20:
                paragraphs.append(text)

        if not paragraphs:
            # Fallback: get all text
            text = target.get_text(separator="\n", strip=True)
            paragraphs = [line.strip() for line in text.split("\n") if len(line.strip()) > 20]

        return "\n\n".join(paragraphs)

    def _extract_headings(self, soup: BeautifulSoup) -> list[str]:
        headings: list[str] = []
        for tag in soup.find_all(["h1", "h2", "h3"]):
            text = tag.get_text(strip=True)
            if text:
                headings.append(text)
        return headings[:20]

    def _extract_links(self, soup: BeautifulSoup, base_url: str) -> list[str]:
        links: list[str] = []
        for a in soup.find_all("a", href=True):
            if not isinstance(a, Tag):
                continue
            href = str(a.get("href", ""))
            if href.startswith("http"):
                links.append(href)
        return links[:50]

    def scrape(self, url: str) -> ScrapedPage:
        """Scrape a URL and return structured content."""
        if not self._can_fetch(url):
            return ScrapedPage(
                url=url, title="", text="", meta_description="",
                headings=[], links=[], word_count=0, success=False,
                error="Blocked by robots.txt",
            )

        self._rate_limit(url)

        try:
            resp = requests.get(
                url, headers=_HEADERS, timeout=self.timeout,
                allow_redirects=True, stream=True,
            )
            # Check content length before reading
            cl = resp.headers.get("content-length")
            if cl and int(cl) > self.max_content_length:
                return ScrapedPage(
                    url=url, title="", text="", meta_description="",
                    headings=[], links=[], word_count=0, success=False,
                    error="Content too large",
                )

            resp.raise_for_status()
            content_type = resp.headers.get("content-type", "")
            if "text/html" not in content_type and "application/xhtml" not in content_type:
                return ScrapedPage(
                    url=url, title="", text="", meta_description="",
                    headings=[], links=[], word_count=0, success=False,
                    error=f"Non-HTML content: {content_type}",
                )

            soup = BeautifulSoup(resp.text, "lxml")
            title_tag = soup.find("title")
            title = title_tag.get_text(strip=True) if title_tag else ""

            meta_desc = ""
            meta_tag = soup.find("meta", attrs={"name": "description"})
            if meta_tag and isinstance(meta_tag, Tag):
                meta_desc = str(meta_tag.get("content", ""))

            text = self._extract_text(soup)
            headings = self._extract_headings(soup)
            links = self._extract_links(soup, url)

            return ScrapedPage(
                url=url, title=title, text=text, meta_description=meta_desc,
                headings=headings, links=links, word_count=len(text.split()),
                success=True,
            )

        except requests.RequestException as e:
            return ScrapedPage(
                url=url, title="", text="", meta_description="",
                headings=[], links=[], word_count=0, success=False,
                error=str(e),
            )

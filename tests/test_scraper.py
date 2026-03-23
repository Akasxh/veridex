"""Tests for scraper module."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from src.scraper import ScrapedPage, WebScraper


class TestScrapedPage:
    def test_creation(self) -> None:
        page = ScrapedPage(
            url="https://example.com",
            title="Example",
            text="Hello world",
            meta_description="desc",
            headings=["H1"],
            links=[],
            word_count=2,
            success=True,
        )
        assert page.url == "https://example.com"
        assert page.success is True
        assert page.error == ""

    def test_failed_page(self) -> None:
        page = ScrapedPage(
            url="https://fail.com",
            title="",
            text="",
            meta_description="",
            headings=[],
            links=[],
            word_count=0,
            success=False,
            error="Connection refused",
        )
        assert page.success is False
        assert "Connection" in page.error


class TestWebScraper:
    @patch("src.scraper.RobotFileParser")
    def test_robots_txt_blocks_url(self, mock_rp_cls: MagicMock) -> None:
        mock_rp = MagicMock()
        mock_rp.can_fetch.return_value = False
        mock_rp_cls.return_value = mock_rp

        scraper = WebScraper()
        # Clear cache to force our mock
        scraper._robots_cache = {}
        result = scraper.scrape("https://blocked.com/secret")

        assert result.success is False
        assert "robots.txt" in result.error

    @patch("src.scraper.requests.get")
    def test_non_html_content_type(self, mock_get: MagicMock) -> None:
        mock_resp = MagicMock()
        mock_resp.headers = {"content-type": "application/pdf", "content-length": "1000"}
        mock_resp.raise_for_status = MagicMock()

        mock_get.return_value = mock_resp

        scraper = WebScraper(rate_limit_delay=0.0)
        scraper._robots_cache = {}
        # Make robots check pass
        with patch.object(scraper, "_can_fetch", return_value=True):
            result = scraper.scrape("https://example.com/file.pdf")

        assert result.success is False
        assert "Non-HTML" in result.error

    @patch("src.scraper.requests.get")
    def test_content_too_large(self, mock_get: MagicMock) -> None:
        mock_resp = MagicMock()
        mock_resp.headers = {"content-type": "text/html", "content-length": "999999999"}
        mock_resp.raise_for_status = MagicMock()

        mock_get.return_value = mock_resp

        scraper = WebScraper(rate_limit_delay=0.0, max_content_length=5_000_000)
        with patch.object(scraper, "_can_fetch", return_value=True):
            result = scraper.scrape("https://example.com/huge")

        assert result.success is False
        assert "too large" in result.error

    @patch("src.scraper.requests.get")
    def test_successful_html_scrape(self, mock_get: MagicMock) -> None:
        html = """<html><head><title>Test Page</title>
        <meta name="description" content="A test page"></head>
        <body><main>
        <h1>Main Heading</h1>
        <p>This is a sufficiently long paragraph for extraction to work properly in the scraper.</p>
        <p>Another paragraph that is also long enough for the scraper extraction logic to pick up.</p>
        </main></body></html>"""

        mock_resp = MagicMock()
        mock_resp.headers = {"content-type": "text/html; charset=utf-8"}
        mock_resp.text = html
        mock_resp.raise_for_status = MagicMock()

        mock_get.return_value = mock_resp

        scraper = WebScraper(rate_limit_delay=0.0)
        with patch.object(scraper, "_can_fetch", return_value=True):
            result = scraper.scrape("https://example.com/page")

        assert result.success is True
        assert result.title == "Test Page"
        assert result.meta_description == "A test page"
        assert "Main Heading" in result.headings

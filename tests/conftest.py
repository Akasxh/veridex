"""Shared fixtures for ResearchBot test suite."""

from __future__ import annotations

import pytest

from src.credibility import CredibilityScore
from src.extractor import ExtractedFacts
from src.scraper import ScrapedPage
from src.search import SearchResult
from src.storage import Storage


@pytest.fixture()
def memory_storage() -> Storage:
    """In-memory SQLite storage for isolated tests."""
    return Storage(db_path=":memory:")


@pytest.fixture()
def sample_search_results() -> list[SearchResult]:
    return [
        SearchResult(
            title="AI in Healthcare Review",
            url="https://www.nature.com/articles/ai-health",
            snippet="Comprehensive review of AI applications in clinical medicine.",
            source="nature.com",
        ),
        SearchResult(
            title="Machine Learning Drug Discovery",
            url="https://arxiv.org/abs/2024.1234",
            snippet="ML approaches for pharmaceutical research.",
            source="arxiv.org",
        ),
    ]


@pytest.fixture()
def sample_scraped_page() -> ScrapedPage:
    return ScrapedPage(
        url="https://www.nature.com/articles/ai-health",
        title="AI in Healthcare Review",
        text="Artificial intelligence is transforming healthcare. " * 50,
        meta_description="A review of AI in healthcare",
        headings=["Introduction", "Methods", "Results"],
        links=["https://example.com/ref1"],
        word_count=350,
        success=True,
    )


@pytest.fixture()
def sample_extracted_facts() -> ExtractedFacts:
    return ExtractedFacts(
        entities={"ORG": ["WHO", "FDA"], "GPE": ["United States"]},
        key_phrases=["artificial intelligence", "healthcare systems"],
        statistics=["AI market projected to reach $187 billion by 2030."],
        claims=["According to a study, AI matches radiologist accuracy."],
    )

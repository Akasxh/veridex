"""Tests for credibility scoring module."""

from __future__ import annotations

import pytest

from src.credibility import CredibilityScore, CredibilityScorer


@pytest.fixture()
def scorer() -> CredibilityScorer:
    return CredibilityScorer()


class TestCredibilityScore:
    def test_rating_high(self) -> None:
        cs = CredibilityScore(
            url="https://nature.com", domain="nature.com",
            score=0.95, is_https=True, is_known_source=True,
            tld_trust=0.5, reasons=[],
        )
        assert cs.rating == "High"

    def test_rating_medium(self) -> None:
        cs = CredibilityScore(
            url="https://example.com", domain="example.com",
            score=0.6, is_https=True, is_known_source=False,
            tld_trust=0.5, reasons=[],
        )
        assert cs.rating == "Medium"

    def test_rating_low(self) -> None:
        cs = CredibilityScore(
            url="http://spam.com", domain="spam.com",
            score=0.3, is_https=False, is_known_source=False,
            tld_trust=0.5, reasons=[],
        )
        assert cs.rating == "Low"


class TestCredibilityScorer:
    def test_trusted_domain_nature(self, scorer: CredibilityScorer) -> None:
        result = scorer.score("https://www.nature.com/articles/123")
        assert result.score >= 0.9
        assert result.is_known_source is True
        assert result.rating == "High"

    def test_https_vs_http(self, scorer: CredibilityScorer) -> None:
        https_result = scorer.score("https://example.com/page")
        http_result = scorer.score("http://example.com/page")
        assert https_result.score > http_result.score

    def test_blogspot_low_credibility(self, scorer: CredibilityScorer) -> None:
        result = scorer.score("https://random.blogspot.com/post")
        assert result.score < 0.6
        assert any("User-generated" in r for r in result.reasons)

    @pytest.mark.parametrize(
        "url,expected_min",
        [
            ("https://www.cdc.gov/health", 0.85),
            ("https://mit.edu/research", 0.80),
        ],
    )
    def test_gov_edu_tld_trust(self, scorer: CredibilityScorer, url: str, expected_min: float) -> None:
        result = scorer.score(url)
        assert result.score >= expected_min
        assert result.tld_trust == 0.85

    def test_word_count_bonus(self, scorer: CredibilityScorer) -> None:
        short = scorer.score("https://example.com/x", word_count=50)
        long = scorer.score("https://example.com/x", word_count=1000)
        assert long.score > short.score

    def test_citations_bonus(self, scorer: CredibilityScorer) -> None:
        without = scorer.score("https://example.com/x")
        with_cit = scorer.score("https://example.com/x", has_citations=True)
        assert with_cit.score > without.score

    def test_score_clamped_0_to_1(self, scorer: CredibilityScorer) -> None:
        # Even worst case should be >= 0.0
        result = scorer.score("http://spam.blogspot.com/x", word_count=10)
        assert 0.0 <= result.score <= 1.0

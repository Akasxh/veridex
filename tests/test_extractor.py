"""Tests for extractor module."""

from __future__ import annotations

import pytest

from src.extractor import ExtractedFacts, FactExtractor


@pytest.fixture(scope="module")
def extractor() -> FactExtractor:
    """Shared extractor (loads spaCy model once)."""
    return FactExtractor()


class TestExtractedFacts:
    def test_dataclass_fields(self) -> None:
        facts = ExtractedFacts(
            entities={"ORG": ["NASA"]},
            key_phrases=["space exploration"],
            statistics=["Budget is $25 billion."],
            claims=["Research showed improvement."],
        )
        assert facts.entities["ORG"] == ["NASA"]
        assert len(facts.key_phrases) == 1
        assert len(facts.statistics) == 1
        assert len(facts.claims) == 1


class TestFactExtractor:
    def test_extract_returns_proper_structure(self, extractor: FactExtractor) -> None:
        text = (
            "Google and Microsoft are leading AI research. "
            "The United States invests heavily in technology. "
            "According to a study, 45% of companies use machine learning."
        )
        facts = extractor.extract(text)

        assert isinstance(facts, ExtractedFacts)
        assert isinstance(facts.entities, dict)
        assert isinstance(facts.key_phrases, list)
        assert isinstance(facts.statistics, list)
        assert isinstance(facts.claims, list)

    def test_statistics_with_percentages(self, extractor: FactExtractor) -> None:
        text = (
            "The adoption rate reached 78.5% in 2024. "
            "Revenue grew by 23% compared to the previous year. "
            "About $500 million was invested in renewable energy projects last year."
        )
        facts = extractor.extract(text)
        # At least one stat should be extracted (percentage or dollar amount)
        assert len(facts.statistics) >= 1

    def test_entity_extraction_with_named_entities(self, extractor: FactExtractor) -> None:
        text = (
            "Barack Obama visited the United Nations headquarters in New York City. "
            "He met with representatives from the World Health Organization."
        )
        facts = extractor.extract(text)
        # Should find at least some entities
        all_entities = [e for ents in facts.entities.values() for e in ents]
        assert len(all_entities) >= 1

    def test_claims_extraction(self, extractor: FactExtractor) -> None:
        text = (
            "According to research published in Nature, the treatment showed a 40% improvement. "
            "A study demonstrated that early intervention reduced complications significantly. "
            "The weather is nice today."
        )
        facts = extractor.extract(text)
        # Should pick up at least one claim (sentences with claim indicators)
        assert len(facts.claims) >= 1
        assert any("research" in c.lower() or "study" in c.lower() for c in facts.claims)

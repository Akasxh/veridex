"""Tests for demo module."""

from __future__ import annotations

import pytest

from src.demo import DEMO_QUERIES, get_demo_queries, get_demo_result


class TestDemo:
    def test_get_demo_queries_returns_list(self) -> None:
        queries = get_demo_queries()
        assert isinstance(queries, list)
        assert len(queries) >= 3

    def test_get_demo_result_known_query(self) -> None:
        queries = get_demo_queries()
        result = get_demo_result(queries[0])
        assert result is not None
        assert "query" in result
        assert "summary" in result
        assert "sources" in result
        assert len(result["sources"]) > 0

    def test_get_demo_result_unknown_query(self) -> None:
        result = get_demo_result("nonexistent query that does not exist")
        assert result is None

    @pytest.mark.parametrize("query", get_demo_queries())
    def test_all_demo_queries_have_required_keys(self, query: str) -> None:
        result = get_demo_result(query)
        assert result is not None
        required_keys = {
            "query", "summary", "key_sentences", "entities",
            "key_phrases", "statistics", "claims", "sources",
            "consensus_points", "conflict_points",
        }
        assert required_keys.issubset(result.keys()), f"Missing keys: {required_keys - result.keys()}"

    @pytest.mark.parametrize("query", get_demo_queries())
    def test_demo_sources_have_credibility(self, query: str) -> None:
        result = get_demo_result(query)
        assert result is not None
        for src in result["sources"]:
            assert "credibility_score" in src
            assert 0.0 <= src["credibility_score"] <= 1.0
            assert src["credibility_rating"] in ("High", "Medium", "Low")

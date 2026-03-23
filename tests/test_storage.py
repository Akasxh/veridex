"""Tests for SQLite storage module."""

from __future__ import annotations

import pytest

from src.storage import ResearchRecord, Storage


class TestStorage:
    def test_save_and_get_history(self, memory_storage: Storage) -> None:
        sid = memory_storage.save_session(
            query="test AI research",
            num_sources=3,
            summary="AI is transforming healthcare.",
        )
        assert isinstance(sid, int)
        assert sid > 0

        history = memory_storage.get_history(limit=10)
        assert len(history) == 1
        assert history[0].query == "test AI research"
        assert history[0].num_sources == 3

    def test_get_session(self, memory_storage: Storage) -> None:
        sid = memory_storage.save_session(
            query="quantum computing",
            num_sources=5,
            summary="Quantum breakthroughs.",
        )
        session = memory_storage.get_session(sid)
        assert session is not None
        assert session.query == "quantum computing"
        assert session.num_sources == 5

    def test_get_session_not_found(self, memory_storage: Storage) -> None:
        result = memory_storage.get_session(99999)
        assert result is None

    def test_search_history(self, memory_storage: Storage) -> None:
        memory_storage.save_session(query="climate change energy", num_sources=4, summary="s1")
        memory_storage.save_session(query="AI healthcare", num_sources=3, summary="s2")
        memory_storage.save_session(query="climate policy", num_sources=2, summary="s3")

        results = memory_storage.search_history("climate")
        assert len(results) == 2
        assert all("climate" in r.query.lower() for r in results)

    def test_delete_session(self, memory_storage: Storage) -> None:
        sid = memory_storage.save_session(query="to delete", num_sources=1, summary="gone")
        assert memory_storage.get_session(sid) is not None

        deleted = memory_storage.delete_session(sid)
        assert deleted is True
        assert memory_storage.get_session(sid) is None

    def test_delete_nonexistent_session(self, memory_storage: Storage) -> None:
        deleted = memory_storage.delete_session(99999)
        assert deleted is False

    def test_save_with_sources(self, memory_storage: Storage) -> None:
        sources = [
            {"url": "https://nature.com/1", "title": "Paper 1", "credibility_score": 0.95, "word_count": 5000},
            {"url": "https://arxiv.org/2", "title": "Paper 2", "credibility_score": 0.85, "word_count": 3000},
        ]
        sid = memory_storage.save_session(
            query="test with sources",
            num_sources=2,
            summary="Summary",
            sources=sources,
        )
        session = memory_storage.get_session(sid)
        assert session is not None
        assert session.num_sources == 2

    def test_history_ordering(self, memory_storage: Storage) -> None:
        """Most recent session should come first."""
        memory_storage.save_session(query="first", num_sources=1, summary="s1")
        memory_storage.save_session(query="second", num_sources=1, summary="s2")

        history = memory_storage.get_history(limit=10)
        assert len(history) >= 2
        # Most recent first
        assert history[0].query == "second"

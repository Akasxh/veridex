"""SQLite research history storage."""

from __future__ import annotations

import json
import logging
import sqlite3
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

_DEFAULT_DB = Path.home() / ".veridex" / "history.db"

_SCHEMA = """
CREATE TABLE IF NOT EXISTS research_sessions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    query TEXT NOT NULL,
    created_at TEXT NOT NULL,
    num_sources INTEGER DEFAULT 0,
    summary TEXT,
    report_path TEXT,
    metadata TEXT
);

CREATE TABLE IF NOT EXISTS research_sources (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id INTEGER NOT NULL,
    url TEXT NOT NULL,
    title TEXT,
    credibility_score REAL,
    word_count INTEGER,
    FOREIGN KEY (session_id) REFERENCES research_sessions(id)
);

CREATE INDEX IF NOT EXISTS idx_sessions_query ON research_sessions(query);
CREATE INDEX IF NOT EXISTS idx_sessions_created ON research_sessions(created_at);
"""


@dataclass
class ResearchRecord:
    """A stored research session."""

    id: int
    query: str
    created_at: str
    num_sources: int
    summary: str
    report_path: str
    metadata: dict[str, Any]


@dataclass
class Storage:
    """SQLite-backed research history."""

    db_path: Path = _DEFAULT_DB
    _persistent_conn: sqlite3.Connection | None = field(default=None, init=False, repr=False)

    def __post_init__(self) -> None:
        if isinstance(self.db_path, str):
            if self.db_path == ":memory:":
                # Keep a persistent connection for :memory: databases
                self._persistent_conn = sqlite3.connect(":memory:")
            else:
                self.db_path = Path(self.db_path)
        if isinstance(self.db_path, Path):
            self.db_path.parent.mkdir(parents=True, exist_ok=True)
        with self._connect() as conn:
            conn.executescript(_SCHEMA)

    def _connect(self) -> sqlite3.Connection:
        if self._persistent_conn is not None:
            return self._persistent_conn
        return sqlite3.connect(str(self.db_path))

    def save_session(
        self,
        query: str,
        num_sources: int,
        summary: str,
        report_path: str = "",
        sources: list[dict[str, Any]] | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> int:
        """Save a research session. Returns the session ID."""
        now = datetime.now(timezone.utc).isoformat()
        meta_json = json.dumps(metadata or {})

        with self._connect() as conn:
            cursor = conn.execute(
                "INSERT INTO research_sessions (query, created_at, num_sources, summary, report_path, metadata) "
                "VALUES (?, ?, ?, ?, ?, ?)",
                (query, now, num_sources, summary, report_path, meta_json),
            )
            session_id = cursor.lastrowid
            assert session_id is not None

            if sources:
                for src in sources:
                    conn.execute(
                        "INSERT INTO research_sources (session_id, url, title, credibility_score, word_count) "
                        "VALUES (?, ?, ?, ?, ?)",
                        (
                            session_id,
                            src.get("url", ""),
                            src.get("title", ""),
                            src.get("credibility_score", 0.0),
                            src.get("word_count", 0),
                        ),
                    )

        return session_id

    def get_history(self, limit: int = 20) -> list[ResearchRecord]:
        """Get recent research sessions."""
        with self._connect() as conn:
            rows = conn.execute(
                "SELECT id, query, created_at, num_sources, summary, report_path, metadata "
                "FROM research_sessions ORDER BY created_at DESC LIMIT ?",
                (limit,),
            ).fetchall()

        return [
            ResearchRecord(
                id=r[0], query=r[1], created_at=r[2], num_sources=r[3],
                summary=r[4] or "", report_path=r[5] or "",
                metadata=json.loads(r[6]) if r[6] else {},
            )
            for r in rows
        ]

    def get_session(self, session_id: int) -> ResearchRecord | None:
        """Get a specific session."""
        with self._connect() as conn:
            row = conn.execute(
                "SELECT id, query, created_at, num_sources, summary, report_path, metadata "
                "FROM research_sessions WHERE id = ?",
                (session_id,),
            ).fetchone()

        if not row:
            return None

        return ResearchRecord(
            id=row[0], query=row[1], created_at=row[2], num_sources=row[3],
            summary=row[4] or "", report_path=row[5] or "",
            metadata=json.loads(row[6]) if row[6] else {},
        )

    def search_history(self, query: str) -> list[ResearchRecord]:
        """Search past research sessions."""
        with self._connect() as conn:
            rows = conn.execute(
                "SELECT id, query, created_at, num_sources, summary, report_path, metadata "
                "FROM research_sessions WHERE query LIKE ? ORDER BY created_at DESC LIMIT 50",
                (f"%{query}%",),
            ).fetchall()

        return [
            ResearchRecord(
                id=r[0], query=r[1], created_at=r[2], num_sources=r[3],
                summary=r[4] or "", report_path=r[5] or "",
                metadata=json.loads(r[6]) if r[6] else {},
            )
            for r in rows
        ]

    def get_all_sources(self) -> list[dict]:
        """Return all research sources with session info for analytics."""
        with self._connect() as conn:
            rows = conn.execute(
                "SELECT rs.url, rs.title, rs.credibility_score, rs.word_count, s.query, s.created_at "
                "FROM research_sources rs JOIN research_sessions s ON rs.session_id = s.id "
                "ORDER BY s.created_at DESC LIMIT 500"
            ).fetchall()
        return [
            {"url": r[0], "title": r[1], "credibility_score": r[2], "word_count": r[3], "query": r[4], "created_at": r[5]}
            for r in rows
        ]

    def delete_session(self, session_id: int) -> bool:
        """Delete a research session."""
        with self._connect() as conn:
            conn.execute("DELETE FROM research_sources WHERE session_id = ?", (session_id,))
            cursor = conn.execute("DELETE FROM research_sessions WHERE id = ?", (session_id,))
            return cursor.rowcount > 0

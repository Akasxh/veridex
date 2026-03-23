"""Tests for report generation module."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from src.report import ReportData, ReportGenerator, SourceInfo


def _make_report_data() -> ReportData:
    return ReportData(
        query="AI in healthcare",
        summary="AI is transforming healthcare across diagnostics and drug discovery.",
        key_sentences=["AI matches radiologist accuracy.", "Drug discovery accelerated by 30%."],
        entities={"ORG": ["WHO", "FDA"], "GPE": ["United States"]},
        key_phrases=["artificial intelligence", "healthcare"],
        statistics=["Market reaches $187 billion by 2030."],
        claims=["According to a study, AI improves outcomes."],
        sources=[
            SourceInfo(
                url="https://nature.com/ai",
                title="AI Review",
                credibility_score=0.95,
                credibility_rating="High",
                word_count=5000,
                snippet="Comprehensive review.",
            ),
        ],
        consensus_points=["Sources agree on AI potential."],
        conflict_points=["Timelines differ between sources."],
    )


class TestReportGenerator:
    def test_generate_markdown_content(self) -> None:
        gen = ReportGenerator()
        data = _make_report_data()
        md = gen.generate_markdown(data)

        assert isinstance(md, str)
        assert "# Research Report: AI in healthcare" in md
        assert "Executive Summary" in md
        assert "Key Findings" in md
        assert "AI matches radiologist" in md
        assert "nature.com/ai" in md
        assert "High" in md
        assert "Source Agreement Analysis" in md

    def test_save_json_creates_valid_file(self, tmp_path: Path) -> None:
        gen = ReportGenerator(output_dir=tmp_path)
        data = _make_report_data()
        path = gen.save_json(data)

        assert path.exists()
        assert path.suffix == ".json"

        content = json.loads(path.read_text(encoding="utf-8"))
        assert content["query"] == "AI in healthcare"
        assert len(content["sources"]) == 1
        assert content["sources"][0]["credibility_score"] == 0.95
        assert "key_sentences" in content
        assert "statistics" in content

    def test_save_markdown_creates_file(self, tmp_path: Path) -> None:
        gen = ReportGenerator(output_dir=tmp_path)
        data = _make_report_data()
        path = gen.save_markdown(data)

        assert path.exists()
        assert path.suffix == ".md"
        content = path.read_text(encoding="utf-8")
        assert "AI in healthcare" in content

    def test_safe_filename(self) -> None:
        gen = ReportGenerator()
        assert gen._safe_filename("Hello World!") == "Hello_World"
        assert len(gen._safe_filename("x" * 100)) <= 60

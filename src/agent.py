"""Main research agent orchestrator."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any

try:
    from src.credibility import CredibilityScorer
    from src.extractor import ExtractedFacts, FactExtractor
    from src.report import ReportData, ReportGenerator, SourceInfo
    from src.scraper import ScrapedPage, WebScraper
    from src.search import SearchEngine, SearchResult
    from src.storage import Storage
    from src.summarizer import Summarizer
except ImportError:
    from credibility import CredibilityScorer  # type: ignore[no-redef]
    from extractor import ExtractedFacts, FactExtractor  # type: ignore[no-redef]
    from report import ReportData, ReportGenerator, SourceInfo  # type: ignore[no-redef]
    from scraper import ScrapedPage, WebScraper  # type: ignore[no-redef]
    from search import SearchEngine, SearchResult  # type: ignore[no-redef]
    from storage import Storage  # type: ignore[no-redef]
    from summarizer import Summarizer  # type: ignore[no-redef]


@dataclass
class ResearchSource:
    """A fully processed research source."""

    search_result: SearchResult
    page: ScrapedPage | None
    facts: ExtractedFacts | None
    credibility_score: float
    credibility_rating: str


@dataclass
class ResearchResult:
    """Complete research result."""

    query: str
    sources: list[ResearchSource]
    summary: str
    key_sentences: list[str]
    merged_entities: dict[str, list[str]]
    key_phrases: list[str]
    statistics: list[str]
    claims: list[str]
    consensus_points: list[str]
    conflict_points: list[str]
    report_data: ReportData | None = None


def _detect_consensus_and_conflicts(
    sources: list[ResearchSource],
) -> tuple[list[str], list[str]]:
    """Compare sources for consensus and conflict detection using keyword overlap."""
    if len(sources) < 2:
        return [], []

    # Collect key claims per source
    source_claims: list[set[str]] = []
    for src in sources:
        if src.facts:
            words: set[str] = set()
            for phrase in src.facts.key_phrases[:10]:
                words.update(w.lower() for w in phrase.split() if len(w) > 3)
            for claims in src.facts.claims[:5]:
                words.update(w.lower() for w in claims.split() if len(w) > 3)
            source_claims.append(words)
        else:
            source_claims.append(set())

    # Find overlapping topics (consensus) and unique topics (potential conflicts)
    consensus_points: list[str] = []
    conflict_points: list[str] = []

    if len(source_claims) >= 2:
        # Topics mentioned by majority of sources
        all_words: dict[str, int] = {}
        for claims in source_claims:
            for w in claims:
                all_words[w] = all_words.get(w, 0) + 1

        threshold = max(2, len(sources) // 2)
        common = sorted(
            [w for w, c in all_words.items() if c >= threshold],
            key=lambda w: all_words[w],
            reverse=True,
        )[:10]

        if common:
            consensus_points.append(
                f"Multiple sources discuss: {', '.join(common)}"
            )

        # Topics unique to single sources
        for i, claims in enumerate(source_claims):
            unique = claims - set().union(*(source_claims[:i] + source_claims[i + 1 :]))
            important_unique = [w for w in unique if len(w) > 5]
            if important_unique and sources[i].page:
                title = sources[i].page.title[:40] if sources[i].page else sources[i].search_result.url
                conflict_points.append(
                    f"Unique to {title}: {', '.join(list(important_unique)[:5])}"
                )

    return consensus_points[:5], conflict_points[:5]


ProgressCallback = type[None] | Any  # Callable[[str, float], None] or None


@dataclass
class ResearchAgent:
    """Orchestrates the full research pipeline."""

    max_sources: int = 8
    search_engine: SearchEngine = field(default_factory=SearchEngine)
    scraper: WebScraper = field(default_factory=WebScraper)
    summarizer: Summarizer = field(default_factory=Summarizer)
    extractor: FactExtractor = field(default_factory=FactExtractor)
    scorer: CredibilityScorer = field(default_factory=CredibilityScorer)
    report_gen: ReportGenerator = field(default_factory=ReportGenerator)
    storage: Storage = field(default_factory=Storage)

    def research(
        self,
        query: str,
        max_sources: int | None = None,
        progress_cb: Any = None,
    ) -> ResearchResult:
        """Run full research pipeline on a query."""
        n = max_sources or self.max_sources

        def _progress(msg: str, pct: float) -> None:
            if progress_cb:
                progress_cb(msg, pct)

        # Step 1: Search
        _progress("Searching the web...", 0.05)
        results = self.search_engine.search(query, max_results=n + 4)

        if not results:
            return ResearchResult(
                query=query, sources=[], summary="No search results found.",
                key_sentences=[], merged_entities={}, key_phrases=[],
                statistics=[], claims=[], consensus_points=[], conflict_points=[],
            )

        # Step 2: Scrape top results
        _progress(f"Scraping {min(len(results), n)} sources...", 0.15)
        processed: list[ResearchSource] = []
        texts: list[str] = []

        for i, sr in enumerate(results[:n + 2]):
            if len(processed) >= n:
                break
            _progress(f"Scraping: {sr.title[:40]}...", 0.15 + 0.4 * (i / n))

            page = self.scraper.scrape(sr.url)
            if not page.success or page.word_count < 50:
                continue

            # Score credibility
            has_citations = bool(re.search(r"\[\d+\]|<ref|cite|bibliography", page.text.lower()))
            cred = self.scorer.score(sr.url, word_count=page.word_count, has_citations=has_citations)

            # Extract facts
            _progress(f"Extracting facts from: {sr.title[:40]}...", 0.15 + 0.4 * (i / n))
            facts = self.extractor.extract(page.text)

            processed.append(
                ResearchSource(
                    search_result=sr,
                    page=page,
                    facts=facts,
                    credibility_score=cred.score,
                    credibility_rating=cred.rating,
                )
            )
            texts.append(page.text)

        if not processed:
            return ResearchResult(
                query=query, sources=[], summary="Could not scrape any sources.",
                key_sentences=[], merged_entities={}, key_phrases=[],
                statistics=[], claims=[], consensus_points=[], conflict_points=[],
            )

        # Step 3: Summarize
        _progress("Summarizing content...", 0.65)
        summary_result = self.summarizer.multi_document_summarize(texts, max_sentences=7)

        # Step 4: Merge facts
        _progress("Analyzing facts...", 0.75)
        merged_entities: dict[str, list[str]] = {}
        all_phrases: list[str] = []
        all_stats: list[str] = []
        all_claims: list[str] = []

        for src in processed:
            if not src.facts:
                continue
            for label, ents in src.facts.entities.items():
                if label not in merged_entities:
                    merged_entities[label] = []
                merged_entities[label].extend(ents)
            all_phrases.extend(src.facts.key_phrases)
            all_stats.extend(src.facts.statistics)
            all_claims.extend(src.facts.claims)

        # Deduplicate
        for label in merged_entities:
            merged_entities[label] = list(dict.fromkeys(merged_entities[label]))[:15]
        all_phrases = list(dict.fromkeys(all_phrases))[:20]
        all_stats = list(dict.fromkeys(all_stats))[:15]
        all_claims = list(dict.fromkeys(all_claims))[:15]

        # Step 5: Consensus/conflict detection
        _progress("Comparing sources...", 0.85)
        consensus, conflicts = _detect_consensus_and_conflicts(processed)

        # Step 6: Build report data
        _progress("Generating report...", 0.90)
        source_infos = [
            SourceInfo(
                url=s.search_result.url,
                title=s.page.title if s.page else s.search_result.title,
                credibility_score=s.credibility_score,
                credibility_rating=s.credibility_rating,
                word_count=s.page.word_count if s.page else 0,
                snippet=s.search_result.snippet,
            )
            for s in processed
        ]

        report_data = ReportData(
            query=query,
            summary=summary_result.summary,
            key_sentences=summary_result.key_sentences,
            entities=merged_entities,
            key_phrases=all_phrases,
            statistics=all_stats,
            claims=all_claims,
            sources=source_infos,
            consensus_points=consensus,
            conflict_points=conflicts,
        )

        # Step 7: Save to history
        _progress("Saving to history...", 0.95)
        self.storage.save_session(
            query=query,
            num_sources=len(processed),
            summary=summary_result.summary[:500],
            sources=[
                {
                    "url": s.search_result.url,
                    "title": s.page.title if s.page else "",
                    "credibility_score": s.credibility_score,
                    "word_count": s.page.word_count if s.page else 0,
                }
                for s in processed
            ],
        )

        _progress("Done!", 1.0)

        return ResearchResult(
            query=query,
            sources=processed,
            summary=summary_result.summary,
            key_sentences=summary_result.key_sentences,
            merged_entities=merged_entities,
            key_phrases=all_phrases,
            statistics=all_stats,
            claims=all_claims,
            consensus_points=consensus,
            conflict_points=conflicts,
            report_data=report_data,
        )

    def export_report(
        self, result: ResearchResult, formats: list[str] | None = None
    ) -> dict[str, str]:
        """Export research result to files. Returns format -> path mapping."""
        if not result.report_data:
            return {}

        fmt_list = formats or ["markdown"]
        paths: dict[str, str] = {}

        for fmt in fmt_list:
            if fmt == "markdown":
                p = self.report_gen.save_markdown(result.report_data)
                paths["markdown"] = str(p)
            elif fmt == "pdf":
                p = self.report_gen.save_pdf(result.report_data)
                paths["pdf"] = str(p)
            elif fmt == "json":
                p = self.report_gen.save_json(result.report_data)
                paths["json"] = str(p)

        return paths

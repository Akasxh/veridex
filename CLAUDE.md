# ResearchBot -- AI Web Research Agent

Autonomous web research agent that searches DuckDuckGo, scrapes pages (robots.txt aware, rate-limited), extracts facts via spaCy NLP, scores source credibility across multiple dimensions, and synthesizes multi-source findings into structured reports. Multi-page Streamlit dashboard with Plotly analytics, source radar charts, and claim verification matrix. Supports Markdown, PDF, and JSON export with citations. SQLite-backed research history. Demo mode included for offline presentations. Zero API keys required -- all ML runs locally.

## How to Run

```bash
uv sync && uv run python -m spacy download en_core_web_sm && uv run streamlit run src/app.py
```

Opens at http://localhost:8501. Demo mode works without network access.

### Docker

```bash
docker build -t researchbot:latest .
docker run --rm -p 8501:8501 researchbot:latest
```

Or with Compose: `docker compose up --build -d`

## Key Files

| File | Purpose | Lines |
|------|---------|-------|
| `src/app.py` | Streamlit multi-page UI (Dashboard, Research, History, Analytics, About) | ~1397 |
| `src/cli.py` | CLI for automated research queries and batch use | ~217 |
| `src/agent.py` | Research pipeline orchestrator (search -> scrape -> analyze -> report) | ~311 |
| `src/search.py` | DuckDuckGo search wrapper with rate limiting | ~85 |
| `src/scraper.py` | Web scraping with robots.txt compliance and content extraction | ~183 |
| `src/summarizer.py` | TF-IDF TextRank extractive summarization across documents | ~94 |
| `src/extractor.py` | spaCy NLP fact extraction (entities, key phrases, statistics, claims) | ~119 |
| `src/credibility.py` | Source credibility scoring engine (domain trust, HTTPS, known sources) | ~123 |
| `src/report.py` | Multi-format report generation (Markdown/PDF/JSON) with citations | ~241 |
| `src/storage.py` | SQLite research history tracking + `get_all_sources()` for analytics | ~175 |
| `src/demo.py` | Pre-cached demo results for offline use (3 queries) | ~319 |

## Testing

```bash
uv run pytest tests/ -v
```

8 test modules in `tests/`: test_credibility, test_demo, test_extractor, test_report, test_scraper, test_search, test_storage, test_summarizer.

## Architecture

Pipeline: Query -> SearchEngine.search() -> WebScraper.scrape() -> FactExtractor.extract() -> CredibilityScorer.score() -> Summarizer.multi_document_summarize() -> _detect_consensus_and_conflicts() -> ReportGenerator -> Storage.save_session()

All components are dataclasses with default_factory. ResearchAgent orchestrates everything in `research()` method with progress callbacks.

Dual interface: Streamlit (app.py) for interactive use, argparse CLI (cli.py) for automation. Both use same ResearchAgent class.

## Stack

Python 3.12+, Streamlit 1.40+, Plotly 5.18+, spaCy 3.8+, scikit-learn 1.5+, ddgs 7.0+, BeautifulSoup4, lxml, FPDF2, SQLite, uv + hatchling, ruff, pytest 9.0+.

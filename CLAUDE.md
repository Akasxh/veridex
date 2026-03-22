# ResearchBot — AI Web Research Agent

Autonomous web research agent that searches DuckDuckGo, scrapes pages (robots.txt aware, rate-limited), extracts facts via spaCy NLP, scores source credibility, and synthesizes multi-source findings into structured reports. Supports Markdown, PDF, and JSON export with citations. SQLite-backed research history. Demo mode included for offline presentations.

## How to Run

```bash
uv sync && uv run python -m spacy download en_core_web_sm && uv run streamlit run src/app.py
```

Opens at http://localhost:8501. Demo mode works without network access.

## Key Files

| File | Purpose |
|------|---------|
| `src/app.py` | Streamlit web interface for interactive research |
| `src/cli.py` | CLI for automated research queries and batch use |
| `src/agent.py` | Research pipeline orchestrator (search -> scrape -> analyze -> report) |
| `src/search.py` | DuckDuckGo search wrapper with rate limiting |
| `src/scraper.py` | Web scraping with robots.txt compliance and content extraction |
| `src/summarizer.py` | TF-IDF TextRank extractive summarization across documents |
| `src/extractor.py` | spaCy NLP fact extraction (entities, key phrases, statistics, claims) |
| `src/credibility.py` | Source credibility scoring engine (domain trust, HTTPS, known sources) |
| `src/report.py` | Multi-format report generation (Markdown/PDF/JSON) with citations |
| `src/storage.py` | SQLite research history tracking |
| `src/demo.py` | Pre-cached demo results for offline use |

## Testing

```bash
uv run python -c "from src.demo import *; print('Imports OK')"
```

## Architecture

Pipeline: Query -> DuckDuckGo search (search) -> web scraping with robots.txt (scraper) -> NLP fact extraction (extractor) -> credibility scoring (credibility) -> TF-IDF summarization (summarizer) -> multi-source comparison & synthesis (agent) -> report generation (report) -> SQLite history (storage).

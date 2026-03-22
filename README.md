# ResearchBot -- AI Web Research Agent

An autonomous web research agent that searches, scrapes, summarizes, and synthesizes information from multiple web sources into structured research reports. **No paid API keys required** -- uses DuckDuckGo search and local NLP.

## Features

- **Automated Web Search** -- DuckDuckGo integration, no API keys needed
- **Intelligent Scraping** -- robots.txt aware, rate-limited, content extraction from HTML
- **Extractive Summarization** -- TF-IDF based TextRank across multiple documents
- **NLP Fact Extraction** -- Named entities, key phrases, statistics, and claims via spaCy
- **Source Credibility Scoring** -- Domain trust heuristics, HTTPS, known sources database
- **Multi-Source Comparison** -- Consensus and conflict detection across sources
- **Multiple Export Formats** -- Markdown, PDF, and JSON reports with citations
- **Research History** -- SQLite-backed session tracking and search
- **Dual Interface** -- CLI for automation, Streamlit for interactive use

## Quick Start

```bash
# Install dependencies
uv sync

# Download spaCy model (first run only)
uv run python -m spacy download en_core_web_sm

# CLI usage
uv run python src/cli.py "impact of quantum computing on cryptography"
uv run python src/cli.py "climate change mitigation strategies" -n 10 -f markdown pdf json

# Web interface
uv run streamlit run src/app.py
```

## CLI Options

```
usage: researchbot [-h] [-n NUM_SOURCES] [-f {markdown,pdf,json} ...] [--history] [--search-history QUERY] query

positional arguments:
  query                 Research query/topic

options:
  -n, --num-sources     Max sources to analyze (default: 6)
  -f, --format          Export formats: markdown, pdf, json (default: markdown)
  --history             Show research history
  --search-history      Search past research sessions
```

## Architecture

```
src/
  agent.py       -- Research pipeline orchestrator
  search.py      -- DuckDuckGo search wrapper with rate limiting
  scraper.py     -- Web scraping with robots.txt compliance
  summarizer.py  -- TF-IDF TextRank extractive summarization
  extractor.py   -- spaCy NLP fact extraction
  credibility.py -- Source credibility scoring engine
  report.py      -- Multi-format report generation (MD/PDF/JSON)
  storage.py     -- SQLite research history
  cli.py         -- Command-line interface
  app.py         -- Streamlit web interface
```

### Pipeline

1. **Search** -- Query DuckDuckGo for relevant web pages
2. **Scrape** -- Fetch and parse HTML, extract clean text (robots.txt aware)
3. **Analyze** -- Extract entities, key phrases, statistics, and claims
4. **Score** -- Evaluate source credibility using domain heuristics
5. **Summarize** -- TF-IDF TextRank extractive summarization across documents
6. **Compare** -- Detect consensus and conflicts between sources
7. **Report** -- Generate structured report with citations
8. **Store** -- Save session to SQLite history

## Tech Stack

| Component | Technology |
|-----------|-----------|
| Search | DuckDuckGo (no API key) |
| Scraping | requests + BeautifulSoup4 + lxml |
| NLP | spaCy (en_core_web_sm) |
| Summarization | scikit-learn (TF-IDF + cosine similarity) |
| Reports | fpdf2 (PDF), stdlib json |
| Storage | SQLite3 (stdlib) |
| Web UI | Streamlit |
| Package Manager | uv |

## Responsible Scraping

ResearchBot is designed for respectful web access:

- Checks `robots.txt` before scraping any domain
- Rate limits requests (2s delay between requests to same domain)
- Identifies itself via User-Agent string
- Limits content size (5MB max)
- Only processes HTML content

## Reports

Reports are saved to `~/.researchbot/reports/` and include:

- Executive summary
- Key findings with source attribution
- Named entities and key topics
- Statistics and data points
- Notable claims with citations
- Source consensus and conflict analysis
- Full source table with credibility ratings

## License

MIT

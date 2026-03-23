<div align="center">
  <h1>🔬 ResearchBot</h1>
  <p><strong>Open-source intelligence analyst that fact-checks the internet in real time.</strong></p>
  <p>
    <img src="https://img.shields.io/badge/python-3.12+-blue?logo=python&logoColor=white" alt="Python 3.12+"/>
    <img src="https://img.shields.io/badge/license-MIT-green" alt="MIT License"/>
    <img src="https://img.shields.io/badge/NLP-spaCy-09a3d5?logo=spacy" alt="spaCy"/>
    <img src="https://img.shields.io/badge/UI-Streamlit-FF4B4B?logo=streamlit" alt="Streamlit"/>
    <img src="https://img.shields.io/badge/API_keys-zero-brightgreen" alt="Zero API Keys"/>
    <img src="https://img.shields.io/badge/LLM-none_required-orange" alt="No LLM Required"/>
  </p>
  <p>
    <a href="#features">Features</a> &bull;
    <a href="#demo">Demo</a> &bull;
    <a href="#quick-start">Quick Start</a> &bull;
    <a href="#architecture">Architecture</a> &bull;
    <a href="#tech-stack">Tech Stack</a> &bull;
    <a href="#cli-reference">CLI</a> &bull;
    <a href="#docker">Docker</a>
  </p>
  <img src="./screenshots/hero.png" width="800" alt="ResearchBot Dashboard"/>
</div>

---

ResearchBot is an autonomous web research agent that searches the open web via DuckDuckGo, scrapes pages with robots.txt compliance and rate limiting, extracts structured facts using spaCy NLP, scores source credibility across multiple dimensions, and synthesizes multi-source findings into exportable reports. Every claim is traced back to its source. Every source is scored. Every conflict between sources is surfaced.

**No API keys. No LLM. No hallucinations.** All intelligence runs locally using classical NLP -- TF-IDF vectorization, TextRank summarization, named entity recognition, and cross-source verification. Think of it as: *What if Perplexity showed its work?*

---

## Features

🔍 **Autonomous Web Search** -- Queries DuckDuckGo and retrieves up to 10+ sources per research topic with automatic deduplication and relevance filtering.

🕷️ **Robots.txt-Aware Scraping** -- Respects `robots.txt` directives, enforces rate limiting (configurable delay), and extracts clean text from HTML using BeautifulSoup + lxml.

🧠 **NLP Fact Extraction** -- spaCy `en_core_web_sm` pipeline extracts named entities (people, organizations, dates, locations), key phrases, statistical claims, and factual assertions from every source.

📊 **Multi-Dimensional Credibility Scoring** -- Evaluates sources on domain authority, HTTPS usage, content depth (word count), citation density, and known-source matching. Results displayed as radar charts per source.

🔗 **Cross-Source Verification** -- Compares extracted claims across all sources to identify consensus points (multiple sources agree) and conflicts (unique or contradictory claims). Displayed as a claim verification matrix.

📈 **Interactive Analytics Dashboard** -- Five Plotly charts: research activity over time, sources per query, credibility distribution (donut chart), top researched topics, and research timeline scatter plot.

📑 **Multi-Format Export** -- Generate reports in Markdown, PDF (via FPDF2), or structured JSON with full citations, entity tables, and source credibility breakdowns.

💾 **SQLite Research History** -- Every research session is persisted with full metadata. Search, filter, sort, and re-run past queries from the History page.

🎭 **Offline Demo Mode** -- Three pre-cached research queries (AI in healthcare, quantum computing, climate/renewables) work without network access for presentations and testing.

🖥️ **Multi-Page Dashboard** -- Five-page Streamlit app: Dashboard (overview + quick stats), Research (live pipeline), History (past sessions), Analytics (Plotly charts), and About (architecture + tech stack).

---

## Demo

<table>
  <tr>
    <td align="center">
      <img src="./screenshots/research.png" width="400" alt="Research Pipeline"/>
      <br/><em>Live research pipeline with tabbed results: findings, entities, sources, and full report</em>
    </td>
    <td align="center">
      <img src="./screenshots/analytics.png" width="400" alt="Analytics Dashboard"/>
      <br/><em>Plotly-powered analytics: credibility distribution, activity trends, top topics</em>
    </td>
  </tr>
  <tr>
    <td align="center">
      <img src="./screenshots/history.png" width="400" alt="Research History"/>
      <br/><em>Searchable research history with filters, sorting, and session re-run</em>
    </td>
    <td align="center">
      <img src="./screenshots/mobile.png" width="400" alt="Mobile View"/>
      <br/><em>Responsive layout with dark theme and custom CSS design system</em>
    </td>
  </tr>
</table>

---

## Architecture

```mermaid
graph TD
    subgraph Interface["🖥️ Interface Layer"]
        UI["Streamlit App<br/>(5 pages, 1397 lines)"]
        CLI["CLI Interface<br/>(argparse)"]
    end

    subgraph Agent["🤖 Orchestration"]
        RA["ResearchAgent<br/>Pipeline Controller"]
    end

    subgraph Search["🔍 Data Acquisition"]
        SE["SearchEngine<br/>DuckDuckGo API"]
        WS["WebScraper<br/>robots.txt aware"]
    end

    subgraph Analysis["🧠 NLP Analysis"]
        FE["FactExtractor<br/>spaCy NER + phrases"]
        CS["CredibilityScorer<br/>Multi-dimensional"]
        SUM["Summarizer<br/>TF-IDF TextRank"]
        CDC["Consensus/Conflict<br/>Detection"]
    end

    subgraph Output["📊 Output Layer"]
        RG["ReportGenerator<br/>MD / PDF / JSON"]
        ST["SQLite Storage<br/>Research History"]
        PLT["Plotly Charts<br/>Analytics"]
    end

    UI --> RA
    CLI --> RA
    RA --> SE
    SE -->|SearchResults| WS
    WS -->|ScrapedPages| FE
    WS -->|ScrapedPages| CS
    FE -->|ExtractedFacts| CDC
    FE -->|ExtractedFacts| SUM
    CS -->|CredibilityScore| RG
    CDC -->|Consensus + Conflicts| RG
    SUM -->|Summary| RG
    RG --> ST
    ST --> PLT

    style Interface fill:#1a1a2e,stroke:#6c63ff,color:#e0e0e0
    style Agent fill:#16213e,stroke:#a855f7,color:#e0e0e0
    style Search fill:#0f3460,stroke:#6c63ff,color:#e0e0e0
    style Analysis fill:#1a1a2e,stroke:#a855f7,color:#e0e0e0
    style Output fill:#16213e,stroke:#6c63ff,color:#e0e0e0
```

---

## Research Pipeline

```mermaid
sequenceDiagram
    actor User
    participant UI as Streamlit / CLI
    participant Agent as ResearchAgent
    participant DDG as DuckDuckGo
    participant Scraper as WebScraper
    participant NLP as FactExtractor
    participant Cred as CredibilityScorer
    participant Sum as Summarizer
    participant Report as ReportGenerator
    participant DB as SQLite

    User->>UI: Enter research query
    UI->>Agent: research(query, max_sources)
    Agent->>DDG: search(query, max_results)
    DDG-->>Agent: SearchResult[]

    loop For each source (up to N)
        Agent->>Scraper: scrape(url)
        Scraper->>Scraper: Check robots.txt
        Scraper->>Scraper: Rate limit delay
        Scraper-->>Agent: ScrapedPage (title, text, word_count)
        Agent->>NLP: extract(page.text)
        NLP-->>Agent: ExtractedFacts (entities, phrases, claims, stats)
        Agent->>Cred: score(url, word_count, has_citations)
        Cred-->>Agent: CredibilityResult (score, rating)
    end

    Agent->>Sum: multi_document_summarize(texts)
    Sum-->>Agent: SummaryResult (summary, key_sentences)
    Agent->>Agent: detect_consensus_and_conflicts()
    Agent->>Report: generate(ReportData)
    Report-->>Agent: Markdown / PDF / JSON
    Agent->>DB: save_session(query, sources, summary)
    Agent-->>UI: ResearchResult
    UI-->>User: Dashboard with findings, charts, export
```

---

## Quick Start

### Prerequisites

- **Python 3.12+**
- **[uv](https://docs.astral.sh/uv/)** -- fast Python package manager (`curl -LsSf https://astral.sh/uv/install.sh | sh`)

### Install and Run

```bash
# Clone the repository
git clone https://github.com/akash/researchbot.git
cd researchbot

# Install dependencies + spaCy language model
uv sync
uv run python -m spacy download en_core_web_sm

# Start the web app
uv run streamlit run src/app.py
```

The dashboard opens at [http://localhost:8501](http://localhost:8501).

### One-Liner

```bash
uv sync && uv run python -m spacy download en_core_web_sm && uv run streamlit run src/app.py
```

### Using Make

```bash
make install   # Install all dependencies
make run       # Start Streamlit (port 8501)
make dev       # Start with hot-reload on file save
make test      # Run pytest suite
make lint      # Run ruff linter
make format    # Auto-format with ruff
make clean     # Remove caches and build artifacts
```

---

## Docker

### Build and Run

```bash
# Build the image (multi-stage, ~500MB)
docker build -t researchbot:latest .

# Run the container
docker run --rm -p 8501:8501 --name researchbot researchbot:latest
```

### Docker Compose (recommended)

```bash
# Copy environment config
cp .env.example .env

# Start with persistent SQLite volume
docker compose up --build -d

# View logs
docker compose logs -f researchbot

# Stop
docker compose down
```

The Docker setup includes:
- Multi-stage build for minimal image size
- Non-root `appuser` for security
- Named volume (`researchbot-data`) for SQLite persistence across restarts
- Health check endpoint at `/_stcore/health`
- Auto-restart policy (`unless-stopped`)

---

## CLI Reference

ResearchBot includes a full CLI for scripting and automation:

```bash
# Run a research query
uv run python src/cli.py "impact of AI on healthcare"

# Specify max sources and export formats
uv run python src/cli.py "quantum computing breakthroughs" -n 8 -f markdown pdf json

# View research history
uv run python src/cli.py --history

# Search past sessions
uv run python src/cli.py --search-history "climate"

# Run in demo mode (no network required)
uv run python src/cli.py --demo "AI healthcare"

# List available demo queries
uv run python src/cli.py --list-demos
```

### CLI Options

| Flag | Description | Default |
|------|-------------|---------|
| `query` | Research topic (positional) | -- |
| `-n`, `--num-sources` | Maximum sources to scrape and analyze | `6` |
| `-f`, `--format` | Export formats: `markdown`, `pdf`, `json` | `markdown` |
| `--history` | Display all past research sessions | -- |
| `--search-history` | Search sessions by keyword | -- |
| `--demo` | Use pre-cached results (offline) | -- |
| `--list-demos` | Show available demo queries | -- |

---

## Tech Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| **Language** | Python 3.12+ | Type hints, dataclasses, modern syntax |
| **Web UI** | Streamlit 1.40+ | Multi-page dashboard with custom CSS |
| **Charts** | Plotly 5.18+ | Interactive analytics (radar, donut, scatter, bar, line) |
| **NLP** | spaCy 3.8+ (`en_core_web_sm`) | Named entity recognition, tokenization, POS tagging |
| **Summarization** | scikit-learn 1.5+ | TF-IDF vectorization + TextRank extractive summarization |
| **Search** | ddgs 7.0+ | DuckDuckGo search API wrapper |
| **Scraping** | BeautifulSoup4 + lxml | HTML parsing and clean text extraction |
| **HTTP** | requests + urllib3 | Web requests with robots.txt compliance |
| **PDF Export** | FPDF2 2.8+ | PDF report generation with citations |
| **Database** | SQLite (stdlib) | Research history persistence |
| **Packaging** | uv + hatchling | Fast dependency resolution and builds |
| **Linting** | ruff | Linting + formatting (replaces black, isort, flake8) |
| **Testing** | pytest 9.0+ | Unit and integration tests |
| **Container** | Docker + Compose | Multi-stage build, health checks, named volumes |

---

## Project Structure

```
researchbot/
├── src/
│   ├── __init__.py          # Package marker
│   ├── app.py               # Streamlit multi-page UI (1,397 lines)
│   ├── cli.py               # CLI interface with argparse
│   ├── agent.py             # Research pipeline orchestrator
│   ├── search.py            # DuckDuckGo search wrapper
│   ├── scraper.py           # Web scraping (robots.txt aware, rate-limited)
│   ├── extractor.py         # spaCy NLP fact extraction
│   ├── credibility.py       # Multi-dimensional credibility scoring
│   ├── summarizer.py        # TF-IDF TextRank multi-document summarization
│   ├── report.py            # Report generation (Markdown, PDF, JSON)
│   ├── storage.py           # SQLite research history
│   └── demo.py              # Pre-cached demo data for offline use
├── tests/
│   ├── __init__.py
│   ├── conftest.py          # Shared pytest fixtures
│   ├── test_credibility.py  # Credibility scorer tests
│   ├── test_demo.py         # Demo mode tests
│   ├── test_extractor.py    # NLP extraction tests
│   ├── test_report.py       # Report generation tests
│   ├── test_scraper.py      # Web scraper tests
│   ├── test_search.py       # Search engine tests
│   ├── test_storage.py      # SQLite storage tests
│   └── test_summarizer.py   # Summarizer tests
├── screenshots/             # UI screenshots
├── Dockerfile               # Multi-stage Docker build
├── docker-compose.yml       # Compose with persistent volume
├── Makefile                 # Build, run, test, lint commands
├── pyproject.toml           # Project config (uv + hatch)
├── .env.example             # Environment variable template
├── .gitignore               # Git ignore rules
├── LICENSE                  # MIT License
└── README.md                # This file
```

---

## Environment Variables

All configuration is optional. ResearchBot works with zero configuration out of the box.

| Variable | Description | Default |
|----------|-------------|---------|
| `STREAMLIT_SERVER_PORT` | Port for the Streamlit web server | `8501` |
| `STREAMLIT_SERVER_HEADLESS` | Run without opening browser | `true` |
| `RESEARCHBOT_MAX_SOURCES` | Maximum sources to scrape per query | `10` |
| `RESEARCHBOT_RATE_LIMIT_DELAY` | Seconds between scrape requests | `1.0` |
| `RESEARCHBOT_DB_PATH` | SQLite database file path | `data/research_history.db` |
| `LOG_LEVEL` | Logging verbosity (`DEBUG`, `INFO`, `WARNING`, `ERROR`) | `INFO` |

Copy the template to get started:

```bash
cp .env.example .env
```

---

## Testing

```bash
# Run the full test suite
uv run pytest tests/ -v

# Run with coverage
uv run pytest tests/ -v --tb=short

# Run a specific test module
uv run pytest tests/test_credibility.py -v

# Quick import check (all modules)
uv run python -c "from src.agent import ResearchAgent; print('All imports OK')"
```

---

## Responsible Scraping

ResearchBot is designed to be a respectful web citizen:

- **robots.txt compliance** -- Every domain's `robots.txt` is fetched and parsed before scraping. Disallowed paths are never accessed.
- **Rate limiting** -- Configurable delay (default 1 second) between requests to the same domain. No concurrent scraping of a single host.
- **User-Agent transparency** -- Identifies itself clearly in HTTP headers so site operators can recognize and block it if desired.
- **Content-only extraction** -- Strips navigation, ads, scripts, and boilerplate. Only extracts the article body text relevant to research.
- **No login bypass** -- Does not attempt to circumvent paywalls, login walls, or CAPTCHAs. Inaccessible content is skipped gracefully.
- **Local processing only** -- Scraped content is processed locally via spaCy and scikit-learn. No data is sent to external APIs or third-party services.

---

## Why No LLM?

ResearchBot deliberately avoids large language models. Here is why:

1. **Zero hallucination risk** -- Every sentence in the output traces back to a real source URL. TF-IDF extractive summarization selects actual sentences from actual documents.
2. **No API keys, no cost, no rate limits** -- Runs fully offline (after initial web search). No OpenAI/Anthropic/Google billing. No vendor lock-in.
3. **Full transparency** -- The entire pipeline is inspectable. You can see exactly which sources contributed which facts, how credibility was scored, and where sources agree or disagree.
4. **Reproducibility** -- Same query, same sources, same output. No temperature sampling, no stochastic generation.

---

## License

MIT License. See [LICENSE](./LICENSE) for details.

---

<div align="center">
  <p>Built with classical NLP, zero API keys, and a healthy skepticism of everything on the internet.</p>
  <p>
    <a href="#-researchbot">Back to top</a>
  </p>
</div>

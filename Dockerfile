# Stage 1: Builder — install dependencies with uv
FROM python:3.12-slim AS builder

RUN pip install --no-cache-dir uv

WORKDIR /build

COPY pyproject.toml uv.lock* ./

RUN uv sync --no-dev --frozen 2>/dev/null || uv sync --no-dev

COPY src/ src/

RUN uv run python -m spacy download en_core_web_sm


# Stage 2: Slim runtime
FROM python:3.12-slim AS runtime

RUN groupadd --gid 1000 appuser && \
    useradd --uid 1000 --gid 1000 --create-home appuser

WORKDIR /app

# Copy the full venv from builder
COPY --from=builder /build/.venv /app/.venv
COPY --from=builder /build/src /app/src
COPY --from=builder /build/pyproject.toml /app/pyproject.toml

# Ensure venv binaries are on PATH
ENV PATH="/app/.venv/bin:$PATH"
ENV VIRTUAL_ENV="/app/.venv"
ENV STREAMLIT_SERVER_PORT=8501
ENV STREAMLIT_SERVER_HEADLESS=true
ENV STREAMLIT_BROWSER_GATHER_USAGE_STATS=false

# Create data directory for SQLite persistence
RUN mkdir -p /app/data && chown -R appuser:appuser /app

USER appuser

EXPOSE 8501

HEALTHCHECK --interval=30s --timeout=10s --start-period=15s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8501/_stcore/health')" || exit 1

CMD ["streamlit", "run", "src/app.py", \
     "--server.port=8501", \
     "--server.address=0.0.0.0", \
     "--server.headless=true", \
     "--browser.gatherUsageStats=false"]

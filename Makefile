.DEFAULT_GOAL := help

# ── Setup ──────────────────────────────────────────────
.PHONY: install
install: ## Install all dependencies and spaCy model
	uv sync
	uv run python -m spacy download en_core_web_sm

# ── Run ────────────────────────────────────────────────
.PHONY: run
run: ## Start Streamlit app (port 8501)
	uv run streamlit run src/app.py

.PHONY: dev
dev: ## Start Streamlit in dev/watch mode
	uv run streamlit run src/app.py --server.runOnSave=true

# ── Quality ────────────────────────────────────────────
.PHONY: test
test: ## Run pytest test suite
	uv run pytest tests/ -v

.PHONY: lint
lint: ## Run ruff linter on src/
	uv run ruff check src/

.PHONY: format
format: ## Auto-format code with ruff
	uv run ruff format src/
	uv run ruff check --fix src/

# ── Clean ──────────────────────────────────────────────
.PHONY: clean
clean: ## Remove caches, bytecode, and build artifacts
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -name "*.pyc" -delete 2>/dev/null || true
	find . -name "*.pyo" -delete 2>/dev/null || true
	rm -rf build/ dist/ *.egg-info/ .pytest_cache/ htmlcov/ .coverage .mypy_cache/ .ruff_cache/

# ── Docker ─────────────────────────────────────────────
.PHONY: docker-build
docker-build: ## Build Docker image
	docker build -t veridex:latest .

.PHONY: docker-run
docker-run: ## Run Docker container (port 8501)
	docker run --rm -p 8501:8501 --name veridex veridex:latest

.PHONY: docker-compose-up
docker-compose-up: ## Start services with docker-compose
	docker compose up --build -d

.PHONY: docker-compose-down
docker-compose-down: ## Stop docker-compose services
	docker compose down

# ── Help ───────────────────────────────────────────────
.PHONY: help
help: ## Show this help message
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-22s\033[0m %s\n", $$1, $$2}'

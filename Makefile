# Copilot Webhook Orchestrator - Development Makefile
# =====================================================
# This Makefile provides convenient commands for development tasks.
# Uses uv (https://github.com/astral-sh/uv) for Python package management.

.DEFAULT_GOAL := help
.PHONY: help install install-dev test lint format typecheck clean run dev

# Variables
BACKEND_DIR := src/backend
PYTHON_VERSION := 3.12

# =====================================================
# Help
# =====================================================

help: ## Show this help message
	@echo "Copilot Webhook Orchestrator - Development Commands"
	@echo "===================================================="
	@echo ""
	@echo "Backend (Python/FastAPI):"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}'

# =====================================================
# Backend - Environment Setup
# =====================================================

venv: ## Create Python virtual environment with uv
	cd $(BACKEND_DIR) && uv venv --python $(PYTHON_VERSION)

install: ## Install backend dependencies
	cd $(BACKEND_DIR) && uv sync

install-dev: ## Install backend dependencies including dev tools
	cd $(BACKEND_DIR) && uv sync --all-extras

lock: ## Lock backend dependencies
	cd $(BACKEND_DIR) && uv lock

upgrade: ## Upgrade all backend dependencies
	cd $(BACKEND_DIR) && uv lock --upgrade

add: ## Add a backend dependency (usage: make add pkg=<package>)
	cd $(BACKEND_DIR) && uv add $(pkg)

add-dev: ## Add a backend dev dependency (usage: make add-dev pkg=<package>)
	cd $(BACKEND_DIR) && uv add --dev $(pkg)

remove: ## Remove a backend dependency (usage: make remove pkg=<package>)
	cd $(BACKEND_DIR) && uv remove $(pkg)

# =====================================================
# Backend - Development
# =====================================================

run: ## Run the backend server
	cd $(BACKEND_DIR) && uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

dev: run ## Alias for run

shell: ## Open a Python shell with the virtual environment
	cd $(BACKEND_DIR) && uv run python

# =====================================================
# Backend - Testing
# =====================================================

test: ## Run backend tests
	cd $(BACKEND_DIR) && uv run pytest

test-v: ## Run backend tests with verbose output
	cd $(BACKEND_DIR) && uv run pytest -v

test-vv: ## Run backend tests with very verbose output
	cd $(BACKEND_DIR) && uv run pytest -vv

test-cov: ## Run backend tests with coverage
	cd $(BACKEND_DIR) && uv run pytest --cov=app --cov-report=term-missing --cov-report=html

test-unit: ## Run only unit tests
	cd $(BACKEND_DIR) && uv run pytest tests/unit -v

test-integration: ## Run only integration tests
	cd $(BACKEND_DIR) && uv run pytest tests/integration -v

test-watch: ## Run tests in watch mode (requires pytest-watch)
	cd $(BACKEND_DIR) && uv run ptw -- -v

# =====================================================
# Backend - Code Quality
# =====================================================

lint: ## Run linter (ruff) on backend code
	cd $(BACKEND_DIR) && uv run ruff check app tests

lint-fix: ## Run linter and fix auto-fixable issues
	cd $(BACKEND_DIR) && uv run ruff check --fix app tests

format: ## Format backend code with ruff
	cd $(BACKEND_DIR) && uv run ruff format app tests

format-check: ## Check if backend code is formatted
	cd $(BACKEND_DIR) && uv run ruff format --check app tests

typecheck: ## Run type checker (mypy) on backend code
	cd $(BACKEND_DIR) && uv run mypy app

check: lint format-check typecheck ## Run all code quality checks

fix: lint-fix format ## Fix all auto-fixable issues

# =====================================================
# Backend - Database
# =====================================================

db-init: ## Initialize the database
	cd $(BACKEND_DIR) && uv run python -c "from app.db.engine import init_db; init_db()"

db-reset: ## Reset the database (WARNING: destroys all data)
	cd $(BACKEND_DIR) && rm -f *.db && uv run python -c "from app.db.engine import init_db; init_db()"

# =====================================================
# Backend - Utilities
# =====================================================

clean: ## Clean backend build artifacts and caches
	cd $(BACKEND_DIR) && rm -rf .pytest_cache .mypy_cache .ruff_cache htmlcov .coverage
	cd $(BACKEND_DIR) && find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	cd $(BACKEND_DIR) && find . -type f -name "*.pyc" -delete 2>/dev/null || true

clean-venv: ## Remove the virtual environment
	cd $(BACKEND_DIR) && rm -rf .venv

clean-all: clean clean-venv ## Clean everything including virtual environment

# =====================================================
# Pre-commit
# =====================================================

pre-commit: ## Run pre-commit on all files
	pre-commit run --all-files

pre-commit-install: ## Install pre-commit hooks
	pre-commit install

# =====================================================
# Frontend (SvelteKit) - Placeholder for future development
# =====================================================

# Frontend commands will be added when frontend development begins.
# Expected structure:
#   FRONTEND_DIR := src/frontend
#
# frontend-install: ## Install frontend dependencies
# 	cd $(FRONTEND_DIR) && npm install
#
# frontend-dev: ## Run frontend development server
# 	cd $(FRONTEND_DIR) && npm run dev
#
# frontend-build: ## Build frontend for production
# 	cd $(FRONTEND_DIR) && npm run build
#
# frontend-test: ## Run frontend tests
# 	cd $(FRONTEND_DIR) && npm test
#
# frontend-lint: ## Lint frontend code
# 	cd $(FRONTEND_DIR) && npm run lint

# =====================================================
# Combined Commands
# =====================================================

setup: venv install-dev pre-commit-install ## Full development setup
	@echo "Development environment ready!"
	@echo "Run 'make test' to verify the setup."

all-tests: test ## Run all tests (backend + frontend when available)

all-lint: lint ## Run all linters (backend + frontend when available)

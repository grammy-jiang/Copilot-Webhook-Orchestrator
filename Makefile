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
# Frontend (SvelteKit 2.x + pnpm)
# =====================================================

FRONTEND_DIR := src/frontend

frontend-install: ## Install frontend dependencies
	cd $(FRONTEND_DIR) && pnpm install

frontend-install-browsers: ## Install Playwright browsers for E2E tests
	cd $(FRONTEND_DIR) && pnpm exec playwright install

frontend-dev: ## Run frontend development server
	cd $(FRONTEND_DIR) && pnpm dev

frontend-build: ## Build frontend for production
	cd $(FRONTEND_DIR) && pnpm build

frontend-preview: ## Preview production build
	cd $(FRONTEND_DIR) && pnpm preview

frontend-test: ## Run frontend unit/component tests
	cd $(FRONTEND_DIR) && pnpm test

frontend-test-ui: ## Run frontend tests with UI
	cd $(FRONTEND_DIR) && pnpm test:ui

frontend-test-e2e: ## Run frontend E2E tests (Playwright)
	cd $(FRONTEND_DIR) && pnpm test:e2e

frontend-test-all: ## Run all frontend tests (unit + E2E)
	cd $(FRONTEND_DIR) && pnpm test && pnpm test:e2e

frontend-check: ## Run SvelteKit type checking
	cd $(FRONTEND_DIR) && pnpm check

frontend-lint: ## Lint frontend code
	cd $(FRONTEND_DIR) && pnpm lint

frontend-format: ## Format frontend code
	cd $(FRONTEND_DIR) && pnpm format

frontend-clean: ## Clean frontend build artifacts
	cd $(FRONTEND_DIR) && rm -rf .svelte-kit build node_modules/.vite

frontend-add: ## Add a frontend dependency (usage: make frontend-add pkg=<package>)
	cd $(FRONTEND_DIR) && pnpm add $(pkg)

frontend-add-dev: ## Add a frontend dev dependency (usage: make frontend-add-dev pkg=<package>)
	cd $(FRONTEND_DIR) && pnpm add -D $(pkg)

# =====================================================
# Combined Commands
# =====================================================

setup: venv install-dev pre-commit-install ## Full backend development setup
	@echo "Backend development environment ready!"
	@echo "Run 'make test' to verify the setup."

setup-frontend: frontend-install frontend-install-browsers ## Full frontend development setup
	@echo "Frontend development environment ready!"
	@echo "Run 'make frontend-test' to verify the setup."

setup-all: setup setup-frontend ## Full stack development setup
	@echo "Full stack development environment ready!"

all-tests: test frontend-test ## Run all tests (backend + frontend)

all-lint: lint frontend-lint ## Run all linters (backend + frontend)

all-check: check frontend-check ## Run all code quality checks

dev-all: ## Run both backend and frontend dev servers (use separate terminals)
	@echo "Run 'make run' in one terminal for backend (port 8000)"
	@echo "Run 'make frontend-dev' in another terminal for frontend (port 5173)"

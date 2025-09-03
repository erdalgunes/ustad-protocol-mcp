# Makefile for Sequential Thinking MCP Server
# Enforces Pythonic code standards

.PHONY: help install dev-install lint format type-check security test coverage clean pre-commit ci-local

# Colors for output
RED := \033[0;31m
GREEN := \033[0;32m
YELLOW := \033[1;33m
NC := \033[0m # No Color

help: ## Show this help message
	@echo "$(GREEN)Sequential Thinking MCP - Development Commands$(NC)"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  $(YELLOW)%-20s$(NC) %s\n", $$1, $$2}'

install: ## Install production dependencies
	poetry install --only main

dev-install: ## Install all dependencies including dev
	poetry install
	pre-commit install
	@echo "$(GREEN)✅ Development environment ready!$(NC)"

lint: ## Run all linters (ruff, mypy, bandit)
	@echo "$(YELLOW)Running Ruff linter...$(NC)"
	poetry run ruff check src/ tests/
	@echo "$(YELLOW)Running type checker...$(NC)"
	poetry run mypy src/ --strict
	@echo "$(YELLOW)Running security scan...$(NC)"
	poetry run bandit -r src/
	@echo "$(YELLOW)Running docstring checker...$(NC)"
	poetry run pydocstyle src/
	@echo "$(GREEN)✅ All linting checks passed!$(NC)"

format: ## Auto-format code with ruff and black
	@echo "$(YELLOW)Running Ruff formatter...$(NC)"
	poetry run ruff check src/ tests/ --fix
	poetry run ruff format src/ tests/
	@echo "$(YELLOW)Running Black formatter...$(NC)"
	poetry run black src/ tests/
	@echo "$(YELLOW)Running isort...$(NC)"
	poetry run isort src/ tests/
	@echo "$(GREEN)✅ Code formatted!$(NC)"

type-check: ## Run mypy type checking
	poetry run mypy src/ --strict

security: ## Run security checks with bandit
	poetry run bandit -r src/ -ll

test: ## Run tests
	poetry run pytest tests/ -v

test-fast: ## Run tests without coverage
	poetry run pytest tests/ -v --no-cov

coverage: ## Run tests with coverage report
	poetry run pytest tests/ \
		--cov=src \
		--cov-report=term-missing \
		--cov-report=html \
		--cov-report=xml \
		--cov-fail-under=80
	@echo "$(GREEN)✅ Coverage report generated in htmlcov/index.html$(NC)"

clean: ## Clean up cache and build files
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name "*.coverage" -delete
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".mypy_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".ruff_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "htmlcov" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "coverage.xml" -delete
	@echo "$(GREEN)✅ Cleaned up cache files$(NC)"

pre-commit: ## Run pre-commit hooks on all files
	pre-commit run --all-files

pre-commit-update: ## Update pre-commit hooks
	pre-commit autoupdate

ci-local: ## Run full CI pipeline locally
	@echo "$(YELLOW)🚀 Running full CI pipeline locally...$(NC)"
	@$(MAKE) clean
	@$(MAKE) format
	@$(MAKE) lint
	@$(MAKE) security
	@$(MAKE) coverage
	@echo "$(GREEN)✅ All CI checks passed locally!$(NC)"

check-all: lint type-check security test ## Run all checks (lint, type, security, test)
	@echo "$(GREEN)✅ All checks passed!$(NC)"

fix: format ## Alias for format
	@echo "$(GREEN)✅ Code fixed and formatted!$(NC)"

watch-test: ## Watch for changes and re-run tests
	poetry run ptw tests/ -- -v

complexity: ## Check code complexity
	@echo "$(YELLOW)Checking code complexity...$(NC)"
	poetry run python -m mccabe --min 10 src/
	@echo "$(GREEN)✅ Complexity check complete$(NC)"

docs: ## Generate documentation
	@echo "$(YELLOW)Generating documentation...$(NC)"
	poetry run pydoc -w src/
	@echo "$(GREEN)✅ Documentation generated$(NC)"

stats: ## Show code statistics
	@echo "$(YELLOW)Code Statistics:$(NC)"
	@echo ""
	@echo "Lines of Code:"
	@find src/ -name "*.py" | xargs wc -l | tail -1
	@echo ""
	@echo "Number of Python files:"
	@find src/ -name "*.py" | wc -l
	@echo ""
	@echo "Number of test files:"
	@find tests/ -name "test_*.py" | wc -l

validate: ## Validate pyproject.toml and pre-commit config
	@echo "$(YELLOW)Validating configuration files...$(NC)"
	poetry check
	pre-commit validate-config
	pre-commit validate-manifest
	@echo "$(GREEN)✅ All configuration files are valid$(NC)"

# Default target
.DEFAULT_GOAL := help
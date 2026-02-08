.PHONY: help setup-env upgrade-deps test format lint type-check check clean all

# Default target
help:
	@echo "Available targets:"
	@echo "  setup-env      - Install project dependencies"
	@echo "  upgrade-deps   - Upgrade all dependencies to latest versions"
	@echo "  test           - Run tests with coverage"
	@echo "  format         - Format code with black"
	@echo "  lint           - Lint code with ruff"
	@echo "  type-check     - Type check with mypy"
	@echo "  check          - Run all checks (format, lint, type-check, test)"
	@echo "  clean          - Remove cache and build artifacts"
	@echo "  all            - Run setup and all checks"

# Install dependencies
setup-env:
	uv pip install -e ".[dev]"

# Upgrade dependencies
upgrade-deps:
	uv pip install --upgrade -e ".[dev]"

# Run tests with coverage
test:
	uv run pytest --cov=src --cov-report=term-missing

# Format code
format:
	uv run black src tests

# Lint code
lint:
	uv run ruff check src tests

# Lint and auto-fix
lint-fix:
	uv run ruff check --fix src tests

# Type check
type-check:
	uv run mypy src

# Run all checks
check: format lint type-check test

# Clean cache and build artifacts
clean:
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".mypy_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".ruff_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name ".coverage" -delete 2>/dev/null || true

# Run setup and all checks
all: setup-env check

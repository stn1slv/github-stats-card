.PHONY: help setup upgrade-deps test format lint build run check clean all

# Default target
help:
	@echo "Available targets:"
	@echo "  setup          - Install project dependencies"
	@echo "  upgrade-deps   - Upgrade all dependencies to latest versions"
	@echo "  test           - Run tests with coverage"
	@echo "  format         - Format code with ruff"
	@echo "  lint           - Lint code with ruff"
	@echo "  build          - Build the application package"
	@echo "  run            - Run the CLI tool"
	@echo "  check          - Run all checks (format, lint, type-check, test)"
	@echo "  clean          - Remove cache and build artifacts"
	@echo "  all            - Run setup and all checks"

# Install dependencies
# --all-extras is required: pytest, mypy and ruff live in the `dev` extra, so a
# plain `uv sync` leaves `make lint`, `make type-check` and `make test` unable to run.
setup:
	uv sync --all-extras

# Upgrade dependencies
upgrade-deps:
	uv lock --upgrade
	uv sync --all-extras

# Run tests with coverage
test:
	uv run pytest --cov=src --cov-report=term-missing

# Format code
format:
	uv run ruff format src tests

# Lint code
lint:
	uv run ruff check src tests

# Lint and auto-fix
lint-fix:
	uv run ruff check --fix src tests

# Type check
type-check:
	uv run mypy src

# Build the package
build:
	uv build

# Run the CLI tool
run:
	uv run github-stats-card --help

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
all: setup check

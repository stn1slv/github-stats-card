# GitHub Stats Card

**Project Overview**

`github-stats-card` is a Python-based CLI tool designed to generate high-quality SVG statistics cards for GitHub profiles. It replicates the functionality of popular server-hosted stats cards but runs locally or via GitHub Actions, offering greater privacy, reliability, and customization. The project is architected as a modular application with a clear separation between data fetching (GitHub API), data processing, and SVG rendering.

**Main Technologies:**
*   **Language:** Python 3.13+
*   **Package Management:** `uv`
*   **CLI Framework:** `click`
*   **HTTP Client:** `requests`
*   **Testing:** `pytest`

**Architecture:**
The codebase follows a 3-tier modular structure:
*   `src/core/`: Foundation (Configuration, Constants, Utilities, i18n).
*   `src/github/`: Domain logic (API Client, Data Fetchers, Ranking Algorithm).
*   `src/rendering/`: Presentation (SVG Templates, Theme & Icon definitions).

**Building and Running**

The project uses `uv` for all lifecycle tasks.

*   **Install Dependencies:**
    ```bash
    uv sync
    ```

*   **Run the CLI (Development):**
    ```bash
    # Generate Stats Card
    uv run github-stats-card stats -u <username> -o stats.svg

    # Generate Top Languages Card
    uv run github-stats-card top-langs -u <username> -o langs.svg
    ```

*   **Run Tests:**
    ```bash
    uv run pytest
    ```

*   **Linting & Formatting:**
    ```bash
    uv run ruff check src tests
    uv run black src tests
    ```

*   **Type Checking:**
    ```bash
    uv run mypy src
    ```

**Development Conventions**

*   **Code Style:** Strict adherence to PEP 8, enforced by `ruff` and `black`.
*   **Type Hinting:** Mandatory use of modern Python type hints (PEP 604 style, e.g., `int | None`). `mypy` must pass in strict mode.
*   **Testing:** New features must include unit tests. The project maintains high test coverage.
*   **Modular Design:** Code must reside in the appropriate sub-package (`core`, `github`, or `rendering`). No circular dependencies.
*   **Contribution:** Follow the guidelines in `CONTRIBUTING.md`. Use Conventional Commits for commit messages.

## Active Technologies
- Python 3.13+ (Managed by `uv`) + Click (CLI), Requests (API), Built-in XML/SVG libraries (001-contributor-card)

## Recent Changes
- 001-contributor-card: Added Python 3.13+ (Managed by `uv`) + Click (CLI), Requests (API), Built-in XML/SVG libraries

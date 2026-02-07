<!--
SYNC IMPACT REPORT
Version Change: 1.0.0 -> 1.1.0
Modified Principles: Architectural Separation
Added Sections: None
Removed Sections: None
Templates requiring updates: None
Follow-up TODOs: None
-->

# github-stats-card Constitution

## Core Principles

### I. CLI-First & Automation Ready
The primary interface is the Command Line. Tools must be robust, scriptable (CI/CD friendly), and fully configurable via flags and environment variables (following 12-factor app principles where applicable). Output must be pipe-friendly.

### II. Self-Contained & Local
No external service dependencies for rendering are allowed. All stats generation and SVG rendering must happen locally within the Python environment. This ensures user privacy, speed, and reliability without reliance on third-party uptime.

### III. Modern Python Standards
We strictly adhere to the modern Python ecosystem. `uv` is the mandatory package manager. Code must be typed (`mypy` strict), linted (`ruff`), formatted (`black`), and target Python 3.13+. We strictly use modern type hinting (PEP 604, e.g., `int | None`).

### IV. Visual Flexibility & Accessibility
The tool produces visual artifacts (SVGs). These must be accessible (valid markup), themeable (support for light/dark modes and user-defined colors), and internationalized (i18n support). Visual regression testing is encouraged to ensure consistency.

### V. Test-Driven Quality (NON-NEGOTIABLE)
High test coverage is mandatory. Changes must be verified via `pytest`. Critical paths (fetching, ranking, rendering) must be covered by unit tests. New features require accompanying tests before they are considered complete.

## Design Constraints

### Architecture
- **Separation of Concerns:** We enforce a 3-tier sub-package architecture:
  - **`core/`**: Non-domain specific logic and configuration.
  - **`github/`**: All data retrieval and API-specific logic.
  - **`rendering/`**: All visual logic and SVG generation.
- **Centralized API Handling:** All network calls must pass through a managed client (e.g., `GitHubClient`) to ensure consistent timeout, error handling, and security.
- **Configuration:** All functional options must be strictly typed via Dataclasses inheriting from a common `BaseConfig`.

### Security
- **Token Safety:** GitHub Tokens must be handled securely, read from environment variables or secure input, never logged or hardcoded.
- **Input Validation:** User inputs (usernames, colors, themes) must be validated before processing to prevent injection or rendering errors.

## Development Workflow

### Code Review Gates
- **Linting:** Must pass `ruff check .`
- **Formatting:** Must pass `ruff format . --check`
- **Type Checking:** Must pass `mypy .`
- **Testing:** Must pass `pytest`

### Release Process
- Semantic Versioning (MAJOR.MINOR.PATCH) is strictly followed.
- Changelog must be updated for every release.

## Governance

This constitution governs the architectural and development standards of the `github-stats-card` project.

- **Amendments:** Changes to these principles require a Pull Request with a clear rationale and must be ratified by the project maintainers.
- **Compliance:** All Pull Requests are subject to automated checks against these principles. Code violating "Modern Python Standards" or the "3-tier architecture" will be rejected.

**Version**: 1.1.0 | **Ratified**: 2026-02-07 | **Last Amended**: 2026-02-07

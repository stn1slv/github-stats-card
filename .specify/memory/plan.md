# Development Plan: GitHub Stats Card

## Current Status
The project is a fully functional, highly modular Python CLI tool. It supports **GitHub Stats**, **Top Languages**, and **Top Contributions** card generation with extensive customization. The architecture has been recently refactored into a clear 3-tier sub-package structure (`core`, `github`, `rendering`), ensuring high supportability and extendability.

## Technical Stack
- **Language:** Python 3.13+
- **Dependency Management:** `uv`
- **CLI Framework:** `click`
- **HTTP Client:** `requests` (via centralized `GitHubClient`)
- **Testing:** `pytest` with `pytest-cov` and `pytest-mock`
- **Formatting/Linting:** `ruff`, `black`, `mypy`
- **Build System:** `hatchling`

## Project Structure
```
src/
├── core/                # Shared foundational logic
│   ├── config.py        # Centralized configuration & BaseConfig
│   ├── constants.py     # Centralized constants
│   ├── exceptions.py    # Custom exceptions
│   ├── i18n.py          # Internationalization support
│   └── utils.py         # General utility functions
├── github/              # GitHub-specific integration
│   ├── client.py        # Centralized REST/GraphQL client
│   ├── fetcher.py       # Stats & Contrib Card data fetcher
│   ├── langs_fetcher.py # Top Languages data fetcher
│   └── rank.py          # Ranking algorithm (Stats Card)
├── rendering/           # SVG generation and visual logic
│   ├── base.py          # Base SVG card renderer (shared)
│   ├── colors.py        # Color parsing and utilities
│   ├── contrib.py       # Contributor Card renderer
│   ├── icons.py         # SVG icons
│   ├── langs.py         # Top Languages Card renderer
│   ├── stats.py         # Stats Card renderer
│   └── themes.py        # Theme definitions
├── cli.py               # CLI orchestration
├── __init__.py
└── __main__.py          # Module entry point
```

## Primary Dependencies
- `requests>=2.28.0`: For GitHub API interaction.
- `click>=8.0.0`: For the command-line interface.

## Configuration
- `GITHUB_TOKEN`: Environment variable for GitHub authentication.
- `GITHUB_API_URL`: Custom REST API URL (optional).
- `GITHUB_GRAPHQL_URL`: Custom GraphQL endpoint (optional).

## Development Guidelines
- Use `uv run` for all development tasks.
- Maintain strict typing with `mypy` and modern PEP 604 hints.
- Follow Google-style docstrings.
- Ensure 100% test coverage for core logic and utilities.
- All new features must align with the 3-tier sub-package architecture.

## Recent Changes
- **Contributor Card (2026-02-08):** Added `contrib` subcommand to display top external contributions.
  - Implemented `fetch_contributor_stats` with GraphQL filtering and sorting.
  - Added Base64 avatar embedding for repository owners.
  - Created `ContribCardConfig` and `rendering/contrib.py`.
- **Modular Refactor:** Split the flat structure into `core`, `github`, and `rendering` packages.
- **API Consolidation:** Introduced `GitHubClient` to manage all external requests.
- **Config Automation:** Added `BaseConfig` to handle boilerplate CLI argument parsing.
- **Type Hinting:** Migrated entire codebase to Python 3.10+ modern type hints.

## Future Work
- **Planned: Repository Card:** Implement a card type to display statistics for a specific repository (distinct from user contributions).
  - *Requirements:* New subcommand, `github/repo_fetcher.py`, and `rendering/repo.py`.
- Add support for GitHub Discussions Answered and Achievements.
- Improve SVG accessibility (aria-labels and screen reader support).
- Transition SVG generation to a templating engine (e.g., Jinja2) for better clarity.

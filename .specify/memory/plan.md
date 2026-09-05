# Development Plan: GitHub Stats Card

## Current Status
The project is a fully functional, highly modular Python CLI tool. It supports **GitHub Stats**, **Top Languages**, and **Top Contributions** card generation with extensive customization. The architecture has been recently refactored into a clear 3-tier sub-package structure (`core`, `github`, `rendering`), ensuring high supportability and extendability.

## Technical Stack
- **Language:** Python 3.13+
- **Dependency Management:** `uv`
- **CLI Framework:** `click`
- **HTTP Client:** `httpx` (via centralized `GitHubClient`, supports async)
- **Testing:** `pytest` with `pytest-cov`, `pytest-mock`, and `anyio` (for async tests)
- **Formatting/Linting:** `ruff` (lint + format), `mypy`
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
│   └── rank.py          # Ranking algorithms (User & Repo)
├── rendering/           # SVG generation and visual logic
│   ├── base.py          # Base SVG card renderer (shared)
│   ├── colors.py        # Color parsing and utilities
│   ├── contrib.py       # Contributor Card renderer
│   ├── icons.py         # SVG icons
│   ├── langs.py         # Top Languages Card renderer
│   ├── user_stats.py    # User Stats Card renderer
│   └── themes.py        # Theme definitions
├── cli.py               # CLI orchestration
├── __init__.py
└── __main__.py          # Module entry point
```

## Primary Dependencies
- `httpx>=0.27.0`: For GitHub API interaction (sync + async).
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
- **Repository Rank Simplification (2026-09-05):** Removed the `+`/`-` magnitude modifiers from the `contrib` card rank.
  - `calculate_repo_rank` now takes only `stars` and returns `S`, `A`, `B`, `C` or `D`.
  - Deleted the commit-count pipeline the modifier was the sole consumer of: the `object(expression: "HEAD")` GraphQL fragment, the `total_repo_commits` key and its back-fill branch.
  - Ranks are always one character, so the rank badge font size is a fixed 10px and the multi-character scaling was dropped. Released as 1.4.0.
- **Contribution Types Hardening (2026-08-09):** Follow-up on the filtering feature after an audit of shipped code against its artifacts. [Source: specs/003-filter-contrib-types]
  - `action.yml` no longer builds a command string and runs it through `eval`. All inputs arrive as environment variables and options are collected into a bash array passed directly to the CLI, which removes the shell-injection class entirely.
  - A test asserts the literal `--contrib-types` appears both in `action.yml` and in the `contrib` command's Click parameter list, so dropping the alias from the CLI or switching the Action to `--types` now fails the suite. The flag name is hardcoded in the test, so a rename must touch `src/cli.py`, `action.yml` and the test together.
  - `--help` now reports the `commits,prs` default; `README.md` documents the flag under CLI Usage.
  - Regression coverage added for PR state filtering against partial GraphQL payloads and for single-type query construction.
- **Contribution Type Filtering (2026-03-22):** Added `--types`/`--contrib-types` CLI flag and `contrib-types` GitHub Actions input to filter contributor card by type (`commits`, `prs`, `issues`, `reviews`). Default: `commits,prs`. Dynamic GraphQL query building. PR state filtering (OPEN/MERGED only). [Source: specs/003-filter-contrib-types]
- **Async HTTP Migration (2026-03-13):** Migrated HTTP boundary from `requests` to `httpx`.
  - Added async capabilities to `GitHubClient` for concurrent fetching.
  - Refactored `fetch_contributor_stats` to fetch years and avatars in parallel using `asyncio.gather`.
  - Updated test suite with `AsyncMock` and improved overall coverage to >90%.
- **Rework Ranking (2026-02-20):** Shifted `contrib` card ranking to be repository-centric. [Source: 002-rework-ranking]
  - Implemented `calculate_repo_rank` based on Stars + Repo Total Commits.
  - Renamed `calculate_rank` to `calculate_user_rank` for clarity.
- **Contributor Card (2026-02-08):** Added `contrib` subcommand to display top external contributions. [Source: 001-contributor-card]
  - Implemented `fetch_contributor_stats` with GraphQL filtering and sorting.
  - Added Base64 avatar embedding for repository owners using `<clipPath>` for circular masking.
  - Created `ContribCardConfig` and `rendering/contrib.py`.
- **Modular Refactor:** Split the flat structure into `core`, `github`, and `rendering` packages.
- **API Consolidation:** Introduced `GitHubClient` to manage all external requests.

## Future Work
- **Planned: Repository Card:** Implement a card type to display statistics for a specific repository (distinct from user contributions).
  - *Requirements:* New subcommand, `github/repo_fetcher.py`, and `rendering/repo.py`.
- Add support for GitHub Discussions Answered and Achievements.
- Improve SVG accessibility (aria-labels and screen reader support).
- Transition SVG generation to a templating engine (e.g., Jinja2) for better clarity.

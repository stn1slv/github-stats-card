# Merged Features Log

## Project Baseline - 2026-02-07
**What was added:**
- Core statistics fetching and rendering.
- Top languages fetching and rendering with 5 layouts.
- 50+ built-in themes.
- CLI interface with extensive customization.
- Internationalization support.
- GitHub Action integration.

**New Components:**
- `src/fetcher.py`, `src/langs_fetcher.py`
- `src/stats_card.py`, `src/langs_card.py`, `src/card.py`
- `src/cli.py`
- `src/rank.py`
- `src/themes.py`
- `src/config.py`

**Tasks Completed:** Initial project setup and feature implementation complete.

## Modular Architecture Refactoring - 2026-02-07
**What was added:**
- Refactored project into a modular sub-package structure (`core`, `github`, `rendering`).
- **`GitHubClient`**: Centralized API client for all GitHub interactions (REST/GraphQL).
- **`BaseConfig`**: Automated CLI argument parsing and list handling for all configuration classes.
- Modernized type hints (PEP 604) across the entire codebase.
- Improved animation control logic in the base card renderer.
- Expanded unit tests for utility functions and updated existing tests for modularity.

**New Structure:**
- `src/core/`: `config.py`, `constants.py`, `exceptions.py`, `i18n.py`, `utils.py`
- `src/github/`: `client.py`, `fetcher.py`, `langs_fetcher.py`, `rank.py`
- `src/rendering/`: `base.py`, `colors.py`, `icons.py`, `langs.py`, `stats.py`, `themes.py`

**Tasks Completed:** Architectural modernization and codebase cleanup.
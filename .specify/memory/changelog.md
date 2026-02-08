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

### [Contributor Card] - 2026-02-08
**Branch:** `001-contributor-card`
**Spec:** `specs/001-contributor-card/spec.md`

**What was added:**
- New `contrib` subcommand to generate a card showing top contributed repositories.
- Logic to fetch external contributions, sort by stars, and filter exclusions.
- Feature to download and embed repository owner avatars as Base64 images.
- Support for customizable repository limits, themes, and exclusion patterns.

**New Components:**
- `src/rendering/contrib.py`: SVG renderer for the contributor card.
- `src/core/config.py`: Added `ContribCardConfig` and `ContribFetchConfig`.
- `src/github/fetcher.py`: Updated with `fetch_contributor_stats`.

**Tasks Completed:** 22 tasks

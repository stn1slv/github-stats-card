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

**Tasks Completed:** 22/22 tasks

**Re-archived 2026-08-09:** verified against the implementation. Three residual items merged into `spec.md` (default card title, visual constants, `ContributorStats` entity). No new changelog entry created — this feature was already archived on 2026-02-08.

### [Async HTTP Migration] - 2026-03-13
**What was added:**
- Replaced `requests` with `httpx` for all API interactions.
- Added asynchronous methods (`async_graphql_query`, `async_fetch_image`) to `GitHubClient`.
- Refactored `fetch_contributor_stats` to use `asyncio.gather` for parallel fetching of contribution years and repository avatars.
- Updated test suite to handle async mocks and improved coverage for `GitHubClient` and fetchers (>90%).
- Added context manager support to `GitHubClient` for efficient connection pooling.

**New Components:**
- `src/github/client.py`: Async methods and context managers.
- `src/github/fetcher.py`: `async_fetch_contributor_stats`.

**Tasks Completed:** Migration to `httpx`, performance optimization via parallelism, test coverage improvements.

### [Rework Ranking] - 2026-02-20
**Branch:** `002-rework-ranking`
**Spec:** `002-rework-ranking`

**What was added:**
- Repository-centric ranking logic for Contributor Card (Stars + Repo Magnitude).
- Logic to fetch repository total commit count via GraphQL.
- Visual updates to support scaled rank text (e.g., S+).
- Renamed internal ranking function to `calculate_user_rank` to distinguish from new `calculate_repo_rank`.

**New Components:**
- `src/github/rank.py`: Added `calculate_repo_rank`, updated `calculate_user_rank`.
- `src/github/fetcher.py`: Updated fetch logic for repo magnitude.

**Tasks Completed:** 9/9 tasks

**Re-archived 2026-08-09:** verified against the implementation. Residual items merged into `spec.md` (full `ContributorRepo` field list, the "no global rank on repositories" invariant, concrete font-scale values). No new changelog entry created — this feature was already archived on 2026-02-20.

### [Filter Contribution Types] — 2026-03-22
**Branch:** `003-filter-contrib-types`
**Spec:** specs/003-filter-contrib-types

**What was added:**
- CLI flag `--types`/`--contrib-types` to filter contributor card by contribution type (commits, prs, issues, reviews).
- GitHub Actions input `contrib-types` with explicit default `commits,prs`.
- Dynamic GraphQL query building — only requested types are fetched.
- PR state filtering: only OPEN and MERGED PRs counted as contributions.
- Three-layer validation: CLI (BadParameter), dataclass (`__post_init__`), query builder (`_build_contrib_query`).
- `VALID_CONTRIB_TYPES` constant in `src/core/constants.py`.

**Modified Components:**
- `src/cli.py`: Added `--types` option to `contrib` command.
- `src/core/config.py`: Added `contribution_types` field to `ContribFetchConfig` with `__post_init__` validation.
- `src/core/constants.py`: Added `VALID_CONTRIB_TYPES` frozenset.
- `src/github/fetcher.py`: Dynamic `_build_contrib_query`, PR state filtering, type validation.
- `action.yml`: Added `contrib-types` input.

**Tasks Completed:** 30/30 tasks (20 original + T021–T030 from the 2026-08-09 follow-up)

#### Follow-up — 2026-08-09 (reconcile → converge → implement)
An audit of the shipped code against this feature's artifacts found the automation path was its least protected part.

- **`action.yml` forwards `--contrib-types`, the alias**, while every test exercised only `--types`. Renaming the flag would have passed CI and broken every Actions consumer. A test now checks the forwarded flag against Click's own parameter list.
- **Shell injection hardening:** `contrib-types` is passed via a `CONTRIB_TYPES` env var and dereferenced as a quoted variable, rather than interpolated into the string `eval` executes.
- `--help` now reports the `commits,prs` default; `README.md` documents the flag; the 100-node PR ceiling note moved out of the transmitted GraphQL string.
- Regression tests added for partial GraphQL payloads (field-level errors, `null`/missing PR nodes) and single-type query construction.
- Feature artifacts reconciled with shipped behaviour, including a repaired code fence in `plan.md`.

**Merged:** commit `2555f07`, merged to `main` as `c465483`.

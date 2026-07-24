# GitHub Stats Card

**Project Overview**

`github-stats-card` is a Python-based CLI tool designed to generate high-quality SVG statistics cards for GitHub profiles. It replicates the functionality of popular server-hosted stats cards but runs locally or via GitHub Actions, offering greater privacy, reliability, and customization. The project is architected as a modular application with a clear separation between data fetching (GitHub API), data processing, and SVG rendering.

**Main Technologies:**
*   **Language:** Python 3.13+
*   **Package Management:** `uv`
*   **CLI Framework:** `click`
*   **HTTP Client:** `httpx`
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
    uv run github-stats-card user-stats -u <username> -o stats.svg

    # Generate Top Languages Card
    uv run github-stats-card top-langs -u <username> -o langs.svg

    # Generate Contributor Card
    uv run github-stats-card contrib -u <username> -o contrib.svg
    ```

*   **Run Tests:**
    ```bash
    uv run pytest
    ```

*   **Linting & Formatting:**
    ```bash
    uv run ruff check src tests
    uv run ruff format src tests
    ```

*   **Type Checking:**
    ```bash
    uv run mypy src
    ```

**Development Conventions**

*   **Code Style:** Strict adherence to PEP 8, enforced by `ruff`.
*   **Type Hinting:** Mandatory use of modern Python type hints (PEP 604 style, e.g., `int | None`). `mypy` must pass in strict mode.
*   **Testing:** New features must include unit tests. The project maintains high test coverage.
*   **Modular Design:** Code must reside in the appropriate sub-package (`core`, `github`, or `rendering`). No circular dependencies.
*   **Contribution:** Follow the guidelines in `CONTRIBUTING.md`. Use Conventional Commits for commit messages.

## Development Rules

### Mandatory Validation (2026-03-13)
- **Rule:** After EACH code change (even small ones), the agent MUST run `make format lint test`.
- **Rationale:** Ensures that formatting is consistent, no linting regressions are introduced, and existing/new tests continue to pass. Verification is the only path to finality.
- **Gotcha:** Never skip this step before declaring a task complete. If `lint` fails due to fixable issues (like imports), use `make lint-fix`.

## Active Technologies
- Python 3.13+ (Managed by `uv`) + Click (CLI), httpx (API), Built-in XML/SVG libraries

## Architecture Decisions

### `GitHubClient` is the sole HTTP boundary (2026-02-22)
- **Decision:** `GitHubClient` catches all `httpx.HTTPError` in query/rest methods and re-raises as `APIError`. Image fetching methods intentionally swallow errors and return `None` to prevent missing avatars from breaking the entire card. Fetchers (`fetcher.py`, `langs_fetcher.py`) do not import `httpx`.
- **Rationale:** Prevents the HTTP library from leaking into domain logic.
- **Gotcha:** Tests must mock `GitHubClient.graphql_query` (or `GitHubClient.rest_get`), not `httpx.Client.post`. Mocking at the wrong layer breaks the abstraction and couples tests to the HTTP library.

### Config class hierarchy (2026-02-22)
- **Decision:** `CardStyleConfig(BaseConfig)` holds 11 shared visual fields (theme, colors, border, animations). All card render configs inherit from it. Fetch configs inherit directly from `BaseConfig`.
- **Rationale:** Eliminates duplication of common fields across `UserStatsCardConfig`, `LangsCardConfig`, `ContribCardConfig`. Inheritance chosen over composition because the fields are always used together and the hierarchy is flat (one level).
- **Gotcha:** Do not add fetch-related fields (e.g., `limit`, `exclude_repo`) to render configs. These belong in the corresponding `*FetchConfig` only — strict separation of fetch vs. render concerns.

### Config naming convention (2026-02-22)
- **Decision:** Config pairs are named `{Domain}CardConfig` / `{Domain}FetchConfig`: `UserStatsCardConfig`/`UserStatsFetchConfig`, `LangsCardConfig`/`LangsFetchConfig`, `ContribCardConfig`/`ContribFetchConfig`.
- **Rationale:** Makes the purpose of each config unambiguous at a glance and maintains symmetry as new card types are added.

### Backward-compatible CLI aliases via `AliasGroup` (2026-02-22)
- **Decision:** The `stats` command was renamed to `user-stats`. Old name kept via a custom `AliasGroup` Click subclass that maps aliases to canonical names before dispatch.
- **Rationale:** `AliasGroup` avoids duplicating the entire command definition. A simple `COMMAND_ALIASES` dict is the single source of truth for all aliases.
- **Gotcha:** Adding a new alias requires only a dict entry in `COMMAND_ALIASES` — do not register a second Click command.

### SVG Image Embedding (2026-02-08)
- **Decision:** External images (avatars) are Base64 encoded and embedded as data URIs. Circular masking is achieved using SVG `<clipPath>`.
- **Rationale:** Ensures self-contained SVGs that work in restricted environments (like GitHub READMEs) without external dependencies or tracking.
- **Gotcha:** Use a shared `<clipPath>` definition in `<defs>` and refer to it by ID (`url(#avatar-clip)`) to minimize SVG size.

### Project Magnitude Ranking (2026-02-20)
- **Decision:** Use **Repository Total Commits** as a proxy for "Project Magnitude" to modify repository ranks (+/-) in the contributor card.
- **Rationale:** Distinguishes between contributions to massive, established projects vs. small/new projects, even if star counts are similar.
- **Gotcha:** Fetch total commits via the `object(expression: "HEAD") { history { totalCount } }` fragment in GraphQL. Ensure this is fetched for all contribution types (Commits, PRs, Issues, Reviews) to avoid missing magnitude data when a user hasn't made direct commits.

### Contribution Filtering (2026-03-22)
- **Decision:** Allow users to filter contributor card content by type (`commits`, `prs`, `issues`, `reviews`) via `--types` flag. Default to `commits,prs`.
- **Rationale:** Reduces noise from non-code contributions (e.g., single issue opened) while highlighting primary impact areas.
- **Gotcha:** Validation is enforced in `ContribFetchConfig.__post_init__` to ensure the list is non-empty and valid before API calls.

### PR State Filtering (2026-03-22)
- **Decision:** For PR contributions, fetch individual nodes and count only those in `OPEN` or `MERGED` states.
- **Rationale:** Excludes unmerged closed PRs from contribution counts to provide a more accurate representation of actual repository impact.
- **Gotcha:** Requires fetching `nodes` instead of using `totalCount` for the `pullRequestContributionsByRepository` GraphQL field, which impacts query structure.

### Partial GraphQL Error Resilience (2026-07-24)
- **Decision:** Do not return early in `_async_process_year_contributions` when `"errors"` is present in GraphQL response dict `c_data`. Check for valid `c_data["data"]["user"]["contributionsCollection"]` payload instead.
- **Rationale:** GitHub GraphQL API frequently returns field-level `errors` (e.g. unresolvable repos, SAML restrictions, deleted nodes) alongside valid partial `data`. Discarding the response drops valid contributions for that year.
- **Gotcha:** Always use defensive null checks (e.g., `(item.get("contributions") or {}).get("nodes") or []`, `(node.get("pullRequest") or {}).get("state")`) when parsing partial payloads.

## Recent Changes
- [Partial GraphQL Error Resilience] (2026-07-24): Fixed `contrib` card fetching to process valid partial GraphQL data when top-level `errors` are present; bumped version to 1.1.9. [PR #14]
- [Contribution Filtering] (2026-03-22): Added `--types` flag to `contrib` card; default to `commits,prs`; implemented PR state filtering (OPEN/MERGED). [Source: specs/003-filter-contrib-types]
### [Code Quality Refactor] (2026-02-22)
- Renamed `stats` command to `user-stats`; `stats` kept as backward-compatible alias via `AliasGroup`.
- Extracted `CardStyleConfig` base class; unified fetcher APIs to accept config objects.

### [Rework Ranking] (2026-02-20)

### [Contributor Card] (2026-02-08)


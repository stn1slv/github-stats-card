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
    make setup   # uv sync --all-extras; the dev tooling lives in the `dev` extra
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
    make test
    ```

*   **Linting & Formatting:**
    ```bash
    make lint          # ruff check
    make format        # ruff format (rewrites files)
    make format-check  # ruff format --check, the CI gate
    ```

*   **Type Checking:**
    ```bash
    make type-check
    ```

> Prefer the `make` targets over bare `uv run`: each target passes `--extra dev` explicitly, because whether `uv run` preserves extras from an earlier sync has varied between uv versions.

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

### Contributor fetching uses `contributionsCollection` (2026-02-08)
- **Decision:** `fetch_contributor_stats` sources contributed repositories from `contributionsCollection` (per-year `*ContributionsByRepository` fields), sorting and slicing by stars in Python.
- **Rationale:** `contributionsCollection` exposes the per-type breakdown (commits, PRs, issues, reviews) that the `--types` filter and repo ranking both depend on.
- **Gotcha:** `specs/001-contributor-card/research.md` proposes `repositoriesContributedTo(...)` instead. That research decision was superseded during implementation and never updated. Do not "fix" the fetcher to match it: `repositoriesContributedTo` returns no contribution-type breakdown, which would break `--types` and the repo rank modifier.

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

### `CLAUDE.md` and `AGENTS.md` are one file (2026-08-09)
- **Decision:** `AGENTS.md` is the real agent knowledge file. `CLAUDE.md` is a symlink to it. The former `GEMINI.md` was renamed to `AGENTS.md` and no symlink was left under the old name.
- **Rationale:** `AGENTS.md` is the tool-neutral name and matches the repo's active integration (`agy`, per `.specify/integration.json`).
- **Gotcha:** Writing to "both `CLAUDE.md` and `AGENTS.md`" writes the same content twice. Edit one. `update-agent-context.sh` now deduplicates by resolved path for the same reason, and its `GEMINI_FILE` variable points at `AGENTS.md` so the `gemini` argument cannot resurrect a divergent `GEMINI.md`.

### `--contrib-types` alias is a released contract (2026-08-09)
- **Decision:** The `contrib` types option keeps two spellings, `--types` and `--contrib-types`, declared on one Click option. `action.yml` forwards the value using `--contrib-types`.
- **Rationale:** The alias is the production path for every GitHub Actions consumer, not a convenience. Only the CLI-facing `--types` was ever tested, so renaming or dropping the alias would have passed CI and broken all automation.
- **Gotcha:** `test_action_yml_forwards_a_flag_the_contrib_command_accepts` asserts the literal `--contrib-types` appears both in `action.yml` and in `cli.commands["contrib"].params`. It catches the two regressions that matter (dropping the alias from `src/cli.py`, or switching `action.yml` to `--types`), but the flag name is hardcoded in the test, so renaming the option requires updating three places: `src/cli.py`, `action.yml`, and the test. A coordinated rename of only the first two still fails.

### `action.yml` builds an argument array, never a command string (2026-08-09)
- **Decision:** Every input reaches the "Generate card" step as an environment variable declared under `env:`. The step collects options into a bash array (`ARGS+=(--flag "$VALUE")`) and invokes `github-stats-card "${ARGS[@]}"`. There is no `CMD` string and no `eval`.
- **Rationale:** The step previously interpolated `${{ inputs.* }}` straight into a string it then ran through `eval`, so a value containing a single quote escaped the quoting and executed arbitrary shell. This is a published action, so a consumer can legitimately wire an input to untrusted data such as `custom-title: ${{ github.event.issue.title }}`, which made the injection reachable by an attacker rather than only by the workflow author.
- **Gotcha:** Do not reintroduce `eval` or string concatenation when adding an option. Add an `env:` entry and an `ARGS+=(...)` line. `test_action_yml_forwards_a_flag_the_contrib_command_accepts` asserts that no non-comment line in `action.yml` contains `eval` as a whole word, so a regression fails the suite.

### Token Scope Warning on Empty Contrib Results (2026-08-09)
- **Decision:** When the `contrib` card returns zero repositories and the token starts with `ghs_`, the CLI prints a stderr hint directing the user to a PAT with `read:user` scope. Keep this behaviour; it is deliberate, not leftover debugging.
- **Rationale:** The Actions default `GITHUB_TOKEN` cannot read cross-repository contribution breakdowns, so the card silently renders empty. Without the hint the failure looks like "the user has no contributions" rather than a scope problem, which was the single most common source of confusion.
- **Gotcha:** The hint is keyed off the `ghs_` prefix, so it never fires for a PAT. It writes to stderr so the SVG on stdout stays clean. Surfaced by `/speckit-converge` as unrequested code (T029) and justified here rather than removed.

### `resolve_color` is the only place a gradient collapses (2026-08-16)
- **Decision:** `parse_color` returns a `list` for a gradient spec, and only the card background renders it as a real `<linearGradient>`. Every other colour slot (title, text, icon, border, ring) must pass through `rendering.colors.resolve_color`, which returns the first colour stop with a `#` prefix.
- **Rationale:** `base.py` and `langs.py` had each grown their own inline `isinstance(..., list)` collapse and had already drifted apart: one added the `#`, the other did not. Every slot that had neither interpolated the list into the SVG as its Python repr (`fill: ['90', 'ff0000', '00ff00']`), which is invalid CSS that silently falls back to the browser default.
- **Gotcha:** Never interpolate a value straight out of `get_card_colors` into markup. It is typed `str | list[str]`, and `mypy` will not catch the list case because f-strings accept anything. `bg_color` is the single exception and is handled by `format_gradient`.

### Card width floors are measured, never hardcoded (2026-08-16)
- **Decision:** `--card-width` is a request, not a guarantee. `render_user_stats_card` and `render_top_languages` compute the narrowest width the content actually needs using `core.utils.measure_text`, then clamp up to it.
- **Rationale:** Stat values, the rank circle and the two-column legends sit at fixed offsets, so a narrow card printed content off the canvas or on top of the ring. A single constant cannot work: a short-format `6.6k` needs ~270px of value column while a long-format `12,345,678` needs ~330px, so any fixed floor is either too aggressive for the common case or too small for the long one. Two successive fixed floors (420, then 340) were both measured wrong before this approach.
- **Gotcha:** Use `math.ceil` on the derived floor, never `int()`. Both call sites later floor when halving the body into columns, so truncating gives back the fraction of a pixel the content needed and reintroduces the overlap.
- **Limit:** `measure_text` is `len(text) * font_size * 0.6`, a monospace approximation of proportional bold Segoe UI. The floors and the tests both use it, so the tests prove the renderer agrees with the estimate, not that a browser will never overlap. Wide glyphs, bold digits and non-Latin scripts can still exceed it, and only the value column is measured, not the labels. Treat it as protection against the common cases, not a guarantee.

### Fetch degradation logs, it never returns silently (2026-08-16)
- **Decision:** Fetchers that continue with partial data (pagination cut short, a search fallback, a dropped contribution year) emit `logger.warning` with the cause interpolated into the message. `cli._configure_logging` attaches a stderr handler to the package logger.
- **Rationale:** These paths previously swallowed `APIError` and rendered a plausible card with wrong numbers, which is worse than failing because the SVG gets committed to a README.
- **Gotcha:** Three traps here, all of which were live at some point. (1) Put the cause in the *message*; the formatter does not render `extra=` fields, so context passed only that way is invisible. (2) Derive the logger name from `__package__`, not `__name__` — under `python -m src.cli` the module's `__name__` is `"__main__"` and the handler lands on a logger no fetcher writes to. (3) Do not use `logging.basicConfig`: it is a no-op once the root logger has a handler, and raising the root level turns on `httpx` debug output.

### `action.yml` checks out the caller's own ref (2026-08-16)
- **Decision:** The self-checkout step uses `repository: ${{ github.action_repository }}` and `ref: ${{ github.action_ref }}`. Neither is hardcoded.
- **Rationale:** Without `ref` the checkout takes the default branch, so `uses: ...@v1.1.9` ran whatever was on `main` and no release was reproducible. Without `repository` a fork consumer looks for its own tag in the upstream repository and fails.
- **Gotcha:** Both context values are empty for a local `uses: ./`, where `actions/checkout` then defaults to the caller's repository at its current commit — that is the wanted behaviour, so do not add a fallback. They are also unreliable when this action is invoked from inside another composite action. `test_action_yml_checks_out_the_ref_the_caller_pinned` asserts both, and that no hardcoded repository name remains.

## Recent Changes
- [Review Remediation] (2026-08-16): Fixed action release pinning, gradient colour leaks, `k_formatter` precision, card width overlap, silent fetch degradation, and exception self-wrapping; implemented `--rank-icon` and a real `donut-vertical` layout; added CI, `--debug`, input validation and `CHANGELOG.md`. Tests 201 -> 264.
- [Token Scope Warning] (2026-08-09): Documented the existing `contrib` empty-result PAT hint as an intentional decision; hardened `action.yml` to pass `contrib-types` via `env` instead of direct interpolation. [Source: specs/003-filter-contrib-types Phase 6]
- [Partial GraphQL Error Resilience] (2026-07-24): Fixed `contrib` card fetching to process valid partial GraphQL data when top-level `errors` are present; bumped version to 1.1.9. [PR #14]
- [Contribution Filtering] (2026-03-22): Added `--types` flag to `contrib` card; default to `commits,prs`; implemented PR state filtering (OPEN/MERGED). [Source: specs/003-filter-contrib-types]
### [Code Quality Refactor] (2026-02-22)
- Renamed `stats` command to `user-stats`; `stats` kept as backward-compatible alias via `AliasGroup`.
- Extracted `CardStyleConfig` base class; unified fetcher APIs to accept config objects.

### [Rework Ranking] (2026-02-20)

### [Contributor Card] (2026-02-08)


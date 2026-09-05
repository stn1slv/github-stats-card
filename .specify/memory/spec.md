# Project Specification: GitHub Stats Card

## Overview
A Python CLI tool that generates beautiful GitHub stats cards as SVG images for your profile README. It fetches data from GitHub's GraphQL and REST APIs and renders them locally using customizable themes.

## User Stories
- **US-001:** As a GitHub user, I want to display my repository statistics (stars, commits, PRs, etc.) on my profile in a visually appealing way.
- **US-002:** As a developer, I want to showcase my most used programming languages to highlight my expertise.
- **US-003:** As a user, I want to customize the look of my stats cards with themes and custom colors to match my profile aesthetic.
- **US-004:** As a GitHub Actions user, I want to automate the generation of these cards daily/weekly.
- **US-005:** As an international user, I want the stats cards to support my local language.
- **US-006:** As a GitHub user, I want to generate a card showing the most popular repositories I've contributed to, to showcase my impact.
- **US-007:** As a user, I want to customize the number of repositories displayed on the contributor card.
- **US-008:** As a user, I want to apply existing themes to the contributor card for consistency.
- **US-009:** As a user, I want clear feedback if I have no contributions or if I provide invalid limits.
- **US-010:** As a user, I want the contributor card to rank repositories by their popularity, so that contributing to a widely used project is recognized with a high rank regardless of my commit count. (Repository magnitude was part of this story until 2026-09-05; the rank is now the star count alone.)
- **US-011:** As a user generating a contributor card via the CLI, I want to specify which types of contributions to consider (e.g., only commits and pull requests) so that my card highlights only my active code contributions. [Source: specs/003-filter-contrib-types]
- **US-012:** As a user running card generation via GitHub Actions, I want to configure contribution types via workflow inputs so that my profile is automatically updated with filtered contribution data. [Source: specs/003-filter-contrib-types]
- **US-013:** As a user whose history spans repositories the provider cannot fully resolve (deleted repos, SSO-restricted orgs), I want the card to still reflect the contributions that were returned, so a single unresolvable entry does not blank out an entire year. [Source: specs/003-filter-contrib-types]

## Functional Requirements

### Core System
- **FR-001: Data Fetching**
  - Fetch user statistics (stars, commits, PRs, issues, reviews, contributions) using GitHub GraphQL API.
  - Fetch language usage data from repositories with configurable weighting (size vs. count).
  - Support Personal Access Token (PAT) for authentication.
  - **FR-001.1: GitHubClient:** Centralized handling of GraphQL and REST requests with consistent headers and timeouts.
- **FR-002: CLI Interface**
  - Provide a CLI with subcommands for each card type (`stats`, `top-langs`, `contrib`).
  - Support global flags for customization (themes, colors, output path).
  - **FR-002.1: BaseConfig:** Automatic parsing of comma-separated lists and filtering of `None` values from CLI args.
- **FR-003: Internationalization**
  - Support multiple locales for stat labels (e.g., "Stars" -> "Étoiles").
- **FR-004: GitHub Enterprise Support**
  - Support custom GitHub API and GraphQL endpoints via environment variables.

### Card Type: Stats Card
- **FR-005: User Stats Calculation**
  - Aggregate total commits, PRs (total/merged), issues, reviews, and stars.
  - **User Ranking System:** Calculate a user rank (S+, S, A, B, etc.) via `calculate_user_rank`, a percentile-based algorithm over weighted contributions. This is deliberately distinct from the contributor card's `calculate_repo_rank` and its output must stay stable. [Source: 002-rework-ranking]
- **FR-006: Stats Rendering**
  - Render a vertical list of statistics with optional icons.
  - Display the calculated rank in a dedicated visual circle.
  - Allow hiding specific stats or the rank circle.

### Card Type: Top Languages Card
- **FR-007: Language Aggregation**
  - Aggregate language usage across all public repositories.
  - **Weighting:** Support "Size-Only", "Balanced" (70/30), "Expertise" (50/50), and "Diversity" (40/60) weighting strategies for ranking languages.
  - Exclude specific repositories or languages via CLI flags.
- **FR-008: Language Rendering**
  - Support 5 distinct layouts:
    1. **Normal:** Vertical list with progress bars.
    2. **Compact:** Horizontal stacked bar with legend (matches Stats Card width).
    3. **Donut:** Circular chart with legend.
    4. **Donut-Vertical:** Circular chart with vertical legend.
    5. **Pie:** Pie chart with legend.
  - Display percentage or byte count.

### Card Type: Contributor Card
- **FR-009: Contribution Data Fetching**
  - Fetch repositories where the user is a contributor (Commits, Pull Requests, Issues, Reviews) over the last 5 years.
  - **Filtering:** Filter out user-owned repositories and private repositories. Support manual exclusion via CLI (wildcards supported).
  - **Sorting:** Sort repositories by star count (descending).
- **FR-010: Contributor Rendering**
  - Render a list of top repositories (default 10) with repository name and repository-specific rank.
  - **Default Title:** "Top Contributions", overridable via `--custom-title`. [Source: 001-contributor-card]
  - **Avatars:** Fetch and embed repository owner's avatar (Base64 encoded) as a circular icon next to the repository name.
  - **Fallback:** Use a generic placeholder icon if avatar fetching fails.
  - **Visuals:** Match the visual style of existing cards (fonts, padding, themes). Default card width 467px (matching the stats card), fixed row height 35px, owner avatars 20x20px circular. [Source: 001-contributor-card]
  - **Rank Text Size:** 10px, fixed, so the rank fits the existing circle. Ranks are always one character. The earlier 8px multi-character scaling was removed with the rank modifiers on 2026-09-05; restoring a multi-character rank means restoring the scaling too. [Source: 002-rework-ranking, superseded 2026-09-05]
- **FR-011: Repository Ranking Logic** [Source: 002-rework-ranking]
  - **Base Rank:** Determined by Repository Star Count:
    - `S`: > 10,000 stars.
    - `A`: 1,001 - 10,000 stars.
    - `B`: 101 - 1,000 stars.
    - `C`: 11 - 100 stars.
    - `D`: 0 - 10 stars.
  - **No Modifier:** The star count is the whole rank. The `+` (>5k repository commits) and `-` (1-99) modifiers, and the commit-count lookup that produced them, were removed on 2026-09-05 because the modifier was the only consumer of a per-repository GraphQL field. Do not restore them from `specs/002-rework-ranking`, which still documents them as current. [Source: 002-rework-ranking, superseded 2026-09-05]
  - **Invariant:** The user's global rank MUST NOT be applied to individual repositories. Repository ranks come from `calculate_repo_rank(stars)`; the global rank comes from `calculate_user_rank`. Conflating the two was the defect this feature fixed. [Source: 002-rework-ranking]
- **FR-012: Repository Exclusion Wildcards** [Source: 001-contributor-card]
  - Repository exclusion MUST support wildcard (*) matching and owner-omitted matching (e.g., "awesome-*" matches any repo starting with "awesome-" regardless of owner). Matching MUST be case-insensitive.
- **FR-013: Contribution Type Filtering (CLI)** [Source: specs/003-filter-contrib-types]
  - System MUST parse the comma-separated `--types` flag into a list, validating against allowed values (`commits`, `prs`, `issues`, `reviews`).
- **FR-014: Contribution Type Defaults** [Source: specs/003-filter-contrib-types]
  - System MUST default to including `commits` and `prs` if the `--types` flag is omitted.
- **FR-015: Dynamic GraphQL Query Building** [Source: specs/003-filter-contrib-types]
  - System MUST update the data fetching process to only request data for the specified contribution types, building the GraphQL query dynamically.
- **FR-016: GitHub Actions Contribution Types Input** [Source: specs/003-filter-contrib-types]
  - System MUST expose a `contrib-types` input parameter in `action.yml` with a default of `commits,prs`.
- **FR-017: PR State Filtering** [Source: specs/003-filter-contrib-types]
  - When `prs` are selected, the system MUST only count Pull Requests in `OPEN` or `MERGED` state, excluding `CLOSED` (unmerged) pull requests.
- **FR-018: Contribution Types Option Spelling is a Released Contract** [Source: specs/003-filter-contrib-types]
  - Both `--types` and `--contrib-types` MUST remain valid spellings of the same option.
  - `action.yml` forwards the setting using **`--contrib-types`**, so that alias is the production path for automation, not an internal convenience. It MUST NOT be removed or renamed without a corresponding `action.yml` change, and the wiring MUST stay covered by tests.
- **FR-019: Partial Provider Response Handling** [Source: specs/003-filter-contrib-types]
  - When the provider returns field-level `errors` alongside a usable partial payload, the system MUST process the contributions present in that payload rather than discarding the response.
  - Parsing MUST be defensive: absent `contributions`, absent `nodes`, and `null` `pullRequest` entries are skipped, never counted.
- **FR-020: Discoverable CLI Defaults** [Source: specs/003-filter-contrib-types]
  - The CLI MUST make the default set of contribution types (`commits,prs`) visible in its own `--help` output.

## Non-Functional Requirements
- **NFR-001: Performance** - Card generation should be fast (fetching data is the bottleneck, mitigated by parallel async fetching using `httpx` and `asyncio`).
- **NFR-002: Reliability** - Handle API errors and rate limiting gracefully.
- **NFR-003: Extensibility** - Easy to add new card types, themes, or layouts due to modular 3-tier sub-package structure.

## Key Entities

### StatsCardConfig (`src/core/config.py`)
Configuration for stats card rendering:
- `theme`, `colors` (title, text, icon, bg, border, ring)
- `hide`, `show` (specific stats)
- `hide_rank`, `show_icons`
- `include_all_commits`

### LangsCardConfig (`src/core/config.py`)
Configuration for top languages card rendering:
- `layout` (normal, compact, donut, etc.)
- `langs_count` (max languages to show)
- `weighting` (size vs count weights)
- `stats_format` (percentages vs bytes)

### ContribCardConfig (`src/core/config.py`)
Configuration for contributor card rendering:
- `limit` (max repositories to show)
- `exclude_repo` (list of patterns to exclude)
- `theme`, `colors` (title, text, bg, border)
- `hide_border`, `card_width`, `border_radius`, `disable_animations`

### ContribFetchConfig (`src/core/config.py`) [Updated: specs/003-filter-contrib-types]
Configuration for fetching contributor data:
- `username`, `token`, `limit`, `exclude_repo`
- `contribution_types: list[str]` — Types to fetch. Allowed: `commits`, `prs`, `issues`, `reviews`. Default: `["commits", "prs"]`. Validated in `__post_init__` against `VALID_CONTRIB_TYPES`.

### VALID_CONTRIB_TYPES (`src/core/constants.py`) [Source: specs/003-filter-contrib-types]
`frozenset[str]` containing `{"commits", "prs", "issues", "reviews"}`.

### UserStats (`src/github/fetcher.py`)
TypedDict containing raw statistics from GitHub API.

### Language (`src/github/langs_fetcher.py`)
Dataclass representing an aggregated programming language.

### ContributorRepo (`src/github/fetcher.py`) [Updated: 002-rework-ranking]
TypedDict representing a contributed repository:
- `name` (`owner/repo`), `stars`, `rank_level`, `avatar_b64` (`str | None`)
- `commits`, `prs`, `issues`, `reviews` (`int`): the user's per-type contribution counts for that repository. These are the counters populated selectively by the `--types` filter (FR-013).
- Note: `rank_level` is computed from `stars` alone. The `total_repo_commits` intermediate value was removed on 2026-09-05 along with the rank modifiers.

### ContributorStats (`src/github/fetcher.py`) [Source: 001-contributor-card]
TypedDict wrapping the fetch result: `repos`, the sorted and sliced list of `ContributorRepo`. Returned by `fetch_contributor_stats` / `async_fetch_contributor_stats` and consumed by `render_contrib_card`.

## Architecture

### Data Flow by Card Type

**1. Stats Card Flow:**
`cli.user_stats` (alias `stats`) -> `github.fetcher.fetch_user_stats` -> `github.client.graphql_query` -> `github.rank.calculate_user_rank` -> `rendering.user_stats.render_user_stats_card` -> `rendering.base.render_card` -> Output File

**2. Top Languages Card Flow:**
`cli.top_langs` -> `github.langs_fetcher.fetch_top_languages` -> `github.client.graphql_query` -> `rendering.langs.render_top_languages` -> `rendering.base.render_card` -> Output File

**3. Contributor Card Flow:**
`cli.contrib` -> `github.fetcher.fetch_contributor_stats` (runs async loop) -> `github.fetcher.async_fetch_contributor_stats` -> `github.client.async_graphql_query` & `github.client.async_fetch_image` (concurrently) -> `github.rank.calculate_repo_rank` -> `rendering.contrib.render_contrib_card` -> `rendering.base.render_card` -> Output File

### Layered Architecture (Sub-packages)
- **Core (`src/core/`):** Fundamental logic, constants, and shared configuration.
- **GitHub (`src/github/`):** API integration, data retrieval, and domain logic (ranking).
- **Rendering (`src/rendering/`):** SVG generation, CSS styling, and layout management.
- **Entry Point:** `src/cli.py` (CLI orchestration).

## Edge Cases and Error Handling
- Invalid GitHub Token (401 Unauthorized)
- User Not Found (404 Not Found)
- GitHub API Rate Limiting
- Missing Language Colors (fallback to default)
- Repositories with no languages
- Avatar fetch failures (fallback to placeholder)
- No external contributions found
- Invalid contribution type in `--types` flag (validation error before API call) [Source: specs/003-filter-contrib-types]
- Empty `--types` flag (validation error: at least one type required) [Source: specs/003-filter-contrib-types]
- PR contributions exceeding 100 nodes per repo/year (silently undercounted; documented limitation) [Source: specs/003-filter-contrib-types]
- Field-level GraphQL errors returned alongside valid data (partial payload is processed, not discarded) [Source: specs/003-filter-contrib-types]
- Unresolvable or `null` `pullRequest` nodes within a partial payload (skipped, remaining OPEN/MERGED PRs still counted) [Source: specs/003-filter-contrib-types]

---

### Revision: Archival Sync 2026-08-09
- Re-archival of `specs/001-contributor-card` (originally archived 2026-02-08) merged three residual items: the default card title, the contributor card visual constants (467px width, 35px rows, 20x20px avatars), and the `ContributorStats` entity. All other 001 content was already present and was not duplicated.
- Archival of `specs/003-filter-contrib-types` follow-up work (reconcile + converge + implement, 2026-08-09) added US-013, FR-018 through FR-020, and two partial-payload edge cases. The original 2026-03-22 archival remains valid; this covers what the feature gained afterwards.
- Re-archival of `specs/002-rework-ranking` (originally archived 2026-02-20) merged four residual items: the full `ContributorRepo` field list including the per-type contribution counters, the invariant that the user's global rank must never be applied to individual repositories, the concrete rank font-scale values, and the explicit `calculate_user_rank` / `calculate_repo_rank` distinction. All other 002 content was already present and was not duplicated.

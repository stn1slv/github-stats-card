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
- **FR-005: Stats Calculation**
  - Aggregate total commits, PRs (total/merged), issues, reviews, and stars.
  - **Ranking System:** Calculate a user rank (S+, S, A, B, etc.) using a percentile-based algorithm based on weighted contributions.
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
  - Render a list of top repositories (default 10) with repository name and user rank level.
  - **Avatars:** Fetch and embed repository owner's avatar (Base64 encoded) as a circular icon next to the repository name.
  - **Fallback:** Use a generic placeholder icon if avatar fetching fails.
  - **Visuals:** Match the visual style of existing cards (fonts, padding, themes).

## Non-Functional Requirements
- **NFR-001: Performance** - Card generation should be fast (fetching data is the bottleneck).
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
- `theme`, `colors`, `hide_border`, `card_width`

### UserStats (`src/github/fetcher.py`)
TypedDict containing raw statistics from GitHub API.

### Language (`src/github/langs_fetcher.py`)
Dataclass representing an aggregated programming language.

### ContributorRepo (`src/github/fetcher.py`)
TypedDict representing a contributed repository with name, stars, rank level, and base64 avatar.

## Architecture

### Data Flow by Card Type

**1. Stats Card Flow:**
`cli.stats` -> `github.fetcher.fetch_stats` -> `github.client.graphql_query` -> `github.rank.calculate_rank` -> `rendering.stats.render_stats_card` -> `rendering.base.render_card` -> Output File

**2. Top Languages Card Flow:**
`cli.top_langs` -> `github.langs_fetcher.fetch_top_languages` -> `github.client.graphql_query` -> `rendering.langs.render_top_languages` -> `rendering.base.render_card` -> Output File

**3. Contributor Card Flow:**
`cli.contrib` -> `github.fetcher.fetch_contributor_stats` -> `github.client.graphql_query` -> `github.client.fetch_image` -> `rendering.contrib.render_contrib_card` -> `rendering.base.render_card` -> Output File

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

# Research: Filter Contribution Types

## Feature Context
The feature requires filtering the specific contribution types (commits, pull requests, issues, reviews) queried from the GitHub GraphQL API to calculate the contributor card rankings.

## Decisions

### 1. Handling CLI and Actions Input
- **Decision:** Use a comma-separated string for the CLI flag (`--types` / `--contrib-types`) and GitHub Action input (`contrib-types`), which will be parsed into a `list[str]`. 
- **Rationale:** Standard practice for CLI tools to represent multiple enum-like options. It easily maps to environment variables and YAML inputs for GitHub actions. 
- **Alternatives considered:** Multiple flag declarations (e.g., `--type commits --type prs`), but comma-separated is cleaner for GitHub actions configuration.

### 2. Default Values
- **Decision:** If the `--types` parameter is omitted, default to `commits` and `prs`: `["commits", "prs"]`.
- **Rationale:** Focuses on the most common indicator of code contribution (commits and merged/open PRs) by default. Users who want the broad net can explicitly specify `commits,prs,issues,reviews`.
- **Alternatives considered:** Defaulting to all four types. Rejected because it often includes "noisy" repositories where a user only opened a single issue.

### 3. Modifying GraphQL Query
- **Decision:** Dynamically construct the GraphQL query string in `src/github/fetcher.py` based on the requested `contribution_types` in the `ContribFetchConfig`. Exclude the sub-queries (e.g., `issueContributionsByRepository`) entirely if they are not in the list.
- **Rationale:** Reduces network payload size and GitHub API processing time.
- **Alternatives considered:** Always fetch all data and filter in memory. Rejected because it wastes API bandwidth and GitHub's processing time for data the user explicitly requested to ignore.

### 4. Input Validation
- **Decision:** Validate the parsed list items against a predefined set of valid choices (`{"commits", "prs", "issues", "reviews"}`). Raise a `click.BadParameter` or custom `ValueError` if an invalid type is provided.
- **Rationale:** Fail fast before initiating network requests to GitHub.

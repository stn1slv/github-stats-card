# Data Model: Filter Contribution Types

## Entities

### `ContribFetchConfig` (Update)
The configuration object representing data fetching parameters for the Contributor Card.

**Added Field:**
- `contribution_types`: `list[str]`
  - **Description**: List of contribution types to include.
  - **Validation**: Must only contain items from `{"commits", "prs", "issues", "reviews"}`.
  - **Default**: `["commits", "prs"]`

## Constants (Update)

### `VALID_CONTRIB_TYPES` (New)
- **Type**: `frozenset[str]` or `tuple[str, ...]`
- **Value**: `{"commits", "prs", "issues", "reviews"}`
- **Location**: `src/core/constants.py` (or defined locally in `config.py` / `cli.py` depending on scope).

## Validation Rules
1. When parsing CLI arguments (`src/cli.py` and `src/core/config.py`), split the comma-separated string on `,`, strip whitespace.
2. Ensure every resulting string is in `VALID_CONTRIB_TYPES`.
3. If not, raise an error.

## API Contracts / GraphQL Interaction

The GraphQL query executed in `src/github/fetcher.py` (`_async_process_year_contributions`) will be dynamically adjusted. 

Only inject the following blocks if their corresponding type is present in `contribution_types`:

*   For `commits`:
    ```graphql
    commitContributionsByRepository(maxRepositories: 100) { ... }
    ```
*   For `prs` (fetches nodes rather than `totalCount`, so state can be inspected):
    ```graphql
    pullRequestContributionsByRepository(maxRepositories: 100) {
      ...repoDetails
      contributions(first: 100) {
        nodes { pullRequest { state } }
      }
    }
    ```
    Only nodes whose `state` is `OPEN` or `MERGED` are counted. The `first: 100` ceiling means a repository with more than 100 pull requests by the user in a single year is undercounted.
*   For `issues`:
    ```graphql
    issueContributionsByRepository(maxRepositories: 100) { ... }
    ```
*   For `reviews`:
    ```graphql
    pullRequestReviewContributionsByRepository(maxRepositories: 100) { ... }
    ```

## Response Parsing

Responses may be partial: field-level `errors` can accompany a usable `data` payload. Parsing keys off the presence of a `contributionsCollection`, not the absence of `errors`. Every level is read defensively, since `contributions`, `nodes` and individual `pullRequest` entries may each be absent or `null` in a partial response.
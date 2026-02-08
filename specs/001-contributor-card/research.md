# Research & Design: Add contributor card

**Feature**: `001-contributor-card` | **Date**: 2026-02-07

## 1. GraphQL Data Fetching

### Problem
We need to fetch repositories a user has contributed to, excluding their own, and sort them by stars.
The `repositoriesContributedTo` connection is the correct source.

### Findings
- **Query**: `user(login: "...") { repositoriesContributedTo(includeUserRepositories: false, first: 100, orderBy: {field: STARGAZERS, direction: DESC}) { ... } }`
- **Sorting**: GitHub API `repositoriesContributedTo` *does* support `orderBy`. However, the available fields are typically `CREATED_AT`, `UPDATED_AT`, `PUSHED_AT`. `STARGAZERS` is often *not* available on this specific connection (unlike `search` or generic `repositories`).
- **Strategy**: To ensure we get the *actual* top repositories by stars, we should fetch a larger batch (e.g., `first: 100`) and perform the sorting and slicing in Python. This guarantees accuracy even if the API sort is limited.
- **Fields Needed**:
  - `nameWithOwner` (for "owner/repo" display)
  - `stargazers { totalCount }`
  - `owner { avatarUrl }`
  - `isPrivate` (to filter out private repos client-side if API doesn't strictly enforce it, though we'll use `privacy: PUBLIC` if available).

### Decision
- **Fetch Strategy**: Fetch `first: 100` repositories using `repositoriesContributedTo(includeUserRepositories: false, privacy: PUBLIC)`.
- **Sort Strategy**: Sort by `stargazers.totalCount` descending in Python.
- **Limit**: Slice the top N results after sorting.

## 2. SVG Image Embedding

### Problem
We need to display circular owner avatars in the SVG without external dependencies or tracking pixels.

### Findings
- **Embedding**: Use `base64` encoding of the image data.
- **Format**: `<image href="data:image/png;base64,..." ... />`.
- **Circular Masking**:
  - **Option A**: CSS `border-radius: 50%` on `<image>`. *Risk*: Limited support in some SVG viewers (e.g. older tools).
  - **Option B**: `<clipPath id="circle"><circle ... /></clipPath>` applied to `<image clip-path="url(#circle)">`. *Verdict*: Standard SVG 1.1, widely supported.

### Decision
- **Embedding**: Fetch image -> `base64` encode -> Embed as Data URI.
- **Masking**: Use `<defs><clipPath id="avatar-clip">...</clipPath></defs>` and apply to images.
- **Optimization**: Reuse the same `clipPath` definition for all rows to save bytes.

## 3. Configuration & Data Model

### Data Structures
- **`ContribCardConfig`**: Inherits `BaseConfig`.
  - `limit`: int = 10
  - `exclude_repos`: list[str] = []
- **`Repository`**: Existing classes might be reusable, but we need `owner_avatar_url`.
  - Check `src/github/fetcher.py`. Likely need a lightweight dict or dataclass for the renderer.

## 4. Error Handling
- **Avatar Fetch**: If `requests.get(avatar_url)` fails, use a built-in base64 string of a generic "GitHub Octocat" or "User" icon.
- **Empty State**: If 0 contributions found, render a specific "No contributions found" message in the card body.

## 5. Caching
- **Avatars**: No persistent caching planned for this iteration (CLI run is ephemeral).
- **API**: Standard `GitHubClient` caching logic (if any) applies.

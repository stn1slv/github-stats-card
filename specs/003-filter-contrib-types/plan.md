# Implementation Plan: Filter Contribution Types for Contributor Card

**Branch**: `003-filter-contrib-types` | **Date**: 2026-03-22 | **Spec**: [specs/003-filter-contrib-types/spec.md](spec.md)
**Input**: Feature specification from `/specs/003-filter-contrib-types/spec.md`

## Summary

Add an optional configuration parameter to the Contributor Card to specify exactly which types of contributions (commits, PRs, issues, code reviews) should be fetched and ranked. This will be configurable via a new CLI flag `--types` (or `--contrib-types`) and via a GitHub Actions input parameter `contrib-types`.

## Technical Context

**Language/Version**: Python 3.13+ (Managed by `uv`)
**Primary Dependencies**: Click (CLI), httpx (API), Built-in XML/SVG libraries
**Testing**: `pytest` (Unit), `pytest-mock` (API mocking)
**Linting/Formatting**: `ruff` (Lint+Format), `mypy` (Strict Typing)
**Project Structure**: `src/` layout with `tests/`
**Performance Goals**: Decrease or maintain local generation time (fetching fewer types may slightly improve GraphQL response times).
**Constraints**: Ensure safe default (default includes `commits` and `prs`). Secure token handling remains unchanged.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- [x] **I. CLI-First**: Does this feature expose functionality via flags/args in `src/cli.py`? Yes, adding `--types`.
- [x] **II. Local Generation**: Does it avoid external dependencies for rendering? Yes, only changes data fetching.
- [x] **III. Modern Python**: Is it typed (`mypy` strict) and `ruff` compliant? Yes, updating dataclasses.
- [x] **IV. Visuals**: Is the SVG output accessible and themeable? Yes, visual output is unaffected.
- [x] **V. Testing**: Are unit tests included? Yes, test_cli and test_fetcher will be updated.

## Project Structure

### Documentation (this feature)

```text
specs/003-filter-contrib-types/
├── plan.md              # This file
├── research.md          # Research & Design
├── data-model.md        # Data Structures & Config
├── quickstart.md        # Usage Guide
└── tasks.md             # Implementation Tasks
```

### Source Code

```text
src/
├── core/                
│   ├── config.py        # Update ContribFetchConfig
│   └── utils.py         # Update arg parsing if necessary
├── github/              
│   └── fetcher.py       # Update GraphQL query construction and PR state filtering
└── cli.py               # Add Click option for --types/--contrib-types

tests/
├── test_cli.py          # Add tests for new flag parsing
├── test_fetcher.py      # Mocked API tests for conditional queries
└── test_contrib_card.py # Integration test behavior

action.yml               # Add `contrib-types` input
```

### Technical Detail: PR State Filtering
The system dynamically adjusts the GraphQL query for `prs` to fetch pull request nodes and their states. The parsing logic then iterates through these nodes to count only `OPEN` and `MERGED` pull requests, ensuring that unmerged closed PRs do not contribute to the repository count. Node retrieval is capped at `contributions(first: 100)` per repository per year, so a repository with more than 100 pull requests in a single year is undercounted.

### Integration Contracts
- **CLI surface**: the option is declared once in `src/cli.py` with two spellings, `--types` and `--contrib-types`, both bound to the `contribution_types` parameter.
- **Automation surface**: `action.yml` exposes the `contrib-types` input (hyphenated, default `commits,prs`) and forwards it to the CLI using the **`--contrib-types` alias**, not `--types`. The alias is therefore the production code path for User Story 2 and must remain stable and covered by tests; removing it would silently break every GitHub Actions consumer.

### Partial Response Handling
`_async_process_year_contributions` does not abort when the GraphQL response carries top-level `errors`. GitHub routinely returns field-level errors (unresolvable repositories, SAML restrictions, deleted nodes) alongside a valid partial `data` payload, so the parser checks for a usable `contributionsCollection` instead. Consequently the PR state filter must parse defensively: absent `contributions`, absent `nodes`, and `null` `pullRequest` entries are skipped rather than counted.

### Testing Strategy
- Query construction per `contribution_types` combination (`tests/test_fetcher.py`).
- PR state filtering, including under a partial-error payload (`tests/test_fetcher.py`).
- Flag parsing and validation for **both** spellings, `--types` and `--contrib-types` (`tests/test_cli.py`).
- Config-level validation of empty and invalid type lists (`tests/test_contrib_card.py`).

## Complexity Tracking

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| None | N/A | N/A |

### Revision: Implementation Sync 2026-03-22
- Reason: The default value for the `--types` configuration was updated to `commits,prs` to prevent fetching of noisy non-code repositories (like issue-only contributions) by default.
- Reason: Added logic to filter Pull Request contributions by state (OPEN/MERGED).
- Reason: Added safety guard for dynamic query building and aligned GitHub Action input naming.

### Revision: Implementation Sync 2026-08-09
- Reason: Repaired a corrupted code fence in "Project Structure" — the "Technical Detail: PR State Filtering" heading had been inserted inside the source-tree block, orphaning the `tests/` and `action.yml` entries and leaving an unclosed fence.
- Reason: Documented that `action.yml` forwards its input through the `--contrib-types` **alias** rather than `--types`, making the alias the production path for User Story 2.
- Reason: Recorded the partial-GraphQL-error handling introduced after this feature shipped (PR #14, 2026-07-24), which changes how the PR state filter must parse incomplete payloads.
- Reason: Recorded the 100-node ceiling on per-repository PR retrieval as an explicit technical constraint.

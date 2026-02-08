# Implementation Plan: Add contributor card

**Branch**: `001-contributor-card` | **Date**: 2026-02-07 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `specs/001-contributor-card/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.gemini/commands/speckit.plan.toml` for the execution workflow.

## Summary

This feature adds a new `contrib` subcommand to the CLI that generates an SVG card displaying the top repositories a user has contributed to (excluding their own). It leverages the GitHub GraphQL API to fetch contribution data (Commits, PRs, Issues, Reviews), sorts them by star count, and renders them with the repository owner's avatar embedded as a base64 image.

## Technical Context

**Language/Version**: Python 3.13+ (Managed by `uv`)
**Primary Dependencies**: Click (CLI), Requests (API), Built-in XML/SVG libraries
**Testing**: `pytest` (Unit), `pytest-mock` (API mocking)
**Linting/Formatting**: `ruff` (Lint+Format), `mypy` (Strict Typing)
**Project Structure**: `src/` layout with `tests/`
**Performance Goals**: <500ms local generation time (excluding network latency)
**Constraints**: No external SVG rendering services; Secure token handling

**Unknowns / Needs Clarification**:
- [ ] **GraphQL Sorting**: Can `repositoriesContributedTo` be sorted by `STARGAZERS` directly in the API? [NEEDS CLARIFICATION]
- [ ] **SVG Image Embedding**: Best compatible SVG syntax for circular masking of base64 images? [NEEDS CLARIFICATION]

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- [x] **I. CLI-First**: Does this feature expose functionality via flags/args in `src/cli.py`? (Yes, `contrib` subcommand)
- [x] **II. Local Generation**: Does it avoid external dependencies for rendering? (Yes, local SVG construction)
- [x] **III. Modern Python**: Is it typed (`mypy` strict) and `ruff` compliant? (Yes, strictly typed)
- [x] **IV. Visuals**: Is the SVG output accessible and themeable? (Yes, follows existing patterns)
- [x] **V. Testing**: Are unit tests included? (Yes, planned)

## Project Structure

### Documentation (this feature)

```text
specs/001-contributor-card/
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
│   ├── config.py        # Add ContribCardConfig, ContribFetchConfig
│   └── ...
├── github/
│   ├── client.py        # Update for image fetching
│   ├── fetcher.py       # Add fetch_contributor_stats
│   └── ...
├── rendering/
│   ├── base.py          # Shared logic
│   ├── contrib.py       # NEW: Contributor Card renderer
│   ├── stats.py
│   └── ...
└── cli.py               # Add contrib command

tests/
├── test_cli.py
├── test_contrib_card.py # NEW: Tests for new renderer
├── test_fetcher.py      # Update or new test file
└── ...
```

## Complexity Tracking

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| New `contrib.py` renderer | Distinct layout (rows + avatars) | Reuse of `stats.py` or `langs.py` would require excessive branching and conditional logic. |
| Base64 Image Embedding | Self-contained SVG | Linking to external URLs allows tracking and breaks in some secure viewers (e.g. GitHub raw). |

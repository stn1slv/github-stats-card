# Implementation Plan: [FEATURE]

**Branch**: `[###-feature-name]` | **Date**: [DATE] | **Spec**: [link]
**Input**: Feature specification from `/specs/[###-feature-name]/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.gemini/commands/speckit.plan.toml` for the execution workflow.

## Summary

[Extract from feature spec: primary requirement + technical approach from research]

## Technical Context

**Language/Version**: Python 3.13+ (Managed by `uv`)
**Primary Dependencies**: Click (CLI), Requests (API), Built-in XML/SVG libraries
**Testing**: `pytest` (Unit), `pytest-mock` (API mocking)
**Linting/Formatting**: `ruff` (Lint+Format), `mypy` (Strict Typing)
**Project Structure**: `src/` layout with `tests/`
**Performance Goals**: <500ms local generation time
**Constraints**: No external SVG rendering services; Secure token handling

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- [ ] **I. CLI-First**: Does this feature expose functionality via flags/args in `src/cli.py`?
- [ ] **II. Local Generation**: Does it avoid external dependencies for rendering?
- [ ] **III. Modern Python**: Is it typed (`mypy` strict) and `ruff` compliant?
- [ ] **IV. Visuals**: Is the SVG output accessible and themeable?
- [ ] **V. Testing**: Are unit tests included?

## Project Structure

### Documentation (this feature)

```text
specs/[###-feature]/
├── plan.md              # This file
├── research.md          # Research & Design
├── data-model.md        # Data Structures & Config
├── quickstart.md        # Usage Guide
└── tasks.md             # Implementation Tasks
```

### Source Code

```text
src/
├── core/                # Shared foundational logic
│   ├── config.py        # Centralized configuration
│   ├── constants.py     # Centralized constants
│   ├── exceptions.py    # Custom exceptions
│   └── utils.py         # General utility functions
├── github/              # GitHub-specific integration
│   ├── client.py        # Centralized REST/GraphQL client
│   ├── fetcher.py       # Stats Card data fetcher
│   └── langs_fetcher.py # Top Languages data fetcher
├── rendering/           # SVG generation and visual logic
│   ├── base.py          # Base SVG card renderer (shared)
│   ├── colors.py        # Color parsing and utilities
│   ├── icons.py         # SVG icons
│   ├── langs.py         # Top Languages Card renderer
│   ├── stats.py         # Stats Card renderer
│   └── themes.py        # Theme definitions
└── cli.py               # CLI orchestration

tests/
├── test_cli.py          # Integration tests for commands
├── test_fetcher.py      # Mocked API tests
└── test_[feature].py    # Feature-specific tests
```

## Complexity Tracking

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| [e.g. New Dependency] | [Why standard lib is insufficient] | [Why existing deps insufficient] |
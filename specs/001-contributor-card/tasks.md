# Tasks: Add contributor card

**Branch**: `001-contributor-card` | **Date**: 2026-02-07 | **Spec**: [spec.md](./spec.md)

## Phase 1: Setup

**Goal**: Initialize configuration and project structures for the new feature.
**Independent Test Criteria**: Tests can verify the new config classes are importable and have correct defaults.

- [x] T001 Create ContribFetchConfig in src/core/config.py
- [x] T002 Create ContribCardConfig in src/core/config.py
- [x] T003 Create test for ContribFetchConfig in tests/test_contrib_card.py
- [x] T004 Create test for ContribCardConfig in tests/test_contrib_card.py

## Phase 2: Foundational

**Goal**: Implement core data fetching and rendering capabilities required by all user stories.
**Independent Test Criteria**: Unit tests verify API client fetches and transforms data correctly, and base renderer logic works.

- [x] T005 [P] Update GitHubClient in src/github/client.py to implement fetch_image method for avatars
- [x] T006 [P] Implement fetch_contributor_stats in src/github/fetcher.py (GraphQL query + sorting)
- [x] T007 Create unit tests for fetch_contributor_stats in tests/test_fetcher.py
- [x] T008 [P] Implement render_contrib_card stub in src/rendering/contrib.py
- [x] T009 Register contrib command group in src/cli.py

## Phase 3: Generate Basic Contributor Card

**Goal**: Enable generating a basic card with default settings (User Story 1).
**Independent Test Criteria**: Running the CLI command produces a valid SVG with correct repo list.

- [x] T010 [US1] Implement full render_contrib_card logic in src/rendering/contrib.py (layout + avatars + a11y)
- [x] T011 [US1] Implement avatar fetching and base64 embedding in src/github/fetcher.py
- [x] T012 [US1] Add fallback logic for failed avatar fetches in src/github/fetcher.py
- [x] T013 [US1] Connect cli command to fetcher and renderer in src/cli.py
- [x] T014 [US1] Create integration test for contrib command in tests/test_cli.py

## Phase 4: Customization & Edge Cases

**Goal**: Support customization options and handle edge cases (User Stories 2, 3, 4).
**Independent Test Criteria**: Verifying flags change output (limit, theme) and empty states don't crash.

- [x] T015 [P] [US2] Implement limit and exclude_repos filtering (with format validation) in src/github/fetcher.py
- [x] T016 [P] [US3] Ensure render_contrib_card respects all theme colors in src/rendering/contrib.py
- [x] T017 [US4] Implement "No contributions found" empty state in src/rendering/contrib.py
- [x] T018 [US4] Add tests for empty states and limits in tests/test_contrib_card.py
- [x] T019 [P] [US2] Update CLI arguments in src/cli.py for limits and exclusions

## Phase 5: Polish

**Goal**: Final cleanups and cross-cutting concerns.
**Independent Test Criteria**: All tests pass, linting passes.

- [x] T020 Run ruff check and fix any linting issues
- [x] T021 Run mypy and fix any type errors
- [x] T022 Verify SVG accessibility tags in src/rendering/contrib.py

## Dependencies

1. T001, T002 -> T006, T008 (Config needed for logic)
2. T006 -> T010, T013 (Data needed for rendering)
3. T010 -> T013 (Renderer needed for CLI)
4. T005 -> T011 (Client needed for avatar fetch)

## Implementation Strategy

We will start by defining the configuration classes (T001, T002) to establish the data contract. Then we implement the core data fetching logic (T006) which is the most complex part involving GraphQL and sorting. Once data is available, we build the renderer (T010) and connect it all via the CLI (T013). Finally, we iterate on customization options (Phase 4).

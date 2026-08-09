# Tasks: Filter Contribution Types for Contributor Card

**Input**: Design documents from `/specs/003-filter-contrib-types/`
**Prerequisites**: plan.md, spec.md, data-model.md, research.md

## Phase 1: Setup & Configuration

**Purpose**: Prepare the configuration structures and constants for the feature

- [x] T001 Define `VALID_CONTRIB_TYPES` constant in `src/core/constants.py` (or directly in `src/core/config.py`)
- [x] T002 Update `ContribFetchConfig` in `src/core/config.py` to include `contribution_types: list[str]` with a default value
- [x] T003 Update config instantiation in `src/core/config.py` to properly handle and parse comma-separated strings for the new `types` argument

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Update core data fetching logic to respect the new configuration parameter

- [x] T004 Modify GraphQL query generation in `src/github/fetcher.py` (`_async_process_year_contributions`) to conditionally include/exclude query blocks for commits, PRs, issues, and reviews
- [x] T005 Add unit tests in `tests/test_fetcher.py` to verify the generated GraphQL queries correctly respect the `contribution_types` filter

**Checkpoint**: Core data fetching logic is dynamically responding to configuration parameters.

---

## Phase 3: User Story 1 - Filter to Specific Contribution Types via CLI (Priority: P1)

**Goal**: Expose the ability to specify contribution types via a new CLI flag.

### Tests (Write First)
- [x] T006 [P] [US1] Add test cases for `--types` CLI flag parsing and validation in `tests/test_cli.py`
- [x] T007 [P] [US1] Create an integration test in `tests/test_contrib_card.py` to verify the end-to-end flow with the types flag

### Implementation
- [x] T008 [US1] Add `--types` (and `--contrib-types` alias) flag to the `contrib` command in `src/cli.py` with validation against `VALID_CONTRIB_TYPES`

**Checkpoint**: Users can successfully filter their contributor card via the local CLI.

---

## Phase 4: User Story 2 - Filter Contributions via Automation (Priority: P1)

**Goal**: Allow configuration of contribution types via GitHub Actions inputs.

### Implementation
- [x] T009 [US2] Add `contrib-types` input parameter to `action.yml`, mapped to the CLI `--types` flag
- [x] T010 [US2] Document the new `contrib-types` parameter in the `README.md` usage examples

**Checkpoint**: GitHub Actions workflows can utilize the new filtering logic.

---

## Phase 5: Polish & Quality

**Purpose**: Ensure strict adherence to constitution and project standards

- [x] T011 Run `uv run ruff check src tests` and fix any linting violations
- [x] T012 Run `uv run ruff format src tests` to ensure code formatting consistency
- [x] T013 Run `uv run mypy src` and fix any type checking errors
- [x] T014 Run all tests with `uv run pytest` to ensure no regressions were introduced

## Remediation: Gaps

- [x] T015 [P] Update `action.yml` input description to reflect that the default value is 'commits,prs' in `action.yml` [Sync: Gap Report]
- [x] T016 [P] Update `_build_contrib_query` to fetch PR nodes and states in `src/github/fetcher.py` [Sync: Gap Report]
- [x] T017 Update `_async_process_year_contributions` parsing logic to filter PRs by OPEN/MERGED state in `src/github/fetcher.py` [Sync: Gap Report]
- [x] T018 [P] Add test case for PR state filtering in `tests/test_fetcher.py` [Sync: Gap Report]

## Remediation: Drift

- [x] T019 [P] Add guard to `_build_contrib_query` to prevent invalid empty selection sets in `src/github/fetcher.py` [Sync: Gap Report]
- [x] T020 [P] Add warning or documentation note regarding 100-node limit for PR state filtering in `src/github/fetcher.py` [Sync: Gap Report]

## Remediation: Full Audit (2026-08-09)

**Purpose**: Close the gaps found by a full audit of the shipped implementation against every feature artifact.

- [X] T021 [P] [US2] Add a CLI test that invokes the `--contrib-types` alias (the spelling `action.yml` actually forwards) and asserts it parses identically to `--types` in `tests/test_cli.py` [Sync: Gap Report]
- [X] T022 [US1] Advertise the `commits,prs` default for `--types`/`--contrib-types` in `--help` output in `src/cli.py` [Sync: Gap Report]
- [X] T023 [US1] Document the `--types` / `--contrib-types` flag, its allowed values and its `commits,prs` default in the CLI Usage section of `README.md` [Sync: Gap Report]
- [X] T024 [US3] Add a regression test covering PR state filtering against a partial GraphQL payload (top-level `errors` present, some `pullRequest` nodes null or missing) in `tests/test_fetcher.py` [Sync: Gap Report]
- [X] T025 [P] Move the 100-node PR limit note out of the transmitted GraphQL string in `_build_contrib_query` into a Python comment so it is not sent on every API request in `src/github/fetcher.py` [Sync: Gap Report]

**Implementation note (T022)**: implemented by appending `(default: commits,prs)` to the option's help string rather than by setting Click's `show_default=True`. This repo documents defaults inline in help text in all 14 other places and never uses `show_default`; matching that convention keeps `--help` output uniform. FR-008 and SC-007 are satisfied either way, and `test_contrib_command_types_default_is_documented_in_help` pins the behaviour rather than the mechanism.

**Checkpoint**: The automation code path is covered by tests, the CLI advertises its own default, and the partial-response behaviour this feature depends on is pinned by a regression test.

### Revision: Implementation Sync 2026-03-22
- Reason: Reconciled documentation and code to ensure the default value for the `--types` flag is strictly 'commits,prs' instead of all four contribution types.
- Reason: Implementation now filters Pull Request contributions to only include OPEN and MERGED states.
- Reason: Synchronized Actions input name (`contrib-types`) across spec and implementation.

### Revision: Implementation Sync 2026-08-09
- Reason: Full audit ("check all") added T021–T025 covering the untested `--contrib-types` automation path, the undiscoverable CLI default, missing README CLI documentation, partial-response regression coverage, and the misplaced GraphQL comment.

---

## Implementation Strategy
- **MVP**: Complete Phase 1 through Phase 3 to establish local CLI functionality.
- **Dependencies**: Phase 2 depends on Phase 1. Phase 3 depends on Phase 2. Phase 4 depends on Phase 3.
- **Parallel Execution**: Within Phase 3, tests (T006, T007) can be developed in parallel with the foundational CLI implementation (T008) utilizing mocking before the full integration is wired up.
---

## Phase 6: Convergence

- [X] T026 Add a test asserting `action.yml` declares the `contrib-types` input with default `commits,prs` and forwards it to the CLI as `--contrib-types`, so the automation wiring cannot drift from the flag the CLI accepts, in `tests/test_cli.py` per SC-002, SC-008, US2/AC1, US2/AC2 (partial)
- [X] T027 Assert the default fallback on the no-flag path: extend the plain `contrib` invocation to check `contribution_types == ["commits", "prs"]` in `tests/test_cli.py` per SC-003, FR-002 (partial)
- [X] T028 Pass `contrib-types` to the run step via `env:` and reference it as a quoted shell variable instead of interpolating `${{ inputs.contrib-types }}` directly into the command string in `action.yml` per Constitution Security/Input Validation (contradicts)
- [X] T029 Review and justify the `GITHUB_TOKEN` scope warning emitted by the `contrib` command, either recording it in a feature specification of its own or removing it, in `src/cli.py` (unrequested)
- [X] T030 Extend `test_build_contrib_query` with single-type selections (`issues` only, `reviews` only) to pin that unselected blocks are omitted in `tests/test_fetcher.py` per plan: Testing Strategy (partial)

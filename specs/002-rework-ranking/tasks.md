# Implementation Tasks: Rework Ranking Calculation

**Branch**: `002-rework-ranking` | **Spec**: [specs/002-rework-ranking/spec.md](specs/002-rework-ranking/spec.md) | **Plan**: [specs/002-rework-ranking/plan.md](specs/002-rework-ranking/plan.md)

## Phase 1: Setup

- [x] T001 Create task definitions file
  - **File**: `specs/002-rework-ranking/tasks.md`
  - **Description**: Initialize the task list (this file) to track implementation progress.
  - **Source**: `spec.md` (Process)
  - **Verification**: File exists and follows structure.

## Phase 2: Foundational

- [x] T002 Implement `calculate_repo_rank` core logic
  - **File**: `src/github/rank.py`
  - **Description**: Implement the repository ranking function based on star thresholds (S>10k, A>1k...) and repository magnitude modifiers (Commits>5k -> +, Commits<100 -> -).
  - **Source**: `data-model.md`
  - **Verification**: Unit tests in T003.

- [x] T003 Add unit tests for ranking logic
  - **File**: `tests/test_rank.py`
  - **Description**: Create comprehensive test cases for `calculate_repo_rank` covering all tiers (S-D) and modifiers (+, -, none) based on total repo commits.
  - **Source**: `spec.md` (FR-004)
  - **Verification**: `uv run pytest tests/test_rank.py` passes.

## Phase 3: User Story 1 - Repository-Specific Ranking

- [x] T004 [US1] Update Fetcher Data Model
  - **File**: `src/github/fetcher.py`
  - **Description**: Update `ContributorRepo` TypedDict to include `rank_level: str`.
  - **Source**: `data-model.md`
  - **Verification**: Code compiles/passes mypy.

- [x] T005 [US1] Update Fetcher Logic
  - **File**: `src/github/fetcher.py`
  - **Description**: Update `fetch_contributor_stats` to fetch repository total commit count (via HEAD object history), calculate rank using `calculate_repo_rank`, and assign to `rank_level`.
  - **Source**: `plan.md` (Technical Context)
  - **Verification**: Unit tests in T006.

- [x] T006 [US1] Update Fetcher Tests
  - **File**: `tests/test_fetcher.py`
  - **Description**: Update API mocks to simulate repo total commits. Verify that `fetch_contributor_stats` correctly populates `rank_level`.
  - **Source**: `spec.md` (SC-003)
  - **Verification**: `uv run pytest tests/test_fetcher.py` passes.

- [x] T007 [US1] Update Contributor Card Renderer
  - **File**: `src/rendering/contrib.py`
  - **Description**: Modify `render_contrib_card` to display the specific `rank_level` for each repo. Implement font scaling logic.
  - **Source**: `spec.md` (VR-001, VR-002)
  - **Verification**: Visual tests in T008.

- [x] T008 [US1] Update Rendering Tests
  - **File**: `tests/test_contrib_rendering.py`
  - **Description**: Add test cases to verify SVG output contains the correct rank text and font style/size attributes.
  - **Source**: `spec.md` (VR-001)
  - **Verification**: `uv run pytest tests/test_contrib_rendering.py` passes.

## Phase 4: Verification

- [x] T009 [US1] Manual CLI Verification
  - **File**: N/A
  - **Description**: Run `uv run github-stats-card contrib --username [user]` against a real profile and manually inspect the generated SVG.
  - **Source**: `spec.md` (User Story 1)
  - **Verification**: SVG opens in browser and looks correct.

## Dependencies

- T003 depends on T002
- T004 depends on T002
- T005 depends on T004
- T006 depends on T005
- T007 depends on T005
- T008 depends on T007

## Implementation Strategy

1. Implement core ranking logic and tests first to establish the "truth".
2. Update the data fetcher to use this logic.
3. Update the renderer to display the new data.
4. Verify end-to-end.

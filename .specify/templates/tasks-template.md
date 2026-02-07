---
description: "Task list template for feature implementation"
---

# Tasks: [FEATURE NAME]

**Input**: Design documents from `/specs/[###-feature-name]/`
**Prerequisites**: plan.md, spec.md

## Phase 1: Setup & Configuration

**Purpose**: Prepare the environment and configuration structures

- [ ] T001 Update `src/core/config.py` with new dataclass fields
- [ ] T002 [P] Create/Update `tests/conftest.py` with fixtures for new features
- [ ] T003 [P] Verify `uv` environment matches requirements

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core logic independent of CLI exposure

- [ ] T004 Implement core logic in `src/[module].py`
- [ ] T005 Add unit tests in `tests/test_[module].py` (Must pass `pytest`)
- [ ] T006 Update `src/github/fetcher.py` (if API changes needed)
- [ ] T007 Mock API responses for new data in `tests/`

**Checkpoint**: Core logic tested with 100% coverage

---

## Phase 3: User Story 1 - [Title] (Priority: P1)

**Goal**: [Description]

### Tests (Write First)
- [ ] T008 [P] [US1] Create test case in `tests/test_[feature].py`

### Implementation
- [ ] T009 [P] [US1] Implement rendering logic in `src/rendering/[card_module].py`
- [ ] T010 [P] [US1] Add CLI flags to `src/cli.py`
- [ ] T011 [P] [US1] Wire config to rendering logic
- [ ] T012 [US1] Verify SVG output locally

**Checkpoint**: Feature functional via CLI

---

## Phase N: Polish & Quality

**Purpose**: Ensure strict adherence to constitution

- [ ] TXXX Run `uv run ruff check src tests` and fix violations
- [ ] TXXX Run `uv run black src tests`
- [ ] TXXX Run `uv run mypy src` and fix typing errors
- [ ] TXXX Add documentation to `README.md`
- [ ] TXXX Verify accessibility of generated SVGs
- [ ] TXXX Run all tests with `uv run pytest`
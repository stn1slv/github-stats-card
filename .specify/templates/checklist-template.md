# [CHECKLIST TYPE] Checklist: [FEATURE NAME]

**Purpose**: [Brief description]
**Created**: [DATE]
**Feature**: [Link to spec.md]

## Code Quality Gates (Automated)

- [ ] Run `uv run ruff check src tests` (Linting)
- [ ] Run `uv run black src tests` (Formatting)
- [ ] Run `uv run mypy src` (Strict Typing)
- [ ] Run `uv run pytest` (All tests pass)

## Feature Verification

- [ ] CLI command accepts new flags
- [ ] CLI help text (`--help`) is updated and clear
- [ ] SVG output renders correctly in Light Mode
- [ ] SVG output renders correctly in Dark Mode
- [ ] No regression in existing cards

## Documentation

- [ ] `README.md` updated with new usage examples
- [ ] `CONTRIBUTING.md` updated (if workflow changed)
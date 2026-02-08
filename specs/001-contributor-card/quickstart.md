# Quickstart: Contributor Card

**Feature**: `001-contributor-card` | **Date**: 2026-02-07

## Overview
The `contrib` command generates a card displaying the top external repositories you have contributed to, sorted by stars.

## Usage

### Basic Generation
```bash
uv run github-stats-card contrib -u <username> -o contrib.svg
```

### Options

| Flag | Description | Default |
|------|-------------|---------|
| `--limit`, `-l` | Number of repositories to show | 10 |
| `--exclude-repo` | Comma-separated repos/patterns to hide (supports `*`) | None |
| `--theme` | Visual theme (e.g., `vue-dark`) | `default` |
| `--hide-border` | Hide the card border | `False` |

### Examples

**Top 5 Contributions (Dark Theme):**
```bash
uv run github-stats-card contrib \
  -u octocat \
  -o contributions.svg \
  --theme vue-dark \
  --limit 5
```

**Exclude Specific Repositories or Patterns:**
```bash
# Exclude by full name or wildcard pattern
uv run github-stats-card contrib \
  -u octocat \
  -o contributions.svg \
  --exclude-repo "awesome-*,facebook/react"

# Exclude specific repository across all owners
uv run github-stats-card contrib \
  -u octocat \
  -o contributions.svg \
  --exclude-repo "my-private-repo"
```

**CI/CD Integration (GitHub Actions):**
```yaml
- name: Generate Contributor Card
  run: |
    uv run github-stats-card contrib 
      -u ${{ github.repository_owner }} 
      -o img/contrib.svg 
      --token ${{ secrets.GITHUB_TOKEN }}
```

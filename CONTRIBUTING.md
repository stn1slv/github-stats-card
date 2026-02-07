# Contributing to GitHub Stats Card

Thank you for your interest in contributing! This document provides guidelines and instructions for contributing to the project.

## Development Setup

### Prerequisites

- Python 3.13+
- [uv](https://github.com/astral-sh/uv) (recommended) or pip
- Git
- GitHub account with a Personal Access Token

### Setup Instructions

1. **Fork and clone the repository**

   ```bash
   git clone https://github.com/yourusername/github-stats-card.git
   cd github-stats-card
   ```

2. **Create a virtual environment**

   ```bash
   uv venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install dependencies**

   ```bash
   uv pip install -e ".[dev]"
   ```

4. **Set up GitHub token**

   ```bash
   export GITHUB_TOKEN=ghp_your_token_here
   ```

5. **Verify installation**

   ```bash
   uv run github-stats-card --help
   uv run pytest
   ```

## Development Workflow

### Running Tests

This project uses `uv` for all Python execution and testing:

```bash
# Run all tests
uv run pytest

# Run with coverage
uv run pytest --cov=src

# Run specific test file
uv run pytest tests/test_rank.py

# Run with verbose output
uv run pytest -v
```

### Code Formatting

We use `black` for code formatting and `ruff` for linting (via `uv`):

```bash
# Format code
uv run black src tests

# Check formatting
uv run black --check src tests

# Lint code
uv run ruff check src tests

# Auto-fix linting issues
uv run ruff check --fix src tests
```

### Type Checking

```bash
# Run mypy
uv run mypy src
```

### Manual Testing

```bash
# Test basic functionality
uv run github-stats-card stats -u octocat -o test.svg

# Test with different themes
uv run github-stats-card stats -u octocat -o test.svg --theme dark --show-icons
```

## Project Structure

```
github-stats-card/
├── src/                      # Main package
│   ├── core/                 # Shared foundational logic
│   │   ├── config.py         # Configuration dataclasses
│   │   ├── constants.py      # Centralized constants
│   │   ├── exceptions.py     # Exception hierarchy
│   │   ├── i18n.py           # Internationalization
│   │   └── utils.py          # Utility functions
│   ├── github/               # GitHub-specific integration
│   │   ├── client.py         # Authenticated API client
│   │   ├── fetcher.py        # Statistics retrieval
│   │   ├── langs_fetcher.py  # Language data retrieval
│   │   └── rank.py           # User rank calculation
│   ├── rendering/            # SVG generation and visual logic
│   │   ├── base.py           # Base SVG card "envelope"
│   │   ├── colors.py         # Color parsing and utilities
│   │   ├── icons.py          # SVG icon definitions
│   │   ├── langs.py          # Top languages card renderer
│   │   ├── stats.py          # Stats card renderer
│   │   └── themes.py         # Built-in color schemes
│   ├── cli.py                # Command-line interface
│   ├── __init__.py           # Package initialization
│   └── __main__.py           # Entry point for python -m
├── tests/                    # Test suite
│   ├── test_colors.py
│   ├── test_langs_card.py
│   ├── test_langs_fetcher.py
│   ├── test_rank.py
│   ├── test_stats_card.py
│   └── test_utils.py
├── .github/workflows/        # GitHub Actions
├── pyproject.toml            # Package configuration
└── README.md                 # Documentation
```

## Making Changes

### Adding a New Theme

1. Open `src/rendering/themes.py`
2. Add your theme to the `THEMES` dictionary:

   ```python
   "my_theme": {
       "title_color": "ff6e96",
       "icon_color": "79dafa",
       "text_color": "f8f8f2",
       "bg_color": "282a36",
   },
   ```

3. Test it:

   ```bash
   uv run github-stats-card stats -u octocat -o test.svg --theme my_theme
   ```

### Adding a New Icon

1. Open `src/rendering/icons.py`
2. Find the SVG path from [Octicons](https://primer.style/octicons/)
3. Add it to the `ICONS` dictionary:

   ```python
   "my_icon": """<path fill-rule="evenodd" d="..." />""",
   ```

### Adding a New Stat

1. Update `src/github/fetcher.py` to fetch the new data from GitHub API
2. Update `src/core/i18n.py` to add the translation key
3. Update `src/rendering/stats.py` to include it in `_get_stat_definitions`
4. Add tests in `tests/test_stats_card.py`

### Adding a Translation

1. Open `src/core/i18n.py`
2. Add a new locale to `TRANSLATIONS`:

   ```python
   "es": {
       "statcard_title": "Estadísticas de GitHub de {name}",
       "statcard_totalstars": "Estrellas Totales",
       # ... more translations
   },
   ```

## Submitting Changes

### Commit Guidelines

We follow conventional commits:

- `feat:` - New feature
- `fix:` - Bug fix
- `docs:` - Documentation changes
- `style:` - Code style changes (formatting, etc.)
- `refactor:` - Code refactoring
- `test:` - Adding or updating tests
- `chore:` - Maintenance tasks

### Pull Request Process

1. **Create a branch**
2. **Make your changes**
3. **Run checks** (`pytest`, `black`, `ruff`, `mypy`)
4. **Commit and Push**

## Code Style

### Python

- Follow PEP 8
- Use modern type hints (Python 3.10+)
- Maximum line length: 100 characters
- Use docstrings for functions and classes

Example:

```python
from src.core.config import StatsCardConfig

def render_stats_card(stats: dict[str, Any], config: StatsCardConfig) -> str:
    """
    Render GitHub stats as an SVG card.
    
    Args:
        stats: Dictionary containing user statistics from GitHub API
        config: Configuration object with all rendering options
        
    Returns:
        SVG string representing the stats card
    """
    # Implementation
```

### Configuration Objects

All rendering functions use configuration objects instead of individual parameters:

```python
from src.core.config import StatsCardConfig, LangsCardConfig
from src.rendering.stats import render_stats_card
from src.rendering.langs import render_top_languages

stats_config = StatsCardConfig(theme="vue-dark", show_icons=True)
svg = render_stats_card(stats, stats_config)

langs_config = LangsCardConfig(layout="compact", langs_count=8)
svg = render_top_languages(langs, langs_config)
```

## License

By contributing, you agree that your contributions will be licensed under the MIT License.
# GitHub Stats Card

A Python CLI tool that generates beautiful GitHub stats cards as SVG images for your profile README.

[![Python 3.13+](https://img.shields.io/badge/python-3.13+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Tests](https://img.shields.io/badge/tests-59%20passed-success.svg)](#testing)

## Features

- 🎨 **50+ Built-in Themes** - Choose from a variety of beautiful color schemes
- 📊 **Comprehensive Stats** - Stars, commits, PRs, issues, reviews, and more
- 🔤 **Top Languages Card** - Show your most used programming languages with 5 layouts
- ⚖️ **Smart Weighting** - Preset rankings (balanced, expertise, diversity) for language stats
- 📐 **Aligned Layouts** - Compact top-langs card matches stats card width (467px)
- 🔧 **Highly Customizable** - Customize colors, layout, and content
- 🚀 **GitHub Actions Ready** - Perfect for automated daily/weekly updates
- 🎯 **Local Generation** - No external service dependencies
- 🌐 **Internationalization** - Support for multiple languages (English included)

## 📚 Documentation

- **[Usage Examples](EXAMPLES.md)** - 13+ detailed examples
- **[Contributing Guide](CONTRIBUTING.md)** - How to contribute

## Installation

### Using uv (recommended)

```bash
uv pip install -e .
```

### Using pip

```bash
pip install -e .
```

> **Note:** This project uses `uv` for all Python execution, testing, and package management. All examples in this documentation use `uv` commands.

### Running Without Installation

You can run the application directly without installing it using `uv run`:

```bash
# Run as a Python module
uv run python -m src.cli stats -u your-username -o stats.svg

# Or using the shorter form
uv run python -m src stats -u your-username -o stats.svg
```

**Important:** Don't forget to set your GitHub token:
```bash
export GITHUB_TOKEN=ghp_your_token_here
uv run python -m src.cli stats -u your-username -o stats.svg
```

Or pass it directly:
```bash
uv run python -m src.cli stats -u your-username -o stats.svg --token ghp_your_token_here
```

## Quick Start

### Set up your GitHub token

Create a Personal Access Token (PAT) with `read:user` scope:
https://github.com/settings/tokens/new

```bash
export GITHUB_TOKEN=ghp_your_token_here
```

### Generate your cards

```bash
# GitHub stats card
uv run github-stats-card stats -u your-username -o stats.svg

# Top languages card
uv run github-stats-card top-langs -u your-username -o top-langs.svg
```

## Usage

The CLI provides two main commands:
- `stats` - Generate GitHub stats card
- `top-langs` - Generate top languages card

### GitHub Stats Card

```bash
# Generate with default theme
uv run github-stats-card stats -u octocat -o stats.svg

# Use a specific theme
uv run github-stats-card stats -u octocat -o stats.svg --theme vue-dark

# Show icons and hide border
uv run github-stats-card stats -u octocat -o stats.svg --show-icons --hide-border
```

### Top Languages Card

```bash
# Generate with default layout (normal)
uv run github-stats-card top-langs -u octocat -o top-langs.svg

# Compact layout (467px width, matches stats card)
uv run github-stats-card top-langs -u octocat -o top-langs.svg --layout compact

# Donut chart with dark theme
uv run github-stats-card top-langs -u octocat -o top-langs.svg \
  --layout donut --theme vue-dark --hide-border

# Hide specific languages
uv run github-stats-card top-langs -u octocat -o top-langs.svg \
  --hide "HTML,CSS,Makefile" --langs-count 8

# Balanced weighting preset (70% size, 30% repo count)
uv run github-stats-card top-langs -u octocat -o top-langs.svg \
  --weighting balanced

# Pie chart with bytes display
uv run github-stats-card top-langs -u octocat -o top-langs.svg \
  --layout pie --stats-format bytes
```

### Advanced Options

**Stats Card:**
```bash
# Hide specific stats
uv run github-stats-card stats -u octocat -o stats.svg --hide stars,prs

# Show additional stats
uv run github-stats-card stats -u octocat -o stats.svg --show reviews,discussions_started

# Include all commits (not just current year)
uv run github-stats-card stats -u octocat -o stats.svg --include-all-commits

# Custom colors
uv run github-stats-card stats -u octocat -o stats.svg \
  --title-color ff6e96 \
  --text-color f8f8f2 \
  --bg-color 282a36

# Gradient background
uv run github-stats-card stats -u octocat -o stats.svg \
  --bg-color "90,ff0000,00ff00,0000ff"
```

**Top Languages Card:**
```bash
# Exclude specific repositories
uv run github-stats-card top-langs -u octocat -o top-langs.svg \
  --exclude-repo "repo1,repo2"

# Use weighting presets
uv run github-stats-card top-langs -u octocat -o top-langs.svg \
  --weighting balanced  # Options: size-only, balanced, expertise, diversity

# Custom weighting (manual control)
uv run github-stats-card top-langs -u octocat -o top-langs.svg \
  --size-weight 0.5 --count-weight 0.5

# Custom width and colors
uv run github-stats-card top-langs -u octocat -o top-langs.svg \
  --card-width 400 \
  --title-color ff6e96 \
  --text-color f8f8f2 \
  --bg-color 282a36
```

### All Options

Run `uv run github-stats-card stats --help` or `uv run github-stats-card top-langs --help` for complete option lists.

**Stats Card Options:**
- Basic: username, token, output, theme
- Display: show-icons, hide-border, hide-title, hide-rank, hide/show stats
- Commits: include-all-commits, commits-year
- Colors: title-color, text-color, icon-color, bg-color, border-color, ring-color
- Layout: card-width, line-height, border-radius
- Formatting: number-format, number-precision, locale, custom-title
- Other: rank-icon, disable-animations, text-bold

**Top Languages Card Options:**
- Basic: username, token, output, theme
- Display: hide-border, hide-title, hide-progress
- Layout: layout (normal/compact/donut/donut-vertical/pie), card-width, border-radius
- Languages: langs-count, hide (languages), exclude-repo
- Ranking: weighting (size-only/balanced/expertise/diversity), size-weight, count-weight
- Colors: title-color, text-color, bg-color, border-color
- Other: stats-format (percentages/bytes), custom-title, disable-animations

**Weighting Presets:**
- `size-only` (default) - 100% code size, 0% repo count
- `balanced` - 70% code size, 30% repo count (recommended)
- `expertise` - 50% code size, 50% repo count
- `diversity` - 40% code size, 60% repo count

## Available Themes

Here are some popular themes:

- `default` - Clean and professional
- `dark` - Dark mode friendly
- `radical` - Bold and colorful
- `vue` / `vue-dark` - Vue.js inspired
- `tokyonight` - Tokyo Night theme
- `dracula` - Dracula theme
- `gruvbox` - Gruvbox theme
- `monokai` - Monokai theme
- `github_dark` - GitHub dark theme
- `nord` - Nord theme
- `catppuccin_mocha` / `catppuccin_latte` - Catppuccin themes

[See all 50+ themes](src/themes.py)

## GitHub Actions Integration

### Method 1: Using as a Custom Action (Recommended)

The easiest way to use this project in GitHub Actions is as a custom action:

> **Security Best Practice:** Always pin actions to a specific version tag or commit SHA rather than using `@main`. This prevents supply-chain attacks where a compromised repository could inject malicious code into your workflows.

```yaml
name: Update GitHub Stats

on:
  schedule:
    - cron: '0 0 * * *'  # Daily at midnight UTC
  workflow_dispatch:  # Manual trigger

jobs:
  update-stats:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      # Generate stats card
      - name: Generate GitHub Stats Card
        uses: stn1slv/github-stats-card@v1.0.0  # Always pin to a specific version or commit SHA for security
        with:
          card-type: stats
          username: ${{ github.repository_owner }}
          token: ${{ secrets.GITHUB_TOKEN }}
          output: img/github-stats.svg
          theme: vue-dark
          show-icons: true
          hide-border: true
          include-all-commits: true
      
      # Generate top languages card
      - name: Generate Top Languages Card
        uses: stn1slv/github-stats-card@v1.0.0  # Always pin to a specific version or commit SHA for security
        with:
          card-type: top-langs
          username: ${{ github.repository_owner }}
          token: ${{ secrets.GITHUB_TOKEN }}
          output: img/top-langs.svg
          theme: vue-dark
          layout: compact
          hide-border: true
          langs-count: 8
          weighting: balanced
      
      # Commit and push changes
      - name: Commit and push if changed
        run: |
          git config --local user.email "github-actions[bot]@users.noreply.github.com"
          git config --local user.name "github-actions[bot]"
          git add img/*.svg
          git diff --staged --quiet || git commit -m "Update GitHub stats [skip ci]"
          git push
```

#### Available Action Inputs

**Common inputs:**
- `card-type` (required) - Type of card: `stats` or `top-langs`
- `username` (required) - GitHub username
- `token` (required) - GitHub Personal Access Token
- `output` (required) - Output SVG file path
- `theme` - Theme name (default: `default`)
- `hide-border` - Hide card border (default: `false`)
- `hide-title` - Hide card title (default: `false`)
- `custom-title` - Custom card title
- `title-color`, `text-color`, `bg-color`, `border-color` - Custom colors
- `card-width` - Card width in pixels
- `border-radius` - Border radius (default: `4.5`)
- `disable-animations` - Disable CSS animations (default: `false`)

**Stats card inputs:**
- `show-icons` - Show icons next to stats (default: `false`)
- `hide-rank` - Hide rank circle (default: `false`)
- `include-all-commits` - Include all commits, not just current year (default: `false`)
- `hide` - Comma-separated stats to hide

**Top-langs card inputs:**
- `layout` - Layout style: `normal`, `compact`, `donut`, `donut-vertical`, `pie` (default: `normal`)
- `langs-count` - Number of languages to show (default: `5`)
- `hide-progress` - Hide progress bars (default: `false`)
- `weighting` - Weighting preset: `size-only`, `balanced`, `expertise`, `diversity`
- `exclude-repo` - Comma-separated repos to exclude
- `hide` - Comma-separated languages to hide

### Method 2: Direct CLI Installation

Create `.github/workflows/update-stats.yml`:

```yaml
name: Update GitHub Stats

on:
  schedule:
    - cron: '0 0 * * *'  # Daily at midnight UTC
  workflow_dispatch:  # Manual trigger

jobs:
  update-stats:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.13'
      
      - name: Install uv
        run: pip install uv
      
      - name: Install github-stats-card
        run: uv pip install --system -e .
      
      - name: Generate GitHub Stats Cards
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
        run: |
          # Stats card - Dark theme
          github-stats-card stats \
            --username ${{ github.repository_owner }} \
            --output img/github-stats-dark.svg \
            --theme vue-dark \
            --show-icons \
            --hide-border \
            --include-all-commits
          
          # Stats card - Light theme
          github-stats-card stats \
            --username ${{ github.repository_owner }} \
            --output img/github-stats-light.svg \
            --theme vue \
            --show-icons \
            --hide-border \
            --include-all-commits
          
          # Top languages card - Dark theme (compact layout, 467px width)
          github-stats-card top-langs \
            --username ${{ github.repository_owner }} \
            --output img/top-langs-dark.svg \
            --theme vue-dark \
            --layout compact \
            --hide-border \
            --langs-count 8 \
            --weighting balanced
          
          # Top languages card - Light theme (compact layout, 467px width)
          github-stats-card top-langs \
            --username ${{ github.repository_owner }} \
            --output img/top-langs-light.svg \
            --theme vue \
            --layout compact \
            --hide-border \
            --langs-count 8 \
            --weighting balanced
      
      - name: Commit and push if changed
        run: |
          git config --local user.email "github-actions[bot]@users.noreply.github.com"
          git config --local user.name "github-actions[bot]"
          git add img/*.svg
          git diff --staged --quiet || git commit -m "Update GitHub stats [skip ci]"
          git push
```

### GitHub Enterprise Server Support

This tool is compatible with GitHub Enterprise Server and other GitHub platforms. Use environment variables to configure custom API endpoints:

**Environment Variables:**
- `GITHUB_API_URL` - Custom REST API base URL (default: `https://api.github.com`)
- `GITHUB_GRAPHQL_URL` - Custom GraphQL endpoint URL (default: `https://api.github.com/graphql`)

**Usage Examples:**

```bash
# Using with GitHub Enterprise Server
export GITHUB_API_URL="https://github.enterprise.com/api/v3"
export GITHUB_GRAPHQL_URL="https://github.enterprise.com/api/graphql"
export GITHUB_TOKEN=ghp_your_enterprise_token

uv run github-stats-card stats -u your-username -o stats.svg
```

**In GitHub Actions:**

```yaml
- name: Generate GitHub Stats Card
  uses: stn1slv/github-stats-card@main
  env:
    GITHUB_API_URL: https://github.enterprise.com/api/v3
    GITHUB_GRAPHQL_URL: https://github.enterprise.com/api/graphql
  with:
    card-type: stats
    username: your-username
    token: ${{ secrets.GHE_TOKEN }}
    output: stats.svg
```

**Note:** If only `GITHUB_API_URL` is set, the GraphQL endpoint will automatically be constructed as `${GITHUB_API_URL}/graphql`. You can override this by explicitly setting `GITHUB_GRAPHQL_URL`.

Then add to your README:

```markdown
## My GitHub Stats

<div align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="img/github-stats-dark.svg">
    <source media="(prefers-color-scheme: light)" srcset="img/github-stats-light.svg">
    <img alt="GitHub Stats" src="img/github-stats-dark.svg">
  </picture>
  
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="img/top-langs-dark.svg">
    <source media="(prefers-color-scheme: light)" srcset="img/top-langs-light.svg">
    <img alt="Top Languages" src="img/top-langs-dark.svg">
  </picture>
</div>
```

## Development

### Setup

```bash
# Clone the repository
git clone https://github.com/yourusername/github-stats-card.git
cd github-stats-card

# Install with dev dependencies
uv pip install -e ".[dev]"
```

### Run Tests

```bash
uv run pytest
```

### Code Formatting

```bash
# Format code
uv run black src tests

# Lint
uv run ruff check src tests

# Type check
uv run mypy src
```

## Programmatic Usage (Python API)

You can use the library programmatically in your Python projects:

### Stats Card

```python
from src.fetcher import fetch_stats
from src.stats_card import render_stats_card
from src.config import StatsCardConfig

# Fetch stats
stats = fetch_stats(username="octocat", token="ghp_your_token")

# Create configuration
config = StatsCardConfig(
    theme="vue-dark",
    show_icons=True,
    hide_border=True,
    include_all_commits=True,
)

# Render SVG
svg = render_stats_card(stats, config)

# Save to file
with open("stats.svg", "w") as f:
    f.write(svg)
```

### Top Languages Card

```python
from src.langs_fetcher import fetch_top_languages
from src.langs_card import render_top_languages
from src.config import LangsCardConfig

# Fetch language stats with balanced weighting
langs = fetch_top_languages(
    username="octocat", 
    token="ghp_your_token",
    size_weight=0.7,  # 70% code size
    count_weight=0.3   # 30% repo count
)

# Create configuration (compact layout uses 467px width by default)
config = LangsCardConfig(
    theme="vue-dark",
    layout="compact",
    hide_border=True,
    langs_count=8,
)

# Render SVG
svg = render_top_languages(langs, config)

# Save to file
with open("top-langs.svg", "w") as f:
    f.write(svg)
```

### Configuration Objects

All configuration is done through dataclasses:

**StatsCardConfig** - 20 fields including:
- `theme`: Theme name (str)
- `show_icons`: Display icons (bool)
- `hide_border`: Hide card border (bool)
- `hide`: List of stats to hide (list[str])
- `show`: List of additional stats to show (list[str])
- `include_all_commits`: Include commits from all years (bool)
- `custom_title`: Custom card title (str | None)
- `title_color`, `text_color`, `icon_color`, `bg_color`: Custom colors (str | None)
- And more...

**LangsCardConfig** - 15 fields including:
- `theme`: Theme name (str)
- `layout`: Layout type - "normal", "compact", "donut", "donut-vertical", "pie" (str)
- `hide_border`: Hide card border (bool)
- `langs_count`: Number of languages to display (int)
- `hide`: List of languages to hide (list[str])
- `exclude_repo`: List of repos to exclude (list[str])
- `size_weight`, `count_weight`: Ranking weights (float)
- And more...

### Creating Config from CLI Args

You can also create configurations from CLI-style arguments:

```python
from src.config import StatsCardConfig

# From keyword arguments (like CLI options)
config = StatsCardConfig.from_cli_args(
    theme="vue-dark",
    show_icons=True,
    hide_border=True,
    hide="stars,prs",  # comma-separated string
    custom_title="My Stats"
)
```

## Architecture

The project is organized into focused modules:

**Core:**
- `cli.py` - Command-line interface with Click command group
- `config.py` - Configuration dataclasses (StatsCardConfig, LangsCardConfig)
- `card.py` - Base SVG card renderer
- `themes.py` - Theme definitions (50+ themes)
- `colors.py` - Color parsing and utilities
- `utils.py` - Utility functions
- `constants.py` - Centralized constants and magic numbers
- `exceptions.py` - Exception hierarchy

**Stats Card:**
- `fetcher.py` - GitHub GraphQL/REST API client for user stats
- `rank.py` - Rank calculation algorithm
- `stats_card.py` - Stats card SVG renderer
- `icons.py` - SVG icon definitions
- `i18n.py` - Internationalization

**Top Languages Card:**
- `langs_fetcher.py` - GitHub GraphQL API client for language stats
- `langs_card.py` - Top languages card SVG renderer (5 layouts)

## Credits

Inspired by [github-readme-stats](https://github.com/anuraghazra/github-readme-stats) by [@anuraghazra](https://github.com/anuraghazra).

This project is a Python CLI reimplementation designed for local generation and GitHub Actions usage.

## License

MIT License - see [LICENSE](LICENSE) file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

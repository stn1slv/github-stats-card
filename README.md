# GitHub Stats Card

A Python-based GitHub Action and CLI tool that generates beautiful, high-quality SVG statistics cards for your GitHub profile README.

[![GitHub Marketplace](https://img.shields.io/badge/Marketplace-GitHub_Action-blue.svg?logo=github&style=flat)](https://github.com/marketplace/actions/github-stats-cards)
[![Python 3.13+](https://img.shields.io/badge/python-3.13+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Tests](https://img.shields.io/badge/tests-67%20passed-success.svg)](#testing)

## 🚀 Get Started (GitHub Action)

The easiest way to use this tool is as a **GitHub Action**. It runs automatically on a schedule and updates your profile SVG files.

### 1. Add to your workflow

Create or update `.github/workflows/update-stats.yml`:

```yaml
name: Update GitHub Stats

on:
  schedule:
    - cron: '0 0 * * *'  # Daily at midnight UTC
  workflow_dispatch:      # Allow manual trigger

jobs:
  update-stats:
    runs-on: ubuntu-latest
    permissions:
      contents: write
    steps:
      - uses: actions/checkout@v4
      
      - name: Generate GitHub Stats Card
        uses: stn1slv/github-stats-card@v1.1.1
        with:
          card-type: stats
          username: ${{ github.repository_owner }}
          token: ${{ secrets.GITHUB_TOKEN }}
          output: img/github-stats.svg
          theme: vue-dark
          show-icons: true
      
      - name: Commit and push if changed
        run: |
          git config --local user.email "github-actions[bot]@users.noreply.github.com"
          git config --local user.name "github-actions[bot]"
          git add img/*.svg
          git diff --staged --quiet || git commit -m "Update GitHub stats [skip ci]"
          git push
```

### 2. Display in your README

Use the `<picture>` tag to support both **Dark** and **Light** modes automatically:

```markdown
<div align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="img/github-stats-dark.svg">
    <source media="(prefers-color-scheme: light)" srcset="img/github-stats-light.svg">
    <img alt="GitHub Stats" src="img/github-stats-dark.svg">
  </picture>
</div>
```

### 🔗 See it in Action
- **Demo Profile:** [stn1slv/stn1slv](https://github.com/stn1slv/stn1slv)
- **Example Workflow:** [refresh-stats.yml](https://github.com/stn1slv/stn1slv/blob/main/.github/workflows/refresh-stats.yml)

---

## ✨ Features

- 🎨 **50+ Built-in Themes** - Choose from a variety of beautiful color schemes
- 📊 **Comprehensive Stats** - Stars, commits, PRs, issues, reviews, and more
- 🔤 **Top Languages Card** - Show your most used programming languages with 5 layouts
- 🚀 **Top Contributions Card** - Show your impact on external repositories with rank levels
- ⚖️ **Smart Weighting** - Preset rankings (balanced, expertise, diversity) for language stats
- 📐 **Aligned Layouts** - Compact top-langs card matches stats card width (467px)
- 🔧 **Highly Customizable** - Customize colors, layout, and content
- 🚀 **GitHub Actions Ready** - Perfect for automated daily/weekly updates
- 🎯 **Local Generation** - No external service dependencies
- 🌐 **Internationalization** - Support for multiple languages (English included)

## 🎨 Available Themes

Choose from 50+ themes like `default`, `dark`, `radical`, `vue`, `tokyonight`, `dracula`, `monokai`, and more.

[**View all themes →**](src/rendering/themes.py)

---

## ⚙️ Configuration (GitHub Action)

### Common Inputs
| Input | Description | Default |
| :--- | :--- | :--- |
| `card-type` | Type of card: `stats`, `top-langs`, or `contrib` | **Required** |
| `username` | Your GitHub username | **Required** |
| `token` | GitHub PAT with `read:user` scope | **Required** |
| `output` | Output SVG file path | **Required** |
| `theme` | Theme name | `default` |
| `hide-border`| Hide card border | `false` |
| `card-width` | Card width in pixels | Varies |

### Card-Specific Inputs
Detailed configuration options are available for each card type:
- **Stats Card:** `show-icons`, `include-all-commits`, `hide`, `show`, `hide-rank`
- **Top Languages:** `layout` (normal/compact/donut/pie), `langs-count`, `weighting`, `exclude-repo`
- **Top Contributions:** `limit`, `exclude-repo`

[**View full configuration guide →**](EXAMPLES.md)

---

## 💻 CLI Usage

For local generation or manual usage, you can run the tool as a CLI.

### Installation

```bash
# Using uv (recommended)
uv pip install -e .

# Using pip
pip install -e .
```

### Quick Run (no installation)
```bash
export GITHUB_TOKEN=ghp_your_token
uv run github-stats-card stats -u your-username -o stats.svg
```

---

## 🌐 GitHub Enterprise Server Support

This tool is compatible with GitHub Enterprise Server. Configure custom API endpoints:

```yaml
- name: Generate GitHub Stats Card
  uses: stn1slv/github-stats-card@v1.1.1
  env:
    GITHUB_API_URL: https://github.enterprise.com/api/v3
  with:
    card-type: stats
    username: your-username
    token: ${{ secrets.GHE_TOKEN }}
    output: stats.svg
```

---

## 📚 Documentation & Contributing

- **[Detailed Examples](EXAMPLES.md)** - 13+ use cases and advanced configurations
- **[Contributing Guide](CONTRIBUTING.md)** - How to help improve this project
- **[Architecture](src/core/config.py)** - Overview of the codebase structure

## Credits
Inspired by [github-readme-stats](https://github.com/anuraghazra/github-readme-stats). This project is a Python CLI/Action reimplementation designed for reliability and privacy.

## License
MIT License - see [LICENSE](LICENSE) file for details.

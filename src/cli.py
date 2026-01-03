"""Command-line interface for GitHub Stats Card generator."""

import os
import sys
from typing import Union

import click

# Weighting presets for language ranking
WEIGHTING_PRESETS = {
    "size-only": {"size_weight": 1.0, "count_weight": 0.0},
    "balanced": {"size_weight": 0.7, "count_weight": 0.3},
    "expertise": {"size_weight": 0.5, "count_weight": 0.5},
    "diversity": {"size_weight": 0.4, "count_weight": 0.6},
}

from .config import FetchConfig, LangsFetchConfig, LangsCardConfig, StatsCardConfig
from .exceptions import FetchError, LanguageFetchError
from .fetcher import fetch_stats
from .langs_fetcher import fetch_top_languages
from .langs_card import render_top_languages
from .stats_card import render_stats_card


@click.group()
def cli():
    """GitHub Stats Card Generator - Create beautiful SVG stats cards for your GitHub profile."""
    pass


@cli.command(name="stats")
@click.option(
    "--username",
    "-u",
    required=True,
    help="GitHub username",
)
@click.option(
    "--token",
    "-t",
    envvar="GITHUB_TOKEN",
    required=True,
    help="GitHub Personal Access Token (or set GITHUB_TOKEN env var)",
)
@click.option(
    "--output",
    "-o",
    required=True,
    type=click.Path(),
    help="Output SVG file path",
)
@click.option(
    "--theme",
    default="default",
    help="Theme name (default, dark, radical, etc.)",
)
@click.option(
    "--show-icons",
    is_flag=True,
    help="Show icons next to stats",
)
@click.option(
    "--hide-border",
    is_flag=True,
    help="Hide card border",
)
@click.option(
    "--hide-title",
    is_flag=True,
    help="Hide card title",
)
@click.option(
    "--hide-rank",
    is_flag=True,
    help="Hide rank circle",
)
@click.option(
    "--include-all-commits",
    is_flag=True,
    help="Count all commits (not just current year)",
)
@click.option(
    "--commits-year",
    type=int,
    help="Filter commits to specific year (e.g., 2023)",
)
@click.option(
    "--hide",
    default="",
    help="Comma-separated stats to hide (e.g., stars,prs)",
)
@click.option(
    "--show",
    default="",
    help="Comma-separated additional stats to show (e.g., reviews,discussions_started)",
)
@click.option(
    "--title-color",
    help="Custom title color (hex without #)",
)
@click.option(
    "--text-color",
    help="Custom text color (hex without #)",
)
@click.option(
    "--icon-color",
    help="Custom icon color (hex without #)",
)
@click.option(
    "--bg-color",
    help="Custom background color (hex without # or gradient: angle,color1,color2)",
)
@click.option(
    "--border-color",
    help="Custom border color (hex without #)",
)
@click.option(
    "--ring-color",
    help="Custom rank ring color (hex without #)",
)
@click.option(
    "--custom-title",
    help="Custom card title text",
)
@click.option(
    "--locale",
    default="en",
    help="Language locale (default: en)",
)
@click.option(
    "--card-width",
    type=int,
    help="Card width in pixels",
)
@click.option(
    "--line-height",
    type=int,
    default=25,
    help="Line height between stats (default: 25)",
)
@click.option(
    "--border-radius",
    type=float,
    default=4.5,
    help="Border radius (default: 4.5)",
)
@click.option(
    "--number-format",
    type=click.Choice(["short", "long"]),
    default="short",
    help="Number format: short (6.6k) or long (6626)",
)
@click.option(
    "--number-precision",
    type=int,
    help="Decimal places for short format (0-2)",
)
@click.option(
    "--rank-icon",
    type=click.Choice(["default", "github", "percentile"]),
    default="default",
    help="Rank icon style",
)
@click.option(
    "--disable-animations",
    is_flag=True,
    help="Disable CSS animations",
)
@click.option(
    "--text-bold/--no-text-bold",
    default=True,
    help="Use bold text (default: yes)",
)
def stats(
    username: str,
    token: str,
    output: str,
    theme: str,
    show_icons: bool,
    hide_border: bool,
    hide_title: bool,
    hide_rank: bool,
    include_all_commits: bool,
    commits_year: Union[int, None],
    hide: str,
    show: str,
    title_color: Union[str, None],
    text_color: Union[str, None],
    icon_color: Union[str, None],
    bg_color: Union[str, None],
    border_color: Union[str, None],
    ring_color: Union[str, None],
    custom_title: Union[str, None],
    locale: str,
    card_width: Union[int, None],
    line_height: int,
    border_radius: float,
    number_format: str,
    number_precision: Union[int, None],
    rank_icon: str,
    disable_animations: bool,
    text_bold: bool,
) -> None:
    """
    Generate GitHub Stats Card SVG.
    
    This tool fetches your GitHub statistics and generates a beautiful
    SVG card that you can embed in your README.md or profile.
    
    Examples:
    
      # Basic usage with environment variable
      export GITHUB_TOKEN=ghp_xxxxx
      github-stats-card -u octocat -o stats.svg
      
      # With theme and custom options
      github-stats-card -u octocat -o stats.svg --theme vue-dark \\
        --show-icons --hide-border --include-all-commits
      
      # Hide specific stats
      github-stats-card -u octocat -o stats.svg --hide stars,prs
      
      # Show additional stats
      github-stats-card -u octocat -o stats.svg --show reviews,discussions_started
    """
    try:
        # Create fetch configuration
        fetch_config = FetchConfig.from_cli_args(
            username=username,
            token=token,
            include_all_commits=include_all_commits,
            commits_year=commits_year,
            show=show,
        )

        # Fetch stats from GitHub
        click.echo(f"Fetching GitHub stats for {username}...", err=True)
        stats = fetch_stats(
            username=fetch_config.username,
            token=fetch_config.token,
            include_all_commits=fetch_config.include_all_commits,
            commits_year=fetch_config.commits_year,
            show=fetch_config.show,
        )

        click.echo(f"Found stats for {stats['name']} (@{stats['login']})", err=True)

        # Create rendering configuration
        render_config = StatsCardConfig.from_cli_args(
            theme=theme,
            show_icons=show_icons,
            hide_border=hide_border,
            hide_title=hide_title,
            hide_rank=hide_rank,
            include_all_commits=include_all_commits,
            hide=hide,
            show=show,
            title_color=title_color,
            text_color=text_color,
            icon_color=icon_color,
            bg_color=bg_color,
            border_color=border_color,
            ring_color=ring_color,
            custom_title=custom_title,
            locale=locale,
            card_width=card_width,
            line_height=line_height,
            border_radius=border_radius,
            number_format=number_format,
            number_precision=number_precision,
            rank_icon=rank_icon,
            disable_animations=disable_animations,
            text_bold=text_bold,
        )

        # Render SVG card
        click.echo("Generating SVG card...", err=True)
        svg = render_stats_card(stats, render_config)

        # Write to file
        output_path = os.path.abspath(output)
        os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)

        with open(output_path, "w", encoding="utf-8") as f:
            f.write(svg)

        click.echo(f"✅ Generated {output_path}", err=True)

    except FetchError as e:
        click.echo(f"❌ Error fetching data: {e}", err=True)
        sys.exit(1)
    except Exception as e:
        click.echo(f"❌ Unexpected error: {e}", err=True)
        sys.exit(1)


@cli.command(name="top-langs")
@click.option(
    "--username",
    "-u",
    required=True,
    help="GitHub username",
)
@click.option(
    "--token",
    "-t",
    envvar="GITHUB_TOKEN",
    required=True,
    help="GitHub Personal Access Token (or set GITHUB_TOKEN env var)",
)
@click.option(
    "--output",
    "-o",
    required=True,
    type=click.Path(),
    help="Output SVG file path",
)
@click.option(
    "--theme",
    default="default",
    help="Theme name (default, dark, radical, etc.)",
)
@click.option(
    "--hide-border",
    is_flag=True,
    help="Hide card border",
)
@click.option(
    "--hide-title",
    is_flag=True,
    help="Hide card title",
)
@click.option(
    "--hide-progress",
    is_flag=True,
    help="Hide progress bars",
)
@click.option(
    "--layout",
    type=click.Choice(["normal", "compact", "donut", "donut-vertical", "pie"]),
    default="normal",
    help="Card layout style",
)
@click.option(
    "--langs-count",
    type=int,
    help="Number of languages to show (1-20)",
)
@click.option(
    "--hide",
    default="",
    help="Comma-separated languages to hide (e.g., HTML,CSS)",
)
@click.option(
    "--exclude-repo",
    default="",
    help="Comma-separated repos to exclude",
)
@click.option(
    "--weighting",
    type=click.Choice(["size-only", "balanced", "expertise", "diversity"]),
    help="Weighting preset: size-only (default), balanced (70/30), expertise (50/50), diversity (40/60)",
)
@click.option(
    "--size-weight",
    type=float,
    help="Weight for byte count in ranking (overrides --weighting, default: 1.0)",
)
@click.option(
    "--count-weight",
    type=float,
    help="Weight for repo count in ranking (overrides --weighting, default: 0.0)",
)
@click.option(
    "--card-width",
    type=int,
    help="Card width in pixels (min: 280)",
)
@click.option(
    "--title-color",
    help="Custom title color (hex without #)",
)
@click.option(
    "--text-color",
    help="Custom text color (hex without #)",
)
@click.option(
    "--bg-color",
    help="Custom background color or gradient (hex or angle,color1,color2)",
)
@click.option(
    "--border-color",
    help="Custom border color (hex without #)",
)
@click.option(
    "--custom-title",
    help="Custom card title",
)
@click.option(
    "--border-radius",
    type=float,
    default=4.5,
    help="Border radius (default: 4.5)",
)
@click.option(
    "--stats-format",
    type=click.Choice(["percentages", "bytes"]),
    default="percentages",
    help="Display format for stats",
)
@click.option(
    "--disable-animations",
    is_flag=True,
    help="Disable CSS animations",
)
def top_langs(
    username: str,
    token: str,
    output: str,
    theme: str,
    hide_border: bool,
    hide_title: bool,
    hide_progress: bool,
    layout: str,
    langs_count: Union[int, None],
    hide: str,
    exclude_repo: str,
    weighting: Union[str, None],
    size_weight: Union[float, None],
    count_weight: Union[float, None],
    card_width: Union[int, None],
    title_color: Union[str, None],
    text_color: Union[str, None],
    bg_color: Union[str, None],
    border_color: Union[str, None],
    custom_title: Union[str, None],
    border_radius: float,
    stats_format: str,
    disable_animations: bool,
) -> None:
    """
    Generate Top Languages Card SVG.
    
    This tool fetches programming languages from your GitHub repositories
    and generates a beautiful SVG card showing language distribution.
    
    Examples:
      
      # Basic usage
      github-stats-card top-langs -u octocat -o top-langs.svg
      
      # Compact layout with dark theme
      github-stats-card top-langs -u octocat -o langs.svg \\
        --layout compact --theme vue-dark --hide-border
      
      # Donut chart, hide specific languages
      github-stats-card top-langs -u octocat -o langs.svg \\
        --layout donut --hide "HTML,CSS,Makefile" --langs-count 8
      
      # Balanced size and repo count weighting
      github-stats-card top-langs -u octocat -o langs.svg \\
        --size-weight 0.5 --count-weight 0.5
      
      # Use weighting preset
      github-stats-card top-langs -u octocat -o langs.svg \\
        --weighting balanced
    """
    try:
        # Resolve weighting preset if specified
        final_size_weight = size_weight
        final_count_weight = count_weight
        
        if weighting:
            preset = WEIGHTING_PRESETS[weighting]
            # Only use preset values if individual weights not specified
            if size_weight is None:
                final_size_weight = preset["size_weight"]
            if count_weight is None:
                final_count_weight = preset["count_weight"]
        
        # Apply defaults if still None
        if final_size_weight is None:
            final_size_weight = 1.0
        if final_count_weight is None:
            final_count_weight = 0.0
        
        # Create fetch configuration
        fetch_config = LangsFetchConfig.from_cli_args(
            username=username,
            token=token,
            exclude_repo=exclude_repo,
            size_weight=final_size_weight,
            count_weight=final_count_weight,
        )

        # Fetch languages from GitHub
        click.echo(f"Fetching language data for {username}...", err=True)
        top_languages = fetch_top_languages(
            username=fetch_config.username,
            token=fetch_config.token,
            exclude_repo=fetch_config.exclude_repo,
            size_weight=fetch_config.size_weight,
            count_weight=fetch_config.count_weight,
        )

        if not top_languages:
            click.echo("⚠️  No languages found", err=True)
        else:
            click.echo(
                f"Found {len(top_languages)} languages across repositories", err=True
            )

        # Create rendering configuration
        render_config = LangsCardConfig.from_cli_args(
            hide=hide,
            hide_title=hide_title,
            hide_border=hide_border,
            hide_progress=hide_progress,
            card_width=card_width,
            layout=layout,
            langs_count=langs_count,
            theme=theme,
            custom_title=custom_title,
            title_color=title_color,
            text_color=text_color,
            bg_color=bg_color,
            border_color=border_color,
            border_radius=border_radius,
            stats_format=stats_format,
            disable_animations=disable_animations,
        )

        # Render SVG card
        click.echo("Generating SVG card...", err=True)
        svg = render_top_languages(top_languages, render_config)

        # Write to file
        output_path = os.path.abspath(output)
        os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)

        with open(output_path, "w", encoding="utf-8") as f:
            f.write(svg)

        click.echo(f"✅ Generated {output_path}", err=True)

    except LanguageFetchError as e:
        click.echo(f"❌ Error fetching language data: {e}", err=True)
        sys.exit(1)
    except Exception as e:
        click.echo(f"❌ Unexpected error: {e}", err=True)
        sys.exit(1)


if __name__ == "__main__":
    cli()

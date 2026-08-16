"""Command-line interface for GitHub Stats Card generator."""

import logging
import os
import sys

import click

from .core.config import (
    ContribCardConfig,
    ContribFetchConfig,
    LangsCardConfig,
    LangsFetchConfig,
    UserStatsCardConfig,
    UserStatsFetchConfig,
)
from .core.constants import VALID_CONTRIB_TYPES
from .core.exceptions import FetchError, LanguageFetchError
from .core.i18n import TRANSLATIONS
from .github.fetcher import fetch_contributor_stats, fetch_user_stats
from .github.langs_fetcher import fetch_top_languages
from .rendering.contrib import render_contrib_card
from .rendering.langs import render_top_languages
from .rendering.user_stats import render_user_stats_card

# Weighting presets for language ranking
WEIGHTING_PRESETS = {
    "size-only": {"size_weight": 1.0, "count_weight": 0.0},
    "balanced": {"size_weight": 0.7, "count_weight": 0.3},
    "expertise": {"size_weight": 0.5, "count_weight": 0.5},
    "diversity": {"size_weight": 0.4, "count_weight": 0.6},
}


# Command aliases for backward compatibility
COMMAND_ALIASES = {
    "stats": "user-stats",
}


class AliasGroup(click.Group):
    """Click group that supports command aliases for backward compatibility."""

    def get_command(self, ctx: click.Context, cmd_name: str) -> click.Command | None:
        # Resolve alias to canonical name
        canonical = COMMAND_ALIASES.get(cmd_name, cmd_name)
        return super().get_command(ctx, canonical)

    def resolve_command(
        self, ctx: click.Context, args: list[str]
    ) -> tuple[str | None, click.Command | None, list[str]]:
        cmd_name, cmd, remaining = super().resolve_command(ctx, args)
        # Resolve alias so help text shows the canonical name
        if cmd_name and cmd_name in COMMAND_ALIASES:
            canonical = COMMAND_ALIASES[cmd_name]
            cmd = super().get_command(ctx, canonical)
            cmd_name = canonical
        return cmd_name, cmd, remaining


def _configure_logging(debug: bool) -> None:
    """
    Route this package's warnings to stderr so partial results are never silent.

    The fetchers degrade rather than fail when a page or a supplementary query
    errors. Without a handler those warnings are discarded and the card renders
    with quietly wrong numbers.

    The handler is attached to this package's logger rather than through
    ``logging.basicConfig``: basicConfig is a no-op once the root logger already
    has a handler, which would make --debug silently ineffective inside a host
    process, and raising the *root* level would also turn on httpx and httpcore
    debug output that has nothing to do with fetch diagnostics.
    """
    package_logger = logging.getLogger(__name__.split(".", 1)[0])

    handler = logging.StreamHandler(sys.stderr)
    handler.setFormatter(logging.Formatter("%(levelname)s %(name)s: %(message)s"))

    # Idempotent: repeated invocations (tests, embedded use) must not stack handlers
    for existing in list(package_logger.handlers):
        package_logger.removeHandler(existing)
    package_logger.addHandler(handler)
    package_logger.setLevel(logging.DEBUG if debug else logging.WARNING)
    package_logger.propagate = False


def _abort(error: Exception, debug: bool) -> None:
    """Report an unexpected error and exit, or re-raise it when --debug is set."""
    if debug:
        raise error
    click.echo(f"❌ Unexpected error: {error}", err=True)
    click.echo("Re-run with --debug for the full traceback.", err=True)
    sys.exit(1)


def _write_svg_file(svg: str, output: str) -> None:
    """Write SVG content to file, creating parent directories as needed."""
    output_path = os.path.abspath(output)
    os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(svg)

    click.echo(f"✅ Generated {output_path}", err=True)


@click.group(cls=AliasGroup)
def cli() -> None:
    """GitHub Stats Card Generator - Create beautiful SVG stats cards for your GitHub profile."""


@cli.command(name="user-stats")
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
    help="Comma-separated stats to show (e.g., repos, reviews, prs_merged, discussions_started, discussions_answered)",
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
    # Choices come from TRANSLATIONS so the CLI cannot advertise a locale that
    # has no strings. An unknown value used to fall back to English in silence.
    type=click.Choice(sorted(TRANSLATIONS)),
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
    type=click.IntRange(0, 2),
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
@click.option(
    "--debug",
    is_flag=True,
    help="Show the full traceback on an unexpected error and log fetch diagnostics",
)
def user_stats(
    username: str,
    token: str,
    output: str,
    theme: str,
    show_icons: bool,
    hide_border: bool,
    hide_title: bool,
    hide_rank: bool,
    include_all_commits: bool,
    commits_year: int | None,
    hide: str,
    show: str,
    title_color: str | None,
    text_color: str | None,
    icon_color: str | None,
    bg_color: str | None,
    border_color: str | None,
    ring_color: str | None,
    custom_title: str | None,
    locale: str,
    card_width: int | None,
    line_height: int,
    border_radius: float,
    number_format: str,
    number_precision: int | None,
    rank_icon: str,
    disable_animations: bool,
    text_bold: bool,
    debug: bool,
) -> None:
    """
    Generate GitHub User Stats Card SVG.

    This tool fetches your GitHub statistics and generates a beautiful
    SVG card that you can embed in your README.md or profile.

    Examples:

      # Basic usage with environment variable
      export GITHUB_TOKEN=ghp_xxxxx
      github-stats-card user-stats -u octocat -o stats.svg

      # With theme and custom options
      github-stats-card user-stats -u octocat -o stats.svg --theme vue-dark \\
        --show-icons --hide-border --include-all-commits

      # Hide specific stats
      github-stats-card user-stats -u octocat -o stats.svg --hide stars,prs

      # Show additional stats (repos = total owned repositories)
      github-stats-card user-stats -u octocat -o stats.svg --show repos,reviews,discussions_started

      # Backward-compatible alias
      github-stats-card stats -u octocat -o stats.svg
    """
    _configure_logging(debug)

    # --include-all-commits replaces the commit count with an all-time search
    # total, which would silently discard the year filter.
    if include_all_commits and commits_year is not None:
        raise click.BadParameter("--include-all-commits and --commits-year cannot be combined.")

    try:
        # Create fetch configuration
        fetch_config = UserStatsFetchConfig.from_cli_args(
            username=username,
            token=token,
            include_all_commits=include_all_commits,
            commits_year=commits_year,
            show=show,
        )

        # Fetch stats from GitHub
        click.echo(f"Fetching GitHub stats for {username}...", err=True)
        user_stats_data = fetch_user_stats(fetch_config)

        click.echo(f"Found stats for {user_stats_data['name']} (@{user_stats_data['login']})", err=True)

        # Create rendering configuration
        render_config = UserStatsCardConfig.from_cli_args(
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
        svg = render_user_stats_card(user_stats_data, render_config)
        _write_svg_file(svg, output)

    except FetchError as e:
        click.echo(f"❌ Error fetching data: {e}", err=True)
        if token.startswith("ghs_") or "Resource not accessible by integration" in str(e):
            click.echo(
                "⚠️ Note: the user-stats card needs a token that can read contribution data "
                "(contributionsCollection), which the GitHub Actions default GITHUB_TOKEN cannot access.\n"
                "Please use a Personal Access Token (PAT with 'read:user' scope) stored as a repository "
                "secret and pass it via the `token` input.",
                err=True,
            )
        sys.exit(1)
    except Exception as e:
        _abort(e, debug)


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
    # Bounded: the weight is an exponent (size ** weight), so a large value
    # overflows to an OverflowError and a negative one inverts the ranking.
    type=click.FloatRange(0.0, 2.0),
    help="Weight for byte count in ranking, 0.0-2.0 (overrides --weighting, default: 1.0)",
)
@click.option(
    "--count-weight",
    type=click.FloatRange(0.0, 2.0),
    help="Weight for repo count in ranking, 0.0-2.0 (overrides --weighting, default: 0.0)",
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
@click.option(
    "--debug",
    is_flag=True,
    help="Show the full traceback on an unexpected error and log fetch diagnostics",
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
    langs_count: int | None,
    hide: str,
    exclude_repo: str,
    weighting: str | None,
    size_weight: float | None,
    count_weight: float | None,
    card_width: int | None,
    title_color: str | None,
    text_color: str | None,
    bg_color: str | None,
    border_color: str | None,
    custom_title: str | None,
    border_radius: float,
    stats_format: str,
    disable_animations: bool,
    debug: bool,
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
    _configure_logging(debug)

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
        top_languages = fetch_top_languages(fetch_config)

        if not top_languages:
            click.echo("⚠️  No languages found", err=True)
        else:
            click.echo(f"Found {len(top_languages)} languages across repositories", err=True)

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
        _write_svg_file(svg, output)

    except LanguageFetchError as e:
        click.echo(f"❌ Error fetching language data: {e}", err=True)
        sys.exit(1)
    except Exception as e:
        _abort(e, debug)


@cli.command(name="contrib")
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
    "--limit",
    "-l",
    # Bounded below: the value is used as a list slice, so 0 renders an empty
    # card and a negative value silently drops repositories from the end.
    type=click.IntRange(min=1),
    default=10,
    help="Number of repositories to show (default: 10)",
)
@click.option(
    "--exclude-repo",
    default="",
    help="Comma-separated repos to exclude",
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
    "--card-width",
    type=int,
    help="Card width in pixels (default: 467)",
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
    help="Custom background color (hex without # or gradient)",
)
@click.option(
    "--border-color",
    help="Custom border color (hex without #)",
)
@click.option(
    "--custom-title",
    help="Custom card title text",
)
@click.option(
    "--border-radius",
    type=float,
    default=4.5,
    help="Border radius (default: 4.5)",
)
@click.option(
    "--disable-animations",
    is_flag=True,
    help="Disable CSS animations",
)
@click.option(
    "--types",
    "--contrib-types",
    "contribution_types",
    default="commits,prs",
    help="Comma-separated list of contribution types to fetch: commits, prs, issues, reviews (default: commits,prs)",
)
@click.option(
    "--debug",
    is_flag=True,
    help="Show the full traceback on an unexpected error and log fetch diagnostics",
)
def contrib(
    username: str,
    token: str,
    output: str,
    limit: int,
    exclude_repo: str,
    theme: str,
    hide_border: bool,
    hide_title: bool,
    card_width: int | None,
    title_color: str | None,
    text_color: str | None,
    bg_color: str | None,
    border_color: str | None,
    custom_title: str | None,
    border_radius: float,
    disable_animations: bool,
    contribution_types: str,
    debug: bool,
) -> None:
    """
    Generate Top Contributions Card SVG.

    This tool fetches repositories you have contributed to (excluding your own)
    and generates an SVG card sorted by star count.

    Examples:

      # Basic usage
      github-stats-card contrib -u octocat -o contrib.svg

      # Top 5 contributions with dark theme
      github-stats-card contrib -u octocat -o contrib.svg \\
        --theme vue-dark --limit 5

      # Exclude specific repositories
      github-stats-card contrib -u octocat -o contrib.svg \\
        --exclude-repo "facebook/react,microsoft/vscode"
    """
    _configure_logging(debug)

    # Validate contribution types (outside try so Click handles BadParameter natively)
    parsed_types = [t.strip() for t in contribution_types.split(",") if t.strip()]
    if not parsed_types:
        raise click.BadParameter(
            f"At least one contribution type is required. Allowed: {', '.join(sorted(VALID_CONTRIB_TYPES))}"
        )
    for c_type in parsed_types:
        if c_type not in VALID_CONTRIB_TYPES:
            raise click.BadParameter(
                f"Invalid contribution type '{c_type}'. Allowed: {', '.join(sorted(VALID_CONTRIB_TYPES))}"
            )

    try:
        # Create fetch configuration (pass parsed list to avoid double-parsing)
        fetch_config = ContribFetchConfig.from_cli_args(
            username=username,
            token=token,
            limit=limit,
            exclude_repo=exclude_repo,
            contribution_types=parsed_types,
        )

        # Fetch stats from GitHub
        click.echo(f"Fetching contribution stats for {username}...", err=True)
        stats = fetch_contributor_stats(fetch_config)

        click.echo(f"Found {len(stats['repos'])} repositories", err=True)
        if len(stats["repos"]) == 0 and token.startswith("ghs_"):
            click.echo(
                "⚠️ Note: GitHub Actions default GITHUB_TOKEN cannot access cross-repository contribution breakdowns "
                "due to GitHub API scope restrictions.\nTo display external contributions on the contrib card, "
                "please use a Personal Access Token (PAT with 'read:user' scope) stored as a repository secret.",
                err=True,
            )

        # Create rendering configuration
        render_config = ContribCardConfig.from_cli_args(
            theme=theme,
            hide_border=hide_border,
            hide_title=hide_title,
            card_width=card_width,
            title_color=title_color,
            text_color=text_color,
            bg_color=bg_color,
            border_color=border_color,
            custom_title=custom_title,
            border_radius=border_radius,
            disable_animations=disable_animations,
        )

        # Render SVG card
        click.echo("Generating SVG card...", err=True)
        svg = render_contrib_card(stats, render_config)
        _write_svg_file(svg, output)

    except FetchError as e:
        click.echo(f"❌ Error fetching data: {e}", err=True)
        sys.exit(1)
    except Exception as e:
        _abort(e, debug)


if __name__ == "__main__":
    cli()

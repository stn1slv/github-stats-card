"""Stats card SVG renderer with all customization options."""

from typing import Any

from .base import render_card
from .colors import get_card_colors
from ..core.config import StatsCardConfig
from ..core.constants import (
    ANIMATION_INITIAL_DELAY_MS,
    ANIMATION_STAGGER_DELAY_MS,
    RANK_CIRCLE_X_OFFSET,
    RANK_CIRCLE_Y_OFFSET,
    STAT_LABEL_X_BASE,
    STAT_LABEL_X_WITH_ICON,
    STAT_VALUE_X_POSITION,
    STATS_CARD_BASE_HEIGHT,
)
from ..github.fetcher import UserStats
from ..core.i18n import get_translation
from .icons import get_icon_svg
from ..github.rank import calculate_rank
from ..core.utils import encode_html, k_formatter


def _get_stat_definitions(stats: UserStats, locale: str) -> dict[str, dict[str, Any]]:
    """Get all available stat definitions."""
    return {
        "stars": {
            "label": get_translation("statcard_totalstars", locale),
            "value": stats["totalStars"],
            "icon": "star",
        },
        "commits": {
            "label": get_translation("statcard_commits", locale),
            "value": stats["totalCommits"],
            "icon": "commits",
        },
        "prs": {
            "label": get_translation("statcard_prs", locale),
            "value": stats["totalPRs"],
            "icon": "prs",
        },
        "prs_merged": {
            "label": get_translation("statcard_prs_merged", locale),
            "value": stats["mergedPRs"],
            "icon": "prs_merged",
        },
        "prs_merged_percentage": {
            "label": get_translation("statcard_prs_merged_percentage", locale),
            "value": f"{(stats['mergedPRs'] / stats['totalPRs'] * 100) if stats['totalPRs'] > 0 else 0:.1f}%",
            "icon": "prs_merged",
            "skip_format": True,
        },
        "issues": {
            "label": get_translation("statcard_issues", locale),
            "value": stats["totalIssues"],
            "icon": "issues",
        },
        "contribs": {
            "label": get_translation("statcard_contribs", locale),
            "value": stats["contributedTo"],
            "icon": "contribs",
        },
        "reviews": {
            "label": get_translation("statcard_reviews", locale),
            "value": stats["totalReviews"],
            "icon": "reviews",
        },
        "discussions_started": {
            "label": get_translation("statcard_discussions_started", locale),
            "value": stats["discussionsStarted"],
            "icon": "discussions_started",
        },
        "discussions_answered": {
            "label": get_translation("statcard_discussions_answered", locale),
            "value": stats["discussionsAnswered"],
            "icon": "discussions_answered",
        },
    }


def render_stats_card(stats: UserStats, config: StatsCardConfig) -> str:
    """
    Render GitHub stats card as SVG.

    Args:
        stats: User statistics dictionary from fetcher
        config: Configuration object with all rendering options

    Returns:
        Complete SVG markup as string
    """
    # Get resolved colors
    colors = get_card_colors(
        theme=config.theme,
        title_color=config.title_color,
        text_color=config.text_color,
        icon_color=config.icon_color,
        bg_color=config.bg_color,
        border_color=config.border_color,
        ring_color=config.ring_color,
    )

    # Calculate rank
    rank_result = calculate_rank(
        commits=stats["totalCommits"],
        prs=stats["totalPRs"],
        issues=stats["totalIssues"],
        reviews=stats["totalReviews"],
        stars=stats["totalStars"],
        followers=stats["followers"],
        all_commits=config.include_all_commits,
    )

    # Determine title
    title = config.custom_title or get_translation(
        "statcard_title", config.locale, name=stats["name"]
    )

    # Build stat items
    all_stats = _get_stat_definitions(stats, config.locale)

    # Default stats to show
    default_stats = ["stars", "commits", "prs", "issues", "contribs"]

    # Determine which stats to display
    stats_to_show = [s for s in default_stats if s not in config.hide]

    # Add explicitly requested stats
    for stat_key in config.show:
        if stat_key in all_stats and stat_key not in stats_to_show:
            stats_to_show.append(stat_key)

    # Build stat items SVG
    stat_items = []
    for i, stat_key in enumerate(stats_to_show):
        stat = all_stats.get(stat_key)
        if not stat:
            continue

        label = encode_html(stat["label"])
        value = stat["value"]

        # Format value
        if not stat.get("skip_format"):
            if config.number_format == "short":
                formatted_value = k_formatter(int(value), config.number_precision)
            else:
                formatted_value = f"{int(value):,}"
        else:
            formatted_value = str(value)

        # Icon
        icon_svg = ""
        label_x = STAT_LABEL_X_BASE
        if config.show_icons:
            icon_svg = get_icon_svg(stat["icon"], colors["iconColor"])  # type: ignore
            label_x = STAT_LABEL_X_WITH_ICON

        # Animation delay starts at 450ms and increments by 150ms
        delay = ANIMATION_INITIAL_DELAY_MS + (i * ANIMATION_STAGGER_DELAY_MS)

        # Calculate value position (right-aligned)
        value_x = STAT_VALUE_X_POSITION

        bold_class = "bold" if config.text_bold else ""

        # Nested transform structure matching reference
        stat_svg = f"""<g transform="translate(0, {i * config.line_height})">
    <g class="stagger" style="animation-delay: {delay}ms" transform="translate(25, 0)">
      {icon_svg}
      <text class="stat {bold_class}" x="{label_x}" y="12.5">{label}:</text>
      <text class="stat {bold_class}" x="{value_x}" y="12.5">{formatted_value}</text>
    </g>
  </g>"""

        stat_items.append(stat_svg)

    # Rank circle
    rank_svg = ""
    if not config.hide_rank:
        rank_x = RANK_CIRCLE_X_OFFSET
        rank_y = RANK_CIRCLE_Y_OFFSET

        rank_svg = f"""
    <g data-testid="rank-circle"
          transform="translate({rank_x}, {rank_y})">
        <circle class="rank-circle-rim" cx="-10" cy="8" r="40" />
        <circle class="rank-circle" cx="-10" cy="8" r="40" />
        <g class="rank-text">
          <text x="-5" y="3" alignment-baseline="central" dominant-baseline="central" text-anchor="middle" data-testid="level-rank-icon">
          {rank_result['level']}
        </text>
        </g>
      </g>"""

    # Combine stat items wrapped in SVG structure
    stats_content = "\n".join(stat_items)
    body = f"""{rank_svg}
    <svg x="0" y="0">
      {stats_content}
    </svg>"""

    # Calculate card height to match reference
    num_stats = len(stat_items)
    card_height = (num_stats * config.line_height) + STATS_CARD_BASE_HEIGHT

    # Add 30px extra height when title is shown (55px offset vs 25px)
    if not config.hide_title:
        card_height += 30

    # Use provided width or default to 467 (matches reference)
    final_width = config.card_width or 467

    return render_card(
        title=title,
        body=body,
        width=final_width,
        height=card_height,
        colors=colors,
        hide_title=config.hide_title,
        hide_border=config.hide_border,
        border_radius=config.border_radius,
        disable_animations=config.disable_animations,
        a11y_title=title,
        a11y_desc=f"{stats['name']}'s GitHub statistics",
    )

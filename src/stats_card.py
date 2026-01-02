"""Stats card SVG renderer with all customization options."""

from typing import Union

from .card import render_card
from .colors import get_card_colors
from .constants import (
    ANIMATION_INITIAL_DELAY_MS,
    ANIMATION_STAGGER_DELAY_MS,
    RANK_CIRCLE_X_OFFSET,
    RANK_CIRCLE_Y_OFFSET,
    STAT_LABEL_X_BASE,
    STAT_LABEL_X_WITH_ICON,
    STAT_LINE_HEIGHT,
    STAT_VALUE_X_POSITION,
    STATS_CARD_BASE_HEIGHT,
)
from .fetcher import UserStats
from .i18n import get_translation
from .icons import get_icon_svg
from .rank import calculate_rank
from .utils import encode_html, k_formatter


def render_stats_card(
    stats: UserStats,
    theme: str = "default",
    hide: Union[list[str], None] = None,
    show: Union[list[str], None] = None,
    hide_title: bool = False,
    hide_border: bool = False,
    hide_rank: bool = False,
    show_icons: bool = False,
    title_color: Union[str, None] = None,
    text_color: Union[str, None] = None,
    icon_color: Union[str, None] = None,
    bg_color: Union[str, None] = None,
    border_color: Union[str, None] = None,
    ring_color: Union[str, None] = None,
    custom_title: Union[str, None] = None,
    locale: str = "en",
    card_width: Union[int, None] = None,
    line_height: int = 25,
    border_radius: float = 4.5,
    number_format: str = "short",
    number_precision: Union[int, None] = None,
    rank_icon: str = "default",
    disable_animations: bool = False,
    text_bold: bool = True,
    include_all_commits: bool = False,
) -> str:
    """
    Render GitHub stats card as SVG.

    Args:
        stats: User statistics dictionary from fetcher
        theme: Theme name
        hide: List of stats to hide (stars, commits, prs, issues, contribs)
        show: List of additional stats to show (reviews, discussions_started, etc.)
        hide_title: Hide card title
        hide_border: Hide card border
        hide_rank: Hide rank circle
        show_icons: Show icons next to stats
        title_color: Custom title color (hex without #)
        text_color: Custom text color
        icon_color: Custom icon color
        bg_color: Custom background color
        border_color: Custom border color
        ring_color: Custom rank ring color
        custom_title: Custom card title
        locale: Language locale
        card_width: Card width in pixels
        line_height: Line height between stats
        border_radius: Border radius
        number_format: 'short' (6.6k) or 'long' (6626)
        number_precision: Decimal places for short format
        rank_icon: Rank icon style
        disable_animations: Disable CSS animations
        text_bold: Use bold text
        include_all_commits: Whether commits are all-time

    Returns:
        Complete SVG markup as string
    """
    hide = hide or []
    show = show or []

    # Get resolved colors
    colors = get_card_colors(
        theme=theme,
        title_color=title_color,
        text_color=text_color,
        icon_color=icon_color,
        bg_color=bg_color,
        border_color=border_color,
        ring_color=ring_color,
    )

    # Calculate rank
    rank_result = calculate_rank(
        commits=stats["totalCommits"],
        prs=stats["totalPRs"],
        issues=stats["totalIssues"],
        reviews=stats["totalReviews"],
        stars=stats["totalStars"],
        followers=stats["followers"],
        all_commits=include_all_commits,
    )

    # Determine title
    title = custom_title or get_translation("statcard_title", locale, name=stats["name"])

    # Build stat items
    stat_items = []

    # Define available stats
    all_stats = {
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

    # Default stats to show
    default_stats = ["stars", "commits", "prs", "issues", "contribs"]

    # Determine which stats to display
    stats_to_show = []
    for stat_key in default_stats:
        if stat_key not in hide:
            stats_to_show.append(stat_key)

    # Add explicitly requested stats
    for stat_key in show:
        if stat_key in all_stats and stat_key not in stats_to_show:
            stats_to_show.append(stat_key)

    # Build stat items SVG
    for i, stat_key in enumerate(stats_to_show):
        stat = all_stats.get(stat_key)
        if not stat:
            continue

        label = encode_html(stat["label"])
        value = stat["value"]

        # Format value
        if not stat.get("skip_format"):
            if number_format == "short":
                if number_precision is not None:
                    formatted_value = k_formatter(int(value), number_precision)
                else:
                    formatted_value = k_formatter(int(value))
            else:
                formatted_value = f"{int(value):,}"
        else:
            formatted_value = str(value)

        # Icon
        icon_svg = ""
        label_x = STAT_LABEL_X_BASE
        if show_icons:
            icon_svg = get_icon_svg(stat["icon"], colors["iconColor"])
            label_x = STAT_LABEL_X_WITH_ICON

        # Animation delay starts at 450ms and increments by 150ms
        delay = ANIMATION_INITIAL_DELAY_MS + (i * ANIMATION_STAGGER_DELAY_MS)

        # Calculate value position (right-aligned)
        value_x = STAT_VALUE_X_POSITION  # Match reference position

        bold_class = "bold" if text_bold else ""

        # Nested transform structure matching reference
        stat_svg = f"""<g transform="translate(0, {i * line_height})">
    <g class="stagger" style="animation-delay: {delay}ms" transform="translate(25, 0)">
      {icon_svg}
      <text class="stat {bold_class}" x="{label_x}" y="12.5">{label}:</text>
      <text class="stat {bold_class}" x="{value_x}" y="12.5">{formatted_value}</text>
    </g>
  </g>"""

        stat_items.append(stat_svg)

    # Rank circle
    rank_svg = ""
    if not hide_rank:
        ring_color_value = colors.get("ringColor") or colors["titleColor"]
        if isinstance(ring_color_value, list):
            # Use first color from gradient
            ring_color_value = f"#{ring_color_value[1]}"

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
    # Reference: 165 height for 5 stats with no title
    # That's 5*25 = 125 + 40 = 165
    card_height = (num_stats * line_height) + STATS_CARD_BASE_HEIGHT

    # Use provided width or default to 467 (matches reference)
    final_width = card_width or 467

    return render_card(
        title=title,
        body=body,
        width=final_width,
        height=card_height,
        colors=colors,
        hide_title=hide_title,
        hide_border=hide_border,
        border_radius=border_radius,
        disable_animations=disable_animations,
        a11y_title=title,
        a11y_desc=f"{stats['name']}'s GitHub statistics",
    )

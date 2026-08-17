"""Contributor card renderer."""

from ..core.config import ContribCardConfig
from ..core.constants import MIN_CARD_WIDTH
from ..core.utils import encode_html
from ..github.fetcher import ContributorStats
from .base import render_card
from .colors import get_card_colors, resolve_color


def render_contrib_card(stats: ContributorStats, config: ContribCardConfig) -> str:
    """
    Render contributor statistics card.

    Args:
        stats: Contributor statistics
        config: Card configuration

    Returns:
        SVG string
    """
    colors = get_card_colors(
        theme=config.theme,
        title_color=config.title_color,
        text_color=config.text_color,
        bg_color=config.bg_color,
        border_color=config.border_color,
    )

    # The rank badge is placed relative to the right edge, so a width below the
    # minimum would drop it on top of the avatar and repo name. Clamp instead.
    card_width = max(config.card_width, MIN_CARD_WIDTH)

    # Calculate height based on number of repos
    # body_y_offset + items * 35 + padding (15)
    body_y_offset = 25 if config.hide_title else 55
    item_height = 35
    num_items = len(stats["repos"])
    height = body_y_offset + 45 if num_items == 0 else body_y_offset + (num_items * item_height) + 15

    # Generate body content
    body = []

    if num_items == 0:
        text_color = resolve_color(colors["text_color"])
        body.append(f'<text x="25" y="15" class="stat bold" fill="{text_color}">No contributions found</text>')
    else:
        # Avatar clip path definition (reused)
        # Using objectBoundingBox ensures the circle is always centered on the element
        body.append("""
        <defs>
            <clipPath id="avatar-clip" clipPathUnits="objectBoundingBox">
                <circle cx="0.5" cy="0.5" r="0.5" />
            </clipPath>
        </defs>
        """)

        for i, repo in enumerate(stats["repos"]):
            y_pos = i * item_height

            # Row group
            body.append(f'<g transform="translate(25, {y_pos})">')

            # 1. Avatar (centered vertically: (35-20)/2 = 7.5)
            if repo["avatar_b64"]:
                # Use embedded base64 image
                body.append(f"""
                <image x="0" y="7.5" width="20" height="20" clip-path="url(#avatar-clip)"
                       href="data:image/png;base64,{repo["avatar_b64"]}" />
                """)
            else:
                # Fallback circle
                body.append(f"""
                <circle cx="10" cy="17.5" r="10" fill="{resolve_color(colors["icon_color"])}" opacity="0.5" />
                """)

            # 2. Repo Name (centered vertically: baseline at ~22)
            full_name = repo["name"]
            display_name = full_name.split("/")[-1] if "/" in full_name else full_name
            name = encode_html(display_name)
            body.append(f"""
            <text x="30" y="22" class="stat bold">{name}</text>
            """)

            # 3. Rank Level (right aligned in a circle)
            right_edge = card_width - 75
            rank = repo["rank_level"]

            # Use ring color from theme or fallback to title color. `or` rather
            # than a .get default: a present-but-None value must fall back too.
            ring_color = resolve_color(colors.get("ring_color") or colors["title_color"])

            rank_size = 8 if len(rank) > 1 else 10

            body.append(f"""
            <g transform="translate({right_edge}, 7.5)">
                <circle cx="10" cy="10" r="12" stroke="{ring_color}" stroke-width="2" fill="none" opacity="0.2" />
                <text x="10" y="10" alignment-baseline="central" dominant-baseline="central"
                      text-anchor="middle" class="stat bold" style="font-size: {rank_size}px;">{rank}</text>
            </g>
            """)

            body.append("</g>")

    return render_card(
        title=config.custom_title or "Top Contributions",
        body="\n".join(body),
        width=card_width,
        height=height,
        colors=colors,
        hide_title=config.hide_title,
        hide_border=config.hide_border,
        border_radius=config.border_radius,
        disable_animations=config.disable_animations,
        a11y_title="Top Contributions Card",
        a11y_desc=f"List of top {num_items} repositories contributed to, sorted by stars.",
    )

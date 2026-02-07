"""Contributor card renderer."""


from ..core.config import ContribCardConfig
from ..core.utils import encode_html
from ..github.fetcher import ContributorStats
from .base import render_card
from .colors import get_card_colors


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

    # Calculate height based on number of repos
    # Header (55) + items * 30 + padding (15)
    item_height = 30
    num_items = len(stats["repos"])
    if num_items == 0:
        height = 100
    else:
        height = 55 + (num_items * item_height) + 15

    # Generate body content
    body = []
    
    if num_items == 0:
        text_color = colors["textColor"]
        body.append(
            f'<text x="25" y="15" class="stat bold" fill="{text_color}">No contributions found</text>'
        )
    else:
        # Avatar clip path definition (reused)
        body.append("""
        <defs>
            <clipPath id="avatar-clip">
                <circle cx="10" cy="10" r="10" />
            </clipPath>
        </defs>
        """)

        for i, repo in enumerate(stats["repos"]):
            y_pos = i * item_height
            
            # Row group
            body.append(f'<g transform="translate(25, {y_pos})">')
            
            # 1. Avatar
            if repo["avatar_b64"]:
                # Use embedded base64 image
                body.append(f"""
                <image x="0" y="-2" width="20" height="20" clip-path="url(#avatar-clip)" 
                       href="data:image/png;base64,{repo['avatar_b64']}" />
                """)
            else:
                # Fallback circle
                body.append(f"""
                <circle cx="10" cy="8" r="10" fill="{colors['iconColor']}" opacity="0.5" />
                """)

            # 2. Repo Name
            name = encode_html(repo["name"])
            body.append(f"""
            <text x="30" y="12.5" class="stat bold">{name}</text>
            """)

            # 3. Stars (right aligned)
            # Rough width calculation: 467 - 25 (left pad) - 25 (right pad)
            right_edge = config.card_width - 50
            stars = f"{repo['stars']:,}"
            body.append(f"""
            <g transform="translate({right_edge}, 12.5)">
                <text text-anchor="end" class="stat">{stars} ★</text>
            </g>
            """)
            
            body.append("</g>")

    return render_card(
        title=config.custom_title or "Top Contributions",
        body="\n".join(body),
        width=config.card_width,
        height=height,
        colors=colors,
        hide_border=config.hide_border,
        border_radius=config.border_radius,
        disable_animations=config.disable_animations,
        a11y_title="Top Contributions Card",
        a11y_desc=f"List of top {num_items} repositories contributed to, sorted by stars."
    )
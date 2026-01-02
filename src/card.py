"""Base SVG card renderer with common styling and structure."""

from typing import Union

from .colors import format_gradient
from .utils import encode_html


def render_card(
    title: str,
    body: str,
    width: int = 450,
    height: int = 200,
    colors: Union[dict[str, Union[str, list[str]]], None] = None,
    hide_title: bool = False,
    hide_border: bool = False,
    border_radius: float = 4.5,
    disable_animations: bool = False,
    a11y_title: str = "",
    a11y_desc: str = "",
) -> str:
    """
    Render base SVG card with title and body content.

    Args:
        title: Card title text
        body: SVG content for the card body
        width: Card width in pixels
        height: Card height in pixels
        colors: Color dictionary (titleColor, textColor, bgColor, borderColor, iconColor)
        hide_title: Whether to hide the title
        hide_border: Whether to hide the border
        border_radius: Border radius in pixels
        disable_animations: Whether to disable CSS animations
        a11y_title: Accessibility title
        a11y_desc: Accessibility description

    Returns:
        Complete SVG markup as string
    """
    colors = colors or {}

    title_color = colors.get("titleColor", "#2f80ed")
    text_color = colors.get("textColor", "#434d58")
    bg_color = colors.get("bgColor", "#fffefe")
    border_color = colors.get("borderColor", "#e4e2e2")
    icon_color = colors.get("iconColor", "#4c71f2")

    # Handle gradient background
    gradient_def = ""
    fill_color = bg_color

    if isinstance(bg_color, list):
        gradient_id, gradient_svg = format_gradient(bg_color)
        gradient_def = gradient_svg
        fill_color = f"url(#{gradient_id})"

    # CSS styles
    animation_css = ""
    if not disable_animations:
        animation_css = """
        .stagger {
          opacity: 0;
          animation: fadeInAnimation 0.3s ease-in-out forwards;
        }
        @keyframes fadeInAnimation {
          from {
            opacity: 0;
          }
          to {
            opacity: 1;
          }
        }
        """

    # Get ring color for rank circle CSS
    ring_color = colors.get("ringColor") or title_color
    if isinstance(ring_color, list):
        ring_color = f"#{ring_color[1]}"
    # Ensure ring color has # prefix
    if not ring_color.startswith("#"):
        ring_color = f"#{ring_color}"

    css = f"""
    <style>
      .header {{
        font: 600 18px 'Segoe UI', Ubuntu, Sans-Serif;
        fill: {title_color};
      }}
      .stat {{
        font: 600 14px 'Segoe UI', Ubuntu, "Helvetica Neue", Sans-Serif;
        fill: {text_color};
      }}
      .stat.bold {{
        font-weight: 700;
      }}
      .not_bold {{
        font-weight: 400;
      }}
      .icon {{
        fill: {icon_color};
        display: block;
      }}
      .rank-text {{
        font: 800 24px 'Segoe UI', Ubuntu, Sans-Serif;
        fill: {text_color};
        animation: scaleInAnimation 0.3s ease-in-out forwards;
      }}
      .rank-circle-rim {{
        stroke: {ring_color};
        fill: none;
        stroke-width: 6;
        opacity: 0.2;
      }}
      .rank-circle {{
        stroke: {ring_color};
        stroke-dasharray: 250;
        fill: none;
        stroke-width: 6;
        stroke-linecap: round;
        opacity: 0.8;
        transform-origin: -10px 8px;
        transform: rotate(-90deg);
      }}
      @keyframes scaleInAnimation {{
        from {{
          transform: translate(-5px, 5px) scale(0);
        }}
        to {{
          transform: translate(-5px, 5px) scale(1);
        }}
      }}
      {animation_css}
    </style>
    """

    # Encode title for safe XML embedding
    safe_title = encode_html(title)
    safe_a11y_title = encode_html(a11y_title or title)
    safe_a11y_desc = encode_html(a11y_desc or f"{title} statistics")

    # Title section
    title_section = ""
    if not hide_title:
        title_section = f"""
    <g transform="translate(25, 35)">
      <text class="header">{safe_title}</text>
    </g>
    """

    # Adjust body position based on title visibility
    body_y_offset = 55 if not hide_title else 25

    border_opacity = 0 if hide_border else 1

    svg = f"""<svg width="{width}" height="{height}" viewBox="0 0 {width} {height}"
     fill="none" xmlns="http://www.w3.org/2000/svg"
     role="img" aria-labelledby="titleId descId">
  <title id="titleId">{safe_a11y_title}</title>
  <desc id="descId">{safe_a11y_desc}</desc>
  {css}
  
  <defs>
    {gradient_def}
  </defs>
  
  <rect
    x="0.5"
    y="0.5"
    rx="{border_radius}"
    height="{height - 1}"
    stroke="{border_color}"
    width="{width - 1}"
    fill="{fill_color}"
    stroke-opacity="{border_opacity}"
  />
  
  {title_section}
  
  <g transform="translate(0, {body_y_offset})">
    {body}
  </g>
</svg>"""

    return svg

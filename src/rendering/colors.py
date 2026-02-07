"""Color parsing and validation utilities."""

import re

from .themes import THEMES


def is_valid_hex_color(color: str) -> bool:
    """
    Check if string is a valid hex color code.

    Args:
        color: Color string to validate (without # prefix)

    Returns:
        True if valid hex color (3, 4, 6, or 8 digits)
    """
    pattern = r"^([A-Fa-f0-9]{8}|[A-Fa-f0-9]{6}|[A-Fa-f0-9]{3}|[A-Fa-f0-9]{4})$"
    return bool(re.match(pattern, color))


def is_valid_gradient(colors: list[str]) -> bool:
    """
    Check if colors list represents a valid gradient.

    Args:
        colors: List of color strings (first element is angle, rest are hex colors)

    Returns:
        True if valid gradient specification
    """
    return len(colors) > 2 and all(is_valid_hex_color(c) for c in colors[1:])


def parse_color(color: str | None, fallback: str) -> str | list[str]:
    """
    Parse color string, supporting both solid colors and gradients.

    Args:
        color: Color string (hex or gradient: "angle,color1,color2,...")
        fallback: Fallback color if parsing fails

    Returns:
        Parsed color with # prefix, or list of colors for gradient

    Examples:
        >>> parse_color("2f80ed", "#000")
        '#2f80ed'
        >>> parse_color("90,ff0000,00ff00", "#000")
        ['90', 'ff0000', '00ff00']
    """
    if not color:
        return fallback

    # Check for gradient (comma-separated)
    colors = color.split(",")
    if len(colors) > 1 and is_valid_gradient(colors):
        return colors  # Return gradient specification

    # Single color
    if is_valid_hex_color(color):
        return f"#{color}"

    return fallback


def get_card_colors(
    theme: str = "default",
    title_color: str | None = None,
    text_color: str | None = None,
    icon_color: str | None = None,
    bg_color: str | None = None,
    border_color: str | None = None,
    ring_color: str | None = None,
) -> dict[str, str | list[str]]:
    """
    Get resolved colors with theme defaults and custom overrides.

    Args:
        theme: Theme name
        title_color: Custom title color (hex without #)
        text_color: Custom text color
        icon_color: Custom icon color
        bg_color: Custom background color (or gradient)
        border_color: Custom border color
        ring_color: Custom rank ring color

    Returns:
        Dictionary with resolved colors
    """
    selected_theme = THEMES.get(theme, THEMES["default"])
    default_theme = THEMES["default"]

    return {
        "titleColor": parse_color(
            title_color or selected_theme.get("title_color"),
            f"#{default_theme['title_color']}",
        ),
        "textColor": parse_color(
            text_color or selected_theme.get("text_color"),
            f"#{default_theme['text_color']}",
        ),
        "iconColor": parse_color(
            icon_color or selected_theme.get("icon_color"),
            f"#{default_theme['icon_color']}",
        ),
        "bgColor": parse_color(
            bg_color or selected_theme.get("bg_color"),
            f"#{default_theme['bg_color']}",
        ),
        "borderColor": parse_color(
            border_color or selected_theme.get("border_color", default_theme["border_color"]),
            f"#{default_theme['border_color']}",
        ),
        "ringColor": parse_color(
            ring_color or selected_theme.get("ring_color") or selected_theme.get("title_color"),
            f"#{default_theme['title_color']}",
        ),
    }


def format_gradient(colors: list[str]) -> tuple[str, str]:
    """
    Format gradient colors for SVG.

    Args:
        colors: List [angle, color1, color2, ...]

    Returns:
        Tuple of (gradient_id, gradient_svg_definition)
    """
    angle = colors[0]
    color_stops = colors[1:]

    # Convert angle to x1, y1, x2, y2 for linearGradient
    # Simplified: just use horizontal or vertical
    angle_num = int(angle) if angle.isdigit() else 0

    if 45 <= angle_num < 135:
        # Vertical
        x1, y1, x2, y2 = "0%", "0%", "0%", "100%"
    elif 135 <= angle_num < 225:
        # Horizontal (reversed)
        x1, y1, x2, y2 = "100%", "0%", "0%", "0%"
    elif 225 <= angle_num < 315:
        # Vertical (reversed)
        x1, y1, x2, y2 = "0%", "100%", "0%", "0%"
    else:
        # Horizontal (default)
        x1, y1, x2, y2 = "0%", "0%", "100%", "0%"

    stops = []
    step = 100 / (len(color_stops) - 1) if len(color_stops) > 1 else 100
    for i, color in enumerate(color_stops):
        offset = i * step
        stops.append(f'<stop offset="{offset}%" stop-color="#{color}" />')

    gradient_id = "gradient"
    gradient_svg = f"""
    <linearGradient id="{gradient_id}" x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}">
      {chr(10).join(stops)}
    </linearGradient>
    """

    return gradient_id, gradient_svg
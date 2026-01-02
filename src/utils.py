"""Utility functions for formatting and data manipulation."""

from typing import Union

from .constants import NUMBER_FORMAT_THOUSAND_DIVISOR


def k_formatter(num: int, precision: Union[int, None] = None) -> str:
    """
    Format number with K suffix for thousands.

    Args:
        num: The number to format
        precision: Optional decimal places (0-2) for short format

    Returns:
        Formatted string (e.g., "6.6k" or "6626")

    Examples:
        >>> k_formatter(1500)
        '1.5k'
        >>> k_formatter(999)
        '999'
        >>> k_formatter(6626, precision=1)
        '6.6k'
    """
    abs_num = abs(num)
    sign = -1 if num < 0 else 1

    if precision is not None and 0 <= precision <= 2:
        return f"{sign * abs_num / NUMBER_FORMAT_THOUSAND_DIVISOR:.{precision}f}k"

    if abs_num < NUMBER_FORMAT_THOUSAND_DIVISOR:
        return str(sign * abs_num)

    formatted = sign * round(abs_num / NUMBER_FORMAT_THOUSAND_DIVISOR, 1)
    # Remove trailing .0
    if formatted == int(formatted):
        return f"{int(formatted)}k"
    return f"{formatted}k"


def clamp_value(value: float, min_val: float, max_val: float) -> float:
    """
    Clamp value between min and max.

    Args:
        value: Value to clamp
        min_val: Minimum allowed value
        max_val: Maximum allowed value

    Returns:
        Clamped value
    """
    return max(min_val, min(value, max_val))


def encode_html(text: str) -> str:
    """
    Encode special HTML/XML characters for safe SVG embedding.

    Args:
        text: Text to encode

    Returns:
        Encoded text safe for XML/SVG
    """
    return (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
        .replace("'", "&#39;")
    )


def flex_layout(items: list[dict], gap: int, direction: str = "column") -> str:
    """
    Create flexbox-like layout for SVG elements.

    Args:
        items: List of items with 'height' or 'width' attributes
        gap: Gap between items
        direction: 'column' or 'row'

    Returns:
        Combined SVG elements with proper transforms
    """
    elements = []
    offset = 0

    for item in items:
        if direction == "column":
            elements.append(f'<g transform="translate(0, {offset})">{item["svg"]}</g>')
            offset += item.get("height", 0) + gap
        else:
            elements.append(f'<g transform="translate({offset}, 0)">{item["svg"]}</g>')
            offset += item.get("width", 0) + gap

    return "\n".join(elements)


def measure_text(text: str, font_size: int = 14) -> float:
    """
    Approximate text width in pixels.

    This is a rough approximation since we can't actually measure text in Python.
    Assumes monospace-like behavior for simplicity.

    Args:
        text: Text to measure
        font_size: Font size in pixels

    Returns:
        Approximate width in pixels
    """
    # Rough approximation: average character width is ~0.6 * font_size
    return len(text) * font_size * 0.6

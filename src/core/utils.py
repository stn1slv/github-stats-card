"""Utility functions for formatting and data manipulation."""

import fnmatch

from .constants import NUMBER_FORMAT_THOUSAND_DIVISOR


def k_formatter(num: int, precision: int | None = None) -> str:
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


def is_repo_excluded(repo_name: str, exclude_patterns: list[str]) -> bool:
    """
    Check if a repository should be excluded based on patterns.
    Supports wildcards using fnmatch (e.g., "awesome-*").
    If the pattern does not contain a '/', it matches against the repo name only.
    Matching is case-insensitive.

    Args:
        repo_name: Repository name (e.g., "owner/repo" or "repo")
        exclude_patterns: List of exclusion patterns

    Returns:
        True if the repo matches any pattern
    """
    repo_name = repo_name.lower()
    # Extract just the repo name part if repo_name is "owner/repo"
    repo_name_only = repo_name.split("/")[-1] if "/" in repo_name else repo_name

    for pattern in exclude_patterns:
        pattern = pattern.lower()
        # If pattern has no '/', match against the repo name only
        if "/" not in pattern:
            if fnmatch.fnmatch(repo_name_only, pattern):
                return True
        else:
            # If pattern has '/', match against the full provided repo_name
            if fnmatch.fnmatch(repo_name, pattern):
                return True
    return False


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


def parse_list_arg(arg: str | list[str] | None) -> list[str]:
    """
    Parse a comma-separated string or list into a list of strings.

    Args:
        arg: Comma-separated string, list of strings, or None

    Returns:
        List of stripped strings
    """
    if arg is None:
        return []
    if isinstance(arg, list):
        return [str(s).strip() for s in arg if str(s).strip()]
    return [s.strip() for s in arg.split(",") if s.strip()]


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

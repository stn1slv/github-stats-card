"""Tests for color utilities."""

from src.colors import (
    is_valid_hex_color,
    is_valid_gradient,
    parse_color,
    get_card_colors,
)


def test_is_valid_hex_color():
    assert is_valid_hex_color("2f80ed")
    assert is_valid_hex_color("fff")
    assert is_valid_hex_color("ffffff")
    assert is_valid_hex_color("ffffffff")
    assert is_valid_hex_color("FFF")
    assert is_valid_hex_color("2F80ED")

    assert not is_valid_hex_color("gg0000")
    assert not is_valid_hex_color("ff")
    assert not is_valid_hex_color("fffffffff")
    assert not is_valid_hex_color("#fff")


def test_is_valid_gradient():
    assert is_valid_gradient(["90", "ff0000", "00ff00"])
    assert is_valid_gradient(["0", "fff", "000", "f0f"])

    assert not is_valid_gradient(["90", "ff0000"])  # Only 2 elements
    assert not is_valid_gradient(["90", "gg0000", "00ff00"])  # Invalid color


def test_parse_color():
    # Single colors
    assert parse_color("2f80ed", "#000") == "#2f80ed"
    assert parse_color("fff", "#000") == "#fff"

    # Gradients
    result = parse_color("90,ff0000,00ff00", "#000")
    assert isinstance(result, list)
    assert result == ["90", "ff0000", "00ff00"]

    # Fallback
    assert parse_color("invalid", "#000") == "#000"
    assert parse_color(None, "#000") == "#000"
    assert parse_color("", "#000") == "#000"


def test_get_card_colors_default():
    colors = get_card_colors()
    assert colors["titleColor"] == "#2f80ed"
    assert colors["textColor"] == "#434d58"
    assert colors["iconColor"] == "#4c71f2"
    assert colors["bgColor"] == "#fffefe"
    assert colors["borderColor"] == "#e4e2e2"


def test_get_card_colors_theme():
    colors = get_card_colors(theme="dark")
    assert colors["titleColor"] == "#fff"
    assert colors["textColor"] == "#9f9f9f"
    assert colors["bgColor"] == "#151515"


def test_get_card_colors_custom_overrides():
    colors = get_card_colors(
        theme="default",
        title_color="ff0000",
        bg_color="000000",
    )
    assert colors["titleColor"] == "#ff0000"
    assert colors["bgColor"] == "#000000"
    # Other colors should still use theme defaults
    assert colors["textColor"] == "#434d58"


def test_get_card_colors_gradient():
    colors = get_card_colors(bg_color="90,ff0000,00ff00")
    assert isinstance(colors["bgColor"], list)
    assert colors["bgColor"] == ["90", "ff0000", "00ff00"]


def test_get_card_colors_ring_color_default():
    """Test that ringColor is properly formatted with # prefix for default theme."""
    colors = get_card_colors()
    # Should fallback to title_color and have # prefix
    assert colors["ringColor"] == "#2f80ed"
    assert isinstance(colors["ringColor"], str)
    assert colors["ringColor"].startswith("#")


def test_get_card_colors_ring_color_custom():
    """Test that custom ring color is properly formatted."""
    colors = get_card_colors(ring_color="ff0000")
    assert colors["ringColor"] == "#ff0000"
    assert isinstance(colors["ringColor"], str)
    assert colors["ringColor"].startswith("#")

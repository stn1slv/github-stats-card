"""Tests for color parsing and validation."""

from src.rendering.colors import (
    is_valid_hex_color,
    is_valid_gradient,
    parse_color,
    get_card_colors,
)


def test_is_valid_hex_color():
    assert is_valid_hex_color("ffffff") is True
    assert is_valid_hex_color("fff") is True
    assert is_valid_hex_color("ff00ff00") is True
    assert is_valid_hex_color("f0f0") is True
    assert is_valid_hex_color("gggggg") is False
    assert is_valid_hex_color("ff") is False
    assert is_valid_hex_color("fffff") is False


def test_is_valid_gradient():
    assert is_valid_gradient(["90", "ff0000", "00ff00"]) is True
    assert is_valid_gradient(["90", "ff0000"]) is False
    assert is_valid_gradient(["90", "gggggg", "00ff00"]) is False


def test_parse_color():
    # Valid hex
    assert parse_color("2f80ed", "#000") == "#2f80ed"
    # Valid gradient
    assert parse_color("90,ff0000,00ff00", "#000") == ["90", "ff0000", "00ff00"]
    # Invalid
    assert parse_color("invalid", "#000") == "#000"
    # None
    assert parse_color(None, "#000") == "#000"


def test_get_card_colors_default():
    colors = get_card_colors()
    assert colors["titleColor"] == "#2f80ed"
    assert colors["textColor"] == "#434d58"
    assert colors["bgColor"] == "#fffefe"


def test_get_card_colors_theme():
    colors = get_card_colors(theme="radical")
    assert colors["titleColor"] == "#fe428e"
    assert colors["textColor"] == "#a9fef7"
    assert colors["bgColor"] == "#141321"


def test_get_card_colors_custom_overrides():
    colors = get_card_colors(title_color="ff0000", text_color="00ff00")
    assert colors["titleColor"] == "#ff0000"
    assert colors["textColor"] == "#00ff00"
    # Others should be default
    assert colors["bgColor"] == "#fffefe"


def test_get_card_colors_gradient():
    colors = get_card_colors(bg_color="45,ff0000,00ff00")
    assert colors["bgColor"] == ["45", "ff0000", "00ff00"]


def test_get_card_colors_ring_color_default():
    # Should fallback to title color
    colors = get_card_colors(theme="default")
    assert colors["ringColor"] == colors["titleColor"]


def test_get_card_colors_ring_color_custom():
    colors = get_card_colors(ring_color="ff0000")
    assert colors["ringColor"] == "#ff0000"

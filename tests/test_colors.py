"""Tests for color parsing and validation."""

import pytest

from src.rendering.colors import (
    format_gradient,
    get_card_colors,
    is_valid_gradient,
    is_valid_hex_color,
    parse_color,
    resolve_color,
)


@pytest.mark.parametrize(
    ("colors", "expected_attrs"),
    [
        (["0", "ff0000", "00ff00"], {"x1": "0%", "y1": "0%", "x2": "100%", "y2": "0%"}),
        (["90", "ff0000", "00ff00"], {"x1": "0%", "y1": "0%", "x2": "0%", "y2": "100%"}),
        (["180", "ff0000", "00ff00"], {"x1": "100%", "y1": "0%", "x2": "0%", "y2": "0%"}),
        (["270", "ff0000", "00ff00"], {"x1": "0%", "y1": "100%", "x2": "0%", "y2": "0%"}),
        (["not_a_number", "ff0000", "00ff00"], {"x1": "0%", "y1": "0%", "x2": "100%", "y2": "0%"}),
    ],
)
def test_format_gradient(colors: list[str], expected_attrs: dict[str, str]):
    grad_id, grad_svg = format_gradient(colors)
    assert grad_id == "gradient"
    for attr, val in expected_attrs.items():
        assert f'{attr}="{val}"' in grad_svg
    assert 'stop-color="#ff0000"' in grad_svg
    assert 'stop-color="#00ff00"' in grad_svg


@pytest.mark.parametrize(
    ("color", "expected"),
    [
        ("ffffff", True),
        ("fff", True),
        ("ff00ff00", True),
        ("f0f0", True),
        ("gggggg", False),
        ("ff", False),
        ("fffff", False),
    ],
)
def test_is_valid_hex_color(color: str, expected: bool):
    assert is_valid_hex_color(color) is expected


@pytest.mark.parametrize(
    ("parts", "expected"),
    [
        (["90", "ff0000", "00ff00"], True),
        (["90", "ff0000"], False),
        (["90", "gggggg", "00ff00"], False),
    ],
)
def test_is_valid_gradient(parts: list[str], expected: bool):
    assert is_valid_gradient(parts) is expected


@pytest.mark.parametrize(
    ("color", "fallback", "expected"),
    [
        ("2f80ed", "#000", "#2f80ed"),
        ("90,ff0000,00ff00", "#000", ["90", "ff0000", "00ff00"]),
        ("invalid", "#000", "#000"),
        (None, "#000", "#000"),
    ],
)
def test_parse_color(color, fallback, expected):
    assert parse_color(color, fallback) == expected


def test_get_card_colors_default():
    colors = get_card_colors()
    assert colors["title_color"] == "#2f80ed"
    assert colors["text_color"] == "#434d58"
    assert colors["bg_color"] == "#fffefe"


def test_get_card_colors_theme():
    colors = get_card_colors(theme="radical")
    assert colors["title_color"] == "#fe428e"
    assert colors["text_color"] == "#a9fef7"
    assert colors["bg_color"] == "#141321"


def test_get_card_colors_vue_github_dark_theme():
    colors = get_card_colors(theme="vue-github-dark")
    assert colors["title_color"] == "#41b883"
    assert colors["text_color"] == "#fffefe"
    assert colors["bg_color"] == "#0d1117"
    # The border must not fall back to the default light grey, or the card is
    # outlined against the GitHub dark canvas it is meant to blend into.
    assert colors["border_color"] == "#0d1117"


def test_get_card_colors_custom_overrides():
    colors = get_card_colors(title_color="ff0000", text_color="00ff00")
    assert colors["title_color"] == "#ff0000"
    assert colors["text_color"] == "#00ff00"
    # Others should be default
    assert colors["bg_color"] == "#fffefe"


def test_get_card_colors_gradient():
    colors = get_card_colors(bg_color="45,ff0000,00ff00")
    assert colors["bg_color"] == ["45", "ff0000", "00ff00"]


def test_get_card_colors_ring_color_default():
    # Should fallback to title color
    colors = get_card_colors(theme="default")
    assert colors["ring_color"] == colors["title_color"]


def test_get_card_colors_ring_color_custom():
    colors = get_card_colors(ring_color="ff0000")
    assert colors["ring_color"] == "#ff0000"


# ---------------------------------------------------------------------------
# resolve_color
# ---------------------------------------------------------------------------
def test_resolve_color_passes_a_solid_color_through():
    assert resolve_color("#2f80ed") == "#2f80ed"


def test_resolve_color_collapses_a_gradient_to_its_first_stop():
    # parse_color keeps the angle at index 0; the first real color is index 1.
    assert resolve_color(["90", "ff0000", "00ff00"]) == "#ff0000"


def test_resolve_color_falls_back_when_a_gradient_has_no_stop():
    assert resolve_color(["90"], "#000000") == "#000000"

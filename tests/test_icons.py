"""Tests for SVG icon definitions."""

import pytest

from src.rendering.icons import ICONS, get_icon_svg


@pytest.mark.parametrize("name", sorted(ICONS))
def test_get_icon_svg_returns_a_well_formed_icon(name: str):
    svg = get_icon_svg(name)

    assert svg.count("<svg") == 1
    assert svg.count("</svg>") == 1
    assert 'viewBox="0 0 16 16"' in svg
    assert 'class="icon"' in svg
    assert ICONS[name] in svg


def test_get_icon_svg_unknown_name_renders_nothing():
    """An unknown icon must not emit an empty <svg> that occupies layout space."""
    assert get_icon_svg("not-a-real-icon") == ""


def test_every_stat_icon_referenced_by_the_card_exists():
    """A missing icon fails silently as blank space, so the wiring is asserted here."""
    from src.core.i18n import TRANSLATIONS
    from src.rendering.user_stats import _get_stat_definitions

    stats = dict.fromkeys(
        [
            "totalStars",
            "totalCommits",
            "totalPRs",
            "mergedPRs",
            "totalIssues",
            "contributedTo",
            "totalRepos",
            "totalReviews",
            "discussionsStarted",
            "discussionsAnswered",
        ],
        1,
    )
    definitions = _get_stat_definitions(stats, next(iter(TRANSLATIONS)))

    for key, definition in definitions.items():
        assert definition["icon"] in ICONS, f"stat '{key}' references a missing icon"

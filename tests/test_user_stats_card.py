"""Tests for user stats card rendering."""

import re

import pytest

from src.core.config import UserStatsCardConfig
from src.core.constants import (
    CARD_PADDING,
    FONT_SIZE_STAT,
    RANK_CIRCLE_RIM_LEFT_INSET,
    STAT_LABEL_X_WITH_ICON,
    STAT_VALUE_X_POSITION,
)
from src.core.utils import measure_text
from src.github.fetcher import UserStats
from src.rendering.user_stats import render_user_stats_card


@pytest.fixture
def sample_stats() -> UserStats:
    return {
        "name": "The Octocat",
        "login": "octocat",
        "totalCommits": 100,
        "totalPRs": 50,
        "mergedPRs": 40,
        "totalIssues": 25,
        "totalStars": 200,
        "totalRepos": 60,
        "contributedTo": 10,
        "followers": 50,
        "totalReviews": 5,
        "discussionsStarted": 2,
        "discussionsAnswered": 1,
    }


def test_render_user_stats_card_basic(sample_stats):
    config = UserStatsCardConfig()
    svg = render_user_stats_card(sample_stats, config)
    # The title is HTML encoded in the SVG
    assert "The Octocat&#39;s GitHub Stats" in svg
    assert "Total Stars Earned" in svg
    assert "Total Commits" in svg
    # Default stats
    assert "200" in svg
    assert "100" in svg


def test_render_user_stats_card_hide_stats(sample_stats):
    config = UserStatsCardConfig(hide=["stars", "commits"])
    svg = render_user_stats_card(sample_stats, config)
    assert "Total Stars Earned" not in svg
    assert "Total Commits" not in svg
    assert "Total PRs" in svg


def test_render_user_stats_card_show_additional(sample_stats):
    config = UserStatsCardConfig(show=["reviews", "discussions_started"])
    svg = render_user_stats_card(sample_stats, config)
    assert "Total Reviews" in svg
    assert "Discussions Started" in svg


def test_render_user_stats_card_custom_theme(sample_stats):
    config = UserStatsCardConfig(theme="radical")
    svg = render_user_stats_card(sample_stats, config)
    assert "#fe428e" in svg  # title_color from radical theme


def test_render_user_stats_card_hide_rank(sample_stats):
    config = UserStatsCardConfig(hide_rank=True)
    svg = render_user_stats_card(sample_stats, config)
    assert 'data-testid="rank-circle"' not in svg


def test_render_user_stats_card_custom_title(sample_stats):
    config = UserStatsCardConfig(custom_title="My Progress")
    svg = render_user_stats_card(sample_stats, config)
    assert "My Progress" in svg


def test_render_user_stats_card_repos_stat(sample_stats):
    config = UserStatsCardConfig(show=["repos"])
    svg = render_user_stats_card(sample_stats, config)
    assert "Total Repositories" in svg
    assert "60" in svg


def test_render_user_stats_card_contribs_label(sample_stats):
    config = UserStatsCardConfig()
    svg = render_user_stats_card(sample_stats, config)
    assert "Contributed To" in svg
    assert "Total Repositories" not in svg


def test_render_user_stats_card_gradient_title_color_is_a_usable_hex(sample_stats):
    """A gradient in a non-background slot must collapse, not leak a Python list repr."""
    config = UserStatsCardConfig(title_color="90,ff0000,00ff00")
    svg = render_user_stats_card(sample_stats, config)

    assert "['90'" not in svg
    assert "fill: #ff0000;" in svg


def _layout(svg: str) -> dict:
    """Pull the geometry that decides whether the card overlaps itself."""
    width = int(re.search(r'<svg width="(\d+)"', svg).group(1))
    values = re.findall(rf'x="{STAT_VALUE_X_POSITION}" y="12.5">([^<]+)<', svg)
    widest = max((measure_text(v, FONT_SIZE_STAT) for v in values), default=0.0)
    rank = re.search(r'rank-circle"\s*\n?\s*transform="translate\(([\d.]+),', svg)
    return {
        "width": width,
        "value_end": CARD_PADDING + STAT_VALUE_X_POSITION + widest,
        # Rim starts 53px before the transform origin (cx=-10, r=40, stroke 6)
        "rim_left": float(rank.group(1)) - RANK_CIRCLE_RIM_LEFT_INSET if rank else None,
        "values": values,
    }


@pytest.mark.parametrize(
    ("kwargs", "stat_override"),
    [
        ({"card_width": 300}, None),
        ({"card_width": 100}, None),
        # The case a fixed 420px floor did not cover: a long-format value is far
        # wider than a short-format one and used to run underneath the ring.
        ({"card_width": 300, "number_format": "long"}, 12345678),
        ({"number_format": "long"}, 12345678),
        ({}, None),
    ],
)
def test_render_user_stats_card_values_never_reach_the_rank_circle(sample_stats, kwargs, stat_override):
    """The width clamp must keep the stat values clear of the ring, not merely on the canvas."""
    if stat_override is not None:
        sample_stats["totalStars"] = stat_override

    layout = _layout(render_user_stats_card(sample_stats, UserStatsCardConfig(**kwargs)))

    assert layout["rim_left"] is not None
    assert layout["value_end"] <= layout["rim_left"], (
        f"widest value ends at {layout['value_end']} but the rim starts at {layout['rim_left']}"
    )
    # And the ring itself stays on the canvas
    assert layout["rim_left"] > 0
    assert layout["rim_left"] + 2 * RANK_CIRCLE_RIM_LEFT_INSET < layout["width"]


@pytest.mark.parametrize("number_format", ["short", "long"])
def test_render_user_stats_card_hide_rank_still_fits_the_widest_value(sample_stats, number_format):
    """Without the rank circle the floor is lower, but the value must still clear the border."""
    sample_stats["totalStars"] = 12345678

    layout = _layout(
        render_user_stats_card(
            sample_stats, UserStatsCardConfig(card_width=100, hide_rank=True, number_format=number_format)
        )
    )

    assert layout["rim_left"] is None
    assert layout["value_end"] + CARD_PADDING <= layout["width"]


def test_render_user_stats_card_width_floor_tracks_the_value_width(sample_stats):
    """A wider value must produce a wider floor, or the floor is not derived at all."""
    sample_stats["totalStars"] = 12345678

    narrow = _layout(render_user_stats_card(sample_stats, UserStatsCardConfig(card_width=1, number_format="short")))
    wide = _layout(render_user_stats_card(sample_stats, UserStatsCardConfig(card_width=1, number_format="long")))

    assert wide["width"] > narrow["width"]


def test_render_user_stats_card_default_rank_position_is_unchanged(sample_stats):
    """The clamp must not shift the default card, which stays 467px wide."""
    svg = render_user_stats_card(sample_stats, UserStatsCardConfig())

    assert '<svg width="467"' in svg
    assert "translate(390.5, 47.5)" in svg


def test_render_user_stats_card_rank_icon_percentile(sample_stats):
    """--rank-icon percentile must show the percentile, not the letter grade."""
    svg = render_user_stats_card(sample_stats, UserStatsCardConfig(rank_icon="percentile"))

    assert 'data-testid="percentile-rank-icon"' in svg
    assert 'data-testid="level-rank-icon"' not in svg
    assert re.search(r'data-testid="percentile-rank-icon">\d+\.\d%<', svg)


def test_render_user_stats_card_rank_icon_github(sample_stats):
    """--rank-icon github adds the logo mark above the grade."""
    svg = render_user_stats_card(sample_stats, UserStatsCardConfig(rank_icon="github"))

    assert 'data-testid="level-rank-icon"' in svg
    assert svg.count('data-testid="icon"') == 1


def test_render_user_stats_card_rank_icon_default_is_the_letter_grade(sample_stats):
    svg = render_user_stats_card(sample_stats, UserStatsCardConfig(rank_icon="default"))

    assert 'data-testid="level-rank-icon"' in svg
    assert 'data-testid="percentile-rank-icon"' not in svg


def test_render_user_stats_card_number_format_long(sample_stats):
    """--number-format long writes the full number instead of the k-suffixed short form."""
    sample_stats["totalStars"] = 12345

    short = render_user_stats_card(sample_stats, UserStatsCardConfig(number_format="short"))
    long_form = render_user_stats_card(sample_stats, UserStatsCardConfig(number_format="long"))

    assert ">12.3k<" in short
    assert ">12,345<" in long_form
    assert "12.3k" not in long_form


def test_render_user_stats_card_gradient_background_emits_a_gradient_def(sample_stats):
    """A gradient background is the one slot that renders as a real linearGradient."""
    svg = render_user_stats_card(sample_stats, UserStatsCardConfig(bg_color="90,ff0000,00ff00"))

    assert "<linearGradient" in svg
    assert 'stop-color="#ff0000"' in svg
    assert 'fill="url(#gradient)"' in svg


def test_render_user_stats_card_show_icons(sample_stats):
    """--show-icons adds one icon per stat row and shifts the labels right."""
    svg = render_user_stats_card(sample_stats, UserStatsCardConfig(show_icons=True))

    assert svg.count('data-testid="icon"') == 5
    assert f'x="{STAT_LABEL_X_WITH_ICON}"' in svg

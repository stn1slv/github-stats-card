"""Tests for user stats card rendering."""

import re

import pytest

from src.core.config import UserStatsCardConfig
from src.core.constants import STAT_LABEL_X_WITH_ICON, STAT_VALUE_X_POSITION
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


def test_render_user_stats_card_keeps_the_rank_circle_inside_a_narrow_card(sample_stats):
    """--card-width must move the rank circle, not leave it at a fixed x off the canvas.

    Asserting the concrete pair rather than `rank_x < width`: the latter is
    tautological, since rank_x is derived from the same width it is compared to.
    """
    svg = render_user_stats_card(sample_stats, UserStatsCardConfig(card_width=300))

    # 300 is below the floor needed by the value column plus the circle, so the
    # width clamps to 420 and the circle lands at 420 - 76.5.
    assert '<svg width="420"' in svg
    assert "translate(343.5, 47.5)" in svg
    # Circle spans [rank_x - 50, rank_x + 30]; both edges must be on the canvas
    assert 343.5 - 50 > 0
    assert 343.5 + 30 < 420


def test_render_user_stats_card_hide_rank_still_fits_a_long_value(sample_stats):
    """Without the rank circle the floor is lower, but the value column must still fit."""
    sample_stats["totalStars"] = 12345678
    svg = render_user_stats_card(
        sample_stats, UserStatsCardConfig(card_width=100, hide_rank=True, number_format="long")
    )

    width = int(re.search(r'<svg width="(\d+)"', svg).group(1))
    assert width == 340
    # Value is left-anchored at 25 + 219.01; "12,345,678" runs about 84px
    assert width > 25 + STAT_VALUE_X_POSITION + 84


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

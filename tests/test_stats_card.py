"""Tests for stats card rendering."""

import pytest

from src.rendering.stats import render_stats_card
from src.github.fetcher import UserStats
from src.core.config import StatsCardConfig


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
        "contributedTo": 10,
        "followers": 50,
        "totalReviews": 5,
        "discussionsStarted": 2,
        "discussionsAnswered": 1,
    }


def test_render_stats_card_basic(sample_stats):
    config = StatsCardConfig()
    svg = render_stats_card(sample_stats, config)
    # The title is HTML encoded in the SVG
    assert "The Octocat&#39;s GitHub Stats" in svg
    assert "Total Stars Earned" in svg
    assert "Total Commits" in svg
    # Default stats
    assert "200" in svg
    assert "100" in svg


def test_render_stats_card_hide_stats(sample_stats):
    config = StatsCardConfig(hide=["stars", "commits"])
    svg = render_stats_card(sample_stats, config)
    assert "Total Stars Earned" not in svg
    assert "Total Commits" not in svg
    assert "Total PRs" in svg


def test_render_stats_card_show_additional(sample_stats):
    config = StatsCardConfig(show=["reviews", "discussions_started"])
    svg = render_stats_card(sample_stats, config)
    assert "Total Reviews" in svg
    assert "Discussions Started" in svg


def test_render_stats_card_custom_theme(sample_stats):
    config = StatsCardConfig(theme="radical")
    svg = render_stats_card(sample_stats, config)
    assert "#fe428e" in svg  # titleColor from radical theme


def test_render_stats_card_hide_rank(sample_stats):
    config = StatsCardConfig(hide_rank=True)
    svg = render_stats_card(sample_stats, config)
    assert 'data-testid="rank-circle"' not in svg


def test_render_stats_card_custom_title(sample_stats):
    config = StatsCardConfig(custom_title="My Progress")
    svg = render_stats_card(sample_stats, config)
    assert "My Progress" in svg

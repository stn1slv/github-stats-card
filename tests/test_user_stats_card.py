"""Tests for user stats card rendering."""

import pytest

from src.core.config import UserStatsCardConfig
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

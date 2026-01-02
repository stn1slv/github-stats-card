"""Tests for stats card renderer."""

from src.stats_card import render_stats_card
from src.fetcher import UserStats


def test_render_stats_card_basic():
    """Test basic stats card rendering."""
    stats: UserStats = {
        "name": "Test User",
        "login": "testuser",
        "totalCommits": 1000,
        "totalPRs": 100,
        "mergedPRs": 90,
        "totalIssues": 50,
        "totalStars": 200,
        "contributedTo": 25,
        "followers": 50,
        "totalReviews": 10,
        "discussionsStarted": 5,
        "discussionsAnswered": 8,
    }

    svg = render_stats_card(stats)

    # Check that SVG contains expected elements
    assert "<svg" in svg
    assert "</svg>" in svg
    assert "Test User" in svg or "testuser" in svg
    assert "Total Stars" in svg
    assert "Total Commits" in svg


def test_render_stats_card_hide_stats():
    """Test hiding specific stats."""
    stats: UserStats = {
        "name": "Test User",
        "login": "testuser",
        "totalCommits": 1000,
        "totalPRs": 100,
        "mergedPRs": 90,
        "totalIssues": 50,
        "totalStars": 200,
        "contributedTo": 25,
        "followers": 50,
        "totalReviews": 10,
        "discussionsStarted": 5,
        "discussionsAnswered": 8,
    }

    svg = render_stats_card(stats, hide=["stars", "prs"])

    assert "Total Stars" not in svg
    assert "Total PRs" not in svg
    assert "Total Commits" in svg


def test_render_stats_card_show_additional():
    """Test showing additional stats."""
    stats: UserStats = {
        "name": "Test User",
        "login": "testuser",
        "totalCommits": 1000,
        "totalPRs": 100,
        "mergedPRs": 90,
        "totalIssues": 50,
        "totalStars": 200,
        "contributedTo": 25,
        "followers": 50,
        "totalReviews": 10,
        "discussionsStarted": 5,
        "discussionsAnswered": 8,
    }

    svg = render_stats_card(stats, show=["reviews", "discussions_started"])

    assert "Total Reviews" in svg
    assert "Discussions Started" in svg


def test_render_stats_card_custom_theme():
    """Test custom theme."""
    stats: UserStats = {
        "name": "Test User",
        "login": "testuser",
        "totalCommits": 1000,
        "totalPRs": 100,
        "mergedPRs": 90,
        "totalIssues": 50,
        "totalStars": 200,
        "contributedTo": 25,
        "followers": 50,
        "totalReviews": 10,
        "discussionsStarted": 5,
        "discussionsAnswered": 8,
    }

    svg = render_stats_card(stats, theme="dark")

    assert "<svg" in svg
    # Dark theme colors should be applied
    assert "#fff" in svg or "#9f9f9f" in svg


def test_render_stats_card_hide_rank():
    """Test hiding rank circle."""
    stats: UserStats = {
        "name": "Test User",
        "login": "testuser",
        "totalCommits": 1000,
        "totalPRs": 100,
        "mergedPRs": 90,
        "totalIssues": 50,
        "totalStars": 200,
        "contributedTo": 25,
        "followers": 50,
        "totalReviews": 10,
        "discussionsStarted": 5,
        "discussionsAnswered": 8,
    }

    svg_with_rank = render_stats_card(stats, hide_rank=False)
    svg_without_rank = render_stats_card(stats, hide_rank=True)

    # Check for actual rank circle element, not just CSS classes
    assert 'data-testid="rank-circle"' in svg_with_rank
    assert 'data-testid="rank-circle"' not in svg_without_rank


def test_render_stats_card_custom_title():
    """Test custom title."""
    stats: UserStats = {
        "name": "Test User",
        "login": "testuser",
        "totalCommits": 1000,
        "totalPRs": 100,
        "mergedPRs": 90,
        "totalIssues": 50,
        "totalStars": 200,
        "contributedTo": 25,
        "followers": 50,
        "totalReviews": 10,
        "discussionsStarted": 5,
        "discussionsAnswered": 8,
    }

    svg = render_stats_card(stats, custom_title="My Custom Stats")

    assert "My Custom Stats" in svg

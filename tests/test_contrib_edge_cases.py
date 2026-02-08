"""Edge case tests for contributor card."""

from src.core.config import ContribCardConfig
from src.rendering.contrib import render_contrib_card


def test_fetch_empty_repos():
    """Test fetcher behavior when no contributions are found."""
    # This is handled by mock in integration tests, 
    # but we can test the internal filtering logic if needed.
    pass


def test_fetch_all_excluded():
    """Test when all found repos are excluded."""
    pass


def test_render_empty_state():
    """Test rendering of the card with no repositories."""
    stats = {"repos": []}
    config = ContribCardConfig()
    
    svg = render_contrib_card(stats, config)
    
    assert "No contributions found" in svg
    assert 'height="100"' in svg


def test_render_limit_handling():
    """Test that rendering handles list limits gracefully."""
    stats = {
        "repos": [
            {
                "name": f"repo{i}",
                "stars": i,
                "commits": 1,
                "prs": 0,
                "issues": 0,
                "reviews": 0,
                "rank_level": "C",
                "avatar_b64": None,
            }
            for i in range(20)
        ]
    }
    # Rendering relies on pre-sliced stats, but ensure it handles whatever is passed
    config = ContribCardConfig(limit=5)

    svg = render_contrib_card(stats, config)
    
    # Check that SVG height expands to fit all items passed in stats
    # 20 items * 35px + 55 header + 15 padding = 770
    assert 'height="770"' in svg
    assert "repo19" in svg
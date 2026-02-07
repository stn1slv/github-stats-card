"""Tests for contributor card edge cases."""

import pytest
from unittest.mock import patch
from src.core.config import ContribCardConfig, ContribFetchConfig
from src.github.fetcher import fetch_contributor_stats
from src.rendering.contrib import render_contrib_card


@pytest.fixture
def mock_client():
    with patch("src.github.fetcher.GitHubClient") as MockClient:
        client_instance = MockClient.return_value
        yield client_instance


def test_fetch_empty_repos(mock_client):
    """Test fetching when user has no contributions."""
    mock_client.graphql_query.return_value = {
        "data": {
            "user": {
                "repositoriesContributedTo": {
                    "nodes": []
                }
            }
        }
    }

    config = ContribFetchConfig(username="user", token="token")
    stats = fetch_contributor_stats(config)

    assert len(stats["repos"]) == 0


def test_fetch_all_excluded(mock_client):
    """Test when all repositories are excluded."""
    mock_client.graphql_query.return_value = {
        "data": {
            "user": {
                "repositoriesContributedTo": {
                    "nodes": [
                        {
                            "nameWithOwner": "owner/repo1",
                            "isPrivate": False,
                            "stargazers": {"totalCount": 10},
                            "owner": {"avatarUrl": "url", "login": "owner"}
                        }
                    ]
                }
            }
        }
    }

    config = ContribFetchConfig(
        username="user", 
        token="token", 
        exclude_repos=["owner/repo1"]
    )
    stats = fetch_contributor_stats(config)

    assert len(stats["repos"]) == 0


def test_render_empty_state():
    """Test rendering the empty state message."""
    stats = {"repos": []}
    config = ContribCardConfig()
    
    svg = render_contrib_card(stats, config)
    
    assert "No contributions found" in svg
    assert 'height="100"' in svg  # Should have minimal height


def test_render_limit_handling():
    """Test that rendering handles list limits gracefully."""
    stats = {
        "repos": [
            {"name": f"repo{i}", "stars": i, "avatar_b64": None}
            for i in range(20)
        ]
    }
    # Rendering relies on pre-sliced stats, but ensure it handles whatever is passed
    config = ContribCardConfig(limit=5) 
    
    svg = render_contrib_card(stats, config)
    
    # Check that SVG height expands to fit all items passed in stats
    # 20 items * 30px + 55 header + 15 padding = 670
    assert 'height="670"' in svg
    assert "repo19" in svg
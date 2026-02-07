"""Tests for contributor card edge cases."""

import pytest
from unittest.mock import patch
from src.core.config import ContribCardConfig, ContribFetchConfig
from src.github.fetcher import fetch_contributor_stats
from src.rendering.contrib import render_contrib_card


@pytest.fixture
def mock_client():
    with patch("src.github.fetcher.GitHubClient") as MockClient, \
         patch("src.github.fetcher.fetch_stats") as mock_fetch_stats:
        
        client_instance = MockClient.return_value
        client_instance.fetch_image.return_value = b"fake_image_data"
        
        mock_fetch_stats.return_value = {
            "totalCommits": 1000,
            "totalPRs": 100,
            "totalIssues": 50,
            "totalReviews": 20,
            "followers": 10
        }
        
        yield client_instance


def setup_mock_response(mock_client, repos_data):
    """Helper to set up the two-step GraphQL query mock."""
    years_response = {
        "data": {
            "user": {
                "contributionsCollection": {
                    "contributionYears": [2024]
                }
            }
        }
    }

    commit_contribs = []
    for repo in repos_data:
        commit_contribs.append({
            "repository": {
                "nameWithOwner": repo["nameWithOwner"],
                "isPrivate": repo["isPrivate"],
                "stargazers": repo["stargazers"],
                "owner": repo["owner"]
            },
            "contributions": {"totalCount": repo.get("commits", 1)}
        })

    contribs_response = {
        "data": {
            "user": {
                "contributionsCollection": {
                    "commitContributionsByRepository": commit_contribs,
                    "pullRequestContributionsByRepository": [],
                    "issueContributionsByRepository": [],
                    "pullRequestReviewContributionsByRepository": []
                }
            }
        }
    }

    mock_client.graphql_query.side_effect = [years_response, contribs_response]


def test_fetch_empty_repos(mock_client):
    """Test fetching when user has no contributions."""
    setup_mock_response(mock_client, [])

    config = ContribFetchConfig(username="user", token="token")
    stats = fetch_contributor_stats(config)

    assert len(stats["repos"]) == 0


def test_fetch_all_excluded(mock_client):
    """Test when all repositories are excluded."""
    repos = [
        {
            "nameWithOwner": "owner/repo1",
            "isPrivate": False,
            "stargazers": {"totalCount": 10},
            "owner": {"avatarUrl": "url", "login": "owner"}
        }
    ]
    setup_mock_response(mock_client, repos)

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
            {
                "name": f"repo{i}", 
                "stars": i, 
                "commits": 1, "prs": 0, "issues": 0, "reviews": 0,
                "rank_level": "C",
                "avatar_b64": None
            }
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

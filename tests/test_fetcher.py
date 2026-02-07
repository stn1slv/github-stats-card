"""Tests for contributor stats fetcher."""

import pytest
from unittest.mock import patch
from src.core.config import ContribFetchConfig
from src.github.fetcher import fetch_contributor_stats
from src.core.exceptions import FetchError


@pytest.fixture
def mock_client():
    with patch("src.github.fetcher.GitHubClient") as MockClient:
        client_instance = MockClient.return_value
        client_instance.fetch_image.return_value = b"fake_image_data"
        yield client_instance


def test_fetch_contributor_stats_success(mock_client):
    """Test successful fetching of contributor stats."""
    mock_client.graphql_query.return_value = {
        "data": {
            "user": {
                "repositoriesContributedTo": {
                    "nodes": [
                        {
                            "nameWithOwner": "owner/repo1",
                            "isPrivate": False,
                            "stargazers": {"totalCount": 100},
                            "owner": {"avatarUrl": "http://avatar1", "login": "owner"}
                        },
                        {
                            "nameWithOwner": "owner/repo2",
                            "isPrivate": False,
                            "stargazers": {"totalCount": 50},
                            "owner": {"avatarUrl": "http://avatar2", "login": "owner"}
                        }
                    ]
                }
            }
        }
    }

    config = ContribFetchConfig(username="user", token="token", limit=5)
    stats = fetch_contributor_stats(config)

    assert len(stats["repos"]) == 2
    assert stats["repos"][0]["name"] == "owner/repo1"
    assert stats["repos"][0]["stars"] == 100
    assert stats["repos"][1]["name"] == "owner/repo2"
    assert stats["repos"][1]["stars"] == 50


def test_fetch_contributor_stats_sorting(mock_client):
    """Test that repos are sorted by stars."""
    mock_client.graphql_query.return_value = {
        "data": {
            "user": {
                "repositoriesContributedTo": {
                    "nodes": [
                        {
                            "nameWithOwner": "owner/small",
                            "isPrivate": False,
                            "stargazers": {"totalCount": 10},
                            "owner": {"avatarUrl": "http://avatar", "login": "owner"}
                        },
                        {
                            "nameWithOwner": "owner/big",
                            "isPrivate": False,
                            "stargazers": {"totalCount": 500},
                            "owner": {"avatarUrl": "http://avatar", "login": "owner"}
                        }
                    ]
                }
            }
        }
    }

    config = ContribFetchConfig(username="user", token="token", limit=5)
    stats = fetch_contributor_stats(config)

    assert stats["repos"][0]["name"] == "owner/big"
    assert stats["repos"][1]["name"] == "owner/small"


def test_fetch_contributor_stats_limit(mock_client):
    """Test that results are limited."""
    nodes = []
    for i in range(10):
        nodes.append({
            "nameWithOwner": f"owner/repo{i}",
            "isPrivate": False,
            "stargazers": {"totalCount": 100 - i},
            "owner": {"avatarUrl": "http://avatar", "login": "owner"}
        })

    mock_client.graphql_query.return_value = {
        "data": {
            "user": {
                "repositoriesContributedTo": {
                    "nodes": nodes
                }
            }
        }
    }

    config = ContribFetchConfig(username="user", token="token", limit=3)
    stats = fetch_contributor_stats(config)

    assert len(stats["repos"]) == 3
    assert stats["repos"][0]["name"] == "owner/repo0"


def test_fetch_contributor_stats_exclude(mock_client):
    """Test excluded repositories are filtered out."""
    mock_client.graphql_query.return_value = {
        "data": {
            "user": {
                "repositoriesContributedTo": {
                    "nodes": [
                        {
                            "nameWithOwner": "owner/keep",
                            "isPrivate": False,
                            "stargazers": {"totalCount": 100},
                            "owner": {"avatarUrl": "http://avatar", "login": "owner"}
                        },
                        {
                            "nameWithOwner": "owner/skip",
                            "isPrivate": False,
                            "stargazers": {"totalCount": 100},
                            "owner": {"avatarUrl": "http://avatar", "login": "owner"}
                        }
                    ]
                }
            }
        }
    }

    config = ContribFetchConfig(
        username="user", 
        token="token", 
        limit=5, 
        exclude_repos=["owner/skip"]
    )
    stats = fetch_contributor_stats(config)

    assert len(stats["repos"]) == 1
    assert stats["repos"][0]["name"] == "owner/keep"


def test_fetch_error(mock_client):
    """Test error handling."""
    mock_client.graphql_query.return_value = {"errors": [{"message": "Bad query"}]}
    
    config = ContribFetchConfig(username="user", token="token")
    with pytest.raises(FetchError, match="GraphQL error"):
        fetch_contributor_stats(config)

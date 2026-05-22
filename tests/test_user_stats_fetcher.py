"""Tests for user stats fetcher."""

from unittest.mock import patch

import pytest

from src.core.config import UserStatsFetchConfig
from src.core.exceptions import FetchError
from src.github.fetcher import fetch_user_stats


@pytest.fixture
def mock_client():
    with patch("src.github.fetcher.GitHubClient") as MockClient:
        client_instance = MockClient.return_value
        client_instance.__enter__.return_value = client_instance
        client_instance.__exit__.return_value = False
        yield client_instance


def test_fetch_user_stats_success(mock_client):
    """Test successful fetching of user stats."""
    mock_response = {
        "data": {
            "user": {
                "name": "Test User",
                "login": "testuser",
                "contributionsCollection": {
                    "totalCommitContributions": 100,
                    "totalPullRequestReviewContributions": 50,
                },
                "repositoriesContributedTo": {"totalCount": 10},
                "pullRequests": {"totalCount": 20},
                "mergedPullRequests": {"totalCount": 15},
                "openIssues": {"totalCount": 5},
                "closedIssues": {"totalCount": 5},
                "followers": {"totalCount": 100},
                "repositories": {
                    "totalCount": 60,
                    "nodes": [
                        {"stargazers": {"totalCount": 10}},
                        {"stargazers": {"totalCount": 20}},
                    ],
                    "pageInfo": {"hasNextPage": False, "endCursor": None},
                },
            }
        }
    }
    mock_client.graphql_query.return_value = mock_response
    mock_client.rest_get.side_effect = [
        {"total_count": 100},  # Commits search
        {"total_count": 10},  # Issues search
    ]

    config = UserStatsFetchConfig(username="testuser", token="fake-token", include_all_commits=True)
    stats = fetch_user_stats(config)

    assert stats["name"] == "Test User"
    assert stats["totalStars"] == 30
    assert stats["totalCommits"] == 100
    assert stats["totalIssues"] == 10
    assert stats["totalRepos"] == 60


def test_fetch_user_stats_graphql_error(mock_client):
    """Test handling of GraphQL errors."""
    mock_client.graphql_query.return_value = {"errors": [{"message": "Some error"}]}

    config = UserStatsFetchConfig(username="testuser", token="fake-token")
    with pytest.raises(FetchError, match="GraphQL error: Some error"):
        fetch_user_stats(config)


def test_fetch_user_stats_not_found(mock_client):
    """Test handling of user not found."""
    mock_client.graphql_query.return_value = {"data": {"user": None}}

    config = UserStatsFetchConfig(username="nonexistent", token="fake-token")
    with pytest.raises(FetchError, match="User 'nonexistent' not found"):
        fetch_user_stats(config)


def test_fetch_user_stats_pagination(mock_client):
    """Test repository pagination."""
    # Page 1
    resp1 = {
        "data": {
            "user": {
                "name": "User",
                "login": "user",
                "contributionsCollection": {"totalCommitContributions": 0, "totalPullRequestReviewContributions": 0},
                "repositoriesContributedTo": {"totalCount": 0},
                "pullRequests": {"totalCount": 0},
                "mergedPullRequests": {"totalCount": 0},
                "openIssues": {"totalCount": 0},
                "closedIssues": {"totalCount": 0},
                "followers": {"totalCount": 0},
                "repositories": {
                    "totalCount": 5,
                    "nodes": [{"stargazers": {"totalCount": 10}}],
                    "pageInfo": {"hasNextPage": True, "endCursor": "cursor1"},
                },
            }
        }
    }
    # Page 2
    resp2 = {
        "data": {
            "user": {
                "repositories": {
                    "nodes": [{"stargazers": {"totalCount": 5}}],
                    "pageInfo": {"hasNextPage": False, "endCursor": None},
                }
            }
        }
    }
    mock_client.graphql_query.side_effect = [resp1, resp2]
    mock_client.rest_get.return_value = {"total_count": 0}

    config = UserStatsFetchConfig(username="user", token="fake-token")
    stats = fetch_user_stats(config)

    assert stats["totalStars"] == 15
    assert mock_client.graphql_query.call_count == 2


def test_fetch_user_stats_with_discussions(mock_client):
    """Test fetching discussions statistics."""
    mock_response = {
        "data": {
            "user": {
                "name": "User",
                "login": "user",
                "contributionsCollection": {"totalCommitContributions": 0, "totalPullRequestReviewContributions": 0},
                "repositoriesContributedTo": {"totalCount": 0},
                "pullRequests": {"totalCount": 0},
                "mergedPullRequests": {"totalCount": 0},
                "openIssues": {"totalCount": 0},
                "closedIssues": {"totalCount": 0},
                "followers": {"totalCount": 0},
                "repositories": {
                    "totalCount": 0,
                    "nodes": [],
                    "pageInfo": {"hasNextPage": False, "endCursor": None},
                },
            }
        }
    }
    disc_response = {
        "data": {
            "user": {
                "repositoryDiscussions": {"totalCount": 5},
                "repositoryDiscussionComments": {"totalCount": 3},
            }
        }
    }
    mock_client.graphql_query.side_effect = [mock_response, disc_response]
    mock_client.rest_get.return_value = {"total_count": 0}

    config = UserStatsFetchConfig(
        username="user", token="fake-token", show=["discussions_started", "discussions_answered"]
    )
    stats = fetch_user_stats(config)

    assert stats["discussionsStarted"] == 5
    assert stats["discussionsAnswered"] == 3

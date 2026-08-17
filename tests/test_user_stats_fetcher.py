"""Tests for user stats fetcher."""

import logging
from unittest.mock import patch

import pytest

from src.core.config import UserStatsFetchConfig
from src.core.exceptions import APIError, FetchError
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


def test_fetch_user_stats_user_not_found_is_not_double_wrapped(mock_client):
    """FetchError subclasses APIError, so it must not be caught and re-wrapped by its own handler."""
    mock_client.graphql_query.return_value = {"data": {"user": None}}

    config = UserStatsFetchConfig(username="ghost", token="fake-token")
    with pytest.raises(FetchError) as excinfo:
        fetch_user_stats(config)

    assert str(excinfo.value) == "User 'ghost' not found"


def test_fetch_user_stats_warns_when_issue_search_fails(mock_client, caplog):
    """A silent fallback renders a wrong number; the run must say the count is degraded."""
    mock_client.graphql_query.return_value = {
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
                    "totalCount": 1,
                    "nodes": [{"stargazers": {"totalCount": 10}}],
                    "pageInfo": {"hasNextPage": False, "endCursor": None},
                },
            }
        }
    }
    mock_client.rest_get.side_effect = APIError("rate limited")

    config = UserStatsFetchConfig(username="testuser", token="fake-token")
    with caplog.at_level(logging.WARNING, logger="src.github.fetcher"):
        stats = fetch_user_stats(config)

    # Falls back to the GraphQL count rather than failing
    assert stats["totalIssues"] == 10
    assert "Issue search failed" in caplog.text


def test_fetch_user_stats_commits_year_uses_a_date_bounded_query(mock_client):
    """--commits-year switches to a second query shape that nothing covered before."""
    mock_client.graphql_query.return_value = {
        "data": {
            "user": {
                "name": "Test User",
                "login": "testuser",
                "contributionsCollection": {
                    "totalCommitContributions": 42,
                    "totalPullRequestReviewContributions": 7,
                },
                "repositoriesContributedTo": {"totalCount": 3},
                "pullRequests": {"totalCount": 20},
                "mergedPullRequests": {"totalCount": 15},
                "openIssues": {"totalCount": 1},
                "closedIssues": {"totalCount": 1},
                "followers": {"totalCount": 9},
                "repositories": {
                    "totalCount": 2,
                    "nodes": [{"stargazers": {"totalCount": 4}}],
                    "pageInfo": {"hasNextPage": False, "endCursor": None},
                },
            }
        }
    }
    mock_client.rest_get.return_value = {"total_count": 2}

    config = UserStatsFetchConfig(username="testuser", token="fake-token", commits_year=2023)
    stats = fetch_user_stats(config)

    query, variables = mock_client.graphql_query.call_args[0]
    assert "$from: DateTime!" in query
    assert "$to: DateTime!" in query
    assert "contributionsCollection(from: $from, to: $to)" in query
    assert variables["from"] == "2023-01-01T00:00:00Z"
    assert variables["to"] == "2023-12-31T23:59:59Z"
    assert stats["totalCommits"] == 42


def test_fetch_user_stats_without_commits_year_omits_the_date_range(mock_client):
    mock_client.graphql_query.return_value = {
        "data": {
            "user": {
                "name": "Test User",
                "login": "testuser",
                "contributionsCollection": {
                    "totalCommitContributions": 42,
                    "totalPullRequestReviewContributions": 7,
                },
                "repositoriesContributedTo": {"totalCount": 3},
                "pullRequests": {"totalCount": 20},
                "mergedPullRequests": {"totalCount": 15},
                "openIssues": {"totalCount": 1},
                "closedIssues": {"totalCount": 1},
                "followers": {"totalCount": 9},
                "repositories": {
                    "totalCount": 2,
                    "nodes": [{"stargazers": {"totalCount": 4}}],
                    "pageInfo": {"hasNextPage": False, "endCursor": None},
                },
            }
        }
    }
    mock_client.rest_get.return_value = {"total_count": 2}

    fetch_user_stats(UserStatsFetchConfig(username="testuser", token="fake-token"))

    query, variables = mock_client.graphql_query.call_args[0]
    assert "$from: DateTime!" not in query
    assert "from" not in variables

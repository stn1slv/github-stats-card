"""Tests for contributor stats fetcher."""

from unittest.mock import AsyncMock, patch

import pytest

from src.core.config import ContribFetchConfig
from src.core.exceptions import FetchError
from src.github.fetcher import _build_contrib_query, fetch_contributor_stats


@pytest.fixture
def mock_client():
    with patch("src.github.fetcher.GitHubClient") as MockClient:
        client_instance = MockClient.return_value
        client_instance.fetch_image.return_value = b"fake_image_data"
        client_instance.async_fetch_image = AsyncMock(return_value=b"fake_image_data")
        client_instance.async_graphql_query = AsyncMock()
        client_instance.__aenter__ = AsyncMock(return_value=client_instance)
        client_instance.__aexit__ = AsyncMock(return_value=None)

        yield client_instance


def setup_mock_response(mock_client, repos_data):
    """Helper to set up the two-step GraphQL query mock."""

    # 1. Years response
    years_response = {"data": {"user": {"contributionsCollection": {"contributionYears": [2024]}}}}

    # 2. Contributions response
    commit_contribs = []
    for repo in repos_data:
        repo_node = {
            "nameWithOwner": repo["nameWithOwner"],
            "isPrivate": repo["isPrivate"],
            "stargazers": repo["stargazers"],
            "owner": repo["owner"],
        }

        # Add total commit count if provided
        if "total_repo_commits" in repo:
            repo_node["object"] = {"history": {"totalCount": repo["total_repo_commits"]}}

        commit_contribs.append(
            {
                "repository": repo_node,
                "contributions": {"totalCount": repo.get("commits", 1)},
            }
        )

    contribs_response = {
        "data": {
            "user": {
                "contributionsCollection": {
                    "commitContributionsByRepository": commit_contribs,
                    "pullRequestContributionsByRepository": [],
                    "issueContributionsByRepository": [],
                    "pullRequestReviewContributionsByRepository": [],
                }
            }
        }
    }

    mock_client.async_graphql_query.side_effect = [years_response, contribs_response]


def test_fetch_contributor_stats_success(mock_client):
    """Test successful fetching of contributor stats."""
    repos = [
        {
            "nameWithOwner": "owner/repo1",
            "isPrivate": False,
            "stargazers": {"totalCount": 100},
            "owner": {"avatarUrl": "http://avatar1", "login": "owner"},
            "commits": 10,
            "total_repo_commits": 200,  # Neutral modifier
        },
        {
            "nameWithOwner": "owner/repo2",
            "isPrivate": False,
            "stargazers": {"totalCount": 50},
            "owner": {"avatarUrl": "http://avatar2", "login": "owner"},
            "commits": 5,
            "total_repo_commits": 20,  # Low modifier (-)
        },
    ]
    setup_mock_response(mock_client, repos)

    config = ContribFetchConfig(username="user", token="token", limit=5)
    stats = fetch_contributor_stats(config)

    assert len(stats["repos"]) == 2
    assert stats["repos"][0]["name"] == "owner/repo1"
    assert stats["repos"][0]["stars"] == 100
    assert stats["repos"][0]["commits"] == 10
    # Stars=100 -> C. RepoCommits=200 (Neutral) -> "C"
    assert stats["repos"][0]["rank_level"] == "C"

    assert stats["repos"][1]["name"] == "owner/repo2"
    assert stats["repos"][1]["stars"] == 50
    assert stats["repos"][1]["commits"] == 5
    # Stars=50 -> C. RepoCommits=20 (<100) -> "C-"
    assert stats["repos"][1]["rank_level"] == "C-"


def test_fetch_contributor_stats_sorting(mock_client):
    """Test that repos are sorted by stars."""
    repos = [
        {
            "nameWithOwner": "owner/small",
            "isPrivate": False,
            "stargazers": {"totalCount": 10},
            "owner": {"avatarUrl": "http://avatar", "login": "owner"},
        },
        {
            "nameWithOwner": "owner/big",
            "isPrivate": False,
            "stargazers": {"totalCount": 500},
            "owner": {"avatarUrl": "http://avatar", "login": "owner"},
        },
    ]
    setup_mock_response(mock_client, repos)

    config = ContribFetchConfig(username="user", token="token", limit=5)
    stats = fetch_contributor_stats(config)

    assert stats["repos"][0]["name"] == "owner/big"
    assert stats["repos"][1]["name"] == "owner/small"


def test_fetch_contributor_stats_limit(mock_client):
    """Test that results are limited."""
    repos = [
        {
            "nameWithOwner": f"owner/repo{i}",
            "isPrivate": False,
            "stargazers": {"totalCount": 100 - i},
            "owner": {"avatarUrl": "http://avatar", "login": "owner"},
        }
        for i in range(10)
    ]
    setup_mock_response(mock_client, repos)

    config = ContribFetchConfig(username="user", token="token", limit=3)
    stats = fetch_contributor_stats(config)

    assert len(stats["repos"]) == 3
    assert stats["repos"][0]["name"] == "owner/repo0"


def test_fetch_contributor_stats_exclude(mock_client):
    """Test excluded repositories are filtered out."""
    repos = [
        {
            "nameWithOwner": "owner/keep",
            "isPrivate": False,
            "stargazers": {"totalCount": 100},
            "owner": {"avatarUrl": "http://avatar", "login": "owner"},
        },
        {
            "nameWithOwner": "owner/skip",
            "isPrivate": False,
            "stargazers": {"totalCount": 100},
            "owner": {"avatarUrl": "http://avatar", "login": "owner"},
        },
    ]
    setup_mock_response(mock_client, repos)

    config = ContribFetchConfig(username="user", token="token", limit=5, exclude_repo=["owner/skip"])
    stats = fetch_contributor_stats(config)

    assert len(stats["repos"]) == 1
    assert stats["repos"][0]["name"] == "owner/keep"


def test_fetch_contributor_stats_exclude_wildcard(mock_client):
    """Test wildcard repository exclusion."""
    repos = [
        {
            "nameWithOwner": "owner/keep",
            "isPrivate": False,
            "stargazers": {"totalCount": 100},
            "owner": {"avatarUrl": "url", "login": "owner"},
        },
        {
            "nameWithOwner": "awesome-app-1",
            "isPrivate": False,
            "stargazers": {"totalCount": 100},
            "owner": {"avatarUrl": "url", "login": "other"},
        },
        {
            "nameWithOwner": "awesome-app-2",
            "isPrivate": False,
            "stargazers": {"totalCount": 100},
            "owner": {"avatarUrl": "url", "login": "other"},
        },
    ]
    setup_mock_response(mock_client, repos)

    config = ContribFetchConfig(username="user", token="token", limit=5, exclude_repo=["awesome-*"])
    stats = fetch_contributor_stats(config)

    assert len(stats["repos"]) == 1
    assert stats["repos"][0]["name"] == "owner/keep"


def test_fetch_error(mock_client):
    """Test error handling."""
    mock_client.async_graphql_query.side_effect = [{"errors": [{"message": "Bad query"}]}]

    config = ContribFetchConfig(username="user", token="token")
    with pytest.raises(FetchError, match="GraphQL error"):
        fetch_contributor_stats(config)


def test_fetch_contributor_stats_partial_error(mock_client):
    """Test that fetcher continues if one year fails with GraphQL errors."""
    # 1. Years response (2 years)
    years_response = {"data": {"user": {"contributionsCollection": {"contributionYears": [2024, 2023]}}}}

    # 2. 2024 response (errors)
    error_response = {"errors": [{"message": "Some error"}]}

    # 3. 2023 response (success)
    success_response = {
        "data": {
            "user": {
                "contributionsCollection": {
                    "commitContributionsByRepository": [
                        {
                            "repository": {
                                "nameWithOwner": "owner/repo",
                                "isPrivate": False,
                                "stargazers": {"totalCount": 100},
                                "owner": {"avatarUrl": "url", "login": "owner"},
                            },
                            "contributions": {"totalCount": 1},
                        }
                    ],
                    "pullRequestContributionsByRepository": [],
                    "issueContributionsByRepository": [],
                    "pullRequestReviewContributionsByRepository": [],
                }
            }
        }
    }

    mock_client.async_graphql_query.side_effect = [years_response, error_response, success_response]

    config = ContribFetchConfig(username="user", token="token", limit=5)
    stats = fetch_contributor_stats(config)

    assert len(stats["repos"]) == 1
    assert stats["repos"][0]["name"] == "owner/repo"


def test_fetch_contributor_stats_deduplication(mock_client):
    """Test that same repo across different contribution types is deduplicated."""
    # 1. Years response
    years_response = {"data": {"user": {"contributionsCollection": {"contributionYears": [2024]}}}}

    # 2. Contributions response with duplicate repo in commits and PRs
    repo_node = {
        "nameWithOwner": "owner/repo",
        "isPrivate": False,
        "stargazers": {"totalCount": 100},
        "owner": {"avatarUrl": "http://avatar", "login": "owner"},
    }

    contribs_response = {
        "data": {
            "user": {
                "contributionsCollection": {
                    "commitContributionsByRepository": [{"repository": repo_node, "contributions": {"totalCount": 1}}],
                    "pullRequestContributionsByRepository": [
                        {
                            "repository": repo_node,
                            "contributions": {"nodes": [{"pullRequest": {"state": "MERGED"}}]},
                        }
                    ],
                    "issueContributionsByRepository": [],
                    "pullRequestReviewContributionsByRepository": [],
                }
            }
        }
    }
    mock_client.async_graphql_query.side_effect = [years_response, contribs_response]

    config = ContribFetchConfig(username="user", token="token", limit=5, contribution_types=["commits", "prs"])
    stats = fetch_contributor_stats(config)

    assert len(stats["repos"]) == 1
    assert stats["repos"][0]["name"] == "owner/repo"
    assert stats["repos"][0]["commits"] == 1
    assert stats["repos"][0]["prs"] == 1


def test_fetch_contributor_stats_rank_calculation(mock_client):
    """Test rank calculation with repo magnitude (total commits)."""
    # 1. Years response (2 years)
    years_response = {"data": {"user": {"contributionsCollection": {"contributionYears": [2024]}}}}

    # Repo S: S tier stars (>10k), >5000 repo commits -> S+
    repo_s = {
        "nameWithOwner": "owner/repo-s",
        "isPrivate": False,
        "stargazers": {"totalCount": 10001},
        "owner": {"avatarUrl": "url", "login": "owner"},
        "object": {"history": {"totalCount": 6000}},
    }

    # Repo A: A tier stars (>1k), <100 repo commits -> A-
    repo_a = {
        "nameWithOwner": "owner/repo-a",
        "isPrivate": False,
        "stargazers": {"totalCount": 1001},
        "owner": {"avatarUrl": "url", "login": "owner"},
        "object": {"history": {"totalCount": 50}},
    }

    # 2. 2024 response
    response_2024 = {
        "data": {
            "user": {
                "contributionsCollection": {
                    "commitContributionsByRepository": [
                        {"repository": repo_s, "contributions": {"totalCount": 1}},
                        {"repository": repo_a, "contributions": {"totalCount": 1}},
                    ],
                    "pullRequestContributionsByRepository": [],
                    "issueContributionsByRepository": [],
                    "pullRequestReviewContributionsByRepository": [],
                }
            }
        }
    }

    mock_client.async_graphql_query.side_effect = [years_response, response_2024]

    config = ContribFetchConfig(username="user", token="token", limit=5)
    stats = fetch_contributor_stats(config)

    assert len(stats["repos"]) == 2

    # Check Repo S
    s_repo = next(r for r in stats["repos"] if r["name"] == "owner/repo-s")
    assert s_repo["rank_level"] == "S+"  # 10001 Stars, 6000 commits

    # Check Repo A
    a_repo = next(r for r in stats["repos"] if r["name"] == "owner/repo-a")
    assert a_repo["rank_level"] == "A-"  # 1001 Stars, 50 commits


@pytest.mark.anyio
async def test_fetch_contributor_stats_inside_event_loop():
    """Test that fetch_contributor_stats raises FetchError when called inside a running loop."""
    config = ContribFetchConfig(username="user", token="token")
    with pytest.raises(FetchError, match="event loop is already running"):
        fetch_contributor_stats(config)


def test_build_contrib_query():
    # Test with all types
    query_all = _build_contrib_query(["commits", "prs", "issues", "reviews"])
    assert "commitContributionsByRepository" in query_all
    assert "pullRequestContributionsByRepository" in query_all
    assert "issueContributionsByRepository" in query_all
    assert "pullRequestReviewContributionsByRepository" in query_all

    # Test with partial types
    query_partial = _build_contrib_query(["commits", "prs"])
    assert "commitContributionsByRepository" in query_partial
    assert "pullRequestContributionsByRepository" in query_partial
    assert "issueContributionsByRepository" not in query_partial
    assert "pullRequestReviewContributionsByRepository" not in query_partial


def test_build_contrib_query_empty_raises():
    """Test that _build_contrib_query raises ValueError on empty list."""
    with pytest.raises(ValueError, match="must not be empty"):
        _build_contrib_query([])


def test_fetch_contributor_stats_pr_filtering(mock_client):
    """Test that PR contributions are filtered by state (OPEN/MERGED)."""
    # 1. Years response
    years_response = {"data": {"user": {"contributionsCollection": {"contributionYears": [2024]}}}}

    # 2. Contributions response with PRs in different states
    repo_node = {
        "nameWithOwner": "owner/repo",
        "isPrivate": False,
        "stargazers": {"totalCount": 100},
        "owner": {"avatarUrl": "url", "login": "owner"},
        "object": {"history": {"totalCount": 100}},
    }

    contribs_response = {
        "data": {
            "user": {
                "contributionsCollection": {
                    "commitContributionsByRepository": [],
                    "pullRequestContributionsByRepository": [
                        {
                            "repository": repo_node,
                            "contributions": {
                                "nodes": [
                                    {"pullRequest": {"state": "OPEN"}},
                                    {"pullRequest": {"state": "MERGED"}},
                                    {"pullRequest": {"state": "CLOSED"}},  # Should be ignored
                                ]
                            },
                        }
                    ],
                    "issueContributionsByRepository": [],
                    "pullRequestReviewContributionsByRepository": [],
                }
            }
        }
    }

    mock_client.async_graphql_query.side_effect = [years_response, contribs_response]

    config = ContribFetchConfig(username="user", token="token", limit=5, contribution_types=["prs"])
    stats = fetch_contributor_stats(config)

    assert len(stats["repos"]) == 1
    assert stats["repos"][0]["name"] == "owner/repo"
    # Should count 2 (OPEN + MERGED)
    assert stats["repos"][0]["prs"] == 2


def test_fetch_contributor_stats_partial_errors_with_data(mock_client):
    """Test that fetcher processes valid data even when GraphQL returns partial errors."""
    # 1. Years response
    years_response = {"data": {"user": {"contributionsCollection": {"contributionYears": [2024]}}}}

    # 2. Contributions response with both data and errors (e.g., SAML warning or broken node)
    repo_node = {
        "nameWithOwner": "owner/repo",
        "isPrivate": False,
        "stargazers": {"totalCount": 150},
        "owner": {"avatarUrl": "http://avatar", "login": "owner"},
    }

    contribs_response = {
        "errors": [{"message": "Could not resolve to a Repository", "type": "NOT_FOUND"}],
        "data": {
            "user": {
                "contributionsCollection": {
                    "commitContributionsByRepository": [{"repository": repo_node, "contributions": {"totalCount": 5}}],
                    "pullRequestContributionsByRepository": [],
                    "issueContributionsByRepository": [],
                    "pullRequestReviewContributionsByRepository": [],
                }
            }
        },
    }

    mock_client.async_graphql_query.side_effect = [years_response, contribs_response]

    config = ContribFetchConfig(username="user", token="token", limit=5)
    stats = fetch_contributor_stats(config)

    assert len(stats["repos"]) == 1
    assert stats["repos"][0]["name"] == "owner/repo"
    assert stats["repos"][0]["commits"] == 5

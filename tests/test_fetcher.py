"""Tests for contributor stats fetcher."""

from unittest.mock import patch
import pytest
from src.core.config import ContribFetchConfig
from src.github.fetcher import fetch_contributor_stats
from src.core.exceptions import FetchError


@pytest.fixture
def mock_client():
    with (
        patch("src.github.fetcher.GitHubClient") as MockClient,
        patch("src.github.fetcher.fetch_stats") as mock_fetch_stats,
    ):

        client_instance = MockClient.return_value
        client_instance.fetch_image.return_value = b"fake_image_data"

        mock_fetch_stats.return_value = {
            "totalCommits": 1000,
            "totalPRs": 100,
            "totalIssues": 50,
            "totalStars": 500,
            "totalReviews": 20,
            "followers": 10,
            "contributedTo": 5,
        }

        yield client_instance


def setup_mock_response(mock_client, repos_data):
    """Helper to set up the two-step GraphQL query mock."""

    # 1. Years response
    years_response = {"data": {"user": {"contributionsCollection": {"contributionYears": [2024]}}}}

    # 2. Contributions response
    commit_contribs = []
    for repo in repos_data:
        commit_contribs.append(
            {
                "repository": {
                    "nameWithOwner": repo["nameWithOwner"],
                    "isPrivate": repo["isPrivate"],
                    "stargazers": repo["stargazers"],
                    "owner": repo["owner"],
                },
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

    mock_client.graphql_query.side_effect = [years_response, contribs_response]


def test_fetch_contributor_stats_success(mock_client):
    """Test successful fetching of contributor stats."""
    repos = [
        {
            "nameWithOwner": "owner/repo1",
            "isPrivate": False,
            "stargazers": {"totalCount": 100},
            "owner": {"avatarUrl": "http://avatar1", "login": "owner"},
            "commits": 10,
        },
        {
            "nameWithOwner": "owner/repo2",
            "isPrivate": False,
            "stargazers": {"totalCount": 50},
            "owner": {"avatarUrl": "http://avatar2", "login": "owner"},
            "commits": 5,
        },
    ]
    setup_mock_response(mock_client, repos)

    config = ContribFetchConfig(username="user", token="token", limit=5)
    stats = fetch_contributor_stats(config)

    assert len(stats["repos"]) == 2
    assert stats["repos"][0]["name"] == "owner/repo1"
    assert stats["repos"][0]["stars"] == 100
    assert stats["repos"][0]["commits"] == 10
    assert "rank_level" in stats["repos"][0]
    assert stats["repos"][1]["name"] == "owner/repo2"
    assert stats["repos"][1]["stars"] == 50
    assert stats["repos"][1]["commits"] == 5


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
    repos = []
    for i in range(10):
        repos.append(
            {
                "nameWithOwner": f"owner/repo{i}",
                "isPrivate": False,
                "stargazers": {"totalCount": 100 - i},
                "owner": {"avatarUrl": "http://avatar", "login": "owner"},
            }
        )
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

    config = ContribFetchConfig(
        username="user", token="token", limit=5, exclude_repo=["owner/skip"]
    )
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
    mock_client.graphql_query.side_effect = [{"errors": [{"message": "Bad query"}]}]

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

    mock_client.graphql_query.side_effect = [years_response, error_response, success_response]

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
                    "commitContributionsByRepository": [
                        {"repository": repo_node, "contributions": {"totalCount": 1}}
                    ],
                    "pullRequestContributionsByRepository": [
                        {"repository": repo_node, "contributions": {"totalCount": 1}}
                    ],
                    "issueContributionsByRepository": [],
                    "pullRequestReviewContributionsByRepository": [],
                }
            }
        }
    }

    mock_client.graphql_query.side_effect = [years_response, contribs_response]

    config = ContribFetchConfig(username="user", token="token", limit=5)
    stats = fetch_contributor_stats(config)

    assert len(stats["repos"]) == 1
    assert stats["repos"][0]["name"] == "owner/repo"
    assert stats["repos"][0]["commits"] == 1
    assert stats["repos"][0]["prs"] == 1

"""Tests for GitHub language data fetching."""

from unittest.mock import patch, MagicMock
import pytest
import requests

from src.github.langs_fetcher import fetch_top_languages, Language, LanguageFetchError


def test_language_dataclass():
    lang = Language(name="Python", color="#3572A5", size=1000, count=2)
    assert lang.name == "Python"
    assert lang.color == "#3572A5"
    assert lang.size == 1000
    assert lang.count == 2


@patch("requests.post")
def test_fetch_top_languages_success(mock_post):
    # Mock GraphQL response
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "data": {
            "user": {
                "repositories": {
                    "nodes": [
                        {
                            "name": "repo1",
                            "languages": {
                                "edges": [
                                    {"size": 100, "node": {"name": "Python", "color": "#3572A5"}},
                                    {
                                        "size": 50,
                                        "node": {"name": "JavaScript", "color": "#f1e05a"},
                                    },
                                ]
                            },
                        }
                    ]
                }
            }
        }
    }
    mock_post.return_value = mock_response

    result = fetch_top_languages("testuser", "testtoken")

    assert len(result) == 2
    assert "Python" in result
    assert result["Python"].size == 100
    assert result["JavaScript"].size == 50
    assert result["Python"].color == "#3572A5"


@patch("requests.post")
def test_fetch_top_languages_exclude_repos(mock_post):
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "data": {
            "user": {
                "repositories": {
                    "nodes": [
                        {
                            "name": "repo1",
                            "languages": {"edges": [{"size": 100, "node": {"name": "Python"}}]},
                        },
                        {
                            "name": "repo2",
                            "languages": {"edges": [{"size": 200, "node": {"name": "JavaScript"}}]},
                        },
                    ]
                }
            }
        }
    }
    mock_post.return_value = mock_response

    result = fetch_top_languages("testuser", "testtoken", exclude_repo=["repo2"])

    assert len(result) == 1
    assert "Python" in result
    assert "JavaScript" not in result


@patch("requests.post")
def test_fetch_top_languages_with_weights(mock_post):
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "data": {
            "user": {
                "repositories": {
                    "nodes": [
                        {
                            "name": "repo1",
                            "languages": {"edges": [{"size": 100, "node": {"name": "Python"}}]},
                        },
                        {
                            "name": "repo2",
                            "languages": {"edges": [{"size": 100, "node": {"name": "Python"}}]},
                        },
                    ]
                }
            }
        }
    }
    mock_post.return_value = mock_response

    # size^0.5 * count^1.0 = (200^0.5) * (2^1.0) = 14.14 * 2 = 28.28 -> 28
    result = fetch_top_languages("testuser", "testtoken", size_weight=0.5, count_weight=1.0)

    assert result["Python"].size == 28


@patch("requests.post")
def test_fetch_top_languages_api_error(mock_post):
    mock_response = MagicMock()
    mock_response.status_code = 404
    mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError("Not Found")
    mock_post.return_value = mock_response

    with pytest.raises(LanguageFetchError, match="Failed to fetch data"):
        fetch_top_languages("testuser", "testtoken")


@patch("requests.post")
def test_fetch_top_languages_network_error(mock_post):
    mock_post.side_effect = requests.exceptions.ConnectionError("Connection failed")

    with pytest.raises(LanguageFetchError, match="Failed to fetch data"):
        fetch_top_languages("testuser", "testtoken")


@patch("requests.post")
def test_fetch_top_languages_no_data(mock_post):
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"data": None}
    mock_post.return_value = mock_response

    with pytest.raises(LanguageFetchError, match="No data returned"):
        fetch_top_languages("testuser", "testtoken")


@patch("requests.post")
def test_fetch_top_languages_user_not_found(mock_post):
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"data": {"user": None}}
    mock_post.return_value = mock_response

    with pytest.raises(LanguageFetchError, match="User 'testuser' not found"):
        fetch_top_languages("testuser", "testtoken")


@patch("requests.post")
def test_fetch_top_languages_missing_color(mock_post):
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "data": {
            "user": {
                "repositories": {
                    "nodes": [
                        {
                            "name": "repo1",
                            "languages": {
                                "edges": [{"size": 100, "node": {"name": "Python", "color": None}}]
                            },
                        }
                    ]
                }
            }
        }
    }
    mock_post.return_value = mock_response

    result = fetch_top_languages("testuser", "testtoken")
    assert result["Python"].color == "#858585"  # Default color

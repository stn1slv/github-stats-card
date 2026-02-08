"""Tests for environment variable API URL configuration."""

import os
from unittest import mock


def test_default_api_urls():
    """Test that default GitHub.com URLs are used when env vars are not set."""
    # Clear any existing env vars
    with mock.patch.dict(os.environ, {}, clear=True):
        # Need to reload the module to pick up environment changes
        import importlib
        from src.core import constants

        importlib.reload(constants)

        assert constants.API_BASE_URL == "https://api.github.com"
        assert constants.GRAPHQL_ENDPOINT == "https://api.github.com/graphql"


def test_custom_api_url_env_var():
    """Test that GITHUB_API_URL environment variable is respected."""
    custom_api_url = "https://github.enterprise.com/api/v3"
    with mock.patch.dict(os.environ, {"GITHUB_API_URL": custom_api_url}, clear=True):
        import importlib
        from src.core import constants

        importlib.reload(constants)

        assert constants.API_BASE_URL == custom_api_url
        # GraphQL should use the custom base URL
        assert constants.GRAPHQL_ENDPOINT == f"{custom_api_url}/graphql"


def test_custom_graphql_url_env_var():
    """Test that GITHUB_GRAPHQL_URL environment variable is respected."""
    custom_graphql_url = "https://github.enterprise.com/api/graphql"
    with mock.patch.dict(os.environ, {"GITHUB_GRAPHQL_URL": custom_graphql_url}, clear=True):
        import importlib
        from src.core import constants

        importlib.reload(constants)

        # API base should still be default
        assert constants.API_BASE_URL == "https://api.github.com"
        # GraphQL should use the custom URL
        assert constants.GRAPHQL_ENDPOINT == custom_graphql_url


def test_both_custom_env_vars():
    """Test that both environment variables can be set independently."""
    custom_api_url = "https://ghe.company.com/api/v3"
    custom_graphql_url = "https://ghe.company.com/api/graphql"
    with mock.patch.dict(
        os.environ,
        {
            "GITHUB_API_URL": custom_api_url,
            "GITHUB_GRAPHQL_URL": custom_graphql_url,
        },
        clear=True,
    ):
        import importlib
        from src.core import constants

        importlib.reload(constants)

        assert constants.API_BASE_URL == custom_api_url
        assert constants.GRAPHQL_ENDPOINT == custom_graphql_url


def test_fetcher_uses_api_base_url():
    """Test that fetcher module correctly imports and would use API_BASE_URL."""
    # Reset environment to ensure default values
    with mock.patch.dict(os.environ, {}, clear=True):
        import importlib
        from src.core import constants
        from src.github import fetcher

        # Reload both modules to pick up clean environment
        importlib.reload(constants)
        importlib.reload(fetcher)

        # Now check that fetcher's API_BASE_URL matches constants
        assert fetcher.API_BASE_URL == constants.API_BASE_URL

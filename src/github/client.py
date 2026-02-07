"""GitHub API client for making authenticated requests."""

from typing import Any

import requests

from ..core.constants import API_TIMEOUT, GRAPHQL_ENDPOINT


class GitHubClient:
    """Helper client for GitHub API interactions."""

    def __init__(self, token: str):
        self.token = token
        self.headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        }

    def graphql_query(self, query: str, variables: dict[str, Any] | None = None) -> dict[str, Any]:
        """
        Execute a GraphQL query.

        Args:
            query: GraphQL query string
            variables: Optional variables for the query

        Returns:
            JSON response data

        Raises:
            requests.exceptions.RequestException: If API request fails
        """
        response = requests.post(
            GRAPHQL_ENDPOINT,
            json={"query": query, "variables": variables or {}},
            headers=self.headers,
            timeout=API_TIMEOUT,
        )
        response.raise_for_status()
        return response.json()

    def rest_get(self, url: str, headers: dict[str, str] | None = None) -> dict[str, Any]:
        """
        Execute a REST GET request.

        Args:
            url: Full URL for the request
            headers: Optional additional headers

        Returns:
            JSON response data

        Raises:
            requests.exceptions.RequestException: If API request fails
        """
        request_headers = self.headers.copy()
        if headers:
            request_headers.update(headers)

        response = requests.get(
            url,
            headers=request_headers,
            timeout=API_TIMEOUT,
        )
        response.raise_for_status()
        return response.json()
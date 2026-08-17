"""GitHub API client for making authenticated requests."""

import asyncio
from types import TracebackType
from typing import Any, Self, cast

import httpx

from ..core.constants import API_TIMEOUT, GRAPHQL_ENDPOINT
from ..core.exceptions import APIError


def first_graphql_error(payload: object) -> str:
    """
    Describe the first GraphQL error in a response payload.

    Tolerates the shapes a real API and its proxies produce: a missing or empty
    ``errors`` list, and entries that are plain strings rather than objects with
    a ``message``. Indexing or calling ``.get`` on those raises, which turns a
    reportable API failure into an opaque crash.

    Args:
        payload: Decoded GraphQL response, or anything at all

    Returns:
        Human-readable description of the first error
    """
    if not isinstance(payload, dict):
        return "no response payload"
    errors = payload.get("errors") or []
    if not errors:
        return "no error reported"
    first = errors[0]
    return str(first.get("message", first)) if isinstance(first, dict) else str(first)


class GitHubClient:
    """Helper client for GitHub API interactions."""

    def __init__(self, token: str) -> None:
        self.token = token
        self.headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        }
        self.timeout = float(API_TIMEOUT)
        self._client: httpx.Client | None = None
        self._async_client: httpx.AsyncClient | None = None
        self._close_tasks: set[asyncio.Task[Any]] = set()

    @property
    def client(self) -> httpx.Client:
        """Get or create synchronous HTTP client."""
        if self._client is None:
            self._client = httpx.Client(timeout=self.timeout, follow_redirects=True)
        return self._client

    @property
    def async_client(self) -> httpx.AsyncClient:
        """Get or create asynchronous HTTP client."""
        if self._async_client is None:
            self._async_client = httpx.AsyncClient(timeout=self.timeout, follow_redirects=True)
        return self._async_client

    def close(self) -> None:
        """Close synchronous and asynchronous HTTP clients."""
        if self._client:
            self._client.close()
            self._client = None
        if self._async_client:
            try:
                loop = asyncio.get_running_loop()
                task = loop.create_task(self._async_client.aclose())
                self._close_tasks.add(task)
                task.add_done_callback(self._close_tasks.discard)
            except RuntimeError:
                asyncio.run(self._async_client.aclose())
            self._async_client = None

    async def aclose(self) -> None:
        """Close synchronous and asynchronous HTTP clients."""
        if self._client:
            self._client.close()
            self._client = None
        if self._async_client:
            await self._async_client.aclose()
            self._async_client = None

    def __enter__(self) -> Self:
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        self.close()

    async def __aenter__(self) -> Self:
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        await self.aclose()

    def graphql_query(self, query: str, variables: dict[str, Any] | None = None) -> dict[str, Any]:
        """
        Execute a GraphQL query (synchronous).

        Args:
            query: GraphQL query string
            variables: Optional variables for the query

        Returns:
            JSON response data

        Raises:
            APIError: If API request fails
        """
        try:
            response = self.client.post(
                GRAPHQL_ENDPOINT,
                json={"query": query, "variables": variables or {}},
                headers=self.headers,
            )
            response.raise_for_status()
            return cast(dict[str, Any], response.json())
        except httpx.HTTPError as e:
            raise APIError(f"GitHub API request failed: {e}") from e

    async def async_graphql_query(self, query: str, variables: dict[str, Any] | None = None) -> dict[str, Any]:
        """
        Execute a GraphQL query (asynchronous).

        Args:
            query: GraphQL query string
            variables: Optional variables for the query

        Returns:
            JSON response data

        Raises:
            APIError: If API request fails
        """
        try:
            response = await self.async_client.post(
                GRAPHQL_ENDPOINT,
                json={"query": query, "variables": variables or {}},
                headers=self.headers,
            )
            response.raise_for_status()
            return cast(dict[str, Any], response.json())
        except httpx.HTTPError as e:
            raise APIError(f"GitHub API request failed: {e}") from e

    def rest_get(self, url: str, headers: dict[str, str] | None = None) -> dict[str, Any]:
        """
        Execute a REST GET request (synchronous).

        Args:
            url: Full URL for the request
            headers: Optional additional headers

        Returns:
            JSON response data

        Raises:
            APIError: If API request fails
        """
        request_headers = self.headers.copy()
        if headers:
            request_headers.update(headers)

        try:
            response = self.client.get(
                url,
                headers=request_headers,
            )
            response.raise_for_status()
            return cast(dict[str, Any], response.json())
        except httpx.HTTPError as e:
            raise APIError(f"GitHub API request failed: {e}") from e

    async def async_rest_get(self, url: str, headers: dict[str, str] | None = None) -> dict[str, Any]:
        """
        Execute a REST GET request (asynchronous).

        Args:
            url: Full URL for the request
            headers: Optional additional headers

        Returns:
            JSON response data

        Raises:
            APIError: If API request fails
        """
        request_headers = self.headers.copy()
        if headers:
            request_headers.update(headers)

        try:
            response = await self.async_client.get(
                url,
                headers=request_headers,
            )
            response.raise_for_status()
            return cast(dict[str, Any], response.json())
        except httpx.HTTPError as e:
            raise APIError(f"GitHub API request failed: {e}") from e

    def fetch_image(self, url: str) -> bytes | None:
        """
        Fetch an image from a URL (synchronous).

        Args:
            url: Image URL

        Returns:
            Image binary content or None if failed
        """
        try:
            response = self.client.get(url)
            response.raise_for_status()
            return response.content
        except httpx.HTTPError:
            return None

    async def async_fetch_image(self, url: str) -> bytes | None:
        """
        Fetch an image from a URL (asynchronous).

        Args:
            url: Image URL

        Returns:
            Image binary content or None if failed
        """
        try:
            response = await self.async_client.get(url)
            response.raise_for_status()
            return response.content
        except httpx.HTTPError:
            return None

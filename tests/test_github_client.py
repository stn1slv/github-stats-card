"""Tests for GitHub API client."""

import asyncio
from unittest.mock import AsyncMock, MagicMock, PropertyMock, patch

import httpx
import pytest

from src.core.exceptions import APIError
from src.github.client import GitHubClient


@pytest.fixture
def client():
    return GitHubClient(token="fake-token")


def test_client_init(client):
    assert client.token == "fake-token"
    assert client.headers["Authorization"] == "Bearer fake-token"
    assert client.headers["Content-Type"] == "application/json"


def test_graphql_query_success(client):
    with patch("src.github.client.GitHubClient.client", new_callable=PropertyMock) as mock_client_prop:
        mock_httpx_client = MagicMock()
        mock_client_prop.return_value = mock_httpx_client

        mock_response = MagicMock()
        mock_response.json.return_value = {"data": {"user": "test"}}
        mock_response.raise_for_status.return_value = None
        mock_httpx_client.post.return_value = mock_response

        result = client.graphql_query("query", {"var": "val"})

        assert result == {"data": {"user": "test"}}
        mock_httpx_client.post.assert_called_once()


def test_graphql_query_error(client):
    with patch("src.github.client.GitHubClient.client", new_callable=PropertyMock) as mock_client_prop:
        mock_httpx_client = MagicMock()
        mock_client_prop.return_value = mock_httpx_client
        mock_httpx_client.post.side_effect = httpx.HTTPError("Network error")

        with pytest.raises(APIError, match="GitHub API request failed"):
            client.graphql_query("query")


@pytest.mark.anyio
async def test_async_graphql_query_success(client):
    with patch("src.github.client.GitHubClient.async_client", new_callable=PropertyMock) as mock_client_prop:
        mock_httpx_client = MagicMock()
        mock_client_prop.return_value = mock_httpx_client

        mock_httpx_client.post = AsyncMock()
        mock_response = MagicMock()
        mock_response.json.return_value = {"data": {"user": "test"}}
        mock_response.raise_for_status.return_value = None
        mock_httpx_client.post.return_value = mock_response

        result = await client.async_graphql_query("query", {"var": "val"})

        assert result == {"data": {"user": "test"}}
        mock_httpx_client.post.assert_awaited_once()


@pytest.mark.anyio
async def test_async_graphql_query_error(client):
    with patch("src.github.client.GitHubClient.async_client", new_callable=PropertyMock) as mock_client_prop:
        mock_httpx_client = MagicMock()
        mock_client_prop.return_value = mock_httpx_client

        mock_httpx_client.post = AsyncMock(side_effect=httpx.HTTPError("Network error"))

        with pytest.raises(APIError, match="GitHub API request failed"):
            await client.async_graphql_query("query")
        mock_httpx_client.post.assert_awaited_once()


def test_rest_get_success(client):
    with patch("src.github.client.GitHubClient.client", new_callable=PropertyMock) as mock_client_prop:
        mock_httpx_client = MagicMock()
        mock_client_prop.return_value = mock_httpx_client

        mock_response = MagicMock()
        mock_response.json.return_value = {"id": 123}
        mock_response.raise_for_status.return_value = None
        mock_httpx_client.get.return_value = mock_response

        result = client.rest_get("https://api.github.com/user")

        assert result == {"id": 123}
        mock_httpx_client.get.assert_called_once()


def test_rest_get_error(client):
    with patch("src.github.client.GitHubClient.client", new_callable=PropertyMock) as mock_client_prop:
        mock_httpx_client = MagicMock()
        mock_client_prop.return_value = mock_httpx_client
        mock_httpx_client.get.side_effect = httpx.HTTPError("Network error")

        with pytest.raises(APIError, match="GitHub API request failed"):
            client.rest_get("https://api.github.com/user")


def test_fetch_image_success(client):
    with patch("src.github.client.GitHubClient.client", new_callable=PropertyMock) as mock_client_prop:
        mock_httpx_client = MagicMock()
        mock_client_prop.return_value = mock_httpx_client

        mock_response = MagicMock()
        mock_response.content = b"image-data"
        mock_response.raise_for_status.return_value = None
        mock_httpx_client.get.return_value = mock_response

        result = client.fetch_image("https://example.com/image.png")

        assert result == b"image-data"


def test_fetch_image_error(client):
    with patch("src.github.client.GitHubClient.client", new_callable=PropertyMock) as mock_client_prop:
        mock_httpx_client = MagicMock()
        mock_client_prop.return_value = mock_httpx_client
        mock_httpx_client.get.side_effect = httpx.HTTPError("Network error")

        result = client.fetch_image("https://example.com/image.png")

        assert result is None


@pytest.mark.anyio
async def test_async_fetch_image_success(client):
    with patch("src.github.client.GitHubClient.async_client", new_callable=PropertyMock) as mock_client_prop:
        mock_httpx_client = MagicMock()
        mock_client_prop.return_value = mock_httpx_client

        mock_httpx_client.get = AsyncMock()
        mock_response = MagicMock()
        mock_response.content = b"image-data"
        mock_response.raise_for_status.return_value = None
        mock_httpx_client.get.return_value = mock_response

        result = await client.async_fetch_image("https://example.com/image.png")

        assert result == b"image-data"
        mock_httpx_client.get.assert_awaited_once()


@pytest.mark.anyio
async def test_async_fetch_image_error(client):
    with patch("src.github.client.GitHubClient.async_client", new_callable=PropertyMock) as mock_client_prop:
        mock_httpx_client = MagicMock()
        mock_client_prop.return_value = mock_httpx_client

        mock_httpx_client.get = AsyncMock(side_effect=httpx.HTTPError("Network error"))

        result = await client.async_fetch_image("https://example.com/image.png")

        assert result is None
        mock_httpx_client.get.assert_awaited_once()


@pytest.mark.anyio
async def test_context_manager(client):
    with patch("src.github.client.GitHubClient.close") as mock_close:
        with client as c:
            assert c == client
        mock_close.assert_called_once()

    with patch("src.github.client.GitHubClient.aclose", new_callable=AsyncMock) as mock_aclose:
        async with client as c:
            assert c == client
        mock_aclose.assert_called_once()


# ---------------------------------------------------------------------------
# Client lifecycle
# ---------------------------------------------------------------------------
def test_clients_are_created_lazily_and_reused(client):
    assert client._client is None
    assert client._async_client is None

    first = client.client
    assert client.client is first

    first_async = client.async_client
    assert client.async_client is first_async


def test_close_releases_the_sync_client(client):
    client._client = MagicMock()
    sync_client = client._client

    client.close()

    sync_client.close.assert_called_once()
    assert client._client is None


def test_close_without_a_running_loop_awaits_the_async_client(client):
    """close() is the synchronous path, so it must drive the coroutine to completion itself."""
    async_client = MagicMock()
    async_client.aclose = AsyncMock()
    client._async_client = async_client

    client.close()

    async_client.aclose.assert_awaited_once()
    assert client._async_client is None


@pytest.mark.anyio
async def test_close_inside_a_running_loop_schedules_the_aclose(client):
    """asyncio.run() cannot be called from a live loop, so close() must schedule instead."""
    async_client = MagicMock()
    async_client.aclose = AsyncMock()
    client._async_client = async_client

    client.close()
    assert client._async_client is None

    # The close was handed to the loop as a task; let it run
    await asyncio.sleep(0)
    async_client.aclose.assert_awaited_once()


@pytest.mark.anyio
async def test_aclose_releases_both_clients(client):
    sync_client = MagicMock()
    async_client = MagicMock()
    async_client.aclose = AsyncMock()
    client._client = sync_client
    client._async_client = async_client

    await client.aclose()

    sync_client.close.assert_called_once()
    async_client.aclose.assert_awaited_once()
    assert client._client is None
    assert client._async_client is None


def test_context_manager_closes_on_exit():
    with GitHubClient(token="fake-token") as ctx_client:
        ctx_client._client = MagicMock()
        sync_client = ctx_client._client

    sync_client.close.assert_called_once()


@pytest.mark.anyio
async def test_async_context_manager_closes_on_exit():
    async with GitHubClient(token="fake-token") as ctx_client:
        async_client = MagicMock()
        async_client.aclose = AsyncMock()
        ctx_client._async_client = async_client

    async_client.aclose.assert_awaited_once()

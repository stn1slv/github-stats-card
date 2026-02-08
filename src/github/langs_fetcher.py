"""GitHub API client for fetching language statistics."""

from dataclasses import dataclass

import requests  # type: ignore

from ..core.constants import DEFAULT_LANG_COLOR
from ..core.exceptions import LanguageFetchError
from ..core.utils import is_repo_excluded
from .client import GitHubClient


@dataclass
class Language:
    """Represents a programming language with its statistics."""

    name: str
    color: str
    size: int  # bytes (or weighted size)
    count: int  # number of repos using this language


def fetch_top_languages(
    username: str,
    token: str,
    exclude_repo: list[str] | None = None,
    size_weight: float = 1.0,
    count_weight: float = 0.0,
) -> dict[str, Language]:
    """
    Fetch top programming languages for a GitHub user.

    Args:
        username: GitHub username
        token: GitHub Personal Access Token
        exclude_repo: List of repository names to exclude
        size_weight: Weight for byte count in ranking (default: 1.0)
        count_weight: Weight for repo count in ranking (default: 0.0)

    Returns:
        Dictionary mapping language name to Language object, sorted by size descending

    Raises:
        LanguageFetchError: If API request fails or returns errors
    """
    client = GitHubClient(token)
    exclude_repo = exclude_repo or []

    query = """
    query userInfo($login: String!) {
      user(login: $login) {
        repositories(ownerAffiliations: OWNER, isFork: false, first: 100) {
          nodes {
            name
            languages(first: 10, orderBy: {field: SIZE, direction: DESC}) {
              edges {
                size
                node {
                  color
                  name
                }
              }
            }
          }
        }
      }
    }
    """

    try:
        data = client.graphql_query(query, {"login": username})
    except requests.RequestException as e:
        raise LanguageFetchError(f"Failed to fetch data from GitHub API: {e}") from e

    if "errors" in data:
        error_msg = data["errors"][0].get("message", "Unknown GraphQL error")
        raise LanguageFetchError(f"GitHub API error: {error_msg}")

    if "data" not in data or not data["data"]:
        raise LanguageFetchError("No data returned from GitHub API")

    # Get repository nodes
    user_data = data["data"].get("user")
    if not user_data:
        raise LanguageFetchError(f"User '{username}' not found")

    repos = user_data.get("repositories", {}).get("nodes", [])

    # Filter out excluded repositories
    repos = [r for r in repos if not is_repo_excluded(r.get("name", ""), exclude_repo)]

    # Aggregate languages across all repositories
    languages: dict[str, Language] = {}

    for repo in repos:
        lang_edges = repo.get("languages", {}).get("edges", [])
        for edge in lang_edges:
            node = edge.get("node", {})
            lang_name = node.get("name")
            if not lang_name:
                continue

            lang_color = node.get("color") or DEFAULT_LANG_COLOR
            lang_size = edge.get("size", 0)

            if lang_name in languages:
                languages[lang_name].size += lang_size
                languages[lang_name].count += 1
            else:
                languages[lang_name] = Language(
                    name=lang_name,
                    color=lang_color,
                    size=lang_size,
                    count=1,
                )

    # Apply size and count weights for ranking
    for lang in languages.values():
        lang.size = int((lang.size**size_weight) * (lang.count**count_weight))

    # Sort by size descending
    sorted_langs = dict(sorted(languages.items(), key=lambda x: x[1].size, reverse=True))

    return sorted_langs

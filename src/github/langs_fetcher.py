"""GitHub API client for fetching language statistics."""

import logging
from dataclasses import dataclass

from ..core.config import LangsFetchConfig
from ..core.constants import DEFAULT_LANG_COLOR
from ..core.exceptions import APIError, LanguageFetchError
from ..core.utils import is_repo_excluded
from .client import GitHubClient

logger = logging.getLogger(__name__)


@dataclass
class Language:
    """Represents a programming language with its statistics."""

    name: str
    color: str
    size: int  # original bytes
    count: int  # number of repos using this language
    score: int = 0  # weighted score for ranking (set after aggregation)


def fetch_top_languages(config: LangsFetchConfig) -> dict[str, Language]:
    """
    Fetch top programming languages for a GitHub user.

    Args:
        config: Language fetch configuration

    Returns:
        Dictionary mapping language name to Language object, sorted by size descending

    Raises:
        LanguageFetchError: If API request fails or returns errors
    """
    with GitHubClient(config.token) as client:
        username = config.username
        exclude_repo = config.exclude_repo or []
        size_weight = config.size_weight
        count_weight = config.count_weight

        query = """
        query userInfo($login: String!, $after: String) {
          user(login: $login) {
            repositories(ownerAffiliations: OWNER, isFork: false, first: 100, after: $after) {
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
              pageInfo {
                hasNextPage
                endCursor
              }
            }
          }
        }
        """

        # Fetch first page
        try:
            data = client.graphql_query(query, {"login": username})
        except APIError as e:
            raise LanguageFetchError(f"Failed to fetch data from GitHub API: {e}") from e

        if data.get("errors"):
            error_msg = data["errors"][0].get("message", "Unknown GraphQL error")
            raise LanguageFetchError(f"GitHub API error: {error_msg}")

        if "data" not in data or not data["data"]:
            raise LanguageFetchError("No data returned from GitHub API")

        # Get repository nodes
        user_data = data["data"].get("user")
        if not user_data:
            raise LanguageFetchError(f"User '{username}' not found")

        repos_data = user_data.get("repositories", {})
        repos = list(repos_data.get("nodes", []))

        # Paginate through remaining repositories
        page_info = repos_data.get("pageInfo", {})
        while page_info.get("hasNextPage"):
            try:
                page_data = client.graphql_query(query, {"login": username, "after": page_info["endCursor"]})
                page_user = (page_data.get("data") or {}).get("user")
                if not page_user:
                    break
                page_repos = page_user.get("repositories", {})
                repos.extend(page_repos.get("nodes", []))
                page_info = page_repos.get("pageInfo", {})
            except APIError as e:
                # Continue with what we have, but say so: languages used only in
                # the repositories on the unread pages are now missing.
                logger.warning(
                    "Repository pagination failed, language totals may be incomplete: %s",
                    e,
                )
                break

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

        # Compute weighted score for ranking (size is preserved as original bytes)
        for lang in languages.values():
            lang.score = int((lang.size**size_weight) * (lang.count**count_weight))

        # Sort by score descending
        sorted_langs = dict(sorted(languages.items(), key=lambda x: x[1].score, reverse=True))

        return sorted_langs

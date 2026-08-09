"""GitHub API client for fetching user statistics."""

import asyncio
import base64
from typing import Any, TypedDict
from urllib.parse import quote

from ..core.config import ContribFetchConfig, UserStatsFetchConfig
from ..core.constants import API_BASE_URL, VALID_CONTRIB_TYPES
from ..core.exceptions import APIError, FetchError
from ..core.utils import is_repo_excluded
from .client import GitHubClient
from .rank import calculate_repo_rank


class ContributorRepo(TypedDict):
    """Contributor repository details."""

    name: str  # owner/repo
    stars: int
    commits: int
    prs: int
    issues: int
    reviews: int
    rank_level: str
    avatar_b64: str | None


class ContributorStats(TypedDict):
    """Contributor statistics."""

    repos: list[ContributorRepo]


class UserStats(TypedDict):
    """GitHub user statistics."""

    name: str
    login: str
    totalCommits: int
    totalPRs: int
    mergedPRs: int
    totalIssues: int
    totalStars: int
    totalRepos: int
    contributedTo: int
    followers: int
    totalReviews: int
    discussionsStarted: int
    discussionsAnswered: int


def fetch_user_stats(config: UserStatsFetchConfig) -> UserStats:
    """
    Fetch GitHub user statistics via GraphQL and REST APIs.

    Args:
        config: Fetch configuration

    Returns:
        Dictionary with user statistics

    Raises:
        FetchError: If API request fails
    """
    with GitHubClient(config.token) as client:
        username = config.username
        include_all_commits = config.include_all_commits
        commits_year = config.commits_year
        show = config.show or []

        # Build date range for commits_year filter
        from_date = None
        to_date = None
        if commits_year is not None:
            from_date = f"{commits_year}-01-01T00:00:00Z"
            to_date = f"{commits_year}-12-31T23:59:59Z"

        # GraphQL query with optional date range for commits
        variables: dict[str, Any] = {"login": username}
        if commits_year is not None:
            query = """
            query userInfo($login: String!, $from: DateTime!, $to: DateTime!) {
              user(login: $login) {
                name
                login
                contributionsCollection(from: $from, to: $to) {
                  totalCommitContributions
                  totalPullRequestReviewContributions
                }
                repositoriesContributedTo(
                  first: 1
                  includeUserRepositories: true
                  contributionTypes: [COMMIT, ISSUE, PULL_REQUEST, REPOSITORY]
                ) {
                  totalCount
                }
                pullRequests(first: 1) {
                  totalCount
                }
                mergedPullRequests: pullRequests(states: MERGED) {
                  totalCount
                }
                openIssues: issues(states: OPEN) {
                  totalCount
                }
                closedIssues: issues(states: CLOSED) {
                  totalCount
                }
                followers {
                  totalCount
                }
                repositories(
                  first: 100
                  ownerAffiliations: OWNER
                  orderBy: {direction: DESC, field: STARGAZERS}
                ) {
                  totalCount
                  nodes {
                    stargazers {
                      totalCount
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
            variables.update({"from": from_date, "to": to_date})
        else:
            query = """
            query userInfo($login: String!) {
              user(login: $login) {
                name
                login
                contributionsCollection {
                  totalCommitContributions
                  totalPullRequestReviewContributions
                }
                repositoriesContributedTo(
                  first: 1
                  includeUserRepositories: true
                  contributionTypes: [COMMIT, ISSUE, PULL_REQUEST, REPOSITORY]
                ) {
                  totalCount
                }
                pullRequests(first: 1) {
                  totalCount
                }
                mergedPullRequests: pullRequests(states: MERGED) {
                  totalCount
                }
                openIssues: issues(states: OPEN) {
                  totalCount
                }
                closedIssues: issues(states: CLOSED) {
                  totalCount
                }
                followers {
                  totalCount
                }
                repositories(
                  first: 100
                  ownerAffiliations: OWNER
                  orderBy: {direction: DESC, field: STARGAZERS}
                ) {
                  totalCount
                  nodes {
                    stargazers {
                      totalCount
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

        # Execute GraphQL query
        try:
            data = client.graphql_query(query, variables)

            if "errors" in data:
                error_msg = data["errors"][0].get("message", "Unknown GraphQL error")
                raise FetchError(f"GraphQL error: {error_msg}")

            user = data.get("data", {}).get("user")
            if not user:
                raise FetchError(f"User '{username}' not found")

        except APIError as e:
            raise FetchError(f"Failed to fetch data from GitHub: {e}") from e

        # Extract totalCount from the first page — pagination queries omit this field
        total_repos = user["repositories"]["totalCount"]

        # Calculate total stars
        total_stars = sum(repo["stargazers"]["totalCount"] for repo in user["repositories"]["nodes"])

        # Handle pagination for repositories if needed
        has_next_page = user["repositories"]["pageInfo"]["hasNextPage"]
        end_cursor = user["repositories"]["pageInfo"]["endCursor"]

        while has_next_page:
            pagination_query = """
            query userRepos($login: String!, $after: String!) {
              user(login: $login) {
                repositories(
                  first: 100
                  after: $after
                  ownerAffiliations: OWNER
                  orderBy: {direction: DESC, field: STARGAZERS}
                ) {
                  nodes {
                    stargazers {
                      totalCount
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

            try:
                page_data = client.graphql_query(pagination_query, {"login": username, "after": end_cursor})

                page_user = page_data.get("data", {}).get("user")
                if page_user:
                    total_stars += sum(repo["stargazers"]["totalCount"] for repo in page_user["repositories"]["nodes"])
                    has_next_page = page_user["repositories"]["pageInfo"]["hasNextPage"]
                    end_cursor = page_user["repositories"]["pageInfo"]["endCursor"]
                else:
                    break

            except APIError:
                # If pagination fails, continue with what we have
                break

        # Get total commits
        total_commits = user["contributionsCollection"]["totalCommitContributions"]

        if include_all_commits:
            # Use REST API to get all-time commit count
            try:
                search_data = client.rest_get(
                    f"{API_BASE_URL}/search/commits?q=author:{quote(username)}",
                    headers={"Accept": "application/vnd.github.cloak-preview+json"},
                )
                total_commits = search_data.get("total_count", total_commits)
            except APIError:
                # If REST API fails, use GraphQL data
                pass

        # Use REST API to get accurate issue count (includes issues in repos user doesn't own)
        total_issues = user["openIssues"]["totalCount"] + user["closedIssues"]["totalCount"]
        try:
            issues_data = client.rest_get(f"{API_BASE_URL}/search/issues?q=author:{quote(username)}+type:issue")
            total_issues = issues_data.get("total_count", total_issues)
        except APIError:
            # If REST API fails, use GraphQL data
            pass

        # Fetch additional stats if requested
        discussions_started = 0
        discussions_answered = 0

        if "discussions_started" in show or "discussions_answered" in show:
            discussions_query = """
            query userDiscussions($login: String!) {
              user(login: $login) {
                repositoryDiscussions {
                  totalCount
                }
                repositoryDiscussionComments(onlyAnswers: true) {
                  totalCount
                }
              }
            }
            """

            try:
                disc_data = client.graphql_query(discussions_query, {"login": username})
                disc_user = disc_data.get("data", {}).get("user", {})

                discussions_started = disc_user.get("repositoryDiscussions", {}).get("totalCount", 0)
                discussions_answered = disc_user.get("repositoryDiscussionComments", {}).get("totalCount", 0)
            except APIError:
                # If discussions query fails, continue with zeros
                pass

        return {
            "name": user["name"] or user["login"],
            "login": user["login"],
            "totalCommits": total_commits,
            "totalPRs": user["pullRequests"]["totalCount"],
            "mergedPRs": user["mergedPullRequests"]["totalCount"],
            "totalIssues": total_issues,
            "totalStars": total_stars,
            "totalRepos": total_repos,
            "contributedTo": user["repositoriesContributedTo"]["totalCount"],
            "followers": user["followers"]["totalCount"],
            "totalReviews": user["contributionsCollection"]["totalPullRequestReviewContributions"],
            "discussionsStarted": discussions_started,
            "discussionsAnswered": discussions_answered,
        }


_CONTRIB_YEARS_QUERY = """
query userYears($login: String!) {
  user(login: $login) {
    contributionsCollection {
      contributionYears
    }
  }
}
"""

# Shared fragment for repository details.
_REPO_DETAILS_FRAGMENT = """
  repository {
    nameWithOwner
    isPrivate
    owner {
      login
      avatarUrl
    }
    stargazers {
      totalCount
    }
    object(expression: "HEAD") {
      ... on Commit {
        history {
          totalCount
        }
      }
    }
  }
"""


def _build_contrib_query(contribution_types: list[str]) -> str:
    """Build the GraphQL query dynamically based on requested contribution types."""
    if not contribution_types:
        msg = "contribution_types must not be empty"
        raise ValueError(msg)

    invalid = [t for t in contribution_types if t not in VALID_CONTRIB_TYPES]
    if invalid:
        msg = (
            f"Unrecognized contribution types: {', '.join(invalid)}. Allowed: {', '.join(sorted(VALID_CONTRIB_TYPES))}"
        )
        raise ValueError(msg)

    fragments = []

    if "commits" in contribution_types:
        fragments.append(f"""
      commitContributionsByRepository(maxRepositories: 100) {{
        {_REPO_DETAILS_FRAGMENT}
        contributions {{ totalCount }}
      }}""")
    if "prs" in contribution_types:
        # For PRs, we need nodes to check their state (OPEN/MERGED).
        # `first: 100` caps retrieval per repository per year, so a repository with
        # more than 100 PRs by this user in one year is undercounted. Accepted tradeoff.
        fragments.append(f"""
      pullRequestContributionsByRepository(maxRepositories: 100) {{
        {_REPO_DETAILS_FRAGMENT}
        contributions(first: 100) {{
          nodes {{
            pullRequest {{
              state
            }}
          }}
        }}
      }}""")
    if "issues" in contribution_types:
        fragments.append(f"""
      issueContributionsByRepository(maxRepositories: 100) {{
        {_REPO_DETAILS_FRAGMENT}
        contributions {{ totalCount }}
      }}""")
    if "reviews" in contribution_types:
        fragments.append(f"""
      pullRequestReviewContributionsByRepository(maxRepositories: 100) {{
        {_REPO_DETAILS_FRAGMENT}
        contributions {{ totalCount }}
      }}""")

    joined_fragments = "\n".join(fragments)

    return f"""
query userContribs($login: String!, $from: DateTime!, $to: DateTime!) {{
  user(login: $login) {{
    contributionsCollection(from: $from, to: $to) {{
{joined_fragments}
    }}
  }}
}}
"""


async def _async_fetch_contribution_years(client: GitHubClient, username: str) -> list[int]:
    """Fetch the years in which a user has made contributions asynchronously.

    Args:
        client: Authenticated GitHub API client
        username: GitHub username

    Returns:
        List of contribution years (most recent first, up to 5)

    Raises:
        FetchError: If API request fails or user not found
    """
    try:
        data = await client.async_graphql_query(_CONTRIB_YEARS_QUERY, {"login": username})
        if "errors" in data:
            raise FetchError(f"GraphQL error: {data['errors'][0].get('message')}")

        user_data = data.get("data", {}).get("user")
        if not user_data:
            raise FetchError(f"User '{username}' not found")

        years = user_data["contributionsCollection"]["contributionYears"]
    except APIError as e:
        raise FetchError(f"Failed to fetch contribution years: {e}") from e

    return sorted(years, reverse=True)[:5]


async def _async_process_year_contributions(
    client: GitHubClient,
    username: str,
    year: int,
    raw_repos_map: dict[str, dict[str, Any]],
    lock: asyncio.Lock,
    contribution_types: list[str],
) -> None:
    """Fetch and merge one year's contribution data into *raw_repos_map* asynchronously.

    The map is mutated in-place with lock protection.

    Args:
        client: Authenticated GitHub API client
        username: GitHub username
        year: Calendar year to fetch
        raw_repos_map: Mutable accumulator mapping ``nameWithOwner`` to repo data
        lock: Asyncio lock for raw_repos_map protection
        contribution_types: List of contribution types to fetch
    """
    from_date = f"{year}-01-01T00:00:00Z"
    to_date = f"{year}-12-31T23:59:59Z"

    query = _build_contrib_query(contribution_types)

    try:
        c_data = await client.async_graphql_query(
            query,
            {"login": username, "from": from_date, "to": to_date},
        )

        user_data = c_data.get("data", {}).get("user") if isinstance(c_data, dict) and c_data.get("data") else None
        if not user_data:
            return

        collection = user_data.get("contributionsCollection")
        if not collection:
            return

        all_contrib_types = [
            ("commitContributionsByRepository", "commits"),
            ("pullRequestContributionsByRepository", "prs"),
            ("issueContributionsByRepository", "issues"),
            ("pullRequestReviewContributionsByRepository", "reviews"),
        ]

        # Only process the types that were requested
        active_contrib_types = [
            (gh_key, stats_key) for gh_key, stats_key in all_contrib_types if stats_key in contribution_types
        ]

        for gh_key, stats_key in active_contrib_types:
            for item in collection.get(gh_key, []) or []:
                repo = item.get("repository")
                if not repo:
                    continue

                contribs = item.get("contributions") or {}

                if gh_key == "pullRequestContributionsByRepository":
                    # Filter PRs by state: only OPEN and MERGED are considered contributions
                    nodes = contribs.get("nodes") or []
                    count = sum(
                        1 for node in nodes if (node.get("pullRequest") or {}).get("state") in ["OPEN", "MERGED"]
                    )
                else:
                    count = contribs.get("totalCount", 0)

                if count == 0 or repo.get("isPrivate"):
                    continue

                owner = repo.get("owner") or {}
                if (owner.get("login") or "").lower() == username.lower():
                    continue

                name = repo.get("nameWithOwner")
                if not name:
                    continue

                stargazers = repo.get("stargazers") or {}
                stars = stargazers.get("totalCount", 0)
                avatar_url = owner.get("avatarUrl")

                async with lock:
                    if name not in raw_repos_map:
                        total_repo_commits = 0
                        obj = repo.get("object")
                        if obj and "history" in obj:
                            history = obj.get("history") or {}
                            total_repo_commits = history.get("totalCount", 0)

                        raw_repos_map[name] = {
                            "name": name,
                            "stars": stars,
                            "avatar_url": avatar_url,
                            "commits": 0,
                            "prs": 0,
                            "issues": 0,
                            "reviews": 0,
                            "total_repo_commits": total_repo_commits,
                        }
                    else:
                        if raw_repos_map[name]["total_repo_commits"] == 0:
                            obj = repo.get("object")
                            if obj and "history" in obj:
                                history = obj.get("history") or {}
                                raw_repos_map[name]["total_repo_commits"] = history.get("totalCount", 0)

                    raw_repos_map[name][stats_key] += count

    except APIError:
        # Continue to next year on error
        return


async def _async_build_contributor_repos(
    client: GitHubClient,
    raw_repos_map: dict[str, dict[str, Any]],
    exclude_repo: list[str],
    limit: int,
) -> list[ContributorRepo]:
    """Rank, filter, sort, slice and enrich raw repo data asynchronously.

    Args:
        client: Authenticated GitHub API client (for avatar fetching)
        raw_repos_map: Accumulated raw repo data
        exclude_repo: Repository name patterns to exclude
        limit: Maximum number of repos to return

    Returns:
        Final list of ``ContributorRepo`` dicts ready for rendering
    """
    # Calculate ranks
    repos_data: list[dict[str, Any]] = []
    for repo_data in raw_repos_map.values():
        repo_data["rank_level"] = calculate_repo_rank(repo_data["stars"], repo_data["total_repo_commits"])
        repos_data.append(repo_data)

    # Filter excluded repos
    repos_data = [r for r in repos_data if not is_repo_excluded(r["name"], exclude_repo)]

    # Sort by stars descending and limit
    repos_data.sort(key=lambda r: r["stars"], reverse=True)
    repos_data = repos_data[:limit]

    # Fetch avatars asynchronously
    async def fetch_avatar(repo: dict[str, Any]) -> ContributorRepo:
        avatar_b64 = None
        if repo["avatar_url"]:
            image_data = await client.async_fetch_image(repo["avatar_url"])
            if image_data:
                avatar_b64 = base64.b64encode(image_data).decode("utf-8")

        return {
            "name": repo["name"],
            "stars": repo["stars"],
            "commits": repo["commits"],
            "prs": repo["prs"],
            "issues": repo["issues"],
            "reviews": repo["reviews"],
            "rank_level": repo["rank_level"],
            "avatar_b64": avatar_b64,
        }

    tasks = [fetch_avatar(repo) for repo in repos_data]
    return await asyncio.gather(*tasks)


async def async_fetch_contributor_stats(config: ContribFetchConfig) -> ContributorStats:
    """Async implementation of fetch_contributor_stats."""
    async with GitHubClient(config.token) as client:
        years = await _async_fetch_contribution_years(client, config.username)

        raw_repos_map: dict[str, dict[str, Any]] = {}
        lock = asyncio.Lock()
        tasks = [
            _async_process_year_contributions(
                client, config.username, year, raw_repos_map, lock, config.contribution_types
            )
            for year in years
        ]
        await asyncio.gather(*tasks)

        repos = await _async_build_contributor_repos(client, raw_repos_map, config.exclude_repo, config.limit)

        return {"repos": repos}


def fetch_contributor_stats(config: ContribFetchConfig) -> ContributorStats:
    """
    Fetch contributor statistics (repos contributed to) in parallel.

    Args:
        config: Fetch configuration

    Returns:
        Contributor statistics

    Raises:
        FetchError: If API request fails or if called from within an existing event loop.
    """
    try:
        asyncio.get_running_loop()
        has_loop = True
    except RuntimeError:
        has_loop = False

    if has_loop:
        raise FetchError(
            "An asyncio event loop is already running. Please use `async_fetch_contributor_stats` instead."
        )

    return asyncio.run(async_fetch_contributor_stats(config))

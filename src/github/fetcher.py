"""GitHub API client for fetching user statistics."""

from typing import TypedDict

import requests

from ..core.constants import API_BASE_URL
from ..core.exceptions import FetchError
from .client import GitHubClient


class UserStats(TypedDict):
    """GitHub user statistics."""

    name: str
    login: str
    totalCommits: int
    totalPRs: int
    mergedPRs: int
    totalIssues: int
    totalStars: int
    contributedTo: int
    followers: int
    totalReviews: int
    discussionsStarted: int
    discussionsAnswered: int


def fetch_stats(
    username: str,
    token: str,
    include_all_commits: bool = False,
    commits_year: int | None = None,
    show: list[str] | None = None,
) -> UserStats:
    """
    Fetch GitHub user statistics via GraphQL and REST APIs.

    Args:
        username: GitHub username
        token: GitHub Personal Access Token
        include_all_commits: If True, count all commits (uses REST API)
        commits_year: If specified, filter commits to this year
        show: Optional list of additional stats to fetch

    Returns:
        Dictionary with user statistics

    Raises:
        FetchError: If API request fails
    """
    client = GitHubClient(token)
    show = show or []

    # Build date range for commits_year filter
    from_date = None
    to_date = None
    if commits_year is not None:
        from_date = f"{commits_year}-01-01T00:00:00Z"
        to_date = f"{commits_year}-12-31T23:59:59Z"

    # GraphQL query with optional date range for commits
    variables = {"login": username}
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

    except requests.exceptions.RequestException as e:
        raise FetchError(f"Failed to fetch data from GitHub: {e}")

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
            page_data = client.graphql_query(
                pagination_query, {"login": username, "after": end_cursor}
            )

            page_user = page_data.get("data", {}).get("user")
            if page_user:
                total_stars += sum(
                    repo["stargazers"]["totalCount"] for repo in page_user["repositories"]["nodes"]
                )
                has_next_page = page_user["repositories"]["pageInfo"]["hasNextPage"]
                end_cursor = page_user["repositories"]["pageInfo"]["endCursor"]
            else:
                break

        except requests.exceptions.RequestException:
            # If pagination fails, continue with what we have
            break

    # Get total commits
    total_commits = user["contributionsCollection"]["totalCommitContributions"]

    if include_all_commits:
        # Use REST API to get all-time commit count
        try:
            search_data = client.rest_get(
                f"{API_BASE_URL}/search/commits?q=author:{username}",
                headers={"Accept": "application/vnd.github.cloak-preview+json"},
            )
            total_commits = search_data.get("total_count", total_commits)
        except requests.exceptions.RequestException:
            # If REST API fails, use GraphQL data
            pass

    # Use REST API to get accurate issue count (includes issues in repos user doesn't own)
    total_issues = user["openIssues"]["totalCount"] + user["closedIssues"]["totalCount"]
    try:
        issues_data = client.rest_get(f"{API_BASE_URL}/search/issues?q=author:{username}+type:issue")
        total_issues = issues_data.get("total_count", total_issues)
    except requests.exceptions.RequestException:
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
            discussions_answered = disc_user.get("repositoryDiscussionComments", {}).get(
                "totalCount", 0
            )
        except requests.exceptions.RequestException:
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
        "contributedTo": user["repositoriesContributedTo"]["totalCount"],
        "followers": user["followers"]["totalCount"],
        "totalReviews": user["contributionsCollection"]["totalPullRequestReviewContributions"],
        "discussionsStarted": discussions_started,
        "discussionsAnswered": discussions_answered,
    }
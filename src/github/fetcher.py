"""GitHub API client for fetching user statistics."""

import base64
import requests  # type: ignore
from typing import TypedDict, Any

from ..core.constants import API_BASE_URL
from ..core.config import ContribFetchConfig
from ..core.exceptions import FetchError
from ..core.utils import is_repo_excluded
from .client import GitHubClient
from .rank import calculate_rank


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
        issues_data = client.rest_get(
            f"{API_BASE_URL}/search/issues?q=author:{username}+type:issue"
        )
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


def fetch_contributor_stats(config: ContribFetchConfig) -> ContributorStats:
    """
    Fetch contributor statistics (repos contributed to).

    Args:
        config: Fetch configuration

    Returns:
        Contributor statistics

    Raises:
        FetchError: If API request fails
    """
    client = GitHubClient(config.token)

    # 1. Get total user stats as a baseline for rank
    # We use fetch_stats to get overall activity (commits, prs, issues, reviews, followers)
    try:
        user_total_stats = fetch_stats(config.username, config.token, include_all_commits=True)
    except Exception as e:
        raise FetchError(f"Failed to fetch user baseline stats: {e}")

    # 2. Get contribution years to iterate over
    years_query = """
    query userYears($login: String!) {
      user(login: $login) {
        contributionsCollection {
          contributionYears
        }
      }
    }
    """
    try:
        data = client.graphql_query(years_query, {"login": config.username})
        if "errors" in data:
            raise FetchError(f"GraphQL error: {data['errors'][0].get('message')}")

        user_data = data.get("data", {}).get("user")
        if not user_data:
            raise FetchError(f"User '{config.username}' not found")

        years = user_data["contributionsCollection"]["contributionYears"]
    except requests.exceptions.RequestException as e:
        raise FetchError(f"Failed to fetch contribution years: {e}")

    # 3. Iterate over last 5 years to collect repositories
    # We limit to 5 years to balance performance vs accuracy
    target_years = sorted(years, reverse=True)[:5]

    raw_repos_map: dict[str, dict[str, Any]] = {}

    for year in target_years:
        from_date = f"{year}-01-01T00:00:00Z"
        to_date = f"{year}-12-31T23:59:59Z"

        col_query = """
        query userContribs($login: String!, $from: DateTime!, $to: DateTime!) {
          user(login: $login) {
            contributionsCollection(from: $from, to: $to) {
              commitContributionsByRepository(maxRepositories: 100) {
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
                }
                contributions {
                  totalCount
                }
              }
              pullRequestContributionsByRepository(maxRepositories: 100) {
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
                }
                contributions {
                  totalCount
                }
              }
              issueContributionsByRepository(maxRepositories: 100) {
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
                }
                contributions {
                  totalCount
                }
              }
              pullRequestReviewContributionsByRepository(maxRepositories: 100) {
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
                }
                contributions {
                  totalCount
                }
              }
            }
          }
        }
        """

        try:
            c_data = client.graphql_query(
                col_query, {"login": config.username, "from": from_date, "to": to_date}
            )

            if "errors" in c_data:
                # Log error and continue to next year
                continue

            user_data = c_data.get("data", {}).get("user")
            if not user_data:
                continue

            collection = user_data.get("contributionsCollection")
            if not collection:
                continue

            # Helper to process a contribution list
            def process_list(items: list[dict[str, Any]], contrib_type: str) -> None:
                for item in items:
                    repo = item["repository"]
                    name = repo["nameWithOwner"]
                    count = item["contributions"]["totalCount"]

                    # Filter private
                    if repo["isPrivate"]:
                        continue

                    # Filter user's own repos
                    if repo["owner"]["login"].lower() == config.username.lower():
                        continue

                    # Initialize or update repo data
                    if name not in raw_repos_map:
                        raw_repos_map[name] = {
                            "name": name,
                            "stars": repo["stargazers"]["totalCount"],
                            "avatar_url": repo["owner"]["avatarUrl"],
                            "commits": 0,
                            "prs": 0,
                            "issues": 0,
                            "reviews": 0,
                        }

                    raw_repos_map[name][contrib_type] += count

            process_list(collection["commitContributionsByRepository"], "commits")
            process_list(collection["pullRequestContributionsByRepository"], "prs")
            process_list(collection["issueContributionsByRepository"], "issues")
            process_list(collection["pullRequestReviewContributionsByRepository"], "reviews")

        except requests.exceptions.RequestException:
            # Continue to next year on error
            continue

    # Calculate overall user rank once and reuse for all repositories
    user_rank = calculate_rank(
        commits=user_total_stats["totalCommits"],
        prs=user_total_stats["totalPRs"],
        issues=user_total_stats["totalIssues"],
        reviews=user_total_stats["totalReviews"],
        stars=user_total_stats["totalStars"],
        followers=user_total_stats["followers"],
        all_commits=True,
    )

    # Calculate ranks for all repositories
    final_repos_data: list[dict[str, Any]] = []
    for repo_data in raw_repos_map.values():
        # Use the overall user rank level for each contributed repository
        repo_data["rank_level"] = user_rank["level"]
        final_repos_data.append(repo_data)

    # Filter excluded repos
    final_repos_data = [
        r for r in final_repos_data if not is_repo_excluded(r["name"], config.exclude_repo)
    ]

    # Sort by stars descending (or maybe by rank? the user said "top X ... based on score (stars amount)")
    # We'll keep sorting by stars as per original requirement, but display the rank level.
    final_repos_data.sort(key=lambda r: r["stars"], reverse=True)

    # Limit results
    final_repos_data = final_repos_data[: config.limit]

    # Fetch avatars
    final_repos: list[ContributorRepo] = []
    for repo in final_repos_data:
        avatar_b64 = None
        if repo["avatar_url"]:
            image_data = client.fetch_image(repo["avatar_url"])
            if image_data:
                avatar_b64 = base64.b64encode(image_data).decode("utf-8")

        final_repos.append(
            {
                "name": repo["name"],
                "stars": repo["stars"],
                "commits": repo["commits"],
                "prs": repo["prs"],
                "issues": repo["issues"],
                "reviews": repo["reviews"],
                "rank_level": repo["rank_level"],
                "avatar_b64": avatar_b64,
            }
        )

    return {"repos": final_repos}

"""Rank calculation algorithm for GitHub stats."""

from typing import TypedDict


class RankResult(TypedDict):
    """Result of rank calculation."""

    level: str
    percentile: float


def exponential_cdf(x: float) -> float:
    """
    Calculate the exponential cumulative distribution function.

    Args:
        x: Input value

    Returns:
        CDF value
    """
    return 1 - 2**-x


def log_normal_cdf(x: float) -> float:
    """
    Calculate the log-normal cumulative distribution function (approximation).

    Args:
        x: Input value

    Returns:
        CDF value
    """
    return x / (1 + x)


def calculate_user_rank(
    commits: int,
    prs: int,
    issues: int,
    reviews: int,
    stars: int,
    followers: int,
    all_commits: bool = False,
) -> RankResult:
    """
    Calculate user rank based on GitHub statistics.

    The rank is calculated using a weighted combination of various GitHub statistics,
    normalized using CDF functions to handle different scales of contributions.

    Args:
        commits: Total commit contributions
        prs: Total pull requests
        issues: Total issues (opened + closed)
        reviews: Total pull request reviews
        stars: Total stars earned across all repositories
        followers: Total followers
        all_commits: Whether commits include all-time or just current year

    Returns:
        Dictionary with 'level' (S, A+, A, A-, B+, B, B-, C+, C) and 'percentile'

    Examples:
        >>> result = calculate_user_rank(1000, 100, 50, 10, 200, 50)
        >>> result['level']
        'A+'
        >>> 0 <= result['percentile'] <= 100
        True
    """
    # Median values for normalization
    commits_median = 1000 if all_commits else 250
    commits_weight = 2

    prs_median, prs_weight = 50, 3
    issues_median, issues_weight = 25, 1
    reviews_median, reviews_weight = 2, 1
    stars_median, stars_weight = 50, 4
    followers_median, followers_weight = 10, 1

    total_weight = commits_weight + prs_weight + issues_weight + reviews_weight + stars_weight + followers_weight

    # Calculate normalized rank (0 = best, 1 = worst)
    rank = (
        1
        - (
            commits_weight * exponential_cdf(commits / commits_median)
            + prs_weight * exponential_cdf(prs / prs_median)
            + issues_weight * exponential_cdf(issues / issues_median)
            + reviews_weight * exponential_cdf(reviews / reviews_median)
            + stars_weight * log_normal_cdf(stars / stars_median)
            + followers_weight * log_normal_cdf(followers / followers_median)
        )
        / total_weight
    )

    # Define thresholds and corresponding levels
    thresholds = [1, 12.5, 25, 37.5, 50, 62.5, 75, 87.5, 100]
    levels = ["S", "A+", "A", "A-", "B+", "B", "B-", "C+", "C"]

    # Convert to percentile (0-100)
    percentile = rank * 100

    # Find the appropriate level
    level = "C"  # Default to lowest
    for i, threshold in enumerate(thresholds):
        if percentile <= threshold:
            level = levels[i]
            break

    return {"level": level, "percentile": percentile}


def calculate_repo_rank(stars: int) -> str:
    """
    Calculate rank for a single repository contribution.

    Args:
        stars: Repository star count

    Returns:
        Rank string ("S", "A", "B", "C" or "D")
    """
    if stars > 10000:
        return "S"
    if stars > 1000:
        return "A"
    if stars > 100:
        return "B"
    if stars > 10:
        return "C"
    return "D"

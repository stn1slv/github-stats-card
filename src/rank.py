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


def calculate_rank(
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
        >>> result = calculate_rank(1000, 100, 50, 10, 200, 50)
        >>> result['level']
        'A+'
        >>> 0 <= result['percentile'] <= 100
        True
    """
    # Median values for normalization
    COMMITS_MEDIAN = 1000 if all_commits else 250
    COMMITS_WEIGHT = 2

    PRS_MEDIAN, PRS_WEIGHT = 50, 3
    ISSUES_MEDIAN, ISSUES_WEIGHT = 25, 1
    REVIEWS_MEDIAN, REVIEWS_WEIGHT = 2, 1
    STARS_MEDIAN, STARS_WEIGHT = 50, 4
    FOLLOWERS_MEDIAN, FOLLOWERS_WEIGHT = 10, 1

    TOTAL_WEIGHT = (
        COMMITS_WEIGHT
        + PRS_WEIGHT
        + ISSUES_WEIGHT
        + REVIEWS_WEIGHT
        + STARS_WEIGHT
        + FOLLOWERS_WEIGHT
    )

    # Calculate normalized rank (0 = best, 1 = worst)
    rank = (
        1
        - (
            COMMITS_WEIGHT * exponential_cdf(commits / COMMITS_MEDIAN)
            + PRS_WEIGHT * exponential_cdf(prs / PRS_MEDIAN)
            + ISSUES_WEIGHT * exponential_cdf(issues / ISSUES_MEDIAN)
            + REVIEWS_WEIGHT * exponential_cdf(reviews / REVIEWS_MEDIAN)
            + STARS_WEIGHT * log_normal_cdf(stars / STARS_MEDIAN)
            + FOLLOWERS_WEIGHT * log_normal_cdf(followers / FOLLOWERS_MEDIAN)
        )
        / TOTAL_WEIGHT
    )

    # Define thresholds and corresponding levels
    THRESHOLDS = [1, 12.5, 25, 37.5, 50, 62.5, 75, 87.5, 100]
    LEVELS = ["S", "A+", "A", "A-", "B+", "B", "B-", "C+", "C"]

    # Convert to percentile (0-100)
    percentile = rank * 100

    # Find the appropriate level
    level = "C"  # Default to lowest
    for i, threshold in enumerate(THRESHOLDS):
        if percentile <= threshold:
            level = LEVELS[i]
            break

    return {"level": level, "percentile": percentile}

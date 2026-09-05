"""Tests for rank calculation algorithm."""

import pytest

from src.github.rank import (
    calculate_repo_rank,
    calculate_user_rank,
    exponential_cdf,
    log_normal_cdf,
)


# ---------------------------------------------------------------------------
# CDF helpers
# ---------------------------------------------------------------------------
@pytest.mark.parametrize(("x", "expected"), [(0, 0), (1, 0.5), (2, 0.75)])
def test_exponential_cdf(x, expected):
    assert exponential_cdf(x) == expected


@pytest.mark.parametrize(("x", "expected"), [(0, 0), (1, 0.5), (9, 0.9)])
def test_log_normal_cdf(x, expected):
    assert log_normal_cdf(x) == expected


# ---------------------------------------------------------------------------
# calculate_user_rank
# ---------------------------------------------------------------------------
def test_calculate_user_rank_s_tier():
    result = calculate_user_rank(100000, 10000, 10000, 10000, 100000, 10000)
    assert result["level"] == "S"
    assert result["percentile"] <= 1.0


def test_calculate_user_rank_a_tier():
    result = calculate_user_rank(1000, 100, 50, 20, 100, 50)
    assert result["level"] in ["S", "A+", "A"]


def test_calculate_user_rank_c_tier():
    result = calculate_user_rank(10, 1, 1, 0, 0, 0)
    assert result["level"] in ["C+", "C"]


def test_calculate_user_rank_with_all_commits():
    res1 = calculate_user_rank(1000, 50, 25, 2, 50, 10, all_commits=False)
    res2 = calculate_user_rank(1000, 50, 25, 2, 50, 10, all_commits=True)
    assert res2["percentile"] > res1["percentile"]


def test_user_rank_percentile_range():
    res_best = calculate_user_rank(1000000, 100000, 100000, 10000, 100000, 100000)
    res_worst = calculate_user_rank(0, 0, 0, 0, 0, 0)
    assert 0 <= res_best["percentile"] <= 100
    assert 0 <= res_worst["percentile"] <= 100
    assert res_best["percentile"] < res_worst["percentile"]


# ---------------------------------------------------------------------------
# calculate_repo_rank
# ---------------------------------------------------------------------------
@pytest.mark.parametrize(
    ("stars", "expected"),
    [
        (10001, "S"),
        (10000, "A"),  # Boundary: 10000 stars -> A tier
        (1001, "A"),
        (1000, "B"),  # Boundary: 1000 stars -> B tier
        (101, "B"),
        (100, "C"),  # Boundary: 100 stars -> C tier
        (11, "C"),
        (10, "D"),  # Boundary: 10 stars -> D tier
        (0, "D"),
    ],
)
def test_calculate_repo_rank(stars: int, expected: str):
    assert calculate_repo_rank(stars) == expected

"""Tests for rank calculation algorithm."""

from src.github.rank import calculate_rank, exponential_cdf, log_normal_cdf


def test_exponential_cdf():
    assert exponential_cdf(0) == 0
    assert exponential_cdf(1) == 0.5
    assert exponential_cdf(2) == 0.75


def test_log_normal_cdf():
    assert log_normal_cdf(0) == 0
    assert log_normal_cdf(1) == 0.5
    assert log_normal_cdf(9) == 0.9


def test_calculate_rank_s_tier():
    # Extremely high stats to ensure S tier (percentile <= 1.0)
    # Using 100k for most stats to ensure CDF approaches 1.0
    result = calculate_rank(100000, 10000, 10000, 10000, 100000, 10000)
    assert result["level"] == "S"
    assert result["percentile"] <= 1.0


def test_calculate_rank_a_tier():
    # Good stats
    result = calculate_rank(1000, 100, 50, 20, 100, 50)
    assert result["level"] in ["S", "A+", "A"]


def test_calculate_rank_c_tier():
    # Low stats
    result = calculate_rank(10, 1, 1, 0, 0, 0)
    assert result["level"] in ["C+", "C"]


def test_calculate_rank_with_all_commits():
    # Same stats, but one is all-time commits (median is higher)
    res1 = calculate_rank(1000, 50, 25, 2, 50, 10, all_commits=False)
    res2 = calculate_rank(1000, 50, 25, 2, 50, 10, all_commits=True)

    # res2 should have a higher (worse) percentile because 1000 commits
    # is less impressive when compared to all-time median (1000)
    # than when compared to current year median (250)
    assert res2["percentile"] > res1["percentile"]


def test_rank_percentile_range():
    # Test extreme cases
    res_best = calculate_rank(1000000, 100000, 100000, 10000, 100000, 100000)
    res_worst = calculate_rank(0, 0, 0, 0, 0, 0)

    assert 0 <= res_best["percentile"] <= 100
    assert 0 <= res_worst["percentile"] <= 100
    assert res_best["percentile"] < res_worst["percentile"]

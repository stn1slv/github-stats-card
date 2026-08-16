"""Tests for utility functions."""

import pytest

from src.core.utils import clamp_value, encode_html, is_repo_excluded, k_formatter, parse_list_arg


# ---------------------------------------------------------------------------
# k_formatter
# ---------------------------------------------------------------------------
@pytest.mark.parametrize(
    ("value", "kwargs", "expected"),
    [
        (500, {}, "500"),
        (999, {}, "999"),
        (1000, {}, "1k"),
        (1500, {}, "1.5k"),
        (6626, {}, "6.6k"),
        (10000, {}, "10k"),
        (-1500, {}, "-1.5k"),
        (6626, {"precision": 0}, "7k"),
        (6626, {"precision": 1}, "6.6k"),
        (6626, {"precision": 2}, "6.63k"),
    ],
)
def test_k_formatter(value: int, kwargs: dict, expected: str):
    assert k_formatter(value, **kwargs) == expected


# ---------------------------------------------------------------------------
# clamp_value
# ---------------------------------------------------------------------------
@pytest.mark.parametrize(
    ("value", "lo", "hi", "expected"),
    [
        (5, 0, 10, 5),
        (-5, 0, 10, 0),
        (15, 0, 10, 10),
        (7.5, 0, 10, 7.5),
    ],
)
def test_clamp_value(value, lo, hi, expected):
    assert clamp_value(value, lo, hi) == expected


# ---------------------------------------------------------------------------
# encode_html
# ---------------------------------------------------------------------------
@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("Hello World", "Hello World"),
        ("<script>", "&lt;script&gt;"),
        ("A & B", "A &amp; B"),
        ('"quoted"', "&quot;quoted&quot;"),
        ("'single'", "&#39;single&#39;"),
    ],
)
def test_encode_html(text: str, expected: str):
    assert encode_html(text) == expected


# ---------------------------------------------------------------------------
# parse_list_arg
# ---------------------------------------------------------------------------
@pytest.mark.parametrize(
    ("arg", "expected"),
    [
        (None, []),
        ("", []),
        ("foo", ["foo"]),
        ("foo,bar", ["foo", "bar"]),
        (" foo , bar ", ["foo", "bar"]),
        (["foo", "bar"], ["foo", "bar"]),
        ([" foo ", " bar "], ["foo", "bar"]),
    ],
)
def test_parse_list_arg(arg, expected):
    assert parse_list_arg(arg) == expected


# ---------------------------------------------------------------------------
# is_repo_excluded
# ---------------------------------------------------------------------------
@pytest.mark.parametrize(
    ("repo", "patterns", "expected"),
    [
        # Exact match (full name)
        ("owner/repo", ["owner/repo"], True),
        ("owner/repo", ["other/repo"], False),
        # Exact match (repo name only pattern)
        ("stn1slv/awesome-cli-apps", ["awesome-cli-apps"], True),
        ("octocat/awesome-cli-apps", ["awesome-cli-apps"], True),
        ("awesome-cli-apps", ["awesome-cli-apps"], True),
        # Wildcard match (full name pattern)
        ("owner/repo-abc", ["owner/repo-*"], True),
        ("other/repo-abc", ["owner/repo-*"], False),
        # Wildcard match (repo name only pattern)
        ("stn1slv/awesome-speakers", ["awesome-*"], True),
        ("octocat/awesome-newsletters", ["awesome-*"], True),
        ("other-apps", ["awesome-*"], False),
        # Case insensitive matching
        ("AWESOME-apps", ["awesome-*"], True),
        ("awesome-apps", ["AWESOME-*"], True),
        # Multiple patterns
        ("stn1slv/test-repo", ["awesome-*", "test-*"], True),
        # Empty patterns
        ("repo", [], False),
    ],
)
def test_is_repo_excluded(repo: str, patterns: list[str], expected: bool):
    assert is_repo_excluded(repo, patterns) is expected


@pytest.mark.parametrize(
    ("value", "precision", "expected"),
    [
        # A precision must not force the k suffix on a value below the divisor
        (5, 1, "5"),
        (0, 2, "0"),
        (999, 0, "999"),
        (-42, 1, "-42"),
        # At or above the divisor the precision still applies
        (1000, 0, "1k"),
        (6626, 1, "6.6k"),
    ],
)
def test_k_formatter_precision_respects_magnitude(value: int, precision: int, expected: str):
    assert k_formatter(value, precision=precision) == expected

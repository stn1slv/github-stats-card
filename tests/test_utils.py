"""Tests for utility functions."""

from src.core.utils import k_formatter, clamp_value, encode_html, parse_list_arg


def test_k_formatter_less_than_thousand():
    assert k_formatter(500) == "500"
    assert k_formatter(999) == "999"


def test_k_formatter_thousands():
    assert k_formatter(1000) == "1k"
    assert k_formatter(1500) == "1.5k"
    assert k_formatter(6626) == "6.6k"
    assert k_formatter(10000) == "10k"


def test_k_formatter_with_precision():
    assert k_formatter(6626, precision=0) == "7k"
    assert k_formatter(6626, precision=1) == "6.6k"
    assert k_formatter(6626, precision=2) == "6.63k"


def test_k_formatter_negative():
    assert k_formatter(-1500) == "-1.5k"


def test_clamp_value():
    assert clamp_value(5, 0, 10) == 5
    assert clamp_value(-5, 0, 10) == 0
    assert clamp_value(15, 0, 10) == 10
    assert clamp_value(7.5, 0, 10) == 7.5


def test_encode_html():
    assert encode_html("Hello World") == "Hello World"
    assert encode_html("<script>") == "&lt;script&gt;"
    assert encode_html("A & B") == "A &amp; B"
    assert encode_html('"quoted"') == "&quot;quoted&quot;"
    assert encode_html("'single'") == "&#39;single&#39;"


def test_parse_list_arg():
    assert parse_list_arg(None) == []
    assert parse_list_arg("") == []
    assert parse_list_arg("foo") == ["foo"]
    assert parse_list_arg("foo,bar") == ["foo", "bar"]
    assert parse_list_arg(" foo , bar ") == ["foo", "bar"]
    assert parse_list_arg(["foo", "bar"]) == ["foo", "bar"]
    assert parse_list_arg([" foo ", " bar "]) == ["foo", "bar"]


def test_is_repo_excluded():
    from src.core.utils import is_repo_excluded

    # Exact match (full name)
    assert is_repo_excluded("owner/repo", ["owner/repo"]) is True
    assert is_repo_excluded("owner/repo", ["other/repo"]) is False

    # Exact match (repo name only pattern)
    assert is_repo_excluded("stn1slv/awesome-cli-apps", ["awesome-cli-apps"]) is True
    assert is_repo_excluded("octocat/awesome-cli-apps", ["awesome-cli-apps"]) is True
    assert is_repo_excluded("awesome-cli-apps", ["awesome-cli-apps"]) is True

    # Wildcard match (full name pattern)
    assert is_repo_excluded("owner/repo-abc", ["owner/repo-*"]) is True
    assert is_repo_excluded("other/repo-abc", ["owner/repo-*"]) is False

    # Wildcard match (repo name only pattern)
    assert is_repo_excluded("stn1slv/awesome-speakers", ["awesome-*"]) is True
    assert is_repo_excluded("octocat/awesome-newsletters", ["awesome-*"]) is True
    assert is_repo_excluded("other-apps", ["awesome-*"]) is False

    # Case insensitive matching (enforced by lowercasing)
    assert is_repo_excluded("AWESOME-apps", ["awesome-*"]) is True
    assert is_repo_excluded("awesome-apps", ["AWESOME-*"]) is True

    # Multiple patterns
    assert is_repo_excluded("stn1slv/test-repo", ["awesome-*", "test-*"]) is True

    # Empty patterns
    assert is_repo_excluded("repo", []) is False

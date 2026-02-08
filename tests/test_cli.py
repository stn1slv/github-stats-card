"""Integration tests for CLI commands."""

from unittest.mock import patch
from click.testing import CliRunner
from src.cli import cli


def test_stats_command():
    runner = CliRunner()
    with (
        patch("src.cli.fetch_stats") as mock_fetch,
        patch("src.cli.render_stats_card") as mock_render,
    ):

        mock_fetch.return_value = {
            "name": "User",
            "login": "user",
            "totalStars": 100,
            "totalCommits": 50,
            "totalPRs": 10,
            "mergedPRs": 5,
            "totalIssues": 20,
            "contributedTo": 5,
            "followers": 10,
            "totalReviews": 2,
            "discussionsStarted": 0,
            "discussionsAnswered": 0,
        }
        mock_render.return_value = "<svg>stats</svg>"

        result = runner.invoke(
            cli, ["stats", "-u", "user", "-t", "token", "-o", "stats.svg"]
        )

        assert result.exit_code == 0
        assert "Generated" in result.stderr


def test_top_langs_command():
    runner = CliRunner()
    with (
        patch("src.cli.fetch_top_languages") as mock_fetch,
        patch("src.cli.render_top_languages") as mock_render,
    ):

        mock_fetch.return_value = [{"name": "Python", "color": "#3572A5", "size": 100}]
        mock_render.return_value = "<svg>langs</svg>"

        result = runner.invoke(
            cli, ["top-langs", "-u", "user", "-t", "token", "-o", "langs.svg"]
        )

        assert result.exit_code == 0
        assert "Generated" in result.stderr


def test_contrib_command():
    runner = CliRunner()
    with (
        patch("src.cli.fetch_contributor_stats") as mock_fetch,
        patch("src.cli.render_contrib_card") as mock_render,
    ):

        mock_fetch.return_value = {
            "repos": [{"name": "owner/repo", "stars": 100, "avatar_b64": "base64"}]
        }
        mock_render.return_value = "<svg>contrib</svg>"

        result = runner.invoke(
            cli, ["contrib", "-u", "user", "-t", "token", "-o", "contrib.svg"]
        )

        assert result.exit_code == 0
        assert "Generated" in result.stderr

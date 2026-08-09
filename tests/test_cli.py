"""Integration tests for CLI commands."""

import re
from pathlib import Path
from unittest.mock import patch

from click.testing import CliRunner

from src.cli import cli
from src.core.exceptions import FetchError

ACTION_YML = Path(__file__).resolve().parents[1] / "action.yml"


def test_user_stats_command():
    runner = CliRunner()
    with (
        patch("src.cli.fetch_user_stats") as mock_fetch,
        patch("src.cli.render_user_stats_card") as mock_render,
    ):
        mock_fetch.return_value = {
            "name": "User",
            "login": "user",
            "totalStars": 100,
            "totalCommits": 50,
            "totalPRs": 10,
            "mergedPRs": 5,
            "totalIssues": 20,
            "totalRepos": 30,
            "contributedTo": 5,
            "followers": 10,
            "totalReviews": 2,
            "discussionsStarted": 0,
            "discussionsAnswered": 0,
        }
        mock_render.return_value = "<svg>stats</svg>"

        result = runner.invoke(cli, ["user-stats", "-u", "user", "-t", "token", "-o", "stats.svg"])

        assert result.exit_code == 0
        assert "Generated" in result.stderr


def test_user_stats_command_github_token_scope_hint():
    """A restricted GitHub Actions token surfaces an actionable PAT hint, not just a raw error."""
    runner = CliRunner()
    with patch("src.cli.fetch_user_stats") as mock_fetch:
        mock_fetch.side_effect = FetchError(
            "Failed to fetch data from GitHub: GraphQL error: Resource not accessible by integration"
        )

        result = runner.invoke(cli, ["user-stats", "-u", "user", "-t", "ghs_dummy", "-o", "stats.svg"])

        assert result.exit_code == 1
        assert "❌ Error fetching data" in result.stderr
        assert "read:user" in result.stderr


def test_stats_alias_command():
    """Test that 'stats' still works as a backward-compatible alias for 'user-stats'."""
    runner = CliRunner()
    with (
        patch("src.cli.fetch_user_stats") as mock_fetch,
        patch("src.cli.render_user_stats_card") as mock_render,
    ):
        mock_fetch.return_value = {
            "name": "User",
            "login": "user",
            "totalStars": 100,
            "totalCommits": 50,
            "totalPRs": 10,
            "mergedPRs": 5,
            "totalIssues": 20,
            "totalRepos": 30,
            "contributedTo": 5,
            "followers": 10,
            "totalReviews": 2,
            "discussionsStarted": 0,
            "discussionsAnswered": 0,
        }
        mock_render.return_value = "<svg>stats</svg>"

        result = runner.invoke(cli, ["stats", "-u", "user", "-t", "token", "-o", "stats.svg"])

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

        result = runner.invoke(cli, ["top-langs", "-u", "user", "-t", "token", "-o", "langs.svg"])

        assert result.exit_code == 0
        assert "Generated" in result.stderr


def test_contrib_command():
    runner = CliRunner()
    with (
        patch("src.cli.fetch_contributor_stats") as mock_fetch,
        patch("src.cli.render_contrib_card") as mock_render,
    ):
        mock_fetch.return_value = {"repos": [{"name": "owner/repo", "stars": 100, "avatar_b64": "base64"}]}
        mock_render.return_value = "<svg>contrib</svg>"

        result = runner.invoke(cli, ["contrib", "-u", "user", "-t", "token", "-o", "contrib.svg"])

        assert result.exit_code == 0
        assert "Generated" in result.stderr

        # SC-003: omitting --types falls back to the documented default
        fetch_config = mock_fetch.call_args[0][0]
        assert fetch_config.contribution_types == ["commits", "prs"]


def test_contrib_command_with_valid_types():
    runner = CliRunner()
    with (
        patch("src.cli.fetch_contributor_stats") as mock_fetch,
        patch("src.cli.render_contrib_card") as mock_render,
    ):
        mock_fetch.return_value = {"repos": [{"name": "owner/repo", "stars": 100, "avatar_b64": "base64"}]}
        mock_render.return_value = "<svg>contrib</svg>"

        result = runner.invoke(
            cli, ["contrib", "-u", "user", "-t", "token", "-o", "contrib.svg", "--types", "commits,prs"]
        )

        assert result.exit_code == 0
        assert "Generated" in result.stderr

        # Verify fetch config was created with correctly parsed types
        fetch_config = mock_fetch.call_args[0][0]
        assert fetch_config.contribution_types == ["commits", "prs"]


def test_contrib_command_with_contrib_types_alias():
    """The --contrib-types alias is the spelling action.yml forwards, so it must stay valid."""
    runner = CliRunner()
    with (
        patch("src.cli.fetch_contributor_stats") as mock_fetch,
        patch("src.cli.render_contrib_card") as mock_render,
    ):
        mock_fetch.return_value = {"repos": [{"name": "owner/repo", "stars": 100, "avatar_b64": "base64"}]}
        mock_render.return_value = "<svg>contrib</svg>"

        result = runner.invoke(
            cli, ["contrib", "-u", "user", "-t", "token", "-o", "contrib.svg", "--contrib-types", "issues,reviews"]
        )

        assert result.exit_code == 0

        fetch_config = mock_fetch.call_args[0][0]
        assert fetch_config.contribution_types == ["issues", "reviews"]


def test_contrib_command_types_default_is_documented_in_help():
    """FR-008: the default set must be discoverable from --help alone."""
    runner = CliRunner()
    result = runner.invoke(cli, ["contrib", "--help"])

    assert result.exit_code == 0
    # Collapse whitespace: Click wraps help text, so the default may straddle two lines
    assert "default: commits,prs" in " ".join(result.output.split())


def test_action_yml_forwards_a_flag_the_contrib_command_accepts():
    """SC-002/SC-008: the automation wiring must not drift from the CLI it drives."""
    action = ACTION_YML.read_text()

    # The input is declared with the documented default
    assert "contrib-types:" in action
    assert "default: 'commits,prs'" in action

    # Whatever spelling action.yml forwards must be a real option on the contrib command
    contrib_opts = {opt for param in cli.commands["contrib"].params for opt in param.opts}
    assert "--contrib-types" in action
    assert "--contrib-types" in contrib_opts

    # The value travels via env and is passed as an array element, never through a
    # string that a shell re-parses, so a quote in it is data rather than syntax.
    assert "CONTRIB_TYPES: ${{ inputs.contrib-types }}" in action
    assert 'ARGS+=(--contrib-types "$CONTRIB_TYPES")' in action

    # No `eval` in executable lines: re-parsing a built string is what made input
    # interpolation exploitable. Comments may still mention it, and words like
    # "evaluate" must not trip the check, so match eval as a whole word.
    executable = [ln for ln in action.splitlines() if not ln.strip().startswith("#")]
    assert not [ln for ln in executable if re.search(r"\beval\b", ln)]


def test_contrib_command_with_invalid_types():
    runner = CliRunner()
    result = runner.invoke(
        cli, ["contrib", "-u", "user", "-t", "token", "-o", "contrib.svg", "--types", "commits,invalid"]
    )

    assert result.exit_code != 0
    assert "Invalid contribution type 'invalid'" in result.stderr


def test_contrib_command_with_empty_types():
    runner = CliRunner()
    result = runner.invoke(cli, ["contrib", "-u", "user", "-t", "token", "-o", "contrib.svg", "--types", ""])

    assert result.exit_code != 0
    assert "At least one contribution type is required" in result.stderr

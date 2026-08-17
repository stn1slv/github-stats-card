"""Integration tests for CLI commands."""

import io
import logging
import re
from pathlib import Path
from unittest.mock import patch

import pytest
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


def test_action_yml_installs_from_the_action_path_and_never_self_checks_out():
    """A consumer pinning @v1.2.3 must run that tag's code.

    Two self-checkout attempts have failed in production:

    * No `ref` at all, which silently took the default branch, so a pinned tag
      ran whatever was on main.
    * `${{ github.action_repository }}` / `${{ github.action_ref }}`, which
      inside a composite action resolve to the *innermost* action. v1.2.0
      checked out `actions/checkout@v4` into the install directory and produced
      no card at all, with no error.

    GITHUB_ACTION_PATH is what the runner already resolved from the caller's
    pin, so it cannot drift from it. This test forbids the checkout coming back.
    """
    action = ACTION_YML.read_text()

    # The action must install from the path the runner resolved
    assert 'uv pip install --system -e "$GITHUB_ACTION_PATH"' in action

    # And must not check out its own repository under any spelling
    executable = [ln for ln in action.splitlines() if not ln.strip().startswith("#")]
    body = "\n".join(executable)
    assert "github.action_repository" not in body
    assert "github.action_ref" not in body
    assert "Checkout action repository" not in body
    assert ".github-stats-card-action" not in body


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


def test_user_stats_rejects_all_commits_combined_with_a_year():
    """--include-all-commits would overwrite the year-filtered count, discarding --commits-year."""
    runner = CliRunner()
    result = runner.invoke(
        cli,
        ["user-stats", "-u", "user", "-t", "token", "-o", "s.svg", "--include-all-commits", "--commits-year", "2023"],
    )

    assert result.exit_code != 0
    assert "cannot be combined" in result.stderr


def test_user_stats_rejects_out_of_range_number_precision():
    """Documented as 0-2; an out-of-range value used to be ignored in silence."""
    runner = CliRunner()
    result = runner.invoke(cli, ["user-stats", "-u", "user", "-t", "token", "-o", "s.svg", "--number-precision", "5"])

    assert result.exit_code != 0
    assert "--number-precision" in result.stderr


def test_contrib_rejects_a_non_positive_limit():
    """--limit feeds a list slice, so 0 empties the card and -1 drops the last repository."""
    runner = CliRunner()
    result = runner.invoke(cli, ["contrib", "-u", "user", "-t", "token", "-o", "c.svg", "--limit", "0"])

    assert result.exit_code != 0
    assert "--limit" in result.stderr


def test_top_langs_rejects_an_out_of_range_weight():
    """The weight is an exponent, so a large value overflows during scoring."""
    runner = CliRunner()
    result = runner.invoke(cli, ["top-langs", "-u", "user", "-t", "token", "-o", "l.svg", "--size-weight", "100"])

    assert result.exit_code != 0
    assert "--size-weight" in result.stderr


def test_debug_flag_reraises_instead_of_collapsing_to_one_line():
    """Without --debug a genuine bug is indistinguishable from a network problem."""
    runner = CliRunner()
    with patch("src.cli.fetch_user_stats") as mock_fetch:
        mock_fetch.side_effect = KeyError("totalStars")

        plain = runner.invoke(cli, ["user-stats", "-u", "user", "-t", "token", "-o", "s.svg"])
        assert plain.exit_code == 1
        assert "Unexpected error" in plain.stderr

        debugged = runner.invoke(cli, ["user-stats", "-u", "user", "-t", "token", "-o", "s.svg", "--debug"])
        assert isinstance(debugged.exception, KeyError)


def test_user_stats_rejects_an_unsupported_locale():
    """Only locales with translations may be accepted; unknown ones used to fall back in silence."""
    runner = CliRunner()
    result = runner.invoke(cli, ["user-stats", "-u", "user", "-t", "token", "-o", "s.svg", "--locale", "fr"])

    assert result.exit_code != 0
    assert "--locale" in result.stderr


@pytest.fixture
def restore_logging():
    """Snapshot and restore global logging state.

    _configure_logging mutates a package logger that outlives the test, and the
    root-logger test below mutates the root. Without this the next
    logging-sensitive test inherits a level and a handler bound to a torn-down
    capsys stream.
    """
    root = logging.getLogger()
    package = logging.getLogger("src")
    saved = [(lg, lg.level, list(lg.handlers), lg.propagate) for lg in (root, package)]
    try:
        yield
    finally:
        for lg, level, handlers, propagate in saved:
            lg.setLevel(level)
            lg.handlers[:] = handlers
            lg.propagate = propagate


def test_configure_logging_makes_the_fetch_warning_cause_visible_on_stderr(capsys, restore_logging):
    """A warning that names no cause is as useless as the silent fallback it replaced."""
    from src.cli import _configure_logging

    _configure_logging(debug=False)
    logging.getLogger("src.github.fetcher").warning(
        "Issue search failed, falling back to the owned-repository issue count: %s",
        "429 Too Many Requests",
        extra={"username": "octocat"},
    )

    stderr = capsys.readouterr().err
    assert "Issue search failed" in stderr
    assert "429 Too Many Requests" in stderr


def test_configure_logging_is_idempotent_and_survives_a_configured_root(capsys, restore_logging):
    """A host with its own root handler must not silence us or double our output.

    `logging.basicConfig` cannot set this scenario up: pytest's logging plugin
    has already attached a root handler, so basicConfig returns early and the
    previous version of this test simulated nothing at all.
    """
    from src.cli import _configure_logging

    root = logging.getLogger()
    host_stream = io.StringIO()
    host_handler = logging.StreamHandler(host_stream)
    root.addHandler(host_handler)
    root.setLevel(logging.DEBUG)

    _configure_logging(debug=False)
    _configure_logging(debug=True)

    logging.getLogger("src.github.fetcher").debug("debug diagnostic")

    stderr = capsys.readouterr().err
    # --debug took effect despite the pre-configured root...
    assert stderr.count("debug diagnostic") == 1, "expected exactly one line on stderr"
    # ...and the host's root handler did not also receive it, so no duplication
    assert host_stream.getvalue() == ""


def test_configure_logging_keeps_a_level_the_host_chose(restore_logging):
    """An embedding host that asked for DEBUG must not be reset to WARNING."""
    from src.cli import _PACKAGE_LOGGER_NAME, _configure_logging

    logging.getLogger(_PACKAGE_LOGGER_NAME).setLevel(logging.DEBUG)
    _configure_logging(debug=False)

    assert logging.getLogger(_PACKAGE_LOGGER_NAME).level == logging.DEBUG


def test_configure_logging_preserves_a_handler_the_host_attached(restore_logging):
    """Only this module's own handler may be replaced on repeated invocations."""
    from src.cli import _OWN_HANDLER_FLAG, _PACKAGE_LOGGER_NAME, _configure_logging

    package_logger = logging.getLogger(_PACKAGE_LOGGER_NAME)
    host_handler = logging.StreamHandler(io.StringIO())
    package_logger.addHandler(host_handler)

    _configure_logging(debug=False)
    _configure_logging(debug=False)

    assert host_handler in package_logger.handlers
    # Ours is present exactly once, not stacked. Counted by the sentinel rather
    # than "everything that is not the host handler", because pytest's caplog
    # attaches its own capture handlers to this same logger.
    ours = [h for h in package_logger.handlers if getattr(h, _OWN_HANDLER_FLAG, False)]
    assert len(ours) == 1


def test_action_yml_declares_every_input_the_readme_advertises():
    """A README-only input reaches consumers as 'Unexpected input(s)'."""
    action = ACTION_YML.read_text()
    readme = (ACTION_YML.parent / "README.md").read_text()

    section = readme.split("### Card-Specific Inputs")[1].split("---")[0]
    # Only the top-level card bullets name inputs. Indented sub-bullets list
    # allowed *values* of an input, and so do parenthesised groups, so both are
    # dropped before extracting names.
    advertised: set[str] = set()
    for line in section.splitlines():
        if not line.startswith("- **"):
            continue
        without_values = re.sub(r"\([^)]*\)", "", line)
        advertised |= set(re.findall(r"`([a-z][a-z0-9-]*)`", without_values))

    declared = set(re.findall(r"^  ([a-z][a-z0-9-]+):$", action, re.MULTILINE))

    assert advertised, "no inputs parsed from the README; the section format changed"
    missing = advertised - declared
    assert not missing, f"README advertises action inputs that action.yml does not declare: {sorted(missing)}"


def test_action_yml_forwards_rank_icon():
    """--rank-icon is implemented in the CLI; the action must be able to reach it."""
    action = ACTION_YML.read_text()

    assert "rank-icon:" in action
    assert "RANK_ICON: ${{ inputs.rank-icon }}" in action
    assert 'ARGS+=(--rank-icon "$RANK_ICON")' in action
    assert "--rank-icon" in {opt for param in cli.commands["user-stats"].params for opt in param.opts}


def test_user_stats_rejects_a_card_width_below_the_minimum():
    """0 used to be read as 'unset' and silently replaced by the default."""
    runner = CliRunner()
    result = runner.invoke(cli, ["user-stats", "-u", "u", "-t", "t", "-o", "s.svg", "--card-width", "0"])

    assert result.exit_code != 0
    assert "--card-width" in result.stderr


def test_package_logger_name_survives_being_run_as_a_module():
    """Under `python -m src.cli` this module's __name__ is "__main__".

    Deriving the logger name from __name__ would attach the handler to a logger
    no fetcher ever writes to, silently disabling both the warnings and --debug.
    """
    import src.cli as cli_module
    from src.github import fetcher

    # The name must come from the package, not the module
    expected = cli_module.__package__.split(".", 1)[0]
    assert expected == cli_module._PACKAGE_LOGGER_NAME
    assert cli_module._PACKAGE_LOGGER_NAME != "__main__"

    # And it must actually be an ancestor of the loggers the fetchers use
    assert fetcher.logger.name.startswith(f"{cli_module._PACKAGE_LOGGER_NAME}.")

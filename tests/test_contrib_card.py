"""Tests for contributor card configuration."""

import pytest
from src.core.config import ContribCardConfig, ContribFetchConfig


class TestContribCardConfig:
    def test_default_values(self):
        """Test default values for ContribCardConfig."""
        config = ContribCardConfig()
        assert config.limit == 10
        assert config.exclude_repo == []
        assert config.theme == "default"
        assert config.card_width == 467
        assert config.border_radius == 4.5
        assert config.disable_animations is False
        assert config.hide_border is False
        assert config.custom_title is None

    def test_cli_args_parsing(self):
        """Test creating config from CLI arguments."""
        config = ContribCardConfig.from_cli_args(
            limit=5,
            exclude_repo="owner/repo1,owner/repo2",
            theme="dark",
            hide_border=True,
            card_width=500,
        )
        assert config.limit == 5
        assert config.exclude_repo == ["owner/repo1", "owner/repo2"]
        assert config.theme == "dark"
        assert config.hide_border is True
        assert config.card_width == 500

    def test_none_values_ignored(self):
        """Test that None values in CLI args are ignored."""
        config = ContribCardConfig.from_cli_args(limit=None, theme="dark")
        assert config.limit == 10  # Default value
        assert config.theme == "dark"


class TestContribFetchConfig:
    def test_required_fields(self):
        """Test required fields for ContribFetchConfig."""
        with pytest.raises(TypeError):
            ContribFetchConfig()  # Missing username and token

    def test_initialization(self):
        """Test initializing ContribFetchConfig."""
        config = ContribFetchConfig(
            username="testuser", token="testtoken", limit=20, exclude_repo=["repo1"]
        )
        assert config.username == "testuser"
        assert config.token == "testtoken"
        assert config.limit == 20
        assert config.exclude_repo == ["repo1"]

    def test_cli_args_parsing(self):
        """Test creating fetch config from CLI arguments."""
        config = ContribFetchConfig.from_cli_args(
            username="testuser", token="testtoken", limit=5, exclude_repo="repo1,repo2"
        )
        assert config.username == "testuser"
        assert config.token == "testtoken"
        assert config.limit == 5
        assert config.exclude_repo == ["repo1", "repo2"]

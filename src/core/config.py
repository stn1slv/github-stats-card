"""Configuration dataclasses for GitHub Stats Card rendering."""

from dataclasses import dataclass, field
from typing import Any

from .utils import parse_list_arg


@dataclass
class BaseConfig:
    """Base configuration class with CLI argument parsing."""

    @classmethod
    def from_cli_args(cls, **kwargs: Any) -> Any:
        """
        Create configuration from CLI arguments.

        Filters out None values and creates a config instance.
        Automatically handles list parsing for common list fields.

        Args:
            **kwargs: CLI argument values

        Returns:
            Config instance
        """
        # Filter out None values and keys not in dataclass
        valid_fields = {f.name for f in cls.__dataclass_fields__.values()}
        filtered = {k: v for k, v in kwargs.items() if k in valid_fields and v is not None}

        # Handle known list fields
        for list_key in ["hide", "show", "exclude_repo"]:
            if list_key in filtered:
                filtered[list_key] = parse_list_arg(filtered[list_key])

        return cls(**filtered)


@dataclass
class StatsCardConfig(BaseConfig):
    """Configuration for stats card rendering."""

    # Theme and colors
    theme: str = "default"
    title_color: str | None = None
    text_color: str | None = None
    icon_color: str | None = None
    bg_color: str | None = None
    border_color: str | None = None
    ring_color: str | None = None

    # Visibility options
    hide: list[str] = field(default_factory=list)
    show: list[str] = field(default_factory=list)
    hide_title: bool = False
    hide_border: bool = False
    hide_rank: bool = False
    show_icons: bool = False

    # Layout options
    card_width: int | None = None
    line_height: int = 25
    border_radius: float = 4.5

    # Text options
    custom_title: str | None = None
    locale: str = "en"
    text_bold: bool = True

    # Number formatting
    number_format: str = "short"  # "short" or "long"
    number_precision: int | None = None

    # Animation options
    disable_animations: bool = False
    rank_icon: str = "default"  # "default", "github", "percentile"

    # Commit filtering
    include_all_commits: bool = False


@dataclass
class LangsCardConfig(BaseConfig):
    """Configuration for top languages card rendering."""

    # Theme and colors
    theme: str = "default"
    title_color: str | None = None
    text_color: str | None = None
    bg_color: str | None = None
    border_color: str | None = None

    # Visibility options
    hide: list[str] = field(default_factory=list)
    hide_title: bool = False
    hide_border: bool = False
    hide_progress: bool = False

    # Layout options
    layout: str = "normal"  # "normal", "compact", "donut", "donut-vertical", "pie"
    card_width: int | None = None
    border_radius: float = 4.5

    # Language options
    langs_count: int | None = None
    exclude_repo: list[str] = field(default_factory=list)

    # Weighting options
    size_weight: float = 1.0
    count_weight: float = 0.0

    # Display options
    custom_title: str | None = None
    stats_format: str = "percentages"  # "percentages" or "bytes"

    # Animation options
    disable_animations: bool = False


@dataclass
class FetchConfig(BaseConfig):
    """Configuration for fetching GitHub data."""

    username: str
    token: str
    include_all_commits: bool = False
    commits_year: int | None = None
    show: list[str] = field(default_factory=list)


@dataclass
class LangsFetchConfig(BaseConfig):
    """Configuration for fetching language data."""

    username: str
    token: str
    exclude_repo: list[str] = field(default_factory=list)
    size_weight: float = 1.0
    count_weight: float = 0.0


@dataclass
class ContribCardConfig(BaseConfig):
    """Configuration for contributor card rendering."""

    # Theme and colors
    theme: str = "default"
    title_color: str | None = None
    text_color: str | None = None
    bg_color: str | None = None
    border_color: str | None = None

    # Visibility options
    hide_border: bool = False
    hide_title: bool = False

    # Layout options
    card_width: int = 467
    border_radius: float = 4.5

    # Display options
    limit: int = 10
    exclude_repo: list[str] = field(default_factory=list)
    custom_title: str | None = None

    # Animation options
    disable_animations: bool = False


@dataclass
class ContribFetchConfig(BaseConfig):
    """Configuration for fetching contributor data."""

    username: str
    token: str
    limit: int = 10
    exclude_repo: list[str] = field(default_factory=list)

"""Configuration dataclasses for GitHub Stats Card rendering."""

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class StatsCardConfig:
    """Configuration for stats card rendering."""

    # Theme and colors
    theme: str = "default"
    title_color: Optional[str] = None
    text_color: Optional[str] = None
    icon_color: Optional[str] = None
    bg_color: Optional[str] = None
    border_color: Optional[str] = None
    ring_color: Optional[str] = None

    # Visibility options
    hide: list[str] = field(default_factory=list)
    show: list[str] = field(default_factory=list)
    hide_title: bool = False
    hide_border: bool = False
    hide_rank: bool = False
    show_icons: bool = False

    # Layout options
    card_width: Optional[int] = None
    line_height: int = 25
    border_radius: float = 4.5

    # Text options
    custom_title: Optional[str] = None
    locale: str = "en"
    text_bold: bool = True

    # Number formatting
    number_format: str = "short"  # "short" or "long"
    number_precision: Optional[int] = None

    # Animation options
    disable_animations: bool = False
    rank_icon: str = "default"  # "default", "github", "percentile"

    # Commit filtering
    include_all_commits: bool = False

    @classmethod
    def from_cli_args(cls, **kwargs) -> "StatsCardConfig":
        """
        Create configuration from CLI arguments.

        Filters out None values and creates a config instance.

        Args:
            **kwargs: CLI argument values

        Returns:
            StatsCardConfig instance
        """
        # Filter out None values and keys not in dataclass
        valid_fields = {f.name for f in cls.__dataclass_fields__.values()}
        filtered = {k: v for k, v in kwargs.items() if k in valid_fields and v is not None}

        # Handle list fields that might be strings
        if "hide" in filtered and isinstance(filtered["hide"], str):
            filtered["hide"] = [s.strip() for s in filtered["hide"].split(",") if s.strip()]
        if "show" in filtered and isinstance(filtered["show"], str):
            filtered["show"] = [s.strip() for s in filtered["show"].split(",") if s.strip()]

        return cls(**filtered)


@dataclass
class LangsCardConfig:
    """Configuration for top languages card rendering."""

    # Theme and colors
    theme: str = "default"
    title_color: Optional[str] = None
    text_color: Optional[str] = None
    bg_color: Optional[str] = None
    border_color: Optional[str] = None

    # Visibility options
    hide: list[str] = field(default_factory=list)
    hide_title: bool = False
    hide_border: bool = False
    hide_progress: bool = False

    # Layout options
    layout: str = "normal"  # "normal", "compact", "donut", "donut-vertical", "pie"
    card_width: Optional[int] = None
    border_radius: float = 4.5

    # Language options
    langs_count: Optional[int] = None
    exclude_repo: list[str] = field(default_factory=list)

    # Weighting options
    size_weight: float = 1.0
    count_weight: float = 0.0

    # Display options
    custom_title: Optional[str] = None
    stats_format: str = "percentages"  # "percentages" or "bytes"

    # Animation options
    disable_animations: bool = False

    @classmethod
    def from_cli_args(cls, **kwargs) -> "LangsCardConfig":
        """
        Create configuration from CLI arguments.

        Filters out None values and creates a config instance.

        Args:
            **kwargs: CLI argument values

        Returns:
            LangsCardConfig instance
        """
        # Filter out None values and keys not in dataclass
        valid_fields = {f.name for f in cls.__dataclass_fields__.values()}
        filtered = {k: v for k, v in kwargs.items() if k in valid_fields and v is not None}

        # Handle list fields that might be strings
        if "hide" in filtered and isinstance(filtered["hide"], str):
            filtered["hide"] = [s.strip() for s in filtered["hide"].split(",") if s.strip()]
        if "exclude_repo" in filtered and isinstance(filtered["exclude_repo"], str):
            filtered["exclude_repo"] = [
                s.strip() for s in filtered["exclude_repo"].split(",") if s.strip()
            ]

        return cls(**filtered)


@dataclass
class FetchConfig:
    """Configuration for fetching GitHub data."""

    username: str
    token: str
    include_all_commits: bool = False
    commits_year: Optional[int] = None
    show: list[str] = field(default_factory=list)

    @classmethod
    def from_cli_args(cls, **kwargs) -> "FetchConfig":
        """
        Create configuration from CLI arguments.

        Args:
            **kwargs: CLI argument values

        Returns:
            FetchConfig instance
        """
        valid_fields = {f.name for f in cls.__dataclass_fields__.values()}
        filtered = {k: v for k, v in kwargs.items() if k in valid_fields and v is not None}

        # Handle show list
        if "show" in filtered and isinstance(filtered["show"], str):
            filtered["show"] = [s.strip() for s in filtered["show"].split(",") if s.strip()]

        return cls(**filtered)


@dataclass
class LangsFetchConfig:
    """Configuration for fetching language data."""

    username: str
    token: str
    exclude_repo: list[str] = field(default_factory=list)
    size_weight: float = 1.0
    count_weight: float = 0.0

    @classmethod
    def from_cli_args(cls, **kwargs) -> "LangsFetchConfig":
        """
        Create configuration from CLI arguments.

        Args:
            **kwargs: CLI argument values

        Returns:
            LangsFetchConfig instance
        """
        valid_fields = {f.name for f in cls.__dataclass_fields__.values()}
        filtered = {k: v for k, v in kwargs.items() if k in valid_fields and v is not None}

        # Handle exclude_repo list
        if "exclude_repo" in filtered and isinstance(filtered["exclude_repo"], str):
            filtered["exclude_repo"] = [
                s.strip() for s in filtered["exclude_repo"].split(",") if s.strip()
            ]

        return cls(**filtered)

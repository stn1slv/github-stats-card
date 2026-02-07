"""Exception hierarchy for GitHub Stats Card."""


class GitHubStatsCardError(Exception):
    """Base exception for all GitHub Stats Card errors."""

    pass


class APIError(GitHubStatsCardError):
    """GitHub API request failed."""

    pass


class FetchError(APIError):
    """Error fetching data from GitHub API.
    
    Kept for backwards compatibility. Use APIError for new code.
    """

    pass


class LanguageFetchError(APIError):
    """Error fetching language data from GitHub API.
    
    Kept for backwards compatibility. Use APIError for new code.
    """

    pass


class ValidationError(GitHubStatsCardError):
    """Invalid configuration or input parameters."""

    pass


class RenderError(GitHubStatsCardError):
    """SVG rendering failed."""

    pass


class ThemeError(GitHubStatsCardError):
    """Theme-related error (invalid theme name, missing colors, etc.)."""

    pass


class ColorError(ValidationError):
    """Invalid color specification."""

    pass

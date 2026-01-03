"""Internationalization support for stats card labels."""

from typing import TypedDict


class Translations(TypedDict):
    """Translation strings for a locale."""

    statcard_title: str
    statcard_ranktitle: str
    statcard_totalstars: str
    statcard_commits: str
    statcard_prs: str
    statcard_prs_merged: str
    statcard_prs_merged_percentage: str
    statcard_issues: str
    statcard_contribs: str
    statcard_reviews: str
    statcard_discussions_started: str
    statcard_discussions_answered: str


TRANSLATIONS: dict[str, Translations] = {
    "en": {
        "statcard_title": "{name}'s GitHub Stats",
        "statcard_ranktitle": "{name}'s GitHub Rank",
        "statcard_totalstars": "Total Stars Earned",
        "statcard_commits": "Total Commits",
        "statcard_prs": "Total PRs",
        "statcard_prs_merged": "Total PRs Merged",
        "statcard_prs_merged_percentage": "PRs Merged",
        "statcard_issues": "Total Issues",
        "statcard_contribs": "Total Repositories",
        "statcard_reviews": "Total Reviews",
        "statcard_discussions_started": "Discussions Started",
        "statcard_discussions_answered": "Discussions Answered",
    },
}


def get_translation(key: str, locale: str = "en", **kwargs: str) -> str:
    """
    Get translated string for the given key and locale.

    Args:
        key: Translation key (e.g., 'statcard_title')
        locale: Locale code (default: 'en')
        **kwargs: Format arguments for the translation string

    Returns:
        Translated and formatted string

    Examples:
        >>> get_translation('statcard_title', 'en', name='octocat')
        "octocat's GitHub Stats"
    """
    translations = TRANSLATIONS.get(locale, TRANSLATIONS["en"])
    template = translations.get(key, key)  # type: ignore

    if kwargs:
        try:
            return template.format(**kwargs)
        except (KeyError, ValueError):
            return template

    return template

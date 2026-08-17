"""Tests for top languages card rendering."""

import re

import pytest

from src.core.config import LangsCardConfig
from src.core.constants import CARD_PADDING, FONT_SIZE_LANG, LANGS_LEGEND_TEXT_X
from src.core.utils import measure_text
from src.github.langs_fetcher import Language
from src.rendering.langs import (
    format_bytes,
    get_default_langs_count,
    get_display_value,
    render_top_languages,
    trim_top_languages,
)


@pytest.fixture
def sample_langs():
    return {
        "Python": Language(name="Python", color="#3572A5", size=1000, count=2, score=1000),
        "JavaScript": Language(name="JavaScript", color="#f1e05a", size=500, count=1, score=500),
        "TypeScript": Language(name="TypeScript", color="#3178c6", size=1500, count=1, score=1500),
    }


@pytest.mark.parametrize(
    ("size", "expected"),
    [
        (0, "0 B"),
        (1024, "1.0 KB"),
        (1024 * 1024, "1.0 MB"),
    ],
)
def test_format_bytes(size: int, expected: str):
    assert format_bytes(size) == expected


def test_format_bytes_negative():
    with pytest.raises(ValueError, match="Bytes must be non-negative"):
        format_bytes(-1)


@pytest.mark.parametrize(
    ("fmt", "expected"),
    [
        ("bytes", "1.0 KB"),
        ("percentages", "50.5%"),
    ],
)
def test_get_display_value(fmt: str, expected: str):
    assert get_display_value(1024, 50.5, fmt) == expected


@pytest.mark.parametrize(
    ("layout", "expected"),
    [
        ("normal", 5),
        ("compact", 6),
        ("invalid", 5),
    ],
)
def test_get_default_langs_count(layout: str, expected: int):
    assert get_default_langs_count(layout) == expected


def test_trim_top_languages(sample_langs):
    langs, total_score = trim_top_languages(sample_langs, 2)
    assert len(langs) == 2
    assert langs[0].name == "TypeScript"
    assert langs[1].name == "Python"
    assert total_score == 2500


def test_trim_top_languages_empty():
    langs, total = trim_top_languages({}, 5)
    assert langs == []
    assert total == 0


def test_render_top_languages_basic(sample_langs):
    config = LangsCardConfig()
    svg = render_top_languages(sample_langs, config)
    assert "Most Used Languages" in svg
    assert "Python" in svg
    assert "JavaScript" in svg
    assert "TypeScript" in svg


@pytest.mark.parametrize(
    ("layout", "marker"),
    [
        ("compact", 'mask="url(#rect-mask)"'),
        ("donut", 'stroke-width="25"'),
        ("pie", 'data-testid="lang-pie"'),
    ],
)
def test_render_top_languages_layout(sample_langs, layout: str, marker: str):
    config = LangsCardConfig(layout=layout)
    svg = render_top_languages(sample_langs, config)
    assert marker in svg


def test_render_top_languages_hide_languages(sample_langs):
    config = LangsCardConfig(hide=["Python"])
    svg = render_top_languages(sample_langs, config)
    assert "Python" not in svg
    assert "TypeScript" in svg


def test_render_top_languages_custom_title(sample_langs):
    config = LangsCardConfig(custom_title="My Tech Stack")
    svg = render_top_languages(sample_langs, config)
    assert "My Tech Stack" in svg


def test_render_top_languages_hide_title(sample_langs):
    config = LangsCardConfig(hide_title=True)
    svg = render_top_languages(sample_langs, config)
    # Header text should be hidden, but title tag still present for a11y
    assert 'class="header"' not in svg
    assert '<title id="titleId">Most Used Languages</title>' in svg


def test_render_top_languages_hide_border(sample_langs):
    config = LangsCardConfig(hide_border=True)
    svg = render_top_languages(sample_langs, config)
    assert 'stroke-opacity="0"' in svg


def test_render_top_languages_theme(sample_langs):
    config = LangsCardConfig(theme="radical")
    svg = render_top_languages(sample_langs, config)
    assert "#fe428e" in svg  # title_color
    assert "#141321" in svg  # bg_color


def test_render_top_languages_custom_colors(sample_langs):
    config = LangsCardConfig(title_color="ff0000")
    svg = render_top_languages(sample_langs, config)
    assert "fill: #ff0000" in svg


def test_render_top_languages_bytes_format(sample_langs):
    config = LangsCardConfig(stats_format="bytes")
    svg = render_top_languages(sample_langs, config)
    assert "1.5 KB" in svg
    assert "500.0 B" in svg


def test_render_top_languages_percentages_format(sample_langs):
    config = LangsCardConfig(stats_format="percentages")
    svg = render_top_languages(sample_langs, config)
    assert "50.0%" in svg


def test_render_top_languages_disable_animations(sample_langs):
    config = LangsCardConfig(disable_animations=True)
    svg = render_top_languages(sample_langs, config)
    assert "animation:" not in svg


def test_render_top_languages_empty():
    config = LangsCardConfig()
    svg = render_top_languages({}, config)
    assert "No languages data available" in svg


def test_render_top_languages_invalid_layout(sample_langs):
    config = LangsCardConfig(layout="invalid")
    svg = render_top_languages(sample_langs, config)
    # Should fallback to normal
    assert 'data-testid="lang-progress"' in svg


def test_render_top_languages_langs_count(sample_langs):
    config = LangsCardConfig(langs_count=1)
    svg = render_top_languages(sample_langs, config)
    assert "TypeScript" in svg
    assert "Python" not in svg


def test_render_top_languages_card_width(sample_langs):
    config = LangsCardConfig(card_width=400)
    svg = render_top_languages(sample_langs, config)
    assert 'width="400"' in svg


def test_render_top_languages_border_radius(sample_langs):
    config = LangsCardConfig(border_radius=10)
    svg = render_top_languages(sample_langs, config)
    assert 'rx="10"' in svg


def test_render_top_languages_hide_progress(sample_langs):
    config = LangsCardConfig(layout="compact", hide_progress=True)
    svg = render_top_languages(sample_langs, config)
    assert 'mask="url(#rect-mask)"' not in svg


def test_donut_vertical_is_not_the_pie_layout(sample_langs):
    """donut-vertical used to render render_pie_layout verbatim."""
    pie = render_top_languages(sample_langs, LangsCardConfig(layout="pie"))
    donut_vertical = render_top_languages(sample_langs, LangsCardConfig(layout="donut-vertical"))

    assert pie != donut_vertical
    # A donut is drawn with stroked circles, a pie with filled wedge paths
    assert 'data-testid="lang-pie"' in pie
    assert 'data-testid="lang-pie"' not in donut_vertical
    assert "stroke-dasharray" in donut_vertical


def test_donut_vertical_stacks_the_legend_below_the_ring(sample_langs):
    """Vertical means ring on top, legend underneath, and both inside the card."""
    svg = render_top_languages(sample_langs, LangsCardConfig(layout="donut-vertical"))

    height = int(re.search(r'<svg width="\d+" height="(\d+)"', svg).group(1))
    # Anchor on the group that actually holds the legend; the title group also
    # sits at x=25, so a looser pattern matches it first.
    legend_y = int(re.search(r'<g transform="translate\(25, (\d+)\)">\s*<g class="stagger"', svg).group(1))
    ring_center_y = float(re.search(r'<circle[^>]*cy="([\d.]+)"[^>]*stroke-dasharray', svg, re.DOTALL).group(1))

    assert ring_center_y < legend_y
    assert legend_y < height


def test_donut_vertical_with_hide_progress_is_not_sized_as_a_compact_card(sample_langs):
    """The height and layout dispatch must agree, or the ring renders into a clipped card."""
    plain = render_top_languages(sample_langs, LangsCardConfig(layout="donut-vertical"))
    hidden = render_top_languages(sample_langs, LangsCardConfig(layout="donut-vertical", hide_progress=True))

    # hide_progress means nothing to a chart layout: same card, same content
    assert plain == hidden
    # And the ring is still drawn, not replaced by the compact legend
    assert "stroke-dasharray" in hidden


def test_donut_vertical_legend_second_column_stays_inside_the_card(sample_langs):
    """A long language name in column 1 must not run into column 2's marker.

    Measures the rendered text extent against the rendered column boundary. The
    previous version compared `second_column` against the formula it is computed
    from, so it reduced to `floor(x) <= x` and passed with the width derivation
    removed entirely.
    """
    long_name = "Jupyter Notebook Extension"
    langs = dict(sample_langs)
    langs[long_name] = Language(name=long_name, color="#DA5B0B", size=900, count=1, score=900)

    svg = render_top_languages(langs, LangsCardConfig(layout="donut-vertical"))

    width = int(re.search(r'<svg width="(\d+)"', svg).group(1))
    entries = [e.strip() for e in re.findall(r'class="lang-name">([^<]+)<', svg)]
    assert any(long_name in e for e in entries), "the long entry must actually be rendered"

    widest = max(measure_text(e, FONT_SIZE_LANG) for e in entries)
    column_offsets = [float(x) for x in re.findall(r'transform="translate\(([\d.]+), \d+\)"', svg)]
    second_column = max(column_offsets)

    # Column 1's widest text must stop before column 2's marker starts...
    col1_text_end = CARD_PADDING + LANGS_LEGEND_TEXT_X + widest
    assert col1_text_end <= CARD_PADDING + second_column, (
        f"column 1 text ends at {col1_text_end}, column 2 starts at {CARD_PADDING + second_column}"
    )
    # ...and column 2's text must stop before the border
    col2_text_end = CARD_PADDING + second_column + LANGS_LEGEND_TEXT_X + widest
    assert col2_text_end <= width, f"column 2 text ends at {col2_text_end}, card is {width} wide"


def test_donut_vertical_width_grows_with_the_longest_entry(sample_langs):
    """The floor must be derived from the entries rendered, not a constant."""
    long_name = "Jupyter Notebook Extension With A Very Long Name"
    langs = dict(sample_langs)
    langs[long_name] = Language(name=long_name, color="#DA5B0B", size=900, count=1, score=900)

    short = render_top_languages(sample_langs, LangsCardConfig(layout="donut-vertical"))
    wide = render_top_languages(langs, LangsCardConfig(layout="donut-vertical"))

    assert int(re.search(r'<svg width="(\d+)"', wide).group(1)) > int(re.search(r'<svg width="(\d+)"', short).group(1))

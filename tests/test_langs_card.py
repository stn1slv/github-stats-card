"""Tests for top languages card rendering."""

import pytest

from src.rendering.langs import (
    render_top_languages,
    trim_top_languages,
    get_default_langs_count,
    format_bytes,
    get_display_value,
)
from src.github.langs_fetcher import Language
from src.core.config import LangsCardConfig


@pytest.fixture
def sample_langs():
    return {
        "Python": Language(name="Python", color="#3572A5", size=1000, count=2),
        "JavaScript": Language(name="JavaScript", color="#f1e05a", size=500, count=1),
        "TypeScript": Language(name="TypeScript", color="#3178c6", size=1500, count=1),
    }


def test_format_bytes():
    assert format_bytes(0) == "0 B"
    assert format_bytes(1024) == "1.0 KB"
    assert format_bytes(1024 * 1024) == "1.0 MB"
    with pytest.raises(ValueError):
        format_bytes(-1)


def test_get_display_value():
    assert get_display_value(1024, 50.5, "bytes") == "1.0 KB"
    assert get_display_value(1024, 50.5, "percentages") == "50.5%"


def test_get_default_langs_count():
    assert get_default_langs_count("normal") == 5
    assert get_default_langs_count("compact") == 6
    assert get_default_langs_count("invalid") == 5


def test_trim_top_languages(sample_langs):
    langs, total = trim_top_languages(sample_langs, 2)
    assert len(langs) == 2
    assert langs[0].name == "TypeScript"
    assert langs[1].name == "Python"
    assert total == 2500


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


def test_render_top_languages_compact(sample_langs):
    config = LangsCardConfig(layout="compact")
    svg = render_top_languages(sample_langs, config)
    assert 'mask="url(#rect-mask)"' in svg


def test_render_top_languages_donut(sample_langs):
    config = LangsCardConfig(layout="donut")
    svg = render_top_languages(sample_langs, config)
    assert 'stroke-width="25"' in svg


def test_render_top_languages_pie(sample_langs):
    config = LangsCardConfig(layout="pie")
    svg = render_top_languages(sample_langs, config)
    assert 'data-testid="lang-pie"' in svg


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
    assert "#fe428e" in svg  # titleColor
    assert "#141321" in svg  # bgColor


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

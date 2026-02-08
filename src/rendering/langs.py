"""Top Languages card renderer with multiple layout styles."""

import math

from .base import render_card
from .colors import get_card_colors
from ..core.config import LangsCardConfig
from ..core.constants import (
    CARD_PADDING,
    DEFAULT_LANGS_CARD_WIDTH,
    DEFAULT_LANGS_COMPACT_WIDTH,
    MAXIMUM_LANGS_COUNT,
    MIN_CARD_WIDTH,
    LANGS_COMPACT_COLUMN_WIDTH,
    LANGS_COMPACT_COLUMN_WIDTH_WIDE,
    LANGS_COMPACT_ROW_HEIGHT,
    LANGS_DONUT_RADIUS,
    LANGS_PIE_RADIUS,
    ANIMATION_STAGGER_DELAY_MS,
)
from ..github.langs_fetcher import Language
from ..core.utils import clamp_value, encode_html


def trim_top_languages(
    top_langs: dict[str, Language],
    langs_count: int,
    hide: list[str] | None = None,
) -> tuple[list[Language], int]:
    """
    Trim languages to specified count while hiding certain languages.

    Args:
        top_langs: Dictionary of language name to Language object
        langs_count: Maximum number of languages to show
        hide: List of language names to hide

    Returns:
        Tuple of (list of languages, total size of all languages)
    """
    hide = hide or []
    langs_to_hide = {lang.lower().strip() for lang in hide}
    langs_count = int(clamp_value(int(langs_count), 1, MAXIMUM_LANGS_COUNT))

    # Filter and sort
    langs = [lang for lang in top_langs.values() if lang.name.lower().strip() not in langs_to_hide]
    langs = sorted(langs, key=lambda x: x.size, reverse=True)[:langs_count]

    total_size = sum(lang.size for lang in langs)

    return langs, total_size


def get_default_langs_count(layout: str) -> int:
    """Get default language count based on layout."""
    return {
        "normal": 5,
        "compact": 6,
        "donut": 5,
        "donut-vertical": 6,
        "pie": 6,
    }.get(layout, 5)


def format_bytes(bytes_val: int) -> str:
    """
    Convert bytes to human-readable format.

    Args:
        bytes_val: Number of bytes

    Returns:
        Formatted string (e.g., "1.2 MB")
    """
    if bytes_val < 0:
        raise ValueError("Bytes must be non-negative")
    if bytes_val == 0:
        return "0 B"

    sizes = ["B", "KB", "MB", "GB", "TB"]
    base = 1024
    i = int(math.floor(math.log(bytes_val) / math.log(base)))
    i = min(i, len(sizes) - 1)

    return f"{bytes_val / (base ** i):.1f} {sizes[i]}"


def get_display_value(size: int, percentage: float, stats_format: str) -> str:
    """
    Get display value based on format.

    Args:
        size: Size in bytes
        percentage: Percentage value
        stats_format: Format type ('percentages' or 'bytes')

    Returns:
        Formatted display string
    """
    if stats_format == "bytes":
        return format_bytes(size)
    return f"{percentage:.1f}%"


# ============ Layout Renderers ============


def render_normal_layout(
    langs: list[Language],
    width: int,
    total_size: int,
    stats_format: str,
    text_color: str,
) -> str:
    """Render normal layout with vertical progress bars."""
    items = []
    padding_right = 95
    progress_width = width - padding_right

    for index, lang in enumerate(langs):
        percentage = (lang.size / total_size) * 100 if total_size > 0 else 0
        display_value = get_display_value(lang.size, percentage, stats_format)
        stagger_delay = (index + 3) * ANIMATION_STAGGER_DELAY_MS

        item = f"""
        <g class="stagger" style="animation-delay: {stagger_delay}ms" transform="translate(0, {index * 40})">
          <text data-testid="lang-name" x="2" y="15" class="lang-name">{encode_html(lang.name)}</text>
          <text x="{width - padding_right + 10}" y="34" class="lang-name">{display_value}</text>
          <svg width="{progress_width}" x="0" y="25">
            <rect rx="5" ry="5" x="0" y="0" width="{progress_width}" height="8" fill="#ddd"></rect>
            <svg data-testid="lang-progress" width="{percentage}%">
              <rect height="8" fill="{lang.color}" rx="5" ry="5" x="0" y="0"
                    class="lang-progress" style="animation-delay: {stagger_delay + 300}ms;" />
            </svg>
          </svg>
        </g>
        """
        items.append(item)

    return "\n".join(items)


def render_compact_layout(
    langs: list[Language],
    width: int,
    total_size: int,
    hide_progress: bool,
    stats_format: str,
    text_color: str,
) -> str:
    """Render compact layout with stacked progress bar."""
    padding_right = 50
    offset_width = width - padding_right
    # Use wider column width for 467px width layout
    column_width = LANGS_COMPACT_COLUMN_WIDTH_WIDE if width >= 467 else LANGS_COMPACT_COLUMN_WIDTH

    # Progress bar (stacked colors)
    progress_bar = ""
    if not hide_progress:
        progress_offset = 0.0
        bars = []
        for lang in langs:
            percentage = (lang.size / total_size) * offset_width if total_size > 0 else 0
            # Add minimum width for visibility of small bars
            bar_width = percentage + 10 if percentage > 0 and percentage < 10 else percentage
            bars.append(f"""
        <rect
          mask="url(#rect-mask)"
          data-testid="lang-progress"
          x="{progress_offset}"
          y="0"
          width="{bar_width}"
          height="8"
          fill="{lang.color}"
        />
      """)
            progress_offset += percentage

        progress_bar = f"""
  
      <mask id="rect-mask">
          <rect x="0" y="0" width="{offset_width}" height="8" fill="white" rx="5"/>
        </mask>
        {"".join(bars)}
      """

    # Language legend (2 columns)
    half = (len(langs) + 1) // 2
    col1_langs = langs[:half]
    col2_langs = langs[half:]

    # Calculate the max name width for alignment (approximate based on column width)
    # Use wider column width for 467px width layout
    name_max_width = 180 if width >= 467 else 130

    def render_lang_item(lang: Language, index: int) -> str:
        percentage = (lang.size / total_size) * 100 if total_size > 0 else 0
        display_value = get_display_value(lang.size, percentage, stats_format)
        stagger_delay = (index + 3) * ANIMATION_STAGGER_DELAY_MS

        if hide_progress:
            # Without progress bar, just show the name
            return f"""<g transform="translate(0, {index * 25})">
    <g class="stagger" style="animation-delay: {stagger_delay}ms">
      <circle cx="5" cy="6" r="5" fill="{lang.color}" />
      <text data-testid="lang-name" x="15" y="10" class='lang-name'>
        {encode_html(lang.name)}
      </text>
    </g>
  </g>"""
        else:
            # With progress bar, separate name and percentage for alignment
            return f"""<g transform="translate(0, {index * 25})">
    <g class="stagger" style="animation-delay: {stagger_delay}ms">
      <circle cx="5" cy="6" r="5" fill="{lang.color}" />
      <text data-testid="lang-name" x="15" y="10" class='lang-name'>
        {encode_html(lang.name)}
      </text>
      <text x="{name_max_width}" y="10" class='lang-name' text-anchor="end">
        {display_value}
      </text>
    </g>
  </g>"""

    col1 = "\n".join(render_lang_item(lang, i) for i, lang in enumerate(col1_langs))
    col2 = "\n".join(render_lang_item(lang, i) for i, lang in enumerate(col2_langs))

    y_offset = 0 if hide_progress else 25

    return f"""
    {progress_bar}
    <g transform="translate(0, {y_offset})">
      <g transform="translate(0, 0)">{col1}</g><g transform="translate({column_width}, 0)">{col2}</g>
    </g>
  """


def render_donut_layout(
    langs: list[Language],
    width: int,
    total_size: int,
    stats_format: str,
    text_color: str,
) -> str:
    """Render donut chart layout."""
    radius = LANGS_DONUT_RADIUS
    circumference = 2 * math.pi * radius
    center_x, center_y = 100, 100

    # Generate donut segments
    segments = []
    offset = 0.0

    for index, lang in enumerate(langs):
        percentage = (lang.size / total_size) * 100 if total_size > 0 else 0
        segment_length = (percentage / 100) * circumference
        stagger_delay = (index + 3) * ANIMATION_STAGGER_DELAY_MS

        segments.append(f"""
        <circle class="stagger" style="animation-delay: {stagger_delay}ms"
                cx="{center_x}" cy="{center_y}" r="{radius}"
                fill="transparent" stroke="{lang.color}" stroke-width="25"
                stroke-dasharray="{segment_length} {circumference}"
                stroke-dashoffset="{-offset}"
                transform="rotate(-90 {center_x} {center_y})" />
        """)
        offset += segment_length

    # Legend on the right
    legend_items = []
    for index, lang in enumerate(langs):
        percentage = (lang.size / total_size) * 100 if total_size > 0 else 0
        display_value = get_display_value(lang.size, percentage, stats_format)
        stagger_delay = (index + 3) * ANIMATION_STAGGER_DELAY_MS

        legend_items.append(f"""
        <g class="stagger" style="animation-delay: {stagger_delay}ms" transform="translate(0, {index * 32})">
          <circle cx="5" cy="6" r="5" fill="{lang.color}" />
          <text x="15" y="10" class="lang-name">{encode_html(lang.name)} {display_value}</text>
        </g>
        """)

    return f"""
    <g transform="translate(25, 0)">
      {"".join(segments)}
    </g>
    <g transform="translate(175, 50)">
      {"".join(legend_items)}
    </g>
    """


def render_pie_layout(
    langs: list[Language],
    total_size: int,
    stats_format: str,
    text_color: str,
) -> str:
    """Render pie chart layout."""
    radius = LANGS_PIE_RADIUS
    center_x, center_y = 150, 100

    def polar_to_cartesian(cx: float, cy: float, r: float, angle_deg: float) -> tuple[float, float]:
        angle_rad = math.radians(angle_deg)
        return (cx + r * math.cos(angle_rad), cy + r * math.sin(angle_rad))

    # Generate pie slices
    slices = []
    current_angle = -90.0  # Start from top

    for index, lang in enumerate(langs):
        percentage = (lang.size / total_size) * 100 if total_size > 0 else 0
        angle = (percentage / 100) * 360
        stagger_delay = (index + 3) * ANIMATION_STAGGER_DELAY_MS

        # Calculate arc
        start_x, start_y = polar_to_cartesian(center_x, center_y, radius, current_angle)
        end_angle = current_angle + angle
        end_x, end_y = polar_to_cartesian(center_x, center_y, radius, end_angle)

        large_arc = 1 if angle > 180 else 0

        path = f"M {center_x} {center_y} L {start_x} {start_y} A {radius} {radius} 0 {large_arc} 1 {end_x} {end_y} Z"

        slices.append(f"""
        <path class="stagger" style="animation-delay: {stagger_delay}ms"
              d="{path}" fill="{lang.color}" data-testid="lang-pie" />
        """)

        current_angle = end_angle

    # Legend below
    half = (len(langs) + 1) // 2
    legend_items = []

    for index, lang in enumerate(langs):
        percentage = (lang.size / total_size) * 100 if total_size > 0 else 0
        display_value = get_display_value(lang.size, percentage, stats_format)
        stagger_delay = (index + 3) * ANIMATION_STAGGER_DELAY_MS
        col = 0 if index < half else 1
        row = index if index < half else index - half

        legend_items.append(f"""
        <g class="stagger" style="animation-delay: {stagger_delay}ms" 
           transform="translate({col * LANGS_COMPACT_COLUMN_WIDTH}, {row * LANGS_COMPACT_ROW_HEIGHT})">
          <circle cx="5" cy="6" r="5" fill="{lang.color}" />
          <text x="15" y="10" class="lang-name">{encode_html(lang.name)} {display_value}</text>
        </g>
        """)

    return f"""
    <g transform="translate(0, 0)">
      {"".join(slices)}
    </g>
    <g transform="translate(25, 220)">
      {"".join(legend_items)}
    </g>
    """


# ============ Main Renderer ============


def render_top_languages(
    top_langs: dict[str, Language],
    config: LangsCardConfig,
) -> str:
    """
    Render top languages card as SVG.

    Args:
        top_langs: Dictionary of language name to Language object
        config: Configuration object with all rendering options

    Returns:
        SVG string
    """
    # Validate layout
    valid_layouts = ["normal", "compact", "donut", "donut-vertical", "pie"]
    if config.layout not in valid_layouts:
        config.layout = "normal"

    # Validate stats_format
    if config.stats_format not in ["percentages", "bytes"]:
        config.stats_format = "percentages"

    # Default langs_count based on layout
    langs_count = config.langs_count
    if langs_count is None:
        langs_count = get_default_langs_count(config.layout)

    # Trim and filter languages
    langs, total_size = trim_top_languages(top_langs, langs_count, config.hide)

    # Card dimensions - use compact width for compact layout, otherwise default
    if config.layout == "compact":
        width = config.card_width or DEFAULT_LANGS_COMPACT_WIDTH
    else:
        width = config.card_width or DEFAULT_LANGS_CARD_WIDTH
    width = max(width, MIN_CARD_WIDTH)

    # Calculate height based on layout
    if config.layout == "compact" or config.hide_progress:
        height = 60 + ((len(langs) + 1) // 2) * 25
        if config.hide_progress:
            height -= 25
    elif config.layout == "donut":
        height = 215 + max(len(langs) - 5, 0) * 32
        width = width + 50
    elif config.layout == "donut-vertical":
        height = 300 + ((len(langs) + 1) // 2) * 25
    elif config.layout == "pie":
        height = 300 + ((len(langs) + 1) // 2) * 25
    else:  # normal
        height = 45 + (len(langs) + 1) * 40

    # Add 30px extra height when title is shown (55px offset vs 25px)
    if not config.hide_title:
        height += 30

    # Get theme colors
    colors = get_card_colors(
        theme=config.theme,
        title_color=config.title_color,
        text_color=config.text_color,
        bg_color=config.bg_color,
        border_color=config.border_color,
    )

    # Extract text color for rendering
    final_text_color = (
        colors["textColor"] if isinstance(colors["textColor"], str) else colors["textColor"][1]
    )

    # Render layout
    if len(langs) == 0:
        height = 90
        final_layout = """
        <text x="25" y="50" class="lang-name">No languages data available</text>
        """
    elif config.layout == "pie":
        final_layout = render_pie_layout(langs, total_size, config.stats_format, final_text_color)
    elif config.layout == "donut-vertical":
        final_layout = f"""
        <g transform="translate(0, 0)">
          {render_pie_layout(langs, total_size, config.stats_format, final_text_color)}
        </g>
        """
    elif config.layout == "donut":
        final_layout = render_donut_layout(
            langs, width, total_size, config.stats_format, final_text_color
        )
    elif config.layout == "compact" or config.hide_progress:
        final_layout = render_compact_layout(
            langs, width, total_size, config.hide_progress, config.stats_format, final_text_color
        )
    else:
        final_layout = render_normal_layout(
            langs, width, total_size, config.stats_format, final_text_color
        )

    # Add CSS
    css = f"""
    .lang-name {{
      font: 400 11px "Segoe UI", Ubuntu, Sans-Serif;
      fill: {final_text_color};
    }}
    """

    if not config.disable_animations:
        css += """
    .stagger {
      opacity: 0;
      animation: fadeInAnimation 0.3s ease-in-out forwards;
    }
    .lang-progress {
      animation: growWidthAnimation 0.6s ease-in-out forwards;
    }
    @keyframes growWidthAnimation {
      from { width: 0; }
      to { width: 100%; }
    }
    @keyframes fadeInAnimation {
      from { opacity: 0; }
      to { opacity: 1; }
    }
    """

    # Wrap in padding group for most layouts
    if config.layout in ["pie", "donut-vertical"]:
        body = final_layout
    else:
        body = f'<svg data-testid="lang-items" x="{CARD_PADDING}">{final_layout}</svg>'

    # Add CSS to body
    body = f"<style>{css}</style>\n{body}"

    # Render card
    title = config.custom_title or "Most Used Languages"
    svg = render_card(
        title=title,
        body=body,
        width=width,
        height=height,
        colors=colors,
        hide_title=config.hide_title,
        hide_border=config.hide_border,
        border_radius=config.border_radius,
        disable_animations=config.disable_animations,
    )

    return svg

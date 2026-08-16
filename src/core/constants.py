"""Constants for GitHub Stats Card rendering and configuration."""

import os

# API Configuration
# Support GitHub Enterprise Server and other platforms via environment variables
# Fallback to github.com if not set
API_BASE_URL = os.environ.get("GITHUB_API_URL", "https://api.github.com")
GRAPHQL_ENDPOINT = os.environ.get("GITHUB_GRAPHQL_URL", f"{API_BASE_URL}/graphql")
API_TIMEOUT = 30

# Card Dimensions
CARD_PADDING = 25
DEFAULT_CARD_WIDTH = 495
DEFAULT_LANGS_CARD_WIDTH = 300
DEFAULT_LANGS_COMPACT_WIDTH = 467
MIN_CARD_WIDTH = 280
DEFAULT_BORDER_RADIUS = 4.5

# User Stats Card Layout
STAT_LINE_HEIGHT = 25
DEFAULT_LINE_HEIGHT = 25
USER_STATS_CARD_BASE_HEIGHT = 40
DEFAULT_USER_STATS_CARD_WIDTH = 467
RANK_CIRCLE_RADIUS = 40
# Distance from the right card edge to the rank circle's transform origin.
# The circle is positioned relative to the width, not at a fixed x, so a custom
# --card-width cannot push it off the canvas (467 - 76.5 = the historic 390.5).
RANK_CIRCLE_RIGHT_MARGIN = 76.5
RANK_CIRCLE_Y_OFFSET = 47.5
# Narrowest card that still fits the fixed stat-value column next to the rank
# circle. Below this the two overlap, so the width is clamped up to it.
MIN_USER_STATS_CARD_WIDTH_WITH_RANK = 420
# Narrowest card without the rank circle. The stat value is left-anchored at an
# absolute x of 25 + 219.01, and a long value such as "12,345,678" runs about
# 84px, so anything below this clips the number against the right border.
# MIN_CARD_WIDTH (280) is not enough here, whatever the other cards use.
MIN_USER_STATS_CARD_WIDTH = 340
STAT_VALUE_X_POSITION = 219.01
STAT_LABEL_X_BASE = 0
STAT_LABEL_X_WITH_ICON = 25

# Languages Card Layout
MAXIMUM_LANGS_COUNT = 20
LANGS_PROGRESS_BAR_HEIGHT = 8
LANGS_LEGEND_CIRCLE_RADIUS = 5
LANGS_COMPACT_COLUMN_WIDTH = 150
LANGS_COMPACT_COLUMN_WIDTH_WIDE = 225  # For 467px width compact layout
LANGS_COMPACT_ROW_HEIGHT = 25
LANGS_DONUT_RADIUS = 40
LANGS_DONUT_STROKE_WIDTH = 25
# donut-vertical stacks the ring above the legend. The ring's outer edge sits at
# center_y + radius + stroke/2 = 100 + 40 + 12.5, so the legend starts clear of it.
LANGS_DONUT_VERTICAL_CENTER_Y = 100
LANGS_DONUT_VERTICAL_LEGEND_Y = 175
LANGS_PIE_RADIUS = 90

# Animation Settings
ANIMATION_INITIAL_DELAY_MS = 450
ANIMATION_STAGGER_DELAY_MS = 150
ANIMATION_FADE_DURATION_MS = 300
ANIMATION_SCALE_DURATION_MS = 300
ANIMATION_GROW_WIDTH_DURATION_MS = 600

# Color Settings
DEFAULT_LANG_COLOR = "#858585"

# Font Settings
FONT_FAMILY_HEADER = "'Segoe UI', Ubuntu, Sans-Serif"
FONT_FAMILY_STAT = "'Segoe UI', Ubuntu, 'Helvetica Neue', Sans-Serif"
FONT_FAMILY_LANG = "'Segoe UI', Ubuntu, Sans-Serif"
FONT_SIZE_HEADER = 18
FONT_SIZE_STAT = 14
FONT_SIZE_LANG = 14
FONT_SIZE_RANK = 24
FONT_WEIGHT_HEADER = 600
FONT_WEIGHT_STAT = 600
FONT_WEIGHT_STAT_BOLD = 700
FONT_WEIGHT_RANK = 800

# Number Formatting
NUMBER_FORMAT_SHORT = "short"
NUMBER_FORMAT_LONG = "long"
NUMBER_FORMAT_THOUSAND_DIVISOR = 1000

# Valid Contribution Types for Contributor Card
VALID_CONTRIB_TYPES: frozenset[str] = frozenset({"commits", "prs", "issues", "reviews"})

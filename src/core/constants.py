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
# render_card translates the body down by this much when the title is hidden,
# and by 30 more when it is shown. Height formulas must account for it.
HIDDEN_TITLE_BODY_OFFSET = 25
DEFAULT_LANGS_CARD_WIDTH = 300
DEFAULT_LANGS_COMPACT_WIDTH = 467
MIN_CARD_WIDTH = 280

# User Stats Card Layout
USER_STATS_CARD_BASE_HEIGHT = 40
DEFAULT_USER_STATS_CARD_WIDTH = 467
RANK_CIRCLE_RADIUS = 40
RANK_CIRCLE_STROKE_WIDTH = 6
# The rim is drawn centred at cx=-10 relative to the group's transform origin
RANK_CIRCLE_CX_OFFSET = -10
# Distance from the right card edge to the rank circle's transform origin.
# The circle is positioned relative to the width, not at a fixed x, so a custom
# --card-width cannot push it off the canvas (467 - 76.5 = the historic 390.5).
RANK_CIRCLE_RIGHT_MARGIN = 76.5
RANK_CIRCLE_Y_OFFSET = 47.5
# Distance from the transform origin to the left edge of the rim, derived rather
# than hand-computed so it cannot drift from the radius and stroke above. The
# stat values must clear this, not merely the card edge.
RANK_CIRCLE_RIM_LEFT_INSET = -RANK_CIRCLE_CX_OFFSET + RANK_CIRCLE_RADIUS + RANK_CIRCLE_STROKE_WIDTH / 2
# Breathing room between the widest stat value and whatever follows it
STAT_VALUE_RIGHT_GAP = 12
STAT_VALUE_X_POSITION = 219.01
STAT_LABEL_X_BASE = 0
STAT_LABEL_X_WITH_ICON = 25

# Languages Card Layout
MAXIMUM_LANGS_COUNT = 20
# x offset of legend text, clearing the marker circle to its left
LANGS_LEGEND_TEXT_X = 15
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

# Color Settings
DEFAULT_LANG_COLOR = "#858585"

# Font Settings
FONT_FAMILY_HEADER = "'Segoe UI', Ubuntu, Sans-Serif"
FONT_FAMILY_STAT = "'Segoe UI', Ubuntu, 'Helvetica Neue', Sans-Serif"
FONT_SIZE_HEADER = 18
FONT_SIZE_STAT = 14
FONT_SIZE_LANG = 14
FONT_SIZE_RANK = 24
FONT_WEIGHT_HEADER = 600
FONT_WEIGHT_STAT = 600
FONT_WEIGHT_STAT_BOLD = 700
FONT_WEIGHT_RANK = 800

# Number Formatting
NUMBER_FORMAT_THOUSAND_DIVISOR = 1000

# Valid Contribution Types for Contributor Card
VALID_CONTRIB_TYPES: frozenset[str] = frozenset({"commits", "prs", "issues", "reviews"})

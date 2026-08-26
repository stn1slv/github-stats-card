# Changelog

All notable changes to this project are documented here. The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.3.0] - 2026-08-26

### Added

- `vue-github-dark` theme: the `vue-dark` palette on GitHub's dark-mode canvas (`#0d1117`), with a matching border so the card has no visible edge and blends into a README viewed in dark mode. It is a fixed dark background, so it will show as a dark rectangle to anyone browsing in light mode.

## [1.2.1] - 2026-08-17

### Fixed

- **The action produced no card at all in 1.2.0.** The self-checkout used `${{ github.action_repository }}` and `${{ github.action_ref }}`, which inside a composite action resolve to the *innermost* action rather than the outer one. Every run therefore checked out `actions/checkout@v4` into the install directory, then exited without installing or generating anything. Combined with a `continue-on-error: true` step, which is common in these workflows, the run went green while silently regenerating nothing.
- The action no longer checks itself out. It installs from `$GITHUB_ACTION_PATH`, where the runner has already placed this repository at exactly the ref the caller pinned, so the code that runs cannot drift from the pin.

**Anyone on 1.2.0 should move to 1.2.1.** Cards stopped being regenerated without any error being reported. Releases up to and including 1.1.10 are unaffected by this specific bug, though they still ignore the pin and run `main`.

## [1.2.0] - 2026-08-17

### Breaking

These inputs used to accept a wider range of values and degrade silently. They now fail fast with a clear message, so a workflow or script passing one of them will start erroring instead of quietly producing a different card than intended.

- `--locale` only accepts locales that actually have translations. Today that is `en` alone. Previously any value was accepted and silently fell back to English, so `--locale de` looked like it worked.
- `--size-weight` and `--count-weight` are limited to the range `0.0`-`2.0`. The value is used as an exponent (`size ** weight`), so a large one raised `OverflowError` during scoring and a negative one inverted the ranking.
- `--number-precision` is limited to `0`-`2`, the range the help text always documented. Out-of-range values used to be ignored without a word.
- `--limit` (contrib card) must be at least `1`. The value feeds a list slice, so `0` produced an empty card and `-1` silently dropped the last repository.
- `--include-all-commits` can no longer be combined with `--commits-year`. The all-time commit search overwrote the year-filtered count, so the year filter was discarded without notice.
- `--card-width` is widened rather than honoured literally when the content would not fit. Stats sit at fixed offsets, so a narrower card rendered the rank circle outside the canvas, printed stat values underneath the ring, or dropped the contrib rank badge on top of the avatar. The floor is estimated from what is actually rendered, so a long `--number-format long` value or a long language name in a `donut-vertical` legend widens the card further than short ones do, and the widening is logged. The estimate assumes a fixed character width, so unusually wide glyphs can still exceed it. The contrib and top-langs cards keep a flat 280px floor.
- The `donut-vertical` top-langs layout now renders an actual vertical donut (ring above, legend below) instead of the pie layout it previously duplicated. Its default card width is 467px rather than 300px so the two-column legend fits.

### Added

- `--debug` on all three commands. It re-raises the original exception with its traceback instead of collapsing to a single line, including fetch failures, and raises this package's log level to `DEBUG`.
- `rank-icon` as a GitHub Action input, and `--rank-icon` is implemented. `percentile` renders the percentile value the rank is derived from, `github` renders the GitHub mark above the letter grade, and `default` keeps the letter grade alone. The option previously parsed and validated but had no effect.
- CI workflow (`.github/workflows/ci.yml`) running format check, lint, type check and tests on every push and pull request, against the committed lockfile.
- `make format-check`, so CI's formatting gate can be reproduced locally.

### Fixed

- **The action now runs the version you pin.** The composite action checked out its own repository without a `ref`, so it always took the default branch: `uses: stn1slv/github-stats-cards@v1.1.9` ran whatever was on `main`. (The fix shipped in 1.2.0 was itself broken and produced no card; see 1.2.1.)
- Gradient colours in non-background slots (`--title-color`, `--text-color`, `--border-color`, `--icon-color`) leaked a Python list into the SVG as `fill: ['90', 'ff0000', '00ff00']`, which is invalid CSS and silently fell back to the browser default. They now collapse to the gradient's first colour stop.
- `--number-precision` divided by 1000 and appended `k` regardless of magnitude, so 5 stars rendered as `0.0k` and 999 rounded up to `1k`.
- API failures during repository pagination, the all-commits search, the issue search, the discussions query, a contribution year, and language pagination were swallowed in silence, producing a plausible card with wrong numbers. Each now writes a warning to stderr naming both the degradation and its cause.
- `FetchError` subclasses `APIError`, so the `except APIError` handlers in the fetchers caught errors they had just raised themselves and wrapped them again. `User 'x' not found` no longer arrives as `Failed to fetch contribution years: User 'x' not found`.
- A GraphQL response carrying an empty `errors` list raised `IndexError` instead of being treated as success.
- `--layout donut-vertical --hide-progress` sized the card with the compact-legend formula while rendering the ring, clipping most of the content.
- `make setup` did not install the dev dependencies, so `make lint`, `make type-check` and `make test` all failed on a fresh clone.
- A `{"data": null}` GraphQL response with no `errors` raised `AttributeError` instead of being reported as a fetch failure.
- A contribution year whose response carried no `user` or no `contributionsCollection`, the usual shape of a field-level GraphQL failure, was dropped without a warning.

### Removed

- Nineteen unused constants from `core/constants.py`, including the nine rank thresholds that described a different scale from the one `rank.py` applies. `RANK_CIRCLE_RIM_LEFT_INSET` is now derived from the radius and stroke width rather than hand-computed beside them.
- The unused `color` parameter of `get_icon_svg`, and the unused `text_color` parameter of both donut layout renderers. Colours come from CSS rules, so the arguments were always discarded.

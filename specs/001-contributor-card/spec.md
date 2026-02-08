# Feature Specification: Add contributor card

**Feature Branch**: `001-contributor-card`
**Created**: 2026-02-07
**Status**: Draft
**Input**: User description: "I want to create a third card generation for contribution to external repos (not a user ones). I should show top X (default 10) repositories on which user contributed based on score (stars amount). The example of the layout is https://github.com/stn1slv/stn1slv/blob/main/img/github-contributor-dark.svg"

## Clarifications

### Session 2026-02-07
- Q: How should the system identify which repositories a user has "contributed to"? → A: Option A - Standard (All types): Includes Commits, Pull Requests, Issues, and Reviews (matches GitHub profile).
- Q: Besides the repository name, should the card display any other information about the user's specific contribution to that repository? → A: Use existing calculate_rank function to show user's rank level for that repository.
- Q: Should the card include contributions to private repositories if the provided GITHUB_TOKEN has access to them? → A: Option A - Public Only: Filter for contributions to public repositories only.
- Q: Should the system include repositories owned by organizations that the user is a member of? → A: Option A - Include All: Include any repository not owned by the user personally (including user's orgs).
- Q: What should be the default title displayed at the top of the contributor card? → A: Option A - "Top Contributions"
- Q: Where should the "repository favicon" be sourced from? → A: Option A - Owner Avatar: Use the repository owner's (User/Org) avatar image.
- Q: How should the owner avatar be styled within the repository list? → A: Option A - Circular: Rounded into a circle.
- Q: Where should the owner avatar be placed relative to the repository name? → A: Option A - Left of name: Avatar icon appears to the left of the repository name.
- Q: How should the repository name be displayed? → A: Repository name only, without owner/organization prefix.
- Q: What should be the dimensions of the circular owner avatar? → A: Option A - 20px x 20px (Standard small icon)
- Q: How should the repository owner avatars be included in the SVG? → A: Option A - Embedded Base64: Download the avatar and embed it directly in the SVG as a data URI.
- Q: Should we impose a hard limit on how many avatars we attempt to download? → A: Option A - No Limit: Fetch avatars for all repositories up to the user-defined --limit.
- Q: What should the system do if it fails to download the owner avatar for a specific repository? → A: Option A - Placeholder: Use a generic SVG icon placeholder for that repository.
- Q: What should be the default width for the contributor card? → A: Option A - 467px (Matches standard stats card width).
- Q: What should be the fixed height for each repository row in the list? → A: Option B - 35px (Spacious)
- Q: How should repository exclusion work? → A: Support wildcard (*) patterns and case-insensitive matching. If no owner is specified (e.g., "awesome-*"), match against repository name only.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Generate Basic Contributor Card (Priority: P1)

As a GitHub user, I want to generate a card showing the most popular repositories I've contributed to, so that I can showcase my impact on the open-source community.

**Why this priority**: Core functionality requested.

**Independent Test**: Verify the card is generated with default settings.
- Example Command: `uv run github-stats-card contrib -u <username> -o contrib.svg`

**Acceptance Scenarios**:

1. **Given** a valid GitHub username and token, **When** `uv run github-stats-card contrib -u <username> -o contrib.svg`, **Then** a file `contrib.svg` is created containing a list of repositories (displaying repository name only, without owner) not owned by the user, sorted by star count, and displaying the user's rank level for each.
2. **Given** an invalid token, **When** the command is run, **Then** an authentication error is displayed.

---

### User Story 2 - Customize Repository Count (Priority: P2)

As a user, I want to specify how many repositories to display, so that I can fit the card into my profile layout constraints.

**Independent Test**: Verify the limit flag works.
- Example Command: `uv run github-stats-card contrib -u <username> -o contrib.svg --limit 5`

**Acceptance Scenarios**:

1. **Given** a limit of 5, **When** `uv run github-stats-card contrib ... --limit 5`, **Then** the generated SVG contains exactly 5 repository entries (if available).

---

### User Story 3 - Apply Visual Themes (Priority: P2)

As a user, I want to apply existing themes to the contributor card, so that it matches my other stats cards.

**Independent Test**: Verify theming.
- Example Command: `uv run github-stats-card contrib -u <username> -o contrib.svg --theme vue-dark`

**Acceptance Scenarios**:

1. **Given** a theme name, **When** `uv run github-stats-card contrib ... --theme vue-dark`, **Then** the SVG uses the colors defined in the `vue-dark` theme.

---

### User Story 4 - Handle Edge Cases (Priority: P3)

As a user, I want clear feedback if I have no contributions or if I request more items than available, so that I understand the output.

**Independent Test**: Run with a user who has no external contributions.
- Example Command: `uv run github-stats-card contrib -u <new_user> ...`

**Acceptance Scenarios**:

1. **Given** a user with 0 external contributions, **When** the command is run, **Then** the SVG displays a friendly "No contributions found" message (or empty list) instead of crashing.
2. **Given** a limit of 100 but only 5 contributions exist, **When** command runs, **Then** it displays the 5 available repos without error.

## Requirements *(mandatory)*

### CLI Interface Design
- **Command**: `github-stats-card contrib` (New subcommand)
- **New Flags/Options**:
  - `--limit` / `-l`: Number of repositories to display (Default: 10)
  - Standard options: `--username`, `--token`, `--output`, `--theme`, `--hide-border`, `--disable-animations`, `--card-width`, etc.
  - Optional exclusion: `--exclude-repo` to manually hide specific repos.

### Configuration Changes
- **Dataclass**: Create `ContribCardConfig` in `src/core/config.py` (or similar).
- **New Fields**:
  - `limit`: int
  - `exclude_repo`: list[str]

### Functional Requirements
- **FR-001**: System MUST fetch repositories where the user is a contributor (including Commits, Pull Requests, Issues, and Reviews) across the last 5 years using `contributionsCollection`.
- **FR-002**: System MUST filter out repositories owned by the user.
- **FR-003**: System MUST filter for public repositories only.
- **FR-004**: System MUST sort the filtered repositories by star count (descending).
- **FR-005**: System MUST limit the result to the top X repositories specified by the user (default 10).
- **FR-006**: System MUST render the list of repositories as an SVG.
- **FR-007**: The SVG MUST display the repository name (without owner prefix) and the user's calculated rank level for that repository.
- **FR-008**: The default card title MUST be "Top Contributions".
- **FR-009**: System MUST fetch and display the repository owner's avatar as a visual indicator for each repository.
- **FR-010**: Avatars MUST be embedded directly in the SVG as Base64-encoded Data URIs to ensure self-contained rendering.
- **FR-011**: System MUST use a generic placeholder icon if an owner avatar fails to download.
- **FR-012**: Repository exclusion MUST support wildcard (*) matching and owner-omitted matching (e.g., "awesome-*" matches any repo starting with "awesome-" regardless of owner). Matching MUST be case-insensitive.

### Visual/Output Requirements
- **VR-001**: SVG MUST match the visual style (fonts, padding, border radius) of existing cards, with a default width of 467px.
- **VR-002**: Colors MUST respect the active theme.
- **VR-003**: Layout MUST accommodate the list of repositories cleanly, using a standard row height of 35px (e.g., rows with owner avatar on the left, followed by repo name, and user rank level inside a circle on the right).
- **VR-004**: Owner avatars MUST be rendered as circular images with dimensions of 20px x 20px.

## Success Criteria *(mandatory)*

### Measurable Outcomes
- **SC-001**: Command generates a valid SVG file in under 5 seconds for a typical user.
- **SC-002**: The output SVG passes standard XML validation.
- **SC-003**: Top 10 repositories are correctly identified and sorted by stars in 100% of test cases.

# Feature Specification: Filter Contribution Types for Contributor Card

**Feature Branch**: `003-filter-contrib-types`  
**Created**: 2026-03-22  
**Status**: Completed  
**Input**: User description: "Here is the updated feature request, including the requirement for it to be configurable via GitHub Actions: *** ### Title: Feature Request: Add optional flag to filter contribution types for Contributor Card **Is your feature request related to a problem? Please describe.** Currently, the `contrib` card automatically fetches and aggregates data across all four available GitHub contribution types: Commits, Pull Requests, Issues, and Code Reviews. While this provides a great overview, some users might want to highlight specific types of contributions. For example, a user might only want to showcase repositories where they have contributed actual code (Commits/PRs) rather than repositories where they have only opened issues or done reviews. **Describe the solution you'd like** I would like an optional configuration parameter added to the Contributor Card to specify exactly which types of contributions should be taken into account when fetching and ranking repositories. This needs to be available both in the local CLI and when running the tool via GitHub Actions. The supported types should map to the GitHub GraphQL API: 1. `commits` (`commitContributionsByRepository`) 2. `prs` (`pullRequestContributionsByRepository`) 3. `issues` (`issueContributionsByRepository`) 4. `reviews` (`pullRequestReviewContributionsByRepository`) **Proposed Implementation Details:** 1. **CLI Flag**: Add a `--types` or `--contrib-types` flag to the `contrib` command that accepts a comma-separated list of types. *Example:* `uv run github-stats-card contrib -u <username> --types commits,prs` 2. **GitHub Actions Input**: Add a new input parameter (e.g., `contrib-types`) to `action.yml` so users can configure this behavior in their CI/CD workflows. *Example yaml:* ```yaml with: contrib-types: 'commits,prs' ``` 3. **Configuration (`ContribFetchConfig`)**: Add a new parameter `contribution_types: list[str]` which defaults to all four types (`["commits", "prs", "issues", "reviews"]`) to maintain backward compatibility. 4. **Fetching Logic (`src/github/fetcher.py`)**: Update `_async_process_year_contributions` to conditionally include or skip the GraphQL queries for the contribution types based on the provided configuration. **Describe alternatives you've considered** Currently, the only way to filter out certain repositories is by using the `--exclude-repo` flag, but this is a manual, repository-by-repository approach rather than a behavior-based filter. **Additional context** Default behavior should remain unchanged (all types enabled). By allowing users to opt-in to specific contribution types, the tool becomes much more flexible for different types of profiles (e.g., highlighting open-source code contributions vs. community management/issue triage) across both local generation and automated profile README updates."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Filter to Specific Contribution Types via CLI (Priority: P1)

As a user generating a contributor card via the CLI, I want to specify which types of contributions to consider (e.g., only commits and pull requests) so that my generated card highlights only my active code contributions rather than code reviews or issues.

**Why this priority**: Filtering contribution types is the core feature requested to allow users to showcase specific kinds of work.

**Independent Test**: Verify the generated output only includes repositories where the user has the specified contribution types.
- Example Command: `uv run github-stats-card contrib -u <username> --types commits,prs -o contrib.svg`

**Acceptance Scenarios**:

1. **Given** a valid username, **When** `uv run github-stats-card contrib -u <username> --types commits,prs`, **Then** the file is generated, and the underlying data fetch only queries for commits and pull requests.
2. **Given** an invalid type in the types flag, **When** `uv run github-stats-card contrib -u <username> --types invalid`, **Then** the CLI should fail with an appropriate error message indicating invalid contribution types.

---

### User Story 2 - Filter Contributions via Automation (Priority: P1)

As a user running the stats card generation in an automated workflow (e.g., GitHub Actions), I want to configure the contribution types via inputs so that my profile is automatically updated with my filtered contribution data.

**Why this priority**: Automation support was explicitly requested and is the primary way many users generate these cards for their profiles.

**Independent Test**: Verify the workflow definition accepts the new input and passes it correctly.

**Acceptance Scenarios**:

1. **Given** an automated workflow specifying `contrib-types: 'commits,prs'`, **When** the workflow runs, **Then** the internal generation call includes the correct filter.
2. **Given** an automated workflow specifying `contrib-types`, **When** the workflow builds the generation command, **Then** it passes the value using the `--contrib-types` spelling, and that spelling is accepted as equivalent to `--types`.

---

### User Story 3 - Filtering Survives Incomplete Provider Responses (Priority: P2)

As a user whose contribution history spans repositories the provider cannot fully resolve (deleted repositories, organisations behind SSO, restricted nodes), I want the card to still reflect the contributions the provider did return, so that a single unresolvable entry does not blank out an entire year of my history.

**Why this priority**: Discovered after release. Without it, users with any restricted organisation in their history silently lose whole years of contributions.

**Independent Test**: Supply a provider response containing field-level errors alongside valid contribution data and verify the valid entries are still counted.

**Acceptance Scenarios**:

1. **Given** a provider response carrying field-level errors together with valid contribution data, **When** the contributor card is generated, **Then** the valid contributions are counted rather than the whole response being discarded.
2. **Given** a partial response in which some pull request entries are missing or empty, **When** `prs` is among the selected types, **Then** those entries are skipped and the remaining `OPEN`/`MERGED` pull requests are still counted.

## Requirements *(mandatory)*

### CLI Interface Design
- **Command**: `github-stats-card contrib`
- **New Flags/Options**:
  - `--types`: Comma-separated list of contribution types to include. Allowed values: `commits`, `prs`, `issues`, `reviews`. (Default: `commits,prs`)

### Configuration Changes
- **Dataclass**: `ContribFetchConfig`
- **New Fields**:
  - `contribution_types: list[str]` - Types of contributions to fetch

### Functional Requirements
- **FR-001**: System MUST parse the comma-separated `--types` flag into a list, validating against the allowed values (`commits`, `prs`, `issues`, `reviews`).
- **FR-002**: System MUST default to including `commits` and `prs` if the flag is omitted, prioritizing core code contributions.
- **FR-003**: System MUST update the data fetching process to only request data for the specified contribution types, ignoring the others.
- **FR-004**: System MUST expose a new `contrib-types` input parameter in the automation definition (`action.yml`).
- **FR-005**: When `prs` are selected, the system MUST only count Pull Requests that are in `OPEN` or `MERGED` state, excluding `CLOSED` (unmerged) pull requests.
- **FR-006**: The automation definition MUST forward its configured types using an option spelling the CLI accepts; both `--types` and `--contrib-types` MUST remain valid spellings of the same option.
- **FR-007**: When the provider returns field-level errors alongside a usable partial payload, the system MUST process the contributions present in that payload instead of discarding the response, and MUST skip missing or empty entries rather than counting them.
- **FR-008**: The CLI MUST make the default value of the types option discoverable from its own help output.

### Visual/Output Requirements
- **VR-001**: The rendered image MUST NOT change its visual layout; only the underlying data populating the repositories will change based on the filter.

### Assumptions & Dependencies
- **Assumptions**: 
  - The available contribution types from the provider API remain consistent (`commits`, `prs`, `issues`, `reviews`).
  - Filtering PRs by state is performed by fetching up to 100 pull requests per repository per year and counting those matching the required states. A repository with more than 100 pull requests by the user in a single year is undercounted; this is accepted.
  - Provider responses may be partial. Field-level errors are expected in normal operation and do not invalidate the data returned alongside them.
- **Dependencies**: The automation workflow (`action.yml`) maps directly to the CLI options. It uses the `--contrib-types` spelling, so that alias is a released contract and not an internal convenience.

## Success Criteria *(mandatory)*

### Measurable Outcomes
- **SC-001**: Users can successfully limit fetched repositories to those matching specific contribution types without the visual layout breaking.
- **SC-002**: The automation workflow successfully accepts the new configuration parameter and passes it to the generation process.
- **SC-003**: Omitting the new configuration falls back to the default behavior (fetching `commits` and `prs`).
- **SC-004**: Providing an invalid type results in a clear validation error before any data fetching begins.
- **SC-005**: Generated contributor cards for `prs` exclude counts for closed, unmerged pull requests.
- **SC-006**: A provider response carrying field-level errors alongside valid data still yields the contributions contained in that data.
- **SC-007**: A user reading the CLI help output can determine the default set of contribution types without consulting external documentation.
- **SC-008**: The option spelling used by the automation definition is exercised by the test suite, so it cannot regress unnoticed.

### Revision: Implementation Sync 2026-03-22
- Reason: The default value for `--types` flag was changed from including all four types to `commits,prs` to prioritize core code contributions and reduce noise.
- Reason: Added requirement to filter PR contributions by state (only OPEN/MERGED counted).
- Reason: Synchronized GitHub Actions input name (`contrib-types`) and documentation across all artifacts.

### Revision: Implementation Sync 2026-08-09
- Reason: Full audit of the shipped implementation against all feature artifacts ("check all").
- Reason: The automation definition invokes the CLI through the `--contrib-types` alias rather than `--types`, making that alias a released contract; it was undocumented as such and untested. Captured as FR-006, SC-008 and User Story 2 scenario 2.
- Reason: Post-release work (PR #14, 2026-07-24) changed the contribution parsing this feature owns so that partial provider responses are processed rather than discarded. Captured as User Story 3, FR-007 and SC-006.
- Reason: The CLI help output does not reveal the `commits,prs` default, leaving FR-002 undiscoverable to CLI users. Captured as FR-008 and SC-007.
- Reason: Recorded the 100-pull-request-per-repository-per-year ceiling as an accepted limitation rather than an unstated one.

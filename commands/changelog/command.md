---
description: "Generate a changelog grouped by intent from git history. Reads commits since the last tag, classifies by purpose, and outputs Keep a Changelog format."
---

# Changelog Command

Generate release notes by synthesizing commit intent, not just listing commits.

## Instructions

### Step 1: Find the Baseline

Determine the starting point for the changelog:

```bash
LAST_TAG=$(git describe --tags --abbrev=0 2>/dev/null)
echo "Last tag: ${LAST_TAG:-none}"
```

If a tag exists, use it as the baseline. If no tags exist, fall back to the last 50 commits. If $ARGUMENTS specifies a tag, range, or count, use that instead.

```bash
# Since last tag
git log "$LAST_TAG"..HEAD --oneline --no-merges

# Or: last N commits
git log --oneline --no-merges -50
```

### Step 2: Analyze Each Commit

For each commit, read both the message and the diff to understand what actually changed:

```bash
git log <range> --format="%H %s" --no-merges
```

When the message is unclear, inspect the diff:

```bash
git show <hash> --stat
git show <hash> -- <relevant files>
```

Classify each commit into one of these categories based on the combination of message and diff:
- **Added** - new features, capabilities, endpoints, commands
- **Changed** - modifications to existing behavior, refactors that alter output
- **Fixed** - bug fixes, error handling corrections, regression fixes
- **Removed** - removed features, deprecated code cleanup
- **Security** - vulnerability patches, dependency security updates
- **Breaking Changes** - renamed functions, changed signatures, removed public APIs, changed config formats

### Step 3: Synthesize and Group

Do NOT list one line per commit. Instead:
1. Group related commits that serve the same purpose into a single entry
2. Write each entry from the user's perspective (what changed for them), not the developer's (what files were touched)
3. If 5 commits all fix the same feature, that is one changelog entry, not 5

### Step 4: Format as Keep a Changelog

```
## [Unreleased] - YYYY-MM-DD

### Added
- Description of new feature from user's perspective
- Another new capability

### Changed
- What existing behavior is different now

### Fixed
- What bug was fixed and what the symptom was

### Removed
- What was removed

### Security
- What vulnerability was addressed

### Breaking Changes
- What breaks and what users need to do about it
```

Omit any section that has no entries. If a tag was found, note the range in the header.

### Step 5: Offer Follow-ups

After presenting the changelog, ask:
- "Want me to write this to a CHANGELOG.md file?"
- "Want me to adjust the level of detail?"
- "Want me to generate this for a different range?"

## Important

- Synthesize intent from diffs, not just commit messages. A message "fix typo" might actually fix a logic bug.
- Group by purpose, not by commit. Three commits fixing the same feature = one entry.
- Write from the user's perspective. "Added CSV export to reports" not "Added csv_export() to report_generator.py".
- Skip merge commits and test-only changes (unless they reveal new behavior).
- If a commit touches only CI config, group those under a "CI/Infrastructure" note at the end.

## Arguments

$ARGUMENTS can be:
- Empty (default: changes since last tag, or last 50 commits if no tags)
- A tag: `/changelog v1.2.0` (changes since that tag)
- A range: `/changelog v1.0.0..v1.2.0` (changes between two tags)
- A count: `/changelog 20` (last 20 commits)

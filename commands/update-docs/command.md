---
description: "Find and update stale documentation after code changes. Scans all doc files in the focused repo, matches against the diff, and proposes targeted updates for review."
---

# Update Docs Command

Use the Skill tool to invoke `update-docs`. The skill handles the full process: diffing against the default branch, discovering all documentation files, matching changed identifiers against doc content, evaluating candidates, and drafting targeted updates.

If the Skill tool is not available or the skill is not found, follow the process defined in `skills/update-docs/SKILL.md` directly.

Present all proposed changes for user review before applying. Do not commit automatically.

## Arguments

$ARGUMENTS can be:
- Empty (default: check all docs against current branch diff)
- A file path: `/update-docs README.md` (check only that specific doc file)

#!/usr/bin/env bash
# PreToolUse hook: warn when a git commit has a large staged diff.
# Advisory only — always exits 0.

THRESHOLD=500

CMD=$(echo "$CLAUDE_TOOL_INPUT" | grep -oP '"command"\s*:\s*"\K[^"]+' 2>/dev/null)
[ -z "$CMD" ] && exit 0

# Only care about git commit commands
echo "$CMD" | grep -qiE "git commit" || exit 0

# Skip amend commits (reworking existing commits, not adding new bulk)
echo "$CMD" | grep -qiE "\-\-amend" && exit 0

# Count staged diff lines (additions + deletions)
STAT=$(git diff --cached --stat 2>/dev/null | tail -1)
[ -z "$STAT" ] && exit 0

INSERTIONS=$(echo "$STAT" | grep -oP '\d+(?= insertion)' || echo 0)
DELETIONS=$(echo "$STAT" | grep -oP '\d+(?= deletion)' || echo 0)
TOTAL=$((${INSERTIONS:-0} + ${DELETIONS:-0}))

if [ "$TOTAL" -gt "$THRESHOLD" ]; then
  echo "Large commit: $TOTAL changed lines (threshold: $THRESHOLD)."
  echo "Consider splitting into smaller, focused commits:"
  echo "  - Use 'git add -p' to stage related changes separately"
  echo "  - Group by logical unit: one commit per feature, fix, or refactor"
fi

exit 0

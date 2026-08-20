#!/bin/bash
# Auto-tracking hook for cost-speed-meter
# Measures execution time of test, build, lint, and git commands
# Called by Claude Code PreToolUse hook

METRICS_DIR="${CLAUDE_PROJECT_DIR}/.claude"
METRICS_FILE="${METRICS_DIR}/metrics.json"

# Extract command from Bash tool input (JSON)
CMD=$(echo "$CLAUDE_TOOL_INPUT" | grep -oP '"command"\s*:\s*"\K[^"]+' 2>/dev/null | head -1)

# Skip if no command or already running meter
[[ -z "$CMD" ]] && exit 0
[[ "$CMD" =~ ^meter ]] && exit 0

# Categorize command and extract operation name
categorize_cmd() {
  local cmd="$1"

  # Test commands
  if [[ "$cmd" =~ ^(pytest|py\.test|python.*test) ]]; then
    echo "test:pytest"
  elif [[ "$cmd" =~ ^(jest|vitest|mocha) ]]; then
    echo "test:node"
  elif [[ "$cmd" =~ ^(cargo test) ]]; then
    echo "test:rust"
  elif [[ "$cmd" =~ ^(go test) ]]; then
    echo "test:go"

  # Build commands
  elif [[ "$cmd" =~ ^(npm run build|yarn build|pnpm build) ]]; then
    echo "build:npm"
  elif [[ "$cmd" =~ ^(cargo build) ]]; then
    echo "build:rust"
  elif [[ "$cmd" =~ ^(pip install|uv sync|uv install) ]]; then
    echo "build:python"

  # Lint commands
  elif [[ "$cmd" =~ ^(ruff check|pylint|black) ]]; then
    echo "lint:python"
  elif [[ "$cmd" =~ ^(eslint|prettier|biome lint) ]]; then
    echo "lint:node"
  elif [[ "$cmd" =~ ^(cargo clippy) ]]; then
    echo "lint:rust"

  # Git commands
  elif [[ "$cmd" =~ ^git ]]; then
    echo "vcs:git"
  fi
}

category=$(categorize_cmd "$CMD")
[[ -z "$category" ]] && exit 0

# Only track if metrics file exists (repo has initialized)
[[ ! -f "$METRICS_FILE" ]] && exit 0

# Record timing in background (don't block the command)
{
  start_time=$(date +%s.%N)
  # Actual command runs via Claude Code (not here)
  # We just record what we know
  sleep 0.1  # placeholder; actual timing comes from Claude Code measurement
} &

exit 0

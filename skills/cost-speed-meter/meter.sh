#!/bin/bash
# cost-speed-meter — track command execution times across sessions
# Usage: meter [init|report|slowest|recommend|show-metrics]

set -e

METRICS_FILE="${PWD}/.claude/metrics.json"
METER_BIN="${METER_BIN:-meter}"

# Initialize metrics for a repo
init_metrics() {
  local repo_name=$(basename "$PWD")
  mkdir -p .claude

  if [[ -f "$METRICS_FILE" ]]; then
    echo "Metrics already initialized for: $repo_name"
    return 0
  fi

  cat > "$METRICS_FILE" <<EOF
{
  "repo": "$repo_name",
  "timestamp": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
  "operations": [],
  "slowest_op": null,
  "recommendations": []
}
EOF
  echo "Initialized metrics for: $repo_name"
}

# Record a command execution time
record_time() {
  local cmd_name="$1"
  local duration_seconds="$2"
  local category="${3:-custom}"

  [[ ! -f "$METRICS_FILE" ]] && init_metrics

  # Read current metrics, update, write back
  python3 << PYTHON
import json
import os
from datetime import datetime, timedelta

metrics_file = "$METRICS_FILE"
with open(metrics_file, 'r') as f:
  data = json.load(f)

now = datetime.utcnow().isoformat() + 'Z'
week_ago = (datetime.utcnow() - timedelta(days=7)).isoformat() + 'Z'

# Find or create operation
op = next((o for o in data['operations'] if o['name'] == "$cmd_name"), None)
if not op:
  op = {
    'name': "$cmd_name",
    'category': "$category",
    'last_run_seconds': 0,
    'run_count_7d': 0,
    'avg_7d': 0,
    'trend_7d': '0s',
    'last_run_time': now
  }
  data['operations'].append(op)

# Update metrics
old_avg = op.get('avg_7d', 0)
op['last_run_seconds'] = $duration_seconds
op['run_count_7d'] = op.get('run_count_7d', 0) + 1
op['last_run_time'] = now
new_avg = (old_avg * (op['run_count_7d'] - 1) + $duration_seconds) / op['run_count_7d']
op['avg_7d'] = round(new_avg, 1)
op['trend_7d'] = f"{$duration_seconds - old_avg:+.1f}s"

# Update slowest
slowest = max(data['operations'], key=lambda x: x['last_run_seconds'], default=None)
if slowest:
  data['slowest_op'] = {
    'name': slowest['name'],
    'seconds': slowest['last_run_seconds']
  }

data['timestamp'] = now
with open(metrics_file, 'w') as f:
  json.dump(data, f, indent=2)

print(f"Recorded: {cmd_name} = {$duration_seconds}s")
PYTHON
}

# Show metrics for current session
show_current() {
  [[ ! -f "$METRICS_FILE" ]] && { echo "No metrics yet. Run commands first."; return; }

  python3 << 'PYTHON'
import json
import os

metrics_file = os.environ.get('METRICS_FILE')
with open(metrics_file, 'r') as f:
  data = json.load(f)

if not data['operations']:
  print("No operations tracked yet.")
  return

print("\n=== CURRENT METRICS ===")
print(f"Repo: {data['repo']}\n")

# Sort by last run time
ops = sorted(data['operations'], key=lambda x: x.get('last_run_seconds', 0), reverse=True)
for op in ops:
  name = op['name']
  seconds = op['last_run_seconds']
  trend = op.get('trend_7d', '0s')
  print(f"  {name:20} {seconds:6.1f}s  (trend: {trend})")

if data['slowest_op']:
  print(f"\nSlowest: {data['slowest_op']['name']} ({data['slowest_op']['seconds']:.1f}s)")

if data['recommendations']:
  print("\nRecommendations:")
  for rec in data['recommendations']:
    print(f"  • {rec}")
PYTHON
}

# Weekly summary
weekly_report() {
  [[ ! -f "$METRICS_FILE" ]] && { echo "No metrics yet."; return; }

  python3 << 'PYTHON'
import json
import os

metrics_file = os.environ.get('METRICS_FILE')
with open(metrics_file, 'r') as f:
  data = json.load(f)

print("\n=== 7-DAY SUMMARY ===")
print(f"Repo: {data['repo']}\n")

ops = sorted(data['operations'], key=lambda x: x.get('avg_7d', 0), reverse=True)
for op in ops:
  name = op['name']
  avg = op.get('avg_7d', 0)
  count = op.get('run_count_7d', 0)
  trend = op.get('trend_7d', '0s')
  if count > 0:
    pct_change = ((float(trend.rstrip('s')) / avg * 100) if avg > 0 else 0)
    print(f"  {name:20} avg {avg:6.1f}s ({count} runs, trend: {trend:+} {pct_change:+.1f}%)")
PYTHON
}

# Main dispatcher
case "${1:-show}" in
  init)
    init_metrics
    ;;
  show|status)
    show_current
    ;;
  report)
    weekly_report
    ;;
  record)
    record_time "$2" "$3" "${4:-custom}"
    ;;
  *)
    echo "Usage: $0 {init|show|report|record <name> <seconds>}"
    exit 1
    ;;
esac

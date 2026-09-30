#!/usr/bin/env python3
"""
Create a unique task directory under .tmp/ for organizing temporary files.

Usage:
    uv run .ai-workspace/scripts/mktmpdir.py [name]

Arguments:
    name    Optional directory name (e.g., JIRA-123).
            If provided, creates .tmp/{name}/ and reuses if it exists.
            If omitted, generates .tmp/YYYYMMDD-xxxx/ (date + random hex).

Cross-platform: works on Windows, macOS, and Linux.
"""

import argparse
import datetime
import secrets
import sys
from pathlib import Path


def main() -> None:
    """Create unique task directory and print its path."""
    parser = argparse.ArgumentParser(description="Create a task directory under .tmp/")
    parser.add_argument(
        "name",
        nargs="?",
        help="Directory name (e.g., JIRA-123). If omitted, generates a random name.",
    )
    args = parser.parse_args()

    # Scripts are in .ai-workspace/scripts/, so go up two levels
    base_dir = Path(__file__).parent.parent.parent
    tmp_dir = base_dir / ".tmp"

    if args.name:
        # Named directory: create or reuse existing
        task_dir = tmp_dir / args.name
        created = not task_dir.exists()
        task_dir.mkdir(parents=True, exist_ok=True)
    else:
        # Random directory: generate unique name with date prefix
        date_str = datetime.date.today().strftime("%Y%m%d")
        while True:
            random_suffix = secrets.token_hex(2)  # 4 hex chars
            task_dir = tmp_dir / f"{date_str}-{random_suffix}"
            try:
                task_dir.mkdir(parents=True, exist_ok=False)
                break
            except FileExistsError:
                continue
        created = True

    relative_path = task_dir.relative_to(base_dir).as_posix()
    action = "Created" if created else "Using existing"
    # Status goes to stderr so that `$(mktmpdir.py)` captures the path alone.
    # Emitting the prose on stdout made callers create directories literally
    # named "Created task directory: .tmp/...".
    print(f"{action} task directory: {relative_path}", file=sys.stderr)
    print(relative_path)


if __name__ == "__main__":
    main()

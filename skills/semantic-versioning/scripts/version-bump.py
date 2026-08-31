#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# ///
"""Analyze commits since last tag and suggest the next semantic version.

Usage:
  uv run version-bump.py [repo-path]   Show recommended version bump
  uv run version-bump.py --apply       Update version file (with confirmation)
  uv run version-bump.py --tag         Also create a git tag after applying

Exit codes:
  0 - Success (version info printed)
  1 - No commits to analyze
"""

from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

CONVENTIONAL_RE = re.compile(
    r"^(?P<type>feat|feature|fix|chore|docs|style|refactor|test|ci|perf|build|revert)"
    r"(?:\([^)]*\))?"
    r"(?P<breaking>!)?"
    r":\s*(?P<desc>.+)$",
    re.IGNORECASE,
)

MAJOR_KEYWORDS = re.compile(r"\b(breaking|removed?|dropped?|rename\s+api)\b", re.IGNORECASE)
MINOR_KEYWORDS = re.compile(r"\b(add|new|feature|implement)\b", re.IGNORECASE)

VERSION_FILES = [
    ("pyproject.toml", re.compile(r'(version\s*=\s*")(\d+\.\d+\.\d+)(")')),
    ("package.json", re.compile(r'("version"\s*:\s*")(\d+\.\d+\.\d+)(")')),
    ("Cargo.toml", re.compile(r'(version\s*=\s*")(\d+\.\d+\.\d+)(")')),
    ("VERSION", re.compile(r"^(\d+\.\d+\.\d+)$", re.MULTILINE)),
]


def git(*args: str, cwd: Path | None = None) -> str:
    result = subprocess.run(["git", *args], capture_output=True, text=True, cwd=cwd)
    return result.stdout.strip()


def get_last_tag(cwd: Path) -> str | None:
    tag = git("describe", "--tags", "--abbrev=0", cwd=cwd)
    return tag if tag else None


def get_commits_since(tag: str | None, cwd: Path) -> list[str]:
    cmd = ["log", "--oneline", "--format=%s"]
    if tag:
        cmd.append(f"{tag}..HEAD")
    output = git(*cmd, cwd=cwd)
    return output.split("\n") if output else []


def parse_version(tag: str | None) -> tuple[int, int, int]:
    match = re.match(r"v?(\d+)\.(\d+)\.(\d+)", tag or "0.0.0")
    if not match:
        return (0, 0, 0)
    return (int(match.group(1)), int(match.group(2)), int(match.group(3)))


def classify_commit(msg: str) -> str:
    m = CONVENTIONAL_RE.match(msg)
    if m:
        if m.group("breaking") or "BREAKING CHANGE" in msg.upper():
            return "major"
        if m.group("type").lower() in ("feat", "feature"):
            return "minor"
        return "patch"

    if MAJOR_KEYWORDS.search(msg):
        return "major"
    if MINOR_KEYWORDS.search(msg):
        return "minor"
    return "patch"


def highest_bump(classifications: list[str]) -> str:
    if "major" in classifications:
        return "major"
    if "minor" in classifications:
        return "minor"
    return "patch"


def next_version(current: tuple[int, int, int], bump: str) -> str:
    major, minor, patch = current
    if bump == "major":
        if major == 0:
            return f"0.{minor + 1}.0"
        return f"{major + 1}.0.0"
    if bump == "minor":
        return f"{major}.{minor + 1}.0"
    return f"{major}.{minor}.{patch + 1}"


def find_version_file(cwd: Path) -> tuple[Path, re.Pattern[str]] | None:
    for filename, pattern in VERSION_FILES:
        path = cwd / filename
        if path.is_file():
            content = path.read_text()
            if pattern.search(content):
                return path, pattern
    return None


def update_version_file(path: Path, pattern: re.Pattern[str], new_version: str) -> None:
    content = path.read_text()
    if path.name == "VERSION":
        updated = pattern.sub(new_version, content)
    else:
        updated = pattern.sub(rf"\g<1>{new_version}\g<3>", content)
    path.write_text(updated)


def main() -> None:
    args = sys.argv[1:]
    apply_flag = "--apply" in args
    tag_flag = "--tag" in args
    repo_args = [a for a in args if not a.startswith("--")]
    cwd = Path(repo_args[0]).resolve() if repo_args else Path.cwd()

    last_tag = get_last_tag(cwd)
    commits = get_commits_since(last_tag, cwd)

    if not commits:
        print("No commits since last tag. No version bump needed.")
        sys.exit(1)

    classifications = [classify_commit(msg) for msg in commits]
    bump = highest_bump(classifications)
    current = parse_version(last_tag)
    new_ver = next_version(current, bump)

    print(f"Current version: {last_tag or '0.0.0 (no tags)'}")
    print(f"Commits analyzed: {len(commits)}")
    print(f"Recommended bump: {bump}")
    print(f"Next version: v{new_ver}")
    print()

    counts = {"major": 0, "minor": 0, "patch": 0}
    for msg, cls in zip(commits, classifications):
        counts[cls] += 1
        print(f"  [{cls:5s}] {msg}")

    print(f"\nBreakdown: {counts['major']} major, {counts['minor']} minor, {counts['patch']} patch")

    if apply_flag:
        vf = find_version_file(cwd)
        if vf:
            path, pattern = vf
            update_version_file(path, pattern, new_ver)
            print(f"\nUpdated {path.name} to {new_ver}")
        else:
            print("\nNo version file found to update.")

        if tag_flag:
            git("tag", f"v{new_ver}", cwd=cwd)
            print(f"Created tag v{new_ver}")

    result = {
        "current": last_tag or "0.0.0",
        "next": f"v{new_ver}",
        "bump": bump,
        "commits": len(commits),
        "breakdown": counts,
    }
    print(f"\n{json.dumps(result)}")


if __name__ == "__main__":
    main()

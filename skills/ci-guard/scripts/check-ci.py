#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# ///
"""Check if a repository has CI configuration.

Exit codes:
  0 - CI found or repo is research-exempt
  1 - No CI configuration found
"""

from __future__ import annotations

import sys
from pathlib import Path

CI_INDICATORS = [
    (".github/workflows", True),  # (path, is_directory)
    (".gitlab-ci.yml", False),
    (".circleci/config.yml", False),
    ("Jenkinsfile", False),
    (".travis.yml", False),
    ("azure-pipelines.yml", False),
    ("bitbucket-pipelines.yml", False),
]


def has_ci(repo_root: Path) -> str | None:
    """Return the CI provider name if found, None otherwise."""
    for indicator, is_dir in CI_INDICATORS:
        path = repo_root / indicator
        if is_dir:
            if path.is_dir() and any(path.glob("*.y*ml")):
                return indicator
        elif path.is_file():
            return indicator
    return None


def is_research(repo_root: Path) -> bool:
    """Check if the repo is marked as research-only."""
    if (repo_root / ".research").exists():
        return True
    toml = repo_root / "pyproject.toml"
    if toml.is_file():
        content = toml.read_text()
        if 'purpose = "research"' in content or "purpose = 'research'" in content:
            return True
    return False


def main() -> None:
    repo_path = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(".")
    repo_path = repo_path.resolve()

    if not repo_path.is_dir():
        print(f"ERROR: {repo_path} is not a directory", file=sys.stderr)
        sys.exit(2)

    if is_research(repo_path):
        print(f"SKIP: {repo_path.name} is marked as research — CI not required")
        sys.exit(0)

    ci = has_ci(repo_path)
    if ci:
        print(f"OK: CI found ({ci}) in {repo_path.name}")
        sys.exit(0)

    print(f"WARNING: No CI configuration found in {repo_path.name}")
    print("  Add a CI workflow or mark as research: touch .research")
    sys.exit(1)


if __name__ == "__main__":
    main()

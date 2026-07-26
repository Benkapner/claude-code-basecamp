---
description: "Audit project dependencies for unused packages, outdated versions, known vulnerabilities, and license compatibility. Language-agnostic."
---

# Dependency Check Command

Audit project dependencies for health, security, and licensing issues.

## Instructions

### Step 1: Detect Package Manifests

Scan for dependency manifests in the project:

```bash
ls package.json package-lock.json yarn.lock pnpm-lock.yaml 2>/dev/null
ls pyproject.toml requirements*.txt setup.py setup.cfg Pipfile 2>/dev/null
ls go.mod go.sum 2>/dev/null
ls Cargo.toml Cargo.lock 2>/dev/null
ls Gemfile Gemfile.lock 2>/dev/null
ls pom.xml build.gradle build.gradle.kts 2>/dev/null
```

If no manifest files are found, ask the user what package manager the project uses. For each detected manifest, read it and extract the dependency list.

### Step 2: Identify Unused Dependencies

For each declared dependency, search the codebase for actual usage:

```bash
# Python
grep -rn "import <package>" --include="*.py" . 2>/dev/null
grep -rn "from <package>" --include="*.py" . 2>/dev/null

# Node
grep -rn "require(['\"]<package>" --include="*.js" --include="*.ts" --include="*.jsx" --include="*.tsx" . 2>/dev/null
grep -rn "from ['\"]<package>" --include="*.js" --include="*.ts" --include="*.jsx" --include="*.tsx" . 2>/dev/null
```

Account for:
- Packages with different import names than their package name (e.g., `Pillow` imported as `PIL`, `python-dateutil` as `dateutil`)
- Dev dependencies used only in tooling (linters, formatters, test runners) are not "unused"
- Packages used as CLI tools rather than imported (e.g., `black`, `ruff`, `prettier`)
- Framework plugins loaded by convention, not import (e.g., pytest plugins, Django apps)

Mark findings as **LIKELY UNUSED** (high confidence, no references found) or **POSSIBLY UNUSED** (needs manual verification).

### Step 3: Check for Outdated Versions

Use the appropriate package manager:

```bash
# Python
pip list --outdated 2>/dev/null || uv pip list --outdated 2>/dev/null

# Node
npm outdated 2>/dev/null

# Go
go list -u -m all 2>/dev/null

# Rust
cargo outdated 2>/dev/null
```

If the native tool is not available, check versions manually from lock files. Classify updates:
- **Patch** (1.2.3 to 1.2.4) - usually safe
- **Minor** (1.2.3 to 1.3.0) - review changelog
- **Major** (1.2.3 to 2.0.0) - likely breaking

### Step 4: Check for Known Vulnerabilities

Use available audit tools:

```bash
# Python
pip-audit 2>/dev/null || safety check 2>/dev/null

# Node
npm audit 2>/dev/null

# Go
govulncheck ./... 2>/dev/null

# Rust
cargo audit 2>/dev/null
```

If no audit tool is installed, note which ones could be used and suggest installing them.

### Step 5: Check License Compatibility

For each dependency, identify its license:

```bash
# Python
pip show <package> 2>/dev/null | grep License

# Node
cat node_modules/<package>/package.json 2>/dev/null | grep -i license
```

Flag potential issues:
- Copyleft licenses (GPL, AGPL) in a project that appears proprietary or permissive-licensed
- Unknown or missing licenses that need manual review
- License conflicts between dependencies

### Step 6: Report

```
DEPENDENCY HEALTH REPORT
========================
Project: [name]
Manifest: [pyproject.toml / package.json / etc.]
Total dependencies: [N] (prod: [X], dev: [Y])

UNUSED DEPENDENCIES:
  LIKELY UNUSED:
    - <package>  (no imports found in source)
  POSSIBLY UNUSED:
    - <package>  (only referenced in config, verify manually)

OUTDATED:
  MAJOR updates available:
    - <package> 1.2.3 -> 2.0.0  (breaking changes likely)
  MINOR updates available:
    - <package> 1.2.3 -> 1.3.0
  PATCH updates available:
    - <package> 1.2.3 -> 1.2.5

VULNERABILITIES:
  [audit tool output, or "no audit tool available, install pip-audit / npm audit"]

LICENSE ISSUES:
  - <package>: GPL-3.0 (copyleft, verify compatibility)
  - <package>: UNKNOWN (no license metadata found)

RECOMMENDATIONS:
  1. Remove unused: [commands]
  2. Update safe patches: [commands]
  3. Review major updates: [list with changelog links]
  4. Install audit tool: [command]
```

## Important

- This is a read-only audit. Never run install or update commands without asking.
- Account for packages with different import names vs package names.
- Dev dependencies used only in tooling are not "unused" just because they are not imported in source code.
- If multiple manifest files exist (e.g., both pyproject.toml and requirements.txt), analyze all and note any discrepancies.

## Arguments

$ARGUMENTS can be:
- Empty (default: scan current project)
- A path: `/dep-check repositories/my-api` (check a specific project)
- A focus: `/dep-check --unused` (only check for unused deps)
- A focus: `/dep-check --security` (only check vulnerabilities)

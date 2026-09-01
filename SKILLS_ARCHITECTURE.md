# Skills Architecture

This document maps all skills, their purpose, activation triggers, and relationships.

## Skills Overview

### Core Verification & Review (always available)

**`verification-loop`** — Unified verification engine covering 7 phases: environment check, type check, lint, tests, code review, security scan, pre-push checks. Invoked by `/verify`, `/quality-gate`, and code-review commands. Core skill powering the entire QA workflow.

**`refactoring-patterns`** — Measurement-driven refactoring (profile → refactor → measure). Activates when user says "refactor", "clean up", "simplify", or when code has high complexity. Ensures changes improve metrics, not just code appearance.

**`update-docs`** — Detects stale documentation after code changes by matching diff against in-repo docs. Finds and updates prose that contradicts new code. Auto-activates when implementing features/fixes that rename, remove, or add APIs.

**`security-check`** — Scans for credential leaks, secrets in code, insecure patterns, LLM API key exposure, PII leakage to external services, and `.env/.gitignore` misconfigurations. Runs automatically before commits and when editing credential-related code.

### Python Development (language-specific)

**`python-patterns`** — Unified conventions for team Python development:
- **Credentials:** dotenv loading, fail-fast on missing secrets, `.env.example` patterns
- **API clients:** timeouts (30s), transient retry logic, response validation, LLM response parsing
- **Testing:** TDD workflow, mock external APIs, set `random_state=42`, 80%+ coverage
- **Pipelines:** standard stage structure, JSON metadata, validation-before-processing, fail-fast, checkpointing

Replaces separate `python-conventions` and `data-pipeline-patterns` skills (merged for clarity).

### Design & Workflow

**`brainstorming`** — Design exploration before implementation. Activates when user asks "design", "how should i build", "what's the approach", "plan this out". Proposes 2-3 approaches with trade-offs, gets approval before coding.

**`cost-speed-meter`** — Tracks command execution times (tests, builds, lint) across sessions. Shows trends, detects regressions, suggests fast-path alternatives (unit tests vs integration). Measures if optimizations actually worked.

## Skill Activation Model

| Skill | Activation Type | Trigger |
|-------|-----------------|---------|
| `verification-loop` | Command-invoked | `/verify`, `/quality-gate`, code-review commands |
| `refactoring-patterns` | Declarative | User says "refactor", "simplify", "clean up", or high complexity detected |
| `update-docs` | Declarative | Code changes APIs/configs/CLI flags; user asks "update docs" |
| `security-check` | Declarative | Editing credential/secret handling code; before commits |
| `python-patterns` | Declarative | Editing Python code files (any `.py` file in context) |
| `brainstorming` | Declarative | User explicitly asks for design, planning, or approach exploration |
| `cost-speed-meter` | Automatic | Tracks all bash command execution; invoked via `/metrics` or `/metrics-report` |

## Command Dependencies

Commands that rely on specific skills:

| Command | Requires | Notes |
|---------|----------|-------|
| `/verify` | `verification-loop` | Runs phases 1-4: environment, types, lint, tests |
| `/quality-gate` | `verification-loop` | Runs phases 1-4 + phase 6: plus pre-push security |
| `/refactor-safe` | `verification-loop`, `refactoring-patterns` | Verify code works before refactoring, then measure |
| `/test-coverage` | `verification-loop` | Part of verification loop; finds untested code |
| `/update-docs` | `update-docs` | Standalone; detects stale docs from code changes |
| `/diff-explain` | None | Standalone; explains diffs by intent |
| `/explain-code` | None | Standalone; layered explanation by complexity |
| `/prompt-test` | None | Standalone; tests LLM prompts against samples |
| `/ai-engineer-review` | None | Standalone; architectural review |
| `/changelog` | None | Standalone; generates changelog from commits |
| `/dep-check` | None | Standalone; audits dependencies |
| `/env-check` | None | Standalone; validates local dev environment |

## Removed Skills

**`redhat-writing`** — Deleted. This was user-specific (Red Hat brand voice/style). Does not belong in a generic meta-repo that others clone. Users who need it should add their own CLAUDE.md instructions locally.

**`python-conventions` (merged)** — Consolidated into `python-patterns` with `data-pipeline-patterns`. Both covered Python team conventions; one unified skill is clearer.

**`data-pipeline-patterns` (merged)** — Consolidated into `python-patterns`. Pipeline structure is a specific application of Python conventions, not separate.

## Token Budget

Always-loaded skills (loaded once per session):
- `verification-loop` — ~3KB (core engine)
- `refactoring-patterns` — ~2KB
- `security-check` — ~2KB
- `python-patterns` — ~4KB (credentials, APIs, testing, pipelines)
- `brainstorming` — ~2KB
- `cost-speed-meter` — ~4KB

**Total always-loaded: ~17KB** — under 5% of typical conversation context.

On-demand skills (load only when invoked):
- `update-docs` — ~8KB (detailed multi-step process)

## Design Rationale

1. **Merged python-conventions + data-pipeline-patterns** — Both were "team conventions for Python code." Keeping them separate created confusion about scope. One unified `python-patterns` skill is clearer and avoids redundancy.

2. **Explicit activation in ai-workspace.toml** — Skills can now be tracked as dependencies. Commands that require a skill have it documented. Future refactoring is safer.

3. **Removed redhat-writing from repo** — Generic meta-repo should not include user-specific or organization-specific content. Red Hat employees can add this locally to `~/.claude/CLAUDE.md`.

4. **Clarified brainstorming and cost-speed-meter** — Both had vague triggers ("when to activate"). Rewritten with explicit user-facing conditions (what the user asks for, not implicit context).

5. **Consolidated core verification** — Multiple commands (`/verify`, `/quality-gate`, `/refactor-safe`) all use `verification-loop`. Having them as separate commands is fine; they invoke the same skill with different phase subsets.

# Guidelines

## Verdict Rules

- Any **CRITICAL** finding → **REQUEST CHANGES** (no exceptions)
- 3+ **HIGH** findings → **REQUEST CHANGES**
- Only **MEDIUM** findings → **APPROVE** with suggestions

## Phase Requirements

- If Phase 1 (environment) fails, **STOP** and fix before proceeding
- Each phase must complete before moving to the next
- Report results per phase even if a later phase fails

## Coverage Target

- Use the project's configured coverage target when one exists.
- If no target is configured, report measured coverage and prioritize important untested behavior rather than enforcing a universal percentage.

## Escalation

- If pre-commit hooks fail, investigate the root cause — don't bypass with `--no-verify`
- If security scan finds CRITICAL issues, do not approve the push regardless of other phase results

---
name: brainstorming
description: "User asks for design, planning, or approach exploration before implementation. Covers new features, components, refactors, or architecture decisions. Creates design docs and proposes approaches with trade-offs."
---

# Brainstorming — Design Exploration

Turn ideas into fully formed designs through collaborative dialogue.

When triggered, present a design before implementation. The design scales to complexity: short (few sentences) for simple tasks, detailed (pages) for architectural changes. Always get approval before proceeding to code.

## When to Activate

- User explicitly asks: "design this", "how should i build", "what's the approach", "plan this out"
- User describes a feature/component/refactor and asks for guidance before coding
- User wants to explore trade-offs or multiple approaches to a problem

## Process

1. **Explore context** — check relevant code files, docs, recent commits
2. **Ask clarifying questions** — one at a time, prefer multiple choice, understand: purpose, constraints, success criteria, scope
3. **Propose 2-3 approaches** — name each, describe trade-offs, state your recommendation
4. **Present design** — scale to complexity (1-2 sentences for trivial, multiple sections for architecture), ask approval after each section
5. **Get approval** — wait for user buy-in before writing code

## Design Principles

- **One question at a time** — don't overwhelm
- **YAGNI ruthlessly** — remove unnecessary features
- **Design for isolation** — break into units with one purpose, well-defined interfaces, independently testable
- **Explore alternatives** — always 2-3 approaches, with trade-offs
- **Scope check** — if request spans multiple subsystems, decompose first

## In Existing Codebases

- Explore current structure and patterns before proposing changes
- Include targeted fixes only if they block the current goal
- Don't propose unrelated refactoring

## Output

Present design as prose (short or detailed based on complexity), then ask: "Does this look right?" Wait for approval before proceeding to implementation.

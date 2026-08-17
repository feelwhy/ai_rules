---
id: 16-commit-workflow
description: Commit, test, review, and push workflow
apply: agent
---

# Commit workflow

## Before committing

1. Run the **relevant tests** for the changed module(s) via Docker (`env-up … --test`, `support/devops/run_tests.sh`, or febado `scripts/test.sh`). Do not commit knowingly broken behavior.
2. `git status` / `git diff` — commit only paths belonging to this task; respect never-discard-WIP.
3. Follow the repo’s existing commit-message style (focus on why).

## Review

- Code review / Bugbot is **optional** unless the user or repo policy asks for it.
- Do not block a requested commit solely to invent a review ritual.

## Push variants

- **ai_rules / ai_rules_fao**: push when the user asks to publish rules.
- **tools / support / life / …**: push only when the user explicitly asks; prefer leaving working-tree deletions/edits for review when trimming rules.
- **febado**: follow febado push / MR rules (`febado-push-workflows`); never force-push shared branches unless explicitly requested.
- Never `--no-verify` / skip hooks unless the user explicitly requests it.

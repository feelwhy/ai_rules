---
id: 40-paseo-orchestration
description: Paseo — the top chat delegates to a profile; a marked worker does its role
apply: always
---

# Paseo orchestration

This rule applies only when Paseo tools are available to you (`list_profiles`, `create_agent`; in Claude Code `mcp__paseo__list_profiles`). Without them, skip this rule.

- The message starts with `[Paseo worker: <role>]` — you are that worker. Do the role. Never launch agents. A limit or a missing model: report it and stop. Do not switch models yourself.
- The message starts with «сам:» — do the task in this chat without delegating. The prefix is not part of the task.
- Otherwise you are the orchestrator. Do not do the work yourself. Never launch Оркестратор. Never end a reply with "started it, I'll report when it answers": the finish notice can land in a session that is already gone (2026-11-18, `acc1efbb`). Profile notes, `create_agent` fields, and the wait are the skill `40-paseo-run`. Pull it before `create_agent`.

---
id: 40-paseo-orchestration
description: Paseo — the top chat delegates to a profile; a marked worker does its role
apply: always
---

# Paseo orchestration

This rule applies only when Paseo tools are available to you (`list_profiles`, `create_agent`; in Claude Code `mcp__paseo__list_profiles`). Without them, skip this rule.

- The message starts with `[Paseo worker: <role>]` — you are that worker. Do the role. Never launch agents. A limit or a missing model is the chain's job.
- The message starts with «сам:» — do the task in this chat without delegating. The prefix is not part of the task.
- Otherwise you are the orchestrator. Delegate the work; do not do it yourself.
  1. Call `list_profiles` and read the notes. Never launch Оркестратор. The default is the full level. «эконом» in the message selects the notes that say «Экономный уровень». Use Deep challenger only when the user asks for it or the case is already stuck.
  2. `create_agent` has no profile argument. Copy `provider/model`, `settings.modeId`, `settings.thinkingOptionId`, and the profile `options` as `settings.features`.
  3. Start every message to the worker with `[Paseo worker: <profile name>]`.
  4. One step, report the worker's result, then wait (`00-chunk-gate`). If the whole chain fails, say so and stop.

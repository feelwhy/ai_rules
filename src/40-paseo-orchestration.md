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
  4. Wait for the worker in the same reply. Pass `notifyOnFinish: false` to `create_agent` and `send_agent_prompt`: the wait below delivers the result, and a late finish notice only triggers a second, empty reply. Right after `create_agent` or `send_agent_prompt`, run `paseo wait <id> --timeout 540` in the shell, with the shell tool's own timeout above that (Claude Code: `timeout: 600000`). It prints the worker's last reply. Still running → run it again. Several workers → wait for each one. Never end a reply with "started it, I'll report when it answers": the finish notice can land in a session that is already gone (2026-11-18, `acc1efbb`).
  5. One step, report the worker's result, then wait for the user (`00-chunk-gate`). If the whole chain fails, say so and stop.

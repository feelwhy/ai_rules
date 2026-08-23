---
id: 04-plan-challenge
description: Challenge plans and task framing before large or ambiguous work
apply: agent
---

# Plan / task challenging

Before a large implementation or when a plan looks thin:

1. **Restate the goal** and the smallest change that would satisfy it.
2. **Name risks**: shared-checkout serie, foreign WIP, production data, apps-store compatibility, Docker-only constraints.
3. **Point out missing gates**: tests, confirmation before delete/push/live write, which repo owns the change.
4. **Prefer alternatives** when the proposed path fights existing rules (host Odoo, editing `odoo/` core, silent version bumps, tools-ports paths).
5. If the user already decided, implement — but still surface blockers instead of quietly bypassing rules.

## Writing and changing the plan

- Numbered chunks, each with a check (`00-chunk-gate`).
- If an audit or review assumes findings will be **fixed during implementation**, put
  each finding **into the matching plan step** — usually the **current** step — not a
  sidecar list. That step is not complete until those fixes are done or the user
  **explicitly commanded** a skip (highlighted, never marked done).
- After a plan exists: **follow it, or change the numbered list and then follow**. Do
  not replace it with a newly invented sequence. Never mark a point done unless its
  check passed — all cases, including automatic plan updates. Never miss a point
  without an explicit user command. Last step is always: consider skipped points
  (`00-chunk-gate`).

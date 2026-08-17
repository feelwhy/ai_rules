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

---
id: 02-docker-only
description: All local Odoo runs in Docker — never host venv or odoo-bin
apply: always
---

# Docker only

Local Odoo **always** runs in Docker. Never start, suggest, or document a host Python venv, host `odoo-bin`, `python -m odoo`, or host Postgres for app work.

Commands are `30-command-vocabulary`. In a faOtools workspace the examples and the disk bans are `ai_rules_fao` `20-local-commands` and `20-local-docker`.

One-off containers must be `--rm`. Prefer existing launch scripts over ad-hoc `docker run`.

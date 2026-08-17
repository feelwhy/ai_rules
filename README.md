# ai_rules

Universal Cursor / agent rules for Odoo work (faOtools + Febado hubs).

faOtools-specific rules live in sibling repo [`ai_rules_fao`](https://github.com/feelwhy/ai_rules_fao).

## Layout

| Path | Role |
|------|------|
| `src/*.md` | **Canonical** rule sources (edit these) |
| `overrides/<id>.md` | Optional body overrides (same `id`) |
| `tools/sync_rules.py` | Generator |
| `.cursor/rules/*.mdc` | **Generated** — do not edit by hand |
| `AGENTS.md` | **Generated** aggregate |

## Frontmatter

```yaml
---
id: 10-python-odoo
description: Short summary for the agent
apply: always   # or: agent
---
```

- `apply: always` → `alwaysApply: true` in the `.mdc`
- `apply: agent` → `alwaysApply: false` (agent-requestable)
- No `globs:` — distribution is by which workspace folders include this repo

## Sync workflow

```bash
cd /home/feelwhy/Odoo/ai_rules
# edit src/*.md
python3 tools/sync_rules.py          # write .mdc + AGENTS.md
python3 tools/sync_rules.py --check  # CI / pre-commit drift check
```

## Workspace

Add this repo (and usually `ai_rules_fao`) as folders in the Cursor workspace so rules load.

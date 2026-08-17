---
id: 00-index
description: Index of centralized AI rules — what to read and when
apply: always
---

# AI rules index

This folder (`ai_rules`) holds **universal** Cursor / agent rules shared across faOtools and Febado workspaces. faOtools-specific rules live in sibling `ai_rules_fao`.

## Always-on (read every turn)

| id | Topic |
|----|--------|
| `00-index` | This map |
| `01-process-confirmation` | Step-by-step work with user confirmation |
| `02-docker-only` | Never host venv / `odoo-bin` |
| `03-never-discard-wip` | Do not stash/discard foreign WIP |
| `30-command-vocabulary` | Natural-language → concrete commands |

## Agent-requestable (pull when the task matches)

| id | When |
|----|------|
| `04-plan-challenge` | Planning, large tasks, ambiguous scope |
| `05-module-structure` | New modules / scaffolding |
| `10-python-odoo` | Python / ORM |
| `11-xml-views` | XML views / data / QWeb |
| `12-owl-assets` | JS / OWL / SCSS assets |
| `13-security` | ACL, record rules, controllers |
| `14-tests` | Writing or running tests |
| `15-translations` | i18n / exportable strings |
| `16-commit-workflow` | Commit / push / review |
| `20-migrate-v17-to-v18` | Port module 17 → 18 |
| `21-migrate-v18-to-v19` | Port module 18 → 19 |

## Companion repo

When the Cursor workspace includes `ai_rules_fao`, also follow its always-on map (`00-repo-map`, serie discipline, boundaries, local Docker, MCP).

## Editing rules

Edit `src/*.md` only, then run `python3 tools/sync_rules.py`. Do not hand-edit `.cursor/rules/*.mdc` or `AGENTS.md`.

---
id: 30-command-vocabulary
description: Natural-language commands mapped to hub / Docker actions
apply: always
---

# Command vocabulary

Resolve phrases using the **flat hub** (`/home/feelwhy/Odoo`) and the **active serie** (tools git branch / `env-serie.sh`). Never invent host `odoo-bin` commands.

| User says (approx.) | Do |
|---------------------|-----|
| run odoo 19 / demo 19 | `faotools_env/local/env-up.sh demo19` |
| run odoo 19 enterprise | `env-serie.sh 19.0` if needed, then `env-up.sh demo19e` |
| run odoo 17 / 18 | `env-up.sh demo17` / `demo18` (add `e` for enterprise) |
| run support / faotools.com locally | `env-up.sh support` |
| run life | `env-up.sh life` |
| switch serie / checkout 18 | `faotools_env/local/env-serie.sh 18.0` |
| test \<module\> | `env-up.sh demo<N>[e] --test <module>` for the requested/active serie |
| odoo shell / psql | `env-shell.sh <target>` / `env-shell.sh <target> psql` |
| show odoo logs | `docker compose -f faotools_env/local/run/<target>/compose.yml logs -f` |
| sync images/dbs | `faotools_env/local/env-sync.sh` |
| launch / start febado | febado `scripts/docker-dev.sh` + febado local Docker rules — not `env-up` |
| test febado module | febado `scripts/test.sh` (in-repo) |

If serie is unclear, check `git -C /home/feelwhy/Odoo/tools rev-parse --abbrev-ref HEAD` or ask.

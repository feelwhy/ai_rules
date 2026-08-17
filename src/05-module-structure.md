---
id: 05-module-structure
description: Odoo module scaffolding and engineering defaults
apply: agent
---

# Module structure

## Scaffolding

- Every new module always gets a `models/` and a `views/` folder, even if there is nothing to put in them yet.
- `models/` always gets an `__init__.py` (empty is fine until the first model file is added). The module's root `__init__.py` always does `from . import models` regardless of whether `models/__init__.py` currently imports anything itself.
- `views/` holds XML views/actions even if it starts empty; do not skip creating it just because the first change doesn't add a view yet.

## Engineering

- Follow existing module style and naming before introducing new patterns.
- Favor Odoo extension points: inheritance, registries, services, hooks, view inheritance, and manifest assets.
- Keep public behavior backward-compatible for shipped products unless explicitly asked to break it.
- Never inline secrets, API keys, passwords, or OAuth tokens. Use `ir.config_parameter`, environment variables, or existing settings models.
- Avoid broad refactors across independent apps/modules unless the task explicitly asks for them.
- Keep changes scoped to the requested module and its declared companions — no hidden cross-module imports, XML IDs, assets, or model dependencies.

## Variants

- **tools** (apps store): each top-level `__manifest__.py` is a separately installable product unless `depends` says otherwise.
- **support**: one database; flows span modules via declared dependencies — still avoid undeclared coupling.
- **febado**: follow `febado-new-module.mdc` and in-repo packaging rules.

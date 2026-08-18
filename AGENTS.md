# ai_rules

Generated from `src/*.md` by `tools/sync_rules.py`. Do not edit by hand.

## 00-index

_Index of centralized AI rules — what to read and when_

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

## 01-process-confirmation

_Work step-by-step and confirm with the user before irreversible or multi-phase actions_

# Process confirmation

For non-trivial work (multi-file changes, deploys, branch switches, deletions, migrations, publishes):

1. **State the plan** in a short ordered list before doing irreversible steps.
2. **Confirm with the user** at phase gates (delete duplicates, push remotes, switch shared checkout serie, `docker compose down`, live writes).
3. **Do one phase at a time** when the plan says so; do not batch “while I’m here” deletions or refactors.
4. **Report outcomes** with concrete evidence (commands run, paths changed, test results) — not “should be fine”.
5. If blocked (foreign WIP, missing permission, unclear target serie), **stop and ask** instead of improvising.

Small single-file fixes in an already-agreed task do not need a ceremony gate; still avoid surprise side effects.

## 02-docker-only

_All local Odoo runs in Docker — never host venv or odoo-bin_

# Docker only

Local Odoo **always** runs in Docker. Never start, suggest, or document a host Python venv, host `odoo-bin`, or host Postgres for app work.

## Variants

### faOtools flat hub (`faotools_env/local/`)

```bash
cd /home/feelwhy/Odoo/faotools_env
./local/env-up.sh demo19          # community
./local/env-up.sh demo19e         # enterprise
./local/env-up.sh support         # faotools.com neutralized
./local/env-shell.sh demo19       # odoo shell
./local/env-shell.sh demo19 psql
```

Details: `faotools_env/local/README.md` and `ai_rules_fao` local-Docker rule.

### Febado (Doodba / `febado-odoo`)

- Stack via `febado/scripts/docker-dev.sh` and sibling `febado-odoo` compose (`PORT_PREFIX=23`).
- Follow febado in-repo rules (`odoo-local-docker.local.mdc`, telepresence, test scripts).
- Do not stop/recreate the user’s long-lived `:23069` stack unless asked.

### Shared bans

- No `python -m odoo`, no `./odoo-bin`, no activating a project venv to “just run Odoo”.
- One-off containers must be `--rm`. Prefer existing launch scripts over ad-hoc `docker run`.

## 03-never-discard-wip

_Never discard, stash-away, or overwrite other sessions' WIP without explicit user permission_

# Never discard WIP without permission

This worktree is shared across parallel Cursor sessions and human edits.
**Reverting, discarding, or parking someone else's changes without an explicit
user OK is absolutely unacceptable.** "It looked unrelated to my task" is not
permission.

## Hard bans (unless the user explicitly asks)

Do **not** run any of these when the working tree has changes you did not make
in *this* conversation, or when untracked files exist that you did not create:

- `git stash` / `git stash push` / `git stash -u` (including "just to rebase")
- `git checkout -- <path>` / `git restore <path>` / `git clean`
- `git reset --hard` / `git checkout -f` / destructive branch switches that
  drop or replace dirty/untracked files
- `git commit --amend` that rewrites files belonging to another change
- Overwriting a dirty file with `Write` / `checkout <other-commit> -- <path>`
  when that path's working-tree content is not yours

"Park it in a stash and pop later" still counts as discarding if the pop is
incomplete, the untracked parent is empty, or another session's branch no
longer matches the worktree the user's server is reading.

## Before any git / branch / rebase / MR push

1. Run `git status -sb` and read **every** dirty and untracked path.
2. Classify each path: **mine (this chat)** vs **foreign / unknown**.
3. If anything is foreign or unknown → **stop**. Tell the user what would be
   affected. Ask what to do. Do not stash, rebase, switch branch, or force a
   clean tree yourself.
4. If foreign WIP blocks a switch: **stop and ask**. Do **not** “solve” it by
   doing this chat’s real work only in a side worktree while the shared tree
   stays elsewhere — see hub serie discipline in `ai_rules_fao`.
5. Committing *only your* paths on a new branch in the **shared** checkout is
   fine when that does not touch foreign files — never "clear the desk" first.

## Shared worktree + long-lived Docker Odoo

Shared checkouts under `/home/feelwhy/Odoo/` are bind-mounted into Docker (Febado `:23069`, faOtools `env-up` targets, etc.). Switching the
checked-out branch (or stashing files that exist only as WIP / on another
branch) changes what the live server serves.

- **This chat’s active branch must live in the shared checkout** so `:23069`
  runs current code and SCM shows what is uncommitted
  (see `ai_rules_fao` hub serie discipline).
- Do not switch away from a branch that holds **foreign** WIP the user may be
  browsing unless they ask.
- After any allowed branch change, warn if `:23069` may now be missing code
  that was visible a minute ago.

## If you already disturbed foreign WIP

1. Say so immediately (what was lost/moved, which paths).
2. Recover from reflog / stash / the other branch (`git checkout <commit> --`
   only to **restore**, and say you are restoring).
3. Do not hide it inside an unrelated MR.

## Incident that caused this rule (2026-07-28)

DATA-010 prep stashed/rebased in the shared worktree while
`journey/§1-PUB-bidder-privacy` WIP (`_febado_public_bidder_label`, templates)
was present. Public Current-bids names reappeared on the live local server without permission.
That class of mistake must not recur.

## 04-plan-challenge

_Challenge plans and task framing before large or ambiguous work_

# Plan / task challenging

Before a large implementation or when a plan looks thin:

1. **Restate the goal** and the smallest change that would satisfy it.
2. **Name risks**: shared-checkout serie, foreign WIP, production data, apps-store compatibility, Docker-only constraints.
3. **Point out missing gates**: tests, confirmation before delete/push/live write, which repo owns the change.
4. **Prefer alternatives** when the proposed path fights existing rules (host Odoo, editing `odoo/` core, silent version bumps, tools-ports paths).
5. If the user already decided, implement — but still surface blockers instead of quietly bypassing rules.

## 05-module-structure

_Odoo module scaffolding and engineering defaults_

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

## 10-python-odoo

_Python and Odoo ORM conventions (incl. model member order)_

# Python / Odoo ORM

## Style

- Follow PEP 8 and the coding conventions already used in the target module / serie.
- Keep the repository's existing quote/formatting style when editing nearby code.
- Use `_logger = logging.getLogger(__name__)`; no `print`.
- Type hints are allowed only when they do not interfere with Odoo registry loading or monkey-patching.
- Prefer compact signatures (few lines) over one-argument-per-line wrapping unless the file already uses that style.

## ORM

- Use the ORM. Raw SQL needs a strong reason, parameterized queries, and no user-controlled f-strings.
- Write recordset-safe code: methods should work with empty, singleton, and multi-record `self` where appropriate.
- Prefer `search_count`, `read_group`, `_read_group`, mapped/filtered operations, and batching over per-record queries.
- Use `sudo()` deliberately and narrowly; add a short comment when it changes access semantics.
- Avoid manual `cr.commit()` in business logic; only use it in explicit jobs or integration flows with a documented reason.

## Model file order

1. `_name`, `_description`, `_inherit`, `_order`, `_rec_name`, `_check_company_auto`
2. Default methods
3. Selection fields methods
4. `@api.depends` computes
5. inverse methods
6. `@api.constrains`
7. `@api.onchange`
8. Field definitions (grouped: stored → related → computed → company-dependent)
9. SQL constraints (`_sql_constraints` / `models.Constraint` on serie that requires it)
10. CRUD overrides (`create`, `write`, `unlink`, `copy`)
11. Action methods (`action_*`)
12. Business / helper methods (`_*`)

## Module integrity

- New models need `security/ir.model.access.csv`, optional record rules, manifest `data`, and package imports in the same change.
- Declare every direct module dependency in `__manifest__.py`; do not rely on transitive dependencies.
- Do not import Python from another custom add-on unless the manifest depends on that add-on.
- Keep model, field, XML ID, and config parameter names prefixed by the owning module or existing product family.

## Variants

- Match the **active Odoo serie** (git branch / env target), not an assumed 19.0 API.
- **febado**: also follow febado in-repo `python-odoo.mdc` (stricter formatting, `api.model_create_multi`, etc.).
- **tools** apps-store metadata / version policy: see `ai_rules_fao` manifest + packaging rules.

## 11-xml-views

_XML conventions for views, data, templates, menus, and reports_

# XML IDs
- Prefix new IDs with the module technical name or the module's established prefix.
- Do not reference XML IDs from another custom module unless the manifest declares that module in `depends`.
- Prefer stable IDs for apps-store upgrades; do not rename existing IDs without a migration reason.

# Views
- Inherit Odoo/core views with targeted `<xpath>` changes; do not redefine full upstream views.
- Keep form structure conventional: `<header>`, `<sheet>`, grouped fields, `<notebook>`, chatter when used.
- Preserve existing groups, attrs/modifiers, context, domain, and sequence behavior unless the task targets them.

# Data
- Put seed/configuration records in `data/`; demo-only records in `demo/` and manifest `demo`.
- Use `noupdate="1"` only for records that should not be changed by module upgrades.
- Avoid hardcoded database IDs. Use `ref()` and external IDs.

# QWeb
- Use `t-out` for escaped output and avoid `t-raw` unless content is already sanitized HTML.
- Inherit website/portal templates with `t-inherit` and precise XPath changes.
- Keep translatable user-facing strings extractable.

# Menus and Actions
- Menu items should define parent, action when applicable, sequence, and groups where access is restricted.
- Window actions should declare `view_mode` in the intended priority order.

## 12-owl-assets

_JavaScript, OWL, XML template, SCSS, and asset bundle conventions_

# JavaScript Modules
- Start Odoo JavaScript files with `/** @odoo-module **/` unless the surrounding file type intentionally differs.
- Use ES module syntax and Odoo registries/services. Do not add AMD-style `odoo.define` in new code.
- Prefer existing Odoo services (`orm`, `rpc`, `notification`, `dialog`, `action`, `user`, `router`) over ad hoc globals.

# OWL
- Use hooks (`useState`, `useRef`, `useService`, `onWillStart`, `onMounted`) instead of manual lifecycle workarounds.
- Keep component templates, class names, and registry keys consistent with the module's established naming.
- Validate props when the surrounding codebase does so; keep components small and module-local.

# Assets
- Register all new JS/XML/SCSS in the owning module's `__manifest__.py` assets.
- Add backend UI to `web.assets_backend`; website/portal UI to `web.assets_frontend`; custom bundles only when reused.
- Do not include assets from another custom add-on unless the manifest depends on that add-on.

# Styling
- Reuse Odoo variables and existing SCSS utilities before adding new colors or layout primitives.
- Keep styles scoped to the component/view where possible; avoid global selectors that can affect other installed apps.

# Don'ts
- No jQuery in new code unless maintaining an existing legacy widget.
- No global `window.*` state for business logic.
- No inline `<script>` in QWeb templates.

## 13-security

_Access rights, record rules, portals, and security-sensitive code_

# Access Rights
- Every persistent model needs explicit `ir.model.access.csv` entries unless it is intentionally transient or abstract.
- Keep CSV header exactly: `id,name,model_id:id,group_id:id,perm_read,perm_write,perm_create,perm_unlink`.
- Grant portal/public permissions narrowly and only for records they should actually reach.

# Record Rules
- Add record rules for company, website, portal, vendor/customer, or user-owned data boundaries.
- Bind rules to groups where possible; unscoped global rules need a clear reason.
- Use domains based on `user`, `company_ids`, partner relations, or website context, not hardcoded IDs.

# Controllers
- Every `@http.route` must explicitly declare `auth`, `type`, `methods`, and `csrf` when relevant.
- Validate request payloads before write operations. Never trust client-side domains or readonly fields.
- For public routes, check access tokens/signatures or use standard portal token patterns when exposing private records.

# Secrets and External Services
- Store credentials in settings / `ir.config_parameter`; never in manifests, data files, JS, or templates.
- Use explicit request timeouts and sanitized logging for outbound HTTP calls.

# Review Checklist
- New model: access CSV added, record rules considered, and tests added for denied access when practical.
- New controller: auth mode, CSRF behavior, access checks, and error payloads reviewed.

## 14-tests

_Test layout and conventions for Odoo module tests_

# Layout
- Tests live in `<module>/tests/`.
- Test files are named `test_<feature>.py` and imported from `<module>/tests/__init__.py`.
- Use `TransactionCase` for ORM behavior, `HttpCase` for controllers/browser flows, and tagged cases where install timing matters.

# Conventions
- Use `@tagged("post_install", "-at_install", "<module>")` when a module-specific tag is helpful.
- One behavior per test method. Name tests as `test_<scenario>_<expected>`.
- Prefer `setUpClass` for shared records and factories when setup is reused.
- Use Odoo assertions such as `assertRecordValues` where they make failures clearer.

# Coverage Priorities
- Computed fields, constraints, onchange-impacting helpers, cron/job behavior, and upgrade-sensitive defaults.
- Security rules with `with_user(...)` for portal/public/user isolation.
- Controllers: auth mode, response shape, access denial, and side effects.
- External APIs/cloud integrations: mock network calls; never hit live services in tests.

# Command Reference
`../faotools_env/local/env-up.sh demo19 --test <module>`
(or `demo19e` for enterprise). See `faotools_env/local/README.md`.

## 15-translations

_Translation and i18n conventions for Odoo modules_

# Translations

- User-facing strings in Python, XML, and JS must be exportable (`_()`, XML text nodes, OWL/`_t` as used by the serie).
- Do not wrap technical identifiers, logger messages, or already-translated values unnecessarily.
- Prefer editing source strings in code/XML over hand-patching `.po` unless the task is translation-only.
- After string changes that matter for release, mention that a translation export/update may be needed.
- Keep existing `i18n/` structure and language codes; do not delete translation files casually.
- On serie upgrades, follow migration rules for deprecated `_()` uses (e.g. pure-Python constraint messages on 18+).

## 16-commit-workflow

_Commit, test, review, and push workflow_

# Commit workflow

## Commit modes (A / B)

The **letters are universal**; the routing and the gates behind them belong to the project. The table
below is the **faOtools hub** mapping.

**febado already owns its own A/B definition** (`febado-push-workflows.local.mdc`) and it is *not*
this one — there, Mode A (local commit) is the default even for “push this workflow / push WF-…”, and
Mode B means a **section-scoped MR**, not a bare `git push`. In febado, always route the phrase and
the test/review gates through febado’s rule; never apply the hub row below to it, and never relax
febado’s stricter policy.

| User says | Mode | Push | Tests | Review |
|-----------|------|------|-------|--------|
| “commit”, “commit A”, “commit mode A” | **A** | no | not required | no review |
| “commit A1” | **A1** | no | not required | **review first** |
| “commit B”, “commit mode B”, “commit and push”, “push” | **B** | yes | **required** | **offer** a Cursor review before pushing |
| “commit B1” | **B1** | yes | **required** | **review first** (no need to ask) |
| “commit B2” | **B2** | yes | **required** | no review — push directly |

- **Bare “commit” means mode A.** Never push in mode A — not “while I’m here”, not because the
 branch looks ready.
- **Every B mode is gated on tests**: run the relevant tests for the changed module(s) first and
 report the result. Failing, skipped, or un-runnable tests → **stop and ask**; do not push.
- Mode A does not require a test run, but never commit knowingly broken code, and say plainly
 whether tests were run.
- **Review = Cursor review of the local changes** (Bugbot subagent; add a security review when the
 change touches auth, ACL, controllers, or secrets). Fix or report its findings **before** pushing.
- **Push with review unspecified → offer the review** (mode B): ask once, do not push while waiting.
 An explicit “with review” / “without review” in the request wins over the mode letter.
- All modes: commit only paths belonging to this task (never-discard-WIP), keep the repo’s message
 style, and never `--no-verify` unless the user asks.
- Which repos a bare “commit” / “push” covers on the faOtools hub: see `ai_rules_fao`
 `02-repo-boundaries` (every non-read-only checkout).

## Before committing

1. Run the **relevant tests** for the changed module(s) via Docker (`env-up … --test`, `support/devops/run_tests.sh`, or febado `scripts/test.sh`). Do not commit knowingly broken behavior.
2. `git status` / `git diff` — commit only paths belonging to this task; respect never-discard-WIP.
3. Follow the repo’s existing commit-message style (focus on why).

## Review

- Review is driven by the mode suffix above: none for `A` / `B2`, run it for `A1` / `B1`, **offer** it
 for a bare `B` / “push”.
- Do not invent extra review rituals beyond that, and do not block a mode `A` commit on a review.

## Push variants

- **ai_rules / ai_rules_fao**: push when the user asks to publish rules.
- **tools / support / life / …**: push only when the user explicitly asks; prefer leaving working-tree deletions/edits for review when trimming rules.
- **febado**: follow febado push / MR rules (`febado-push-workflows`); never force-push shared branches unless explicitly requested.
- Never `--no-verify` / skip hooks unless the user explicitly requests it.

## 20-migrate-v17-to-v18

_Checklist and transforms for migrating an Odoo module from 17.0 to 18.0_

# Odoo 17 -> 18 migration

Apply these transforms when porting a module to 18.0. Work module-by-module, keep
public model/field/XML-ID names stable unless the upgrade itself renames them, and
bump the manifest `version` to `18.0.x.y.z`. After edits run the test command from
the active test command / module structure rules. Don't edit `odoo/` (and `enterprise/`); override in the custom module.

## Python

- `_()` translation in pure Python (e.g. `_sql_constraints` messages) is deprecated -> just remove the `_()` wrapper.
- `check_access_rights(...)` is deprecated -> use `check_access(...)`.
- `_check_recursion()` is deprecated -> use `_has_cycle()`. It can take a field name arg (covers children, not only parents). **The boolean result is inverted** — flip the surrounding logic.
- `def _search(...)`: `access_rights_uid` is no longer accepted as an argument — drop it from signature and callers.
- `group_expand` callables no longer accept a `domain` argument. See `documentation_builder/documentation_section.py` (`_read_group_category_id`).
- `slug` / `slugify` are removed from `odoo.addons.http_routing`:

```python
# BEFORE
from odoo.addons.http_routing.models.ir_http import slug, slugify
slug(product)
slugify(text, max_length=1024, path=True)
# AFTER
self.env["ir.http"]._slug(product)
self.env["ir.http"]._slugify(text, max_length=1024, path=True)
```

- `request.session` is now pure JSON: keys are integers, values must be JSON-serializable (no `datetime`, recordsets, etc.). See `odoo_password_manager/.../bundle_security_mixin.py`.
- Watch `expression.OR` / `expression.AND` with empty sub-lists: an empty list element can collapse to a buggy `[(1, "=", 1)]`. Guard empties before combining. See `odoo_password_manager/.../password_key.py` `_construct_duplicates_domain`.

## XML / views

- `tree` is renamed to `list` everywhere — view `<tree>` tags, `view_mode="tree,..."` in actions, `view_type`, etc. -> `list`.
- Chatter is declared with a single tag. Replace the old block:

```xml
<!-- BEFORE -->
<div class="oe_chatter">
  <field name="message_follower_ids"/>
  <field name="activity_ids"/>
  <field name="message_ids"/>
</div>
<!-- AFTER -->
<chatter/>
```

- `ir.cron` no longer has `numbercall` and `doall` fields — remove them from `<record>` data.
- `ir.actions.act_window` gains an optional `path` field for a clean web URL: `<field name="path">sticky-notes</field>`.
- Kanban view template names changed:
  - `<t t-name="kanban-box">` -> `<t t-name="card">`
  - `<t t-name="kanban-menu">` -> `<t t-name="menu">`
  - the bottom area: use `<footer>` instead of `o_kanban_record_bottom`.

## OWL / JS

- `_lt()` is deprecated -> use `_t()`.
- `useService("user")` is deprecated -> import the singleton:

```js
import { user } from "@web/core/user";
await user.hasGroup("project.group_project_user");
```

- `useService("rpc")` is deprecated -> import `rpc` directly:

```js
import { rpc } from "@web/core/network/rpc";
const fields = await rpc("/web/export/get_fields", { ...parentParams, model, import_compat });
```

- `archParseBoolean(...)` (utils) is deprecated -> use plain `Boolean(...)`.
- For mounting components, don't use `import { templates } from "@web/core/assets"` -> use `import { getTemplate } from "@web/core/templates"`. See `odoo_password_manager/.../js/vault_login.js`.

## Single-view UI / JS

- `SearchModel._getDomain` can now be cleanly overridden (super-call returns properly); drop the old `try/except` workaround or you'll get an error. See `product_management/.../search/product_search_model.js`.
- `web.KanbanRecord` root element changed from `<div t-ref="root">` to `<article t-ref="root">`. See `product_management/.../kanban/product_kanban_record.xml`.
- jQuery is NOT in backend assets. If truly needed, load it on component start: `loadJS("/web/static/lib/jquery/jquery.js")` (`odoo_password_manager/password_navigation`). Prefer removing jQuery. Typical replacement:

```js
// BEFORE: var d = $.Deferred();
import { Deferred } from "@web/core/utils/concurrency";
const d = new Deferred();
```

## 21-migrate-v18-to-v19

_Checklist and transforms for migrating an Odoo module from 18.0 to 19.0_

# Odoo 18 -> 19 migration

Apply these transforms when porting a module to 19.0. Assumes the module is already
v18-clean (see `20-migrate-v17-to-v18`). Keep public model/field/XML-ID names stable
unless the upgrade renames them, and bump the manifest `version` to `19.0.x.y.z`.
Release notes: https://www.odoo.com/odoo-18-1-release-notes (and -18-2/-18-3/-18-4).
Run the test command from the active test command / module structure rules. Override in the module, never edit `odoo/`.

## Security / res.groups (touch every security XML)

- New intermediate level `res.groups.privilege` sits between `ir.module.category` and `res.groups`. `res.groups` gains a `privilege_id`.
- Field renames — update all `security/*.xml`, `data`, and code:
  - `res.groups.users` -> `res.groups.user_ids`
  - `res.users.groups_id` -> `res.users.group_ids`
  - `ir.actions.server`, `ir.actions.act_window`, `ir.ui.menu`: `groups_id` -> `group_ids`
  - chained access: `access_ids.group_id.users` -> `access_ids.group_id.user_ids` (note: `group_id` itself keeps its name).
- `base.module_category_hidden` is no longer needed — remove it, no privilege replacement.
- `res.groups.all_user_ids` = all users of a group (NOT stored). For `@api.depends` use:
  `"access_user_group_ids"`, `"access_user_group_ids.user_ids"`, `"access_user_ids"`,
  `"access_user_group_ids.implied_by_ids.all_implied_by_ids.user_ids"`.
  See `mail_manual_routing` `security.xml` + `mail_message.xml` + `mail_attach.xml` (and `password_key`).

## Python

- `auto_join` on relational fields is deprecated — remove it.
- Domain combinators move to `odoo.fields.Domain`:

```python
# BEFORE
from odoo.osv.expression import OR, AND
# AFTER
from odoo.fields import Domain
Domain.OR([...]); Domain.AND([...])
```

- `@api.returns(...)` is no longer used — remove the decorator.
- Obsolete aliases: `self._cr` -> `self.env.cr`; `self._context` -> `self.env.context`; `request.context` -> `request.env.context`.
- `_sql_constraints` is unsupported -> use `models.Constraint`:

```python
# BEFORE: _sql_constraints = [("name_uniq", "unique (name)", "Tag name already exists!")]
# AFTER
_name_uniq = models.Constraint("unique (name)", "Tag name already exists!")
```

- `sale.order.line` / `purchase.order.line`: field `product_uom` -> `product_uom_id`.
- `read_group` is deprecated -> use `_read_group` (see `stock_qty_forecast/.../stock_forecast_wizard.py`).
- `@route(type='json')` is a deprecated alias -> use `@route(type='jsonrpc')`.
- `def _search(...)` has new args — check the v19 signature when overriding.
- `ir.mail_server.build_email(...)` removed -> `_build_email__(...)`.
- `safe_eval` no longer accepts a `nocopy` argument.
- A record's "search" field attribute now relies on a method whose `value` is an `OrderedSet`.

## XML / views / actions

- `ir.actions.act_window` `target` no longer supports the `inline` value — fix every `res_config_settings.xml` (and any inline action).
- Kanban actions: `type="edit"` is deprecated -> use `type="open"`.
- `search_view_id` must use `ref` not `eval`: `<field name="search_view_id" ref="sticky_note_view_search"/>`.
- A `<group>` in a search view should not carry `expand="0"` / `string="Group by..."` — drop those attrs.
- `customize_show` on website pages is deprecated -> replace with the website-builder JS option.

## Email templates

- Use `ctx.get("key")` instead of `ctx["key"]` in template expressions.

## OWL / JS

- `FormController` `mode` prop is replaced with `readonly` — search source for `mode: "`, `mode: '`, `mode: {` and adapt.
- Record `data` is now a dict, not an array — update any index-based access.
- `useDateTimePicker` import moved:

```js
// BEFORE
import { useDateTimePicker } from "@web/core/datetime/datetime_hook";
// AFTER
import { useDateTimePicker } from "@web/core/datetime/datetime_picker_hook";
```

## Single-view UI / JS

- `all_group_ids` = all current groups of the user (incl. built-in). In every single-view-interface module, rework `action_return_mass_actions` accordingly.
- `getExportedFields` must be adapted (see `product_management/components/product_manager/product_manager.js`):

```js
async getExportedFields(isCompatible, parentParams) {
  const resIds = this.props.selection.map((rec) => rec.id);
  const ids = resIds.length > 0 && resIds;
  const domain = [["id", "in", ids]];
  return await rpc("/web/export/get_fields", {
    model: this.props.kanbanModel.root.resModel,
    domain,
    import_compat: isCompatible,
    ...parentParams,
  });
}
```

## Mail / activities

- Completed `mail.activity` records are now archived, not deleted — code that relied on deletion (counts, cleanup, searches) must account for archived rows.

## 30-command-vocabulary

_Natural-language commands mapped to hub / Docker actions_

# Command vocabulary

Resolve phrases using the **flat hub** (`/home/feelwhy/Odoo`) and the **active serie** (tools git branch / `env-serie.sh`). Never invent host `odoo-bin` commands.

| User says (approx.) | Do |
|---------------------|-----|
| run odoo 19 / demo 19 | `faotools_env/local/env-up.sh demo19` |
| run odoo 19 enterprise | `env-serie.sh 19.0` if needed, then `env-up.sh demo19e` |
| run odoo 17 / 18 | `env-up.sh demo17` / `demo18` (add `e` for enterprise) |
| start / launch **the same** target again, restart it | `env-up.sh <that-target> --restart` **only** — see below |
| run support / faotools.com locally | `env-up.sh support` |
| run life | `env-up.sh life` |
| switch serie / change version / switch branch to 18 | put the serie repos on `18.0` — on the faOtools hub follow `ai_rules_fao` `01-hub-serie` (explicit per-repo checkout, then pull) |
| pull changes | fast-forward the current branch of the hub repos with `--ff-only` (`ai_rules_fao` `01-hub-serie`) |
| test \<module\> | `env-up.sh demo<N>[e] --test <module>` for the requested/active serie |
| odoo shell / psql | `env-shell.sh <target>` / `env-shell.sh <target> psql` |
| show odoo logs | `docker compose -f faotools_env/local/run/<target>/compose.yml logs -f` (history: `~/env-sync/logs/<target>/odoo.log`) |
| sync images/dbs | `faotools_env/local/env-sync.sh` (downloads **and** restores + neutralizes) |
| is \<target\> ready to launch? | `faotools_env/local/env-prepare.sh --check` |
| launch / start febado | febado `scripts/docker-dev.sh` + febado local Docker rules — not `env-up` |
| test febado module | febado `scripts/test.sh` (in-repo) |
| commit / commit A | prepare the **local** commit only — never push, no review (`16-commit-workflow`) |
| (in **febado**) commit / push \<one workflow\> | febado’s own Mode A/B rule decides — “push this workflow” stays **local** there |
| commit A1 | local commit only, **with** a Cursor review first |
| commit B / commit and push / push | **tests** → commit → push; review unspecified → **offer** a review before pushing |
| commit B1 / commit B2 | as B, **with** review (B1) / **without** review (B2) |

If serie is unclear, check `git -C /home/feelwhy/Odoo/tools rev-parse --abbrev-ref HEAD` or ask.

## Same target again: restart only

If the user asks to start / launch / run **the same** image or target again
(the one already up, or the one last launched in this chat — e.g. “start it
again”, “restart demo17e”, “launch the same”):

1. Run **only** `faotools_env/local/env-up.sh <that-target> --restart` (logs +
   URLs as usual). That restarts the Odoo container.
2. Do **not** do anything else: no `env-serie.sh`, no `env-prepare.sh`, no
   `env-sync.sh`, no `--fresh`, no `-u` / `-i` / `--test`, no git checkout,
   no Docker Desktop start unless `docker info` actually fails, no script or
   rule edits, no commits.

A different target or serie is a new launch, not this case.

## Launching a local target: what the user must always get

1. **Speed.** A launch is a container start: ~1.5s warm, ~6s cold, ~25s when the hub
   has to switch serie. Anything in the minutes means the target was never restored
   or neutralized — run `env-prepare.sh --check`, fix the **refresh**, and say so.
   Never present a multi-minute wait as normal.
2. **Logs.** Stream them in the terminal: run `env-up.sh <target>` (no `--no-logs`)
   and background the command so it keeps printing. Also give the host log path.
3. **Links.** Always repeat the printed Odoo URL (with `admin` / `admin`), the
   Mailpit URL, and the database name — do not make the user hunt for them.
4. **Errors.** `env-up.sh` prints `ERROR`/`CRITICAL` lines logged since start.
   Report them instead of claiming a clean launch.

# ai_rules

Generated from `src/*.md` by `tools/sync_rules.py`. Do not edit by hand.

## 00-chunk-gate

_Work in small checkable chunks and stop for user confirmation after each one_

# Chunk gate (read this before anything else)

**The default mode of work is: one small chunk, then stop and wait for the user.**
Long autonomous runs are forbidden. An agent that disappears for many tool calls and
comes back with a finished multi-file, multi-repo change has failed the task even if
the code is correct — the user could not steer, review, or veto anything.

## What a chunk is

One coherent change the user can check **in about a minute**:

- typically **one repo** and **≤ ~5 files**
- **at most one** build / test / deploy / long command
- a single reviewable idea ("add field X", "wire payload key", "write this test")

If the work does not fit that, it is **several** chunks. Split it and do the first one.

## The gate

After every chunk, **stop your turn** and report:

1. **What changed** — exact paths, and what each edit does.
2. **What you verified** — the command run and its real result (`06-verify-hypotheses`).
3. **What is next** — the single next chunk.
4. **An explicit question** — "proceed with X?" Then wait.

Do **not** start the next chunk in the same turn. "It was obviously next" is not
confirmation. Silence is not confirmation.

## Planning

- A plan is delivered as a **numbered list of chunks**, each with its own check, before
  any code is written. Get the plan approved first (`04-plan-challenge`).
- **Approving a plan approves chunk 1 only.** A plan, a todo list, a phase list, or a
  document in the repo is a map — never a licence to run the whole route unattended.
- Phrases like "implement the plan", "finish the todos", "continue", "do the last phase"
  mean **the next chunk**, not all remaining work.
- If the user explicitly says "do it all, no check-ins", honor it — and say plainly how
  many chunks you are about to run before starting.

### Follow the plan (strict)

Once a plan exists, **follow that numbered list**. If it is wrong, **change the list**
(say what changed and why), then follow the new list. Do **not** invent a second plan
mid-flight because it “seems better” — that is how the plan becomes a mess.

**Never mark a plan point completed if it is not.** This is absolute — **all cases**,
no exceptions: not todos, not the reprinted plan, not “what changed”, not a Cursor /
automatic plan update, not a rewrite, not a mode or branch switch, not “while I’m here”.
Partial work stays open. “I started it” is not done. The point’s check must have passed.

**Never miss a plan point** unless the user **explicitly commanded** that skip
(“skip 3”, “drop this point”). Blocked, inconvenient, or “we’ll do it later” is **not**
a miss — stop, leave the point open (`You are here`), and ask. An automatic plan
update must not hide, reorder-away, or complete a point.

**Audit / review findings that the plan assumes will be fixed during implementation**
belong **inside the matching plan step** — usually the **current** one — not a sidecar
list and not “we’ll get to it”. Fold them into that step’s work and check before calling
the step done.

**While implementing, reprint the numbered plan every turn with `You are here` on the
current point.** Keep the original numbers. Example:

```
1. Add field X — done
2. Wire payload — **You are here**
3. Write the test
4. Consider missed points
```

**Missed points (user-commanded only).** If the user explicitly said to skip a point:
**highlight it** on the reprint (`skipped: <user command>`). Do **not** mark it
completed. The **last plan step** is always: consider every skipped point and either
do it, fold it into a new numbered step, or get an explicit user OK to drop it.

## Hard stops (stop the turn immediately, mid-work if needed)

- ~10 write operations (edits / file creations) since the last user message
- a second repo is about to be touched
- a manifest `version`, migration, or schema change is about to be added
- a test / build / deploy run just finished — report it, do not keep editing
- anything irreversible or shared: push, deploy, branch switch, delete, live write
- the plan turned out wrong, or you found something the user does not know yet

## Never

- Batch unrelated fixes because "I was already in the file".
- Add scope the user did not ask for (extra tests, refactors, doc updates, renames).
- Keep working through a failure you have not reported.
- Present hours of unsupervised work as a single result and ask for approval afterwards
  — approval before the work is the whole point.

## Exempt (no gate needed)

- Read-only investigation: reading, grepping, searching, querying.
- One trivial edit the user asked for literally ("fix this typo").
- Steps inside a chunk the user just approved.

This rule outranks any instinct to be efficient or "helpful" by finishing early.
When in doubt: smaller chunk, ask sooner.

## 00-index

_Index of centralized AI rules — what to read and when_

# AI rules index

This folder (`ai_rules`) holds **universal** Cursor / agent rules shared across faOtools and Febado workspaces. faOtools-specific rules live in sibling `ai_rules_fao`.

## Always-on (read every turn)

| id | Topic |
|----|--------|
| `00-chunk-gate` | **First rule.** Small chunks, follow the approved plan, stop and confirm |
| `00-plain-replies` | Short answers, no filler, no status theater |
| `00-index` | This map |
| `01-process-confirmation` | Step-by-step work with user confirmation |
| `02-docker-only` | Never host venv / `odoo-bin` |
| `03-never-discard-wip` | Do not stash/discard foreign WIP |
| `06-verify-hypotheses` | Check the hypothesis before recommending |
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
| `17-translations` | faOtools glossary-driven app + website translations |
| `20-migrate-v17-to-v18` | Port module 17 → 18 |
| `21-migrate-v18-to-v19` | Port module 18 → 19 |

## Companion repo

When the Cursor workspace includes `ai_rules_fao`, also follow its always-on map (`00-repo-map`, serie discipline, boundaries, local Docker, MCP, `17-translations`). Any task that changes copy, `.po`, `module.description`, or `module.release.description` must pull `ai_rules` `17-translations` as well. “Prepare / make / publish a release” must pull `ai_rules_fao` `33-faotools-release` (step 8 is TM-first changelog translation on 19.0+).

## Editing rules

Edit `src/*.md` only, then run `python3 tools/sync_rules.py`. Do not hand-edit `.cursor/rules/*.mdc` or `AGENTS.md`.

## 00-plain-replies

_Short replies — answer first, no filler, no status theater_

# Plain replies (no filler)

The user is here to **do or check something**, not to read a report about the agent.

## Lead with the answer

First sentence: the fact, the URL, or the decision. Then the minimum evidence that proves it (`path:line`, command, HTTP code). Then stop.

A yes/no question gets a yes/no — then one line of how to check, if that is the point.

## Forbidden

- Restating the question, narrating the plan, or "wrapping up" what the user already knows
  (exception: while a plan is in progress, reprint it with `You are here` — `00-chunk-gate`)
- Status theater: "What ran", "What I verified", "Checked on …", bullet inventories, coverage percentages, unless the user asked for an audit
- Hedging and padding: "ready enough", "mostly yes", "for the items you listed", "belt and suspenders"
- Repeating login/URLs/Mailpit/DB every turn
- Explaining why a sentence is short, or apologizing for length

## When they want to check

Give the URL (and login **once** if they do not have it). Do not list every translated string. Do not recap the pipeline. If something is **not** ready, say that in one sentence and ask to proceed with the missing step.

## Length

Default: a few short sentences. A table or a file list only when it is the deliverable. Chunk-gate reports stay to the four required lines — not an essay under each heading. When a plan is in progress, add the numbered reprint with `You are here` (and any user-commanded `skipped` highlights).

## 01-process-confirmation

_Work step-by-step and confirm with the user before irreversible or multi-phase actions_

# Process confirmation

For non-trivial work (multi-file changes, deploys, branch switches, deletions, migrations, publishes):

1. **State the plan** in a short ordered list before doing irreversible steps.
2. **Confirm with the user** at phase gates (delete duplicates, push remotes, switch shared checkout serie, `docker compose down`, live writes).
3. **Do one phase at a time** when the plan says so; do not batch “while I’m here” deletions or refactors. Follow the approved numbered plan, or change that list and follow the new one — do not invent a parallel plan (`00-chunk-gate`).
4. **Report outcomes** with concrete evidence (commands run, paths changed, test results) — not “should be fine”.
5. If blocked (foreign WIP, missing permission, unclear target serie), **stop and ask** instead of improvising. Do not skip or mark a plan point done — blocked is not a miss (`00-chunk-gate`).

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
- `docker-dev.sh start` / `logs` open a visible Cursor tab (`febado Odoo logs`)
  the same way faOtools `env-up.sh` does — do not pass `--no-logs` on a launch.
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

## 06-verify-hypotheses

_Verify a hypothesis against real code, data, or logs before recommending or asserting it_

# Verify, don't theorize

An explanation, diagnosis, or recommendation is only worth giving once it has been **checked against
reality**. Plausible-sounding reasoning about code you did not read, an API you remember from
another serie, or data you did not query is a guess — do not deliver it as a finding.

## Check first (the cheap checks are always available)

- **Code**: read the file, `Grep` the symbol, follow the actual call site — including upstream
  `odoo/` / `enterprise/` / `others/oca/` sources (read-only) instead of recalling the API.
- **Data**: query the real database (`env-shell.sh <target> psql`, Odoo MCP, pgweb) instead of
  assuming what records exist.
- **Behavior**: run the test, hit the URL, reproduce the user's step in the running Docker stack.
- **Logs**: read the traceback / `ERROR` lines rather than inferring the failure mode.
- **Version reality**: check the **active serie** (branch / env target) — an API that exists on 19.0
  may be gone or renamed on the serie in front of you.

## Rules

1. **No unverified cause.** Before "the reason is X", confirm X. One concrete check beats three
   paragraphs of reasoning.
2. **No unverified fix.** Do not recommend an edit whose premise (this field exists, this hook
   fires, this template is inherited) has not been looked up.
3. **Label real hypotheses.** When a check is genuinely impossible (needs prod, the user's browser,
   a permission), say it is a hypothesis, name the check that would settle it, and ask — never
   promote it to a conclusion.
4. **Cite the evidence** in the reply: `path:line`, the command run, the query result, the log line,
   the test outcome. "Should be fine" / "probably" is not a report (`01-process-confirmation`).
5. **Don't stack on an unverified premise.** If step 1 is a guess, stop and check it before building
   steps 2-5 on top of it.
6. **When the user reports a bug**, inspect or reproduce before proposing a fix; a fix for the wrong
   cause costs more than the check would have.
7. **A user's premise is checkable too.** If the code contradicts what the request assumes, say so
   with the evidence instead of implementing on the wrong assumption.

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

# XPath
- Select on stable hooks only: `@id`, `@name`, `@t-name`, `hasclass(...)`, or a unique structural path.
- Do **not** write XPath that matches `@t-esc`, `@t-raw`, or `@string`. `@string` fails view validation (`View inheritance may not use attribute 'string' as a selector.`). `@t-esc`/`@t-raw` selectors die when the parent switches to `@t-out`. `--dev=qweb` logs `Found deprecated directive @t-esc`/`@t-raw` only when those directives sit on rendered QWeb nodes, not when XPath merely matches them.
- Prefer `hasclass('foo')` over `contains(@class, 'foo')`.
- Exception: an inherit whose **only** job is replacing a remaining upstream `@t-esc`/`@t-raw` with `@t-out` may match that directive for the replace.

```xml
<!-- BAD: selector dies when the parent switches to t-out -->
<xpath expr="//span[@t-esc=&quot;record.name&quot;]" position="replace">
    <span t-out="record.name"/>
</xpath>
<!-- GOOD -->
<xpath expr="//span[@id='partner_name']" position="replace">
    <span id="partner_name" t-out="record.name"/>
</xpath>
```

# Data
- Put seed/configuration records in `data/`; demo-only records in `demo/` and manifest `demo`.
- Use `noupdate="1"` only for records that should not be changed by module upgrades.
- Avoid hardcoded database IDs. Use `ref()` and external IDs.

# QWeb
- Use `@t-out` for escaped output. Do not add `@t-esc` or `@t-raw` in new `ir.ui.view` / website / portal QWeb (`t-raw` only if the value is already sanitized `Markup`).
- OWL component templates (`static/src/**/*.xml`) may still use `t-esc` — that is OWL, not `ir.qweb`.
- Inherit website/portal templates with `t-inherit` and precise XPath (see **XPath** above).
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
- faOtools apps and faotools.com: **always** follow `17-translations` in the same change (glossary / TM-first, do-not-translate list, no apps.odoo.com leak). Do not leave English fingerprint drift for a later task.

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

## Delivery gate — never leave shippable work behind (STRICT)

Every push / MR / “commit B*” is a **delivery moment**. Before pushing, account for *all* work that is
not yet on the target branch, and either **include it** or **warn about it by name** in the reply.
Staying silent about undelivered work is a failure, not a tidy scope.

1. `git status -sb` in every repo the request covers. Read **every** dirty and untracked path.
2. Enumerate work that is committed locally but **not pushed**: local branches and stashes whose
 content is missing from the target branch. Compare **by content** (are the added lines present on
 the target?), never by patch-id (`git cherry`) or commit subject — rebases and cherry-picks change
 patch-ids, and ids get reassigned, so both shortcuts confidently report the opposite of the truth.
3. Classify each item and act:
 - **belongs to this delivery** → include it in the commit / MR;
 - **foreign WIP** from another session → never touch it, and **warn**, naming the paths
 (`03-never-discard-wip`);
 - **genuinely local-only** → exclude it and say so;
 - **unsure** → ask once. Do not push it silently and do not omit it from the report.
4. **“Local-only” is a narrow allowlist**, meaning *must never reach production*: gitignored files
 (e.g. `*.local.mdc`), personal notes outside the repo, secrets / `.env`, throwaway scratch. A
 finished feature, fix, test, doc, or script is **never** local-only. A mode A commit is
 “committed locally, **queued for push**” — never call it local-only, in chat or in notes.
5. The push reply **must** contain a delivery report: what shipped, plus every local item that did
 **not** ship and why. “Pushed / merged” with no such list is an incomplete answer.
6. When the user says “push” and unshipped work plausibly belongs to it, default to **including**
 it and say what you included. Only clearly unrelated work may be left behind — with a warning.

Incident (2026-08-18): six walked febado workflows plus a finished local-Docker script change had
sat undelivered for weeks because walk notes called them “local-only” and the check compared commit
subjects. Recovery took two extra MRs. This gate exists so that never repeats.

## Before committing

0. Run the **delivery gate** above; a push must not start while shippable work is unaccounted for.
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

## 17-translations

_faOtools glossary-driven translations (apps, website, TM-first, no apps.odoo.com leak)_

# faOtools translations

Pull this rule for any task that adds or changes user-facing strings, `.po` / `.pot` files, website/QWeb copy, `module.description` content, `module.release.description` (public changelog), or languages.

Source of truth is **`support/support_translations/`** (glossary, do-not-translate list, fingerprinted TM). Odoo `.po` files and the DB loader are outputs, not the place to invent wording.

## Source language

- Source is **en_US**. Never translate into English. Never treat another language as source.
- Prepublishments stay English-only workspaces. Translations are re-applied after publish (loader hook), never authored on the origin by hand.

## TM-first

1. Update glossary / TM YAML first.
2. Run validators (protected terms, placeholders, XML, length).
3. Generate `.po` or let the loader apply website/DB terms.
4. MCP/UI spot fixes are the same loop: TM first, then apply. Never the reverse.

## When source strings change

If the task touches a module that already has `i18n/` or TM chunks:

- Adapt those translations in the same change (or flag the English fingerprint drift).
- Description / page copy edits must update TM for every shipped language, or leave an explicit drift item.
- New **19.0+** public `module.release.description` rows are TM-first in the same change (`tm/website/<tech>_<serie>.yaml` `releases`, then loader). Internal `notes` and `description_html` stay English. Older-serie rows that a 19.0 page actually shows (`migration_release_ids`) are translated too. A publish of 18.0-only is not a translation target. After publish follow `ai_rules_fao` `33-faotools-release`.
- Version ports (19.0 -> 20.0, including intermediate migration branches) **carry translations**; `copy()` keeps them, then refresh fingerprints.

## Do not translate

- Trademarks and product names: Odoo, faOtools, KnowSystem, module **display** names, technical names, slugs, URLs.
- Odoo edition names stay English: Enterprise, Community, Odoo.sh, Odoo Online (`odoo_editions` in `do-not-translate.yaml`; `check_dnt_editions.py`).
- Local technical terms: Bootstrap, Kanban, Omnibox, OWL, QWeb, JSON-LD, MCP, SMTP, IMAP.
- Customer review quotes.
- **faotools.com email templates are never translated.** Support-owned `mail.template` records (`support_connector`, `ticketing`, `support_teams`) pin `<field name="lang">en_US</field>`. Their `model:mail.template,*` `.po` terms stay empty. `check_mail_templates.py` fails the build if either side slips. Do not set `{{ object.lang }}`. Shipped `tools/` templates are the opposite: they must set `lang` to the recipient and fill subject/body terms.
- Generated store blobs: `resulted_description`, `static_description`, GitHub manifest `summary`. `module.description.short_summary` **is** translated on the website; store/GitHub paths stay `en_US` (`_prepare_description`, `get_short_summary()` with `lang=en_US`).

Ambiguous English (one word, several meanings) goes to the review queue with `ambiguous: true`. Ask rather than guess.

## Extraction and wording

- Extract `.pot` files through Odoo (`export_pot_via_odoo.py`). Do not hand-inject msgids (`ensure_pot_msgids.py` is not a source of truth). A `#: model_terms:ir.ui.view` reference must point at the view whose English arch contains the msgid (`check_pot_view_refs.py`).
- Do not split a sentence across a link. Keep the sentence as one term (`o_translate_inline` on a wrapper whose `<a>` has no `t-` attributes, or put the whole sentence inside the `<a>`). `check_link_fragments.py` flags the split.
- Russian action labels (buttons, wizards, menu actions) are perfective infinitive or imperative, never imperfective present (`Выбрать` not `Выбирать`). `check_action_labels` enforces the seed list.
- VAT stays verbatim only as a **legal identifier** (`EU VAT ID: PT332289761`, `VAT PT332289761`). The tax word in running copy still follows the glossary (VAT → НДС).
- File Manager is a UI label, not a trademark. Translate it (ru: Файловый менеджер).
- Product **display** names stay English. Exceptions that **are** translated: the `low_sales_report` menu label, and scoring **tab / field / filter** labels (`Customer Scoring`, `Vendor Scoring`) even though the manifest name stays English.
- `Industry` means business sector (ru Отрасль, pt Setor), not manufacturing. The glossary entry is `ambiguous: true`.
- No shipped msgid may have an empty msgstr except do-not-translate exact matches and support `mail.template` terms (`check_empty_msgstr.py`).

## Permanent gate

`support/support_translations/scripts/check_translation_coverage.py` is the entry point. It runs the detectors (`check_html_structure`, `check_frontend_modules`, `check_code_terms`, `check_action_labels`, `check_dnt_editions`, `check_link_fragments`, `check_mail_templates`) and, with `--live`, crawls faotools.com pages in `en_US` vs each shipped language. `devops/run_tests.sh … 19` runs the static gate. New modules and languages must pass it rather than a later cleanup pass.

Mechanisms the gate is built for:

- `_()` / `_t()` literals need `#. odoo-python` / `#. odoo-javascript` in every language `.po` (`check_code_terms.py`).
- Public OWL/JS modules must be listed in `ir.http._get_translation_frontend_modules_name` (`check_frontend_modules.py`).
- Runtime-created `translate=True` records (`website.menu`, `module.pic.name`) need a write path plus `check_db_records.py`.
- Odoo edition names (Enterprise, Community, Odoo.sh) stay English (`odoo_editions` in `do-not-translate.yaml`).
- Non-void HTML must not self-close (`check_html_structure.py`).

Visible leftover empty msgstrs (logger text, technical help) are a tracked follow-up, not this gate's `--full` default.

## Consistency

- One concept, one term, on **app UI and website**. Seed from current Odoo core/enterprise `.po`, then keep the glossary aligned after hub pulls / serie updates (two-axis drift checker).
- Prefer similar length to English for labels and headers (per-language thresholds in TM config).
- Arabic is RTL: check our SCSS/OWL, not only `.po` text.
- `summary_key_words`: locale keyword research, extend-only, never a literal translation.

## apps.odoo.com

Store HTML and manifests stay ASCII English. Render/push paths are pinned to `en_US`. Do not ship translated `index.html` to GitHub.

## Languages

Shipped (module list and website list stay identical):

- Bases: `ru_RU`, `fr_FR`, `de_DE`, `es_ES`, `pt_PT`, `nl_NL`, `it_IT`, `ar_001`
- Extended: `tr_TR`, `sv_SE`, `fi_FI`, `pl_PL`, `nb_NO`, `hu_HU`, `cs_CZ`, `da_DK`
- Country: `pt_BR`, `de_CH`, `en_GB`, `fr_BE`, `fr_CA`, `fr_CH`, `nl_BE`, `es_419`, `es_CL`

Source stays `en_US` (never a target). **No language in this program is post-launch.** Production URL prefixes are Phase 11 activation.

Country locales seed from the shipped **root** (`pt_PT` → `pt_BR`, `de_DE` → `de_CH`, `fr_FR` → `fr_BE` / `fr_CA` / `fr_CH`, `nl_NL` → `nl_BE`, `es_ES` → `es_419` / `es_CL`; `en_GB` from `en_US`), then every string is analyzed for that country. Do not copy the root TM. Do not treat variants as hreflang/switcher only.

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
| show odoo logs | faOtools: `docker compose -f faotools_env/local/run/<target>/compose.yml logs -f` (history: `~/env-sync/logs/<target>/odoo.log`). Febado: `febado/scripts/docker-dev.sh logs` (Cursor tab `febado Odoo logs`) |
| sync images/dbs | `faotools_env/local/env-sync.sh` (downloads **and** restores + neutralizes) |
| is \<target\> ready to launch? | `faotools_env/local/env-prepare.sh --check` |
| launch / start febado | febado `scripts/docker-dev.sh start` (no `--no-logs`) + febado local Docker rules — not `env-up`. Same Cursor log tab as faOtools (`febado Odoo logs`) |
| test febado module | febado `scripts/test.sh` (in-repo) |
| commit / commit A | prepare the **local** commit only — never push, no review (`16-commit-workflow`) |
| (in **febado**) commit / push \<one workflow\> | febado’s own Mode A/B rule decides — “push this workflow” stays **local** there |
| commit A1 | local commit only, **with** a Cursor review first |
| commit B / commit and push / push | **tests** → commit → push; review unspecified → **offer** a review before pushing |
| commit B1 / commit B2 | as B, **with** review (B1) / **without** review (B2) |
| prepare / make / publish a release | faOtools `module.release` on faotools.com via MCP `user-faotools` — `ai_rules_fao` `33-faotools-release` (`tools` / `odoo-apps-addons` only) |

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
2. **Logs.** Stream them in a **visible** Cursor terminal tab (agent shells stay
   hidden). faOtools: `env-up.sh <target>` with no `--no-logs` — it follows on a
   TTY and requests `<target> Odoo logs`. Febado: `scripts/docker-dev.sh start`
   with no `--no-logs` — it requests `febado Odoo logs` the same way
   (`~/env-sync/logs/reveal-in-cursor`). Also give the host log path when
   faOtools prints one.
3. **Links.** Always repeat the printed Odoo URL (with `admin` / `admin`), the
   Mailpit URL, and the database name — do not make the user hunt for them.
4. **Errors.** `env-up.sh` and Febado `docker-dev.sh start` print `ERROR`/`CRITICAL`
   lines logged since start. Report them instead of claiming a clean launch.

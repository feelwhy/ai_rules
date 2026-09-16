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

Do **not** ask for confirmation of an action the user already requested in this
message. If they said "commit" / "commit (a)" / "do X", do that now — the
post-chunk question is never "proceed with the commit?" / "proceed with X?".
If they said **commit B / B1 / B2** / “push” / “open the MR”, that request **is**
local Docker tests → check → fix → then MR (`16-commit-workflow`). Do not skip
the local run, and do not ask “proceed with the MR?” after it is green.

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
  (**except B / B1 / B2**: red → fix and re-run locally; green → continue to
  review + push. Do **not** skip the local run to avoid this stop, and do **not**
  treat GitLab as the test run.)
- anything irreversible or shared: push, deploy, branch switch, delete, live write
  (**except** the push / MR that is the last step of a B* the user already asked
  for, and only after local tests are green)
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
| `00-plain-replies` | Summary first, then only the asked-for facts; technical asks include the how |
| `00-index` | This map |
| `01-process-confirmation` | Step-by-step work with user confirmation |
| `02-docker-only` | Never host venv / `odoo-bin` |
| `03-never-discard-wip` | Do not stash/discard foreign WIP |
| `07-parallel-sessions` | Coordinate parallel chats on shared code and DBs |
| `06-verify-hypotheses` | Check the hypothesis before recommending |
| `18-xml-translate-html` | Never empty/`<i/>` icons in `xml_translate` HTML |
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
| `22-migrate-v19-to-v20` | Port module 19 → 20 (via saas-19.4); living rule + `tools/check_migrate_v20.py` |

## Companion repo

When the Cursor workspace includes `ai_rules_fao`, also follow its always-on map (`00-repo-map`, serie discipline, boundaries, local Docker, MCP, `17-translations`). Any task that changes copy, `.po`, `module.description`, or `module.release.description` must pull `ai_rules` `17-translations` as well. “Prepare / make / publish a release” must pull `ai_rules_fao` `33-faotools-release` (step 8 is TM-first changelog translation **and live loader apply** on 19.0+; never skip unless the user explicitly says to). HTML in those fields must follow always-on `18-xml-translate-html`.

## Editing rules

Edit `src/*.md` only, then run `python3 tools/sync_rules.py`. Do not hand-edit `.cursor/rules/*.mdc` or `AGENTS.md`.

## 00-plain-replies

_Summary first, then only the asked-for facts — technical asks include the how_

# Plain replies (strict)

This rule **outranks** default “be thorough / complete / helpful” instincts, including
restating the work, defining every term, or writing a standalone essay.

The user is here to **do or check one thing**. Answer that. Stop.

## 1. Summary first (mandatory)

Every reply **opens** with a short human-readable summary: **1–3 sentences**.

- A non-specialist can act on it (yes/no, the fact, the URL, what to do next).
- Ordinary words. No file dumps, no symbol lists, no “I checked…”.
- Then **stop**, unless one proof line or one next question is required.

```
Bad:  I reviewed the loader, the TM apply path, and the QWeb wrapper. The
      post-script does not write the cover; it only hits the hook via
      _update_translations when the lang was already active…
Good: Yes for a new demo. The homepage text is already copied from the
      template. The post-script only turns that language on.
```

A yes/no question gets **yes** or **no** in sentence one, then one line of what
that means for them.

## 2. Precision — no extra scope

- Answer **only** what was asked. Do not add alternatives, architecture, or
  “while we’re here” steps.
- Do **not** generalize (“in Odoo you typically…”, “best practice is…”) unless
  they asked for a general rule. Speak about **this** repo, serie, and check.
- One idea per sentence. Two cases = two short lines, not a blended paragraph.
- If a symbol is required, say what it does in the same sentence.
- One proof is enough (`path:line`, command + result, HTTP code). Not a tour.

## 3. Forbidden

- Restating the question, narrating the plan, or wrapping up what they already know
  (exception: while a plan is in progress, reprint it with `You are here` — `00-chunk-gate`)
- Status theater: “What ran”, “What I verified”, “Checked on …”, bullet inventories,
  coverage percentages — unless they asked for an audit
- Hedging and padding: “ready enough”, “mostly yes”, “for the items you listed”
- Repeating login / URLs / Mailpit / DB every turn
- Explaining why the answer is short, or apologizing for length
- Teaching Odoo / Python / Docker basics they did not ask for
- Dense jargon as a substitute for a short answer

## 4. When they want to check

Give the URL (and login **once** if they do not have it). Do not list every string
or recap the pipeline. If something is **not** ready **and they did not already
ask you to do it**, say that in one sentence and ask to proceed with the missing
step. If they already said commit / commit (a) / close the case, do the pin and
local commit — do not ask.

## 5. When offering options

Any time the user is given a choice — in reply text **or** a multiple-choice
question form — every option carries its **pros and cons** (one short line each
is enough). An option list without trade-offs is not a decision aid.

- In a form, put the pros/cons in the option label or the question prompt so
  they are visible at pick time.
- Still recommend one option and say why in one sentence.
- Options nobody should pick are left out, not listed with empty cons.

## 6. Length

Default: **summary + at most a few sentences**. A table or file list only when it
**is** the deliverable.

Chunk-gate reports: summary first, then the four required lines — not an essay
under each heading. When a plan is in progress, add the numbered reprint with
`You are here` (and any user-commanded `skipped` highlights).

## 7. Technical asks include the how

When you ask the user to do a technical step, **give the how in the same
reply** — exact file or command, one undo, and which machine it hits
(Windows vs WSL). Short. No lecture.

Do not write a bare “block X / clear Y / restart Z”.

## 01-process-confirmation

_Work step-by-step and confirm with the user before irreversible or multi-phase actions_

# Process confirmation

For non-trivial work (multi-file changes, deploys, branch switches, deletions, migrations, publishes):

1. **State the plan** in a short ordered list before doing irreversible steps.
2. **Confirm with the user** at phase gates (delete duplicates, push remotes, switch shared checkout serie, `docker compose down`, live writes).
3. **Do one phase at a time** when the plan says so; do not batch “while I’m here” deletions or refactors. Follow the approved numbered plan, or change that list and follow the new one — do not invent a parallel plan (`00-chunk-gate`).
4. **Report outcomes** with concrete evidence (commands run, paths changed, test results) — not “should be fine”.
5. If blocked (foreign WIP, another chat on the same DB/branch, missing permission, unclear target serie), **stop and ask** instead of improvising. Do not skip or mark a plan point done — blocked is not a miss (`00-chunk-gate`, `07-parallel-sessions`).

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
permission. Coordinating those other chats (same DB, same branch) is
`07-parallel-sessions`.

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

## 07-parallel-sessions

_Coordinate parallel chats that share a checkout or database — do not collide_

# Parallel sessions (shared code and databases)

Several Cursor chats and the human share the same worktrees and the same
local / live databases. **This chat is never the only writer.** Before you
mutate shared source or a shared DB, take the other session's work into
this chat and sequence your change after it.

Companion: `03-never-discard-wip` (do not discard). This rule is about
**not colliding** and **not hiding** the other chat's branch or DB state.

## When this applies

Any of:

- editing files another chat may also be editing
- `git checkout` / `env-serie.sh` / branch or serie switch
- `env-up` (`--fresh`, `-u`, `-i`, `--test`, restore, neutralize)
- Febado stack start/recreate, or a restart of a target another chat is using
- live MCP / production writes (faotools.com, master, life)

Read-only search does not need this gate.

## Take the other chat into this one

Do not start as if the tree and DB are yours. Before the first mutation:

1. `git status -sb` on every repo this task would touch. Classify dirty /
   untracked paths: **this chat** vs **foreign / unknown**.
2. Read the current branch (do not assume it). A branch you did not check
   out in this chat is someone else's working branch.
3. See which Docker target is up (`env-up` ports, Febado `:23069`, open
   terminals). A target another chat launched is **their** DB until the
   user says otherwise.
4. If agent transcripts or the user mention another chat on the same
   module, branch, or target — read that work and treat it as the base.
   Cite it as `[short title](<transcript-uuid>)`.

Then tell the user what you found (paths, branch, target) in one or two
sentences. Do not silently overwrite it.

## Database: changes must be consequential

Two chats must not write the same DB at the same time.

- Do **not** `--fresh`, restore, neutralize, drop, or recreate a DB
  another chat is using.
- Do **not** `-u` / `-i` / `--test` / shell writes on that target while
  the other chat is mid-change — wait, or ask which chat owns it.
- Live MCP: do not write the same records another chat is editing
  (prepublishment, `module.release`, tickets, website views).
- If you must continue on the same DB, **sequence**: read the current
  rows / last write, then apply this chat's change on top. Never reset
  to an older state to "start clean".

`--restart` of **this** chat's last target is fine. Restarting a target
another chat is testing is not — ask.

## Branches: do not spoil the other chat

One checkout = one visible branch for every chat and every bind-mounted
Odoo.

- Do **not** switch branch / serie to serve this chat if another chat's
  WIP or intended branch is checked out (`03-never-discard-wip`,
  `ai_rules_fao` `01-hub-serie`).
- Do **not** hide their branch by parking this work only in a side
  worktree while the shared tree moves.
- After any **user-approved** switch, say which chats / running
  containers now see different code.

## If you would collide

Stop. Name the overlap (repo, paths, branch, DB/target). Ask which chat
owns the next write. Do not stash, switch, or "fix" the conflict by
discarding (`03-never-discard-wip`).

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
| “commit B”, “commit mode B”, “commit and push”, “push” | **B** | yes, **after** local tests | **local Docker, then fix** | **offer** a Cursor review before pushing |
| “commit B1” | **B1** | yes, **after** local tests | **local Docker, then fix** | **review first** (no need to ask) |
| “commit B2” | **B2** | yes, **after** local tests | **local Docker, then fix** | no review — push directly |

- **Bare “commit” means mode A.** Never push in mode A — not “while I’m here”, not because the
  branch looks ready.
- **Never re-ask.** If the user said commit / commit A / commit (a) / commit the case, do the
  local commit. Do not ask “proceed with the local commit?” or wait for a second confirmation.
- Mode A does not require a test run, but never commit knowingly broken code, and say plainly
  whether tests were run.

### B / B1 / B2 — local tests → check → fix → then MR (HARD)

Order is fixed. Do not reorder. Do not skip. This is the whole B* request — do not
stop after tests to ask “proceed with the MR?”, and do not skip tests to finish the
push.

1. **Run** the relevant tests **locally in Docker** for every changed module
   (`env-up.sh demo<N>[e] --test <module>`, `support/devops/run_tests.sh`,
   febado `scripts/test.sh`).
2. **Check** the real output in this chat (command + pass/fail).
3. **Fix** failures and **re-run the same local command** until green. Un-runnable →
   stop and ask. Do not push.
4. **Then** review (B1 / offered B) → commit if needed → push / open the MR.

**GitLab CI is not step 1.** Watching a pipeline does not replace the local run.
**No local test command output in this chat → no `git push`, no MR, no MWPS.**
Speed, chunk-gate, `:23069` going into test mode, “CI will catch it”, or “Mode A
already committed” are not exceptions. After `test.sh`, restart the Febado stack
if the user still needs the browser.
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
1. On **B / B1 / B2**: finish the **local tests → check → fix** sequence above before
   any push or MR. Do not commit knowingly broken behavior.
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
- New **19.0+** public `module.release.description` rows are TM-first **and loader-applied on faotools.com in the same change** (`tm/website/<tech>_<serie>.yaml` `releases`, then MCP `_apply_description`). The release is not done while `/ru/` still shows English. Skip that apply only if the user **explicitly** says to skip translations. Internal `notes` and `description_html` stay English. Older-serie rows that a 19.0 page actually shows (`migration_release_ids`) are translated too. A publish of 18.0-only is not a translation target. After publish follow `ai_rules_fao` `33-faotools-release`.
- Website/ticket FAQ copy lives in `tm/website/faqs/` (overlay). KnowSystem article records stay English. Do not enable KnowSystem Multi Languages. Store `/docs` / `/knowsystem` stay English.
- Version ports (19.0 -> 20.0, including intermediate migration branches) **carry translations**; `copy()` keeps them, then refresh fingerprints.
- **QWeb / demo restyle is a translation change.** If you change English in a `<template>`, `string=`, `title=`, or Layer 1 demo XML, the `.pot` msgid must be the **new** `xml_translate` key — not the old `<strong>…</strong>` / icon wrapper. `_update_translations(overwrite=False)` leaves the new term empty on an existing DB (incident 2026-09-09: Appointments `Any` / `Select` / more details). Same job: glossary or TM, regenerate `.po`, and the empty-term fill (`ir.module.module` hooks in `support_translations`, `odootools_demo`, every tools / `odoo-apps-addons` module that owns QWeb `<template>` views). `check_view_term_restyle.py` fails when XML is bare and the pot still only has the old tagged msgid. Demo values must stay in the module `.pot` (`demo_lint`).

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

`support/support_translations/scripts/check_translation_coverage.py` is the entry point. It runs the detectors (`check_html_structure`, `check_frontend_modules`, `check_code_terms`, `check_action_labels`, `check_dnt_editions`, `check_link_fragments`, `check_mail_templates`, `check_view_term_restyle`) and, with `--live`, crawls faotools.com pages in `en_US` vs each shipped language. `devops/run_tests.sh … 19` runs the static gate. New modules and languages must pass it rather than a later cleanup pass.

Mechanisms the gate is built for:

- `_()` / `_t()` literals need `#. odoo-python` / `#. odoo-javascript` in every language `.po` (`check_code_terms.py`).
- Public OWL/JS modules must be listed in `ir.http._get_translation_frontend_modules_name` (`check_frontend_modules.py`).
- Runtime-created `translate=True` records (`website.menu`, `module.pic.name`) need a write path plus `check_db_records.py`.
- Restyled QWeb must not leave only the old tagged `.pot` msgid (`check_view_term_restyle.py`). Existing DBs need `_fill_empty_view_translations`; a `.po` update alone is not enough.
- Odoo edition names (Enterprise, Community, Odoo.sh) stay English (`odoo_editions` in `do-not-translate.yaml`).
- Non-void HTML must not self-close (`check_html_structure.py`). **Always** follow `18-xml-translate-html`: never empty `<i></i>` / `<i/>` (Odoo `xml_translate` re-serializes them and HTML5 swallows the page, including `en_US`).

Visible leftover empty msgstrs (logger text, technical help) are a tracked follow-up, not this gate's `--full` default.

## Consistency

- One concept, one term, on **app UI and website**. Seed from current Odoo core/enterprise `.po`, then keep the glossary aligned after hub pulls / serie updates (two-axis drift checker).
- Prefer similar length to English for labels and headers (per-language thresholds in TM config).
- Arabic is RTL: check our SCSS/OWL, not only `.po` text.
- `summary_key_words`: locale keyword research, extend-only, never a literal translation.

## Closing an "empty msgstr" backlog — do it exhaustively, not in samples

A request to "translate the missing strings" means **every** shipped language on **every**
touched (or scanned) module, not the 8 base languages, not the "important" ones. Treat the
8-language set as a sampling shortcut only when the user says so explicitly; otherwise scope
to the full list in **Languages** below (currently 42 codes) from the start, so the work is not
redone after someone points out the narrower scope was wrong.

1. **Scan against `.po` msgstr, not against a fixed language subset.** Build the worklist from
 `const.SHIPPED_LANGS` / `const.PO_STEM_TO_LANG`, not a hand-typed list — a hand-typed list
 silently drops languages.
2. **Map language code -> file stem before touching a file.** `PO_STEM_TO_LANG` inverts to
 `LANG_TO_STEM`; a batch script keyed by full lang code (`el_GR`) that assumes the file is
 `el_GR.po` will silently miss `el.po`. After every batch apply, list the file stems the batch
 actually touched and diff them against the language list it claimed to cover.
3. **A msgstr of only whitespace is not "empty."** `msgstr " "` is a deliberate placeholder
 (e.g. an Arabic RTL glyph with no visible text). A completeness check based on `str.strip()`
 will re-flag it forever; check for `msgstr ""` (true empty) and treat a non-empty whitespace
 value as already decided.
4. **Before filling any `mail.template`-sourced term, check the exemption.** A `.po` entry whose
 **only** `#:` reference is `model:mail.template,` on a support-owned template
 (`support_connector`, `ticketing`, `support_teams`) must stay empty (see **Do not translate**).
 Read the template's `lang` field and run `check_mail_templates.py` before and after the batch —
 filling one of these is a regression, not progress, even though it looks like closing a gap.
5. **Source words that duplicate Odoo core verbatim from core's own `.po`.** When a msgid is a
 literal reuse of a core model/field/product display name (its `#:` ref is a core `ir.model` /
 `ir.model.fields` / `product.template` xmlid, not a module-owned one), pull the translation from
 that same string in `odoo/addons/<module>/i18n/` (or `odoo/odoo/addons/base/i18n/` for `base`)
 instead of inventing wording — keeps the term consistent with the rest of the UI. Fall back to
 the parent locale for a country variant missing the entry (e.g. `fr_CA` -> `fr`), and hand-fill
 only the handful of languages core does not ship at all.
6. **Verify with an independent re-scan, not the apply script's own report.** "0 missing" from
 the batch-apply tool only means every msgid it was given landed somewhere; it does not mean the
 module has zero empty `msgstr` left (a string outside that batch, or one the original scan
 missed, can still be empty). Re-parse every touched module's `.po` files with `polib` and
 recount true empties before calling a module done.
7. **Finish with one full-repo re-scan across every repo that ships `.po` files** (`tools`,
 `support`, `system`, `odoo-apps-addons`, `life`) against the complete language list, cross-
 referenced against `do-not-translate.yaml` and the mail-template exemption, before reporting
 "all languages done." A per-module "looks complete" is not the same claim.

## apps.odoo.com

Store HTML and manifests stay ASCII English. Render/push paths are pinned to `en_US`. Do not ship translated `index.html` to GitHub.

## Languages

Shipped (module list and website list stay identical):

- Bases: `ru_RU`, `fr_FR`, `de_DE`, `es_ES`, `pt_PT`, `nl_NL`, `it_IT`, `ar_001`
- Extended: `tr_TR`, `sv_SE`, `fi_FI`, `pl_PL`, `nb_NO`, `hu_HU`, `cs_CZ`, `da_DK`
- Country: `pt_BR`, `de_CH`, `en_GB`, `fr_BE`, `fr_CA`, `fr_CH`, `nl_BE`, `es_419`, `es_CL`
- Additional: `el_GR`, `lt_LT`, `et_EE`, `hr_HR`, `ro_RO`, `sr@Cyrl`, `bg_BG`, `sl_SI`, `lv_LV`, `vi_VN`, `ko_KR`, `ja_JP`, `zh_CN`, `hi_IN`, `bn_IN`, `id_ID`, `ms_MY`

Only Odoo `res.lang` codes. Serbian is Cyrillic (`sr@Cyrl`). Chinese is Simplified Mandarin (`zh_CN`) only. Source stays `en_US` (never a target). **No language in this program is post-launch.** Production URL prefixes are Phase 11 activation.

Country locales seed from the shipped **root** (`pt_PT` → `pt_BR`, `de_DE` → `de_CH`, `fr_FR` → `fr_BE` / `fr_CA` / `fr_CH`, `nl_NL` → `nl_BE`, `es_ES` → `es_419` / `es_CL`; `en_GB` from `en_US`), then every string is analyzed for that country. Do not copy the root TM. Do not treat variants as hreflang/switcher only.

## 18-xml-translate-html

_Never let xml_translate emit self-closing non-void HTML (empty FA icons break pages)_

# xml_translate HTML — never self-close non-void tags

Odoo `xml_translate` serializes a truly empty `<i></i>` / `<span></span>` as `<i/>` / `<span/>`. HTML5 ignores the `/`, so the tag stays open and **swallows the rest of the page** — including `en_US`. Incident 2026-08-23: app pages on faotools.com rendered as leftover icon glyphs.

## Hard ban (English source, TM, MCP, QWeb, defaults)

Never write:

- `<i class="fa …"/>`
- `<i class="fa …"></i>` (empty pair)
- empty `<span></span>`, `<b></b>`, `<em></em>` used as icons/wrappers

Always keep a space inside the pair:

```html
<i class="fa fa-plus text-success mr8"> </i>
```

Same for any other non-void wrapper. Void tags (`<br/>`, `<img/>`) stay void.

## After every xml_translate write

1. Close English with `close_self_closing_html` (`me_check_xml` / `validators`). The loader `_write_xml` must do this **after** `update_field_translations` — that call is what re-opens the hole.
2. Do not run TM `_apply_all` without closing English again (`close_live_html_void.py`).
3. App-page QWeb must use `safe_website_markup`, never raw `Markup()`, so a leftover `<i/>` cannot ship in HTML.

## Tests that must stay green

- `support_translations:TestXmlTranslateHtml`
- `modules_website:TestSafeWebsiteMarkup`
- `modules_website:TestAppPageFaqHttp`
- `validators` `html_void` / `check_html_structure`

A change that reintroduces empty `<i></i>` or drops the post-apply closer has failed, even if the Russian page still looks fine.

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

## 22-migrate-v19-to-v20

_Checklist and transforms for migrating an Odoo module from 19.0 to 20.0 (via saas-19.4)_

# Odoo 19 -> 20 migration

Apply these transforms when porting a module to 20.0. Assumes the module is already 19-clean
(see `21-migrate-v18-to-v19`). Keep public model/field/XML-ID names stable unless the upgrade
renames them. **Do not write `20.0.x.y.z` while the stand-in is a saas branch** — see
**Manifest version** below. Override in the module, never edit `odoo/`.

**This rule is living.** Every fact below is source-confirmed against a stated pin. When a port
reveals a new fact: decide the fix, apply it, prove it, then write the fact here and into
`tools/check_migrate_v20.py` in the same job. Pause only for a current-serie defect that must
be fixed on 19.0 first, or when there is a real choice of successor.

Tested pins (2026-09-12, pre-release):

| Ref | SHA |
|---|---|
| `odoo@saas-19.4` | `3630379f63633612e5a9e8d435deecbe26eaa15a` |
| `enterprise@saas-19.4` | `8d73a02a8ba9a99fb41b2cd01b1680c6ded4b837` |

Full evidence: `ai_rules_fao/docs/20-saas-19.4-delta.md`.

## Read this before any 19 -> 20 port

### The saas branches are independent forks, not a chain

`saas-19.1` … `saas-19.4` are **not** ancestors of one another, and none is a descendant of `19.0`.
Their common ancestor with `19.0` is the release cut. Measured on the pins above: **8638 commits
exist in `19.0` that are absent from `saas-19.4`**.

Consequences:

- Commit counts per "boundary" measure nothing. Compare **trees**, not ancestry.
- **A fix present on `19.0` may not be on the target.** Never assume a 19.0 bugfix travelled; check
  the target tree.
- Attribute a change to the first serie whose tree lacks what you use.

### Release notes are not a porting signal

Across 19.1-19.4 the official notes contain **one** technical entry. Every other break in this rule
was found by static existence checks. Read the notes for discovery, then confirm in source — and
never wait for a note to tell you something broke.

### Silent failures outnumber loud ones

Most of the 19 -> 20 damage does not raise:

- An override of a hook upstream deleted is **never called**. No error, no warning, no failed install.
- A write to a removed field can be **silently dropped** (see `ir.attachment.datas`).
- A string-keyed field name (group-by, domain, selection) just stops resolving.

Tests and warning gates do not catch these. Run `tools/check_migrate_v20.py` and read its output.

## Dead-override check (run this first, every module)

For **every** override of a core hook, assert the hook still exists on the target. Bind the check to
the **inherited model or imported class**, never to a global name search: a surviving name on an
unrelated model hides a dead hook, and a module-internal `super()` chain looks dead because its name
never existed upstream.

Confirmed dead hooks on `saas-19.4`:

| 19.0 hook | 20.0 successor |
|---|---|
| `mail.thread._track_subtype(initial_values)` | `_track_log_get_default_subtype(track_init_values)` — renamed parameter; returns an empty `mail.message.subtype` recordset, not `False` |
| `res.users.SELF_READABLE_FIELDS` / `SELF_WRITEABLE_FIELDS` | **delete the override**; set `user_writeable=True` on the field itself |
| `mail.message._extras_to_store` | `_store_extra_fields(res, *, format_reply)` |
| `mail.message._to_store_defaults` | `_store_*_fields(self, res: Store.FieldList)` family |
| `mail.thread._get_store_message_update_extra_fields` | `_store_message_fields` — moved to `mail.message` |
| `res.users._init_store_data` | `_store_init_fields` / `_store_init_global_fields` |
| `ir.attachment._inverse_datas` | `_inverse_raw` |
| `BaseModel._check_access(operation)` | **name survives**, never called. `_access_domain` + `res_access_*` (see below) |

`tracking=True` on a field is **still valid** (`mail.track.mixin._valid_field_parameter`).

### `_check_access` is dead even though the name survives

`check_access` / `has_access` / `_filtered_access` are `@typing.final` at saas-19.4
(`odoo/orm/models.py:3371`) and call `_access_domain`. `_check_access` still exists
(`:3499`) but is `@deprecated("Since 20.0, use Model._access_domain instead")` and is
**never called**. Overriding it is a silent miss: a write that used to raise
`AccessError` succeeds.

Observed on `20_14` Gx.7: `TestCloudsFolderPreparing.test3_security_rights_check`
`AssertionError: AccessError not raised` at `rule_folder_1.with_user(...).write({})`.
Gx.2 on 19.0 is green for the same test.

Successor: match `ir.attachment` / `mail.activity`:

1. `_access_domain_heavy = True`
2. Computed searchable `res_access_read` / `res_access_write`
   (`groups=fields.NO_ACCESS`, `compute_sudo=True`,
   `depends_context=('uid',)` plus every field the old `_check_access` read —
   `depends_context=('uid',)` alone caches a True after the first
   `has_access` and misses a later `access_user_ids` / `rule_id` write)
3. `_compute_res_access` / `_search_res_access` — body of the old `_check_access`
   **minus** `super()` ACL
4. `_access_domain(operation)` = `super() & Domain(f"res_access_{op}", "=", True)`
   with create/unlink mapped to write
5. Delete `_check_access`

In compute, use `self.sudo(False)` before `_inaccessible_comodel_records` (that
helper no-ops when `env.su`). Do **not** skip checks because `compute_sudo` makes
`env.su` True.

`has_access('read')` short-circuits on `env.transaction.access_read` (keyed by
uid). `_check_access` re-evaluated every call; after the port, a write that
changes the data `_access_domain` reads must
`self.env.transaction.invalidate_access_cache(self._name)` or the next read
keeps the old True. Core mail tests do the same after changing the related
record.

An override that only passed context into `super()._check_access` (e.g.
`cloud_base` `ir.attachment` `ir_attachment_security`) becomes the same context on
`_inaccessible_comodel_records`.

In `tools@19.0`: `cloud_base` (folder + attachment), `message_edit`,
`joint_calendar`, `business_appointment`. Checker kind is `dead-hook` via
`DEAD_DESPITE_EXISTING` — a name-exists check reports clean.

### x2many to `res.users` hides inactive rows

saas-19.4 Many2many read (`odoo/orm/fields_relational.py`) splits out inactive
comodel rows (`active_test=True` by default). The write still stores them; the
next `record.user_ids` is empty. 19.0 returned OdooBot / archived users on the
same field.

A security compute that builds an allow-list from a Many2many to `res.users`
(or `res.groups` → users) must read
`record.with_context(active_test=False).<m2m>`. Otherwise a write of
`base.user_root` (inactive) is a silent no-op: stored restriction stays `[]`,
`has_access` stays True. Observed on `20_14` Gx.7 Case 5
(`clouds.folder._compute_restricted_users`). Not a 19.0 defect — Gx.2 is green.

Do **not** "fix" this by pointing the test at an active user. That drops the
19.0 meaning (an archived-only restriction still locks the folder).

No reliable checker kind: a `Many2many("res.users")` grep is every user-tags
field. Read the compute.

### Ordering hooks: dead before 19.0, same successor on both refs

These three are `stale-override`, not `dead-hook` — absent from core at **both** refs, so they were
already doing nothing on 19.0. The successor is the same on 19.0 and saas-19.4, which is why the fix
belongs on the current serie and ports over unchanged.

| Removed hook | Successor |
|---|---|
| `_generate_order_by(order_spec, query)` | 19.0: `_order_field_to_sql(alias, field_name, direction, nulls, query)`. saas-19.4 **dropped `query`**: `_order_field_to_sql(table, field_expr, direction, nulls)` (`odoo/orm/models.py:4651`). `_order_to_sql` is `_order_to_sql(table, order)` |
| `_generate_order_by_inner(alias, order_spec, query, …)` | same |
| `_inherits_join_calc(alias, fname, query)` | `_field_to_sql(alias, field_expr, query)` still exists (query optional) |

The 19.0 lowercase hook does **not** port unchanged. Copying it onto saas raises
`TypeError: …_order_field_to_sql() missing 1 required positional argument: 'query'`
as soon as anything searches the model (observed `20_4` Gx.6 while loading
`account` groups). Successor matches core `mailing` / `documents`:

```python
# saas-19.4 — table is TableSQL; append group-by like mailing.state
def _order_field_to_sql(self, table, field_expr, direction, nulls):
    if field_expr == "name":
        sql_field = table.name
        table._query._order_groupby.append(sql_field)
        return SQL("LOWER(%s) %s %s", sql_field, direction, nulls)
    return super()._order_field_to_sql(table, field_expr, direction, nulls)
```

Tests that called `_order_to_sql(order, records._as_query(...)).code` become
`_order_to_sql(query.table, order)._sql_tuple[0]` (saas `LiteralSQL` has no
`.code`). Checker `python-api` flags a leftover `query` on the def and a
string-first `_order_to_sql(`.

19.0 still uses the five-arg form (`knowsystem`, `odoo_password_manager`,
2026-09-12). Do not change 19.0.

**Assert the emitted SQL, not the row order.** A "mixed-case rows come back sorted" check cannot
tell a working lowercase hook from a dead one on our databases: they are created with `en_US.utf8`
collation (`datcollate` on every `env-sync` target), where Postgres already ignores case while
ordering. Pick probes whose byte order and case-insensitive order genuinely differ, and assert
`LOWER(` in `_order_to_sql(...).code`; keep the row-order assertion only as a smoke test that the
term is valid SQL.

### Portal sharing field list: current-serie cache, both refs

`project.task._portal_accessible_fields` is `@ormcache(cache='stable')` at **both** pins
(19.0 `:1048`, saas-19.4 `:1077`). Portal `fields_get` / `_has_field_access` then keeps only that
frozen set. The sharing form arch is ordinary inherited XML and is **not** filtered the same way.

`task_custom_fields` extends `TASK_PORTAL_READABLE_FIELDS` / `TASK_PORTAL_WRITABLE_FIELDS` from live
`custom.task.field` rows (`portal_edit_placement`). `_generate_xml` writes those names into
`project.project_sharing_project_task_view_form`. The stable cache does not invalidate on that
write. A portal collaborator then gets `TypeError: "project.task"."x_oz_tsk_N" field is undefined`
in `Field.parseFieldNode` (arch has the node, `get_views` `models.fields` does not).

This is a defect on the **current** serie (ledger `source_serie_defects` id 6). Do **not** paper it
over on 20 only (do not drop the field from the sharing arch, do not sudo `fields_get` for portal).
Fix on 19.0: invalidate `project.task._portal_accessible_fields` from `custom.task.field`
create/write/`_generate_xml`. A process restart only refreshes the cache until the next write.

The checker cannot see this: both hooks exist at both refs, and a grep for `TASK_PORTAL` + `search(`
would stay red after a correct invalidate-on-write. Prove it with HTTP `get_views` on the **running**
worker as a portal user (a new `odoo shell` process has a fresh cache and hides the hole). 19.0
demo data leaves `portal_edit_placement` empty, so the sharing form never injects `x_oz_tsk_*` and
the hole stays latent there.

## Python

### Manifest version — drop the serie prefix on the saas stand-in

`odoo/modules/module.py` `check_version` (`:452`) sets `installable=False` and logs a warning
when the adapted version does not start with `release.major_version + '.'`. On the
`faotools/env-demo-20:current` image that string is **`saas~19.4`**, not `19.0` and not `20.0`.
Measured on that image at the pin above:

| Manifest `version` | `adapt_version` | `installable` |
|---|---|---|
| `19.0.1.0.2` (every `tools` module on 19.0) | `19.0.1.0.2` | **False** |
| `20.0.1.0.2` (what this rule used to say to write) | `20.0.1.0.2` | **False** |
| `1.0.2` (three parts, no serie) | `saas~19.4.1.0.2` | True |

A serie-prefixed version is accepted only on that exact serie. Writing `20.0.x` therefore
breaks the module on the stand-in we actually run, and it fights `ai_rules_fao`
`11-manifest-version`. The port exception is:

1. **Gx.3 (saas-19.4):** drop the serie prefix. `19.0.1.3.33` → `1.3.33`. Leave a one-line
   comment that phase 8 / `Fx` re-prefixes. The checker reports leftover prefixes as
   `manifest-version` when `--odoo-ref` is a `saas-*` branch.
2. **Fx / phase 8 (real 20.0):** re-prefix to `20.0.x.y.z`. That is the one bump
   `11-manifest-version` allows for this program.

Do not invent a fourth number. The tail after the serie is what stays.

### `version_info[0]` is a string on a saas branch

`odoo.release.version_info` on saas-19.4 is `('saas~19', 4, 0, 'final', 0, '')`. Code that
does `"%s.0" % version_info[0]` or `int(version_info[0])` is wrong on the stand-in. Treat a
`saas~N` major as the **next** released major (`20.0`). Example:
`odootools_demo` `_demo_ticket_serie`.

### `res.users` self-access: field parameter, not a list

`SELF_READABLE_FIELDS` / `SELF_WRITEABLE_FIELDS` are gone (13 and 8 core definitions at 19.0, zero
now). Access is decided per field by `user_writeable`.

```python
# BEFORE (19.0) — property override on res.users
@property
def SELF_WRITEABLE_FIELDS(self):
    return super().SELF_WRITEABLE_FIELDS + ["my_pref_field"]

# AFTER (20.0) — drop the override entirely, declare on the field
my_pref_field = fields.Boolean(string="My Preference", user_writeable=True)
```

### `ir.attachment.datas` removed — and writes are swallowed

`datas` no longer exists. `_check_contents` pops it and emits `warnings.warn("Use raw, datas has
beeen removed")`, so a `create`/`write` carrying `datas` **succeeds and stores nothing**.

This is also an encoding change: `datas` was base64. `raw` is a `BinaryValue`
(`odoo.tools.binary`), not a `bytes`. Read the payload as `record.raw.content`.
A write still accepts bytes.

```python
# BEFORE
self.env["ir.attachment"].create({"name": fname, "datas": base64.b64encode(content)})
# AFTER
self.env["ir.attachment"].create({"name": fname, "raw": content})
# READ
payload = record.raw.content  # bytes; record.raw itself is BinaryValue
```

Audit every attachment write, not just the ones a grep highlights. Encode to
base64 only at the boundary that still needs it.

saas `_to_http_stream` (`odoo/addons/base/models/ir_attachment.py:990`) is a
different hole from `datas`. After `store_fname` it does
`elif self.url: return Stream(type='url', url=self.url)`, then
`data = self.raw.content`. 19.0 used `elif self.db_datas` and streamed
`self.raw` as bytes — it never redirected a URL-only attachment. A synced
`type=url` row with no filestore file therefore **sends the browser to the
cloud URL** unless the module overrides `_to_http_stream`. Observed `20_14`
Gx.8: File Manager `/web/image/<attach_id>` and Documents FileViewer
`/web/image/<docId>?model=documents.document`. Successor in `cloud_base`:
override, fetch only when `_cloud_http_may_fetch` allows (`download` /
`cloud_preview` / preview group / Documents model or path), and return an
empty `type=data` stream for a bare list/kanban thumb.

### `odoo.http` is a package — `Stream` / `content_disposition` moved

19.0 is a single `odoo/http.py`. saas-19.4 is `odoo/http/` (`__init__.py` at the pin). That
file re-exports `request`, `Controller`, `route`, `Response`. It does **not** re-export
`Stream` or `content_disposition` — those live in `odoo/http/stream.py`.

Observed on the saas-19.4 image during `20_14` Gx.6: `ImportError: cannot import name
'Stream' from 'odoo.http'` while loading `cloud_base`. A leftover
`from odoo.http import content_disposition` fails the same way. Checker kind is
`python-api` (import form). In `tools@19.0` this is `cloud_base` (3 sites) and
`short_urls` (1).

```python
# BEFORE
from odoo.http import Stream, content_disposition, request
# AFTER
from odoo.http import request
from odoo.http.stream import Stream, content_disposition
```

Keep `from odoo.http import request` / `Controller` / `route`. Do not "fix" those.

### `request.website` is gone — use `request.env.website`

19.0 `website.ir.http` assigned `request.website = website.with_context(...)`.
saas-19.4 deleted that assignment. The current website is
`request.env.website` (also `self.env.website` on a Controller). `website=True`
on the route still puts `website_id` in the context.

Observed `20_9` Gx.7: every `odoo_typo_reporter` jsonrpc test died
`AttributeError: 'Request' object has no attribute 'website'` despite
`website=True`. Same leftover on `short_urls` and `website_url_translations`.
Successor: `request.env.website`. Checker `python-api` greps `request.website`
(does not match `request.env.website`).

```python
# BEFORE
website = request.website
# AFTER
website = request.env.website
```

### `StaticList._replaceWith` is gone — use `list.set(ids)`

19.0 `web` `StaticList._replaceWith(ids, { reload })` (`static_list.js:1081`)
wrote a SET command and optionally `_loadRecords`. saas-19.4 deleted the
method (zero `_replaceWith` in the tree). The public successor is
`set(resIds)` (`:455`): `x2ManyCommands.SET` plus `_onUpdate`, and it
already runs inside `model.mutex`.

Observed `20_10` Gx.3: all four checklist field widgets
(`task_checklist` / `crm_checklist` / `sale_order_checklist` /
`purchase_order_checklist`) called `_replaceWith(..., { reload: true })`
then `_onUpdate` inside a second mutex. Successor: `return this.list.set(currentIds)`.
Do not wrap another mutex. Checker `js-symbol` greps `._replaceWith(`.

```js
// BEFORE
return this.list.model.mutex.exec(async () => {
    await this.list._replaceWith(currentIds, { reload: true });
    await this.list._onUpdate();
});
// AFTER
return this.list.set(currentIds);
```

### `ir.config_parameter.get_param` / `set_param` are gone

Both methods exist at 19.0 (`odoo/addons/base/models/ir_config_parameter.py`) and are **absent**
at saas-19.4 (zero `def get_param` / `def set_param` in the tree). The successor is a typed
pair: `get_str` / `get_bool` / `get_int` / `get_float` and `set_str` / `set_bool` / `set_int` /
`set_float`. Defaults are typed too (`get_str(key, default='')`, `get_bool(key, default=False)`).

Observed on the saas-19.4 image during `20_2` Gx.8 neutralize: `AttributeError` on `set_param`.
In `tools` this is **166 production + 55 test call sites** (`get_param` 153, `set_param` 68),
plus 35 in `system` and 5 in `odoo-apps-addons`. The checker kind is `python-api`.

```python
# BEFORE
icp.get_param("web.base.url", default="http://localhost:8069")
icp.set_param("my.flag", "True")
# AFTER
icp.get_str("web.base.url", "http://localhost:8069")
icp.set_bool("my.flag", True)   # or set_str if the value is really a string
```

Do not keep `safe_eval(get_param(..., "False"))` for a boolean — that is the 19.0 string
convention. Call `get_bool`. A leftover `get_param` is an `AttributeError` at runtime, not a
silent miss.

### `Registry.clear_cache` is gone

`Registry.clear_cache` / `clear_all_caches` exist at 19.0 (`odoo/orm/registry.py:998`) and are
**absent** at saas-19.4. The successor is `Environment.transaction.invalidate_ormcache`
(`odoo/orm/environments.py:833`). The cache key names (`stable`, `templates`, `default`,
`routing`, `assets`, `groups`) are the same; a bare `clear_cache()` is `invalidate_ormcache()`
(default key).

Observed on the saas-19.4 image during `20_c` B1 tests: `AttributeError: 'Registry' object has
no attribute 'clear_cache'` when the 19.0 defect-6 fix was copied verbatim. Core itself now
does this (e.g. `analytic_plan.py:274`, `ir_model.py:1107`). Checker kind is `python-api`.
In `tools@19.0` this is also `cloud_base`, `knowsystem*`, `joint_calendar`, `documentation_builder`,
`odoo_menu_management`, `odoo_email_from`, `odoo_password_manager`.

```python
# BEFORE
self.env.registry.clear_cache("stable")
self.env.registry.clear_cache()
# AFTER
self.env.transaction.invalidate_ormcache("stable")
self.env.transaction.invalidate_ormcache()
```

### `tools.ormcache` is deprecated — import from `odoo.api`

`@tools.ormcache(...)` still exists at saas-19.4 but emits
`DeprecationWarning: Since 20.0 import ormcache from odoo.api` (observed
`20_5` Gx.6 `joint_calendar` `ir_ui_menu.py`). The warning gate treats that as
ours. Successor: `@api.ormcache(...)`. Checker `python-api` flags `tools.ormcache`.

```python
# BEFORE
from odoo import api, models, tools
@tools.ormcache("self.env.uid")
# AFTER
from odoo import api, models
@api.ormcache("self.env.uid")
```

### `mail` Store API redesigned around `Store.FieldList`

`Store.add()` changed signature and `Store.get_result()` is gone:

```python
# BEFORE (19.0): fields optional, result fetched separately
def add(self, records, fields=None, extra_fields=None, as_thread=False, **kwargs)
return Store().add(messages).get_result()

# AFTER (20.0): fields mandatory and positional, no get_result
def add(self, records, fields, *, as_thread=False, fields_params=None, ignore_empty=False)
store = Store().add(messages, "_store_message_fields")
# jsonrpc serializes Store via as_dict(); do not call get_result
```

Attachment box (`cloud_base` `/cloud_base/attachments/data`): same hole. Successor matches
core `mail` upload (`attachment.py:85`):

```python
store = Store()
if attachments:
    store.add(attachments, lambda res: (
        res.from_method("_store_attachment_fields"),
        res.from_method("_store_ownership_fields"),
    ))
return {"data": store, "attachments": attachments.ids}
```

Checker `python-api` flags `.get_result(`. The model-side hooks moved with it. The old hooks
appended to a dict or returned a list of names; the new ones receive a `Store.FieldList` and
call `res.attr(...)` / `res.extend([...])`. This is a rewrite, not a rename — budget real work
for any module that formats mail data.

### `stock.move.product_uom` renamed to `uom_id`

```python
# BEFORE: stock_move.product_uom
# AFTER:  stock_move.uom_id
```

Dangerous because these names are often **strings** in group-by keys, domains and selection values,
where nothing raises. Grep for the literal `"product_uom"`, not just attribute access. Note
`sale.order.line` and `product.supplierinfo` already use `product_uom_id` on 19.0 — do not conflate.

### Mail tracking values are gone

`mail.tracking.value` and `mail.message.tracking_value_ids` were removed in saas-19.3
(`addons/mail/models/mail_tracking_value.py` present at saas-19.2, absent at saas-19.3); the tracking
message is generated on the fly by the new `mail.track.mixin` plus the `_track_*` family on
`mail.thread`.

Anything that **reads** `message.tracking_value_ids` therefore raises on 20.0. In this hub that is
`odoo-apps-addons/ai_mcp_server` — `services/tool_service.py:1256` and
`services/catalog_service.py:245` both iterate `msg.sudo().tracking_value_ids` to format chatter
payloads, and `tests/test_mcp_models.py` creates `mail.tracking.value` rows. That module is outside
the `tools` group list, so no group gate covers it; schedule it explicitly.

`mail.tracking.duration.mixin` **survives in name only** — do not read that as "stage-duration
features still work". The 19.0 implementation was replaced (94 lines deleted, 29 added) and
`duration_tracking` changed in two ways that break readers silently:

- it is now **stored** (`store=True`), so it is no longer recomputed on read;
- the JSON schema changed from `{"<stage_id>": seconds}` to
  `{"d": "<utc datetime entered>", "s": <current stage id>, "<stage_id>": <minutes>}` —
  different unit (minutes, not seconds), plus two reserved non-numeric keys.

Code that sums the dict values, or treats every key as a stage id, produces wrong numbers instead of
an error. No `tools` / `system` module reads `duration_tracking` today, so this is a gate for future
work rather than a current port item.

## Security: `ir.rule` + `ir.model.access` merged into `ir.access`

**This one is loud, and it stops the install of any module that ships security data.**
`odoo/addons/base/models/ir_rule.py` and the `ir.model.access` model exist at `19.0` **and at
`saas-19.1`, `19.2`, `19.3`** — and are both gone at `saas-19.4`. The successor is a single model,
`ir.access` (`odoo/addons/base/models/ir_access.py`), holding what used to be two concepts.

Symptom: `KeyError: 'ir.rule'` from `convert.py` `_tag_record`, wrapped in a `ParseError` naming
your `security.xml`, during `-i`. A `security/ir.model.access.csv` fails the same way — the model
name comes from the **file stem**, so the file must be renamed, not just edited.

### XML

```xml
<!-- BEFORE (19.0) -->
<record id="sticky_note_rule" model="ir.rule">
    <field name="name">Sticky Note Rule</field>
    <field name="model_id" ref="model_sticky_note"/>
    <field name="domain_force">['|', ('share', '=', True), ('create_uid', '=', user.id)]</field>
</record>

<!-- AFTER (20.0) -->
<record id="sticky_note_rule" model="ir.access">
    <field name="name">Sticky Note Rule</field>
    <field name="model_id" ref="model_sticky_note"/>
    <field name="operation">crud</field>
    <field name="domain">['|', ('share', '=', True), ('create_uid', '=', user.id)]</field>
</record>
```

- `domain_force` → **`domain`**.
- `perm_read` / `perm_write` / `perm_create` / `perm_unlink` → one **`operation`** string, a subset
  of `crud` **in that letter order**. Valid keys are `CRUD_SELECTION` (`r`, `cr`, `cu`, `ru`,
  `crud`, …). `rc` is not a key — 19.0 read+create is `cr`. saas raises
  `Value 'rc' not found in selection field 'Operation'` (`20_10` Gx.6). Checker `access-op`.
  The `for_read` / `for_write` / `for_create` / `for_unlink` booleans still exist as
  computed+inverse helpers, but data files set `operation`.
- `groups` (many2many) → **`group_id`** (many2one). Several groups is now **several records**.
- `model_id` still takes the `model_<name>` xmlid via `ref` (core does:
  `ref="project.model_project_task"`).

**The empty-group semantics carried over, but the vocabulary changed.** `_compute_kind`
(`ir_access.py:129`) reads: no `group_id` → **restriction**, `group_id` → **permission**. A
restriction is ANDed for everyone, which is exactly what an `ir.rule` with no `groups` meant. So a
global rule ports across unchanged — leave `group_id` empty and do not "fix" it by inventing a group.

### CSV

Rename `security/ir.model.access.csv` → **`security/ir.access.csv`**, in the file system *and* in
the manifest `data` list. The header changed too:

```csv
# BEFORE  security/ir.model.access.csv
id,name,model_id:id,group_id:id,perm_read,perm_write,perm_create,perm_unlink
access_sticky_note,access_sticky_note,model_sticky_note,base.group_user,1,1,1,1

# AFTER   security/ir.access.csv
id,name,model_id,group_id/id,operation,domain
access_sticky_note,access_sticky_note,sticky.note,base.group_user,crud,
```

Three traps in that header, all silent if you copy the old one:

- **`model_id` is no longer an xmlid column.** It has no `:id` / `/id` suffix and carries the
  **technical model name** (`sticky.note`). It resolves through `ir.model._rec_names_search =
  ['name', 'model']`. All 236 core `ir.access.csv` files use this exact header.
- **`group_id/id`** uses the modern `/id` separator, not `:id`.
- **`domain`** is a real column now: a record rule and an ACL row are the same thing, so the two
  files may be merged.

Because the CSV can now carry a domain, ACL rows and record rules are interchangeable in form.
Do not restructure a module's security while porting — keep the same rows, translated one to
one, **except** an empty ACL domain is not the old ACL behavior (see below).

### Empty ACL permission ORs away the record rule

On 19.0, `ir.model.access` had no record filter. An empty ACL only meant "this group may use
the model"; `ir.rule` still applied.

On saas-19.4 both are `ir.access`. `_get_domain_for` is
`Domain.OR(permissions) & Domain.AND(restrictions)` (`ir_access.py:355`). An empty `domain` on
a **permission** (`group_id` set) becomes `Domain.TRUE` (`:308`). TRUE OR anything is TRUE, so
every grouped domain on that model is ignored.

That is silent. Install succeeds. The user sees every record.

Successor:

1. A 19.0 **global** rule (no `groups`) stays a **restriction** (no `group_id`). Restrictions
   AND. An empty ACL next to that is safe — `20_2` `sticky_notes` / `smart_warnings`,
   `20_5` `joint_calendar`.
2. A 19.0 **grouped** rule next to an empty ACL: **put that domain on the ACL CSV row**, or
   drop the empty ACL if a same-group domain permission already covers those operations.
   Do not leave the empty permission.
3. A 19.0 `[(1, '=', 1)]` rule (intentional all-records) must stay an **explicit**
   `[(1, '=', 1)]` on the 20.0 permission. Empty is indistinguishable from a forgotten ACL;
   the checker flags only empty, not explicit TRUE.
4. Do not invent `group_id` on a rule that was global.
5. Narrowing **this module's** empty rows is not enough. Another installed
   module (`sale_stock.access_stock_location_user`, `purchase_stock`,
   `pos_stock`, `stock_account`) can ship an empty permission on the same
   model. Inherit that xmlid only when it is a hard `depends`; otherwise
   AND the 19.0 filter in `_access_domain` and skip Super / `env.su`.
   Observed `20_6` Gx.8: demo (Inventory Administrator + Sales Own Documents
   Only, not Super) read `NY/Stock` while quants and operation types stayed
   hidden — only location had the `sale_stock` TRUE row.

Observed `20_5` Gx.8: empty `access_kpi_item` for `group_kpi_user` ORed away
`kpi_item_multi_company_rule` (`access_user_ids`). Demo saw every KPI. Same shape:
`total_notify` empty `access_total_notify` next to `total_notify_user` (`user_id`).
`20_14` `access_clouds_share` is empty next to the partner-domain Internal User row — 19.0
already had a TRUE File Manager rule, so write `[(1, '=', 1)]` there (hygiene, not a
product regression). `20_2` / `20_c` have no empty-permission + grouped-domain pair.

Checker kind `access-or`.

### Grouped `ir.rule` is not an ACL grant

On 19.0, `ir.rule` never granted model access. A grouped rule on
`base.group_user` only filtered records for people who already had
`ir.model.access`. The ACL row stayed on the product group
(`group_kpi_user` read-only, `group_kpi_admin` CRUD).

On saas-19.4 a grouped `ir.access` **is** the ACL. Porting that
`base.group_user` rule as `operation=crud` gives every Internal User
create/write/unlink, and `Domain.OR` unions it with the product-group
row so KPI User also becomes writable. Observed `20_5` Gx.9 review:
`kpi_item_multi_company_rule` / `kpi_category_multi_company_rule` /
`kpi_tag_multi_company_rule`.

Successor:

1. Put the 19.0 rule domain on the **product-group** permission
   (`group_kpi_user`), not on `base.group_user`.
2. Copy the 19.0 **ACL operations** (`r` vs `crud`), not a default
   `crud`. 19.0 `ir.rule` `perm_*` flags (scorecard line read vs edit)
   stay as separate rows with `r` / `cud`.
3. Keep 19.0 global rules as restrictions (no `group_id`).
4. Do not leave a `base.group_user` write permission on a model that
   also has a product-group ACL — that is the grant.
5. **Exception:** 19.0 `ir.model.access` already granted Internal User
   write on that model. Keep the ACL row and put the 19.0 *rule* domain
   on it. Observed `20_4` `portal.password.key` /
   `portal.password.bundle` (`group_user` crud + vaults group `r`).
   Checker `access-grant` stays quiet when `origin/19.0`
   `ir.model.access.csv` already had that write.

Checker kind `access-grant`.

## XML / views

### Calendar `date_delay` is gone (RNG + arch parser)

19.0 `calendar` accepted `date_delay` (`odoo/addons/base/rng/calendar_view.rng`,
`web/.../calendar_arch_parser.js` `FIELD_ATTRIBUTE_NAMES`). saas-19.4 dropped it
from both. The model field may stay; the **view attribute** kills `-i`:
`Invalid attribute date_delay for element calendar`. Observed `20_5` Gx.6
`joint_calendar` `joint_event_view_calendar`. Successor: drop the attribute.
`date_start` + `date_stop` remain. Checker kind `calendar-attr`.

### `t-esc` / `t-raw` in `ir.ui.view` arch are forbidden

`_validate_qweb_directive` (`ir_ui_view.py:2371`) allows `t-out` on qweb-based
views (kanban, card, and enterprise `gantt`) and rejects `t-esc`. Observed
`20_5` Gx.6 `joint_calendar_gantt` `joint_event_view_gantt`
(`Forbidden owl directive used in arch (t-esc)`). Successor: `t-out`. OWL
`static/src` templates may keep `t-esc`. Checker kind `qweb-tesc` (skips
`/static/`).

### Named inherit anchors: check the node, not just the view

A core view surviving under the same xmlid does **not** mean the node you hook onto survived.
`crm`'s `<group name="lead_priority">` (19.0 `crm_lead_views.xml:248`, the lead-only sibling of the
opportunity `tag_ids` group) is gone at `saas-19.4`: the lead and opportunity sidebars were merged
into one group with a single `tag_ids`. `complementary_lead_data` inherited that group by name, so
`crm.crm_lead_view_form` still resolved and the module still failed to load.

For every inherit of a core view, verify each anchor exists in the target arch:

- an `xpath` `expr` predicate — `//group[@name='lead_priority']` or `//div[@id='portal_service_category']`
- a tag carrying `position=` — `<group name="lead_priority" position="inside">` or
  `<div id="portal_service_category" position="inside">`

The checker's `view-anchor` kind does this mechanically (both `name` and `id`). When the
`inherit_id` record can be loaded, the token is checked **on that view's arch plus its
`card_id` / inherit chain**, not across every XML file. A surviving xmlid with a hollow
`<kanban card_id="…">` is the `20_10` miss: `project.view_task_kanban` still exists,
`priority` lives on `project.view_task_card`. Successor: inherit the card (or xpath a
node that is actually on the parent). A global-only lookup stays the fallback when the
parent record cannot be loaded. Read the target arch before deleting an xpath.

When the anchor is genuinely gone, prefer dropping the redundant hook over inventing a new one —
here the surviving `<field name="tag_ids" position="before">` already placed the widget, so the
second block was deleted rather than retargeted.

### Portal home cards: `portal.entry`, not QWeb into `portal_service_category`

19.0 `portal.portal_my_home` has `<div id="portal_service_category"/>`. Modules dumped a
`portal.portal_docs_entry` call into that node (`cloud_base`, `knowsystem_website`,
`odoo_password_manager`, `documentation_builder`, `business_appointment_website`).

saas-19.4 dropped the node. The home page iterates `portal.entry` records
(`sale/data/portal_entry_data.xml`). `_prepare_home_portal_values` still feeds
`placeholder_count` via `/my/counters`.

```xml
<!-- BEFORE — dies: Element '<div id="portal_service_category">' cannot be located -->
<template id="portal_my_home" inherit_id="portal.portal_my_home">
    <div id="portal_service_category" position="inside">
        <t t-call="portal.portal_docs_entry">…</t>
    </div>
</template>

<!-- AFTER -->
<record id="portal_shares" model="portal.entry">
    <field name="name">Shares</field>
    <field name="description">Check and download shared attachments</field>
    <field name="url">/clouds/shares</field>
    <field name="image" type="bytes" file="cloud_base/static/src/img/portal.svg"/>
    <field name="placeholder_count">shares_count</field>
    <field name="category">service_category</field>
    <field name="sequence" eval="110"/>
</record>
```

Keep the counter method. Do not xpath a surviving `o_portal_docs` wrapper and re-call
`portal_docs_entry` — that template now requires a `portal.entry` record (`entry.url`,
`entry.should_show_portal_card()`). Observed `20_14` Gx.6 `cloud_base` install after the
`Stream` import was already fixed. Checker `view-anchor` now sees the `id=` form.

### `t-call` inner `t-set` does not reach the callee

19.0 `t-call` copied `values` and applied inner `t-set` to that copy, so

```xml
<t t-call="portal.message_thread">
    <t t-set="object" t-value="share_id"/>
</t>
```

set `object` on `portal.message_thread`. saas-19.4 `_compile_directive_call`
(`ir_qweb.py:2682`) compiles the body as the `t-out="0"` slot only;
`t_call_values` starts as `{0: qwebContent}`. Inner `t-set` never reaches the
callee → `KeyError: 'object'` and a 500. Core sale/account set `object` on the
page via `_get_page_view_values` and use an empty `<t t-call="portal.message_thread"/>`.
Successor: write `object` / `token` / `breadcrumbs_searchbar` on the controller
values, **or** put them on the `t-call` tag (`breadcrumbs_searchbar="True"`),
or `t-set` **before** the `t-call` as a sibling. Inner `t-set` of
`breadcrumbs_searchbar` is why portal shares rendered **two** `/ Shares / …`
rows: `portal.portal_layout` never saw the flag (so it printed crumbs at its
first `t-call`) and the slot later set the flag for `portal.portal_searchbar`
(second row). Core sale writes:

```xml
<t t-call="portal.portal_layout" breadcrumbs_searchbar="True">
    <t t-call="portal.portal_searchbar" breadcrumbs_searchbar="True" title.translate="Quotations"/>
```

Checker kind `qweb-tcall` flags a first-child `t-set` of `breadcrumbs_searchbar`
/ `object` / `token` / `title`. Observed `20_14` Gx.8 token share.

### `website.default_website` moved to `base.default_website`

19.0 `addons/website/data/website_data.xml` shipped `<record id="default_website">`.
saas-19.4 deleted that node. The row is `base.default_website`
(`odoo/addons/base/data/website.xml`); `website._ensure_default_website_consistency`
keeps the xmlid on the first website. Core now does
`self.env.ref('base.default_website')`. A leftover `website.default_website`
raises `ValueError: External ID not found` — observed `20_9` Gx.7
`TestTypoReporterController.setUpClass`. Successor: retarget every
`env.ref` / XML `ref`. Checker `view-xmlid` greps the old token, including
tests. `field-lit` does not (it skips `/tests/`).

### `product.product_variant_easy_edit_view` removed

Present through `saas-19.3`, absent in `saas-19.4`. Any `inherit_id` pointing at it fails to load.
Surviving product forms include `product_normal_form_view` and
`product_product_view_form_normalized`; pick the target by reading the 20.0 layout, and fold the
xpath into it. Watch for modules that also name a **local** record
`product_variant_easy_edit_view` — the two are easy to confuse.

Check every core `inherit_id` for existence on the target, in `odoo` **and** `enterprise`.

## OWL / JS

saas-19.4 ships **OWL 3**. `@odoo/owl` is still the loader alias (`odoo.define("@odoo/owl", …)
{ return owl }`), so a **path** check reports clean. The public exports changed. The
compat layer (`web/static/src/owl2/owl3_compatibility_layer.js`) restores a subset of OWL 2
hooks and **does not** restore `useState` or `reactive`. Phase 1 skipped `@odoo/owl` as a
loader-alias false positive; the `20_2` review DB then died with
`TypeError: useState is not a function` on every form. The checker kind is `js-symbol`.

### 1. `useState` → `proxy` (FIRST — loud, every form if you patch `FormRenderer`)

`useState` is **deleted**. It is in the 19.0 `owl.js` export list (37 names) and absent from
saas-19.4 `owl.d.ts` and from the compat layer. Core `FormRenderer.setup` did exactly this
substitution (`addons/web/static/src/views/form/form_renderer.js`):

```js
// BEFORE (19.0)
import { useState } from "@odoo/owl";
this.state = useState({});
// AFTER (saas-19.4)
import { proxy } from "@odoo/owl";
this.state = proxy({});
```

Same for `const { useState } = owl` (portal / public code). `Object.assign(this.state, …)` on
the object `proxy` returns is what core and our form patches already do.

In `tools` this is **66 files** (23 named `@odoo/owl` imports plus `owl` destructures). A
global `FormRenderer` patch that still calls `useState` kills **every** backend form, not just
that module's view (`smart_warnings` / `sticky_notes` on `20_2`).

`reactive` is deleted the same way. `@web/core/utils/reactive.js` now imports `proxy` and only
exports `Reactive` (deprecated). The 19.0 `effect(cb, deps)` helper in that file is **gone**.
OWL 3's own `effect(fn)` (no deps array) is not a drop-in.

### 2. Compat layer — what it restores, and what it does not

Restored on `owl.*` (also re-exported from `@web/owl2/utils`): `Component` wrapper, `mount`,
`App`, `useRef`, `useEnv`, `useSubEnv`, `useChildSubEnv`, `useComponent`,
`useExternalListener`, `useLayoutEffect` (OWL 2 `useEffect` semantics), `onWillRender`,
`onRendered`.

**Not** restored: `useState`, `reactive`, `loadFile`, `validate`.

Still native on OWL 3 (safe to keep importing): `Component`, `onWillStart`,
`onWillUpdateProps`, `onMounted`, `onPatched`, `onWillUnmount`, `onWillDestroy`, `markup`,
`mount`, `xml`, `status`, `toRaw`, `useEffect` (see signature below).

### 3. `useEffect(fn, deps)` is not OWL 3 `useEffect`

OWL 3 `useEffect` exists but is `useEffect(fn)` — signal-based, **no dependency array**
(`owl.d.ts`). Extra arguments are ignored. Our three call sites still pass
`() => [deps]` (`knowsystem` iframe ×2, `cloud_base_documents` kanban record). That is a
silent miss: the effect will not re-run when those deps change.

Odoo core moved 183 → 43 `useEffect` and 0 → 161 `useLayoutEffect`. The compat
`useLayoutEffect(effect, computeDependencies)` is the OWL 2-shaped replacement:

```js
// BEFORE
import { useEffect } from "@odoo/owl";
useEffect(() => { …; return cleanup; }, () => [this.state.flag]);
// AFTER
import { useLayoutEffect } from "@web/owl2/utils";
// or: import { useLayoutEffect } from "@odoo/owl";  (compat assigns it)
useLayoutEffect(() => { …; return cleanup; }, () => [this.state.flag]);
```

### 4. `t-ref` in OWL templates and in `t-inherit` XPath

The compat header says replace `t-ref` → `t-custom-ref`, `t-portal` → `t-custom-portal`,
`t-model` → `t-custom-model`. Core `web` did: 322 → 41 `t-ref=`, 0 → 294 `t-custom-ref`.
Leftover `t-ref` in core is the OWL 3 form `t-ref="this.rootRef"` (a signal), not the OWL 2
named `t-ref="root"`.

**Inherit XPath that selects `@t-ref` is dead.** `web.KanbanRecord` is no longer a standalone
`<article t-ref="root">`. It `t-inherit`s `web.CardRenderer` and sets
`<attribute name="t-custom-ref">root</attribute>`. `mail.Message` `shadowBody` is now
`t-ref="this.shadowBody"`. Four jstree kanbans and `message_edit` still xpath
`//article[@t-ref='root']` / `//div[@t-ref='shadowBody']` — the inherit will not match.
Checker kind: `owl-xpath`.

**`o-kanban-button-new` left `web.KanbanView`.** At 19.0 the New button sits in
`control-panel-create-button` on `web.KanbanView` (`kanban_controller.xml:8`). At
saas-19.4 that slot is gone; the button lives on `web.KanbanView.Buttons` (`:101`)
and the view `t-call`s `this.props.buttonTemplate`. An inherit of `web.KanbanView`
that xpaths `//button[hasclass('o-kanban-button-new')]` dies at template compile
(`Element '…' cannot be located in element tree`) — File Manager, KnowSystem,
KPI Scorecard. Successor: inherit `web.KanbanView.Buttons` (primary), same xpath;
core does this (`product` catalog, `hr_expense`, `project`). Checker `owl-xpath`
now flags `hasclass()` that is absent from the inherited `t-name` at the target.

**`t-if` / `t-elif` inherit matches the exact attribute string.** OWL `applyInheritance`
looks up the opening tag, not the method name. saas-19.4 prefixed `mail.AttachmentList`
`canDownload(attachment)` with `this.` (19.0 `:91`, saas-19.4 the same file). A leftover
`<button t-elif="canDownload(attachment)" position="after">` dies at compile
(`Element '…' cannot be located`) and **kills every chatter attachment box**, not just
File Manager. Successor: `t-elif="this.canDownload(attachment)"`. Drop a dead
`<img t-else="">` hook — that node is a `div` on both refs. Checker `owl-xpath` now
indexes `(tag, t-if|t-elif|t-else, value)` per inherited `t-name`. A hasclass-only
pass reported this clean.

**`class="…" position=` is the same exact-string match.** saas `web.CalendarSidePanel`
still has a node whose class *token* is `o_calendar_sidebar`, but the attribute is
`class="o_calendar_sidebar flex-grow-0 …"` and that node is the **collapsed rail**.
The expanded filters live on `o_calendar_sidepanel_content`. A leftover
`<div class="o_calendar_sidebar" position="inside">` dies at compile
(`Element '…' cannot be located`) and **blocks the Joint Calendar menu**.
`hasclass('o_calendar_sidebar')` would compile and attach Refresh to the rail —
wrong UX. Successor: `//div[hasclass('o_calendar_sidepanel_content')]`.
Checker `owl-xpath` now indexes exact `class="…"` strings on `position=` tags
and `@class=` XPath. Observed `20_5` Gx.8 first-click.

**Bare `state` / `props` / `model` / `panelState` / `env` in an OWL template is undefined.**
OWL 3 does not put those names in the compile scope. Core saas templates write
`this.state` / `this.props` / `this.model` / `this.env` (19.0 `kanban_renderer.xml` still has
bare `state.selectionAvailable`; saas-19.4 has `this.state.selectionAvailable`).
File Manager then died with `Cannot read properties of undefined (reading
'reloaded')` at `CloudManagersKanbanRenderer`, then
`ctx.getCloudManagerNavigationProps is not a function`. Prefix `this.` on every
inherit expression, including `t-props="this.getX()"`. Checker kind: `owl-this`.
Same `this.` prefix on standalone OWL templates (`this.panelState`, getters
`this.panelClass` / `this.panelStyle`, `t-props="this.getX()"`,
`update.bind="this.handleChange"`, `t-on-click="this.clear"`) **and** on
`xml\`...\`` literals in JS. Portal `jsTreePortal` used `t-if="state.treeData"`
— the left folder/tag column rendered empty (no TypeError in the public page).
A `state|props|model`-only regex then missed KPI `panelState.collapsed` and
Reminder Designer `update.bind="handleChange"` (`undefined.bind`). Observed
`20_5` Gx.8 first-click. `20_14` `cloud_navigation.xml` / `rule_parent.xml`
already prefixed; `20_2` has no FieldFilter.

**jstree + `owl.proxy` / `state` plugin:** do not keep the tree payload on a
reactive `proxy`. jstree mutates `core.data` in place; a proxy write re-renders
OWL, replaces the host node, and the `state` plugin's `get_state` then does
`this.element.scrollLeft()` with `this.element === null`
(`TypeError: Cannot read properties of null (reading 'scrollLeft')`).
The stack often names `jstree.plugins.contextmenu.get_state` — that is the
last plugin on the prototype chain, not a contextmenu bug. The state plugin
binds `changed`/`ready` and schedules `save_state` on a **100ms timer**;
`destroy()` nulls `this.element` first, then the timer fires.

A parent OWL `proxy` write is enough to remount the tree. In File Manager
chatter that write was `this.state.cloudsFolderId = nextId` inside
`onRefreshAttachmentBoxWithFolder` (called from `state_ready`). Keep the
folder id on a **plain instance field** (`this.cloudsFolderId`); only
`folderExist` belongs on the proxy. Bind `onUpdateSearch` once in `setup`.

Successor: store the payload on `this.treeData`, pass a **copy** into
`core.data`, bind the host with `t-custom-ref` + `window.jQuery(ref.el)`,
**do not remount on `onPatched`**, **patch `$.jstree.core.prototype.get_state`**
to no-op when `!this.element`, and **stub `save_state`/`get_state` on the
instance before every `jstree("destroy")`**. Do **not** skip destroy on a
disconnected host — that leaves the 100ms timer armed. A `t-if` that needs
reactivity should key a boolean (`ready`), not the tree array. Observed
`20_14` Gx.8 chatter attachment box after the Store / canDownload fixes
already landed — off-proxy alone was not enough; skip-destroy was not
enough either.

**Do NOT drop the `state` plugin as a fix for that crash.** It was tried
here and is wrong: `state_ready.jstree` (emitted only by the `state`
plugin) is what the `check_node`/`changed`/`open_node`/`search` bindings
*and the very first `_onUpdateDomain()` call* wait on in this module's
`CloudJsTreeContainer._renderJsTree`. Dropping the plugin for the chatter
tree (`!fileUi`) didn't just disable state restore — it silently disabled
**all** folder-selection handling, so the attachment box stopped filtering
by folder and stopped tracking `cloudsFolderId` (uploads fell back to the
record). A missing feature discovered later ("selection not restored",
"folder does not filter attachments") is the signal that a plugin got
dropped instead of the actual crash cause being fixed.

**`portal.message_thread` heading:** saas starts with a bare
`<h3>Communication History</h3>`. A wrapper `class="row"` (19.0) applies
a negative gutter; saas `#wrapwrap` / nested `.container` clips the first
letter. Putting the `t-call` in a **sibling** of `.row` with only `mt32`
is still clipped. Successor: drop the extra inner `.container` (portal
layout already wraps the slot), and put `#share_communication` in
`class="col-12"` **inside** the existing row so the heading sits in the
gutter padding. 19.0 used the same `.row` and did not clip.

Our own templates that still write `t-ref="start-date"` should become `t-custom-ref="start-date"`
to match core datetime fields and the compat `useRef("start-date")`. Same rename for
`t-model` → `t-custom-model` (`email_suite` `scheduled_date_dialog_patch.xml`) and
`t-portal` → `t-custom-portal`. Checker kind: `owl-tref`.
`useRef` itself is restored by the compat layer.

### 5. `this.render` on patched view renderers

`FormRenderer` no longer passes `this.render` to `useDebounced`. It imports `render` from
`@web/owl2/utils` and calls `render(this)`. No `tools` file currently calls `this.render(`.
If a later patch does, rewrite it the same way.

### 6. Same-path JS symbol moves (the file survived; the export did not)

The `js-import` check only asks whether `@mod/path` resolves to a file. These exports left a
surviving file. Checker kind: `js-symbol`.

| 19.0 import | Symbol | saas-19.4 successor |
|---|---|---|
| `@odoo/owl` | `useState` / `reactive` | `proxy` from `@odoo/owl` |
| `@web/core/utils/concurrency` | `Deferred` | `Promise.withResolvers()` (polyfill in `web/static/src/polyfills/promise.js`). 158 core imports → 0. `KeepLast` / `Mutex` / `Race` stay |
| `@web/core/assets` | `LazyComponent` | `@web/core/lazy_component` |
| `@web/core/emoji_picker/emoji_picker` | `loadEmoji` | `useLoadEmoji` from `@web/core/emoji_picker/emoji_loader` |
| `@web/core/utils/reactive` | `effect` | rewrite; OWL 3 `effect(fn)` is not the two-arg helper |
| `@html_builder/core/utils` | `BaseOptionComponent` | `@html_builder/core/base_option_component` |

`static props = { x: { type: Object } }` is still used in 160 core `web` files on saas-19.4
(compat `Component` wrapper). Do not rewrite props schemas in the same breath as `useState`
unless a runtime error names them.

### Moved modules (import path only)

| 19.0 import | 20.0 import | Symbol |
|---|---|---|
| `@mail/core/common/record` | `@mail/model/export` (re-exports from `./misc`) | `fields` |
| `@web/core/orm_service` | `@web/core/orm_plugin` | `x2ManyCommands` |

### Removed with no drop-in

- **`@web/core/ensure_jquery`** — gone. It used to load `web._assets_jquery` plus the Bootstrap
  jQuery plugins. Rewrite the call site without jQuery; do not reintroduce a loader.
- **`/web/static/lib/jquery/jquery.js`** — gone with the same deletion (`addons/web/static/lib/jquery`
  is present at 19.0, absent at saas-19.4). `loadJS` of that URL is an `AssetsLoadingError`.
  File Manager / jstree still needs `$` and already vendors `jstree.min.js`. Successor: copy the
  19.0 `jquery.js` (MIT, currently 3.6.3) next to it as `/<module>/static/lib/jquery/jquery.js`
  and retarget every `loadJS`. Do not rewrite the tree in the same job. Checker `js-import`
  flags the old URL. Observed `20_14` Gx.8 after the `o-kanban-button-new` xpath landed.
- **`@html_editor/others/dynamic_placeholder_plugin`** (`DynamicPlaceholderPlugin`) — gone.
- **`@html_builder/utils/option_sequence`** (`before`, `after`, `VERTICAL_ALIGNMENT`, `WIDTH`) —
  gone. Sequencing is now **numeric**: `withSequence(N, object)` from `@html_editor/utils/resource`.
  `withSequence(after(VERTICAL_ALIGNMENT), …)` must be rewritten, not remapped.

### Renamed / restructured (architecture port, not a substitution)

| 19.0 | 20.0 | Note |
|---|---|---|
| `DYNAMIC_PLACEHOLDER_PLUGINS` from `@html_editor/backend/plugin_sets` | `DYNAMIC_FIELD_PLUGINS` from `@html_editor/backend/dynamic_field/dynamic_field_plugin`, consumed via the `dynamicField` prop | not `@web/views/fields/dynamic_placeholder_*`, which serves plain char/text fields |
| `@mail/chatter/web_portal/chatter` | `@mail/chatter/web_portal_project/chatter` | the component was rewritten and backend behavior moved to `chatter/web/chatter_patch.js`; retargeting the import is necessary but not sufficient |
| `@website/js/content/website_root` + legacy `.include()` | `website/static/src/interactions/` | e.g. a `_onLangChangeClick` include becomes the `LangChange` Interaction (`selector = ".js_change_lang"`) |
| `@website_sale/interactions/website_sale` (`WebsiteSale`) | split into `add_to_cart.js`, `add_to_comparison.js`, `add_to_wishlist.js`, `product_page.js` | pick the Interaction per call site; `ProductPage` (`.o_wsale_product_page`) covers product-page behavior |

### Signature changes

`MessageModel.edit` narrowed to
`async edit(body, attachments = [], { mentionedPartners = [], mentionedRoles = [] } = {})`.
Forwarding with `super.edit(...arguments)` survives, but a dropped option is silently ignored.

### Patching rules learned here

- `patch()` on a **prototype** cannot override an own instance property. Upstream `fields.Attr(...)`
  members (e.g. `MessageModel.isEmpty`) are instance fields, so a `get x()` in a prototype patch is
  shadowed and **never runs** — including on 19.0. **Patch the field's compute**, which upstream
  routes through a normal prototype method:

  ```js
  // BEFORE — shadowed by the own instance property, dead on every serie
  get isEmpty() { return this.deleted ? true : super.isEmpty; },
  // AFTER — computeIsEmpty() is a prototype method, so the patch runs
  computeIsEmpty() { return this.deleted ? true : super.computeIsEmpty(); },
  ```

  `isEmpty = fields.Attr(false, {compute() { return this.computeIsEmpty(); }})` and
  `computeIsEmpty()` are both present at 19.0 (`message_model.js:338`, `:350`) and saas-19.4
  (`:392`, `:404`), so the same fix holds on both. The compute's body did change — 19.0 reads
  `this.trackingValues`, which is gone at saas-19.4 with the tracking values — so re-read it rather
  than assuming what `super()` returns. Computes are **lazy** by default
  (`mail/static/src/model/misc.js:69`), so a patch may safely read fields its own `setup()` declares
  after `super.setup()`.
- Members reached only through a shadowed patch are dead too. In `message_edit` the `editable`
  getter read `this.isEmpty` and therefore silently got upstream's value, not the module's.
- A patch that **fully replaces** a core method without `super()` keeps working syntactically while
  diverging from new core behavior. Re-read the upstream method on every port.
- Resolve the patched target through its import, then walk the parent chain. A member may live on an
  ancestor or mixin (`FileModelMixin`, `Record`), not the class you imported.

## Checker

`ai_rules/tools/check_migrate_v20.py` implements the mechanical half of this rule. Run it before and
after each module port:

```bash
python3 ai_rules/tools/check_migrate_v20.py \
    --repo /home/feelwhy/Odoo/tools \
    --odoo /home/feelwhy/Odoo/odoo --odoo-ref origin/saas-19.4 --odoo-base-ref origin/19.0 \
    --enterprise /home/feelwhy/Odoo/enterprise --enterprise-ref origin/saas-19.4 \
    [--modules mod_a,mod_b] [--only js-symbol,owl-xpath,python-api] [--json]
```

About 30s for one module or group, ~3min for 93 modules. Findings:

| Kind | Meaning |
|---|---|
| `dead-hook` | the hook existed at the **base** ref and is gone at the target — a silent break. Also `_check_access`: the name survives but `check_access` is `@typing.final` (`DEAD_DESPITE_EXISTING`) |
| `stale-override` | absent at **both** refs — already dead before this port; a defect on the current serie, not porting work |
| `js-import` | an `@mod/path` import resolving to no file in `odoo` or `enterprise`, or a `loadJS` URL deleted at the target (`/web/static/lib/jquery/jquery.js`) |
| `js-symbol` | a **named** import (or `const { X } = owl`) whose path still resolves but the symbol is not exported at the target — this is how `useState` hid. Also `._replaceWith(` (method gone; successor `list.set`) |
| `owl-xpath` | an OWL `t-inherit` XPath that selects `@t-ref` / `@t-esc` on a core template, **or** `hasclass()` of a class that left the inherited `t-name` (`o-kanban-button-new` left `web.KanbanView`), **or** a `position=` tag whose `t-if` / `t-elif` / `t-else` value is not on that `t-name` (`canDownload` vs `this.canDownload`), **or** a `position=` / `@class=` inherit whose exact `class="…"` string is not on that `t-name` (`o_calendar_sidebar` vs the saas collapsed-rail class list) |
| `owl-tref` | an OWL-2 named `t-ref` / `t-model` / `t-portal` in our own `static/src` template; core writes `t-custom-*` |
| `owl-this` | a `t-inherit` / standalone / `xml\`` OWL template still uses a bare OWL-3 scope name (`state.` / `panelState.` / `env.` / `props.` / `model.`), a bare getter (`t-att-class="panelClass"`, `t-out="title"`), a bare `#{id}` interpolation, a bare method bind (`update.bind="handleChange"`, `t-on-click="clear"`), or a `t-on-*` arrow that calls a method without `this.` (`(event) => _onSearchNavigation(...)`) |
| `qweb-tcall` | first-child `t-set` of `breadcrumbs_searchbar` / `object` / `token` / `title` on a `t-call` — saas-19.4 slot only |
| `owl-hook` | `useEffect(fn, deps)` imported from `@odoo/owl` — OWL 3 `useEffect` ignores the deps array |
| `python-api` | a call to a core method that is gone at the target (`get_param` / `set_param` / `Registry.clear_cache` / `Store.get_result`), a leftover `tools.ormcache` (import from `odoo.api`), a leftover `request.website` (use `request.env.website`), a named import that left `odoo.http` (`Stream` / `content_disposition`), or a leftover 19.0 `_order_field_to_sql(..., query)` / `_order_to_sql(order, query)` (saas dropped `query`; first arg is `table`) |
| `calendar-attr` | a `<calendar date_delay=...>` — RNG and `FIELD_ATTRIBUTE_NAMES` dropped it at saas-19.4; drop the attribute |
| `qweb-tesc` | `t-esc` / `t-raw` in a non-`static` XML arch — saas forbids those OWL directives; use `t-out` |
| `patch-target` | a `patch()` whose imported target no longer resolves |
| `patch-shadow` | a `patch(X.prototype, …)` member that upstream declares as a **class field** on the patched class or an ancestor — an own instance property shadows it, so it never runs, on any serie |
| `view-xmlid` | an `inherit_id` ref to a core view that no longer exists, **or** a leftover `website.default_website` (tests included — successor `base.default_website`) |
| `view-anchor` | an inherit anchor (`@name=` / `@id=` predicate, or a `position=` tag's `name` / `id`) absent from the **inherited** view arch (plus `inherit_id` chain, **not** `card_id` — Odoo does not apply xpath to the card). Global name-set is only the fallback when that record cannot be loaded. A hollow `view_task_kanban` / sharing kanban plus an anchor that lives only on the card is a finding (`20_10`, `20_4`) |
| `security-model` | a data file declaring `ir.rule` / `ir.model.access`, gone at the target; CSV findings mean **rename the file** |
| `access-or` | a grouped `ir.access` with an **empty** domain on a model that also has a grouped row with a real domain and overlapping ops — empty is `Domain.TRUE` and ORs the filter away. Explicit `[(1, '=', 1)]` is not this kind. Restrictions (no `group_id`) AND and are safe. Also a **core/enterprise** empty permission on a model this module domains, unless the module ANDs via `_access_domain` |
| `access-grant` | a `base.group_user` permission with write ops (`c`/`u`/`d`) on a model that also has a product-group permission — 19.0 `ir.rule` on Internal User was a filter, not an ACL grant. Quiet when 19.0 `ir.model.access` already granted that write (`20_4` portal vaults) |
| `access-op` | `ir.access.operation` is not a `CRUD_SELECTION` key. Letters stay in `crud` order (`cr` not `rc`). saas rejects the CSV (`Value 'rc' not found`) |
| `field-lit` | a literal use of a removed field name |
| `manifest-version` | a serie-prefixed `__manifest__.py` `version` (`19.0.x` / `20.0.x`) while `--odoo-ref` is a `saas-*` branch — `check_version` sets `installable=False` |

Always pass `--odoo-base-ref`. Without it the hook check cannot tell a fresh removal from an
override that was already dead, and reports both the same way.

A clean run is a precondition, not proof of a working port — the runtime gates still apply.

### Why the checker is built the way it is

Each of these cost a false-positive round on the first run, so do not "simplify" them away:

- **Bind the hook to the inherited model, then expand the chain.** A global name search is wrong in
  both directions. It hides a dead hook when the name survives on an unrelated model, and invents
  dead hooks for internal `super()` chains. The MRO also commonly reaches core *through one of our
  own models*, so only direct parents will report live hooks as dead.
- **Framework methods live outside `models/`.** `export_data`, `_check_access`, `copy`, … are on
  `BaseModel` in `odoo/orm/models.py`. A check that only scans addon `models/` directories reports
  all of them as dead.
- **Span `odoo` and `enterprise`.** An `odoo`-only pass reports `@web_gantt/*` and `@documents/*`
  as missing.
- **`git grep -E` is POSIX ERE.** `(?:…)` and `\s` are invalid there and silently match nothing,
  which is indistinguishable from "clean". Use `(…)` and `[[:space:]]`, or filter in Python.
- **Occurrence counts are not work estimates.** Report sites to read, never a total to trust.
- **No core parent in the class is not a reason to skip it.** Every Odoo model still inherits
  `BaseModel`, so a class whose `_inherit` names only one of our own mixins can still hold a dead
  override. Skipping those hid `portal.password.key._generate_order_by` from the chain check
  entirely; only a direct grep found it. Fall back to the implicit `base` ancestor, which resolves
  through the framework-method index.
- **`_name = X` with `_inherit = [X, …]` is the extend-in-place style**, so `X` *is* the core parent.
  Discarding the class's own `_name` unconditionally left `odoo_email_from`'s `mail.compose.message`
  with no core chain — first skipping it silently, then reporting five live core methods as stale.
- **Suppress a repo-internal `super()` chain by definition site, not by module.** Comparing owning
  modules reports the second class of the same model, inside one module, as a stale override.
- **Bind `patch-shadow` to the patched class, through the name that module exports.** A whole-file
  scan is wrong twice over: a field of a class nobody patched proves nothing about the one that was,
  and `import { Message as MessageModel }` means the class to find is `Message` — searching for
  `class MessageModel` finds nothing and reports clean. Resolve local name -> (spec, exported name),
  follow `extends` (local or imported) with no depth cap, and report **nothing** when the class
  cannot be located rather than falling back to the file.
- **Locate members by brace depth, never by indent width.** An assumed four-space indent silently
  matches nothing in a differently formatted file, which again looks exactly like "clean". Blank out
  comment and string contents first, or a brace inside a template literal ends the class body early.
  `static` fields are excluded — they live on the constructor and shadow nothing for instances.
- **Gate a "removed model" check on the target actually lacking it**, and on the successor being
  present. A hardcoded list of renames reports every module as broken the day the check runs against
  real 20.0 with something restored, and cannot be trusted when it stays silent.
- **`@odoo/owl` is a loader alias, not a reason to skip the file.** Path existence is always
  true. Named exports must be checked against `owl.d.ts` plus the compat layer's `owl.X =`
  assignments. Skipping the alias hid `useState` from every module that imports it.
- **A QWeb `<template id>` is an xmlid.** `view-xmlid` collected only
  `<record id>`. saas `website.snippets` is
  `<template id="snippets">` (`addons/website/views/snippets/snippets.xml:5`
  at pin `3630379f63633612e5a9e8d435deecbe26eaa15a`). `20_9` `short_urls`
  inherit then looked dead. Index `<template id>` the same way as records.
- **A surviving JS file is not a surviving export.** `js-import` asks whether `@mod/path`
  resolves. `Deferred` left `concurrency.js` in place and still broke 158 core call sites.
  `js-symbol` reads the named import against that file's `export` list.
- **A `loadJS` URL is not an `@mod/path`.** `js-import` never saw
  `/web/static/lib/jquery/jquery.js`. saas-19.4 deleted the file; File Manager
  then died with `AssetsLoadingError` after the xpath was already clean.
  `GONE_JS_PATHS` scans the same JS walk.
- **Bare `state.` in a `t-inherit` is not a `t-ref`.** OWL 3 compile scope is
  `this`. Core saas templates already write `this.state`. `owl-this` scans
  inherit bodies, standalone OWL templates (`t-props="getX()"`), **and**
  `xml\`...\`` literals in JS. A file-only `t-name` walk missed portal
  `jsTreePortal` (`t-if="state.treeData"`). A `state|props|model`-only
  regex then missed `panelState.collapsed`, `env.isSmall`,
  `t-att-class="panelClass"`, and `update.bind="handleChange"` (`20_5`
  Gx.8 first-click). The kind now flags `*State.` / `env.` / bare bind /
  bare `t-att-*` / bare `t-on-click` idents.
- **A class token on the parent is not an exact `class="…"` inherit.** OWL
  `applyInheritance` matches the opening-tag attribute string.
  `<div class="o_calendar_sidebar" position="inside">` does not match saas
  `class="o_calendar_sidebar flex-grow-0 …"`. `hasclass()` indexing
  reported clean because the token survived on the collapsed rail.
  `owl-xpath` now indexes exact `class=` strings on `position=` tags.
- **`t-esc` in `ir.ui.view` is not OWL `t-esc`.** saas `_validate_qweb_directive`
  forbids `t-esc`/`t-raw` on qweb-based arches (kanban, card, gantt). OWL
  `static/src` templates may keep `t-esc`. `qweb-tesc` skips `/static/`. A
  view-only pass that ignored gantt popovers hid `joint_calendar_gantt`.
- **Inner `t-set` of a `t-call` is the slot, not the callee.** 19.0 forced
  `str(qwebContent)` when the call had only `t-*` attrs plus child `t-set`
  (`is_deprecated_version`). saas-19.4 deleted that. Checker `qweb-tcall`
  flags a first-child `t-set` of `breadcrumbs_searchbar` / `object` /
  `token` / `title`. Sale writes those as `t-call` attributes.
- **A surviving method name is not a surviving inherit.** OWL `applyInheritance`
  matches the opening-tag attribute string. `t-elif="canDownload(attachment)"`
  does not match saas `t-elif="this.canDownload(attachment)"`. `hasclass()`
  indexing reported that chatter inherit clean. `owl-xpath` now indexes
  `(tag, t-if|t-elif|t-else, value)` on `position=` tags.
- **`view-anchor` collects only nodes an inherit *targets*.** A `name` inside an added block, or an
  `<attribute name="invisible">` under `position="attributes"`, is not an anchor; only an `expr`
  predicate (`@name=` or `@id=`) and a tag carrying `position=` (`name` or `id`) are. Walk
  `<record>` **and** `<template inherit_id>` — a record-only scan missed
  `portal_service_category` on `portal.portal_my_home`. A name-only scan missed the
  `<div id="…" position="inside">` form. Without the target/add distinction every field a
  module adds becomes a finding. It also does not see OWL `t-inherit` XPath on `@t-ref` —
  that is `owl-xpath`.
- **The target node-name set rides on the existing XML walk.** `view_xmlids()` already `git show`s
  every XML file in both trees, so the fallback lookup is a set membership, not one `git grep` per
  anchor (553 `position=` tags in `tools` would otherwise mean 553 greps).
- **A surviving parent xmlid is not a surviving field node.** saas
  `project.view_task_kanban` is a `card_id` shell (`project_task_views.xml:752`
  at pin `3630379f63633612e5a9e8d435deecbe26eaa15a`). `priority` / `footer`
  live on `project.view_task_card`. A global `name=` set reported clean.
  `view-anchor` binds to the inherited record plus the `inherit_id` chain,
  **not** `card_id` (Odoo applies xpath to the parent only; walking the
  card hid `20_4` `task_numbers`). Unqualified `inherit_id`
  (`ref="sale_order_tree"`) must take the parent module prefix or
  `sale.view_order_tree` looks empty (`state` is on `sale.sale_order_tree`).
  Successor: inherit `view_task_card` (and the sharing card). Observed
  `20_10` Gx.6 and `20_4` Gx.6.
- *(2026-09-16, `20_10` Gx.6)* Sale/purchase history ACL `operation=rc`
  died (`Value 'rc' not found in selection field 'Operation'`). 19.0 was
  read+create (`perm_read`+`perm_create`). Successor: `cr`. Checker
  `access-op` against saas `CRUD_SELECTION`.
- **An empty grouped `ir.access` domain is not the 19.0 ACL.** saas
  `Domain.OR(permissions)` treats empty as `Domain.TRUE` (`ir_access.py:308`,
  `:355`). A one-to-one ACL+rule port leaves the rule in the file and never
  applies it. `access-or` flags empty (not explicit `[(1, '=', 1)]`) next to a
  sibling grouped real domain. A restriction (no `group_id`) ANDs — do not
  flag that pair. Same-group is not required: `group_kpi_user` empty +
  `base.group_user` domain is the incident (`20_5` KPI). Parse XML
  `<field .../>` separately from `<field>...</field>`: a `[^>]*` that
  swallows the `/` of `/>` ate `model_id` and hid every grouped XML
  domain (`total_notify_user`) on the first run.
- **A module-local `access-or` pass does not see `sale_stock`.** Empty
  permissions that OR the filter live in another addon. `access-or` now
  reads target `security/ir.access.csv` for models this module domains.
  An `_access_domain` override on that model is the successor when the
  other module is not a hard depend (`20_6` location / demo + salesman).

## Verify at runtime, not from this rule

These are not settled by source reading. Do not write them into a port as fact:

- Asset bundle existence and restructuring (manifest-key grepping is unreliable; use the runtime
  asset gate).
- Remaining field renames inside surviving models (read the registry after a fresh install).
- Whether 20.0's optional-product rule on `sale.order.line` affects your line creation.
- Attendance access-rights and geolocation RPC changes for kiosk-facing code.
- Which deprecation warnings **your** code actually triggers (test-window log on the pinned image).
- Portal sharing `get_views` on the **running** worker (arch vs `fields_get` for `x_oz_*` / other
  `TASK_PORTAL_*` extras). A new shell process resets `@ormcache(cache='stable')` and is not that
  check. See **Portal sharing field list** above.

## Learned while porting

Append each entry with its date, the module that revealed it, and the source evidence. An entry
without evidence does not belong in this rule.

- *(2026-09-12, phase 1 analysis)* Rule created from the saas-19.4 delta: 23 source-confirmed
  breaks, 5 open hypotheses. Nothing here has been observed on a running 20 instance yet.
- *(2026-09-12, checker first run)* `patch()` on a prototype cannot override an upstream
  `fields.Attr(...)` member, because that is an own instance property. Found via `MessageModel.isEmpty`,
  which has therefore been dead since 19.0 — a port check that binds patched members to their real
  target finds this class of bug on the **current** serie too, not just the new one.
- *(2026-09-12, checker first run)* The `stale-override` class exists because three overrides
  (`_generate_order_by`, `_generate_order_by_inner`, `_inherits_join_calc`) are absent from core at
  **both** refs. Pre-existing dead code is a defect on the current serie; do not bill it to the port.
- *(2026-09-12, 19.0 defect fixes)* Those four sites are now fixed on 19.0 via `_order_field_to_sql`
  (`knowsystem/models/knowsystem_article.py`, `odoo_password_manager/models/password_key.py`,
  `.../portal_password_key.py`), and `message_edit`'s `isEmpty` patch moved to `computeIsEmpty()`.
  Verified in `demo19`: `_order_to_sql("name asc")` emits `LOWER("<table>"."name"->>%s) ASC` on all
  three models, and grouped ordering through those models still resolves (`_read_group` on
  `portal.password.key`, `password.user.log`, `documentation.section.article`,
  `knowsystem.article.revision`). Regression tests: `knowsystem/tests/test_article_ordering.py`,
  `odoo_password_manager/tests/test_password_ordering.py`.
- *(2026-09-12, verification correction)* The first evidence offered for that fix — "mixed-case
  probes sort `AA, mm, zz`" — proved nothing. Those probes share byte order with case-insensitive
  order, and our databases are `en_US.utf8`, where Postgres ignores case while ordering anyway, so
  the assertion passes with the hook dead. The SQL shape was the only load-bearing check. Choose
  probes whose orders actually differ, and assert on `_order_to_sql(...).code`.
- *(2026-09-12, checker hardening)* Both new checks found a defect on their first run:
  `patch-shadow` reproduced `message_edit/static/src/core/common/message_model.js:82`, and the
  `base`-fallback chain exposed the `_name` + `_inherit` self-extension bug above. A checker change
  that reports **nothing** new is the suspicious outcome, not the reassuring one.
- *(2026-09-12, tracking correction)* "`mail_tracking_duration_mixin` survives" was true of the file
  and false of the behavior: `duration_tracking` became stored and changed JSON schema and unit.
  Reading a surviving *name* is not evidence; diff the implementation.
- *(2026-09-12, 4.3 system port)* A serie-prefixed manifest is silently uninstallable on the
  saas-19.4 image: `check_version` compares to `release.major_version` (`saas~19.4`), so both
  `19.0.x` and `20.0.x` become `installable=False` plus a warning. Drop the prefix on the
  stand-in; re-prefix on real 20.0. Same run: `version_info[0]` is `'saas~19'`, not an int —
  `_demo_ticket_serie` was emitting `saas~19.0`.
- *(2026-09-12, `20_2` `Gx.3`)* `crm`'s `group name="lead_priority"` is gone at saas-19.4, so an
  inherit of a **surviving** view (`crm.crm_lead_view_form`) still failed. Static checks that stop at
  the xmlid cannot see this; hence the `view-anchor` kind. Found by reading the target arch after the
  view check came back clean — which is the general lesson: a clean `view-xmlid` says nothing about
  the nodes inside.
- *(2026-09-12, `20_2` `Gx.6`)* First runtime evidence of this program, and it was not a silent
  failure: `KeyError: 'ir.rule'` killed `sticky_notes` and `smart_warnings` on `-i`. `ir.rule` and
  `ir.model.access` survive `saas-19.1`…`19.3` and are **both** replaced by `ir.access` at
  `saas-19.4` — so serie-by-serie existence checks are worth running per saas branch, not just
  against the newest one. Two process notes from the same run: the checker had **no** security kind
  at all (five sites, zero findings, install dead on the first file), and the baked
  `env_dbfilter_header` breaks on the stand-in too (`import odoo.service.db`), which is infrastructure
  noise rather than a module port item — read the failing module name before blaming the group.
- *(2026-09-14, `20_2` Gx.8 review)* Phase 1's JS check was **path existence only** and
  **skipped `@odoo/owl`** as a loader alias. saas-19.4 ships OWL 3; `useState` is deleted and
  the compat layer does not restore it. Opening a Smart Alert form died with
  `TypeError: useState is not a function` at `FormRenderer.setup` because
  `smart_warnings` / `sticky_notes` patch that class. Same-path export removals
  (`Deferred`, `LazyComponent`, `loadEmoji`, `effect`, `BaseOptionComponent`) and
  `@t-ref` inherit XPaths were the same hole. `get_param` / `set_param` were already
  observed at neutralize and were still missing from this rule. The checker now has
  `js-symbol`, `owl-xpath`, `owl-tref`, `owl-hook`, `python-api`. A path-only "OWL clean"
  is not a finding.
- *(2026-09-14, `20_c` Gx.8 review)* Opening a task in project sharing edit as the portal
  collaborator died with `TypeError: "project.task"."x_oz_tsk_1" field is undefined` at
  `Field.parseFieldNode`. The sharing form arch had `x_oz_tsk_1` (Version
  `portal_edit_placement=left_panel_group`); the running worker's portal `get_views` omitted it
  from `models.fields`. Admin and demo HTTP `get_views` included it. A new `odoo shell` on the
  same DB included it for portal too — `_portal_accessible_fields` is `@ormcache(cache='stable')`
  at **both** refs (19.0 `project_task.py:1048`, saas-19.4 `:1077`), so the first call in that
  process freezes the set. `task_custom_fields` fills `TASK_PORTAL_*` from
  `custom.task.field` and writes the arch in `_generate_xml` without invalidating that cache.
  19.0 demo leaves `portal_edit_placement` empty, so the generated sharing groups stay empty and
  the hole is latent. Not a 20-only `fields_get` / `ir.access` miss. Not a checker kind (both
  hooks exist; a `TASK_PORTAL`+`search(` grep would stay red after a correct invalidate-on-write).
  Ledger defect 6. Fix on 19.0 (`a9154df3008`: `registry.clear_cache("stable")`). On saas-19.4
  that call is itself an `AttributeError` — use `env.transaction.invalidate_ormcache("stable")`
  (see **Registry.clear_cache**).
- *(2026-09-14, `20_c` B1 tests)* Copying the 19.0 defect-6 commit onto `20_c` died at
  `Registry.clear_cache`. Successor confirmed at saas-19.4 `environments.py:833`. Checker
  `python-api` now flags `.clear_cache(`.
- *(2026-09-14, `20_14` Gx.6)* `odoo.http` is a package. `__init__.py` does not re-export
  `Stream` / `content_disposition`. `cloud_base` died at import (`cannot import name
  'Stream'`). Successor: `odoo.http.stream`. Checker `python-api` now flags the import form.
- *(2026-09-14, `20_14` Gx.6)* After the import landed, install died on
  `portal.portal_my_home`: `id="portal_service_category"` is gone. Cards are `portal.entry`
  records. A name-only **and** record-only `view-anchor` both missed it (`<template
  inherit_id>` + `<div id="…" position="inside">`). Five 19.0 modules still hook that node.
- *(2026-09-14, `20_14` Gx.7)* `_check_access` still exists at saas-19.4 and the
  checker reported clean. `check_access` is `@typing.final` and uses `_access_domain`.
  `TestCloudsFolderPreparing.test3_security_rights_check` Case 1 (rule-folder
  write) passed after the port. Case 5 stayed red for two independent saas
  facts: (1) `has_access('read')` short-circuits on `transaction.access_read`
  — field `depends` is not enough, `write` must
  `invalidate_access_cache(self._name)`; (2) after that cache was empty,
  `access_user_ids` still read `[]` because saas x2many hides inactive
  `res.users` (`base.user_root`). Compute must use `active_test=False`.
  Checker `DEAD_DESPITE_EXISTING` for (1) only.
- *(2026-09-15, `20_14` Gx.8)* Opening File Manager died with
  `Element '<xpath expr="//button[hasclass('o-kanban-button-new')]">' cannot be
  located`. The class moved from `web.KanbanView` to `web.KanbanView.Buttons`
  (19.0 `kanban_controller.xml:8`, saas-19.4 `:101`). Same hole on 19.0
  `knowsystem` and `kpi_scorecard`. Moved the upload/URL replace onto
  `cloud_base.CloudBaseViewButtons` (`t-inherit-mode="primary"`). Checker
  `owl-xpath` now indexes OWL `t-name` classes in `/static/` (the QWeb
  `view-anchor` walk skips that tree).
- *(2026-09-15, `20_14` Gx.8)* After that xpath landed, File Manager died on
  `AssetsLoadingError: The loading of /web/static/lib/jquery/jquery.js failed`.
  The file is at 19.0 `addons/web/static/lib/jquery/jquery.js` and **absent**
  at saas-19.4 (whole `jquery/` dir gone with `ensure_jquery`). jstree is
  already vendored in `cloud_base` and still needs `$`. Copied 19.0 jquery
  3.6.3 to `cloud_base/static/lib/jquery/jquery.js` and retargeted every
  `loadJS`. Checker `js-import` now flags the old URL. Same leftover in later
  groups that still `loadJS` the core path.
- *(2026-09-15, `20_14` Gx.8)* After jquery loaded, File Manager died on
  `TypeError: Cannot read properties of undefined (reading 'reloaded')` in
  `CloudManagersKanbanRenderer`. OWL 3 inherit templates do not bind bare
  `state` / `props`. Core saas `web.KanbanRenderer` writes `this.state`.
  Prefixed the inherit expressions. Next compile error was
  `ctx.getCloudManagerNavigationProps is not a function` — same `this.`
  on `t-props`. Checker `owl-this` also flags `t-props="getX()"` without
  `this.`.
- *(2026-09-15, `20_14` Gx.8)* Opening a contact chatter attachment box died
  with `Element '<button t-elif="canDownload(attachment)" …>' cannot be
  located`. The button is still on `mail.AttachmentList`; saas writes
  `t-elif="this.canDownload(attachment)"` (OWL 3 `this.`). Inherit matches
  the attribute string, not the method. Slideshow then died on the already-
  known leftover `t-props="getPhotosSlideShowProps()"` / bare `state.playing`.
  Checker `owl-xpath` now indexes OWL `t-if` / `t-elif` / `t-else` on
  `position=` tags. A hasclass-only pass reported the chatter inherit clean.
- *(2026-09-15, `20_14` Gx.8)* After that inherit landed, opening the same
  attachment box died on `Store().add(attachments).get_result()` —
  `AttributeError: 'Store' object has no attribute 'get_result'`. Already in
  this rule; checker `python-api` did not flag `.get_result(`. Token share
  with `show_chatter` stayed 500 on `KeyError: 'object'`: saas `t-call` no
  longer applies inner `t-set` to the callee.
- *(2026-09-15, `20_14` Gx.8)* Same attachment box then died on jstree
  `get_state` → `this.element.scrollLeft()` with `this.element === null`.
  `CloudJsTreeContainer` kept `treeData` on `owl.proxy`; jstree mutated it,
  OWL replaced the host, the `state` plugin saved. Tree payload is now
  `this.treeData`; host is `t-custom-ref` + `window.jQuery(ref.el)`.
- *(2026-09-15, `20_14` Gx.8)* Token share still showed two `/ Shares / TEST`
  breadcrumb rows and an empty folder/tag column. Inner
  `t-set="breadcrumbs_searchbar"` never reached `portal.portal_layout`
  (layout printed crumbs) while the slot later set the flag for
  `portal.portal_searchbar` (second row). Sale successor:
  `t-call … breadcrumbs_searchbar="True"`. The left column was already in
  the HTML; `jsTreePortal`'s `xml\`` template still used bare `state.treeData`.
  Checker `qweb-tcall` + `owl-this` on `xml\`` literals.
- *(2026-09-15, `20_14` Gx.8)* Off-proxy `treeData` was not enough for the
  attachment box. Chatter `state_ready` → `this.state.cloudsFolderId = …`
  (OWL proxy) remounts `CloudJsTreeContainer`; the state plugin's 100ms
  `save_state` then reads `this.element.scrollLeft` of null. Stack names
  `contextmenu.get_state` because that plugin is last on the chain. Keep
  the folder id off the proxy, patch `get_state` when `!this.element`,
  stub `save_state` before `destroy`. Do not drop the `state` plugin and
  do not skip `destroy` on a detached host. Portal `jsTreePortal` keeps
  `treeData` off `proxy`; `ready` stays on `proxy` for the `t-if`.
- *(2026-09-15, `20_14` Gx.8)* Token-share `Communication History` heading
  was half-cut. saas `portal.message_thread` is a bare `<h3>`. Dropping
  our wrapper `class="row"` was not enough — the heading as a sibling of
  the row (and inside a nested `.container`) is still clipped. Successor:
  no inner container; `#share_communication` is `col-12` inside the row.
- *(2026-09-15, `20_5` Gx.6)* `<calendar date_delay=...>` dies at install:
  RNG + `FIELD_ATTRIBUTE_NAMES` dropped `date_delay` (19.0
  `calendar_view.rng` + `calendar_arch_parser.js`; absent at saas-19.4).
  Drop the attribute; keep `date_start` / `date_stop`. Same run:
  `@tools.ormcache` is a deprecation that the warning gate attributes to
  us — `@api.ormcache`. Checker `calendar-attr` + `python-api`.
- *(2026-09-15, `20_5` Gx.6)* Gantt popover `<t t-esc=...>` in
  `ir.ui.view` arch dies (`Forbidden owl directive`). `t-out` is on the
  allowed list for qweb-based views; `web_gantt` adds `gantt` to that
  set. OWL `static/src` `t-esc` is unchanged. Checker `qweb-tesc`.
- *(2026-09-15, `20_14` Gx.8)* saas `_to_http_stream` redirects
  `type=url` when `store_fname` is empty (`ir_attachment.py:990`). 19.0
  streamed `db_datas` / `raw` as bytes and never took that branch. Synced
  File Manager thumbs then hit the cloud; Documents FileViewer
  (`/web/image/${documentId}?model=documents.document`) showed the camera
  placeholder when the gate only allowed `download` / `cloud_preview` /
  the preview group. `raw` is `BinaryValue` — use `.content`. Allow
  Documents `model=` / path; keep blocking bare `/web/image/{attach_id}`
  (proved: PNG 1885×1098 vs `size=0`).
- *(2026-09-16, `20_5` Gx.8 walk)* First clicks died on three OWL-3 holes the
  checker had reported clean: Joint Calendar
  `class="o_calendar_sidebar" position="inside"` (exact-string inherit; saas
  expanded panel is `o_calendar_sidepanel_content`), KPI
  `panelState.collapsed` / bare `panelClass`, Reminder Designer
  `update.bind="handleChange"` (`undefined.bind`). Same class as File
  Manager Gx.8. `20_14` `rule_parent.xml` already had `this.handleChange`;
  `20_2` has no FieldFilter. Checker `owl-xpath` exact `class=` +
  `owl-this` `*State.` / `env.` / bind / getter idents.
- *(2026-09-16, `20_5` Gx.8 re-walk)* Formula search died on
  `t-on-keydown="(event) => _onSearchNavigation(...)"` (handler undefined)
  and `orm.call(..., [[record.data.id]])` with a falsy id
  (`AssertionError: Invalid falsy real id` in saas `browse`). Successor:
  `this._onSearchNavigation`; pass `[[]]` when there is no `resId`. Checker
  `owl-this` now flags a `t-on-*` arrow that calls a method without `this.`.
  Same walk: empty calendars / one reminder / one KPI because
  `odootools_demo` never installed (hard depends on unported apps) and the
  `/tmp` seed ignored the 19.0 loaders. Gx.5 cannot be green without
  running those loaders and proving the 19.0 record counts.
- *(2026-09-16, `20_5` Gx.8 access)* Porting `ir.model.access` as an empty
  grouped `ir.access` next to a grouped domain permission ORs the filter
  away. saas `_get_domain_for` is `Domain.OR(permissions) &
  Domain.AND(restrictions)`; empty domain is `Domain.TRUE`
  (`ir_access.py:308`, `:355` at pin `3630379f63633612e5a9e8d435deecbe26eaa15a`).
  19.0 ACL was not a record filter. KPI User then saw every `kpi.item`
  despite `access_user_ids`. Successor: put the domain on the ACL row (or
  drop the empty ACL); keep global rules as restrictions; write explicit
  `[(1, '=', 1)]` only when 19.0 had a TRUE rule. Checker `access-or`.
  `20_2` restrictions are safe.   `20_14` `clouds.share` File Manager empty
  ACL matches a 19.0 TRUE rule — make the TRUE explicit. `total_notify`
  has the same empty-ACL hole as KPI.
- *(2026-09-16, `20_5` Gx.9 review)* Grouped 19.0 `ir.rule` on
  `base.group_user` ported as `ir.access` `operation=crud` granted
  every Internal User write on `kpi.item` / `kpi.category` / `kpi.tag`.
  19.0 ACL for those models was `group_kpi_user` read-only. Successor:
  product-group + 19.0 ops. Checker `access-grant`.
- *(2026-09-16, `20_6` Gx.8)* Demo read restricted `NY/Stock` (Own/All =
  Doris Cole only) without Super Warehouse Manager. Quants and operation
  types stayed hidden. Live `ir.access` on `stock.location` included
  `sale_stock.access_stock_location_user` (`sales_team.group_sale_salesman`,
  empty domain → `Domain.TRUE` at `ir_access.py:308`). Demo has Sales
  "User: Own Documents Only". `_access_domain` after OR was only company.
  Successor: AND the 19.0 `user_ids` filter in `_access_domain` on
  location / quant / move / move.line / picking / picking.type; skip Super
  and `env.su`. Do not hard-depend `sale_stock` just to inherit that xmlid.
  Checker `access-or` now scans core/enterprise empty permissions on models
  this module domains, and stays quiet when `_access_domain` is defined.
- *(2026-09-16, `20_9` Gx.3)* `view-xmlid` reported `website.snippets` gone.
  The template is still there; the checker only indexed `<record id>`.
  Successor: index `<template id>` too. `short_urls` keep the inherit; add
  `group="content"` next to saas inner snippets. `website_url_translations`
  `_onLangChangeClick` `.include()` of `website_root` becomes a `patch` of
  `LangChange` (`@website/interactions/lang_change`). `type_person` search
  filter is gone — hook `inactive`. Typo-report JSON `datas` is not an
  ORM field but `field-lit` still flags it; the wire key is `raw`.
- *(2026-09-16, `20_9` Gx.7)* `website.default_website` is gone. saas
  ships `base.default_website` (`odoo/addons/base/data/website.xml`) and
  `website._ensure_default_website_consistency`. Typo HttpCase
  `setUpClass` died (`ValueError: External ID not found`). Successor:
  `env.ref("base.default_website")`. Checker `view-xmlid` now greps the
  old xmlid in `.py` / `.xml` / `.js` **including tests** (`field-lit`
  skips `/tests/`).
- *(2026-09-16, `20_9` Gx.7)* `request.website` is gone. saas website
  `ir.http` no longer assigns it; current site is `request.env.website`.
  Typo jsonrpc tests then died `AttributeError` on every method even with
  `website=True`. Successor on typo / short_urls / transliterations.
  Checker `python-api`.
- *(2026-09-16, `20_10` Gx.3)* `StaticList._replaceWith` is gone at
  saas-19.4 (present 19.0 `static_list.js:1081`). Four checklist field
  widgets would silently fail to write the SET command. Successor
  `list.set(ids)` (`:455`). Checker `js-symbol` greps `._replaceWith(`.
  Already-ported groups have no leftover.
- *(2026-09-16, `20_10` Gx.6)* `task_checklist` inherit of
  `project.view_task_kanban` died
  (`Element '<field name="priority">' cannot be located`). saas kanban is
  `<kanban card_id="%(project.view_task_card)d">`; `priority` is on the
  card. Successor: inherit `project.view_task_card`. Checker `view-anchor`
  now binds to the inherited arch + `card_id` (global name-set hid this).
- *(2026-09-16, `20_4` Gx.3)* `password_key.export_data` still reads
  `result["datas"]`. saas-19.4 `BaseModel.export_data` returns
  `{'datas': self._export_rows(...)}` (`odoo/orm/models.py:932` at pin
  `3630379f63633612e5a9e8d435deecbe26eaa15a`). That key is not
  `ir.attachment.datas`. Leave it. Checker `field-lit` skips a `datas`
  literal on an `export_data` / `result.get("datas")` line.
- *(2026-09-16, `20_4` Gx.3)* `access-grant` flagged
  `access_portal_password_key` / `_bundle` (`base.group_user` crud next
  to the vaults-group `r` row). 19.0 ACL already granted Internal User
  crud on those models; the grouped `ir.rule` was only a filter.
  Successor: keep `group_user` crud + the 19.0 **internal** bundle
  domain. Put the 19.0 **portal** partner domain on `base.group_portal`
  (the 19.0 rule group), not on `group_portal_password_vaults`.
  Internals receive that vaults group when Portal vaults is on; saas
  `Domain.OR(permissions)` then unions the partner filter with the
  bundle filter. Controller / menu still gate the vaults group.
  Checker reads `origin/19.0` `ir.model.access.csv` and stays quiet
  when that Internal User write already existed.
- *(2026-09-16, `20_4` Gx.6)* 19.0 `_order_field_to_sql(..., query)` died
  at install (`TypeError: missing … query`) while loading
  `account.group_account_readonly`. saas-19.4
  `odoo/orm/models.py:4651` dropped `query`; `_order_to_sql` is
  `(table, order)`. Successor: `(table, field_expr, direction, nulls)`
  and `table.name` like `mailing`. Tests:
  `_order_to_sql(query.table, order)`. Checker `python-api`. Only
  `odoo_password_manager` had the leftover; `knowsystem` is not on
  `_port` yet.
- *(2026-09-16, `20_4` Gx.6)* `task_numbers` inherit of
  `project.view_task_kanban` died
  (`Element '<xpath expr="//main/field[@name='name']">' cannot be
  located`). Same `card_id` shell as `20_10`. Sharing kanban is also a
  shell (`project_sharing_project_task_view_card`). Walking `card_id` in
  `view-anchor` hid this — Odoo applies xpath to the parent only.
  Successor: inherit the card. Checker no longer walks `card_id`; an
  anchor that lives only on the card is a finding.
- *(2026-09-16, `20_4` B1)* Partner-domain portal ACL on
  `group_portal_password_vaults` ORed with the internal bundle row.
  19.0 `portal_password_*_read_rule_portal` used
  `groups=base.group_portal`. Successor: `base.group_portal` + `r`.
- *(2026-09-16, `20_4` B1)* `pwm_jstree_container` still had
  `t-out="title"` and `#{id}`. OWL 3 compile scope is `this`.
  Checker `owl-this` now flags bare `t-out` / `t-esc` idents and
  `#{name}` interpolations.

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
| commit / commit A / commit (a) | **do** the local commit now — never ask “proceed with the commit?”, never push, no review (`16-commit-workflow`) |
| (in **febado**) commit / push \<one workflow\> | febado’s own Mode A/B rule decides — “push this workflow” stays **local** there |
| commit A1 | local commit only, **with** a Cursor review first |
| commit B / commit and push / push | **local Docker tests → check → fix →** then commit → push; review unspecified → **offer** a review before pushing. No local test output → no MR (`16-commit-workflow`) |
| commit B1 / commit B2 | as B, **with** review (B1) / **without** review (B2). GitLab is not the first test run |
| prepare / make / publish a release | faOtools `module.release` on faotools.com via MCP `user-faotools` — `ai_rules_fao` `33-faotools-release` (`tools` / `odoo-apps-addons` only). On 19.0+ **always** finish step 8 (TM + live loader apply) in the same job; skip translations only if the user **explicitly** says so |

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

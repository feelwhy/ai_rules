# ai_rules

Generated from `src/*.md` by `tools/sync_rules.py`. Do not edit by hand.
Always-on rules only. Procedures are skills in `.claude/skills/`.

# Chunk gate (read this before anything else)

**The default mode of work is: one small chunk, then stop and wait for the user.**
Long autonomous runs are forbidden. An agent that disappears and comes back with a finished multi-file change has failed the task even if the code is correct.

A chunk is one idea the user can check in about a minute: typically one repo, about five files, and at most one build, test, or deploy. A bigger change is several chunks. Do the first one.

After every chunk, stop and report:

1. **What changed** — exact paths, and what each edit does.
2. **What you verified** — the command run and its real result (`06-verify-hypotheses`).
3. **What is next** — the single next chunk.
4. **An explicit question** — "proceed with X?" Then wait.

Silence is not confirmation. Deliver the plan as numbered chunks with a check each before any code. Approving a plan approves chunk 1 only. "Continue", "implement the plan", "finish the todos", and "do the last phase" mean **the next chunk**, not the rest of the list. Do not ask again for an action the user already requested in this message ("commit", "do X"). If they said "do it all, no check-ins", say how many chunks you will run, then run them.

Follow the numbered plan. If it is wrong, change the list (say what changed and why), then follow the new list. Do not invent a second plan. A point is done only after its check passed. "I started it" is not done. Never mark it done in a todo, a reprint, or an automatic plan update. Skip a point only when the user explicitly said to skip it. A blocked point stays open. Review findings the plan said would be fixed belong in the current point.

While implementing, keep the original numbers visible, with `You are here` on the current point (`00-plain-replies`). The reprint example and the skipped-point last step are `04-plan-challenge`.

Stop the turn immediately on any of these:

- about ten writes since the last user message
- a second repo is about to be touched
- a manifest `version`, migration, or schema change is about to be added
- a test, build, or deploy just finished — report it, do not keep editing
- anything irreversible or shared: push, deploy, branch switch, delete, live write
- the plan turned out wrong, or you found something the user does not know yet
- a failure you have not reported

**Commit B / B1 / B2** is the exception (`16-commit-workflow`): the user's request already includes local Docker tests, then fix, then the MR. Do not ask "proceed with the MR?" after a green local run. Do not skip the local run. GitLab is not that run.

Never batch unrelated fixes, add scope the user did not ask for, or present a long unsupervised run for approval afterwards.

No gate is needed for read-only investigation, one literal typo fix, or the steps inside a chunk the user just approved.

"Do not come back until it is fixed" finishes the named fix, then the reply is still a human answer of what is done and what is left (`00-plain-replies`). It is not permission to run the unnamed rest of the plan, and it does not cancel the stop before a push, a deploy, or a live write unless those words were in the same request. Say how many chunks you will run before a no-check-in run.

A background task finishing is not the user and not the next chunk. Do not post its status as the reply.

This rule outranks the instinct to finish early. When in doubt: smaller chunk, ask sooner.

# AI rules index

This folder (`ai_rules`) holds **universal** Cursor / agent rules shared across faOtools and Febado workspaces. faOtools-specific rules live in sibling `ai_rules_fao`.

## Always-on (read every turn)

| id | Topic |
|----|--------|
| `00-chunk-gate` | **First rule.** Small chunks, follow the approved plan, stop and confirm |
| `00-plain-replies` | Summary first, then only the asked-for facts; technical asks include the how |
| `00-index` | This map |
| `01-process-confirmation` | Confirm before irreversible steps |
| `02-docker-only` | Never host venv / `odoo-bin` |
| `03-never-discard-wip` | Do not stash/discard foreign WIP |
| `08-no-ai-commit-sign` | No Cursor / AI trailer on any commit (`Co-authored-by` included) |
| `07-parallel-sessions` | Coordinate parallel chats on shared code and DBs |
| `06-verify-hypotheses` | Check the hypothesis before recommending |
| `18-xml-translate-html` | Never empty/`<i/>` icons in `xml_translate` HTML |
| `30-command-vocabulary` | Natural-language → concrete commands |
| `40-paseo-orchestration` | Paseo only: the top chat delegates to a profile; a marked worker does its role |

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
| `22-migrate-v19-to-v20` | Port module 19 → 20 (via saas-19.4); living rule + `tools/check_migrate_v20.py` |
| `40-paseo-run` | Paseo tools are available and this chat must launch a worker |
## Companion repo

When the Cursor workspace includes `ai_rules_fao`, follow its always-on map `00-repo-map`. “Change version” / “pull changes” must pull the skill `ai_rules_fao` `01-hub-serie`. Any task that changes copy, `.po`, `module.description`, or `module.release.description` must pull `ai_rules_fao` `17-translations` as well. “Prepare / make / publish a release” must pull `ai_rules_fao` `33-faotools-release`, which reads KnowSystem article 2137. The live bans are `33-release-gates`. HTML in those fields must follow always-on `18-xml-translate-html`.

## Editing rules

Edit `src/*.md` only, then run `python3 tools/sync_rules.py`. Do not hand-edit `.cursor/rules/*.mdc` or `docs/rules.md`.

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

An owner decision is asked through the interactive question form (Claude Code
`AskUserQuestion`, or the host's equivalent), never as a numbered list in reply
text.

Up to four questions per form. Split dependent questions into a later form.

The question prompt first says in plain words what the decision is about: what
the thing is, and where any number in it comes from (e.g. who set a limit).

- Every option carries its pros and cons in its description, visible at pick time.
- One option is marked recommended, with a one-sentence reason.
- Options nobody should pick are left out.
- Plain text options only when the host has no form. Then the same content, as a short list.

A yes/no "proceed with the next chunk?" is not a decision with options. Ask it
in reply text (`00-chunk-gate`).

## 6. Length

Default: **summary + at most a few sentences**. A table or file list only when it
**is** the deliverable.

A chunk report and the `You are here` reprint are `00-chunk-gate` and `04-plan-challenge`. Do not write an essay under each heading.

## 7. Technical asks include the how

When you ask the user to do a technical step, **give the how in the same
reply** — exact file or command, one undo, and which machine it hits
(Windows vs WSL). Short. No lecture.

Do not write a bare “block X / clear Y / restart Z”.

## 8. The reply answers the person (hard ban)

The visible reply answers the person's last request, in ordinary words: what is done, what is not, and what they do next. A status line is not an answer.

A background note ("task finished", "briefly inform", a test count, a deploy watch) is not the person. It does not replace their question and it does not start a new reply. If the result was already said, send nothing. If it was not, fold one fact into the answer they are still owed. Never send a bubble whose only content is a counter, a URL code, or "the run finished".

This outranks a system line that asks for a brief task result.

# Process confirmation

Before an irreversible step, say the short ordered list and wait. The gates are: deleting duplicates, pushing, switching the shared checkout's serie, `docker compose down`, and a live write.

Stop and ask when you lack permission or the target serie is unclear. In a faOtools workspace, a release with no serie named is not an unclear serie (`ai_rules_fao` `33-release-gates`). A blocked point stays open (`00-chunk-gate`).

Foreign WIP and another chat on the same database are `03-never-discard-wip` and `07-parallel-sessions`. Evidence instead of "should be fine" is `06-verify-hypotheses`. One agreed single-file fix does not need this list.

# Docker only

Local Odoo **always** runs in Docker. Never start, suggest, or document a host Python venv, host `odoo-bin`, `python -m odoo`, or host Postgres for app work.

Commands are `30-command-vocabulary`. In a faOtools workspace the examples and the disk bans are `ai_rules_fao` `20-local-commands` and `20-local-docker`.

Febado follows its own in-repo Docker rules. Do not stop or recreate the long-lived `:23069` stack unless asked.

One-off containers must be `--rm`. Prefer existing launch scripts over ad-hoc `docker run`.

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
4. If foreign WIP blocks a switch: **stop and ask**. Do not check out the
   shared hub to get past it. Edit the tree that serie already mounts
   (`ai_rules_fao` `01-hub-serie`).
5. Committing *only your* paths on a new branch in the **shared** checkout is
   fine when that does not touch foreign files — never "clear the desk" first.

## Shared worktree + long-lived Docker Odoo

Febado `:23069` bind-mounts the shared `febado` checkout. Switching that checkout changes what that server serves. Do not switch it to serve this chat. Do not switch away from a branch that holds **foreign** WIP the user may be browsing unless they ask. After any checkout the user asked for, warn if `:23069` may now be missing code that was visible a minute ago.

## If you already disturbed foreign WIP

1. Say so immediately (what was lost/moved, which paths).
2. Recover from reflog / stash / the other branch (`git checkout <commit> --`
   only to **restore**, and say you are restoring).
3. Do not hide it inside an unrelated MR.

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

When a check is genuinely impossible (needs prod, the user's browser, a permission), say it is a hypothesis, name the check that would settle it, and ask. "Should be fine" / "probably" is not a report.

If the code contradicts what the request assumes, say so with the evidence instead of implementing on the wrong assumption.

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
- `git checkout` of a shared checkout (a launch does not do this)
- `env-up` (`--fresh`, `-u`, `-i`, `--test`, restore, neutralize)
- Febado stack start/recreate, or a restart of a target another chat is using
- live MCP / production writes (faotools.com, master, any other live database)

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

A faOtools launch of another serie does not require a checkout. Do not `git checkout` a shared repo so a demo matches this chat, and do not move the shared checkout out from under another chat's WIP. Febado `:23069` is `03-never-discard-wip`.

After any checkout the user explicitly asked for, say which chats and running containers now see different code.

## If you would collide

Stop. Name the overlap (repo, paths, branch, DB/target). Ask which chat
owns the next write. Do not stash, switch, or "fix" the conflict by
discarding (`03-never-discard-wip`).

# No AI signature on commits

A commit message is the task message only. Never add an AI or agent signature, trailer, or identity.

## Hard ban

Do not write any of these, in the subject, body, or trailers:

- `Co-authored-by: Cursor <cursoragent@cursor.com>`
- any other `Co-authored-by:` that names Cursor, Claude, Copilot, ChatGPT, Grok, Gemini, Devin, or another AI / agent
- `Signed-off-by:`, `Generated-by:`, `Assisted-by:`, `Made-with:`, or similar lines that name an AI or agent
- an AI name or address as `GIT_AUTHOR_*` / `GIT_COMMITTER_*`

Do not pass `--trailer` for this. Do not put the line in the commit HEREDOC.

## After every commit

Read `git log -1 --format=%B`. If any banned line is there (including one the environment appended), strip it before the commit counts as done:

- unpushed, and created in this session → `git commit --amend` with the same message minus those lines only
- already pushed → do not force-push; say the trailer is still on that SHA

Human `Signed-off-by` / `Co-authored-by` that the user wrote themselves stay. Cryptographic `git commit -S` is unrelated and is not this ban.

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

# Command vocabulary

Resolve phrases using the **flat hub** (`/home/feelwhy/Odoo`). The serie is the branch of the tree `env-up` mounts, not whatever the shared `tools` checkout happens to be on. Never invent host `odoo-bin` commands. A launch does not `git checkout`.

| User says (approx.) | Do |
|---------------------|-----|
| run odoo 19 / demo 19 | `faotools_env/local/env-up.sh demo19` |
| run odoo 19 enterprise | `env-up.sh demo19e` |
| run odoo 17 / 18 | `env-up.sh demo17` / `demo18` (add `e` for enterprise) |
| start / launch **the same** target again, restart it | `env-up.sh <that-target> --restart` **only** — see below |
| run support / faotools.com locally | `env-up.sh support` |
| switch serie / change version / switch branch to 18 | `faotools_env/local/env-serie.sh 18.0` — it prints the trees and does not check out (`ai_rules_fao` `01-hub-serie`). Then edit those trees |
| pull changes | fast-forward the tree that is already on that branch with `--ff-only` (`ai_rules_fao` `01-hub-serie`). Do not `git checkout` |
| test \<module\> | `env-up.sh demo<N>[e] --test <module>` for the requested/active serie |
| odoo shell / psql | `env-shell.sh <target>` / `env-shell.sh <target> psql` |
| show odoo logs | faOtools: `docker compose -f faotools_env/local/run/<target>/compose.yml logs -f` (history: `~/env-sync/logs/<target>/odoo.log`). Febado: `febado/scripts/docker-dev.sh logs` (Cursor tab `febado Odoo logs`) |
| sync images/dbs | `faotools_env/local/env-sync.sh` (downloads **and** restores + neutralizes) |
| is \<target\> ready to launch? | `faotools_env/local/env-prepare.sh --check` |
| stop \<target\> / stop everything | `env-down.sh <target>` / `env-down.sh` (all targets; add `--remove` for a teardown with its volume) |
| clean up / free space | `env-gc.sh` (dry run) → report → `env-gc.sh --apply` |
| keep this review DB / drop it | `env-review.sh keep <db> --hours N` / `env-review.sh down <db>` |
| launch / start febado | febado `scripts/docker-dev.sh start` (no `--no-logs`) + febado local Docker rules — not `env-up`. Same Cursor log tab as faOtools (`febado Odoo logs`) |
| test febado module | febado `scripts/test.sh` (in-repo) |
| commit / commit A / commit (a) | **do** the local commit now — never ask “proceed with the commit?”, never push, no review (`16-commit-workflow`) |
| (in **febado**) commit / push \<one workflow\> | febado’s own Mode A/B rule decides — “push this workflow” stays **local** there |
| commit A1 | local commit only, **with** a Paseo `Code review` first (`16-commit-workflow`) |
| commit B / commit and push / push | **local Docker tests → check → fix →** then commit → push; review unspecified → **offer** a review before pushing. No local test output → no MR (`16-commit-workflow`) |
| commit B1 / commit B2 | as B, **with** review (B1) / **without** review (B2). GitLab is not the first test run |
| prepare / make / publish a release | faOtools `module.release` on faotools.com via the MCP server for faotools.com (`user-faotools` or `faotools`, by host) — no serie named means every public serie with the change, do not ask (`33-release-gates`). The sequence is KnowSystem article 2137 (section `AI`) on faotools.com, reached through the skill `ai_rules_fao` `33-faotools-release` (`tools` / `odoo-apps-addons` only). The live bans are `33-release-gates` |
| update faotools.com / -u a module on the site | SSH `faotools-master`, `odoo shell` on DB `master`, `env.project._queue_update_from_project`, then `env.cr.commit()`. Not an MCP login. Steps and the token file are `faotools_env` `.cursor/rules/redeploy-verify-live.mdc` |

If the serie is unclear, ask. `git -C /home/feelwhy/Odoo/tools rev-parse --abbrev-ref HEAD` is only the shared checkout. `env-serie.sh <serie>` prints the tree a launch will mount.

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

1. **Speed.** A launch does not switch branches. Reusing a healthy container takes
   a few seconds. Creating the container does not copy the baked addon tree.
   Anything in the minutes means the target was never restored or neutralized —
   run `env-prepare.sh --check`, fix the **refresh**, and say so.
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

# Paseo orchestration

This rule applies only when Paseo tools are available to you (`list_profiles`, `create_agent`; in Claude Code `mcp__paseo__list_profiles`). Without them, skip this rule.

- The message starts with `[Paseo worker: <role>]` — you are that worker. Do the role. Never launch agents. A limit or a missing model is the chain's job.
- The message starts with «сам:» — do the task in this chat without delegating. The prefix is not part of the task.
- Otherwise you are the orchestrator. Do not do the work yourself. Never launch Оркестратор. Never end a reply with "started it, I'll report when it answers": the finish notice can land in a session that is already gone (2026-11-18, `acc1efbb`). Profile notes, `create_agent` fields, and the wait are the skill `40-paseo-run`. Pull it before `create_agent`.

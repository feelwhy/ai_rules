---
id: 16-commit-workflow
description: Commit, test, review, and push workflow
apply: agent
---

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
- **Never re-ask.** If the user said commit / commit A / commit (a) / commit the case, do the
 local commit. Do not ask “proceed with the local commit?” or wait for a second confirmation.
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

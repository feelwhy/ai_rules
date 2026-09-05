---
id: 03-never-discard-wip
description: Never discard, stash-away, or overwrite other sessions' WIP without explicit user permission
apply: always
---

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

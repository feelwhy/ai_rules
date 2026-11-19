---
id: 07-parallel-sessions
description: Coordinate parallel chats that share a checkout or database — do not collide
apply: always
---

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

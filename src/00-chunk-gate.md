---
id: 00-chunk-gate
description: Work in small checkable chunks and stop for user confirmation after each one
apply: always
---

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

---
id: 00-chunk-gate
description: Work in small checkable chunks and stop for user confirmation after each one
apply: always
---

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

While implementing, keep the original numbers visible, with `You are here` on the current point (`00-plain-replies`) and every open point shown in full, never collapsed. The reprint example and the skipped-point last step are `04-plan-challenge`.

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

---
id: 01-process-confirmation
description: Confirm with the user before irreversible steps
apply: always
---

# Process confirmation

Before an irreversible step, say the short ordered list and wait. The gates are: deleting duplicates, pushing, switching the shared checkout's serie, `docker compose down`, and a live write.

Stop and ask when you lack permission or the target serie is unclear. In a faOtools workspace, a release with no serie named is not an unclear serie (`ai_rules_fao` `33-release-gates`). A blocked point stays open (`00-chunk-gate`).

Foreign WIP and another chat on the same database are `03-never-discard-wip` and `07-parallel-sessions`. Evidence instead of "should be fine" is `06-verify-hypotheses`. One agreed single-file fix does not need this list.

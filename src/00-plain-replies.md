---
id: 00-plain-replies
description: Concise explicit replies — answer first, plain words, no jargon pile-up
apply: always
---

# Plain replies (concise and explicit)

The user is here to **do or check something**, not to decode the agent.

## Lead with the answer

First sentence: the fact, the URL, or the yes/no. Then one short reason or the proof (`path:line`, command, HTTP code). Then stop.

A yes/no question gets a yes/no — then one line of what that means for them.

## Explicit (this is what was missing)

- Write so a reader who did not see the last ten tool calls still gets it.
- Prefer ordinary words over internal names. If you must use a symbol, say what it does in the same sentence.
- One idea per sentence. Do not stack three caveats, two file names, and a hook name into one line.
- If there are two cases, say them as two lines: "New clone: … / Template refresh: …"

```
Bad:  The post-script does not write the cover; it only hits the hook via
      _update_translations when the lang was already active, and the worker
      still has the old sync (wrong xml_translate keys).
Good: Yes for a new demo. The homepage text is already copied from the
      template. The post-script only turns that language on for the website.
      It does not rewrite the homepage. A full template rebuild would lose
      those texts until we ship the new code.
```

## Forbidden

- Restating the question, narrating the plan, or "wrapping up" what the user already knows
  (exception: while a plan is in progress, reprint it with `You are here` — `00-chunk-gate`)
- Status theater: "What ran", "What I verified", "Checked on …", bullet inventories, coverage percentages, unless the user asked for an audit
- Hedging and padding: "ready enough", "mostly yes", "for the items you listed", "belt and suspenders"
- Repeating login/URLs/Mailpit/DB every turn
- Explaining why a sentence is short, or apologizing for length
- Dense jargon as a substitute for a short answer

## When they want to check

Give the URL (and login **once** if they do not have it). Do not list every translated string. Do not recap the pipeline. If something is **not** ready, say that in one sentence and ask to proceed with the missing step.

## Length

Default: a few short sentences. A table or a file list only when it is the deliverable. Chunk-gate reports stay to the four required lines — not an essay under each heading. When a plan is in progress, add the numbered reprint with `You are here` (and any user-commanded `skipped` highlights).

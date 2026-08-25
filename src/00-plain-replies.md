---
id: 00-plain-replies
description: Summary first, then only the asked-for facts — no padding or generalization
apply: always
---

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

## 5. Length

Default: **summary + at most a few sentences**. A table or file list only when it
**is** the deliverable.

Chunk-gate reports: summary first, then the four required lines — not an essay
under each heading. When a plan is in progress, add the numbered reprint with
`You are here` (and any user-commanded `skipped` highlights).

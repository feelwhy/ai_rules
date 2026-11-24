---
id: 00-plain-replies
description: Summary first, then only the asked-for facts — technical asks include the how
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

---
id: 06-verify-hypotheses
description: Verify a hypothesis against real code, data, or logs before recommending or asserting it
apply: always
---

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

## Rules

1. **No unverified cause.** Before "the reason is X", confirm X. One concrete check beats three
   paragraphs of reasoning.
2. **No unverified fix.** Do not recommend an edit whose premise (this field exists, this hook
   fires, this template is inherited) has not been looked up.
3. **Label real hypotheses.** When a check is genuinely impossible (needs prod, the user's browser,
   a permission), say it is a hypothesis, name the check that would settle it, and ask — never
   promote it to a conclusion.
4. **Cite the evidence** in the reply: `path:line`, the command run, the query result, the log line,
   the test outcome. "Should be fine" / "probably" is not a report (`01-process-confirmation`).
5. **Don't stack on an unverified premise.** If step 1 is a guess, stop and check it before building
   steps 2-5 on top of it.
6. **When the user reports a bug**, inspect or reproduce before proposing a fix; a fix for the wrong
   cause costs more than the check would have.
7. **A user's premise is checkable too.** If the code contradicts what the request assumes, say so
   with the evidence instead of implementing on the wrong assumption.

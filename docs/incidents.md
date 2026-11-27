# Incident history

The always-on rules keep the ban. This file keeps the story. It is not loaded
into every chat.

Longer logs stay where the work happens: `src/16-commit-workflow.md`,
`src/22-migrate-v19-to-v20.md`, and in `ai_rules_fao` the skills
`33-faotools-release`, `17-translations`, `36-major-version-port`.

## 2026-07-28 — foreign WIP was stashed

A prep step stashed and rebased the shared worktree while another
chat's unfinished change was present. The change was dropped, and what it
had hidden reappeared on the running local server without permission. The ban is `03-never-discard-wip`.

## 2026-08-23 — an empty icon swallowed the page

App pages on faotools.com rendered as leftover icon glyphs. An empty
`<i></i>` becomes `<i/>` under `xml_translate`, and HTML5 leaves the tag
open. The ban is `18-xml-translate-html`.

## 2026-09-01 — screenshot captions stayed English

The Google Drive guideline body was translated. `/ru/` captions stayed
English (`Open the Google Auth Platform`). The ban is `17-translation-gates`.

## 2026-09-09 — a restyled template left an empty term

Appointments `Any` / `Select` stayed empty on an existing database after the
English in the template changed. The ban is `17-translation-gates`.

## 2026-09-10 — a changelog shipped in English

Appointments `1.3.33`: `/ru/` still showed the English changelog. A filled
`.po` was treated as published. The ban is `33-release-gates`.

## 2026-09-23 — a red test log stopped a push

A push stopped after a red test run and reported that instead of fixing it. The ban is the skill `16-commit-workflow`.

## 2026-09-28 — disks filled up, and an MCP write had to be repeated

Docker Desktop on WSL brought up 22 Odoo containers. Postgres held 167
databases (152 left by agents) and 62 orphaned volumes of about 1.2 GB. Two
WSL virtual disks reached about 400 GB. The bans that remain in every chat
are `20-local-docker`: stop what you started, do not leave databases behind,
do not `docker prune`. The same day an MCP encoding error on a release meant
the payload had to be rewritten and applied again (`33-release-gates`).

## 2026-11-18 — a Paseo result arrived in a dead session

The top chat ended with "started it, I'll report when it answers"
(`acc1efbb`). The finish notice landed in a session that was already gone.
The ban is `40-paseo-orchestration`.

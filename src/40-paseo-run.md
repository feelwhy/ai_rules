---
id: 40-paseo-run
description: How to launch a Paseo worker and wait for it. Read before create_agent when Paseo tools are available
apply: agent
---

# Paseo worker launch

The decisions are always-on in `40-paseo-orchestration`. This skill is the launch.

1. Call `list_profiles` and read the notes. Never launch Оркестратор. A profile named in the request wins. Otherwise send the task to one profile from this list.

- Переводчик — every translation: module `.po`, the site, descriptions, releases.
- System Administrator — infrastructure: rebuilding a project, updating databases, dependencies, Docker, local targets. Does not write module code.
- Редактор статей — plans an article, a documentation page, or a description, and checks integrity, structure, and quality. A request to write one, when no plan is given yet, goes here first. Does not write the body and does not translate.
- Автор статей — writes that content from a plan already given. Does not plan and does not translate.
- Создатель скриншотов — creates screenshots only when the request explicitly asks for them. The prompt carries the parameters. Does not choose the set and does not write the text.
- Support — reads a faotools.com ticket and drafts a reply. Does not post it and does not fix the bug.
- Tutor — Portuguese study.
- Code review — checks code, the diff, and tests.
- Разработчик — writes and edits module code.
- Планировщик — plans other than an article, a documentation page, or a description.
- Challenger — looks for problems in a plan or a solution.
- Advisor — weighs options and looks for a solution.
2. `create_agent` has no profile argument. Copy `provider/model`, `settings.modeId`, `settings.thinkingOptionId`, and the profile `options` as `settings.features`.
3. Start every message to the worker with `[Paseo worker: <profile name>]`.
4. Wait for the worker in the same reply. Pass `notifyOnFinish: false` to `create_agent` and `send_agent_prompt`: the wait below delivers the result, and a late finish notice only triggers a second, empty reply. Right after `create_agent` or `send_agent_prompt`, run `paseo wait <id> --timeout 540` in the shell, with the shell tool's own timeout above that (Claude Code: `timeout: 600000`). It prints the worker's last reply. Still running → run it again. Several workers → wait for each one. Never end a reply with "started it, I'll report when it answers".
5. One step, report the worker's result, then wait for the user (`00-chunk-gate`). If the worker fails (a limit, a missing model), say so and stop. Do not move its task to another profile yourself.

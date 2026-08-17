---
id: 15-translations
description: Translation and i18n conventions for Odoo modules
apply: agent
---

# Translations

- User-facing strings in Python, XML, and JS must be exportable (`_()`, XML text nodes, OWL/`_t` as used by the serie).
- Do not wrap technical identifiers, logger messages, or already-translated values unnecessarily.
- Prefer editing source strings in code/XML over hand-patching `.po` unless the task is translation-only.
- After string changes that matter for release, mention that a translation export/update may be needed.
- Keep existing `i18n/` structure and language codes; do not delete translation files casually.
- On serie upgrades, follow migration rules for deprecated `_()` uses (e.g. pure-Python constraint messages on 18+).

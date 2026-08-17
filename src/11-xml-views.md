---
id: 11-xml-views
description: XML conventions for views, data, templates, menus, and reports
apply: agent
---

# XML IDs
- Prefix new IDs with the module technical name or the module's established prefix.
- Do not reference XML IDs from another custom module unless the manifest declares that module in `depends`.
- Prefer stable IDs for apps-store upgrades; do not rename existing IDs without a migration reason.

# Views
- Inherit Odoo/core views with targeted `<xpath>` changes; do not redefine full upstream views.
- Keep form structure conventional: `<header>`, `<sheet>`, grouped fields, `<notebook>`, chatter when used.
- Preserve existing groups, attrs/modifiers, context, domain, and sequence behavior unless the task targets them.

# Data
- Put seed/configuration records in `data/`; demo-only records in `demo/` and manifest `demo`.
- Use `noupdate="1"` only for records that should not be changed by module upgrades.
- Avoid hardcoded database IDs. Use `ref()` and external IDs.

# QWeb
- Use `t-out` for escaped output and avoid `t-raw` unless content is already sanitized HTML.
- Inherit website/portal templates with `t-inherit` and precise XPath changes.
- Keep translatable user-facing strings extractable.

# Menus and Actions
- Menu items should define parent, action when applicable, sequence, and groups where access is restricted.
- Window actions should declare `view_mode` in the intended priority order.

---
id: 13-security
description: Access rights, record rules, portals, and security-sensitive code
apply: agent
---

# Access Rights
- Every persistent model needs explicit `ir.model.access.csv` entries unless it is intentionally transient or abstract.
- Keep CSV header exactly: `id,name,model_id:id,group_id:id,perm_read,perm_write,perm_create,perm_unlink`.
- Grant portal/public permissions narrowly and only for records they should actually reach.

# Record Rules
- Add record rules for company, website, portal, vendor/customer, or user-owned data boundaries.
- Bind rules to groups where possible; unscoped global rules need a clear reason.
- Use domains based on `user`, `company_ids`, partner relations, or website context, not hardcoded IDs.

# Controllers
- Every `@http.route` must explicitly declare `auth`, `type`, `methods`, and `csrf` when relevant.
- Validate request payloads before write operations. Never trust client-side domains or readonly fields.
- For public routes, check access tokens/signatures or use standard portal token patterns when exposing private records.

# Secrets and External Services
- Store credentials in settings / `ir.config_parameter`; never in manifests, data files, JS, or templates.
- Use explicit request timeouts and sanitized logging for outbound HTTP calls.

# Review Checklist
- New model: access CSV added, record rules considered, and tests added for denied access when practical.
- New controller: auth mode, CSRF behavior, access checks, and error payloads reviewed.

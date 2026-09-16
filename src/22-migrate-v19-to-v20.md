---
id: 22-migrate-v19-to-v20
description: Checklist and transforms for migrating an Odoo module from 19.0 to 20.0 (via saas-19.4)
apply: agent
---

# Odoo 19 -> 20 migration

Apply these transforms when porting a module to 20.0. Assumes the module is already 19-clean
(see `21-migrate-v18-to-v19`). Keep public model/field/XML-ID names stable unless the upgrade
renames them. **Do not write `20.0.x.y.z` while the stand-in is a saas branch** — see
**Manifest version** below. Override in the module, never edit `odoo/`.

**This rule is living.** Every fact below is source-confirmed against a stated pin. When a port
reveals a new fact: decide the fix, apply it, prove it, then write the fact here and into
`tools/check_migrate_v20.py` in the same job. Pause only for a current-serie defect that must
be fixed on 19.0 first, or when there is a real choice of successor.

Tested pins (2026-09-12, pre-release):

| Ref | SHA |
|---|---|
| `odoo@saas-19.4` | `3630379f63633612e5a9e8d435deecbe26eaa15a` |
| `enterprise@saas-19.4` | `8d73a02a8ba9a99fb41b2cd01b1680c6ded4b837` |

Full evidence: `ai_rules_fao/docs/20-saas-19.4-delta.md`.

## Read this before any 19 -> 20 port

### The saas branches are independent forks, not a chain

`saas-19.1` … `saas-19.4` are **not** ancestors of one another, and none is a descendant of `19.0`.
Their common ancestor with `19.0` is the release cut. Measured on the pins above: **8638 commits
exist in `19.0` that are absent from `saas-19.4`**.

Consequences:

- Commit counts per "boundary" measure nothing. Compare **trees**, not ancestry.
- **A fix present on `19.0` may not be on the target.** Never assume a 19.0 bugfix travelled; check
  the target tree.
- Attribute a change to the first serie whose tree lacks what you use.

### Release notes are not a porting signal

Across 19.1-19.4 the official notes contain **one** technical entry. Every other break in this rule
was found by static existence checks. Read the notes for discovery, then confirm in source — and
never wait for a note to tell you something broke.

### Silent failures outnumber loud ones

Most of the 19 -> 20 damage does not raise:

- An override of a hook upstream deleted is **never called**. No error, no warning, no failed install.
- A write to a removed field can be **silently dropped** (see `ir.attachment.datas`).
- A string-keyed field name (group-by, domain, selection) just stops resolving.

Tests and warning gates do not catch these. Run `tools/check_migrate_v20.py` and read its output.

## Dead-override check (run this first, every module)

For **every** override of a core hook, assert the hook still exists on the target. Bind the check to
the **inherited model or imported class**, never to a global name search: a surviving name on an
unrelated model hides a dead hook, and a module-internal `super()` chain looks dead because its name
never existed upstream.

Confirmed dead hooks on `saas-19.4`:

| 19.0 hook | 20.0 successor |
|---|---|
| `mail.thread._track_subtype(initial_values)` | `_track_log_get_default_subtype(track_init_values)` — renamed parameter; returns an empty `mail.message.subtype` recordset, not `False` |
| `res.users.SELF_READABLE_FIELDS` / `SELF_WRITEABLE_FIELDS` | **delete the override**; set `user_writeable=True` on the field itself |
| `mail.message._extras_to_store` | `_store_extra_fields(res, *, format_reply)` |
| `mail.message._to_store_defaults` | `_store_*_fields(self, res: Store.FieldList)` family |
| `mail.thread._get_store_message_update_extra_fields` | `_store_message_fields` — moved to `mail.message` |
| `res.users._init_store_data` | `_store_init_fields` / `_store_init_global_fields` |
| `ir.attachment._inverse_datas` | `_inverse_raw` |
| `BaseModel._check_access(operation)` | **name survives**, never called. `_access_domain` + `res_access_*` (see below) |

`tracking=True` on a field is **still valid** (`mail.track.mixin._valid_field_parameter`).

### `_check_access` is dead even though the name survives

`check_access` / `has_access` / `_filtered_access` are `@typing.final` at saas-19.4
(`odoo/orm/models.py:3371`) and call `_access_domain`. `_check_access` still exists
(`:3499`) but is `@deprecated("Since 20.0, use Model._access_domain instead")` and is
**never called**. Overriding it is a silent miss: a write that used to raise
`AccessError` succeeds.

Observed on `20_14` Gx.7: `TestCloudsFolderPreparing.test3_security_rights_check`
`AssertionError: AccessError not raised` at `rule_folder_1.with_user(...).write({})`.
Gx.2 on 19.0 is green for the same test.

Successor: match `ir.attachment` / `mail.activity`:

1. `_access_domain_heavy = True`
2. Computed searchable `res_access_read` / `res_access_write`
   (`groups=fields.NO_ACCESS`, `compute_sudo=True`,
   `depends_context=('uid',)` plus every field the old `_check_access` read —
   `depends_context=('uid',)` alone caches a True after the first
   `has_access` and misses a later `access_user_ids` / `rule_id` write)
3. `_compute_res_access` / `_search_res_access` — body of the old `_check_access`
   **minus** `super()` ACL
4. `_access_domain(operation)` = `super() & Domain(f"res_access_{op}", "=", True)`
   with create/unlink mapped to write
5. Delete `_check_access`

In compute, use `self.sudo(False)` before `_inaccessible_comodel_records` (that
helper no-ops when `env.su`). Do **not** skip checks because `compute_sudo` makes
`env.su` True.

`has_access('read')` short-circuits on `env.transaction.access_read` (keyed by
uid). `_check_access` re-evaluated every call; after the port, a write that
changes the data `_access_domain` reads must
`self.env.transaction.invalidate_access_cache(self._name)` or the next read
keeps the old True. Core mail tests do the same after changing the related
record.

An override that only passed context into `super()._check_access` (e.g.
`cloud_base` `ir.attachment` `ir_attachment_security`) becomes the same context on
`_inaccessible_comodel_records`.

In `tools@19.0`: `cloud_base` (folder + attachment), `message_edit`,
`joint_calendar`, `business_appointment`. Checker kind is `dead-hook` via
`DEAD_DESPITE_EXISTING` — a name-exists check reports clean.

### x2many to `res.users` hides inactive rows

saas-19.4 Many2many read (`odoo/orm/fields_relational.py`) splits out inactive
comodel rows (`active_test=True` by default). The write still stores them; the
next `record.user_ids` is empty. 19.0 returned OdooBot / archived users on the
same field.

A security compute that builds an allow-list from a Many2many to `res.users`
(or `res.groups` → users) must read
`record.with_context(active_test=False).<m2m>`. Otherwise a write of
`base.user_root` (inactive) is a silent no-op: stored restriction stays `[]`,
`has_access` stays True. Observed on `20_14` Gx.7 Case 5
(`clouds.folder._compute_restricted_users`). Not a 19.0 defect — Gx.2 is green.

Do **not** "fix" this by pointing the test at an active user. That drops the
19.0 meaning (an archived-only restriction still locks the folder).

No reliable checker kind: a `Many2many("res.users")` grep is every user-tags
field. Read the compute.

### Ordering hooks: dead before 19.0, same successor on both refs

These three are `stale-override`, not `dead-hook` — absent from core at **both** refs, so they were
already doing nothing on 19.0. The successor is the same on 19.0 and saas-19.4, which is why the fix
belongs on the current serie and ports over unchanged.

| Removed hook | Successor |
|---|---|
| `_generate_order_by(order_spec, query)` | `_order_field_to_sql(alias, field_name, direction, nulls, query)` |
| `_generate_order_by_inner(alias, order_spec, query, …)` | same |
| `_inherits_join_calc(alias, fname, query)` | `_field_to_sql(alias, field_expr, query)`, normally reached through the hook above |

`_order_field_to_sql` (`odoo/orm/models.py:5262`) is the per-field hook `_order_to_sql` calls, and it
is what core itself overrides for this (`stock_picking.py:240`, `project_project.py:725`,
`res_device.py:65`). Build the term from `self._field_to_sql(...)` rather than a hand-written column
reference: that keeps core's read-access check and, for a translated field, core's
`COALESCE(col->>'<lang>', col->>'en_US')` fallback chain.

```python
# BEFORE (dead since before 19.0) — string surgery on the whole ORDER BY clause
def _generate_order_by(self, order_spec, query):
    res = super()._generate_order_by(order_spec=order_spec, query=query)
    return res.replace('"my_table"."name"', 'LOWER("my_table"."name")')

# AFTER — one term, translation-aware, access-checked
def _order_field_to_sql(self, alias, field_name, direction, nulls, query):
    if field_name == "name":
        return SQL("LOWER(%s) %s %s", self._field_to_sql(alias, field_name, query), direction, nulls)
    return super()._order_field_to_sql(alias, field_name, direction, nulls, query)
```

Note the return type: `_order_to_sql` composes `SQL` objects, so `str.replace` on the result is not
available even if the old hook still existed. Fixed on 19.0 in `knowsystem` and
`odoo_password_manager` (2026-09-12).

**Assert the emitted SQL, not the row order.** A "mixed-case rows come back sorted" check cannot
tell a working lowercase hook from a dead one on our databases: they are created with `en_US.utf8`
collation (`datcollate` on every `env-sync` target), where Postgres already ignores case while
ordering. Pick probes whose byte order and case-insensitive order genuinely differ, and assert
`LOWER(` in `_order_to_sql(...).code`; keep the row-order assertion only as a smoke test that the
term is valid SQL.

### Portal sharing field list: current-serie cache, both refs

`project.task._portal_accessible_fields` is `@ormcache(cache='stable')` at **both** pins
(19.0 `:1048`, saas-19.4 `:1077`). Portal `fields_get` / `_has_field_access` then keeps only that
frozen set. The sharing form arch is ordinary inherited XML and is **not** filtered the same way.

`task_custom_fields` extends `TASK_PORTAL_READABLE_FIELDS` / `TASK_PORTAL_WRITABLE_FIELDS` from live
`custom.task.field` rows (`portal_edit_placement`). `_generate_xml` writes those names into
`project.project_sharing_project_task_view_form`. The stable cache does not invalidate on that
write. A portal collaborator then gets `TypeError: "project.task"."x_oz_tsk_N" field is undefined`
in `Field.parseFieldNode` (arch has the node, `get_views` `models.fields` does not).

This is a defect on the **current** serie (ledger `source_serie_defects` id 6). Do **not** paper it
over on 20 only (do not drop the field from the sharing arch, do not sudo `fields_get` for portal).
Fix on 19.0: invalidate `project.task._portal_accessible_fields` from `custom.task.field`
create/write/`_generate_xml`. A process restart only refreshes the cache until the next write.

The checker cannot see this: both hooks exist at both refs, and a grep for `TASK_PORTAL` + `search(`
would stay red after a correct invalidate-on-write. Prove it with HTTP `get_views` on the **running**
worker as a portal user (a new `odoo shell` process has a fresh cache and hides the hole). 19.0
demo data leaves `portal_edit_placement` empty, so the sharing form never injects `x_oz_tsk_*` and
the hole stays latent there.

## Python

### Manifest version — drop the serie prefix on the saas stand-in

`odoo/modules/module.py` `check_version` (`:452`) sets `installable=False` and logs a warning
when the adapted version does not start with `release.major_version + '.'`. On the
`faotools/env-demo-20:current` image that string is **`saas~19.4`**, not `19.0` and not `20.0`.
Measured on that image at the pin above:

| Manifest `version` | `adapt_version` | `installable` |
|---|---|---|
| `19.0.1.0.2` (every `tools` module on 19.0) | `19.0.1.0.2` | **False** |
| `20.0.1.0.2` (what this rule used to say to write) | `20.0.1.0.2` | **False** |
| `1.0.2` (three parts, no serie) | `saas~19.4.1.0.2` | True |

A serie-prefixed version is accepted only on that exact serie. Writing `20.0.x` therefore
breaks the module on the stand-in we actually run, and it fights `ai_rules_fao`
`11-manifest-version`. The port exception is:

1. **Gx.3 (saas-19.4):** drop the serie prefix. `19.0.1.3.33` → `1.3.33`. Leave a one-line
   comment that phase 8 / `Fx` re-prefixes. The checker reports leftover prefixes as
   `manifest-version` when `--odoo-ref` is a `saas-*` branch.
2. **Fx / phase 8 (real 20.0):** re-prefix to `20.0.x.y.z`. That is the one bump
   `11-manifest-version` allows for this program.

Do not invent a fourth number. The tail after the serie is what stays.

### `version_info[0]` is a string on a saas branch

`odoo.release.version_info` on saas-19.4 is `('saas~19', 4, 0, 'final', 0, '')`. Code that
does `"%s.0" % version_info[0]` or `int(version_info[0])` is wrong on the stand-in. Treat a
`saas~N` major as the **next** released major (`20.0`). Example:
`odootools_demo` `_demo_ticket_serie`.

### `res.users` self-access: field parameter, not a list

`SELF_READABLE_FIELDS` / `SELF_WRITEABLE_FIELDS` are gone (13 and 8 core definitions at 19.0, zero
now). Access is decided per field by `user_writeable`.

```python
# BEFORE (19.0) — property override on res.users
@property
def SELF_WRITEABLE_FIELDS(self):
    return super().SELF_WRITEABLE_FIELDS + ["my_pref_field"]

# AFTER (20.0) — drop the override entirely, declare on the field
my_pref_field = fields.Boolean(string="My Preference", user_writeable=True)
```

### `ir.attachment.datas` removed — and writes are swallowed

`datas` no longer exists. `_check_contents` pops it and emits `warnings.warn("Use raw, datas has
beeen removed")`, so a `create`/`write` carrying `datas` **succeeds and stores nothing**.

This is also an encoding change: `datas` was base64. `raw` is a `BinaryValue`
(`odoo.tools.binary`), not a `bytes`. Read the payload as `record.raw.content`.
A write still accepts bytes.

```python
# BEFORE
self.env["ir.attachment"].create({"name": fname, "datas": base64.b64encode(content)})
# AFTER
self.env["ir.attachment"].create({"name": fname, "raw": content})
# READ
payload = record.raw.content  # bytes; record.raw itself is BinaryValue
```

Audit every attachment write, not just the ones a grep highlights. Encode to
base64 only at the boundary that still needs it.

saas `_to_http_stream` (`odoo/addons/base/models/ir_attachment.py:990`) is a
different hole from `datas`. After `store_fname` it does
`elif self.url: return Stream(type='url', url=self.url)`, then
`data = self.raw.content`. 19.0 used `elif self.db_datas` and streamed
`self.raw` as bytes — it never redirected a URL-only attachment. A synced
`type=url` row with no filestore file therefore **sends the browser to the
cloud URL** unless the module overrides `_to_http_stream`. Observed `20_14`
Gx.8: File Manager `/web/image/<attach_id>` and Documents FileViewer
`/web/image/<docId>?model=documents.document`. Successor in `cloud_base`:
override, fetch only when `_cloud_http_may_fetch` allows (`download` /
`cloud_preview` / preview group / Documents model or path), and return an
empty `type=data` stream for a bare list/kanban thumb.

### `odoo.http` is a package — `Stream` / `content_disposition` moved

19.0 is a single `odoo/http.py`. saas-19.4 is `odoo/http/` (`__init__.py` at the pin). That
file re-exports `request`, `Controller`, `route`, `Response`. It does **not** re-export
`Stream` or `content_disposition` — those live in `odoo/http/stream.py`.

Observed on the saas-19.4 image during `20_14` Gx.6: `ImportError: cannot import name
'Stream' from 'odoo.http'` while loading `cloud_base`. A leftover
`from odoo.http import content_disposition` fails the same way. Checker kind is
`python-api` (import form). In `tools@19.0` this is `cloud_base` (3 sites) and
`short_urls` (1).

```python
# BEFORE
from odoo.http import Stream, content_disposition, request
# AFTER
from odoo.http import request
from odoo.http.stream import Stream, content_disposition
```

Keep `from odoo.http import request` / `Controller` / `route`. Do not "fix" those.

### `ir.config_parameter.get_param` / `set_param` are gone

Both methods exist at 19.0 (`odoo/addons/base/models/ir_config_parameter.py`) and are **absent**
at saas-19.4 (zero `def get_param` / `def set_param` in the tree). The successor is a typed
pair: `get_str` / `get_bool` / `get_int` / `get_float` and `set_str` / `set_bool` / `set_int` /
`set_float`. Defaults are typed too (`get_str(key, default='')`, `get_bool(key, default=False)`).

Observed on the saas-19.4 image during `20_2` Gx.8 neutralize: `AttributeError` on `set_param`.
In `tools` this is **166 production + 55 test call sites** (`get_param` 153, `set_param` 68),
plus 35 in `system` and 5 in `odoo-apps-addons`. The checker kind is `python-api`.

```python
# BEFORE
icp.get_param("web.base.url", default="http://localhost:8069")
icp.set_param("my.flag", "True")
# AFTER
icp.get_str("web.base.url", "http://localhost:8069")
icp.set_bool("my.flag", True)   # or set_str if the value is really a string
```

Do not keep `safe_eval(get_param(..., "False"))` for a boolean — that is the 19.0 string
convention. Call `get_bool`. A leftover `get_param` is an `AttributeError` at runtime, not a
silent miss.

### `Registry.clear_cache` is gone

`Registry.clear_cache` / `clear_all_caches` exist at 19.0 (`odoo/orm/registry.py:998`) and are
**absent** at saas-19.4. The successor is `Environment.transaction.invalidate_ormcache`
(`odoo/orm/environments.py:833`). The cache key names (`stable`, `templates`, `default`,
`routing`, `assets`, `groups`) are the same; a bare `clear_cache()` is `invalidate_ormcache()`
(default key).

Observed on the saas-19.4 image during `20_c` B1 tests: `AttributeError: 'Registry' object has
no attribute 'clear_cache'` when the 19.0 defect-6 fix was copied verbatim. Core itself now
does this (e.g. `analytic_plan.py:274`, `ir_model.py:1107`). Checker kind is `python-api`.
In `tools@19.0` this is also `cloud_base`, `knowsystem*`, `joint_calendar`, `documentation_builder`,
`odoo_menu_management`, `odoo_email_from`, `odoo_password_manager`.

```python
# BEFORE
self.env.registry.clear_cache("stable")
self.env.registry.clear_cache()
# AFTER
self.env.transaction.invalidate_ormcache("stable")
self.env.transaction.invalidate_ormcache()
```

### `tools.ormcache` is deprecated — import from `odoo.api`

`@tools.ormcache(...)` still exists at saas-19.4 but emits
`DeprecationWarning: Since 20.0 import ormcache from odoo.api` (observed
`20_5` Gx.6 `joint_calendar` `ir_ui_menu.py`). The warning gate treats that as
ours. Successor: `@api.ormcache(...)`. Checker `python-api` flags `tools.ormcache`.

```python
# BEFORE
from odoo import api, models, tools
@tools.ormcache("self.env.uid")
# AFTER
from odoo import api, models
@api.ormcache("self.env.uid")
```

### `mail` Store API redesigned around `Store.FieldList`

`Store.add()` changed signature and `Store.get_result()` is gone:

```python
# BEFORE (19.0): fields optional, result fetched separately
def add(self, records, fields=None, extra_fields=None, as_thread=False, **kwargs)
return Store().add(messages).get_result()

# AFTER (20.0): fields mandatory and positional, no get_result
def add(self, records, fields, *, as_thread=False, fields_params=None, ignore_empty=False)
store = Store().add(messages, "_store_message_fields")
# jsonrpc serializes Store via as_dict(); do not call get_result
```

Attachment box (`cloud_base` `/cloud_base/attachments/data`): same hole. Successor matches
core `mail` upload (`attachment.py:85`):

```python
store = Store()
if attachments:
    store.add(attachments, lambda res: (
        res.from_method("_store_attachment_fields"),
        res.from_method("_store_ownership_fields"),
    ))
return {"data": store, "attachments": attachments.ids}
```

Checker `python-api` flags `.get_result(`. The model-side hooks moved with it. The old hooks
appended to a dict or returned a list of names; the new ones receive a `Store.FieldList` and
call `res.attr(...)` / `res.extend([...])`. This is a rewrite, not a rename — budget real work
for any module that formats mail data.

### `stock.move.product_uom` renamed to `uom_id`

```python
# BEFORE: stock_move.product_uom
# AFTER:  stock_move.uom_id
```

Dangerous because these names are often **strings** in group-by keys, domains and selection values,
where nothing raises. Grep for the literal `"product_uom"`, not just attribute access. Note
`sale.order.line` and `product.supplierinfo` already use `product_uom_id` on 19.0 — do not conflate.

### Mail tracking values are gone

`mail.tracking.value` and `mail.message.tracking_value_ids` were removed in saas-19.3
(`addons/mail/models/mail_tracking_value.py` present at saas-19.2, absent at saas-19.3); the tracking
message is generated on the fly by the new `mail.track.mixin` plus the `_track_*` family on
`mail.thread`.

Anything that **reads** `message.tracking_value_ids` therefore raises on 20.0. In this hub that is
`odoo-apps-addons/ai_mcp_server` — `services/tool_service.py:1256` and
`services/catalog_service.py:245` both iterate `msg.sudo().tracking_value_ids` to format chatter
payloads, and `tests/test_mcp_models.py` creates `mail.tracking.value` rows. That module is outside
the `tools` group list, so no group gate covers it; schedule it explicitly.

`mail.tracking.duration.mixin` **survives in name only** — do not read that as "stage-duration
features still work". The 19.0 implementation was replaced (94 lines deleted, 29 added) and
`duration_tracking` changed in two ways that break readers silently:

- it is now **stored** (`store=True`), so it is no longer recomputed on read;
- the JSON schema changed from `{"<stage_id>": seconds}` to
  `{"d": "<utc datetime entered>", "s": <current stage id>, "<stage_id>": <minutes>}` —
  different unit (minutes, not seconds), plus two reserved non-numeric keys.

Code that sums the dict values, or treats every key as a stage id, produces wrong numbers instead of
an error. No `tools` / `system` module reads `duration_tracking` today, so this is a gate for future
work rather than a current port item.

## Security: `ir.rule` + `ir.model.access` merged into `ir.access`

**This one is loud, and it stops the install of any module that ships security data.**
`odoo/addons/base/models/ir_rule.py` and the `ir.model.access` model exist at `19.0` **and at
`saas-19.1`, `19.2`, `19.3`** — and are both gone at `saas-19.4`. The successor is a single model,
`ir.access` (`odoo/addons/base/models/ir_access.py`), holding what used to be two concepts.

Symptom: `KeyError: 'ir.rule'` from `convert.py` `_tag_record`, wrapped in a `ParseError` naming
your `security.xml`, during `-i`. A `security/ir.model.access.csv` fails the same way — the model
name comes from the **file stem**, so the file must be renamed, not just edited.

### XML

```xml
<!-- BEFORE (19.0) -->
<record id="sticky_note_rule" model="ir.rule">
    <field name="name">Sticky Note Rule</field>
    <field name="model_id" ref="model_sticky_note"/>
    <field name="domain_force">['|', ('share', '=', True), ('create_uid', '=', user.id)]</field>
</record>

<!-- AFTER (20.0) -->
<record id="sticky_note_rule" model="ir.access">
    <field name="name">Sticky Note Rule</field>
    <field name="model_id" ref="model_sticky_note"/>
    <field name="operation">crud</field>
    <field name="domain">['|', ('share', '=', True), ('create_uid', '=', user.id)]</field>
</record>
```

- `domain_force` → **`domain`**.
- `perm_read` / `perm_write` / `perm_create` / `perm_unlink` → one **`operation`** string, a subset
  of `crud` in that order (`r`, `cu`, `ru`, `crud`, …). The `for_read` / `for_write` / `for_create` /
  `for_unlink` booleans still exist as computed+inverse helpers, but data files set `operation`.
- `groups` (many2many) → **`group_id`** (many2one). Several groups is now **several records**.
- `model_id` still takes the `model_<name>` xmlid via `ref` (core does:
  `ref="project.model_project_task"`).

**The empty-group semantics carried over, but the vocabulary changed.** `_compute_kind`
(`ir_access.py:129`) reads: no `group_id` → **restriction**, `group_id` → **permission**. A
restriction is ANDed for everyone, which is exactly what an `ir.rule` with no `groups` meant. So a
global rule ports across unchanged — leave `group_id` empty and do not "fix" it by inventing a group.

### CSV

Rename `security/ir.model.access.csv` → **`security/ir.access.csv`**, in the file system *and* in
the manifest `data` list. The header changed too:

```csv
# BEFORE  security/ir.model.access.csv
id,name,model_id:id,group_id:id,perm_read,perm_write,perm_create,perm_unlink
access_sticky_note,access_sticky_note,model_sticky_note,base.group_user,1,1,1,1

# AFTER   security/ir.access.csv
id,name,model_id,group_id/id,operation,domain
access_sticky_note,access_sticky_note,sticky.note,base.group_user,crud,
```

Three traps in that header, all silent if you copy the old one:

- **`model_id` is no longer an xmlid column.** It has no `:id` / `/id` suffix and carries the
  **technical model name** (`sticky.note`). It resolves through `ir.model._rec_names_search =
  ['name', 'model']`. All 236 core `ir.access.csv` files use this exact header.
- **`group_id/id`** uses the modern `/id` separator, not `:id`.
- **`domain`** is a real column now: a record rule and an ACL row are the same thing, so the two
  files may be merged.

Because the CSV can now carry a domain, ACL rows and record rules are interchangeable in form.
Do not restructure a module's security while porting — keep the same rows, translated one to
one, **except** an empty ACL domain is not the old ACL behavior (see below).

### Empty ACL permission ORs away the record rule

On 19.0, `ir.model.access` had no record filter. An empty ACL only meant "this group may use
the model"; `ir.rule` still applied.

On saas-19.4 both are `ir.access`. `_get_domain_for` is
`Domain.OR(permissions) & Domain.AND(restrictions)` (`ir_access.py:355`). An empty `domain` on
a **permission** (`group_id` set) becomes `Domain.TRUE` (`:308`). TRUE OR anything is TRUE, so
every grouped domain on that model is ignored.

That is silent. Install succeeds. The user sees every record.

Successor:

1. A 19.0 **global** rule (no `groups`) stays a **restriction** (no `group_id`). Restrictions
   AND. An empty ACL next to that is safe — `20_2` `sticky_notes` / `smart_warnings`,
   `20_5` `joint_calendar`.
2. A 19.0 **grouped** rule next to an empty ACL: **put that domain on the ACL CSV row**, or
   drop the empty ACL if a same-group domain permission already covers those operations.
   Do not leave the empty permission.
3. A 19.0 `[(1, '=', 1)]` rule (intentional all-records) must stay an **explicit**
   `[(1, '=', 1)]` on the 20.0 permission. Empty is indistinguishable from a forgotten ACL;
   the checker flags only empty, not explicit TRUE.
4. Do not invent `group_id` on a rule that was global.

Observed `20_5` Gx.8: empty `access_kpi_item` for `group_kpi_user` ORed away
`kpi_item_multi_company_rule` (`access_user_ids`). Demo saw every KPI. Same shape:
`total_notify` empty `access_total_notify` next to `total_notify_user` (`user_id`).
`20_14` `access_clouds_share` is empty next to the partner-domain Internal User row — 19.0
already had a TRUE File Manager rule, so write `[(1, '=', 1)]` there (hygiene, not a
product regression). `20_2` / `20_c` have no empty-permission + grouped-domain pair.

Checker kind `access-or`.

### Grouped `ir.rule` is not an ACL grant

On 19.0, `ir.rule` never granted model access. A grouped rule on
`base.group_user` only filtered records for people who already had
`ir.model.access`. The ACL row stayed on the product group
(`group_kpi_user` read-only, `group_kpi_admin` CRUD).

On saas-19.4 a grouped `ir.access` **is** the ACL. Porting that
`base.group_user` rule as `operation=crud` gives every Internal User
create/write/unlink, and `Domain.OR` unions it with the product-group
row so KPI User also becomes writable. Observed `20_5` Gx.9 review:
`kpi_item_multi_company_rule` / `kpi_category_multi_company_rule` /
`kpi_tag_multi_company_rule`.

Successor:

1. Put the 19.0 rule domain on the **product-group** permission
   (`group_kpi_user`), not on `base.group_user`.
2. Copy the 19.0 **ACL operations** (`r` vs `crud`), not a default
   `crud`. 19.0 `ir.rule` `perm_*` flags (scorecard line read vs edit)
   stay as separate rows with `r` / `cud`.
3. Keep 19.0 global rules as restrictions (no `group_id`).
4. Do not leave a `base.group_user` write permission on a model that
   also has a product-group ACL — that is the grant.

Checker kind `access-grant`.

## XML / views

### Calendar `date_delay` is gone (RNG + arch parser)

19.0 `calendar` accepted `date_delay` (`odoo/addons/base/rng/calendar_view.rng`,
`web/.../calendar_arch_parser.js` `FIELD_ATTRIBUTE_NAMES`). saas-19.4 dropped it
from both. The model field may stay; the **view attribute** kills `-i`:
`Invalid attribute date_delay for element calendar`. Observed `20_5` Gx.6
`joint_calendar` `joint_event_view_calendar`. Successor: drop the attribute.
`date_start` + `date_stop` remain. Checker kind `calendar-attr`.

### `t-esc` / `t-raw` in `ir.ui.view` arch are forbidden

`_validate_qweb_directive` (`ir_ui_view.py:2371`) allows `t-out` on qweb-based
views (kanban, card, and enterprise `gantt`) and rejects `t-esc`. Observed
`20_5` Gx.6 `joint_calendar_gantt` `joint_event_view_gantt`
(`Forbidden owl directive used in arch (t-esc)`). Successor: `t-out`. OWL
`static/src` templates may keep `t-esc`. Checker kind `qweb-tesc` (skips
`/static/`).

### Named inherit anchors: check the node, not just the view

A core view surviving under the same xmlid does **not** mean the node you hook onto survived.
`crm`'s `<group name="lead_priority">` (19.0 `crm_lead_views.xml:248`, the lead-only sibling of the
opportunity `tag_ids` group) is gone at `saas-19.4`: the lead and opportunity sidebars were merged
into one group with a single `tag_ids`. `complementary_lead_data` inherited that group by name, so
`crm.crm_lead_view_form` still resolved and the module still failed to load.

For every inherit of a core view, verify each anchor exists in the target arch:

- an `xpath` `expr` predicate — `//group[@name='lead_priority']` or `//div[@id='portal_service_category']`
- a tag carrying `position=` — `<group name="lead_priority" position="inside">` or
  `<div id="portal_service_category" position="inside">`

The checker's `view-anchor` kind does this mechanically (both `name` and `id`), and is a
**signal in both directions**: it looks the token up across all target XML, so an anchor that
moved to another model's view is a miss, and one built in Python rather than XML would be a
false positive. Read the target arch before deleting an xpath.

When the anchor is genuinely gone, prefer dropping the redundant hook over inventing a new one —
here the surviving `<field name="tag_ids" position="before">` already placed the widget, so the
second block was deleted rather than retargeted.

### Portal home cards: `portal.entry`, not QWeb into `portal_service_category`

19.0 `portal.portal_my_home` has `<div id="portal_service_category"/>`. Modules dumped a
`portal.portal_docs_entry` call into that node (`cloud_base`, `knowsystem_website`,
`odoo_password_manager`, `documentation_builder`, `business_appointment_website`).

saas-19.4 dropped the node. The home page iterates `portal.entry` records
(`sale/data/portal_entry_data.xml`). `_prepare_home_portal_values` still feeds
`placeholder_count` via `/my/counters`.

```xml
<!-- BEFORE — dies: Element '<div id="portal_service_category">' cannot be located -->
<template id="portal_my_home" inherit_id="portal.portal_my_home">
    <div id="portal_service_category" position="inside">
        <t t-call="portal.portal_docs_entry">…</t>
    </div>
</template>

<!-- AFTER -->
<record id="portal_shares" model="portal.entry">
    <field name="name">Shares</field>
    <field name="description">Check and download shared attachments</field>
    <field name="url">/clouds/shares</field>
    <field name="image" type="bytes" file="cloud_base/static/src/img/portal.svg"/>
    <field name="placeholder_count">shares_count</field>
    <field name="category">service_category</field>
    <field name="sequence" eval="110"/>
</record>
```

Keep the counter method. Do not xpath a surviving `o_portal_docs` wrapper and re-call
`portal_docs_entry` — that template now requires a `portal.entry` record (`entry.url`,
`entry.should_show_portal_card()`). Observed `20_14` Gx.6 `cloud_base` install after the
`Stream` import was already fixed. Checker `view-anchor` now sees the `id=` form.

### `t-call` inner `t-set` does not reach the callee

19.0 `t-call` copied `values` and applied inner `t-set` to that copy, so

```xml
<t t-call="portal.message_thread">
    <t t-set="object" t-value="share_id"/>
</t>
```

set `object` on `portal.message_thread`. saas-19.4 `_compile_directive_call`
(`ir_qweb.py:2682`) compiles the body as the `t-out="0"` slot only;
`t_call_values` starts as `{0: qwebContent}`. Inner `t-set` never reaches the
callee → `KeyError: 'object'` and a 500. Core sale/account set `object` on the
page via `_get_page_view_values` and use an empty `<t t-call="portal.message_thread"/>`.
Successor: write `object` / `token` / `breadcrumbs_searchbar` on the controller
values, **or** put them on the `t-call` tag (`breadcrumbs_searchbar="True"`),
or `t-set` **before** the `t-call` as a sibling. Inner `t-set` of
`breadcrumbs_searchbar` is why portal shares rendered **two** `/ Shares / …`
rows: `portal.portal_layout` never saw the flag (so it printed crumbs at its
first `t-call`) and the slot later set the flag for `portal.portal_searchbar`
(second row). Core sale writes:

```xml
<t t-call="portal.portal_layout" breadcrumbs_searchbar="True">
    <t t-call="portal.portal_searchbar" breadcrumbs_searchbar="True" title.translate="Quotations"/>
```

Checker kind `qweb-tcall` flags a first-child `t-set` of `breadcrumbs_searchbar`
/ `object` / `token` / `title`. Observed `20_14` Gx.8 token share.

### `product.product_variant_easy_edit_view` removed

Present through `saas-19.3`, absent in `saas-19.4`. Any `inherit_id` pointing at it fails to load.
Surviving product forms include `product_normal_form_view` and
`product_product_view_form_normalized`; pick the target by reading the 20.0 layout, and fold the
xpath into it. Watch for modules that also name a **local** record
`product_variant_easy_edit_view` — the two are easy to confuse.

Check every core `inherit_id` for existence on the target, in `odoo` **and** `enterprise`.

## OWL / JS

saas-19.4 ships **OWL 3**. `@odoo/owl` is still the loader alias (`odoo.define("@odoo/owl", …)
{ return owl }`), so a **path** check reports clean. The public exports changed. The
compat layer (`web/static/src/owl2/owl3_compatibility_layer.js`) restores a subset of OWL 2
hooks and **does not** restore `useState` or `reactive`. Phase 1 skipped `@odoo/owl` as a
loader-alias false positive; the `20_2` review DB then died with
`TypeError: useState is not a function` on every form. The checker kind is `js-symbol`.

### 1. `useState` → `proxy` (FIRST — loud, every form if you patch `FormRenderer`)

`useState` is **deleted**. It is in the 19.0 `owl.js` export list (37 names) and absent from
saas-19.4 `owl.d.ts` and from the compat layer. Core `FormRenderer.setup` did exactly this
substitution (`addons/web/static/src/views/form/form_renderer.js`):

```js
// BEFORE (19.0)
import { useState } from "@odoo/owl";
this.state = useState({});
// AFTER (saas-19.4)
import { proxy } from "@odoo/owl";
this.state = proxy({});
```

Same for `const { useState } = owl` (portal / public code). `Object.assign(this.state, …)` on
the object `proxy` returns is what core and our form patches already do.

In `tools` this is **66 files** (23 named `@odoo/owl` imports plus `owl` destructures). A
global `FormRenderer` patch that still calls `useState` kills **every** backend form, not just
that module's view (`smart_warnings` / `sticky_notes` on `20_2`).

`reactive` is deleted the same way. `@web/core/utils/reactive.js` now imports `proxy` and only
exports `Reactive` (deprecated). The 19.0 `effect(cb, deps)` helper in that file is **gone**.
OWL 3's own `effect(fn)` (no deps array) is not a drop-in.

### 2. Compat layer — what it restores, and what it does not

Restored on `owl.*` (also re-exported from `@web/owl2/utils`): `Component` wrapper, `mount`,
`App`, `useRef`, `useEnv`, `useSubEnv`, `useChildSubEnv`, `useComponent`,
`useExternalListener`, `useLayoutEffect` (OWL 2 `useEffect` semantics), `onWillRender`,
`onRendered`.

**Not** restored: `useState`, `reactive`, `loadFile`, `validate`.

Still native on OWL 3 (safe to keep importing): `Component`, `onWillStart`,
`onWillUpdateProps`, `onMounted`, `onPatched`, `onWillUnmount`, `onWillDestroy`, `markup`,
`mount`, `xml`, `status`, `toRaw`, `useEffect` (see signature below).

### 3. `useEffect(fn, deps)` is not OWL 3 `useEffect`

OWL 3 `useEffect` exists but is `useEffect(fn)` — signal-based, **no dependency array**
(`owl.d.ts`). Extra arguments are ignored. Our three call sites still pass
`() => [deps]` (`knowsystem` iframe ×2, `cloud_base_documents` kanban record). That is a
silent miss: the effect will not re-run when those deps change.

Odoo core moved 183 → 43 `useEffect` and 0 → 161 `useLayoutEffect`. The compat
`useLayoutEffect(effect, computeDependencies)` is the OWL 2-shaped replacement:

```js
// BEFORE
import { useEffect } from "@odoo/owl";
useEffect(() => { …; return cleanup; }, () => [this.state.flag]);
// AFTER
import { useLayoutEffect } from "@web/owl2/utils";
// or: import { useLayoutEffect } from "@odoo/owl";  (compat assigns it)
useLayoutEffect(() => { …; return cleanup; }, () => [this.state.flag]);
```

### 4. `t-ref` in OWL templates and in `t-inherit` XPath

The compat header says replace `t-ref` → `t-custom-ref`, `t-portal` → `t-custom-portal`,
`t-model` → `t-custom-model`. Core `web` did: 322 → 41 `t-ref=`, 0 → 294 `t-custom-ref`.
Leftover `t-ref` in core is the OWL 3 form `t-ref="this.rootRef"` (a signal), not the OWL 2
named `t-ref="root"`.

**Inherit XPath that selects `@t-ref` is dead.** `web.KanbanRecord` is no longer a standalone
`<article t-ref="root">`. It `t-inherit`s `web.CardRenderer` and sets
`<attribute name="t-custom-ref">root</attribute>`. `mail.Message` `shadowBody` is now
`t-ref="this.shadowBody"`. Four jstree kanbans and `message_edit` still xpath
`//article[@t-ref='root']` / `//div[@t-ref='shadowBody']` — the inherit will not match.
Checker kind: `owl-xpath`.

**`o-kanban-button-new` left `web.KanbanView`.** At 19.0 the New button sits in
`control-panel-create-button` on `web.KanbanView` (`kanban_controller.xml:8`). At
saas-19.4 that slot is gone; the button lives on `web.KanbanView.Buttons` (`:101`)
and the view `t-call`s `this.props.buttonTemplate`. An inherit of `web.KanbanView`
that xpaths `//button[hasclass('o-kanban-button-new')]` dies at template compile
(`Element '…' cannot be located in element tree`) — File Manager, KnowSystem,
KPI Scorecard. Successor: inherit `web.KanbanView.Buttons` (primary), same xpath;
core does this (`product` catalog, `hr_expense`, `project`). Checker `owl-xpath`
now flags `hasclass()` that is absent from the inherited `t-name` at the target.

**`t-if` / `t-elif` inherit matches the exact attribute string.** OWL `applyInheritance`
looks up the opening tag, not the method name. saas-19.4 prefixed `mail.AttachmentList`
`canDownload(attachment)` with `this.` (19.0 `:91`, saas-19.4 the same file). A leftover
`<button t-elif="canDownload(attachment)" position="after">` dies at compile
(`Element '…' cannot be located`) and **kills every chatter attachment box**, not just
File Manager. Successor: `t-elif="this.canDownload(attachment)"`. Drop a dead
`<img t-else="">` hook — that node is a `div` on both refs. Checker `owl-xpath` now
indexes `(tag, t-if|t-elif|t-else, value)` per inherited `t-name`. A hasclass-only
pass reported this clean.

**`class="…" position=` is the same exact-string match.** saas `web.CalendarSidePanel`
still has a node whose class *token* is `o_calendar_sidebar`, but the attribute is
`class="o_calendar_sidebar flex-grow-0 …"` and that node is the **collapsed rail**.
The expanded filters live on `o_calendar_sidepanel_content`. A leftover
`<div class="o_calendar_sidebar" position="inside">` dies at compile
(`Element '…' cannot be located`) and **blocks the Joint Calendar menu**.
`hasclass('o_calendar_sidebar')` would compile and attach Refresh to the rail —
wrong UX. Successor: `//div[hasclass('o_calendar_sidepanel_content')]`.
Checker `owl-xpath` now indexes exact `class="…"` strings on `position=` tags
and `@class=` XPath. Observed `20_5` Gx.8 first-click.

**Bare `state` / `props` / `model` / `panelState` / `env` in an OWL template is undefined.**
OWL 3 does not put those names in the compile scope. Core saas templates write
`this.state` / `this.props` / `this.model` / `this.env` (19.0 `kanban_renderer.xml` still has
bare `state.selectionAvailable`; saas-19.4 has `this.state.selectionAvailable`).
File Manager then died with `Cannot read properties of undefined (reading
'reloaded')` at `CloudManagersKanbanRenderer`, then
`ctx.getCloudManagerNavigationProps is not a function`. Prefix `this.` on every
inherit expression, including `t-props="this.getX()"`. Checker kind: `owl-this`.
Same `this.` prefix on standalone OWL templates (`this.panelState`, getters
`this.panelClass` / `this.panelStyle`, `t-props="this.getX()"`,
`update.bind="this.handleChange"`, `t-on-click="this.clear"`) **and** on
`xml\`...\`` literals in JS. Portal `jsTreePortal` used `t-if="state.treeData"`
— the left folder/tag column rendered empty (no TypeError in the public page).
A `state|props|model`-only regex then missed KPI `panelState.collapsed` and
Reminder Designer `update.bind="handleChange"` (`undefined.bind`). Observed
`20_5` Gx.8 first-click. `20_14` `cloud_navigation.xml` / `rule_parent.xml`
already prefixed; `20_2` has no FieldFilter.

**jstree + `owl.proxy` / `state` plugin:** do not keep the tree payload on a
reactive `proxy`. jstree mutates `core.data` in place; a proxy write re-renders
OWL, replaces the host node, and the `state` plugin's `get_state` then does
`this.element.scrollLeft()` with `this.element === null`
(`TypeError: Cannot read properties of null (reading 'scrollLeft')`).
The stack often names `jstree.plugins.contextmenu.get_state` — that is the
last plugin on the prototype chain, not a contextmenu bug. The state plugin
binds `changed`/`ready` and schedules `save_state` on a **100ms timer**;
`destroy()` nulls `this.element` first, then the timer fires.

A parent OWL `proxy` write is enough to remount the tree. In File Manager
chatter that write was `this.state.cloudsFolderId = nextId` inside
`onRefreshAttachmentBoxWithFolder` (called from `state_ready`). Keep the
folder id on a **plain instance field** (`this.cloudsFolderId`); only
`folderExist` belongs on the proxy. Bind `onUpdateSearch` once in `setup`.

Successor: store the payload on `this.treeData`, pass a **copy** into
`core.data`, bind the host with `t-custom-ref` + `window.jQuery(ref.el)`,
**do not remount on `onPatched`**, **patch `$.jstree.core.prototype.get_state`**
to no-op when `!this.element`, and **stub `save_state`/`get_state` on the
instance before every `jstree("destroy")`**. Do **not** skip destroy on a
disconnected host — that leaves the 100ms timer armed. A `t-if` that needs
reactivity should key a boolean (`ready`), not the tree array. Observed
`20_14` Gx.8 chatter attachment box after the Store / canDownload fixes
already landed — off-proxy alone was not enough; skip-destroy was not
enough either.

**Do NOT drop the `state` plugin as a fix for that crash.** It was tried
here and is wrong: `state_ready.jstree` (emitted only by the `state`
plugin) is what the `check_node`/`changed`/`open_node`/`search` bindings
*and the very first `_onUpdateDomain()` call* wait on in this module's
`CloudJsTreeContainer._renderJsTree`. Dropping the plugin for the chatter
tree (`!fileUi`) didn't just disable state restore — it silently disabled
**all** folder-selection handling, so the attachment box stopped filtering
by folder and stopped tracking `cloudsFolderId` (uploads fell back to the
record). A missing feature discovered later ("selection not restored",
"folder does not filter attachments") is the signal that a plugin got
dropped instead of the actual crash cause being fixed.

**`portal.message_thread` heading:** saas starts with a bare
`<h3>Communication History</h3>`. A wrapper `class="row"` (19.0) applies
a negative gutter; saas `#wrapwrap` / nested `.container` clips the first
letter. Putting the `t-call` in a **sibling** of `.row` with only `mt32`
is still clipped. Successor: drop the extra inner `.container` (portal
layout already wraps the slot), and put `#share_communication` in
`class="col-12"` **inside** the existing row so the heading sits in the
gutter padding. 19.0 used the same `.row` and did not clip.

Our own templates that still write `t-ref="start-date"` should become `t-custom-ref="start-date"`
to match core datetime fields and the compat `useRef("start-date")`. Same rename for
`t-model` → `t-custom-model` (`email_suite` `scheduled_date_dialog_patch.xml`) and
`t-portal` → `t-custom-portal`. Checker kind: `owl-tref`.
`useRef` itself is restored by the compat layer.

### 5. `this.render` on patched view renderers

`FormRenderer` no longer passes `this.render` to `useDebounced`. It imports `render` from
`@web/owl2/utils` and calls `render(this)`. No `tools` file currently calls `this.render(`.
If a later patch does, rewrite it the same way.

### 6. Same-path JS symbol moves (the file survived; the export did not)

The `js-import` check only asks whether `@mod/path` resolves to a file. These exports left a
surviving file. Checker kind: `js-symbol`.

| 19.0 import | Symbol | saas-19.4 successor |
|---|---|---|
| `@odoo/owl` | `useState` / `reactive` | `proxy` from `@odoo/owl` |
| `@web/core/utils/concurrency` | `Deferred` | `Promise.withResolvers()` (polyfill in `web/static/src/polyfills/promise.js`). 158 core imports → 0. `KeepLast` / `Mutex` / `Race` stay |
| `@web/core/assets` | `LazyComponent` | `@web/core/lazy_component` |
| `@web/core/emoji_picker/emoji_picker` | `loadEmoji` | `useLoadEmoji` from `@web/core/emoji_picker/emoji_loader` |
| `@web/core/utils/reactive` | `effect` | rewrite; OWL 3 `effect(fn)` is not the two-arg helper |
| `@html_builder/core/utils` | `BaseOptionComponent` | `@html_builder/core/base_option_component` |

`static props = { x: { type: Object } }` is still used in 160 core `web` files on saas-19.4
(compat `Component` wrapper). Do not rewrite props schemas in the same breath as `useState`
unless a runtime error names them.

### Moved modules (import path only)

| 19.0 import | 20.0 import | Symbol |
|---|---|---|
| `@mail/core/common/record` | `@mail/model/export` (re-exports from `./misc`) | `fields` |
| `@web/core/orm_service` | `@web/core/orm_plugin` | `x2ManyCommands` |

### Removed with no drop-in

- **`@web/core/ensure_jquery`** — gone. It used to load `web._assets_jquery` plus the Bootstrap
  jQuery plugins. Rewrite the call site without jQuery; do not reintroduce a loader.
- **`/web/static/lib/jquery/jquery.js`** — gone with the same deletion (`addons/web/static/lib/jquery`
  is present at 19.0, absent at saas-19.4). `loadJS` of that URL is an `AssetsLoadingError`.
  File Manager / jstree still needs `$` and already vendors `jstree.min.js`. Successor: copy the
  19.0 `jquery.js` (MIT, currently 3.6.3) next to it as `/<module>/static/lib/jquery/jquery.js`
  and retarget every `loadJS`. Do not rewrite the tree in the same job. Checker `js-import`
  flags the old URL. Observed `20_14` Gx.8 after the `o-kanban-button-new` xpath landed.
- **`@html_editor/others/dynamic_placeholder_plugin`** (`DynamicPlaceholderPlugin`) — gone.
- **`@html_builder/utils/option_sequence`** (`before`, `after`, `VERTICAL_ALIGNMENT`, `WIDTH`) —
  gone. Sequencing is now **numeric**: `withSequence(N, object)` from `@html_editor/utils/resource`.
  `withSequence(after(VERTICAL_ALIGNMENT), …)` must be rewritten, not remapped.

### Renamed / restructured (architecture port, not a substitution)

| 19.0 | 20.0 | Note |
|---|---|---|
| `DYNAMIC_PLACEHOLDER_PLUGINS` from `@html_editor/backend/plugin_sets` | `DYNAMIC_FIELD_PLUGINS` from `@html_editor/backend/dynamic_field/dynamic_field_plugin`, consumed via the `dynamicField` prop | not `@web/views/fields/dynamic_placeholder_*`, which serves plain char/text fields |
| `@mail/chatter/web_portal/chatter` | `@mail/chatter/web_portal_project/chatter` | the component was rewritten and backend behavior moved to `chatter/web/chatter_patch.js`; retargeting the import is necessary but not sufficient |
| `@website/js/content/website_root` + legacy `.include()` | `website/static/src/interactions/` | e.g. a `_onLangChangeClick` include becomes the `LangChange` Interaction (`selector = ".js_change_lang"`) |
| `@website_sale/interactions/website_sale` (`WebsiteSale`) | split into `add_to_cart.js`, `add_to_comparison.js`, `add_to_wishlist.js`, `product_page.js` | pick the Interaction per call site; `ProductPage` (`.o_wsale_product_page`) covers product-page behavior |

### Signature changes

`MessageModel.edit` narrowed to
`async edit(body, attachments = [], { mentionedPartners = [], mentionedRoles = [] } = {})`.
Forwarding with `super.edit(...arguments)` survives, but a dropped option is silently ignored.

### Patching rules learned here

- `patch()` on a **prototype** cannot override an own instance property. Upstream `fields.Attr(...)`
  members (e.g. `MessageModel.isEmpty`) are instance fields, so a `get x()` in a prototype patch is
  shadowed and **never runs** — including on 19.0. **Patch the field's compute**, which upstream
  routes through a normal prototype method:

  ```js
  // BEFORE — shadowed by the own instance property, dead on every serie
  get isEmpty() { return this.deleted ? true : super.isEmpty; },
  // AFTER — computeIsEmpty() is a prototype method, so the patch runs
  computeIsEmpty() { return this.deleted ? true : super.computeIsEmpty(); },
  ```

  `isEmpty = fields.Attr(false, {compute() { return this.computeIsEmpty(); }})` and
  `computeIsEmpty()` are both present at 19.0 (`message_model.js:338`, `:350`) and saas-19.4
  (`:392`, `:404`), so the same fix holds on both. The compute's body did change — 19.0 reads
  `this.trackingValues`, which is gone at saas-19.4 with the tracking values — so re-read it rather
  than assuming what `super()` returns. Computes are **lazy** by default
  (`mail/static/src/model/misc.js:69`), so a patch may safely read fields its own `setup()` declares
  after `super.setup()`.
- Members reached only through a shadowed patch are dead too. In `message_edit` the `editable`
  getter read `this.isEmpty` and therefore silently got upstream's value, not the module's.
- A patch that **fully replaces** a core method without `super()` keeps working syntactically while
  diverging from new core behavior. Re-read the upstream method on every port.
- Resolve the patched target through its import, then walk the parent chain. A member may live on an
  ancestor or mixin (`FileModelMixin`, `Record`), not the class you imported.

## Checker

`ai_rules/tools/check_migrate_v20.py` implements the mechanical half of this rule. Run it before and
after each module port:

```bash
python3 ai_rules/tools/check_migrate_v20.py \
    --repo /home/feelwhy/Odoo/tools \
    --odoo /home/feelwhy/Odoo/odoo --odoo-ref origin/saas-19.4 --odoo-base-ref origin/19.0 \
    --enterprise /home/feelwhy/Odoo/enterprise --enterprise-ref origin/saas-19.4 \
    [--modules mod_a,mod_b] [--only js-symbol,owl-xpath,python-api] [--json]
```

About 30s for one module or group, ~3min for 93 modules. Findings:

| Kind | Meaning |
|---|---|
| `dead-hook` | the hook existed at the **base** ref and is gone at the target — a silent break. Also `_check_access`: the name survives but `check_access` is `@typing.final` (`DEAD_DESPITE_EXISTING`) |
| `stale-override` | absent at **both** refs — already dead before this port; a defect on the current serie, not porting work |
| `js-import` | an `@mod/path` import resolving to no file in `odoo` or `enterprise`, or a `loadJS` URL deleted at the target (`/web/static/lib/jquery/jquery.js`) |
| `js-symbol` | a **named** import (or `const { X } = owl`) whose path still resolves but the symbol is not exported at the target — this is how `useState` hid |
| `owl-xpath` | an OWL `t-inherit` XPath that selects `@t-ref` / `@t-esc` on a core template, **or** `hasclass()` of a class that left the inherited `t-name` (`o-kanban-button-new` left `web.KanbanView`), **or** a `position=` tag whose `t-if` / `t-elif` / `t-else` value is not on that `t-name` (`canDownload` vs `this.canDownload`), **or** a `position=` / `@class=` inherit whose exact `class="…"` string is not on that `t-name` (`o_calendar_sidebar` vs the saas collapsed-rail class list) |
| `owl-tref` | an OWL-2 named `t-ref` / `t-model` / `t-portal` in our own `static/src` template; core writes `t-custom-*` |
| `owl-this` | a `t-inherit` / standalone / `xml\`` OWL template still uses a bare OWL-3 scope name (`state.` / `panelState.` / `env.` / `props.` / `model.`), a bare getter (`t-att-class="panelClass"`), a bare method bind (`update.bind="handleChange"`, `t-on-click="clear"`), or a `t-on-*` arrow that calls a method without `this.` (`(event) => _onSearchNavigation(...)`) |
| `qweb-tcall` | first-child `t-set` of `breadcrumbs_searchbar` / `object` / `token` / `title` on a `t-call` — saas-19.4 slot only |
| `owl-hook` | `useEffect(fn, deps)` imported from `@odoo/owl` — OWL 3 `useEffect` ignores the deps array |
| `python-api` | a call to a core method that is gone at the target (`get_param` / `set_param` / `Registry.clear_cache` / `Store.get_result`), a leftover `tools.ormcache` (import from `odoo.api`), or a named import that left `odoo.http` (`Stream` / `content_disposition`) |
| `calendar-attr` | a `<calendar date_delay=...>` — RNG and `FIELD_ATTRIBUTE_NAMES` dropped it at saas-19.4; drop the attribute |
| `qweb-tesc` | `t-esc` / `t-raw` in a non-`static` XML arch — saas forbids those OWL directives; use `t-out` |
| `patch-target` | a `patch()` whose imported target no longer resolves |
| `patch-shadow` | a `patch(X.prototype, …)` member that upstream declares as a **class field** on the patched class or an ancestor — an own instance property shadows it, so it never runs, on any serie |
| `view-xmlid` | an `inherit_id` ref to a core view that no longer exists |
| `view-anchor` | an inherit anchor (`@name=` / `@id=` predicate, or a `position=` tag's `name` / `id`) that exists in no target view — a signal, see the caveat above |
| `security-model` | a data file declaring `ir.rule` / `ir.model.access`, gone at the target; CSV findings mean **rename the file** |
| `access-or` | a grouped `ir.access` with an **empty** domain on a model that also has a grouped row with a real domain and overlapping ops — empty is `Domain.TRUE` and ORs the filter away. Explicit `[(1, '=', 1)]` is not this kind. Restrictions (no `group_id`) AND and are safe |
| `access-grant` | a `base.group_user` permission with write ops (`c`/`u`/`d`) on a model that also has a product-group permission — 19.0 `ir.rule` on Internal User was a filter, not an ACL grant |
| `field-lit` | a literal use of a removed field name |
| `manifest-version` | a serie-prefixed `__manifest__.py` `version` (`19.0.x` / `20.0.x`) while `--odoo-ref` is a `saas-*` branch — `check_version` sets `installable=False` |

Always pass `--odoo-base-ref`. Without it the hook check cannot tell a fresh removal from an
override that was already dead, and reports both the same way.

A clean run is a precondition, not proof of a working port — the runtime gates still apply.

### Why the checker is built the way it is

Each of these cost a false-positive round on the first run, so do not "simplify" them away:

- **Bind the hook to the inherited model, then expand the chain.** A global name search is wrong in
  both directions. It hides a dead hook when the name survives on an unrelated model, and invents
  dead hooks for internal `super()` chains. The MRO also commonly reaches core *through one of our
  own models*, so only direct parents will report live hooks as dead.
- **Framework methods live outside `models/`.** `export_data`, `_check_access`, `copy`, … are on
  `BaseModel` in `odoo/orm/models.py`. A check that only scans addon `models/` directories reports
  all of them as dead.
- **Span `odoo` and `enterprise`.** An `odoo`-only pass reports `@web_gantt/*` and `@documents/*`
  as missing.
- **`git grep -E` is POSIX ERE.** `(?:…)` and `\s` are invalid there and silently match nothing,
  which is indistinguishable from "clean". Use `(…)` and `[[:space:]]`, or filter in Python.
- **Occurrence counts are not work estimates.** Report sites to read, never a total to trust.
- **No core parent in the class is not a reason to skip it.** Every Odoo model still inherits
  `BaseModel`, so a class whose `_inherit` names only one of our own mixins can still hold a dead
  override. Skipping those hid `portal.password.key._generate_order_by` from the chain check
  entirely; only a direct grep found it. Fall back to the implicit `base` ancestor, which resolves
  through the framework-method index.
- **`_name = X` with `_inherit = [X, …]` is the extend-in-place style**, so `X` *is* the core parent.
  Discarding the class's own `_name` unconditionally left `odoo_email_from`'s `mail.compose.message`
  with no core chain — first skipping it silently, then reporting five live core methods as stale.
- **Suppress a repo-internal `super()` chain by definition site, not by module.** Comparing owning
  modules reports the second class of the same model, inside one module, as a stale override.
- **Bind `patch-shadow` to the patched class, through the name that module exports.** A whole-file
  scan is wrong twice over: a field of a class nobody patched proves nothing about the one that was,
  and `import { Message as MessageModel }` means the class to find is `Message` — searching for
  `class MessageModel` finds nothing and reports clean. Resolve local name -> (spec, exported name),
  follow `extends` (local or imported) with no depth cap, and report **nothing** when the class
  cannot be located rather than falling back to the file.
- **Locate members by brace depth, never by indent width.** An assumed four-space indent silently
  matches nothing in a differently formatted file, which again looks exactly like "clean". Blank out
  comment and string contents first, or a brace inside a template literal ends the class body early.
  `static` fields are excluded — they live on the constructor and shadow nothing for instances.
- **Gate a "removed model" check on the target actually lacking it**, and on the successor being
  present. A hardcoded list of renames reports every module as broken the day the check runs against
  real 20.0 with something restored, and cannot be trusted when it stays silent.
- **`@odoo/owl` is a loader alias, not a reason to skip the file.** Path existence is always
  true. Named exports must be checked against `owl.d.ts` plus the compat layer's `owl.X =`
  assignments. Skipping the alias hid `useState` from every module that imports it.
- **A surviving JS file is not a surviving export.** `js-import` asks whether `@mod/path`
  resolves. `Deferred` left `concurrency.js` in place and still broke 158 core call sites.
  `js-symbol` reads the named import against that file's `export` list.
- **A `loadJS` URL is not an `@mod/path`.** `js-import` never saw
  `/web/static/lib/jquery/jquery.js`. saas-19.4 deleted the file; File Manager
  then died with `AssetsLoadingError` after the xpath was already clean.
  `GONE_JS_PATHS` scans the same JS walk.
- **Bare `state.` in a `t-inherit` is not a `t-ref`.** OWL 3 compile scope is
  `this`. Core saas templates already write `this.state`. `owl-this` scans
  inherit bodies, standalone OWL templates (`t-props="getX()"`), **and**
  `xml\`...\`` literals in JS. A file-only `t-name` walk missed portal
  `jsTreePortal` (`t-if="state.treeData"`). A `state|props|model`-only
  regex then missed `panelState.collapsed`, `env.isSmall`,
  `t-att-class="panelClass"`, and `update.bind="handleChange"` (`20_5`
  Gx.8 first-click). The kind now flags `*State.` / `env.` / bare bind /
  bare `t-att-*` / bare `t-on-click` idents.
- **A class token on the parent is not an exact `class="…"` inherit.** OWL
  `applyInheritance` matches the opening-tag attribute string.
  `<div class="o_calendar_sidebar" position="inside">` does not match saas
  `class="o_calendar_sidebar flex-grow-0 …"`. `hasclass()` indexing
  reported clean because the token survived on the collapsed rail.
  `owl-xpath` now indexes exact `class=` strings on `position=` tags.
- **`t-esc` in `ir.ui.view` is not OWL `t-esc`.** saas `_validate_qweb_directive`
  forbids `t-esc`/`t-raw` on qweb-based arches (kanban, card, gantt). OWL
  `static/src` templates may keep `t-esc`. `qweb-tesc` skips `/static/`. A
  view-only pass that ignored gantt popovers hid `joint_calendar_gantt`.
- **Inner `t-set` of a `t-call` is the slot, not the callee.** 19.0 forced
  `str(qwebContent)` when the call had only `t-*` attrs plus child `t-set`
  (`is_deprecated_version`). saas-19.4 deleted that. Checker `qweb-tcall`
  flags a first-child `t-set` of `breadcrumbs_searchbar` / `object` /
  `token` / `title`. Sale writes those as `t-call` attributes.
- **A surviving method name is not a surviving inherit.** OWL `applyInheritance`
  matches the opening-tag attribute string. `t-elif="canDownload(attachment)"`
  does not match saas `t-elif="this.canDownload(attachment)"`. `hasclass()`
  indexing reported that chatter inherit clean. `owl-xpath` now indexes
  `(tag, t-if|t-elif|t-else, value)` on `position=` tags.
- **`view-anchor` collects only nodes an inherit *targets*.** A `name` inside an added block, or an
  `<attribute name="invisible">` under `position="attributes"`, is not an anchor; only an `expr`
  predicate (`@name=` or `@id=`) and a tag carrying `position=` (`name` or `id`) are. Walk
  `<record>` **and** `<template inherit_id>` — a record-only scan missed
  `portal_service_category` on `portal.portal_my_home`. A name-only scan missed the
  `<div id="…" position="inside">` form. Without the target/add distinction every field a
  module adds becomes a finding. It also does not see OWL `t-inherit` XPath on `@t-ref` —
  that is `owl-xpath`.
- **The target node-name set rides on the existing XML walk.** `view_xmlids()` already `git show`s
  every XML file in both trees, so the anchor lookup is a set membership, not one `git grep` per
  anchor (553 `position=` tags in `tools` would otherwise mean 553 greps).
- **An empty grouped `ir.access` domain is not the 19.0 ACL.** saas
  `Domain.OR(permissions)` treats empty as `Domain.TRUE` (`ir_access.py:308`,
  `:355`). A one-to-one ACL+rule port leaves the rule in the file and never
  applies it. `access-or` flags empty (not explicit `[(1, '=', 1)]`) next to a
  sibling grouped real domain. A restriction (no `group_id`) ANDs — do not
  flag that pair. Same-group is not required: `group_kpi_user` empty +
  `base.group_user` domain is the incident (`20_5` KPI). Parse XML
  `<field .../>` separately from `<field>...</field>`: a `[^>]*` that
  swallows the `/` of `/>` ate `model_id` and hid every grouped XML
  domain (`total_notify_user`) on the first run.

## Verify at runtime, not from this rule

These are not settled by source reading. Do not write them into a port as fact:

- Asset bundle existence and restructuring (manifest-key grepping is unreliable; use the runtime
  asset gate).
- Remaining field renames inside surviving models (read the registry after a fresh install).
- Whether 20.0's optional-product rule on `sale.order.line` affects your line creation.
- Attendance access-rights and geolocation RPC changes for kiosk-facing code.
- Which deprecation warnings **your** code actually triggers (test-window log on the pinned image).
- Portal sharing `get_views` on the **running** worker (arch vs `fields_get` for `x_oz_*` / other
  `TASK_PORTAL_*` extras). A new shell process resets `@ormcache(cache='stable')` and is not that
  check. See **Portal sharing field list** above.

## Learned while porting

Append each entry with its date, the module that revealed it, and the source evidence. An entry
without evidence does not belong in this rule.

- *(2026-09-12, phase 1 analysis)* Rule created from the saas-19.4 delta: 23 source-confirmed
  breaks, 5 open hypotheses. Nothing here has been observed on a running 20 instance yet.
- *(2026-09-12, checker first run)* `patch()` on a prototype cannot override an upstream
  `fields.Attr(...)` member, because that is an own instance property. Found via `MessageModel.isEmpty`,
  which has therefore been dead since 19.0 — a port check that binds patched members to their real
  target finds this class of bug on the **current** serie too, not just the new one.
- *(2026-09-12, checker first run)* The `stale-override` class exists because three overrides
  (`_generate_order_by`, `_generate_order_by_inner`, `_inherits_join_calc`) are absent from core at
  **both** refs. Pre-existing dead code is a defect on the current serie; do not bill it to the port.
- *(2026-09-12, 19.0 defect fixes)* Those four sites are now fixed on 19.0 via `_order_field_to_sql`
  (`knowsystem/models/knowsystem_article.py`, `odoo_password_manager/models/password_key.py`,
  `.../portal_password_key.py`), and `message_edit`'s `isEmpty` patch moved to `computeIsEmpty()`.
  Verified in `demo19`: `_order_to_sql("name asc")` emits `LOWER("<table>"."name"->>%s) ASC` on all
  three models, and grouped ordering through those models still resolves (`_read_group` on
  `portal.password.key`, `password.user.log`, `documentation.section.article`,
  `knowsystem.article.revision`). Regression tests: `knowsystem/tests/test_article_ordering.py`,
  `odoo_password_manager/tests/test_password_ordering.py`.
- *(2026-09-12, verification correction)* The first evidence offered for that fix — "mixed-case
  probes sort `AA, mm, zz`" — proved nothing. Those probes share byte order with case-insensitive
  order, and our databases are `en_US.utf8`, where Postgres ignores case while ordering anyway, so
  the assertion passes with the hook dead. The SQL shape was the only load-bearing check. Choose
  probes whose orders actually differ, and assert on `_order_to_sql(...).code`.
- *(2026-09-12, checker hardening)* Both new checks found a defect on their first run:
  `patch-shadow` reproduced `message_edit/static/src/core/common/message_model.js:82`, and the
  `base`-fallback chain exposed the `_name` + `_inherit` self-extension bug above. A checker change
  that reports **nothing** new is the suspicious outcome, not the reassuring one.
- *(2026-09-12, tracking correction)* "`mail_tracking_duration_mixin` survives" was true of the file
  and false of the behavior: `duration_tracking` became stored and changed JSON schema and unit.
  Reading a surviving *name* is not evidence; diff the implementation.
- *(2026-09-12, 4.3 system port)* A serie-prefixed manifest is silently uninstallable on the
  saas-19.4 image: `check_version` compares to `release.major_version` (`saas~19.4`), so both
  `19.0.x` and `20.0.x` become `installable=False` plus a warning. Drop the prefix on the
  stand-in; re-prefix on real 20.0. Same run: `version_info[0]` is `'saas~19'`, not an int —
  `_demo_ticket_serie` was emitting `saas~19.0`.
- *(2026-09-12, `20_2` `Gx.3`)* `crm`'s `group name="lead_priority"` is gone at saas-19.4, so an
  inherit of a **surviving** view (`crm.crm_lead_view_form`) still failed. Static checks that stop at
  the xmlid cannot see this; hence the `view-anchor` kind. Found by reading the target arch after the
  view check came back clean — which is the general lesson: a clean `view-xmlid` says nothing about
  the nodes inside.
- *(2026-09-12, `20_2` `Gx.6`)* First runtime evidence of this program, and it was not a silent
  failure: `KeyError: 'ir.rule'` killed `sticky_notes` and `smart_warnings` on `-i`. `ir.rule` and
  `ir.model.access` survive `saas-19.1`…`19.3` and are **both** replaced by `ir.access` at
  `saas-19.4` — so serie-by-serie existence checks are worth running per saas branch, not just
  against the newest one. Two process notes from the same run: the checker had **no** security kind
  at all (five sites, zero findings, install dead on the first file), and the baked
  `env_dbfilter_header` breaks on the stand-in too (`import odoo.service.db`), which is infrastructure
  noise rather than a module port item — read the failing module name before blaming the group.
- *(2026-09-14, `20_2` Gx.8 review)* Phase 1's JS check was **path existence only** and
  **skipped `@odoo/owl`** as a loader alias. saas-19.4 ships OWL 3; `useState` is deleted and
  the compat layer does not restore it. Opening a Smart Alert form died with
  `TypeError: useState is not a function` at `FormRenderer.setup` because
  `smart_warnings` / `sticky_notes` patch that class. Same-path export removals
  (`Deferred`, `LazyComponent`, `loadEmoji`, `effect`, `BaseOptionComponent`) and
  `@t-ref` inherit XPaths were the same hole. `get_param` / `set_param` were already
  observed at neutralize and were still missing from this rule. The checker now has
  `js-symbol`, `owl-xpath`, `owl-tref`, `owl-hook`, `python-api`. A path-only "OWL clean"
  is not a finding.
- *(2026-09-14, `20_c` Gx.8 review)* Opening a task in project sharing edit as the portal
  collaborator died with `TypeError: "project.task"."x_oz_tsk_1" field is undefined` at
  `Field.parseFieldNode`. The sharing form arch had `x_oz_tsk_1` (Version
  `portal_edit_placement=left_panel_group`); the running worker's portal `get_views` omitted it
  from `models.fields`. Admin and demo HTTP `get_views` included it. A new `odoo shell` on the
  same DB included it for portal too — `_portal_accessible_fields` is `@ormcache(cache='stable')`
  at **both** refs (19.0 `project_task.py:1048`, saas-19.4 `:1077`), so the first call in that
  process freezes the set. `task_custom_fields` fills `TASK_PORTAL_*` from
  `custom.task.field` and writes the arch in `_generate_xml` without invalidating that cache.
  19.0 demo leaves `portal_edit_placement` empty, so the generated sharing groups stay empty and
  the hole is latent. Not a 20-only `fields_get` / `ir.access` miss. Not a checker kind (both
  hooks exist; a `TASK_PORTAL`+`search(` grep would stay red after a correct invalidate-on-write).
  Ledger defect 6. Fix on 19.0 (`a9154df3008`: `registry.clear_cache("stable")`). On saas-19.4
  that call is itself an `AttributeError` — use `env.transaction.invalidate_ormcache("stable")`
  (see **Registry.clear_cache**).
- *(2026-09-14, `20_c` B1 tests)* Copying the 19.0 defect-6 commit onto `20_c` died at
  `Registry.clear_cache`. Successor confirmed at saas-19.4 `environments.py:833`. Checker
  `python-api` now flags `.clear_cache(`.
- *(2026-09-14, `20_14` Gx.6)* `odoo.http` is a package. `__init__.py` does not re-export
  `Stream` / `content_disposition`. `cloud_base` died at import (`cannot import name
  'Stream'`). Successor: `odoo.http.stream`. Checker `python-api` now flags the import form.
- *(2026-09-14, `20_14` Gx.6)* After the import landed, install died on
  `portal.portal_my_home`: `id="portal_service_category"` is gone. Cards are `portal.entry`
  records. A name-only **and** record-only `view-anchor` both missed it (`<template
  inherit_id>` + `<div id="…" position="inside">`). Five 19.0 modules still hook that node.
- *(2026-09-14, `20_14` Gx.7)* `_check_access` still exists at saas-19.4 and the
  checker reported clean. `check_access` is `@typing.final` and uses `_access_domain`.
  `TestCloudsFolderPreparing.test3_security_rights_check` Case 1 (rule-folder
  write) passed after the port. Case 5 stayed red for two independent saas
  facts: (1) `has_access('read')` short-circuits on `transaction.access_read`
  — field `depends` is not enough, `write` must
  `invalidate_access_cache(self._name)`; (2) after that cache was empty,
  `access_user_ids` still read `[]` because saas x2many hides inactive
  `res.users` (`base.user_root`). Compute must use `active_test=False`.
  Checker `DEAD_DESPITE_EXISTING` for (1) only.
- *(2026-09-15, `20_14` Gx.8)* Opening File Manager died with
  `Element '<xpath expr="//button[hasclass('o-kanban-button-new')]">' cannot be
  located`. The class moved from `web.KanbanView` to `web.KanbanView.Buttons`
  (19.0 `kanban_controller.xml:8`, saas-19.4 `:101`). Same hole on 19.0
  `knowsystem` and `kpi_scorecard`. Moved the upload/URL replace onto
  `cloud_base.CloudBaseViewButtons` (`t-inherit-mode="primary"`). Checker
  `owl-xpath` now indexes OWL `t-name` classes in `/static/` (the QWeb
  `view-anchor` walk skips that tree).
- *(2026-09-15, `20_14` Gx.8)* After that xpath landed, File Manager died on
  `AssetsLoadingError: The loading of /web/static/lib/jquery/jquery.js failed`.
  The file is at 19.0 `addons/web/static/lib/jquery/jquery.js` and **absent**
  at saas-19.4 (whole `jquery/` dir gone with `ensure_jquery`). jstree is
  already vendored in `cloud_base` and still needs `$`. Copied 19.0 jquery
  3.6.3 to `cloud_base/static/lib/jquery/jquery.js` and retargeted every
  `loadJS`. Checker `js-import` now flags the old URL. Same leftover in later
  groups that still `loadJS` the core path.
- *(2026-09-15, `20_14` Gx.8)* After jquery loaded, File Manager died on
  `TypeError: Cannot read properties of undefined (reading 'reloaded')` in
  `CloudManagersKanbanRenderer`. OWL 3 inherit templates do not bind bare
  `state` / `props`. Core saas `web.KanbanRenderer` writes `this.state`.
  Prefixed the inherit expressions. Next compile error was
  `ctx.getCloudManagerNavigationProps is not a function` — same `this.`
  on `t-props`. Checker `owl-this` also flags `t-props="getX()"` without
  `this.`.
- *(2026-09-15, `20_14` Gx.8)* Opening a contact chatter attachment box died
  with `Element '<button t-elif="canDownload(attachment)" …>' cannot be
  located`. The button is still on `mail.AttachmentList`; saas writes
  `t-elif="this.canDownload(attachment)"` (OWL 3 `this.`). Inherit matches
  the attribute string, not the method. Slideshow then died on the already-
  known leftover `t-props="getPhotosSlideShowProps()"` / bare `state.playing`.
  Checker `owl-xpath` now indexes OWL `t-if` / `t-elif` / `t-else` on
  `position=` tags. A hasclass-only pass reported the chatter inherit clean.
- *(2026-09-15, `20_14` Gx.8)* After that inherit landed, opening the same
  attachment box died on `Store().add(attachments).get_result()` —
  `AttributeError: 'Store' object has no attribute 'get_result'`. Already in
  this rule; checker `python-api` did not flag `.get_result(`. Token share
  with `show_chatter` stayed 500 on `KeyError: 'object'`: saas `t-call` no
  longer applies inner `t-set` to the callee.
- *(2026-09-15, `20_14` Gx.8)* Same attachment box then died on jstree
  `get_state` → `this.element.scrollLeft()` with `this.element === null`.
  `CloudJsTreeContainer` kept `treeData` on `owl.proxy`; jstree mutated it,
  OWL replaced the host, the `state` plugin saved. Tree payload is now
  `this.treeData`; host is `t-custom-ref` + `window.jQuery(ref.el)`.
- *(2026-09-15, `20_14` Gx.8)* Token share still showed two `/ Shares / TEST`
  breadcrumb rows and an empty folder/tag column. Inner
  `t-set="breadcrumbs_searchbar"` never reached `portal.portal_layout`
  (layout printed crumbs) while the slot later set the flag for
  `portal.portal_searchbar` (second row). Sale successor:
  `t-call … breadcrumbs_searchbar="True"`. The left column was already in
  the HTML; `jsTreePortal`'s `xml\`` template still used bare `state.treeData`.
  Checker `qweb-tcall` + `owl-this` on `xml\`` literals.
- *(2026-09-15, `20_14` Gx.8)* Off-proxy `treeData` was not enough for the
  attachment box. Chatter `state_ready` → `this.state.cloudsFolderId = …`
  (OWL proxy) remounts `CloudJsTreeContainer`; the state plugin's 100ms
  `save_state` then reads `this.element.scrollLeft` of null. Stack names
  `contextmenu.get_state` because that plugin is last on the chain. Keep
  the folder id off the proxy, patch `get_state` when `!this.element`,
  stub `save_state` before `destroy`. Do not drop the `state` plugin and
  do not skip `destroy` on a detached host. Portal `jsTreePortal` keeps
  `treeData` off `proxy`; `ready` stays on `proxy` for the `t-if`.
- *(2026-09-15, `20_14` Gx.8)* Token-share `Communication History` heading
  was half-cut. saas `portal.message_thread` is a bare `<h3>`. Dropping
  our wrapper `class="row"` was not enough — the heading as a sibling of
  the row (and inside a nested `.container`) is still clipped. Successor:
  no inner container; `#share_communication` is `col-12` inside the row.
- *(2026-09-15, `20_5` Gx.6)* `<calendar date_delay=...>` dies at install:
  RNG + `FIELD_ATTRIBUTE_NAMES` dropped `date_delay` (19.0
  `calendar_view.rng` + `calendar_arch_parser.js`; absent at saas-19.4).
  Drop the attribute; keep `date_start` / `date_stop`. Same run:
  `@tools.ormcache` is a deprecation that the warning gate attributes to
  us — `@api.ormcache`. Checker `calendar-attr` + `python-api`.
- *(2026-09-15, `20_5` Gx.6)* Gantt popover `<t t-esc=...>` in
  `ir.ui.view` arch dies (`Forbidden owl directive`). `t-out` is on the
  allowed list for qweb-based views; `web_gantt` adds `gantt` to that
  set. OWL `static/src` `t-esc` is unchanged. Checker `qweb-tesc`.
- *(2026-09-15, `20_14` Gx.8)* saas `_to_http_stream` redirects
  `type=url` when `store_fname` is empty (`ir_attachment.py:990`). 19.0
  streamed `db_datas` / `raw` as bytes and never took that branch. Synced
  File Manager thumbs then hit the cloud; Documents FileViewer
  (`/web/image/${documentId}?model=documents.document`) showed the camera
  placeholder when the gate only allowed `download` / `cloud_preview` /
  the preview group. `raw` is `BinaryValue` — use `.content`. Allow
  Documents `model=` / path; keep blocking bare `/web/image/{attach_id}`
  (proved: PNG 1885×1098 vs `size=0`).
- *(2026-09-16, `20_5` Gx.8 walk)* First clicks died on three OWL-3 holes the
  checker had reported clean: Joint Calendar
  `class="o_calendar_sidebar" position="inside"` (exact-string inherit; saas
  expanded panel is `o_calendar_sidepanel_content`), KPI
  `panelState.collapsed` / bare `panelClass`, Reminder Designer
  `update.bind="handleChange"` (`undefined.bind`). Same class as File
  Manager Gx.8. `20_14` `rule_parent.xml` already had `this.handleChange`;
  `20_2` has no FieldFilter. Checker `owl-xpath` exact `class=` +
  `owl-this` `*State.` / `env.` / bind / getter idents.
- *(2026-09-16, `20_5` Gx.8 re-walk)* Formula search died on
  `t-on-keydown="(event) => _onSearchNavigation(...)"` (handler undefined)
  and `orm.call(..., [[record.data.id]])` with a falsy id
  (`AssertionError: Invalid falsy real id` in saas `browse`). Successor:
  `this._onSearchNavigation`; pass `[[]]` when there is no `resId`. Checker
  `owl-this` now flags a `t-on-*` arrow that calls a method without `this.`.
  Same walk: empty calendars / one reminder / one KPI because
  `odootools_demo` never installed (hard depends on unported apps) and the
  `/tmp` seed ignored the 19.0 loaders. Gx.5 cannot be green without
  running those loaders and proving the 19.0 record counts.
- *(2026-09-16, `20_5` Gx.8 access)* Porting `ir.model.access` as an empty
  grouped `ir.access` next to a grouped domain permission ORs the filter
  away. saas `_get_domain_for` is `Domain.OR(permissions) &
  Domain.AND(restrictions)`; empty domain is `Domain.TRUE`
  (`ir_access.py:308`, `:355` at pin `3630379f63633612e5a9e8d435deecbe26eaa15a`).
  19.0 ACL was not a record filter. KPI User then saw every `kpi.item`
  despite `access_user_ids`. Successor: put the domain on the ACL row (or
  drop the empty ACL); keep global rules as restrictions; write explicit
  `[(1, '=', 1)]` only when 19.0 had a TRUE rule. Checker `access-or`.
  `20_2` restrictions are safe.   `20_14` `clouds.share` File Manager empty
  ACL matches a 19.0 TRUE rule — make the TRUE explicit. `total_notify`
  has the same empty-ACL hole as KPI.
- *(2026-09-16, `20_5` Gx.9 review)* Grouped 19.0 `ir.rule` on
  `base.group_user` ported as `ir.access` `operation=crud` granted
  every Internal User write on `kpi.item` / `kpi.category` / `kpi.tag`.
  19.0 ACL for those models was `group_kpi_user` read-only. Successor:
  product-group + 19.0 ops. Checker `access-grant`.

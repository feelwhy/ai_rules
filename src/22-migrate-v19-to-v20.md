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
reveals a new fact, update this rule and `tools/check_migrate_v20.py` **first**, in their own chunk,
then resume the module.

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

`tracking=True` on a field is **still valid** (`mail.track.mixin._valid_field_parameter`).

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

This is also an encoding change: `datas` was base64, `raw` is bytes.

```python
# BEFORE
self.env["ir.attachment"].create({"name": fname, "datas": base64.b64encode(content)})
# AFTER
self.env["ir.attachment"].create({"name": fname, "raw": content})
```

Audit every attachment write, not just the ones a grep highlights. Reading is affected too: use
`raw` (bytes) and encode only at the boundary that needs base64.

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

### `mail` Store API redesigned around `Store.FieldList`

`Store.add()` changed signature and `Store.get_result()` is gone:

```python
# BEFORE (19.0): fields optional, result fetched separately
def add(self, records, fields=None, extra_fields=None, as_thread=False, **kwargs)
return Store().add(messages).get_result()

# AFTER (20.0): fields mandatory and positional, no get_result
def add(self, records, fields, *, as_thread=False, fields_params=None, ignore_empty=False)
return Store().add(messages, "_store_message_fields")
```

The model-side hooks moved with it. The old hooks appended to a dict or returned a list of names;
the new ones receive a `Store.FieldList` and call `res.attr(...)` / `res.extend([...])`. This is a
rewrite, not a rename — budget real work for any module that formats mail data.

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
  files may be merged. An empty `domain` is the old ACL behavior.

Because the CSV can now carry a domain, ACL rows and record rules are interchangeable in form.
Do not take that as licence to restructure a module's security while porting — keep the same rows,
translated one to one, so a reviewer can diff them.

## XML / views

### Named inherit anchors: check the node, not just the view

A core view surviving under the same xmlid does **not** mean the node you hook onto survived.
`crm`'s `<group name="lead_priority">` (19.0 `crm_lead_views.xml:248`, the lead-only sibling of the
opportunity `tag_ids` group) is gone at `saas-19.4`: the lead and opportunity sidebars were merged
into one group with a single `tag_ids`. `complementary_lead_data` inherited that group by name, so
`crm.crm_lead_view_form` still resolved and the module still failed to load.

For every inherit of a core view, verify each anchor exists in the target arch:

- an `xpath` `expr` predicate — `//group[@name='lead_priority']`
- a tag carrying `position=` — `<group name="lead_priority" position="inside">`

The checker's `view-anchor` kind does this mechanically, and is a **signal in both directions**: it
looks the name up across all target XML, so an anchor that moved to another model's view is a miss,
and one built in Python rather than XML would be a false positive. Read the target arch before
deleting an xpath.

When the anchor is genuinely gone, prefer dropping the redundant hook over inventing a new one —
here the surviving `<field name="tag_ids" position="before">` already placed the widget, so the
second block was deleted rather than retargeted.

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
| `dead-hook` | the hook existed at the **base** ref and is gone at the target — a silent break |
| `stale-override` | absent at **both** refs — already dead before this port; a defect on the current serie, not porting work |
| `js-import` | an `@mod/path` import resolving to no file in `odoo` or `enterprise` |
| `js-symbol` | a **named** import (or `const { X } = owl`) whose path still resolves but the symbol is not exported at the target — this is how `useState` hid |
| `owl-xpath` | an OWL `t-inherit` XPath that selects `@t-ref` / `@t-esc` on a core template; those attributes moved (`t-custom-ref`, `t-ref="this.x"`) |
| `owl-tref` | an OWL-2 named `t-ref` / `t-model` / `t-portal` in our own `static/src` template; core writes `t-custom-*` |
| `owl-hook` | `useEffect(fn, deps)` imported from `@odoo/owl` — OWL 3 `useEffect` ignores the deps array |
| `python-api` | a call to a core method that is gone at the target (`get_param` / `set_param`) |
| `patch-target` | a `patch()` whose imported target no longer resolves |
| `patch-shadow` | a `patch(X.prototype, …)` member that upstream declares as a **class field** on the patched class or an ancestor — an own instance property shadows it, so it never runs, on any serie |
| `view-xmlid` | an `inherit_id` ref to a core view that no longer exists |
| `view-anchor` | an inherit anchor (`@name=` predicate, or a `position=` tag's `name`) that exists in no target view — a signal, see the caveat above |
| `security-model` | a data file declaring `ir.rule` / `ir.model.access`, gone at the target; CSV findings mean **rename the file** |
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
- **`view-anchor` collects only nodes an inherit *targets*.** A `name` inside an added block, or an
  `<attribute name="invisible">` under `position="attributes"`, is not an anchor; only an `expr`
  predicate and a tag carrying `position=` are. Without that distinction every field a module adds
  becomes a finding. It also does not see OWL `t-inherit` XPath on `@t-ref` — that is `owl-xpath`.
- **The target node-name set rides on the existing XML walk.** `view_xmlids()` already `git show`s
  every XML file in both trees, so the anchor lookup is a set membership, not one `git grep` per
  anchor (553 `position=` tags in `tools` would otherwise mean 553 greps).

## Verify at runtime, not from this rule

These are not settled by source reading. Do not write them into a port as fact:

- Asset bundle existence and restructuring (manifest-key grepping is unreliable; use the runtime
  asset gate).
- Remaining field renames inside surviving models (read the registry after a fresh install).
- Whether 20.0's optional-product rule on `sale.order.line` affects your line creation.
- Attendance access-rights and geolocation RPC changes for kiosk-facing code.
- Which deprecation warnings **your** code actually triggers (test-window log on the pinned image).

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

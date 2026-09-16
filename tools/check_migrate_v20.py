#!/usr/bin/env python3
"""Mechanical checks for the Odoo 19 -> 20 port (companion to rule 22-migrate-v19-to-v20).

Reads a repo of Odoo addons and target core/enterprise git refs, then reports the breaks that
phase-1 analysis proved are findable statically:

  dead-hook    an override of a core hook that no longer exists ON THE INHERITED MODEL
               (or still exists but the public path never calls it — see
               DEAD_DESPITE_EXISTING, e.g. _check_access)
  js-import    an `@mod/path` import that resolves to no file in odoo or enterprise,
               or a loadJS/loadCSS URL deleted at the target
               (/web/static/lib/jquery/jquery.js)
  view-xmlid   an `inherit_id` ref to a core view that no longer exists
  field-lit         a literal use of a removed field name (`datas`, `product_uom`)
  access-or         a grouped ir.access with an empty domain next to another
                    grouped row on the same model that has a real domain —
                    empty is Domain.TRUE and ORs the filter away (rule 22).
                    Also a core/enterprise empty permission on a model this
                    module domains, unless the module ANDs via _access_domain
  access-grant      a base.group_user permission with write ops on a model
               that also has a product-group permission — 19.0 ir.rule
               on Internal User was a filter, not an ACL grant (rule 22)
  access-op         ir.access.operation is not a CRUD_SELECTION key
               (letters stay in crud order: cr not rc)
  js-symbol         a named import whose file still exists but the export does not
  owl-xpath         an OWL t-inherit XPath selecting @t-ref / @t-esc on a core
                    template, or hasclass() of a class that left the inherited
                    t-name (o-kanban-button-new left web.KanbanView), or a
                    position= tag whose t-if/t-elif/t-else value is not on
                    that t-name (canDownload vs this.canDownload), or a
                    position= / @class= inherit whose exact class="…" string
                    is not on that t-name (o_calendar_sidebar vs the saas
                    collapsed-rail class list)
  owl-tref          an OWL-2 named t-ref / t-model / t-portal in our own static/src template
  owl-this          a t-inherit / standalone / xml` OWL template still uses
                    a bare OWL-3 scope name (state. / panelState. / env. /
                    props. / model.), a bare getter (t-att-class="panelClass"),
                    or a bare method bind (update.bind="handleChange",
                    t-on-click="clear", or t-on-keydown="(event) => foo()")
  qweb-tcall        inner t-set of a t-call (breadcrumbs_searchbar / object /
                    token / title) — saas-19.4 no longer copies those onto the
                    callee; write a t-call attribute or a controller value
  owl-hook          useEffect(fn, deps) from @odoo/owl — OWL 3 ignores the deps array
  python-api        a call to a core method gone at the target
                    (get_param / set_param / Registry.clear_cache /
                    Store.get_result)
                    or a leftover tools.ormcache (use odoo.api.ormcache)
                    or a named import that left odoo.http
                    (Stream / content_disposition)
  calendar-attr     a <calendar date_delay=...> — gone from RNG and
                    FIELD_ATTRIBUTE_NAMES at saas-19.4; drop the attribute
  qweb-tesc         t-esc / t-raw in a non-static XML arch (ir.ui.view);
                    saas _validate_qweb_directive forbids them. Use t-out.
  patch-target      a `patch()` on an import path that no longer resolves
  patch-shadow      a prototype patch of a member upstream declares as a class field
  manifest-version  a serie-prefixed manifest version while --odoo-ref is a saas-* branch

Design notes that matter (learned the hard way in phase 1):

* Hook existence is resolved against the *inherited model*, not a global name search. A global
  grep both hides dead hooks (name survives on an unrelated model) and invents false ones
  (module-internal super() chains whose name never existed upstream).
* Every existence check spans odoo AND enterprise. An odoo-only pass reports `@web_gantt/*` and
  `@documents/*` as missing.
* Counts are derived from `ast` / XML parsing, never regex, and occurrence counts are never
  presented as a work estimate.
* Nothing here proves a working port. Runtime gates still apply (see rule 22).
* Portal sharing "field is undefined" (`x_oz_tsk_*` in the arch, missing from portal
  `get_views` `models.fields`) is a current-serie `@ormcache(cache='stable')` hole on
  `project.task._portal_accessible_fields` (both refs). It is not a dead-hook and must
  not become a `TASK_PORTAL`+`search(` kind: that would stay red after a correct
  invalidate-on-write. Prove it with HTTP `get_views` on the running worker as portal.

Usage:
  python3 tools/check_migrate_v20.py --repo /path/to/tools \
      --odoo /path/to/odoo --odoo-ref origin/saas-19.4 \
      --enterprise /path/to/enterprise --enterprise-ref origin/saas-19.4 \
      [--modules a,b,c] [--json] [--quiet]

Exit code 1 if any finding is reported, else 0.
"""
from __future__ import annotations

import argparse
import ast
import csv
import json
import os
import re
import subprocess
import sys
from collections import defaultdict
from functools import lru_cache

# Field names removed upstream whose literal use fails silently (rule 22).
REMOVED_FIELD_LITERALS = {
    "datas": "ir.attachment.datas removed; use raw (BinaryValue; bytes via .content, not base64). Writes are silently dropped.",
    "product_uom": "stock.move.product_uom renamed uom_id. NOTE: sale.order.line / "
                   "product.supplierinfo legitimately use product_uom_id - check the model.",
}

# Security models unified into `ir.access` (rule 22). Keyed by the model name a data
# file declares, which is also the CSV file stem. Reported only when the old model is
# absent AND the successor present at the target ref, so a run against a serie that
# still has them stays silent.
RENAMED_SECURITY_MODELS = {
    "ir.rule": (
        "ir.access",
        "record rules and ACLs are one model now. XML: model=\"ir.access\", "
        "domain_force -> domain, perm_* -> operation (a subset of 'crud'), "
        "groups (M2M) -> group_id (one record per group). An empty group_id is a "
        "RESTRICTION, which is what a rule with no groups used to mean; a group_id "
        "makes it a PERMISSION.",
    ),
    "ir.model.access": (
        "ir.access",
        "rename the file to security/ir.access.csv and the manifest entry with it. "
        "Header: id,name,model_id,group_id/id,operation,domain. model_id is the "
        "technical model name (sticky.note), not the model_ xmlid; "
        "perm_read/write/create/unlink collapse into one operation string (1,1,1,1 -> "
        "crud; 1,0,0,0 -> r).",
    ),
}

# Loader aliases that never map to an addon file; PATH absence is not a finding.
# Symbol existence for @odoo/owl IS a finding (js-symbol). Do not skip that check.
JS_ALIAS_PREFIXES = ("@odoo/",)
JS_ALIAS_EXACT = {"@web/../tests/web_test_helpers", "@web/../tests/public/helpers"}

# Named imports whose file survived but the export did not (rule 22 OWL / JS).
# Hints only — the mechanical test is "is this name exported at the target?".
JS_SYMBOL_HINTS = {
    ("@odoo/owl", "useState"):
        "OWL 3 deleted useState. Core FormRenderer: this.state = proxy({}). "
        "The owl3 compat layer does NOT restore it.",
    ("@odoo/owl", "reactive"):
        "OWL 3 deleted reactive. Use proxy() from @odoo/owl.",
    ("@odoo/owl", "loadFile"):
        "OWL 3 deleted loadFile.",
    ("@odoo/owl", "validate"):
        "OWL 3 deleted validate.",
    ("@web/core/utils/concurrency", "Deferred"):
        "gone; use Promise.withResolvers() "
        "(polyfill in web/static/src/polyfills/promise.js).",
    ("@web/core/assets", "LazyComponent"):
        "moved to @web/core/lazy_component.",
    ("@web/core/emoji_picker/emoji_picker", "loadEmoji"):
        "use useLoadEmoji() from @web/core/emoji_picker/emoji_loader.",
    ("@web/core/utils/reactive", "effect"):
        "gone from this module. OWL 3 effect(fn) is not the two-arg helper.",
    ("@html_builder/core/utils", "BaseOptionComponent"):
        "moved to @html_builder/core/base_option_component.",
}

REMOVED_PYTHON_CALLS = {
    "get_param":
        "ir.config_parameter.get_param is gone; use get_str / get_bool / "
        "get_int / get_float.",
    "set_param":
        "ir.config_parameter.set_param is gone; use set_str / set_bool / "
        "set_int / set_float.",
    "clear_cache":
        "Registry.clear_cache is gone; use "
        "env.transaction.invalidate_ormcache('stable') "
        "(or 'templates' / 'default').",
    "get_result":
        "Store.get_result is gone; Store.add(records, fields) returns the "
        "Store, and json_default calls as_dict(). Core mail upload uses "
        "Store().add(attachment, lambda res: res.from_method("
        "'_store_attachment_fields')).",
}

# Named imports that left odoo.http when it became a package (saas-19.4).
# request / Controller / route / Response stay on odoo.http.
HTTP_PACKAGE_MOVED = {
    "Stream": "from odoo.http.stream import Stream",
    "content_disposition": "from odoo.http.stream import content_disposition",
}

HTTP_FROM_RE = re.compile(
    r"from\s+odoo\.http\s+import\s+(\([^)]*\)|[^\n]+)",
    re.S,
)

# Hooks that still exist at the target but the public path no longer calls them.
# check_access / has_access / _filtered_access are @typing.final and use _access_domain.
# _check_access is @deprecated("Since 20.0, use Model._access_domain instead") and is
# never invoked — a name-exists check reports clean and the override is a silent miss.
DEAD_DESPITE_EXISTING = {
    "_check_access": (
        "check_access / has_access / _filtered_access are @typing.final and use "
        "_access_domain; _check_access is @deprecated Since 20.0 and is never called. "
        "Port to _access_domain + res_access_* (see ir.attachment / mail.activity)"
    ),
}

OWL_DESTRUCTURE_RE = re.compile(
    r"""(?:const|let|var)\s*\{\s*([^}]+)\}\s*=\s*owl\b"""
)
OWL_XPATH_TREF_RE = re.compile(
    r"""@t-(?:ref|esc|raw|portal|model)\s*=\s*["'][^"']+["']"""
)
OWL_OWN_TREF_RE = re.compile(
    r"""(?<!@)t-(?:ref|model|portal)\s*=\s*["'](?!this\.)[^"']+["']"""
)
OWL_TNAME_OPEN_RE = re.compile(
    r'<t\b([^>]*\bt-name="([^"]+)"[^>]*)>',
    re.I | re.S,
)
OWL_TINHERIT_RE = re.compile(r'\bt-inherit="([^"]+)"')
OWL_HASCLASS_RE = re.compile(r"""hasclass\(\s*['"]([^'"]+)['"]\s*\)""")
# OWL 3 compiled templates no longer bind `state` / `props` / `model` as
# bare names — nor `panelState` / `env` (20_5 Gx.8 KPI + calendar).
# Core inherit targets write this.state / this.props / this.env.
OWL_BARE_SCOPE_RE = re.compile(
    r"(?<![\w.])([A-Za-z_]*[Ss]tate|props|model|env)\."
)
# OWL 3 compile: ctx.foo is not auto-bound. t-props="getX()" dies
# (getCloudManagerNavigationProps is not a function).
OWL_BARE_CALL_RE = re.compile(
    r"""\b(?:t-props|t-out|t-esc|t-att-class|t-att-style)=["'](?!this\.)([A-Za-z_]\w*)\("""
)
# Getters and methods used as a bare ident: t-att-class="panelClass",
# t-on-click="clear". Arrow / this. values are excluded.
OWL_BARE_ATTR_IDENT_RE = re.compile(
    r"""\b(?:t-att-class|t-att-style|t-on-click(?:\.\w+)?)=["'](?!this\.|[\(\[])([A-Za-z_]\w*)["']"""
)
# update.bind="handleChange" → TypeError: Cannot read properties of
# undefined (reading 'bind'). 20_14 already wrote this.handleChange.
OWL_BARE_BIND_RE = re.compile(
    r"""\b[A-Za-z_]\w*\.bind=["'](?!this\.)([A-Za-z_]\w*)["']"""
)
# t-on-keydown="(event) => _onSearchNavigation(...)" — OWL 3 handler is
# undefined (20_5 KPI formula). Arrow + this. is fine.
OWL_BARE_ARROW_CALL_RE = re.compile(
    r"""\bt-on-[\w.]+=["'][^"']*?=>\s*(?!this\.)([A-Za-z_]\w*)\s*\("""
)
OWL_CLASS_ATTR_RE = re.compile(r'\bclass="([^"]+)"')
OWL_XPATH_CLASS_RE = re.compile(
    r"""//([A-Za-z][\w.]*)\[@class=(?:&quot;|'|\")(.*?)(?:&quot;|'|\")\]"""
)
# Inline OWL templates (`xml\`...\``) are not t-name files. Bare state.
# there still dies (portal jsTreePortal).
OWL_XML_LIT_RE = re.compile(r"\bxml\s*`([\s\S]*?)`")
# saas-19.4 dropped is_deprecated_version: inner t-set of a t-call is
# the slot only. First child t-set of these keys never reaches the callee.
QWEB_TCALL_INNER_SET_RE = re.compile(
    r'<t\b[^>]*\bt-call="([^"]+)"[^>]*>\s*<t\b[^>]*\bt-set="'
    r'(breadcrumbs_searchbar|object|token|title)"',
    re.S,
)
# OWL inherit matches the full opening tag. saas-19.4 prefixed many
# directives with this. (`canDownload` → `this.canDownload`); a leftover
# 19.0 t-elif is then "cannot be located".
OWL_OPEN_TAG_RE = re.compile(
    r"<([A-Za-z][\w.]*)((?:[^>\"']|\"[^\"]*\"|'[^']*')*)>",
    re.DOTALL,
)
OWL_DIR_ATTR_RE = re.compile(r"""\b(t-if|t-elif|t-else)=("[^"]*"|'[^']*')""")
OWL_XPATH_DIR_PRED_RE = re.compile(
    r"""//([A-Za-z][\w.]*)\[@(t-if|t-elif|t-else)=(?:&quot;|'|\")(.*?)(?:&quot;|'|\")\]"""
)


def log(msg: str = "") -> None:
    """Informational output. Goes to stderr so --json keeps stdout machine-readable."""
    print(msg, file=sys.stderr)


class Tree:
    """Read-only view of one git ref, with cached path/content lookups."""

    def __init__(self, repo: str, ref: str, label: str):
        self.repo = repo
        self.ref = ref
        self.label = label
        self._paths: set[str] | None = None

    def _git(self, *args: str) -> subprocess.CompletedProcess:
        return subprocess.run(["git", "-C", self.repo, *args],
                              capture_output=True, text=True)

    @property
    def paths(self) -> set[str]:
        if self._paths is None:
            out = self._git("ls-tree", "-r", "--name-only", self.ref)
            if out.returncode != 0:
                raise SystemExit(f"{self.label}: cannot read ref {self.ref}: {out.stderr.strip()}")
            self._paths = set(out.stdout.splitlines())
        return self._paths

    def exists(self, path: str) -> bool:
        return path in self.paths

    @lru_cache(maxsize=4096)
    def show(self, path: str) -> str | None:
        if not self.exists(path):
            return None
        out = self._git("show", f"{self.ref}:{path}")
        return out.stdout if out.returncode == 0 else None

    def grep(self, pattern: str, *pathspecs: str, raw_paths: bool = False) -> str:
        flags = ["-oE"] if raw_paths else ["-h", "-oE"]
        out = self._git("grep", *flags, pattern, self.ref, "--", *pathspecs)
        return out.stdout


class Target:
    """odoo + enterprise at the target refs, queried as one surface."""

    def __init__(self, odoo: Tree, enterprise: Tree | None):
        self.trees = [t for t in (odoo, enterprise) if t is not None]
        self.odoo = odoo
        self.enterprise = enterprise

    # ---- module layout -------------------------------------------------
    def addon_roots(self, module: str) -> list[tuple[Tree, str]]:
        """Where module `module` could live in each target tree."""
        out: list[tuple[Tree, str]] = []
        out.append((self.odoo, f"addons/{module}"))
        out.append((self.odoo, f"odoo/addons/{module}"))  # base only
        if self.enterprise is not None:
            out.append((self.enterprise, module))
        return out

    def any_exists(self, rel_candidates: list[tuple[Tree, str]]) -> bool:
        return any(tree.exists(path) for tree, path in rel_candidates)

    # ---- model registry ------------------------------------------------
    # Resolved lazily, one model at a time, via `git grep`. An eager index of every
    # model in both trees costs thousands of `git show` calls (~25 min for a full run);
    # a port only ever asks about the few dozen models the repo actually extends.
    @lru_cache(maxsize=2048)
    def model_files(self, model: str) -> tuple[tuple[Tree, str], ...]:
        """Files that declare or extend `model`, across both trees."""
        found: list[tuple[Tree, str]] = []
        needle = re.compile(
            rf"""_(?:name|inherit)\s*=\s*(?:\[[^\]]*['"]{re.escape(model)}['"]|['"]{re.escape(model)}['"])"""
        )
        # NOTE: `git grep -E` is POSIX ERE - no `(?:...)`, no `\s`. Using them here silently
        # matches nothing, which looks exactly like "no findings".
        posix_model = model.replace(".", "[.]")
        for tree in self.trees:
            out = tree.grep(rf"""_(name|inherit)[[:space:]]*=.*['"]{posix_model}['"]""",
                            "*.py", raw_paths=True)
            for line in out.splitlines():
                # format: <ref>:<path>:<match>
                parts = line.split(":", 2)
                if len(parts) < 3:
                    continue
                path = parts[1]
                if "/tests/" in path or "/static/" in path:
                    continue
                src = tree.show(path)
                if src and needle.search(src):
                    found.append((tree, path))
        return tuple(found)

    @lru_cache(maxsize=1)
    def framework_methods(self) -> set[str]:
        """Methods defined on BaseModel and friends, i.e. available on EVERY model.

        Without this the check reports `export_data`, `_check_access`, `copy`, ... as dead,
        because they live in odoo/orm/models.py rather than an addon's models/ directory.
        """
        names: set[str] = set()
        pat = re.compile(r"^\s*(?:def|async def)\s+([a-zA-Z_][\w]*)\s*\(", re.M)
        for path in self.odoo.paths:
            if not path.endswith(".py"):
                continue
            if not (path.startswith(("odoo/orm/", "odoo/models/", "odoo/api/", "odoo/fields/"))
                    or re.fullmatch(r"odoo/[a-z_]+\.py", path)):
                continue
            src = self.odoo.show(path)
            if src:
                names.update(pat.findall(src))
        return names

    def model_defines(self, model: str, method: str) -> bool:
        """Does any file touching `model` define `method`?

        Scoped to the model's own files, which is the whole point: a global name search
        both hides dead hooks and invents false ones.
        """
        if method in self.framework_methods():
            return True
        files = self.model_files(model)
        if not files:
            return False
        needle = re.compile(rf"^\s*(?:def|async def)\s+{re.escape(method)}\s*\(", re.M)
        attr = re.compile(rf"^\s*{re.escape(method)}\s*=", re.M)
        for tree, path in files:
            src = tree.show(path)
            if src and (needle.search(src) or attr.search(src)):
                return True
        return False

    def model_known(self, model: str) -> bool:
        return bool(self.model_files(model))

    # ---- js module resolution -------------------------------------------
    def js_candidates(self, spec: str) -> list[tuple[Tree, str]]:
        mod, _, rest = spec.lstrip("@").partition("/")
        if not rest:
            return []
        cands: list[tuple[Tree, str]] = []
        for tree, root in self.addon_roots(mod):
            base = f"{root}/static/src/{rest}"
            cands += [(tree, base + ".js"), (tree, base + "/index.js"), (tree, base + ".xml")]
        return cands

    def resolve_js(self, spec: str) -> bool:
        if spec in JS_ALIAS_EXACT or spec.startswith(JS_ALIAS_PREFIXES):
            return True
        cands = self.js_candidates(spec)
        return True if not cands else self.any_exists(cands)

    @lru_cache(maxsize=1)
    def owl_exports(self) -> frozenset[str]:
        """Public names on `@odoo/owl` at this target: owl.d.ts plus compat assignments.

        `@odoo/owl` is a loader alias, so resolve_js is always True. The 19 -> 20 break is
        a deleted *export* (useState). Compat restores useRef / useLayoutEffect / … and
        does not restore useState or reactive.
        """
        names: set[str] = set()
        dts = self.odoo.show("addons/web/static/lib/owl/owl.d.ts") or ""
        names.update(re.findall(
            r"^export (?:declare )?(?:function|class|const|type|enum|interface)\s+"
            r"([A-Za-z_][\w]*)",
            dts, re.M,
        ))
        for grp in re.findall(r"^export \{([^}]+)\}", dts, re.M):
            names.update(re.findall(r"([A-Za-z_][\w]*)", grp))
        compat = self.odoo.show(
            "addons/web/static/src/owl2/owl3_compatibility_layer.js"
        ) or ""
        names.update(re.findall(r"owl\.([A-Za-z_][\w]*)\s*=", compat))
        return frozenset(names)

    def js_exported_names(self, spec: str) -> set[str] | None:
        """Export names of the file `spec` resolves to, or None if the path is gone.

        One-level relative `export { … } from` / `export * from` are followed so a
        barrel file is not reported as missing everything it re-exports. `@odoo/owl`
        is handled by owl_exports, not here.
        """
        if spec == "@odoo/owl" or spec.startswith("@odoo/owl"):
            return set(self.owl_exports())
        src = self.js_source(spec)
        if src is None:
            return None
        return _js_parse_exports(src, spec, self)

    def js_source(self, spec: str) -> str | None:
        for tree, path in self.js_candidates(spec):
            if path.endswith(".js") and tree.exists(path):
                return tree.show(path)
        return None

    @lru_cache(maxsize=512)
    def js_class_fields(self, spec: str, symbol: str) -> frozenset[str]:
        """Members declared as CLASS FIELDS by class `symbol` of module `spec`, and its ancestors.

        A class field is an *own property* of every instance, so `patch(X.prototype, ...)` can
        never override it - the patch is silently dead (rule 22, `MessageModel.isEmpty`).

        Bound to the *patched class*, never to the file: a module may export several classes, and
        a field of a class nobody patched says nothing about the one that was. Ancestors are
        followed through `extends` (local or imported) because the member may live on a parent or
        mixin rather than the class the module imported. Returns an empty set - never a guess -
        when the class cannot be located.
        """
        names: set[str] = set()
        seen: set[tuple[str, str]] = set()
        pending = [(spec, symbol)]
        while pending:
            cur_spec, cur_symbol = pending.pop()
            if (cur_spec, cur_symbol) in seen:
                continue
            seen.add((cur_spec, cur_symbol))
            src = self.js_source(cur_spec)
            if not src:
                continue
            body, parent = js_class_body(js_blank_literals(src), cur_symbol)
            if body is None:
                continue
            names.update(js_own_field_names(body))
            if parent:
                imports = js_import_bindings(src)
                # An imported parent moves to its own module; a local one stays in this file.
                pending.append((imports.get(parent, cur_spec), parent))
        return frozenset(names)

    # ---- view xmlids -----------------------------------------------------
    @lru_cache(maxsize=1)
    def _xml_index(self) -> tuple[set[str], set[str]]:
        """(record + QWeb `<template id>` xmlids, every `name="..."` value) over all target XML.

        One pass for both: `tree.show` is cached, but the walk itself is the expensive
        part, so the node-name set rides along instead of grepping per anchor.
        """
        ids: set[str] = set()
        node_names: set[str] = set()
        rec = re.compile(r'<record[^>]*\bid="([a-zA-Z0-9_.]+)"')
        # QWeb <template id="snippets"> is ir.ui.view xmlid website.snippets.
        # A record-only scan reported website.snippets gone at saas-19.4 (20_9).
        tmpl = re.compile(r'<template[^>]*\bid="([a-zA-Z0-9_.]+)"')
        name = re.compile(r'\bname="([^"]+)"')
        html_id = re.compile(r'\bid="([^"]+)"')
        for tree in self.trees:
            for path in tree.paths:
                if not path.endswith(".xml") or "/static/" in path or "/i18n/" in path:
                    continue
                parts = path.split("/")
                if path.startswith("addons/"):
                    module = parts[1]
                elif path.startswith("odoo/addons/"):
                    module = parts[2]
                else:
                    module = parts[0]
                src = tree.show(path)
                if not src:
                    continue
                for xid in rec.findall(src) + tmpl.findall(src):
                    ids.add(xid if "." in xid else f"{module}.{xid}")
                node_names.update(name.findall(src))
                node_names.update(html_id.findall(src))
        return ids, node_names

    def view_xmlids(self) -> set[str]:
        return self._xml_index()[0]

    def view_node_names(self) -> set[str]:
        return self._xml_index()[1]

    @lru_cache(maxsize=1)
    def _view_record_index(self) -> dict[str, str]:
        """xmlid -> full `<record>` / `<template>` source at the target.

        Parent-bound `view-anchor` needs the inherited view's own arch, not the
        global name set. `project.view_task_kanban` still exists at saas-19.4
        but is a `card_id` shell — `priority` lives on `view_task_card`.
        """
        rec_re = re.compile(
            r'<record\b[^>]*\bid="([a-zA-Z0-9_.]+)"[^>]*>.*?</record>',
            re.S,
        )
        tmpl_re = re.compile(
            r'<template\b[^>]*\bid="([a-zA-Z0-9_.]+)"[^>]*>.*?</template>',
            re.S,
        )
        out: dict[str, str] = {}
        for tree in self.trees:
            for path in tree.paths:
                if not path.endswith(".xml") or "/static/" in path or "/i18n/" in path:
                    continue
                parts = path.split("/")
                if path.startswith("addons/"):
                    module = parts[1]
                elif path.startswith("odoo/addons/"):
                    module = parts[2]
                else:
                    module = parts[0]
                src = tree.show(path)
                if not src:
                    continue
                for cre, blob in ((rec_re, src), (tmpl_re, src)):
                    for m in cre.finditer(blob):
                        xid = m.group(1)
                        key = xid if "." in xid else f"{module}.{xid}"
                        out[key] = m.group(0)
        return out

    def view_record_src(self, xid: str) -> str | None:
        return self._view_record_index().get(xid)

    @lru_cache(maxsize=1)
    def owl_template_classes(self) -> dict[str, frozenset[str]]:
        """`t-name` -> CSS classes in that OWL template at the target.

        `_xml_index` skips `/static/`, so a class that moved between two
        `t-name`s in the same file (web.KanbanView -> web.KanbanView.Buttons)
        was invisible. Split on `t-name`, never on file.
        """
        out: dict[str, set[str]] = {}
        for tree in self.trees:
            seen: set[str] = set()
            grep_out = tree.grep(r't-name=', "*.xml", raw_paths=True)
            for line in grep_out.splitlines():
                parts = line.split(":", 2)
                if len(parts) < 3:
                    continue
                path = parts[1]
                if "/static/" not in path or path in seen:
                    continue
                seen.add(path)
                src = tree.show(path)
                if not src:
                    continue
                for _off, name, _inherit, body in _owl_template_spans(src):
                    classes = set()
                    for raw in OWL_CLASS_ATTR_RE.findall(body):
                        classes.update(raw.split())
                    out.setdefault(name, set()).update(classes)
        return {name: frozenset(classes) for name, classes in out.items()}

    @lru_cache(maxsize=1)
    def owl_template_class_strings(self) -> dict[str, frozenset[str]]:
        """`t-name` -> exact `class="…"` attribute strings at the target.

        OWL inherit matches the opening-tag attribute, not a class token.
        `class="o_calendar_sidebar"` does not match saas
        `class="o_calendar_sidebar flex-grow-0 …"` even though the token
        still exists on the collapsed rail.
        """
        out: dict[str, set[str]] = {}
        for tree in self.trees:
            seen: set[str] = set()
            grep_out = tree.grep(r't-name=', "*.xml", raw_paths=True)
            for line in grep_out.splitlines():
                parts = line.split(":", 2)
                if len(parts) < 3:
                    continue
                path = parts[1]
                if "/static/" not in path or path in seen:
                    continue
                seen.add(path)
                src = tree.show(path)
                if not src:
                    continue
                for _off, name, _inherit, body in _owl_template_spans(src):
                    out.setdefault(name, set()).update(OWL_CLASS_ATTR_RE.findall(body))
        return {name: frozenset(vals) for name, vals in out.items()}

    @lru_cache(maxsize=1)
    def owl_template_directives(self) -> dict[str, frozenset[tuple[str, str, str]]]:
        """`t-name` -> {(tag, t-if|t-elif|t-else, value)} at the target.

        OWL inherit matches the opening tag, so `t-elif="canDownload(attachment)"`
        does not match saas `t-elif="this.canDownload(attachment)"`. hasclass()
        indexing cannot see that.
        """
        out: dict[str, set[tuple[str, str, str]]] = {}
        for tree in self.trees:
            seen: set[str] = set()
            grep_out = tree.grep(r't-name=', "*.xml", raw_paths=True)
            for line in grep_out.splitlines():
                parts = line.split(":", 2)
                if len(parts) < 3:
                    continue
                path = parts[1]
                if "/static/" not in path or path in seen:
                    continue
                seen.add(path)
                src = tree.show(path)
                if not src:
                    continue
                for _off, name, _inherit, body in _owl_template_spans(src):
                    out.setdefault(name, set()).update(_owl_directive_triples(body))
        return {name: frozenset(triples) for name, triples in out.items()}


def _owl_directive_triples(body: str) -> set[tuple[str, str, str]]:
    triples = set()
    for match in OWL_OPEN_TAG_RE.finditer(body):
        tag, attrs = match.group(1), match.group(2)
        dm = OWL_DIR_ATTR_RE.search(attrs)
        if not dm:
            continue
        triples.add((tag, dm.group(1), dm.group(2)[1:-1]))
    return triples


def _owl_position_directive_triples(body: str):
    """Yield `(offset, tag, attr, value)` for inherit anchors with position=."""
    for match in OWL_OPEN_TAG_RE.finditer(body):
        tag, attrs = match.group(1), match.group(2)
        if "position=" not in attrs:
            continue
        dm = OWL_DIR_ATTR_RE.search(attrs)
        if dm:
            yield match.start(), tag, dm.group(1), dm.group(2)[1:-1]
        if tag == "xpath":
            expr_m = re.search(r'\bexpr="([^"]+)"', attrs)
            if not expr_m:
                continue
            pred = OWL_XPATH_DIR_PRED_RE.search(expr_m.group(1))
            if pred:
                yield match.start(), pred.group(1), pred.group(2), pred.group(3)


# ------------------------------------------------------------------ repo side

class Finding:
    def __init__(self, kind: str, module: str, path: str, line: int, detail: str):
        self.kind, self.module, self.path, self.line, self.detail = kind, module, path, line, detail

    def as_dict(self) -> dict:
        return {"kind": self.kind, "module": self.module, "path": self.path,
                "line": self.line, "detail": self.detail}


def discover_modules(repo: str, wanted: list[str] | None) -> list[str]:
    mods = sorted(d for d in os.listdir(repo)
                  if os.path.isfile(os.path.join(repo, d, "__manifest__.py")))
    if wanted:
        missing = [m for m in wanted if m not in mods]
        if missing:
            raise SystemExit(f"not addons of {repo}: {', '.join(missing)}")
        return [m for m in mods if m in wanted]
    return mods


def walk(repo: str, module: str, *suffixes: str):
    root = os.path.join(repo, module)
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in {".git", "__pycache__", "i18n"}]
        for name in filenames:
            if suffixes and not name.endswith(suffixes):
                continue
            full = os.path.join(dirpath, name)
            yield full, os.path.relpath(full, repo)


def read(path: str) -> str:
    with open(path, encoding="utf-8", errors="replace") as fh:
        return fh.read()


class RepoModels:
    """Inheritance graph and method index for the repo under test.

    Needed for two false-positive classes that a naive scan gets wrong:

    * The MRO often reaches core *through one of our own models*
      (`business.appointment` -> `business.appointment.core` -> `mail.thread`).
      Only direct parents would miss `mail.thread` and report live hooks as dead.
    * Another class may define the method on the same model - in a sibling
      module or in this one - so the super() chain resolves inside the repo.
      Limitation: if two of our classes both override the same *removed* core
      hook on the same model, this hides it. That only affects the
      `stale-override` class; a real 19 -> 20 removal is classified from the
      base ref before this suppression runs.
    """

    def __init__(self, repo: str, modules: list[str]):
        self.parents: dict[str, set[str]] = defaultdict(set)
        # model -> {(method, module, relative path, line)}
        self.methods: dict[str, set[tuple[str, str, str, int]]] = defaultdict(set)
        self.owned: set[str] = set()
        for module in modules:
            for full, rel in walk(repo, module, ".py"):
                if "/tests/" in rel.replace(os.sep, "/"):
                    continue
                try:
                    tree = ast.parse(read(full))
                except SyntaxError:
                    continue
                for node in ast.walk(tree):
                    if not isinstance(node, ast.ClassDef):
                        continue
                    name, inherits = class_models(node)
                    model = name or (inherits[0] if inherits else None)
                    if not model:
                        continue
                    if name:
                        self.owned.add(name)
                    for parent in inherits:
                        if parent != model:
                            self.parents[model].add(parent)
                    for stmt in node.body:
                        if isinstance(stmt, (ast.FunctionDef, ast.AsyncFunctionDef)):
                            self.methods[model].add((stmt.name, module, rel, stmt.lineno))

    def ancestors(self, model: str) -> set[str]:
        """Transitive parents, expanding through repo-owned models."""
        seen: set[str] = set()
        stack = list(self.parents.get(model, ()))
        while stack:
            cur = stack.pop()
            if cur in seen:
                continue
            seen.add(cur)
            stack.extend(self.parents.get(cur, ()))
        return seen

    def defined_elsewhere(self, models: set[str], method: str,
                          path: str, line: int) -> str | None:
        """Another definition of `method` on one of `models`, outside the site being judged.

        Compared by (path, line) rather than by module: an internal chain inside one module is
        just as real as a cross-module one, and comparing modules made the check report the
        second class of the same model as a stale override.
        """
        for model in models:
            for name, owner, opath, oline in self.methods.get(model, ()):
                if name == method and (opath, oline) != (path, line):
                    return f"{owner} ({opath}:{oline})"
        return None


def class_models(node: ast.ClassDef) -> tuple[str | None, list[str]]:
    """(_name, _inherit list) declared on an Odoo model class."""
    own = None
    inherits: list[str] = []
    for stmt in node.body:
        if not isinstance(stmt, ast.Assign):
            continue
        names = {t.id for t in stmt.targets if isinstance(t, ast.Name)}
        if not names & {"_inherit", "_name"}:
            continue
        try:
            val = ast.literal_eval(stmt.value)
        except Exception:
            continue
        vals = [val] if isinstance(val, str) else list(val) if isinstance(val, (list, tuple)) else []
        vals = [v for v in vals if isinstance(v, str)]
        if "_name" in names and vals:
            own = vals[0]
        if "_inherit" in names:
            inherits += vals
    return own, inherits


def check_dead_hooks(repo: str, module: str, target: Target, repo_models: RepoModels,
                     base: Target | None = None) -> list[Finding]:
    """Overrides of core hooks, classified by comparing the base and target refs.

    exists at base, gone at target -> dead-hook     (the 19 -> 20 break we care about)
    gone at both                   -> stale-override (pre-existing; not caused by this port)
    exists at target               -> live; not reported, except DEAD_DESPITE_EXISTING
                                      (_check_access is still defined but never called)

    Comparing both refs is what makes this trustworthy. A target-only check cannot tell a
    fresh removal from an override that was already dead on 19.0, and it is exactly why the
    earlier sibling-module heuristic had to go: that heuristic hid real removals whenever two
    of our modules overrode the same core hook.
    """
    out: list[Finding] = []
    for full, rel in walk(repo, module, ".py"):
        if "/tests/" in rel.replace(os.sep, "/"):
            continue
        try:
            tree = ast.parse(read(full))
        except SyntaxError:
            continue
        for node in ast.walk(tree):
            if not isinstance(node, ast.ClassDef):
                continue
            own_name, inherits = class_models(node)
            model = own_name or (inherits[0] if inherits else None)
            if not model:
                continue
            # Full ancestor set, expanded through our own models, then keep the core ones.
            chain = set(inherits) | repo_models.ancestors(model)
            if own_name and own_name not in inherits:
                # `_name` alone means the model starts here, so it is not its own parent. But
                # `_name = X` together with `_inherit = [X, ...]` is the extend-in-place style
                # (odoo_email_from's mail.compose.message), where X *is* the core parent -
                # dropping it left the class with no core chain at all.
                chain.discard(own_name)
            core_chain = {m for m in chain if target.model_known(m)}
            if not core_chain:
                # Every Odoo model still inherits BaseModel, so an override can be dead even
                # when the class names no core parent. `portal.password.key` (_inherit = one of
                # our own mixins) hid a dead `_generate_order_by` from this check exactly that
                # way; only a direct grep found it. `base` resolves through framework_methods().
                core_chain = {"base"}
            for stmt in node.body:
                if not isinstance(stmt, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    continue
                if not calls_super(stmt):
                    continue
                models_txt = ", ".join(sorted(core_chain))
                target_has = any(target.model_defines(m, stmt.name) for m in core_chain)
                if target_has and stmt.name in DEAD_DESPITE_EXISTING:
                    out.append(Finding(
                        "dead-hook", module, rel, stmt.lineno,
                        f"{stmt.name}() still exists on {models_txt} at the target "
                        f"ref but is never called. {DEAD_DESPITE_EXISTING[stmt.name]}",
                    ))
                    continue
                if target_has:
                    continue
                existed_at_base = base is not None and any(
                    base.model_defines(m, stmt.name) for m in core_chain
                )
                if base is None:
                    kind, detail = "dead-hook", (
                        f"{stmt.name}() overrides nothing on {models_txt} at the target ref "
                        f"- pass --odoo-base-ref to tell a fresh removal from a stale override")
                elif existed_at_base:
                    kind, detail = "dead-hook", (
                        f"{stmt.name}() existed on {models_txt} at the base ref and is gone at the "
                        f"target ref - the override will never be called, silently")
                else:
                    sibling = repo_models.defined_elsewhere(
                        chain | {model}, stmt.name, rel, stmt.lineno)
                    if sibling:
                        continue  # our own super() chain, never an upstream hook
                    kind, detail = "stale-override", (
                        f"{stmt.name}() is absent from {models_txt} at BOTH refs - already dead "
                        f"before this port, not caused by it")
                out.append(Finding(kind, module, rel, stmt.lineno, detail))
    return out


def calls_super(fn: ast.AST) -> bool:
    for n in ast.walk(fn):
        if not isinstance(n, ast.Call):
            continue
        f = n.func
        if isinstance(f, ast.Name) and f.id == "super":
            return True
        if (isinstance(f, ast.Attribute) and isinstance(f.value, ast.Call)
                and isinstance(f.value.func, ast.Name) and f.value.func.id == "super"):
            return True
    return False


JS_IMPORT_RE = re.compile(r"""(?:from|import)\s+["'](@[a-z_0-9]+/[^"']+)["']""")
JS_PATCH_RE = re.compile(r"\bpatch\s*\(\s*([A-Za-z_$][\w$]*)")
JS_PROTO_PATCH_RE = re.compile(r"\bpatch\s*\(\s*([A-Za-z_$][\w$]*)\.prototype\s*,")
JS_IMPORT_STMT_RE = re.compile(
    r"""import\s+(?:\{(?P<named>[^}]*)\}|(?P<default>[A-Za-z_$][\w$]*))\s*from\s*["'](?P<spec>[^"']+)["']"""
)


def _join_js_spec(spec: str, rel: str) -> str:
    """Resolve `./x` / `../x` against an `@mod/path` spec (no .js suffix)."""
    if rel.startswith("@"):
        return rel.split(".", 1)[0] if not rel.endswith(".js") else rel[:-3]
    rel = rel[:-3] if rel.endswith(".js") else rel
    directory = spec.rsplit("/", 1)[0]
    bits: list[str] = []
    for part in (directory + "/" + rel).split("/"):
        if part in (".", ""):
            continue
        if part == "..":
            if bits:
                bits.pop()
            continue
        bits.append(part)
    return "/".join(bits)


def _js_parse_exports(src: str, spec: str, target: "Target") -> set[str]:
    """Export names visible from `src`, following one level of relative re-export."""
    names: set[str] = set()
    reexports: list[str] = []
    for m in re.finditer(
        r"^export\s+(?:async\s+)?(?:function|class|const|let|var)\s+([A-Za-z_$][\w$]*)",
        src, re.M,
    ):
        names.add(m.group(1))
    if re.search(r"^export\s+default\b", src, re.M):
        names.add("default")
    for m in re.finditer(
        r"^export\s+\{([^}]+)\}(?:\s*from\s*['\"]([^'\"]+)['\"])?",
        src, re.M,
    ):
        for part in m.group(1).split(","):
            part = part.strip()
            if not part:
                continue
            bits = re.findall(r"[A-Za-z_$][\w$]*", part)
            if not bits:
                continue
            names.add(bits[-1] if " as " in part else bits[0])
        if m.group(2):
            reexports.append(m.group(2))
    for m in re.finditer(r"^export\s+\*\s+from\s*['\"]([^'\"]+)['\"]", src, re.M):
        reexports.append(m.group(1))
    for rel in reexports:
        if not rel.startswith("."):
            continue
        child = target.js_source(_join_js_spec(spec, rel))
        if not child:
            continue
        for m in re.finditer(
            r"^export\s+(?:async\s+)?(?:function|class|const|let|var)\s+([A-Za-z_$][\w$]*)",
            child, re.M,
        ):
            names.add(m.group(1))
        if re.search(r"^export\s+default\b", child, re.M):
            names.add("default")
        for m in re.finditer(r"^export\s+\{([^}]+)\}", child, re.M):
            for part in m.group(1).split(","):
                bits = re.findall(r"[A-Za-z_$][\w$]*", part)
                if bits:
                    names.add(bits[-1] if " as " in part else bits[0])
    return names


def _useeffect_twoarg_lines(src: str) -> list[int]:
    """Line numbers of `useEffect(` calls that pass a second argument."""
    out: list[int] = []
    for m in re.finditer(r"\buseEffect\s*\(", src):
        i = m.end() - 1
        depth = 0
        args = 0
        saw_token = False
        for j in range(i, len(src)):
            ch = src[j]
            if ch == "(":
                depth += 1
            elif ch == ")":
                depth -= 1
                if depth == 0:
                    if saw_token:
                        args += 1
                    break
            elif ch == "," and depth == 1:
                args += 1
                saw_token = False
            elif not ch.isspace() and depth == 1:
                saw_token = True
        if args >= 2:
            out.append(src.count("\n", 0, m.start()) + 1)
    return out
# A member of a `patch(X.prototype, {...})` body: `get foo()`, `async foo()`, `foo()`, `foo:`.
# Indentation is not part of the pattern - members are located by brace depth instead, because
# an assumed indent width silently matches nothing in a differently formatted file.
JS_PATCH_MEMBER_RE = re.compile(
    r"^\s*(?:(?P<kind>get|set)\s+)?(?:async\s+)?(?P<name>[A-Za-z_$][\w$]*)\s*(?:\(|:)"
)
JS_NEST_OPEN = "{(["
JS_NEST_CLOSE = "})]"


def js_import_targets(src: str) -> dict[str, tuple[str, str]]:
    """Local name -> (module spec, name that module exports), honouring `as` aliases.

    The exported name is what matters for `patch(MessageModel.prototype, ...)`: upstream declares
    the class as `Message`, so looking for `class MessageModel` in the target file finds nothing.
    """
    out: dict[str, tuple[str, str]] = {}
    for m in JS_IMPORT_STMT_RE.finditer(src):
        spec = m.group("spec")
        if default := m.group("default"):
            out[default] = (spec, "default")
        for part in (m.group("named") or "").split(","):
            part = part.strip()
            if not part:
                continue
            original, _, alias = (p.strip() for p in part.partition(" as "))
            if original:
                out[alias or original] = (spec, original)
    return out


def js_import_bindings(src: str) -> dict[str, str]:
    """Local name -> module spec (drops the exported name; see js_import_targets)."""
    return {local: spec for local, (spec, _) in js_import_targets(src).items()}


def js_blank_literals(src: str) -> str:
    """Same text, with comment and string/template contents replaced by spaces.

    Brace counting on raw JS is not safe: a brace inside a string, a regex-ish comment or a
    template literal ends a class body early or never. Length and newlines are preserved so
    offsets and line numbers still line up with the original.
    """
    out = list(src)
    i, n = 0, len(src)
    mode: str | None = None
    while i < n:
        ch = src[i]
        following = src[i + 1] if i + 1 < n else ""
        if mode is None:
            if ch == "/" and following == "/":
                mode, out[i], out[i + 1] = "line", " ", " "
                i += 2
            elif ch == "/" and following == "*":
                mode, out[i], out[i + 1] = "block", " ", " "
                i += 2
            elif ch in "\"'`":
                mode = ch          # keep the quote, blank what is inside
                i += 1
            else:
                i += 1
        elif mode == "line":
            if ch == "\n":
                mode = None
            else:
                out[i] = " "
            i += 1
        elif mode == "block":
            if ch == "*" and following == "/":
                mode, out[i], out[i + 1] = None, " ", " "
                i += 2
            else:
                if ch != "\n":
                    out[i] = " "
                i += 1
        else:                      # inside a string or template literal
            if ch == "\\":
                out[i] = " "
                if following and following != "\n":
                    out[i + 1] = " "
                i += 2
            elif ch == mode:
                mode = None
                i += 1
            else:
                if ch != "\n":
                    out[i] = " "
                i += 1
    return "".join(out)


def js_block_at(blanked: str, brace_pos: int) -> str | None:
    """Text between `brace_pos` (an opening brace) and its match, or None if unbalanced."""
    depth = 0
    for idx in range(brace_pos, len(blanked)):
        if blanked[idx] == "{":
            depth += 1
        elif blanked[idx] == "}":
            depth -= 1
            if depth == 0:
                return blanked[brace_pos + 1:idx]
    return None


def js_class_body(blanked: str, symbol: str) -> tuple[str | None, str | None]:
    """(body, parent class name) for class `symbol`, or (None, None) when it is not found."""
    if symbol == "default":
        header = re.search(r"\bexport\s+default\s+class\b([^{]*)\{", blanked)
    else:
        header = re.search(rf"\bclass\s+{re.escape(symbol)}\b([^{{]*)\{{", blanked)
    if not header:
        return None, None
    parent = None
    if m := re.search(r"\bextends\s+([A-Za-z_$][\w$]*)", header.group(1)):
        parent = m.group(1)
    return js_block_at(blanked, header.end() - 1), parent


def js_own_field_names(body: str) -> set[str]:
    """Instance class fields declared directly in `body` (`name = ...`).

    `static` fields are excluded: they live on the constructor, so they shadow nothing for
    instances. Depth counts every bracket kind, so a field spanning several lines - such as
    `isEmpty = fields.Attr(false, {compute() {...}})` - does not expose its inner lines.
    """
    names: set[str] = set()
    depth = 0
    for line in body.splitlines():
        if depth == 0 and not re.match(r"\s*static\b", line):
            if m := re.match(r"\s*(?:#)?([A-Za-z_$][\w$]*)\s*=\s*(?!=)", line):
                names.add(m.group(1))
        depth = max(0, depth + sum(ch in JS_NEST_OPEN for ch in line)
                    - sum(ch in JS_NEST_CLOSE for ch in line))
    return names


def check_js(repo: str, module: str, target: Target, own_modules: set[str]) -> list[Finding]:
    out: list[Finding] = []
    for full, rel in walk(repo, module, ".js"):
        rel_posix = rel.replace(os.sep, "/")
        if "/tests/" in rel_posix:
            continue
        src = read(full)
        imports: dict[str, str] = {}
        for lineno, line in enumerate(src.splitlines(), 1):
            for spec in JS_IMPORT_RE.findall(line):
                owner = spec.lstrip("@").split("/")[0]
                for name in re.findall(r"[{,]?\s*([A-Za-z_$][\w$]*)", line.split("from")[0]):
                    imports.setdefault(name, spec)
                if owner in own_modules:
                    continue
                if not target.resolve_js(spec):
                    out.append(Finding("js-import", module, rel, lineno,
                                       f"{spec} resolves to no file in odoo or enterprise"))
        # patch() targets whose import is already broken are reported once more,
        # because the failure mode (asset load error) differs from a stale symbol.
        for lineno, line in enumerate(src.splitlines(), 1):
            for sym in JS_PATCH_RE.findall(line):
                spec = imports.get(sym) or imports.get(sym.split(".")[0])
                if not spec:
                    continue
                owner = spec.lstrip("@").split("/")[0]
                if owner in own_modules or target.resolve_js(spec):
                    continue
                out.append(Finding("patch-target", module, rel, lineno,
                                   f"patch({sym}) targets {spec}, which no longer resolves"))
        out += check_patch_shadow(module, rel, src, target, own_modules)
        out += check_js_symbols(module, rel, src, target, own_modules)
        out += check_gone_js_paths(module, rel, src)
    return out


# Static URLs that 19.0 loadJS / loadCSS still hit and that saas-19.4 deleted.
# Distinct from js-import: that kind only sees `@mod/path` specifiers.
GONE_JS_PATHS = {
    "/web/static/lib/jquery/jquery.js": (
        "gone at saas-19.4 (addons/web/static/lib/jquery deleted). "
        "jstree still needs $ — vendor 19.0 jquery next to it "
        "(/<module>/static/lib/jquery/jquery.js) and retarget loadJS. "
        "Do not reintroduce @web/core/ensure_jquery"
    ),
}

# Method calls that left a surviving file. Distinct from js-symbol (named imports).
GONE_JS_CALLS = {
    "._replaceWith(": (
        "StaticList._replaceWith is gone at saas-19.4 (19.0 "
        "static_list.js:1081). Successor: list.set(ids) "
        "(saas static_list.js:455) which applies x2ManyCommands.SET "
        "and _onUpdate. Do not wrap a second mutex — set() already does."
    ),
}

# Data xmlids that left the 19.0 module. view-xmlid only sees inherit_id.
# Include tests: HttpCase setUpClass is where this first raised (20_9 Gx.7).
GONE_XMLIDS = {
    "website.default_website": (
        "gone at saas-19.4 (website/data/website_data.xml). Successor "
        "base.default_website (odoo/addons/base/data/website.xml + "
        "website._ensure_default_website_consistency). Core refs "
        "env.ref('base.default_website')"
    ),
}


def check_gone_js_paths(module: str, rel: str, src: str) -> list[Finding]:
    out: list[Finding] = []
    for lineno, line in enumerate(src.splitlines(), 1):
        stripped = line.lstrip()
        if stripped.startswith("//") or stripped.startswith("*") or stripped.startswith("#"):
            continue
        for path, hint in GONE_JS_PATHS.items():
            if path in line:
                out.append(Finding("js-import", module, rel, lineno, f"{path} {hint}"))
        for token, hint in GONE_JS_CALLS.items():
            if token in line:
                out.append(Finding("js-symbol", module, rel, lineno, f"{token} {hint}"))
    return out


def check_gone_xmlids(repo: str, module: str) -> list[Finding]:
    out: list[Finding] = []
    for full, rel in walk(repo, module, ".py", ".xml", ".js"):
        for lineno, line in enumerate(read(full).splitlines(), 1):
            stripped = line.lstrip()
            if stripped.startswith("#") or stripped.startswith("//"):
                continue
            for xmlid, hint in GONE_XMLIDS.items():
                if xmlid in line:
                    out.append(Finding(
                        "view-xmlid", module, rel, lineno, f"{xmlid} {hint}",
                    ))
    return out


def _named_from_clause(clause: str) -> list[str]:
    names: list[str] = []
    for part in clause.split(","):
        part = part.strip()
        if not part or part == "type":
            continue
        original = part.split(" as ")[0].strip()
        if original:
            names.append(original)
    return names


def check_js_symbols(module: str, rel: str, src: str, target: Target,
                     own_modules: set[str]) -> list[Finding]:
    """Named imports / owl destructures whose export is gone at the target."""
    out: list[Finding] = []
    imported_useeffect_from_owl = False
    for m in JS_IMPORT_STMT_RE.finditer(src):
        spec = m.group("spec")
        if not spec or not spec.startswith("@"):
            continue
        owner = spec.lstrip("@").split("/")[0]
        if owner in own_modules:
            continue
        names = _named_from_clause(m.group("named") or "")
        if spec == "@odoo/owl" and "useEffect" in names:
            imported_useeffect_from_owl = True
        if spec in JS_ALIAS_EXACT:
            continue
        # Path gone is js-import, already reported. Only check symbols on a live file
        # or on the owl alias.
        is_owl = spec == "@odoo/owl" or spec.startswith("@odoo/owl")
        if not is_owl and not target.resolve_js(spec):
            continue
        exported = target.js_exported_names(spec)
        if exported is None:
            continue
        lineno = src.count("\n", 0, m.start()) + 1
        for name in names:
            if name in exported:
                continue
            hint = JS_SYMBOL_HINTS.get((spec, name), "")
            detail = f"{name} is not exported from {spec} at the target"
            if hint:
                detail = f"{name} from {spec}: {hint}"
            out.append(Finding("js-symbol", module, rel, lineno, detail))
    for m in OWL_DESTRUCTURE_RE.finditer(src):
        names = _named_from_clause(m.group(1))
        if "useEffect" in names:
            imported_useeffect_from_owl = True
        exported = target.owl_exports()
        lineno = src.count("\n", 0, m.start()) + 1
        for name in names:
            if name in exported:
                continue
            hint = JS_SYMBOL_HINTS.get(("@odoo/owl", name), "")
            detail = f"{name} is not on owl at the target (`const {{ {name} }} = owl`)"
            if hint:
                detail = f"{name} from owl: {hint}"
            out.append(Finding("js-symbol", module, rel, lineno, detail))
    if imported_useeffect_from_owl:
        for lineno in _useeffect_twoarg_lines(src):
            out.append(Finding(
                "owl-hook", module, rel, lineno,
                "useEffect(fn, deps) from @odoo/owl: OWL 3 useEffect is "
                "useEffect(fn) and ignores the deps array. Use useLayoutEffect "
                "from @web/owl2/utils (compat OWL-2 semantics).",
            ))
    return out


def _owl_template_spans(src: str):
    """Yield `(offset, t-name, t-inherit or '', body)` per OWL `t-name` in `src`."""
    opens = list(OWL_TNAME_OPEN_RE.finditer(src))
    for i, match in enumerate(opens):
        attrs, name = match.group(1), match.group(2)
        inherit_m = OWL_TINHERIT_RE.search(attrs)
        inherit = inherit_m.group(1) if inherit_m else ""
        end = opens[i + 1].start() if i + 1 < len(opens) else len(src)
        yield match.start(), name, inherit, src[match.end():end]


def _owl_sidebar_hint(inherit: str, exact: str) -> str:
    if inherit == "web.CalendarSidePanel" and "o_calendar_sidebar" in exact.split():
        return (
            " saas moved the expanded filters to "
            "o_calendar_sidepanel_content; o_calendar_sidebar is now the "
            "collapsed rail with extra classes. Successor: "
            "//div[hasclass('o_calendar_sidepanel_content')]."
        )
    return ""


def _owl_this_extra_findings(src: str, rel: str, module: str, off: int, body: str, inherit: str) -> list[Finding]:
    """Bare getter / bind / t-on-click idents. OWL 3 compile scope is this.*."""
    out: list[Finding] = []
    where = "t-inherit" if inherit else "OWL"
    for am in OWL_BARE_ATTR_IDENT_RE.finditer(body):
        lineno = src.count("\n", 0, off) + body[:am.start()].count("\n") + 1
        out.append(Finding(
            "owl-this", module, rel, lineno,
            f"{where} template uses bare {am.group(1)!r} as an attribute. "
            f"OWL 3 compile scope is this.{am.group(1)} "
            f"(panelClass / panelStyle / t-on-click=\"clear\").",
        ))
    for bm in OWL_BARE_BIND_RE.finditer(body):
        lineno = src.count("\n", 0, off) + body[:bm.start()].count("\n") + 1
        out.append(Finding(
            "owl-this", module, rel, lineno,
            f"{where} template uses {bm.group(1)!r} without this. on .bind. "
            f"Successor: update.bind=\"this.{bm.group(1)}\" "
            f"(TypeError reading 'bind'; 20_14 rule_parent already prefixes).",
        ))
    for am in OWL_BARE_ARROW_CALL_RE.finditer(body):
        lineno = src.count("\n", 0, off) + body[:am.start()].count("\n") + 1
        out.append(Finding(
            "owl-this", module, rel, lineno,
            f"{where} template calls {am.group(1)}() in a t-on arrow without this. "
            f"Successor: (event) => this.{am.group(1)}(...) "
            f"(Invalid handler expression; 20_5 KPI formula).",
        ))
    return out


def check_owl_templates(repo: str, module: str, target: Target | None = None) -> list[Finding]:
    """OWL t-inherit XPath on @t-ref, OWL-2 named t-ref, dead hasclass(), and dead t-if/t-elif."""
    parent_classes = target.owl_template_classes() if target is not None else {}
    parent_class_strs = target.owl_template_class_strings() if target is not None else {}
    parent_dirs = target.owl_template_directives() if target is not None else {}
    out: list[Finding] = []
    for full, rel in walk(repo, module, ".xml"):
        rel_posix = rel.replace(os.sep, "/")
        if "/static/src/" not in rel_posix:
            continue
        src = read(full)
        for lineno, line in enumerate(src.splitlines(), 1):
            if OWL_XPATH_TREF_RE.search(line):
                out.append(Finding(
                    "owl-xpath", module, rel, lineno,
                    "t-inherit XPath selects @t-ref / @t-esc on a core template. "
                    "saas-19.4 rewrote those to t-custom-ref or t-ref=\"this.x\" "
                    "(web.KanbanRecord article, mail.Message shadowBody). "
                    "Retarget the XPath.",
                ))
            elif OWL_OWN_TREF_RE.search(line) and "xpath" not in line:
                out.append(Finding(
                    "owl-tref", module, rel, lineno,
                    "OWL-2 named t-ref / t-model / t-portal. Compat header: "
                    "t-custom-ref / t-custom-model / t-custom-portal. "
                    "Leftover core t-ref is t-ref=\"this.fooRef\" (OWL 3 signal).",
                ))
        for off, _name, inherit, body in _owl_template_spans(src):
            for bm in OWL_BARE_SCOPE_RE.finditer(body):
                lineno = src.count("\n", 0, off) + body[:bm.start()].count("\n") + 1
                where = "t-inherit" if inherit else "OWL"
                out.append(Finding(
                    "owl-this", module, rel, lineno,
                    f"{where} template uses bare {bm.group(1)}. "
                    f"OWL 3 / saas-19.4 core writes this.{bm.group(1)}. "
                    f"Bare name is undefined (TypeError on .{bm.group(1)}).",
                ))
            for cm in OWL_BARE_CALL_RE.finditer(body):
                lineno = src.count("\n", 0, off) + body[:cm.start()].count("\n") + 1
                where = "t-inherit" if inherit else "OWL"
                out.append(Finding(
                    "owl-this", module, rel, lineno,
                    f"{where} template calls {cm.group(1)}() without this. "
                    f"OWL 3 compile scope is ctx; methods are this.{cm.group(1)}().",
                ))
            out.extend(_owl_this_extra_findings(src, rel, module, off, body, inherit))
            if inherit and inherit in parent_dirs:
                known_dirs = parent_dirs[inherit]
                for doff, tag, attr, val in _owl_position_directive_triples(body):
                    if (tag, attr, val) in known_dirs:
                        continue
                    lineno = src.count("\n", 0, off) + body[:doff].count("\n") + 1
                    hint = ""
                    if attr == "t-elif" and val == "canDownload(attachment)":
                        hint = (
                            " Successor: t-elif=\"this.canDownload(attachment)\" "
                            "(OWL 3 this. on mail.AttachmentList)."
                        )
                    out.append(Finding(
                        "owl-xpath", module, rel, lineno,
                        f"t-inherit {tag} {attr}={val!r} is not on {inherit} at "
                        f"the target.{hint}",
                    ))
            if inherit and inherit in parent_class_strs:
                known_strs = parent_class_strs[inherit]
                for xm in OWL_XPATH_CLASS_RE.finditer(body):
                    exact = xm.group(2)
                    if exact in known_strs:
                        continue
                    lineno = src.count("\n", 0, off) + body[:xm.start()].count("\n") + 1
                    hint = _owl_sidebar_hint(inherit, exact)
                    out.append(Finding(
                        "owl-xpath", module, rel, lineno,
                        f"t-inherit XPath @class={exact!r} is not an exact "
                        f"class=\"…\" on {inherit} at the target.{hint}",
                    ))
                for match in OWL_OPEN_TAG_RE.finditer(body):
                    _tag, attrs = match.group(1), match.group(2)
                    if "position=" not in attrs:
                        continue
                    cm = OWL_CLASS_ATTR_RE.search(attrs)
                    if not cm:
                        continue
                    exact = cm.group(1)
                    if exact in known_strs:
                        continue
                    lineno = src.count("\n", 0, off) + body[:match.start()].count("\n") + 1
                    hint = _owl_sidebar_hint(inherit, exact)
                    out.append(Finding(
                        "owl-xpath", module, rel, lineno,
                        f"t-inherit class={exact!r} position= is not an exact "
                        f"class=\"…\" on {inherit} at the target.{hint}",
                    ))
            if not parent_classes or not inherit or inherit not in parent_classes:
                continue
            known = parent_classes[inherit]
            for hm in OWL_HASCLASS_RE.finditer(body):
                cls = hm.group(1)
                if cls in known:
                    continue
                lineno = src.count("\n", 0, off) + body[:hm.start()].count("\n") + 1
                hint = ""
                if cls == "o-kanban-button-new" and inherit == "web.KanbanView":
                    hint = " Successor: inherit web.KanbanView.Buttons (core did)."
                out.append(Finding(
                    "owl-xpath", module, rel, lineno,
                    f"t-inherit XPath hasclass({cls!r}) is not in {inherit} at "
                    f"the target ref.{hint}",
                ))
    for full, rel in walk(repo, module, ".js"):
        src = read(full)
        for match in OWL_XML_LIT_RE.finditer(src):
            body = match.group(1)
            off = match.start(1)
            for bm in OWL_BARE_SCOPE_RE.finditer(body):
                lineno = src.count("\n", 0, off + bm.start()) + 1
                out.append(Finding(
                    "owl-this", module, rel, lineno,
                    f"xml` template uses bare {bm.group(1)}. "
                    f"OWL 3 compile scope is this.{bm.group(1)} "
                    f"(portal jsTreePortal state.treeData).",
                ))
            for cm in OWL_BARE_CALL_RE.finditer(body):
                lineno = src.count("\n", 0, off + cm.start()) + 1
                out.append(Finding(
                    "owl-this", module, rel, lineno,
                    f"xml` template calls {cm.group(1)}() without this. "
                    f"OWL 3 compile scope is ctx; methods are this.{cm.group(1)}().",
                ))
            out.extend(_owl_this_extra_findings(src, rel, module, off, body, ""))
    return out


def check_qweb_tcall(repo: str, module: str) -> list[Finding]:
    """Inner t-set of a t-call is the slot only at saas-19.4."""
    out: list[Finding] = []
    for full, rel in walk(repo, module, ".xml"):
        rel_posix = rel.replace(os.sep, "/")
        if "/static/" in rel_posix:
            continue
        src = read(full)
        for match in QWEB_TCALL_INNER_SET_RE.finditer(src):
            lineno = src.count("\n", 0, match.start()) + 1
            out.append(Finding(
                "qweb-tcall", module, rel, lineno,
                f"t-call {match.group(1)!r} inner t-set={match.group(2)!r} "
                f"does not reach the callee (saas-19.4 dropped "
                f"is_deprecated_version). Successor: t-call attribute "
                f"({match.group(2)}=\"True\") or a controller / sibling t-set. "
                f"sale portal writes breadcrumbs_searchbar=\"True\".",
            ))
    return out


def _http_import_names(clause: str) -> list[str]:
    clause = clause.strip()
    if clause.startswith("("):
        clause = clause.strip("()")
    names = []
    for part in clause.split(","):
        tok = part.strip().split("#", 1)[0].strip()
        if tok:
            names.append(tok.split()[0])
    return names


TOOLS_ORMCACHE_RE = re.compile(r"tools\.ormcache\s*\(")
REQUEST_WEBSITE_RE = re.compile(r"request\.website\b")
CALENDAR_DATE_DELAY_RE = re.compile(
    r"<calendar\b[^>]*\bdate_delay\s*=",
    re.IGNORECASE,
)


QWEB_TESC_RE = re.compile(r"""\bt-(?:esc|raw)\s*=""")


def check_qweb_tesc(repo: str, module: str) -> list[Finding]:
    """t-esc/t-raw in ir.ui.view arch is forbidden at saas-19.4."""
    out: list[Finding] = []
    for full, rel in walk(repo, module, ".xml"):
        if "/static/" in rel.replace(os.sep, "/"):
            continue
        src = read(full)
        for match in QWEB_TESC_RE.finditer(src):
            lineno = src.count("\n", 0, match.start()) + 1
            out.append(Finding(
                "qweb-tesc", module, rel, lineno,
                "t-esc/t-raw in ir.ui.view arch is forbidden "
                "(_validate_qweb_directive). Use t-out. OWL static/src "
                "templates may keep t-esc.",
            ))
    return out


def check_calendar_attrs(repo: str, module: str) -> list[Finding]:
    """<calendar date_delay> is gone from RNG + arch parser at saas-19.4."""
    out: list[Finding] = []
    for full, rel in walk(repo, module, ".xml"):
        if "/static/" in rel.replace(os.sep, "/"):
            continue
        src = read(full)
        for match in CALENDAR_DATE_DELAY_RE.finditer(src):
            lineno = src.count("\n", 0, match.start()) + 1
            out.append(Finding(
                "calendar-attr", module, rel, lineno,
                "<calendar date_delay=...> is gone at saas-19.4 "
                "(calendar_view.rng + FIELD_ATTRIBUTE_NAMES). "
                "Drop the attribute; keep date_start / date_stop.",
            ))
    return out


def check_python_api(repo: str, module: str) -> list[Finding]:
    out: list[Finding] = []
    pats = {name: re.compile(rf"\.{re.escape(name)}\s*\(") for name in REMOVED_PYTHON_CALLS}
    for full, rel in walk(repo, module, ".py"):
        src = read(full)
        for lineno, line in enumerate(src.splitlines(), 1):
            stripped = line.lstrip()
            if stripped.startswith("#"):
                continue
            for name, why in REMOVED_PYTHON_CALLS.items():
                if pats[name].search(line):
                    out.append(Finding("python-api", module, rel, lineno,
                                       f"{name}(): {why}"))
            if TOOLS_ORMCACHE_RE.search(line):
                out.append(Finding(
                    "python-api", module, rel, lineno,
                    "tools.ormcache: deprecated Since 20.0; use @api.ormcache(...).",
                ))
            if REQUEST_WEBSITE_RE.search(line):
                out.append(Finding(
                    "python-api", module, rel, lineno,
                    "request.website is gone; saas-19.4 uses request.env.website "
                    "(ir_http no longer assigns request.website). Observed 20_9 "
                    "Gx.7 AttributeError on jsonrpc website=True routes.",
                ))
        for m in HTTP_FROM_RE.finditer(src):
            lineno = src.count("\n", 0, m.start()) + 1
            for name in _http_import_names(m.group(1)):
                if name in HTTP_PACKAGE_MOVED:
                    out.append(Finding(
                        "python-api", module, rel, lineno,
                        f"from odoo.http import {name}: saas-19.4 http is a package and "
                        f"does not re-export this name. {HTTP_PACKAGE_MOVED[name]}",
                    ))
    return out


def check_patch_shadow(module: str, rel: str, src: str, target: Target,
                       own_modules: set[str]) -> list[Finding]:
    """Prototype patches of members upstream declares as class fields.

    Such a member is an own property of every instance, so the prototype entry is shadowed and
    never runs - no error, no warning, on any serie (rule 22, `MessageModel.isEmpty`).
    """
    out: list[Finding] = []
    targets = js_import_targets(src)
    blanked = js_blank_literals(src)
    for m in JS_PROTO_PATCH_RE.finditer(blanked):
        sym = m.group(1)
        spec, exported = targets.get(sym, (None, None))
        if not spec or spec.lstrip("@").split("/")[0] in own_modules:
            continue
        fields_ = target.js_class_fields(spec, exported)
        if not fields_:
            continue
        brace = blanked.find("{", m.end() - 1)
        body = js_block_at(blanked, brace) if brace != -1 else None
        if body is None:
            continue
        first_body_line = blanked.count("\n", 0, brace + 1) + 1
        depth = 0
        for offset, body_line in enumerate(body.splitlines()):
            if depth == 0 and (mm := JS_PATCH_MEMBER_RE.match(body_line)):
                if mm.group("name") in fields_:
                    kind = mm.group("kind")
                    shape = f"{kind} " if kind else ""
                    out.append(Finding(
                        "patch-shadow", module, rel, first_body_line + offset,
                        f"{shape}{mm.group('name')} is a class field on {exported} "
                        f"({spec}) - an own instance property shadows this prototype entry, "
                        f"so it never runs"))
            depth = max(0, depth + sum(ch in JS_NEST_OPEN for ch in body_line)
                        - sum(ch in JS_NEST_CLOSE for ch in body_line))
    return out


INHERIT_REF_RE = re.compile(r'name="inherit_id"\s+ref="([\w.]+)"')
CARD_ID_RE = re.compile(r"""card_id=["']%\(([\w.]+)\)d["']""")


def _parent_arch_blob(target: Target, xids: list[str]) -> str:
    """Inherited view record plus `card_id` / inherit_id chain (depth-capped)."""
    seen: set[str] = set()
    parts: list[str] = []

    def add(xid: str, depth: int = 0) -> None:
        if depth > 8 or xid in seen:
            return
        seen.add(xid)
        rec = target.view_record_src(xid)
        if not rec:
            return
        parts.append(rec)
        for card in CARD_ID_RE.findall(rec):
            add(card, depth + 1)
        parent_mod = xid.split(".")[0] if "." in xid else ""
        for href in INHERIT_REF_RE.findall(rec):
            full = href if "." in href else (
                f"{parent_mod}.{href}" if parent_mod else href
            )
            if "." in full:
                add(full, depth + 1)

    for xid in xids:
        add(xid)
    return "\n".join(parts)


def _anchor_in_parent(blob: str, anchor: str) -> bool:
    return (
        f'name="{anchor}"' in blob
        or f"name='{anchor}'" in blob
        or f'id="{anchor}"' in blob
        or f"id='{anchor}'" in blob
    )


def check_views(repo: str, module: str, target: Target, own_modules: set[str]) -> list[Finding]:
    out: list[Finding] = []
    known = target.view_xmlids()
    for full, rel in walk(repo, module, ".xml"):
        rel_posix = rel.replace(os.sep, "/")
        if "/static/" in rel_posix:
            continue
        src = read(full)
        for lineno, line in enumerate(src.splitlines(), 1):
            for xid in INHERIT_REF_RE.findall(line) + TEMPLATE_INHERIT_RE.findall(line):
                if "." not in xid:
                    continue
                if xid.split(".")[0] in own_modules:
                    continue
                if xid not in known:
                    out.append(Finding("view-xmlid", module, rel, lineno,
                                       f"inherit_id ref {xid} does not exist at the target ref"))
    return out


RECORD_BLOCK_RE = re.compile(r"<record\b.*?</record>", re.S)
TEMPLATE_BLOCK_RE = re.compile(r"<template\b.*?</template>", re.S)
TEMPLATE_INHERIT_RE = re.compile(r'\binherit_id="([\w.]+)"')
XPATH_EXPR_RE = re.compile(r'expr="([^"]*)"')
EXPR_NAME_RE = re.compile(r"""@(?:name|id)\s*=\s*['"]([^'"]+)['"]""")
ID_ATTR_RE = re.compile(r'\bid="([^"]+)"')
OPEN_TAG_RE = re.compile(r"<([a-zA-Z_][\w.-]*)\b([^>]*)>", re.S)
NAME_ATTR_RE = re.compile(r'\bname="([^"]+)"')


def _view_anchors(block: str):
    """(offset, name) for every node this inherit block *targets*.

    Two forms, both unambiguous: a `@name=` / `@id=` predicate inside an `xpath` `expr`,
    and a tag carrying `position=` (its `name` or `id` is the anchor). Nodes we merely
    *add* have no `position`, so they are not anchors - and `position="attributes"`
    children (`<attribute name="invisible">`) are not either. `id=` is load-bearing:
    saas-19.4 dropped `portal_service_category` and the inherit used
    `<div id="…" position="inside">`, which a name-only scan missed.
    """
    for m in XPATH_EXPR_RE.finditer(block):
        for anchor in EXPR_NAME_RE.findall(m.group(1)):
            yield m.start(), anchor
    for m in OPEN_TAG_RE.finditer(block):
        attrs = m.group(2)
        if "position=" not in attrs:
            continue
        named = NAME_ATTR_RE.search(attrs)
        if named:
            yield m.start(), named.group(1)
        ided = ID_ATTR_RE.search(attrs)
        if ided:
            yield m.start(), ided.group(1)


def check_view_anchors(repo: str, module: str, target: Target,
                      own_modules: set[str]) -> list[Finding]:
    """Inherit anchors that exist in no view at the target ref.

    A **signal, not proof**, in both directions. The name is looked up across all target
    XML, so an anchor that merely moved to another model's view is a miss; and a name
    present only in a Python-built arch would be a false positive. What it does catch is
    the class that bit `complementary_lead_data`: `crm`'s `group name="lead_priority"`
    vanished when saas-19.4 merged the lead and opportunity sidebars, and no other check
    sees it (the view still exists, so `view-xmlid` is clean, and nothing raises until
    install).
    """
    known = target.view_node_names()
    out: list[Finding] = []
    for full, rel in walk(repo, module, ".xml"):
        rel_posix = rel.replace(os.sep, "/")
        if "/static/" in rel_posix:
            continue
        src = read(full)
        for block_re in (RECORD_BLOCK_RE, TEMPLATE_BLOCK_RE):
            for block in block_re.finditer(src):
                refs = INHERIT_REF_RE.findall(block.group(0))
                refs += TEMPLATE_INHERIT_RE.findall(block.group(0))
                foreign = [r for r in refs if "." in r
                           and r.split(".")[0] not in own_modules]
                if not foreign:
                    continue
                parent_blob = _parent_arch_blob(target, foreign)
                for off, anchor in _view_anchors(block.group(0)):
                    if parent_blob:
                        if _anchor_in_parent(parent_blob, anchor):
                            continue
                        hint = (
                            f"anchor name/id={anchor!r} is absent from the inherited "
                            f"view(+card_id) arch ({', '.join(foreign)}). A global "
                            f"name hit is not enough — saas project.view_task_kanban "
                            f"kept the xmlid but moved priority onto view_task_card."
                        )
                    elif anchor in known:
                        continue
                    else:
                        hint = (
                            f"anchor name/id={anchor!r} exists in no view at the target ref "
                            f"(inherits {', '.join(foreign)}). Read the target arch: the node was "
                            f"renamed, merged away, or moved."
                        )
                    lineno = src.count("\n", 0, block.start() + off) + 1
                    out.append(Finding(
                        "view-anchor", module, rel, lineno, hint,
                    ))
    return out


def check_security_models(repo: str, module: str, target: Target) -> list[Finding]:
    """Data files declaring a security model that no longer exists (rule 22).

    Loud, not silent - the install dies with `KeyError: 'ir.rule'` - but it dies on the
    first file, so a matrix run reports one module at a time. This lists every site up
    front. Gated on the target actually having dropped the model.
    """
    gone = {old: new for old, (new, _why) in RENAMED_SECURITY_MODELS.items()
            if not target.model_known(old) and target.model_known(new)}
    if not gone:
        return []
    out: list[Finding] = []
    for full, rel in walk(repo, module, ".xml", ".csv"):
        rel_posix = rel.replace(os.sep, "/")
        if "/static/" in rel_posix:
            continue
        stem = os.path.basename(rel_posix)[: -len(".csv")]
        if rel_posix.endswith(".csv"):
            if stem in gone:
                new, why = RENAMED_SECURITY_MODELS[stem]
                out.append(Finding("security-model", module, rel, 1,
                                   f"{stem} does not exist at the target ref (now {new}): {why}"))
            continue
        for lineno, line in enumerate(read(full).splitlines(), 1):
            for old in gone:
                if re.search(rf"""model=["']{re.escape(old)}["']""", line):
                    new, why = RENAMED_SECURITY_MODELS[old]
                    out.append(Finding("security-model", module, rel, lineno,
                                       f"{old} does not exist at the target ref (now {new}): {why}"))
    return out


# saas ir.access: empty domain on a permission → Domain.TRUE, then
# Domain.OR(permissions) & Domain.AND(restrictions) (ir_access.py:308 / :355).
# 19.0 ir.model.access had no record filter; a leftover empty ACL therefore
# swallows every grouped domain on that model. An explicit [(1, '=', 1)] is
# intentional (19.0 TRUE rules) and is not this kind. Restrictions (no
# group_id) AND and are safe next to an empty ACL.
_ACCESS_RECORD_RE = re.compile(
    r"<record\b([^>]*)>(.*?)</record>",
    re.DOTALL | re.IGNORECASE,
)
_ACCESS_ATTR_RE = re.compile(r"""\b(id|model)=["']([^"']+)["']""", re.I)
_ACCESS_FIELD_RE = re.compile(
    r"<field\b([^>]*?)\s*/>|<field\b([^>]*)>(.*?)</field>",
    re.DOTALL | re.IGNORECASE,
)
_ACCESS_FIELD_ATTR_RE = re.compile(r"""\b(name|ref)=["']([^"']+)["']""", re.I)
_ACCESS_TRUE_DOMAIN_RE = re.compile(
    r"\[\s*\(\s*1\s*,\s*['\"]=(?:=)?['\"]\s*,\s*1\s*\)\s*\]",
)


# saas ir_access.py CRUD_SELECTION keys at pin 3630379f63633612e5a9e8d435deecbe26eaa15a.
# Letters stay in crud order: 19.0 read+create is `cr`, not `rc` (20_10 Gx.6).
ACCESS_OPERATIONS = frozenset({
    "crud", "cru", "crd", "cud", "rud",
    "cr", "cu", "cd", "ru", "rd", "ud",
    "c", "r", "u", "d",
})


def _access_ops(operation: str) -> set[str]:
    return set(operation or "") & set("crud")


def _access_domain_kind(raw: str) -> str:
    text = (raw or "").strip()
    if not text or text in {"False", "[]"}:
        return "empty"
    compact = re.sub(r"\s+", "", text)
    if _ACCESS_TRUE_DOMAIN_RE.fullmatch(compact):
        return "true"
    return "real"


def _access_model_from_ref(ref: str) -> str:
    name = (ref or "").split(".")[-1]
    if name.startswith("model_"):
        return name[len("model_"):].replace("_", ".")
    return name


def _iter_ir_access_xml(src: str, rel: str):
    for match in _ACCESS_RECORD_RE.finditer(src):
        attrs = {k.lower(): v for k, v in _ACCESS_ATTR_RE.findall(match.group(1))}
        if attrs.get("model") != "ir.access":
            continue
        fields: dict[str, tuple[str, str]] = {}
        for field in _ACCESS_FIELD_RE.finditer(match.group(2)):
            raw_attrs = field.group(1) if field.group(1) is not None else field.group(2)
            fattrs = {k.lower(): v for k, v in _ACCESS_FIELD_ATTR_RE.findall(raw_attrs or "")}
            name = fattrs.get("name")
            if not name:
                continue
            fields[name] = (fattrs.get("ref", ""), (field.group(3) or "").strip())
        model_ref = fields.get("model_id", ("", ""))[0]
        group_ref = fields.get("group_id", ("", ""))[0]
        operation = fields.get("operation", ("", ""))[1]
        domain = fields.get("domain", ("", ""))[1]
        if not model_ref or not operation:
            continue
        yield {
            "id": attrs.get("id", ""),
            "model": _access_model_from_ref(model_ref),
            "group": group_ref,
            "operation": operation,
            "ops": _access_ops(operation),
            "kind": _access_domain_kind(domain),
            "domain": domain,
            "path": rel,
            "line": src[: match.start()].count("\n") + 1,
        }


def _iter_ir_access_csv(src: str, rel: str):
    rows = src.splitlines()
    header = None
    header_idx = None
    for idx, line in enumerate(rows):
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        header = next(csv.reader([line]))
        header_idx = idx
        break
    if not header:
        return
    index = {name.strip(): i for i, name in enumerate(header)}
    model_i = index.get("model_id")
    group_i = index.get("group_id/id", index.get("group_id:id"))
    op_i = index.get("operation")
    domain_i = index.get("domain")
    id_i = index.get("id")
    if model_i is None or op_i is None:
        return
    for lineno, line in enumerate(rows[header_idx + 1 :], header_idx + 2):
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        cols = next(csv.reader([line]))
        if len(cols) <= max(model_i, op_i):
            continue
        group = cols[group_i].strip() if group_i is not None and group_i < len(cols) else ""
        domain = cols[domain_i].strip() if domain_i is not None and domain_i < len(cols) else ""
        operation = cols[op_i].strip()
        yield {
            "id": cols[id_i].strip() if id_i is not None and id_i < len(cols) else "",
            "model": cols[model_i].strip(),
            "group": group,
            "operation": operation,
            "ops": _access_ops(operation),
            "kind": _access_domain_kind(domain),
            "domain": domain,
            "path": rel,
            "line": lineno,
        }


def _module_overrides_access_domain(repo: str, module: str, model: str) -> bool:
    """True when this module defines `_access_domain` on `model`."""
    needle_inherit = re.compile(
        rf"""_inherit\s*=\s*(?:\[[^\]]*['"]{re.escape(model)}['"]|['"]{re.escape(model)}['"])"""
    )
    for full, rel in walk(repo, module, ".py"):
        if "/tests/" in rel.replace(os.sep, "/"):
            continue
        src = read(full)
        if needle_inherit.search(src) and re.search(r"def\s+_access_domain\s*\(", src):
            return True
    return False


def _target_empty_permissions(target: "Target") -> dict[str, list[dict]]:
    """Empty grouped ir.access rows in core/enterprise, keyed by model."""
    cached = getattr(target, "_empty_permissions", None)
    if cached is not None:
        return cached
    out: dict[str, list[dict]] = defaultdict(list)
    for tree in target.trees:
        for path in tree.paths:
            if not path.endswith("security/ir.access.csv"):
                continue
            src = tree.show(path)
            if not src:
                continue
            for row in _iter_ir_access_csv(src, f"{tree.label}:{path}"):
                if row["group"] and row["kind"] == "empty" and row["model"]:
                    out[row["model"]].append(row)
    target._empty_permissions = out
    return out


def check_access_op(repo: str, module: str) -> list[Finding]:
    """`ir.access.operation` must be a CRUD_SELECTION key (rule 22)."""
    out: list[Finding] = []
    for full, rel in walk(repo, module, ".xml", ".csv"):
        rel_posix = rel.replace(os.sep, "/")
        if "/static/" in rel_posix:
            continue
        src = read(full)
        rows: list[dict] = []
        if rel_posix.endswith(".csv"):
            if os.path.basename(rel_posix) != "ir.access.csv":
                continue
            rows = list(_iter_ir_access_csv(src, rel))
        else:
            rows = list(_iter_ir_access_xml(src, rel))
        for row in rows:
            op = row.get("operation") or ""
            if op in ACCESS_OPERATIONS:
                continue
            out.append(Finding(
                "access-op", module, row["path"], row["line"],
                f"operation={op!r} is not a saas ir.access CRUD_SELECTION key "
                f"(letters stay in crud order: read+create is cr, not rc). "
                f"Valid: {', '.join(sorted(ACCESS_OPERATIONS, key=lambda s: (-len(s), s)))}.",
            ))
    return out


def check_access_or(repo: str, module: str, target: "Target | None" = None) -> list[Finding]:
    """Empty grouped ir.access ORs away a sibling domain (rule 22)."""
    rows: list[dict] = []
    for full, rel in walk(repo, module, ".xml", ".csv"):
        rel_posix = rel.replace(os.sep, "/")
        if "/static/" in rel_posix:
            continue
        src = read(full)
        if rel_posix.endswith(".csv"):
            if os.path.basename(rel_posix) != "ir.access.csv":
                continue
            rows.extend(_iter_ir_access_csv(src, rel))
        else:
            rows.extend(_iter_ir_access_xml(src, rel))

    by_model: dict[str, list[dict]] = defaultdict(list)
    for row in rows:
        if row["model"]:
            by_model[row["model"]].append(row)

    out: list[Finding] = []
    for model, items in sorted(by_model.items()):
        permissions = [item for item in items if item["group"]]
        real = [item for item in permissions if item["kind"] == "real"]
        if not real:
            continue
        for empty in permissions:
            if empty["kind"] != "empty":
                continue
            sibling = next(
                (item for item in real if item["ops"] & empty["ops"]),
                None,
            )
            if sibling is None:
                continue
            out.append(Finding(
                "access-or", module, empty["path"], empty["line"],
                f"grouped {empty['id'] or empty['group']} on {model} "
                f"has an empty domain; saas ORs permissions and empty is "
                f"Domain.TRUE, so it hides {sibling['id'] or sibling['group']} "
                f"({sibling['path']}:{sibling['line']}). Put that domain on "
                f"this row, drop the empty ACL if a same-group domain "
                f"permission already covers the ops, or write [(1, '=', 1)] "
                f"if 19.0 had an intentional all-records rule.",
            ))
        if target is None:
            continue
        if _module_overrides_access_domain(repo, module, model):
            continue
        sibling = real[0]
        for empty in _target_empty_permissions(target).get(model, ()):
            if not (empty["ops"] & sibling["ops"]):
                continue
            out.append(Finding(
                "access-or", module, empty["path"], empty["line"],
                f"core/enterprise {empty['id'] or empty['group']} on {model} "
                f"has an empty domain; saas ORs permissions so it hides "
                f"{sibling['id'] or sibling['group']} "
                f"({sibling['path']}:{sibling['line']}). Inherit that xmlid "
                f"and put the domain on it (only if the other module is a "
                f"hard depend), or AND the filter in `_access_domain` "
                f"(skip Super). Narrowing only this module's rows is not "
                f"enough — sale_stock location was the 20_6 hole.",
            ))
    return out


def _is_internal_user_group(group: str) -> bool:
    return group == "base.group_user" or group.endswith(".base.group_user")


def check_access_grant(repo: str, module: str) -> list[Finding]:
    """base.group_user write + product-group ACL is a 19.0 rule grant (rule 22)."""
    rows: list[dict] = []
    for full, rel in walk(repo, module, ".xml", ".csv"):
        rel_posix = rel.replace(os.sep, "/")
        if "/static/" in rel_posix:
            continue
        src = read(full)
        if rel_posix.endswith(".csv"):
            if os.path.basename(rel_posix) != "ir.access.csv":
                continue
            rows.extend(_iter_ir_access_csv(src, rel))
        else:
            rows.extend(_iter_ir_access_xml(src, rel))

    by_model: dict[str, list[dict]] = defaultdict(list)
    for row in rows:
        if row["model"] and row["group"]:
            by_model[row["model"]].append(row)

    out: list[Finding] = []
    for model, items in sorted(by_model.items()):
        product = [item for item in items if not _is_internal_user_group(item["group"])]
        if not product:
            continue
        for row in items:
            if not _is_internal_user_group(row["group"]):
                continue
            if not (row["ops"] & set("cud")):
                continue
            sibling = product[0]
            out.append(Finding(
                "access-grant", module, row["path"], row["line"],
                f"grouped {row['id'] or row['group']} on {model} is "
                f"base.group_user with write ops {''.join(sorted(row['ops']))}; "
                f"19.0 ir.rule on Internal User did not grant ACL. "
                f"A product-group row already exists "
                f"({sibling['id'] or sibling['group']} at "
                f"{sibling['path']}:{sibling['line']}). Move the domain onto "
                f"that group and copy the 19.0 ACL operations (usually r).",
            ))
    return out


def _manifest_version(src: str) -> tuple[str | None, int]:
    """(`version` string, lineno) from a module `__manifest__.py`.

    Walks the module-level dict. `ast.literal_eval` cannot see comments, which
    the port exception writes next to the version.
    """
    try:
        tree = ast.parse(src)
    except SyntaxError:
        return None, 1
    for stmt in tree.body:
        node = stmt.value if isinstance(stmt, ast.Expr) else None
        if not isinstance(node, ast.Dict):
            continue
        for key, val in zip(node.keys, node.values):
            if isinstance(key, ast.Constant) and key.value == "version":
                if isinstance(val, ast.Constant) and isinstance(val.value, str):
                    return val.value, val.lineno
        break
    return None, 1


def check_manifest_version(repo: str, module: str, target: Target) -> list[Finding]:
    """Serie-prefixed versions are uninstallable on a saas stand-in (rule 22).

    `check_version` compares to `release.major_version`. On saas-19.4 that is
    `saas~19.4`, so both `19.0.x` and `20.0.x` become installable=False. Only
    runs when `--odoo-ref` names a saas branch: on real 20.0 the prefix comes
    back at Fx.
    """
    if "saas-" not in target.odoo.ref:
        return []
    rel = os.path.join(module, "__manifest__.py")
    src = read(os.path.join(repo, rel))
    version, lineno = _manifest_version(src)
    if not version:
        return []
    parts = version.split(".")
    if len(parts) >= 4 and parts[0].isdigit() and parts[1] == "0":
        return [Finding(
            "manifest-version", module, rel, lineno,
            f"{version!r} is serie-prefixed; on a saas stand-in check_version "
            f"sets installable=False. Drop the prefix (→ {'.'.join(parts[2:])}), "
            f"re-prefix at Fx / phase 8.",
        )]
    return []


def check_field_literals(repo: str, module: str) -> list[Finding]:
    out: list[Finding] = []
    pats = {name: re.compile(rf"""["']{re.escape(name)}["']""") for name in REMOVED_FIELD_LITERALS}
    attr = {name: re.compile(rf"\.{re.escape(name)}\b(?!_)") for name in REMOVED_FIELD_LITERALS}
    for full, rel in walk(repo, module, ".py", ".xml"):
        rel_posix = rel.replace(os.sep, "/")
        if "/tests/" in rel_posix:
            continue
        for lineno, line in enumerate(read(full).splitlines(), 1):
            for name, why in REMOVED_FIELD_LITERALS.items():
                if pats[name].search(line) or attr[name].search(line):
                    out.append(Finding("field-lit", module, rel, lineno,
                                       f"{name!r}: {why}"))
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description="Odoo 19 -> 20 mechanical port checks (rule 22)")
    ap.add_argument("--repo", required=True, help="addons repo being ported (tools, system, ...)")
    ap.add_argument("--odoo", required=True)
    ap.add_argument("--odoo-ref", default="origin/saas-19.4")
    ap.add_argument("--odoo-base-ref", default="origin/19.0",
                    help="serie being ported FROM; lets the hook check tell a fresh removal "
                         "from an override that was already dead (pass empty to disable)")
    ap.add_argument("--enterprise")
    ap.add_argument("--enterprise-ref", default="origin/saas-19.4")
    ap.add_argument("--enterprise-base-ref", default="origin/19.0")
    ap.add_argument("--modules", help="comma-separated subset")
    ap.add_argument("--only", help="comma-separated check kinds "
                                   "(dead-hook,stale-override,js-import,js-symbol,"
                                   "owl-xpath,owl-tref,owl-this,owl-hook,python-api,patch-target,"
                                   "patch-shadow,view-xmlid,view-anchor,qweb-tcall,security-model,"
                                   "access-or,access-grant,access-op,field-lit,manifest-version,calendar-attr,qweb-tesc)")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--quiet", action="store_true", help="only print findings")
    args = ap.parse_args()

    odoo = Tree(args.odoo, args.odoo_ref, "odoo")
    ent = Tree(args.enterprise, args.enterprise_ref, "enterprise") if args.enterprise else None
    if ent is None and not args.quiet:
        log("WARNING: --enterprise not given; enterprise-only imports and views "
            "will be reported as missing.")
    target = Target(odoo, ent)

    base = None
    if args.odoo_base_ref:
        base_ent = (Tree(args.enterprise, args.enterprise_base_ref, "enterprise-base")
                    if args.enterprise else None)
        base = Target(Tree(args.odoo, args.odoo_base_ref, "odoo-base"), base_ent)

    wanted = [m.strip() for m in args.modules.split(",")] if args.modules else None
    modules = discover_modules(args.repo, wanted)
    own = set(discover_modules(args.repo, None))
    kinds = {k.strip() for k in args.only.split(",")} if args.only else None
    want = kinds or {
        "dead-hook", "stale-override", "js-import", "js-symbol", "owl-xpath",
        "owl-tref", "owl-this", "owl-hook", "python-api", "patch-target", "patch-shadow",
        "view-xmlid", "view-anchor", "qweb-tcall", "security-model", "access-or",
        "access-grant", "access-op", "field-lit",
        "manifest-version", "calendar-attr", "qweb-tesc",
    }

    if not args.quiet:
        log(f"repo        {args.repo} ({len(modules)} module(s))")
        log(f"odoo        {args.odoo} @ {args.odoo_ref}")
        log(f"enterprise  {args.enterprise} @ {args.enterprise_ref}" if ent else "enterprise  (none)")
        log(f"base        {args.odoo_base_ref}" if base else "base        (none - hook check "
            "cannot classify removals)")
        log()

    # Inheritance graph over EVERY module in the repo, not just the subset under test:
    # a chain through a sibling module must resolve even with --modules.
    # Skip the scan when --only does not include hook kinds (js-symbol-only runs
    # used to wait on this for no reason).
    repo_models = (RepoModels(args.repo, sorted(own))
                   if want & {"dead-hook", "stale-override"} else None)

    findings: list[Finding] = []
    for module in modules:
        fs: list[Finding] = []
        if want & {"dead-hook", "stale-override"}:
            fs += check_dead_hooks(args.repo, module, target, repo_models, base)
        if want & {"js-import", "js-symbol", "owl-hook", "patch-target", "patch-shadow"}:
            fs += check_js(args.repo, module, target, own)
        if want & {"owl-xpath", "owl-tref", "owl-this"}:
            fs += check_owl_templates(args.repo, module, target)
        if "python-api" in want:
            fs += check_python_api(args.repo, module)
        if "view-xmlid" in want:
            fs += check_views(args.repo, module, target, own)
            fs += check_gone_xmlids(args.repo, module)
        if "view-anchor" in want:
            fs += check_view_anchors(args.repo, module, target, own)
        if "qweb-tcall" in want:
            fs += check_qweb_tcall(args.repo, module)
        if "security-model" in want:
            fs += check_security_models(args.repo, module, target)
        if "access-or" in want:
            fs += check_access_or(args.repo, module, target)
        if "access-grant" in want:
            fs += check_access_grant(args.repo, module)
        if "access-op" in want:
            fs += check_access_op(args.repo, module)
        if "field-lit" in want:
            fs += check_field_literals(args.repo, module)
        if "manifest-version" in want:
            fs += check_manifest_version(args.repo, module, target)
        if "calendar-attr" in want:
            fs += check_calendar_attrs(args.repo, module)
        if "qweb-tesc" in want:
            fs += check_qweb_tesc(args.repo, module)
        if kinds:
            fs = [f for f in fs if f.kind in kinds]
        findings += fs

    if args.json:
        print(json.dumps([f.as_dict() for f in findings], indent=2))
    else:
        by_kind: dict[str, list[Finding]] = defaultdict(list)
        for f in findings:
            by_kind[f.kind].append(f)
        for kind in ("dead-hook", "js-import", "js-symbol", "owl-xpath", "owl-tref",
                     "owl-this", "owl-hook", "python-api", "patch-target", "patch-shadow", "view-xmlid",
                     "view-anchor", "qweb-tcall", "qweb-tesc", "calendar-attr", "security-model",
                     "access-or", "access-grant", "access-op", "field-lit",
                     "manifest-version", "stale-override"):
            group = by_kind.get(kind)
            if not group:
                continue
            log(f"{'=' * 78}\n{kind}  ({len(group)})\n{'=' * 78}")
            for f in group:
                log(f"  {f.path}:{f.line}")
                log(f"      {f.detail}")
            log()
        if not findings and not args.quiet:
            log("no findings")
        elif findings:
            log(f"{len(findings)} finding(s). A clean run is a precondition, not proof of a "
                f"working port - runtime gates still apply (rule 22).")
    return 1 if findings else 0


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
"""Generate .cursor/rules/*.mdc and AGENTS.md from src/*.md (+ optional overrides/).

Usage:
  python3 tools/sync_rules.py          # write generated files
  python3 tools/sync_rules.py --check  # exit 1 if generated output would drift
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = REPO_ROOT / "src"
OVERRIDES_DIR = REPO_ROOT / "overrides"
OUT_RULES = REPO_ROOT / ".cursor" / "rules"
AGENTS_PATH = REPO_ROOT / "AGENTS.md"

FRONTMATTER_RE = re.compile(r"^---\n(.*?)\n---\n(.*)$", re.DOTALL)


def parse_md(path: Path) -> tuple[dict[str, str], str]:
    text = path.read_text(encoding="utf-8")
    m = FRONTMATTER_RE.match(text)
    if not m:
        raise SystemExit(f"{path}: missing YAML frontmatter")
    meta: dict[str, str] = {}
    for line in m.group(1).splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if ":" not in line:
            raise SystemExit(f"{path}: bad frontmatter line: {line!r}")
        key, val = line.split(":", 1)
        meta[key.strip()] = val.strip().strip("\"'")
    body = m.group(2).lstrip("\n")
    return meta, body


def load_sources() -> list[tuple[str, dict[str, str], str]]:
    if not SRC_DIR.is_dir():
        raise SystemExit(f"missing {SRC_DIR}")
    items: list[tuple[str, dict[str, str], str]] = []
    for path in sorted(SRC_DIR.glob("*.md")):
        meta, body = parse_md(path)
        rid = meta.get("id") or path.stem
        # Optional override: overrides/<id>.md replaces body (keeps meta from src)
        override = OVERRIDES_DIR / f"{rid}.md"
        if override.is_file():
            ometa, obody = parse_md(override)
            body = obody
            meta = {**meta, **{k: v for k, v in ometa.items() if k != "id"}}
        items.append((rid, meta, body))
    return items


def render_mdc(meta: dict[str, str], body: str) -> str:
    apply = meta.get("apply", "agent")
    always = "true" if apply == "always" else "false"
    description = meta.get("description", meta.get("id", "rule"))
    lines = [
        "---",
        f"description: {description}",
        f"alwaysApply: {always}",
        "---",
        "",
        body.rstrip() + "\n",
    ]
    return "\n".join(lines)


def render_agents(items: list[tuple[str, dict[str, str], str]]) -> str:
    parts = [
        f"# {REPO_ROOT.name}",
        "",
        "Generated from `src/*.md` by `tools/sync_rules.py`. Do not edit by hand.",
        "",
    ]
    for rid, meta, body in items:
        title = meta.get("description", rid)
        parts.append(f"## {rid}")
        parts.append("")
        parts.append(f"_{title}_")
        parts.append("")
        parts.append(body.rstrip())
        parts.append("")
    return "\n".join(parts).rstrip() + "\n"


def build() -> tuple[dict[str, str], str]:
    items = load_sources()
    mdc_map = {rid: render_mdc(meta, body) for rid, meta, body in items}
    agents = render_agents(items)
    return mdc_map, agents


def write_all(mdc_map: dict[str, str], agents: str) -> None:
    OUT_RULES.mkdir(parents=True, exist_ok=True)
    # Remove stale generated mdc not in current src
    keep = set(mdc_map)
    for existing in OUT_RULES.glob("*.mdc"):
        if existing.stem not in keep:
            existing.unlink()
    for rid, content in mdc_map.items():
        (OUT_RULES / f"{rid}.mdc").write_text(content, encoding="utf-8")
    AGENTS_PATH.write_text(agents, encoding="utf-8")


def check(mdc_map: dict[str, str], agents: str) -> int:
    drift = False
    if not AGENTS_PATH.is_file() or AGENTS_PATH.read_text(encoding="utf-8") != agents:
        print(f"DRIFT: {AGENTS_PATH}", file=sys.stderr)
        drift = True
    for rid, content in mdc_map.items():
        path = OUT_RULES / f"{rid}.mdc"
        if not path.is_file() or path.read_text(encoding="utf-8") != content:
            print(f"DRIFT: {path}", file=sys.stderr)
            drift = True
    if OUT_RULES.is_dir():
        for existing in OUT_RULES.glob("*.mdc"):
            if existing.stem not in mdc_map:
                print(f"STALE: {existing}", file=sys.stderr)
                drift = True
    return 1 if drift else 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    mdc_map, agents = build()
    if args.check:
        return check(mdc_map, agents)
    write_all(mdc_map, agents)
    print(f"wrote {len(mdc_map)} rules → {OUT_RULES}")
    print(f"wrote {AGENTS_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

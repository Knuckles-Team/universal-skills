#!/usr/bin/env python3
"""Deterministic, idempotent AU -> agent-connector-sdk codemod for one connector repo.

usage: connector_codemod.py <repo> [--map au-to-sdk-map.tsv] [--sdk-root <checkout>] [--dry-run]

* Rewrites ``from agent_utilities... import X`` per the map (EXISTS/ADD rows).
  Rows tagged ``[REWRITE...]`` are rewritten at the import but reported: the
  call site's signature differs and needs review.
* Deletes agent-mode files (``*/agent_server.py`` and tests whose only AU
  imports are agent-mode REMOVE symbols). Every other REMOVE use is reported.
* Rewrites ``"agent_utilities.x.y"`` string literals (mock.patch targets).
* In a file importing agent_connector_sdk.mcp.env_drift, renames the AU-named
  checker internals (see ENV_DRIFT_RENAMES).
* Rewrites the .pre-commit-config.yaml env-drift hook module; other AU hook
  modules are reported.
* Rewrites pyproject: ``agent-utilities[...]`` -> ``agent-connector-sdk>=0.2.0,<1.0.0``,
  drops agent-mode console scripts (``*agent_server:*``).
* Reports every call of a symbol whose semantics changed (SEMANTIC_REWRITES) as
  CALLSITE, even when the map row looks like an exact equivalent.
Prints a per-repo report. Running twice changes nothing the second time.
After the rewrite, run check_tool_parity.py against the old tools/list
census: a missing operation fails the migration.
"""

from __future__ import annotations

import argparse
import ast
import re
import subprocess
import sys
from pathlib import Path

SDK_DEP = "agent-connector-sdk[mcp]>=0.3.11,<1.0.0"
AGENT_MODE = "REMOVE agent mode"
#: AU-named env-drift internals a connector wrapper calls on the checker module.
ENV_DRIFT_RENAMES = {
    "_agent_utilities_reads": "framework_reads",
    "_agent_utilities_dynamic_families": "framework_dynamic_families",
}
#: Symbols whose SDK target has different semantics; every use is a CALLSITE.
SEMANTIC_REWRITES = {
    "agent_utilities.mcp.verbose_tools.register_tool_surface": (
        "SDK >=0.3.0 serves one tool per operation from client_cls; pass "
        "client_cls+get_client and verify with check_tool_parity.py"
    ),
}
#: ``python -m`` hook modules with an SDK equivalent.
HOOK_RENAMES = {
    "agent_utilities.mcp.check_env_var_drift": "agent_connector_sdk.mcp.env_drift",
}


def process_precommit(path: Path, report, dry: bool) -> None:
    src = path.read_text()
    text = src
    for au_mod, sdk_mod in HOOK_RENAMES.items():
        text = text.replace(f"-m {au_mod}", f"-m {sdk_mod}")
    for left in sorted(set(re.findall(r"-m (agent_utilities[\w.]*)", text))):
        report.append(f"  REVIEW .pre-commit-config.yaml hook runs {left}")
    if text != src:
        report.append("  PRECOMMIT env-drift hook -> agent_connector_sdk.mcp.env_drift")
        if not dry:
            path.write_text(text)


def load_map(path: Path) -> dict[str, tuple[str, str]]:
    rows: dict[str, tuple[str, str]] = {}
    for line in path.read_text().splitlines()[1:]:
        sym, repl, status = line.split("\t")
        rows[sym] = (repl, status)
    return rows


def target(repl: str) -> tuple[str, str] | None:
    """``agent_connector_sdk.mod.name [note]`` -> (module, name)."""
    head = repl.split(" ", 1)[0]
    if not head.startswith("agent_connector_sdk") or "(" in head:
        return None
    mod, _, name = head.rpartition(".")
    return mod, name


SDK_ROOT: Path | None = None


def is_module(dotted: str) -> bool:
    if SDK_ROOT is None:
        import importlib.util

        try:
            return importlib.util.find_spec(dotted) is not None
        except (ImportError, ValueError):
            return False
    base = SDK_ROOT / dotted.replace(".", "/")
    return base.with_suffix(".py").exists() or (base / "__init__.py").exists()


def rewrite_import(node: ast.ImportFrom, amap, report, rel) -> str | None:
    """Return replacement source for this import, or None to leave it."""
    out: list[str] = []
    for alias in node.names:
        sym = f"{node.module}.{alias.name}"
        repl, status = amap.get(sym, ("UNMAPPED", "REVIEW"))
        tgt = target(repl) if status in ("EXISTS", "ADD") else None
        if tgt is None:
            report.append(f"  REVIEW {rel}:{node.lineno} {sym} -> {status}: {repl}")
            return None  # leave whole statement for a human
        mod, name = tgt
        local = alias.asname or alias.name
        if is_module(f"{mod}.{name}"):
            parent, _, leaf = f"{mod}.{name}".rpartition(".")
            out.append(f"from {parent} import {leaf}" + (f" as {local}" if local != leaf else ""))
        else:
            out.append(f"from {mod} import {name}" + (f" as {local}" if local != name else ""))
        if "[REWRITE" in repl or sym in SEMANTIC_REWRITES:
            note = SEMANTIC_REWRITES.get(sym, repl)
            report.append(f"  CALLSITE {rel}:{node.lineno} {sym} -> {note}")
    return "\n".join(out)


def process_py(path: Path, rel: str, amap, report, dry: bool) -> str:
    src = path.read_text()
    if "agent_utilities" not in src:
        return "clean"
    try:
        tree = ast.parse(src)
    except SyntaxError:
        report.append(f"  REVIEW {rel}: unparsable")
        return "review"
    nodes = [
        n
        for n in ast.walk(tree)
        if isinstance(n, ast.ImportFrom) and n.module and n.module.split(".")[0] == "agent_utilities"
    ]
    plain = [
        n for n in ast.walk(tree) if isinstance(n, ast.Import) and any(a.name.split(".")[0] == "agent_utilities" for a in n.names)
    ]
    syms = [f"{n.module}.{a.name}" for n in nodes for a in n.names]
    agent_only = syms and all(amap.get(s, ("", ""))[0].startswith(AGENT_MODE) for s in syms)
    if path.name == "agent_server.py" or (agent_only and ("test" in rel)):
        report.append(f"  DELETE {rel} (agent mode)")
        if not dry:
            path.unlink()
        return "deleted"
    lines = src.splitlines(keepends=True)
    edits = []
    for n in nodes:
        new = rewrite_import(n, amap, report, rel)
        if new is not None:
            edits.append((n.lineno, n.end_lineno, n.col_offset, new))
    for n in plain:
        report.append(f"  REVIEW {rel}:{n.lineno} bare 'import agent_utilities...'")
    for start, end, col, new in sorted(edits, reverse=True):
        indent = " " * col
        block = "".join(indent + ln + "\n" for ln in new.splitlines())
        lines[start - 1 : end] = [block]
    text = "".join(lines)

    def _str(m: re.Match) -> str:
        sym = m.group(2)
        repl, status = amap.get(sym, ("", ""))
        tgt = target(repl) if status in ("EXISTS", "ADD") and "[REWRITE" not in repl else None
        if tgt is None:
            return m.group(0)
        return f"{m.group(1)}{tgt[0]}.{tgt[1]}{m.group(1)}"

    text = re.sub(r"([\"'])(agent_utilities(?:\.\w+)+)\1", _str, text)
    for leftover in sorted(set(re.findall(r"[\"'](agent_utilities(?:\.\w+)+)[\"']", text))):
        report.append(f"  REVIEW {rel}: string ref {leftover}")
    if "agent_connector_sdk.mcp import env_drift" in text:
        for au_name, sdk_name in ENV_DRIFT_RENAMES.items():
            text = re.sub(rf"\b{au_name}\b", sdk_name, text)
        if "_agent_utilities_root" in text:
            report.append(
                f"  REVIEW {rel}: still locates an agent-utilities checkout "
                "(_agent_utilities_root) before loading the env-drift checker"
            )
    if text != src:
        if not dry:
            path.write_text(text)
        return "rewritten"
    return "unchanged"


def process_pyproject(path: Path, report, dry: bool) -> None:
    src = path.read_text()
    text = re.sub(r"\"agent-utilities(\[[^\]]*\])?[^\"]*\"", f'"{SDK_DEP}"', src)
    # de-duplicate identical dependency lines produced by the rewrite
    seen: set[str] = set()
    out = []
    for line in text.splitlines(keepends=True):
        key = line.strip()
        if key.startswith(f'"{SDK_DEP}"'):
            if key in seen:
                continue
            seen.add(key)
        if re.match(r"\s*agent-utilities\s*=\s*\{", line):
            report.append(f"  DELETE uv source {key}")
            continue
        if re.match(r"\s*[\w-]+\s*=\s*\"[\w.]+agent_server:\w+\"", line):
            report.append(f"  DELETE pyproject script {key}")
            continue
        out.append(line)
    text = "".join(out)
    for m in re.findall(r"agent[-_]utilities[\w.\[\]-]*", text):
        report.append(f"  REVIEW pyproject mention {m} (entry-point group names are graph-os discovery, kept)")
    if text != src:
        report.append("  PYPROJECT rewritten -> " + SDK_DEP)
        if not dry:
            path.write_text(text)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("repo", type=Path)
    ap.add_argument("--map", type=Path, default=Path(__file__).with_name("au-to-sdk-map.tsv"))
    ap.add_argument("--sdk-root", type=Path, help="agent-connector-sdk checkout (default: installed SDK)")
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()
    global SDK_ROOT
    SDK_ROOT = a.sdk_root
    amap = load_map(a.map)
    repo = a.repo.resolve()
    files = subprocess.run(["git", "-C", str(repo), "ls-files", "*.py"], capture_output=True, text=True, check=True).stdout.split()
    report: list[str] = []
    counts: dict[str, int] = {}
    for rel in sorted(files):
        p = repo / rel
        if p.exists():
            r = process_py(p, rel, amap, report, a.dry_run)
            counts[r] = counts.get(r, 0) + 1
    if (repo / ".pre-commit-config.yaml").exists():
        process_precommit(repo / ".pre-commit-config.yaml", report, a.dry_run)
    if (repo / "pyproject.toml").exists():
        process_pyproject(repo / "pyproject.toml", report, a.dry_run)
    print(f"== {repo.name}: " + ", ".join(f"{k}={v}" for k, v in sorted(counts.items()) if k != "clean"))
    print("\n".join(dict.fromkeys(report)))
    return 0


if __name__ == "__main__":
    sys.exit(main())

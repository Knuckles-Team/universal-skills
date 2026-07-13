#!/usr/bin/env python3
"""CA-016: Wiring Audit — entry-point reachability via the import graph.

Replaces the manual Wiring Audit Checklist with a runnable check: build the package's module
import graph (AST, no execution), then BFS from the declared **entry-point** modules (MCP server,
API routers, CLI) to each **target module**, reporting the minimum import-hop distance. A target
that is not reachable within ``--max-hops`` (default 3) is a Wire-First violation — dead code or a
bolt-on silo.

Resolves absolute (``pkg.sub.mod``) and relative (``from . / from ..``) imports to in-package
file paths. Approximate (import edges, not call edges) but catches the common failure: a new
module that nothing on a hot path imports.

Usage:
    python check_wiring.py --root /path/to/pkg --package pkg \\
        --entry-points mcp/kg_server.py,server/app.py,knowledge_graph/memory/cli.py \\
        --targets knowledge_graph/retrieval/hyde_planner.py,knowledge_graph/core/bitemporal.py
    python check_wiring.py --root . --package pkg --ledger ledger.json   # targets from a ledger
    python check_wiring.py --self-test

CONCEPT:CA-016 — Wiring Audit (Import-Graph Reachability)

Layered KG/engine-native design (see ``_kg_ast.py``): this check is deliberately
kept on local stdlib ``ast`` for two reasons, not convenience. (1) It is designed
to run standalone against ANY local checkout — including un-ingested third-party
comparison targets — with zero graph-os/KG dependency, which is the whole point
of a lightweight, offline Wire-First gate. (2) Even against an ingested target,
the exact hop-count this CI gate pass/fails on needs precise relative-import
dot-level resolution (``ast.ImportFrom.level``) that the engine's
``RustASTParser`` wire protocol does not carry — its import edges are raw,
unresolved module strings (see ``_kg_ast.py``'s module docstring); silently
swapping to an approximate KG substitute risks changing PASS/FAIL results on a
gate builds rely on. This module's ``ast`` usage (``Import``/``ImportFrom``) is
fully modern — none of the Python-3.12-removed node types (``ast.Str``/
``ast.Num``/``ast.NameConstant``/``ast.Ellipsis``) appear here.
"""

from __future__ import annotations

import argparse
import ast
import json
import re
import sys
from collections import deque
from pathlib import Path


def _rel(path: Path, root: Path) -> str:
    return str(path.relative_to(root)).replace("\\", "/")


def _module_to_relpath(dotted: str, package: str) -> str | None:
    """Map an absolute dotted module (``pkg.a.b``) to a repo-relative file path (``a/b.py``)."""
    parts = dotted.split(".")
    if package and parts and parts[0] == package:
        parts = parts[1:]
    if not parts:
        return None
    return "/".join(parts) + ".py"


def _resolve_relative(file_rel: str, node: ast.ImportFrom) -> str | None:
    """Resolve a relative import (``from . / ..``) to a repo-relative module path."""
    base = Path(file_rel).parent
    for _ in range(node.level - 1):  # each extra dot climbs one more package
        base = base.parent
    mod = node.module.replace(".", "/") if node.module else ""
    target = base / mod if mod else base
    return str(target).replace("\\", "/") + ".py"


def build_import_graph(root: Path, package: str) -> dict[str, set[str]]:
    """Map each in-package module (relpath) to the set of in-package modules it imports."""
    files = {_rel(p, root) for p in root.rglob("*.py") if "__pycache__" not in p.parts}
    graph: dict[str, set[str]] = {f: set() for f in files}

    def _exists(relpath: str) -> str | None:
        # Accept a module file or a package __init__.
        if relpath in files:
            return relpath
        pkg_init = relpath[:-3] + "/__init__.py"
        return pkg_init if pkg_init in files else None

    for f in files:
        try:
            tree = ast.parse((root / f).read_text(errors="ignore"))
        except SyntaxError:
            continue
        for node in ast.walk(tree):
            targets: list[str | None] = []
            if isinstance(node, ast.Import):
                targets += [_module_to_relpath(a.name, package) for a in node.names]
            elif isinstance(node, ast.ImportFrom):
                if node.level and node.level > 0:
                    targets.append(_resolve_relative(f, node))
                elif node.module:
                    targets.append(_module_to_relpath(node.module, package))
            for t in targets:
                if not t:
                    continue
                resolved = _exists(t)
                if resolved and resolved != f:
                    graph[f].add(resolved)
    return graph


def min_hops(graph: dict[str, set[str]], entries: list[str], target: str) -> int | None:
    """BFS minimum import-hop distance from any entry module to the target (None if unreachable)."""
    seen = {e: 0 for e in entries if e in graph}
    q = deque(seen)
    while q:
        cur = q.popleft()
        d = seen[cur]
        if cur == target:
            return d
        for nxt in graph.get(cur, ()):
            if nxt not in seen:
                seen[nxt] = d + 1
                if nxt == target:
                    return d + 1
                q.append(nxt)
    return seen.get(target)


# Self-registration / plugin-discovery markers. A module nothing imports directly may still be wired
# via decorator/registry registration (loaded by pkgutil/entry-point discovery). The import-graph is
# blind to this, so an import-unreachable module that self-registers is NOT a Wire-First violation.
_REGISTRATION_MARKERS = re.compile(
    r"@adaptor\b|@register\w*\b|register_source\s*\(|register_extractor\s*\(|"
    r"\.register\s*\(|entry_points\s*\(|importlib\.metadata|pkgutil\.iter_modules|"
    r"setdefault\(['\"][^'\"]+['\"],\s*self\)"
)


def _self_registers(root: Path, target: str) -> bool:
    """True if the target module self-registers via a decorator/registry/entry-point pattern."""
    path = root / target
    if not path.is_file():
        return False
    try:
        return bool(_REGISTRATION_MARKERS.search(path.read_text(errors="ignore")))
    except OSError:
        return False


def audit(root: Path, package: str, entries: list[str], targets: list[str], max_hops: int = 3) -> dict:
    graph = build_import_graph(root, package)
    results = []
    for t in targets:
        d = min_hops(graph, entries, t)
        within = d is not None and d <= max_hops
        registered = False
        if not within:
            # Import-unreachable: check for plugin/decorator self-registration before flagging.
            registered = _self_registers(root, t)
        results.append({
            "target": t,
            "min_hops": d,
            "reachable": d is not None,
            "registered_via_plugin": registered,
            "within_limit": within or registered,
        })
    violations = [r for r in results if not r["within_limit"]]
    return {"max_hops": max_hops, "results": results, "violations": violations,
            "passed": not violations}


def _self_test() -> int:
    import tempfile

    with tempfile.TemporaryDirectory() as d:
        root = Path(d) / "pkg"
        (root / "mcp").mkdir(parents=True)
        (root / "retrieval").mkdir(parents=True)
        # entry → engine → retriever → planner  (planner is 3 hops from entry)
        (root / "mcp" / "server.py").write_text("from pkg.engine import E\n")
        (root / "engine.py").write_text("from pkg.retrieval.retriever import R\n")
        (root / "retrieval" / "retriever.py").write_text("from .planner import P\n")
        (root / "retrieval" / "planner.py").write_text("X = 1\n")
        (root / "orphan.py").write_text("Y = 2\n")  # nothing imports it
        # A self-registering plugin: nothing imports it, but it registers via a registry call.
        (root / "plugin.py").write_text("from pkg.registry import register_source\nregister_source('x', f)\n")
        res = audit(root, "pkg", ["mcp/server.py"],
                    ["retrieval/planner.py", "orphan.py", "plugin.py"], max_hops=3)
        byt = {r["target"]: r for r in res["results"]}
        assert byt["retrieval/planner.py"]["min_hops"] == 3, byt
        assert byt["retrieval/planner.py"]["within_limit"] is True, byt
        assert byt["orphan.py"]["reachable"] is False, byt
        # The self-registering plugin is import-unreachable but NOT a violation.
        assert byt["plugin.py"]["reachable"] is False, byt
        assert byt["plugin.py"]["registered_via_plugin"] is True, byt
        assert byt["plugin.py"]["within_limit"] is True, byt
        # orphan.py (no registration) is still a violation.
        assert not res["passed"] and any(v["target"] == "orphan.py" for v in res["violations"]), res
        # Tightening max_hops to 2 makes the planner a violation too.
        res2 = audit(root, "pkg", ["mcp/server.py"], ["retrieval/planner.py"], max_hops=2)
        assert not res2["passed"], res2
    print("self-test OK")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description="Wiring Audit via import graph (CA-016)")
    ap.add_argument("--root", help="Package root directory")
    ap.add_argument("--package", default="", help="Top-level package name to strip from absolute imports")
    ap.add_argument("--entry-points", default="", help="Comma-separated entry-point relpaths")
    ap.add_argument("--targets", default="", help="Comma-separated target relpaths")
    ap.add_argument("--ledger", help="Read target_module paths from a ledger instead of --targets")
    ap.add_argument("--max-hops", type=int, default=3)
    ap.add_argument("--self-test", action="store_true")
    args = ap.parse_args()

    if args.self_test or not args.root:
        return _self_test()

    entries = [e.strip() for e in args.entry_points.split(",") if e.strip()]
    targets = [t.strip() for t in args.targets.split(",") if t.strip()]
    if args.ledger:
        rows = json.loads(Path(args.ledger).read_text())
        rows = rows if isinstance(rows, list) else rows.get("rows", [])
        # Ledger target_module paths are repo-root relative (include the package name);
        # normalize to --root-relative by stripping a leading "<package>/" prefix so they
        # match the import-graph keys.
        prefix = f"{args.package}/" if args.package else ""
        for r in rows:
            tm = r.get("target_module")
            if not tm:
                continue
            if prefix and tm.startswith(prefix):
                tm = tm[len(prefix):]
            targets.append(tm)

    res = audit(Path(args.root), args.package, entries, sorted(set(targets)), args.max_hops)
    print(json.dumps(res, indent=2))
    if not res["passed"]:
        print(f"WIRE-FIRST FAIL: {len(res['violations'])} target(s) not reachable within "
              f"{args.max_hops} hops.", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

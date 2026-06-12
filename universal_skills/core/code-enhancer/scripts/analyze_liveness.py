#!/usr/bin/env python3
"""CONCEPT:CE-038 — Liveness / dead-pathway analysis.

Detects code that exists but is never wired into a running logic path. Three
DETERMINISTIC layers (no LLM — so this runs unattended on CI/cron), each catching a
distinct failure mode that the others miss:

  1. **Static reachability** — modules never imported by any non-test module
     (orphans) and top-level functions/classes never referenced anywhere
     (dead definitions). Catches "no static path reaches this".

  2. **Dynamic liveness** — functions whose lines were NEVER executed across the
     test suite (+ optional smoke run), read from a ``coverage.py`` JSON report.
     Catches "reachable but never invoked" — the class static analysis ranks as
     live (it IS imported/callable) but no real path actually calls it.

  3. **Typed-seam / contract drift** — functions returning an untyped
     ``dict[str, Any]`` across a module boundary (where producer/consumer key
     contracts silently drift — e.g. a producer writes ``_score`` while the
     consumer reads ``score`` and gets ``0.00``), plus dict keys that are read but
     never written anywhere (silent ``.get`` defaults) or written but never read
     (dead data).

Usage:
    analyze_liveness.py <repo_path> [--coverage coverage.json] [--baseline base.json]
                        [--entry-points a.b.c,d.e] [--json]

Exit code is non-zero when a ``--baseline`` is supplied and any category REGRESSED
(more findings than the baseline) — so it ratchets as a CI guardrail gate.
"""

from __future__ import annotations

import ast
import json
import re
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any

_SKIP_DIRS = frozenset(
    {
        ".venv",
        "venv",
        "__pycache__",
        "node_modules",
        ".git",
        "build",
        "dist",
        ".tox",
        ".mypy_cache",
        ".pytest_cache",
        "migrations",
    }
)
# Files whose top-level symbols/modules are entry points by construction — never
# "orphans" even with no inbound import edge.
_ENTRY_FILES = frozenset(
    {"__main__.py", "__init__.py", "conftest.py", "setup.py", "main.py"}
)
# Decorators that mean "registered/invoked dynamically" — a symbol so decorated is
# wired by a framework, not by a direct call, so static reachability must not flag it.
_REGISTRATION_DECORATORS = frozenset(
    {
        "tool",
        "app",
        "router",
        "route",
        "get",
        "post",
        "put",
        "delete",
        "patch",
        "command",
        "fixture",
        "task",
        "register",
        "register_source",
        "hookimpl",
        "on_event",
        "listens_for",
        "cli",
        "group",
        "callback",
        "property",
        "cached_property",
        "staticmethod",
        "classmethod",
        "abstractmethod",
        "overload",
    }
)
_UNTYPED_DICT_RETURNS = frozenset({"dict", "Dict", "Mapping", "MutableMapping"})


def _iter_py(root: Path):
    for p in root.rglob("*.py"):
        if any(part in _SKIP_DIRS for part in p.parts):
            continue
        yield p


def _module_name(root: Path, p: Path) -> str:
    rel = p.relative_to(root).with_suffix("")
    parts = [x for x in rel.parts if x != "__init__"]
    return ".".join(parts)


def _is_test(p: Path) -> bool:
    return "tests" in p.parts or p.name.startswith("test_") or p.name == "conftest.py"


def _decorator_names(node: ast.AST) -> set[str]:
    out: set[str] = set()
    for d in getattr(node, "decorator_list", []) or []:
        t = d.func if isinstance(d, ast.Call) else d
        if isinstance(t, ast.Name):
            out.add(t.id)
        elif isinstance(t, ast.Attribute):
            out.add(t.attr)
    return out


def _contains_untyped_dict(node: ast.expr | None) -> bool:
    """True if the annotation IS or CONTAINS a bare dict/Mapping — i.e. an untyped
    payload crossing a boundary (``dict``, ``dict[str, Any]``, ``list[dict]``,
    ``Iterable[dict[str, Any]]`` …). This is the seam where producer/consumer key
    contracts silently drift."""
    if node is None:
        return False
    if isinstance(node, ast.Name):
        return node.id in _UNTYPED_DICT_RETURNS
    if isinstance(node, ast.Attribute):
        return node.attr in _UNTYPED_DICT_RETURNS
    if isinstance(node, ast.Subscript):
        # dict[str, Any] is a leaf untyped dict; list[dict[...]] recurses into args
        if _contains_untyped_dict(node.value):
            return True
        return _contains_untyped_dict(node.slice)
    if isinstance(node, ast.Tuple):
        return any(_contains_untyped_dict(e) for e in node.elts)
    return False


def _is_environ_get(call: ast.Call) -> bool:
    """``os.environ.get(...)`` / ``environ.get(...)`` / ``os.getenv(...)`` — an
    environment lookup, not an internal dict-contract read. Excluded from key
    tracking so env-var names aren't flagged as orphan keys."""
    f = call.func
    if isinstance(f, ast.Attribute):
        if f.attr == "getenv":
            return True
        recv = f.value
        if isinstance(recv, ast.Name) and recv.id in ("environ", "os"):
            return True
        if isinstance(recv, ast.Attribute) and recv.attr == "environ":
            return True
    return False


# ── Facade detection (Layer 4): "invoked but fake" ────────────────────────────
# Admitted tells of placeholder/stub code in strings or comments.
_PLACEHOLDER_RE = re.compile(
    r"\b(TODO|FIXME|XXX|HACK|stub(?:bed|s)?|placeholder|mock(?:ed)?|dummy|"
    r"for now|not[ _-]?implemented|coming soon|hard[ -]?coded|sample data|"
    r"example only|fake|lorem ipsum|in (?:a|the) real|real implementation|"
    r"would (?:be|go) here|replace this|simulate[d]?)\b",
    re.IGNORECASE,
)
# Path segments that mean "this module is a LIVE external surface" — its handlers
# are expected to do real work (query/compute), not return canned data.
_SURFACE_PARTS = frozenset(
    {"mcp", "server", "routers", "router", "gateway", "api", "endpoints", "commands"}
)
# Decorators that mark a function as a live surface handler (tool / route / command).
_SURFACE_DECORATORS = frozenset(
    {"tool", "route", "get", "post", "put", "delete", "patch", "command", "endpoint"}
)
# String/list/dict methods that are pure formatting — calling ONLY these is not work.
_PURE_METHODS = frozenset(
    {
        "format",
        "join",
        "split",
        "strip",
        "lstrip",
        "rstrip",
        "lower",
        "upper",
        "replace",
        "startswith",
        "endswith",
        "title",
        "capitalize",
        "items",
        "keys",
        "values",
        "append",
        "extend",
        "get",
        "encode",
        "decode",
        "splitlines",
        "rstrip",
        "zfill",
        "ljust",
        "rjust",
        "isdigit",
    }
)
_PURE_BUILTINS = frozenset(
    {
        "len",
        "str",
        "int",
        "float",
        "bool",
        "list",
        "dict",
        "set",
        "tuple",
        "sorted",
        "reversed",
        "enumerate",
        "range",
        "zip",
        "min",
        "max",
        "sum",
        "any",
        "all",
        "repr",
        "f",
        "print",
        "isinstance",
        "getattr",
        "hasattr",
    }
)
# Handlers whose job IS to return static text — legitimately literal, not facades.
_INFO_NAMES_RE = re.compile(r"help|usage|about|version|info|ping|menu|banner|readme")


def _does_real_work(func: ast.AST) -> bool:
    """A handler does 'real work' if it awaits, or calls anything beyond pure
    string/list/dict formatting + builtins (i.e. it reaches a dependency, a service,
    or another function). A body that only builds literals/strings and returns does
    NO real work — a facade candidate."""
    for n in ast.walk(func):
        if isinstance(n, (ast.Await, ast.Yield, ast.YieldFrom)):
            return True
        if isinstance(n, ast.Call):
            f = n.func
            if isinstance(f, ast.Attribute):
                if f.attr not in _PURE_METHODS:
                    return True  # method call on some object → real work
            elif isinstance(f, ast.Name):
                if f.id not in _PURE_BUILTINS:
                    return True  # delegates to another function → real work
    return False


def _is_canned_value(v: ast.expr) -> bool:
    """A non-trivial literal payload (dict/list, or a long/multi-line string) — the
    fabricated-output shape, vs a trivial ``return None``/``return True``."""
    if isinstance(v, (ast.Dict, ast.List)):
        return True
    if isinstance(v, ast.Constant) and isinstance(v.value, str):
        return len(v.value) > 60 or "\n" in v.value
    if isinstance(v, ast.JoinedStr):  # f-string with a long literal part
        return any(
            isinstance(x, ast.Constant)
            and isinstance(x.value, str)
            and ("\n" in x.value or len(x.value) > 60)
            for x in v.values
        )
    return False


def _returns_canned_payload(func: ast.AST) -> bool:
    return any(
        isinstance(n, ast.Return) and n.value is not None and _is_canned_value(n.value)
        for n in ast.walk(func)
    )


def _stmts_real_work(stmts: list[ast.stmt]) -> bool:
    return any(_does_real_work(s) for s in stmts)


def _stmts_return_canned(stmts: list[ast.stmt]) -> bool:
    return any(
        isinstance(n, ast.Return) and n.value is not None and _is_canned_value(n.value)
        for s in stmts
        for n in ast.walk(s)
    )


def _if_tests_info_keyword(test: ast.expr) -> bool:
    """The branch is keyed on a help/usage/info command (e.g. ``cmd == "help"``) —
    its static text is legitimate, not a facade."""
    return any(
        isinstance(n, ast.Constant)
        and isinstance(n.value, str)
        and _INFO_NAMES_RE.search(n.value)
        for n in ast.walk(test)
    )


def _facade_branches(func: ast.AST) -> list[int]:
    """if/elif branches inside a live-surface dispatcher that return a canned payload
    while doing NO real work — the per-branch facade (e.g. a `/graph stats` arm that
    returns fabricated counts). Returns the branch line numbers."""
    lines: list[int] = []
    for n in ast.walk(func):
        if not isinstance(n, ast.If) or _if_tests_info_keyword(n.test):
            continue
        branches = [n.body]
        # n.orelse is an `else:` body unless it's a single nested If (an `elif`,
        # which the outer ast.walk visits on its own).
        if n.orelse and not (len(n.orelse) == 1 and isinstance(n.orelse[0], ast.If)):
            branches.append(n.orelse)
        for b in branches:
            if b and not _stmts_real_work(b) and _stmts_return_canned(b):
                lines.append(b[0].lineno)
    return lines


def analyze_liveness(argv: list[str]) -> dict[str, Any]:
    args = list(argv)
    cov_path = baseline_path = None
    entry_points: set[str] = set()
    paths: list[str] = []
    i = 0
    while i < len(args):
        a = args[i]
        if a == "--coverage":
            i += 1
            cov_path = args[i]
        elif a == "--baseline":
            i += 1
            baseline_path = args[i]
        elif a == "--entry-points":
            i += 1
            entry_points = {x.strip() for x in args[i].split(",") if x.strip()}
        elif a in ("--json", "-q"):
            pass
        else:
            paths.append(a)
        i += 1
    root = Path(paths[0] if paths else ".").resolve()

    files = [p for p in _iter_py(root)]
    if not files:
        return {
            "domain": "Liveness",
            "score": -1,
            "grade": "N/A",
            "findings": ["No Python files found"],
        }

    # ── Parse every file once ────────────────────────────────────────────────
    trees: dict[Path, ast.Module] = {}
    for p in files:
        try:
            trees[p] = ast.parse(p.read_text(encoding="utf-8", errors="ignore"))
        except SyntaxError:
            continue

    # ── Layer 1: static reachability ─────────────────────────────────────────
    imported_modules: set[str] = set()
    used_names: set[str] = set()
    for p, tree in trees.items():
        for n in ast.walk(tree):
            if isinstance(n, ast.Import):
                for al in n.names:
                    imported_modules.add(al.name)
            elif isinstance(n, ast.ImportFrom) and n.module:
                imported_modules.add(n.module)
                for al in n.names:
                    imported_modules.add(f"{n.module}.{al.name}")
                    used_names.add(al.asname or al.name)
            elif isinstance(n, ast.Name):
                used_names.add(n.id)
            elif isinstance(n, ast.Attribute):
                used_names.add(n.attr)

    def _module_imported(mod: str) -> bool:
        # reachable if the module or any ancestor package is imported anywhere
        parts = mod.split(".")
        return any(
            ".".join(parts[: k + 1]) in imported_modules for k in range(len(parts))
        )

    orphan_modules: list[str] = []
    dead_defs: list[str] = []
    for p, tree in trees.items():
        if _is_test(p) or p.name in _ENTRY_FILES:
            continue
        mod = _module_name(root, p)
        has_main = any(
            isinstance(n, ast.If)
            and isinstance(n.test, ast.Compare)
            and isinstance(n.test.left, ast.Name)
            and n.test.left.id == "__name__"
            for n in tree.body
        )
        if not has_main and mod not in entry_points and not _module_imported(mod):
            # last-segment imported (e.g. `from pkg import bar` where bar is the module)
            if mod.split(".")[-1] not in used_names:
                orphan_modules.append(mod)
        # dead top-level defs: defined, not exported, not decorated-as-registered,
        # and the name never appears anywhere as a use.
        exported = {
            e.value
            for n in tree.body
            if isinstance(n, ast.Assign)
            and any(isinstance(t, ast.Name) and t.id == "__all__" for t in n.targets)
            and isinstance(n.value, (ast.List, ast.Tuple))
            for e in n.value.elts
            if isinstance(e, ast.Constant) and isinstance(e.value, str)
        }
        for n in tree.body:
            if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                name = n.name
                if name.startswith("__") or name in exported:
                    continue
                if _decorator_names(n) & _REGISTRATION_DECORATORS:
                    continue
                # referenced anywhere (other than possibly its own def line)?
                if name not in used_names and name not in imported_modules:
                    dead_defs.append(f"{mod}:{name}")

    # ── Layer 2: dynamic liveness (coverage-driven, optional) ────────────────
    never_executed: list[str] = []
    coverage_available = False
    if cov_path and Path(cov_path).exists():
        coverage_available = True
        cov = json.loads(Path(cov_path).read_text())
        cov_files = cov.get("files", {})
        for p, tree in trees.items():
            if _is_test(p):
                continue
            # match coverage file path (coverage stores repo-relative or absolute)
            key = next(
                (
                    k
                    for k in cov_files
                    if k.endswith(str(p.relative_to(root))) or k == str(p)
                ),
                None,
            )
            if key is None:
                continue
            executed = set(cov_files[key].get("executed_lines", []))
            for n in ast.walk(tree):
                if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    if (
                        n.name.startswith("__")
                        or _decorator_names(n) & _REGISTRATION_DECORATORS
                    ):
                        continue
                    body_lines = {
                        c.lineno for c in ast.walk(n) if hasattr(c, "lineno")
                    } - {n.lineno}
                    if body_lines and not (body_lines & executed):
                        never_executed.append(f"{_module_name(root, p)}:{n.name}")

    # ── Layer 3: typed-seam / contract drift ─────────────────────────────────
    untyped_seams: list[str] = []
    key_writes: dict[str, int] = defaultdict(int)
    key_reads: dict[str, int] = defaultdict(int)
    for p, tree in trees.items():
        if _is_test(p):
            continue
        mod = _module_name(root, p)
        for n in ast.walk(tree):
            # public function returning an (or a collection of) untyped dict → a
            # contract-drift-prone seam (this is the shape the _score/score bug lived in)
            if isinstance(
                n, (ast.FunctionDef, ast.AsyncFunctionDef)
            ) and not n.name.startswith("_"):
                if _contains_untyped_dict(n.returns):
                    untyped_seams.append(f"{mod}:{n.name}")
            # dict key writes: {"k": ..}, d["k"] = .., d.setdefault("k", ..)
            elif isinstance(n, ast.Dict):
                for k in n.keys:
                    if isinstance(k, ast.Constant) and isinstance(k.value, str):
                        key_writes[k.value] += 1
            elif isinstance(n, ast.Subscript) and isinstance(n.ctx, ast.Store):
                if isinstance(n.slice, ast.Constant) and isinstance(n.slice.value, str):
                    key_writes[n.slice.value] += 1
            # dict key reads: d.get("k"), d["k"] (load), "k" in d
            elif isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute):
                if (
                    n.func.attr in ("get", "setdefault", "pop")
                    and n.args
                    and not _is_environ_get(n)
                ):
                    a0 = n.args[0]
                    if isinstance(a0, ast.Constant) and isinstance(a0.value, str):
                        (key_reads if n.func.attr == "get" else key_writes)[
                            a0.value
                        ] += 1
            elif isinstance(n, ast.Subscript) and isinstance(n.ctx, ast.Load):
                if isinstance(n.slice, ast.Constant) and isinstance(n.slice.value, str):
                    key_reads[n.slice.value] += 1

    # keys read meaningfully but NEVER written anywhere → silent .get default risk
    orphan_read_keys = sorted(
        k
        for k, r in key_reads.items()
        if r >= 3
        and key_writes.get(k, 0) == 0
        and not k.startswith("__")
        and len(k) > 1
    )

    # ── Layer 4: facade detection ("invoked but fake") ───────────────────────
    facade_handlers: list[str] = []
    placeholder_hits: list[str] = []
    for p, tree in trees.items():
        if _is_test(p):
            continue
        mod = _module_name(root, p)
        is_surface_mod = bool(set(p.parts) & _SURFACE_PARTS)
        # admitted placeholder/stub tells in raw source (comments + strings)
        try:
            for i, line in enumerate(
                p.read_text(encoding="utf-8", errors="ignore").splitlines(), 1
            ):
                if _PLACEHOLDER_RE.search(line):
                    placeholder_hits.append(f"{mod}:{i}")
        except OSError:
            pass
        # live-surface handlers that return a canned payload doing NO real work —
        # whole-function facades, OR per-branch facades inside a real dispatcher
        # (the /graph-stats-returns-"42-nodes" class lives in one such branch).
        for n in ast.walk(tree):
            if not isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)):
                continue
            decorated = bool(_decorator_names(n) & _SURFACE_DECORATORS)
            if not (is_surface_mod or decorated) or _INFO_NAMES_RE.search(n.name):
                continue
            if not _does_real_work(n) and _returns_canned_payload(n):
                facade_handlers.append(f"{mod}:{n.name}")
                continue  # whole function is a facade; don't double-count its branches
            for line in _facade_branches(n):
                facade_handlers.append(f"{mod}:{n.name}@{line}")

    # ── Score + report ───────────────────────────────────────────────────────
    counts = {
        "orphan_modules": len(orphan_modules),
        "dead_definitions": len(dead_defs),
        "never_executed": len(never_executed),
        "untyped_seams": len(untyped_seams),
        "orphan_read_keys": len(orphan_read_keys),
        "facade_handlers": len(facade_handlers),
        "placeholder_markers": len(placeholder_hits),
    }
    # weighted penalty; facades (fake live surfaces) + never-executed + orphan
    # modules are the most damning.
    penalty = (
        counts["orphan_modules"] * 5
        + counts["facade_handlers"] * 4
        + counts["never_executed"] * 2
        + counts["dead_definitions"] * 1
        # untyped seams are a contract-drift RISK surface, not dead code — capped so
        # a dict-heavy (but live) codebase isn't graded red on style alone.
        + min(15, counts["untyped_seams"] * 0.5)
        + counts["orphan_read_keys"] * 2
        + min(20, counts["placeholder_markers"] * 0.5)
    )
    score = max(0, round(100 - penalty))
    grade = "🟢" if score >= 80 else ("🟡" if score >= 60 else "🔴")

    findings: list[str] = []
    if orphan_modules:
        findings.append(
            f"{len(orphan_modules)} orphan module(s) — never imported: {orphan_modules[:8]}"
        )
    if never_executed:
        findings.append(
            f"{len(never_executed)} function(s) never executed by the test suite (reachable-but-not-invoked): {never_executed[:8]}"
        )
    elif not coverage_available:
        findings.append(
            "Dynamic liveness skipped — pass --coverage <coverage.json> for the never-invoked layer."
        )
    if dead_defs:
        findings.append(
            f"{len(dead_defs)} top-level definition(s) never referenced: {dead_defs[:8]}"
        )
    if orphan_read_keys:
        findings.append(
            f"{len(orphan_read_keys)} dict key(s) READ but never WRITTEN anywhere — silent .get-default / contract drift: {orphan_read_keys[:8]}"
        )
    if untyped_seams:
        findings.append(
            f"{len(untyped_seams)} public function(s) return an untyped dict (contract-drift-prone seam): {untyped_seams[:8]}"
        )
    if facade_handlers:
        findings.append(
            f"{len(facade_handlers)} FACADE handler(s) on a live surface (tool/route/command) that do NO real "
            f"work but return a canned payload — invoked-but-fake: {facade_handlers[:8]}"
        )
    if placeholder_hits:
        findings.append(
            f"{len(placeholder_hits)} placeholder/stub marker(s) (TODO/FIXME/mock/'for now'/sample data): {placeholder_hits[:8]}"
        )
    if not findings:
        findings.append("No dead pathways detected.")

    result = {
        "domain": "Liveness / Dead Pathways",
        "score": score,
        "grade": grade,
        "counts": counts,
        "findings": findings,
        "details": {
            "orphan_modules": orphan_modules,
            "dead_definitions": dead_defs,
            "never_executed": never_executed,
            "orphan_read_keys": orphan_read_keys,
            "untyped_seams": untyped_seams,
            "facade_handlers": facade_handlers,
            "placeholder_markers": placeholder_hits,
        },
        "coverage_available": coverage_available,
    }

    # ── Ratchet gate ─────────────────────────────────────────────────────────
    if baseline_path and Path(baseline_path).exists():
        base = json.loads(Path(baseline_path).read_text()).get("counts", {})
        regressed = {
            k: (v, base.get(k, 0)) for k, v in counts.items() if v > base.get(k, 0)
        }
        result["regressed"] = regressed
        result["gate"] = "fail" if regressed else "pass"
    return result


if __name__ == "__main__":
    out = analyze_liveness(sys.argv[1:])
    print(json.dumps(out, indent=2, default=str))
    # ratchet exit code for CI
    if out.get("gate") == "fail":
        sys.exit(1)

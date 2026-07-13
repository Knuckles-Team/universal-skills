#!/usr/bin/env python3
"""CE-045 — KG-native / engine-AST / local-fallback analysis mechanism hierarchy.

code-enhancer used to hand-roll code analysis with Python's stdlib ``ast`` (fragile
— e.g. ``ast.Str`` broke on 3.12). The platform already ingests the whole ecosystem
into the epistemic-graph as a typed code graph (symbols, call graph, CONCEPT
markers, tests), and exposes a version-independent, multi-language tree-sitter
parser as an engine service. This module gives every code-enhancer script one
shared, three-tier mechanism, preferred in this order:

  1. **The ingested code KG (graph-os)** — a read-only Cypher query over the
     already-ingested ``:Code`` graph (``POST /graph/query``) or the composed
     ``code_context`` answer (``POST /graph/code``, action=code_context — definition,
     callers, blast-radius, CONCEPT markers, docs). Zero re-parsing; the richest,
     most cross-repo-aware answer, when the target repo has already been ingested
     (``source_sync``/``kg_ingest_run.py``).
  2. **The engine AST** (``epistemic_graph.parser.RustASTParser``) — on-demand
     tree-sitter parsing via the Rust engine's out-of-process socket, for a
     file/repo the KG doesn't already hold. Multi-language, version-independent.
  3. **Local stdlib ``ast`` parsing** — the final fallback, used only when neither
     the KG nor the engine socket is reachable (``epistemic_graph`` not installed,
     no socket, or the engine erroring) — Python-only and clearly degraded (the
     ``tier`` every helper returns is ``"local"``), so the skill still works
     standalone with zero platform dependencies.

Every helper is best-effort and **never raises** — an unreachable KG/engine
degrades silently to the next tier.

CONCEPT:CE-045 — KG-native analysis mechanism hierarchy
"""

from __future__ import annotations

import ast
import asyncio
import json
import os
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any

SKIP_DIRS = frozenset(
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
        "target",
        "site",
        ".ruff_cache",
    }
)


# ---------------------------------------------------------------------------
# Tier 1 — the ingested code KG (graph-os)
# ---------------------------------------------------------------------------


def graph_os_endpoint() -> str | None:
    """Resolve the graph-os base URL from the environment (unset = KG tier skipped)."""
    return os.environ.get("GRAPH_OS_MCP_URL") or None


def _auth_headers() -> dict[str, str]:
    token = os.environ.get("GRAPH_OS_MCP_TOKEN")
    return {"Authorization": f"Bearer {token}"} if token else {}


def _post(
    path: str, body: dict[str, Any], endpoint: str | None, timeout: int = 20
) -> Any:
    """POST JSON to a graph-os REST route. Returns the parsed ``result``, or ``None``
    on any failure (unreachable, timeout, non-success) — never raises."""
    url = endpoint or graph_os_endpoint()
    if not url:
        return None
    req = urllib.request.Request(
        url.rstrip("/") + path,
        data=json.dumps(body).encode(),
        headers={"Content-Type": "application/json", **_auth_headers()},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:  # noqa: S310 - operator-configured URL
            payload = json.loads(resp.read().decode() or "{}")
    except (urllib.error.URLError, TimeoutError, OSError, ValueError):
        return None
    if not isinstance(payload, dict) or payload.get("status") != "success":
        return None
    return payload.get("result")


def kg_cypher(
    cypher: str, params: dict[str, Any] | None = None, endpoint: str | None = None
) -> list[dict[str, Any]] | None:
    """Run a read-only Cypher query via graph-os (``POST /graph/query``, ``graph_query``
    MCP tool). ``None`` = KG unreachable/errored (fall through to Tier 2)."""
    result = _post(
        "/graph/query",
        {"cypher": cypher, "params": json.dumps(params or {})},
        endpoint,
    )
    return result if isinstance(result, list) else None


def kg_code_context(
    query: str, target: str = "how", top_k: int = 10, endpoint: str | None = None
) -> dict[str, Any] | None:
    """The composed, cited ``code_context`` answer (``POST /graph/code``, action=
    code_context — CONCEPT:AU-KG.retrieval.synthesized-cited-answer). ``target``
    is the intent: ``how`` | ``usage`` | ``impact``."""
    return _post(
        "/graph/code",
        {"action": "code_context", "query": query, "target": target, "top_k": top_k},
        endpoint,
    )


def _kind(sym: dict[str, Any]) -> str:
    return str(sym.get("kind_detail") or sym.get("kind") or "").lower()


def _line(sym: dict[str, Any]) -> int:
    try:
        return int(sym.get("line") or 0)
    except (TypeError, ValueError):
        return 0


def kg_repo_symbols(
    root: Path, endpoint: str | None = None, limit: int = 20000
) -> list[dict[str, Any]] | None:
    """Every ingested ``:Code`` function/class/method symbol under ``root`` — Tier 1.

    Returns ``None`` when the KG is unreachable OR the repo has no anchored symbols
    (uningested) — either way the caller falls through to Tier 2 (engine AST).
    """
    root_s = str(root.resolve())
    rows = kg_cypher(
        "MATCH (c:Code) WHERE c.kind_detail IN ['function','method','class'] "
        "AND c.file_path STARTS WITH $root "
        "RETURN c.name AS name, c.file_path AS file_path, c.line AS line, "
        "c.kind_detail AS kind_detail, c.language AS language, c.is_test AS is_test, "
        "c.decorators AS decorators, c.marks AS marks, c.assert_count AS assert_count, "
        "c.raises_count AS raises_count, c.mock_count AS mock_count, "
        "c.calls AS calls LIMIT $limit",
        {"root": root_s, "limit": limit},
        endpoint,
    )
    return rows or None


def kg_repo_concepts(
    root: Path, endpoint: str | None = None
) -> list[dict[str, Any]] | None:
    """CONCEPT markers ``MENTIONED_IN`` files under ``root`` — Tier 1 for concept
    traceability. ``None`` when the KG is unreachable or has no concepts for this repo."""
    root_s = str(root.resolve())
    rows = kg_cypher(
        "MATCH (c)-[r]->(f) WHERE type(r) IN ['MENTIONED_IN', 'mentioned_in'] "
        "AND (c.type = 'CONCEPT' OR c.concept_id IS NOT NULL) "
        "AND (f.file_path STARTS WITH $root OR f.path STARTS WITH $root) "
        "RETURN DISTINCT c.concept_id AS concept_id, f.file_path AS file_path, "
        "f.path AS path",
        {"root": root_s},
        endpoint,
    )
    return rows or None


# ---------------------------------------------------------------------------
# Tier 3 — local stdlib ``ast`` (the final fallback; kept in ONE place)
# ---------------------------------------------------------------------------


DECORATOR_SEP = "\x1f"  # unit separator — decorator source may itself contain commas


def split_decorators(decorators: str) -> list[str]:
    """Split a symbol's joined ``decorators`` property back into individual decorator
    source strings. Prefers the unit-separator join (used by this module's own local
    fallback and, per the engine's wire format, its own SYMBOL properties); falls back
    to a paren-depth-aware comma split for any other joined form, since a decorator's
    own arguments (e.g. ``@pytest.mark.parametrize("x,y", ...)``) may contain commas."""
    if not decorators:
        return []
    if DECORATOR_SEP in decorators:
        return [d for d in decorators.split(DECORATOR_SEP) if d]
    parts: list[str] = []
    depth = 0
    cur: list[str] = []
    for ch in decorators:
        if ch in "([{":
            depth += 1
        elif ch in ")]}":
            depth = max(0, depth - 1)
        if ch == "," and depth == 0:
            parts.append("".join(cur))
            cur = []
        else:
            cur.append(ch)
    if cur:
        parts.append("".join(cur))
    return [p.strip() for p in parts if p.strip()]


def _safe_unparse(node: ast.AST) -> str:
    try:
        return ast.unparse(node)
    except Exception:  # noqa: BLE001 - best-effort source reconstruction
        return ""


def _local_ast_symbols(file_path: Path, source: str) -> list[dict[str, Any]]:
    """Tier 3 — final local stdlib ``ast`` fallback.

    Mirrors the engine's SYMBOL property shape as closely as a single-file parse
    can: ``name``/``kind_detail``/``line`` for every function/class, plus
    ``decorators``/``params``/``is_test``/``assert_count``/``raises_count``/
    ``mock_count`` for functions — so downstream scripts see equivalent signal
    whether the KG, the engine socket, or this local parse served the request.
    """
    try:
        tree = ast.parse(source, filename=str(file_path))
    except (SyntaxError, ValueError):
        return []
    lines = source.splitlines()
    out: list[dict[str, Any]] = []
    for node in ast.walk(tree):
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            continue
        kind = "class" if isinstance(node, ast.ClassDef) else "function"
        end_line = getattr(node, "end_lineno", node.lineno)
        decorators = DECORATOR_SEP.join(
            d for d in (_safe_unparse(d) for d in getattr(node, "decorator_list", [])) if d
        )
        props: dict[str, Any] = {
            "name": node.name,
            "file_path": str(file_path),
            "line": node.lineno,
            "end_line": end_line,
            "kind_detail": kind,
            "decorators": decorators,
        }
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            body = "\n".join(lines[node.lineno - 1 : end_line])
            params = [
                a.arg for a in node.args.args if a.arg not in ("self", "cls")
            ]
            props["params"] = ",".join(params)
            props["is_test"] = "true" if node.name.startswith("test_") else "false"
            props["assert_count"] = str(
                sum(1 for n in ast.walk(node) if isinstance(n, ast.Assert))
            )
            props["raises_count"] = str(body.count("pytest.raises"))
            props["mock_count"] = str(
                body.count("MagicMock")
                + body.count("AsyncMock")
                + body.count("patch(")
                + body.count("mocker.")
                + body.count("monkeypatch.")
            )
        out.append(props)
    return out


# ---------------------------------------------------------------------------
# Tier 2 — the engine AST (with transparent Tier 3 fallback)
# ---------------------------------------------------------------------------


def parse_file_symbols(file_path: Path) -> tuple[list[dict[str, Any]], str]:
    """Per-file symbol extraction — Tier 2 (engine AST) with Tier 3 (local ``ast``)
    fallback. Returns ``(symbols, tier)``, ``tier`` in ``{"engine", "local"}``.
    Never raises — a missing ``epistemic_graph`` dependency or an unreachable
    engine socket degrades straight to the local stdlib ``ast`` parse.
    """
    try:
        source = file_path.read_text(encoding="utf-8", errors="ignore")
    except OSError:
        return [], "local"

    try:
        from epistemic_graph.parser import RustASTParser  # optional dependency
    except ImportError:
        return _local_ast_symbols(file_path, source), "local"

    try:
        result = asyncio.run(
            RustASTParser().parse_file(str(file_path), source.encode("utf-8"))
        )
    except Exception:  # noqa: BLE001 - engine is best-effort, never abort the caller
        return _local_ast_symbols(file_path, source), "local"

    nodes = result.get("nodes") or []
    symbols: list[dict[str, Any]] = []
    for n in nodes:
        if n.get("node_type") != "SYMBOL":
            continue
        props = dict(n.get("properties") or {})
        props["file_path"] = str(file_path)
        props.setdefault("kind_detail", props.get("kind", ""))
        symbols.append(props)

    # RustASTParser silently degrades to ITS OWN local ``ast`` fallback
    # (name/kind/line only, no decorators/assert_count/...) when the engine socket
    # is down, without raising — so a coarse result here does not necessarily mean
    # "no symbols found", it means "no live engine". Detect that and re-run OUR
    # richer local fallback (decorators/params/assert_count/...) instead of
    # settling for the coarse one, so Tier 3 stays as useful as Tiers 1/2.
    rich = any(
        k in (symbols[0] if symbols else {})
        for k in ("decorators", "assert_count", "calls")
    )
    if rich:
        return symbols, "engine"
    return _local_ast_symbols(file_path, source), "local"


def repo_symbols(
    root: Path, endpoint: str | None = None, file_glob: str = "*.py"
) -> tuple[list[dict[str, Any]], str]:
    """Tiered symbol retrieval for a whole repo: KG (Tier 1) first, else per-file
    engine/local (Tier 2/3). Returns ``(symbols, tier)``, ``tier`` in
    ``{"kg", "engine", "local"}`` — the tier actually used.
    """
    kg_rows = kg_repo_symbols(root, endpoint)
    if kg_rows:
        return kg_rows, "kg"

    symbols: list[dict[str, Any]] = []
    tiers_seen: set[str] = set()
    for f in root.rglob(file_glob):
        if any(part in SKIP_DIRS for part in f.parts):
            continue
        file_symbols, tier = parse_file_symbols(f)
        symbols.extend(file_symbols)
        tiers_seen.add(tier)
    return symbols, ("engine" if "engine" in tiers_seen else "local")


def body_span(
    source_lines: list[str], symbols: list[dict[str, Any]], index: int
) -> tuple[int, int]:
    """(start_line, end_line), 1-indexed inclusive, for ``symbols[index]``'s body.

    Prefers the symbol's own ``end_line`` (only ever populated by the local ``ast``
    tier, which has a real ``end_lineno``) when present; otherwise approximates it
    as the next symbol's line minus one (or EOF) — the KG/engine tiers don't carry
    an end line, so this is the best available span for those.
    """
    line = _line(symbols[index])
    end_line = symbols[index].get("end_line")
    if end_line:
        try:
            return line, max(int(end_line), line)
        except (TypeError, ValueError):
            pass
    approx_end = (
        _line(symbols[index + 1]) - 1
        if index + 1 < len(symbols)
        else len(source_lines)
    )
    return line, max(approx_end, line)


def file_symbols_by_line(file_path: Path) -> list[dict[str, Any]]:
    """``parse_file_symbols`` for one file, sorted by line — the common shape scripts
    need to derive an approximate body span (next symbol's line, or EOF)."""
    symbols, _tier = parse_file_symbols(file_path)
    return sorted(symbols, key=_line)

#!/usr/bin/env python3
"""Layered, KG/engine-native code-structure extraction for comparative-analysis scripts.

Every comparative-analysis script that needs "what symbols/docstrings/imports does
this file have" prefers, in this order:

1. **graph-os / the ingested code KG** — ``kg_code_context()`` calls the live
   ``graph_analyze action=code_context`` REST twin (``POST /api/graph/analyze/
   code-context``) on a ``GRAPH_OS_URL``-configured gateway. Most native: when the
   target has already been ingested, the KG already holds resolved call graphs,
   wiring, and doc/architecture signals — no re-parsing needed. Best-effort and
   silently skipped when no gateway is configured or the target isn't ingested
   (comparative-analysis routinely targets un-ingested third-party repos).
2. **epistemic-graph's own AST parser** — ``parse_symbols()`` calls
   ``epistemic_graph.parser.RustASTParser().parse_file()`` (tree-sitter, multi-
   language, version-independent — no ``ast.Str``-class breakage across Python
   releases). Returns ``{FILE, SYMBOL}`` nodes + ``CONTAINS`` edges, each SYMBOL
   carrying ``name``/``kind``/``line``.
3. **Local stdlib ``ast``** — the final fallback, used only when the
   ``epistemic_graph`` package itself isn't importable (comparative-analysis is a
   standalone ``universal-skills`` tool and does not hard-depend on it). Mirrors
   the engine's own local-parse fallback shape exactly, using the modern
   ``ast.Constant`` API (``ast.Str``/``ast.Num``/``ast.NameConstant``/``ast.Ellipsis``
   were removed in Python 3.8-3.12) so this tier never breaks on a current
   interpreter. Every result from this tier is tagged ``"tier": "stdlib_ast_fallback"``
   so callers/reports can surface that they got a degraded answer.

``RustASTParser`` itself already implements the engine-first/local-fallback split
internally (service unavailable -> local ``ast``); this module adds the KG tier on
top and guards the ``epistemic_graph`` import entirely, since comparative-analysis
must keep working with neither graph-os nor epistemic-graph installed/reachable.
"""

from __future__ import annotations

import ast
import asyncio
import hashlib
import json
import os
import urllib.request
from pathlib import Path
from typing import Any

# ---------------------------------------------------------------------------
# Tier 1 — graph-os / the ingested code KG
# ---------------------------------------------------------------------------


def kg_code_context(
    query: str,
    *,
    intent: str = "how",
    top_k: int = 10,
    node_id: str = "",
    endpoint: str | None = None,
    timeout: float = 15.0,
) -> dict[str, Any] | None:
    """Best-effort call to the live ``graph_analyze action=code_context`` REST twin.

    ``endpoint`` defaults to the ``GRAPH_OS_URL`` env var (mirrors the established
    ``GRAPH_OS_MCP_URL``-gated pattern in code-enhancer's ``kg_query_runs.py``).
    Returns ``None`` — never raises — when no gateway is configured, the request
    fails, or the response isn't well-formed, so callers can unconditionally fall
    through to tier 2/3.
    """
    url = (endpoint or os.environ.get("GRAPH_OS_URL", "")).rstrip("/")
    if not url:
        return None
    body = json.dumps(
        {"query": query, "intent": intent, "top_k": top_k, "node_id": node_id}
    ).encode("utf-8")
    req = urllib.request.Request(
        url + "/api/graph/analyze/code-context",
        data=body,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:  # noqa: S310 - operator-configured URL
            payload = json.loads(resp.read().decode("utf-8") or "{}")
    except Exception:  # noqa: BLE001 - best-effort; any failure -> fall through
        return None
    if not isinstance(payload, dict) or payload.get("status") != "success":
        return None
    result = payload.get("result")
    return result if isinstance(result, dict) else None


# ---------------------------------------------------------------------------
# Tier 2 — epistemic-graph's own AST parser (RustASTParser, engine or local)
# Tier 3 — local stdlib `ast` fallback when `epistemic_graph` isn't importable
# ---------------------------------------------------------------------------


def _local_fallback_parse(file_path: str, source: str) -> dict[str, Any]:
    """Tier 3: mirrors ``RustASTParser._parse_file_local``'s exact node/edge shape,
    using the modern ``ast.Constant`` API (never ``ast.Str``/``ast.Num``/
    ``ast.NameConstant``/``ast.Ellipsis``, all removed by Python 3.12).
    """
    try:
        tree = ast.parse(source, filename=file_path)
    except SyntaxError:
        return {
            "nodes": [],
            "edges": [],
            "symbols_extracted": 0,
            "tier": "stdlib_ast_fallback",
        }

    file_id = f"FILE::{file_path}"
    nodes: list[dict[str, Any]] = [
        {"id": file_id, "node_type": "FILE", "properties": {"path": file_path}}
    ]
    edges: list[dict[str, Any]] = []

    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            kind = "class" if isinstance(node, ast.ClassDef) else "function"
            has_doc = bool(
                node.body
                and isinstance(node.body[0], ast.Expr)
                and isinstance(node.body[0].value, ast.Constant)
                and isinstance(node.body[0].value.value, str)
            )
            sym_id = f"SYMBOL::{file_path}::{node.name}::{node.lineno}"
            nodes.append(
                {
                    "id": sym_id,
                    "node_type": "SYMBOL",
                    "properties": {
                        "name": node.name,
                        "kind": kind,
                        "line": node.lineno,
                        "end_line": getattr(node, "end_lineno", node.lineno),
                        "has_docstring": has_doc,
                    },
                }
            )
            edges.append({"source": file_id, "target": sym_id, "edge_type": "CONTAINS"})

    symbols_extracted = sum(1 for n in nodes if n["node_type"] == "SYMBOL")
    return {
        "nodes": nodes,
        "edges": edges,
        "symbols_extracted": symbols_extracted,
        "tier": "stdlib_ast_fallback",
    }


def parse_symbols(file_path: Path) -> dict[str, Any]:
    """Tier 2 (RustASTParser, engine-or-local) with a tier-3 stdlib fallback.

    Returns the parser's ``{nodes, edges, symbols_extracted}`` shape plus a
    ``"tier"`` key: ``"engine_ast"`` when ``RustASTParser`` (its own live-service
    path OR its internal local-``ast`` fallback) answered, ``"stdlib_ast_fallback"``
    only when the ``epistemic_graph`` package itself could not be imported at all.
    """
    try:
        source = file_path.read_bytes()
    except OSError:
        return {"nodes": [], "edges": [], "symbols_extracted": 0, "tier": "error"}

    try:
        from epistemic_graph.parser import RustASTParser
    except ImportError:
        result = _local_fallback_parse(str(file_path), source.decode("utf-8", "replace"))
        return result

    parser = RustASTParser()
    try:
        result = asyncio.run(parser.parse_file(str(file_path), source))
    except Exception:  # noqa: BLE001 - RustASTParser already degrades internally;
        # this only catches something outside its own handled exception set
        # (e.g. no running-loop edge cases) — degrade to the local tier here too.
        result = _local_fallback_parse(str(file_path), source.decode("utf-8", "replace"))
        return result
    result.setdefault("tier", "engine_ast")
    return result


def has_docstring_near(file_path: Path, line: int) -> bool:
    """Parser-agnostic docstring-presence heuristic keyed off a symbol's start line.

    Given a ``def``/``class`` header's 1-indexed source line (as returned by any
    parser tier), first skip forward to the header's actual closing ``:`` (a
    multi-line signature — many parameters, a multi-line base-class list — is
    common), then peek at the next few non-blank source lines for a triple-quoted
    string opener. Works identically regardless of which tier produced ``line``,
    so scripts never need to re-parse with stdlib ``ast`` just to answer "does this
    symbol have a docstring".
    """
    try:
        lines = file_path.read_text(encoding="utf-8", errors="ignore").splitlines()
    except OSError:
        return False
    idx = line - 1  # 0-indexed position of the def/class header's first line
    n = len(lines)
    # Advance to the header's closing line (bounded scan against malformed input).
    i, steps = idx, 0
    while i < n and steps < 50 and not lines[i].rstrip().endswith(":"):
        i += 1
        steps += 1
    for raw in lines[i + 1 : i + 6]:
        stripped = raw.strip()
        if not stripped:
            continue
        return stripped.startswith(('"""', "'''", 'r"""', "r'''"))
    return False


def content_fingerprint(text: str) -> str:
    """Stable content hash — mirrors the engine's ``ast_hash`` symbol property
    shape closely enough for cache-key use without needing the engine."""
    return hashlib.sha256(text.encode("utf-8", "replace")).hexdigest()[:16]


__all__ = [
    "kg_code_context",
    "parse_symbols",
    "has_docstring_near",
    "content_fingerprint",
]

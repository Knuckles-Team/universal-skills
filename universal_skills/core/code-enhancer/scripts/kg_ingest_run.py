#!/usr/bin/env python3
"""CE-032 — KG-native ingest of a code-enhancement run into graph-os.

Turns an ``enhance_repo.py`` report into a graph payload and (best-effort) ingests it into the
graph-os Knowledge Graph via the **MCP server's HTTP endpoint** — deliberately NOT via a direct
``import agent_utilities.core`` (that hard dependency is exactly what broke the old XDG/KG check in
the live run). Talking to the running MCP server keeps the skill decoupled from package internals.

Graph shape (per run):
    Repo ──OF_REPO── CodeEnhancementRun ──HAS_DOMAIN── DomainScore ──HAS_FINDING── Finding

Runs are time-stamped, so the KG's bi-temporal layer (KG-2.11) lets ``kg_query_runs.py`` compute
per-repo score deltas vs the prior run. ``build_kg_payload`` is pure and unit-testable; ingest is
best-effort and skips cleanly when no endpoint is configured.

Usage:
    python kg_ingest_run.py <report.enhance.json> [--endpoint URL] [--dry-run]
    python kg_ingest_run.py --self-test
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
from typing import Any


def _id(*parts: str) -> str:
    raw = ":".join(parts)
    return hashlib.sha1(raw.encode(), usedforsecurity=False).hexdigest()[:16]


def build_kg_payload(report: dict[str, Any]) -> dict[str, Any]:
    """Convert an enhance_repo report into ``{nodes, edges}`` (pure, deterministic)."""
    repo = report.get("repo", "unknown")
    ts = report.get("timestamp", "")
    repo_id = f"repo:{repo}"
    run_id = f"ce_run:{repo}:{ts}"

    nodes: list[dict[str, Any]] = [
        {
            "id": repo_id,
            "type": "Repo",
            "props": {"name": repo, "primary_language": report.get("primary_language")},
        },
        {
            "id": run_id,
            "type": "CodeEnhancementRun",
            "props": {
                "name": f"CE run {repo} {ts}",
                "repo": repo,
                "timestamp": ts,
                "overall_score": report.get("overall_score"),
                "overall_grade": report.get("overall_grade"),
                "domains_run": report.get("domains_run"),
                "domains_errored": report.get("domains_errored"),
            },
        },
    ]
    edges: list[dict[str, Any]] = [
        {"src": run_id, "dst": repo_id, "type": "OF_REPO"},
    ]

    for key, v in (report.get("domains") or {}).items():
        if v.get("status") != "ok":
            continue
        ds_id = f"ce_domain:{run_id}:{key}"
        nodes.append(
            {
                "id": ds_id,
                "type": "DomainScore",
                "props": {
                    "name": f"{key} ({repo})",
                    "domain": key,
                    "score": v.get("score"),
                    "grade": v.get("grade"),
                },
            }
        )
        edges.append({"src": run_id, "dst": ds_id, "type": "HAS_DOMAIN"})
        for finding in (v.get("findings") or [])[:10]:
            f_text = str(finding)
            f_id = f"ce_finding:{_id(ds_id, f_text)}"
            nodes.append(
                {
                    "id": f_id,
                    "type": "Finding",
                    "props": {"name": f_text[:120], "domain": key, "text": f_text},
                }
            )
            edges.append({"src": ds_id, "dst": f_id, "type": "HAS_FINDING"})

    return {"nodes": nodes, "edges": edges, "run_id": run_id, "repo_id": repo_id}


def ingest_via_mcp(
    payload: dict[str, Any], endpoint: str | None = None
) -> dict[str, Any]:
    """Best-effort POST of the payload to the graph-os MCP ``graph_write`` endpoint.

    Returns a status dict; never raises. When no endpoint is configured (env ``GRAPH_OS_MCP_URL``
    or ``--endpoint``), returns ``{"status": "skipped"}`` so batch runs don't fail without a KG.
    """
    url = endpoint or os.environ.get("GRAPH_OS_MCP_URL")
    if not url:
        return {
            "status": "skipped",
            "reason": "no GRAPH_OS_MCP_URL configured",
            "nodes": len(payload["nodes"]),
            "edges": len(payload["edges"]),
        }
    try:
        import urllib.request

        body = json.dumps({"action": "bulk_ingest", "payload": payload}).encode()
        req = urllib.request.Request(
            url.rstrip("/") + "/graph_write",
            data=body,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=30) as resp:  # noqa: S310 - operator-configured URL
            return {
                "status": "ingested",
                "http": resp.status,
                "nodes": len(payload["nodes"]),
                "edges": len(payload["edges"]),
            }
    except Exception as e:  # noqa: BLE001 - ingest is best-effort
        return {
            "status": "error",
            "error": str(e),
            "nodes": len(payload["nodes"]),
            "edges": len(payload["edges"]),
        }


def _self_test() -> int:
    report = {
        "repo": "fixture",
        "timestamp": "2026-01-01T00:00:00Z",
        "primary_language": "python",
        "overall_score": 72.0,
        "overall_grade": "C",
        "domains_run": 2,
        "domains_errored": 0,
        "domains": {
            "codebase": {
                "status": "ok",
                "score": 60,
                "grade": "D",
                "findings": ["f1", "f2"],
            },
            "documentation": {
                "status": "ok",
                "score": 84,
                "grade": "B",
                "findings": ["d1"],
            },
            "skipped_one": {"status": "skipped"},
        },
    }
    payload = build_kg_payload(report)
    types = {n["type"] for n in payload["nodes"]}
    assert {"Repo", "CodeEnhancementRun", "DomainScore", "Finding"} <= types, types
    assert any(e["type"] == "OF_REPO" for e in payload["edges"])
    assert any(e["type"] == "HAS_FINDING" for e in payload["edges"])
    # deterministic
    assert build_kg_payload(report) == payload
    # ingest with no endpoint = clean skip
    assert ingest_via_mcp(payload, endpoint=None)["status"] == "skipped"
    print("kg_ingest_run self-test: OK")
    return 0


def main() -> int:
    p = argparse.ArgumentParser(
        description="Ingest a code-enhancement run into graph-os (CE-032)."
    )
    p.add_argument("report", nargs="?", help="Path to a *.enhance.json report.")
    p.add_argument("--endpoint", help="graph-os MCP base URL (else $GRAPH_OS_MCP_URL).")
    p.add_argument(
        "--dry-run", action="store_true", help="Build the payload but do not ingest."
    )
    p.add_argument("--self-test", action="store_true")
    args = p.parse_args()

    if args.self_test:
        return _self_test()
    if not args.report:
        p.error("report path required (or --self-test)")

    report = json.loads(Path(args.report).read_text())
    payload = build_kg_payload(report)
    if args.dry_run:
        print(json.dumps(payload, indent=2))
        return 0
    print(json.dumps(ingest_via_mcp(payload, args.endpoint), indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

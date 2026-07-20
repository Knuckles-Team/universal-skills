#!/usr/bin/env python3
"""CE-034 — Cross-repo + bi-temporal queries over code-enhancement runs.

The genuinely new value a filesystem tool can't give at 60-repo scale: ask the KG questions that
span repos and time. Provides (a) a library of cross-repo Cypher queries to run against graph-os via
the MCP, and (b) an offline ``deltas`` mode that diffs two directories of ``enhance_repo`` reports
(current vs prior) to surface per-repo / per-domain score regressions — a bi-temporal proxy that
works before the KG is wired, and mirrors what the KG-2.11 as-of query returns once it is.

Usage:
    python kg_query_runs.py list                       # print the cross-repo query library
    python kg_query_runs.py query <name> [--endpoint U] # run one query via graph-os MCP (best-effort)
    python kg_query_runs.py deltas --current DIR --prior DIR   # offline regression diff
    python kg_query_runs.py --self-test
"""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
from typing import Any
from urllib.parse import urlsplit
from urllib.request import Request

from universal_skills._security.http import SafeHttpError, UrlPolicy, open_json

# Cross-repo Cypher library (run against graph-os; CodeEnhancementRun/DomainScore/Finding/Repo).
QUERIES: dict[str, str] = {
    "lowest_repos": (
        "MATCH (r:Repo)<-[:OF_REPO]-(run:CodeEnhancementRun) "
        "WITH r, run ORDER BY run.timestamp DESC "
        "WITH r, head(collect(run)) AS latest "
        "RETURN r.name AS repo, latest.overall_score AS score, latest.overall_grade AS grade "
        "ORDER BY score ASC LIMIT 20"
    ),
    "regressions": (
        "MATCH (r:Repo)<-[:OF_REPO]-(run:CodeEnhancementRun) "
        "WITH r, run ORDER BY run.timestamp DESC "
        "WITH r, collect(run)[0..2] AS runs WHERE size(runs) = 2 "
        "WITH r, runs[0] AS cur, runs[1] AS prev "
        "WHERE cur.overall_score < prev.overall_score "
        "RETURN r.name AS repo, prev.overall_score AS was, cur.overall_score AS now, "
        "cur.overall_score - prev.overall_score AS delta ORDER BY delta ASC"
    ),
    "weakest_domains": (
        "MATCH (run:CodeEnhancementRun)-[:HAS_DOMAIN]->(d:DomainScore) "
        "RETURN d.domain AS domain, avg(d.score) AS avg_score, count(*) AS n "
        "ORDER BY avg_score ASC LIMIT 15"
    ),
    "shared_findings": (
        "MATCH (f:Finding)<-[:HAS_FINDING]-(:DomainScore)<-[:HAS_DOMAIN]-"
        "(:CodeEnhancementRun)-[:OF_REPO]->(r:Repo) "
        "WITH f.name AS finding, collect(DISTINCT r.name) AS repos "
        "WHERE size(repos) > 1 RETURN finding, repos ORDER BY size(repos) DESC LIMIT 25"
    ),
}


def execute_via_mcp(cypher: str, endpoint: str | None = None) -> dict[str, Any]:
    """Best-effort run of a Cypher query via the graph-os MCP ``graph_query`` endpoint."""
    url = endpoint or os.environ.get("GRAPH_OS_MCP_URL")
    if not url:
        return {
            "status": "skipped",
            "reason": "no GRAPH_OS_MCP_URL configured",
        }
    try:
        body = json.dumps({"cypher": cypher}).encode()
        req = Request(
            url.rstrip("/") + "/graph_query",
            data=body,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        host = (urlsplit(url).hostname or "").lower().rstrip(".")
        rows, _ = open_json(
            req,
            policy=UrlPolicy(
                frozenset({host}),
                allow_private_hosts=frozenset({host}),
                allow_http_loopback=True,
            ),
            timeout=30,
            max_bytes=8 * 1024 * 1024,
        )
        return {"status": "ok", "rows": rows if isinstance(rows, list) else []}
    except (SafeHttpError, ValueError) as e:
        return {"status": "error", "error": type(e).__name__}


def _load_reports(d: Path) -> dict[str, dict]:
    out: dict[str, dict] = {}
    for f in sorted(Path(d).glob("*.enhance.json")):
        try:
            rep = json.loads(f.read_text())
            out[rep.get("repo", f.stem)] = rep
        except (json.JSONDecodeError, OSError):
            continue
    return out


def compute_deltas(
    current: dict[str, dict], prior: dict[str, dict]
) -> list[dict[str, Any]]:
    """Per-repo overall + per-domain score deltas (current vs prior). Pure, testable."""
    rows: list[dict[str, Any]] = []
    for repo, cur in current.items():
        prev = prior.get(repo)
        if not prev:
            rows.append(
                {
                    "repo": repo,
                    "overall_now": cur.get("overall_score"),
                    "overall_was": None,
                    "overall_delta": None,
                    "status": "new",
                }
            )
            continue
        cur_s, prev_s = cur.get("overall_score"), prev.get("overall_score")
        delta = (
            (cur_s - prev_s)
            if isinstance(cur_s, (int, float)) and isinstance(prev_s, (int, float))
            else None
        )
        domain_deltas = {}
        for dk, dv in (cur.get("domains") or {}).items():
            pv = (prev.get("domains") or {}).get(dk, {})
            if dv.get("status") == "ok" and pv.get("status") == "ok":
                cs, ps = dv.get("score"), pv.get("score")
                if (
                    isinstance(cs, (int, float))
                    and isinstance(ps, (int, float))
                    and cs != ps
                ):
                    domain_deltas[dk] = round(cs - ps, 1)
        rows.append(
            {
                "repo": repo,
                "overall_now": cur_s,
                "overall_was": prev_s,
                "overall_delta": round(delta, 1) if delta is not None else None,
                "regressed": bool(delta is not None and delta < 0),
                "domain_deltas": domain_deltas,
            }
        )
    rows.sort(
        key=lambda r: (r.get("overall_delta") is None, r.get("overall_delta") or 0)
    )
    return rows


def _self_test() -> int:
    cur = {
        "a": {
            "repo": "a",
            "overall_score": 70,
            "domains": {"codebase": {"status": "ok", "score": 60}},
        },
        "b": {"repo": "b", "overall_score": 90, "domains": {}},
    }
    prior = {
        "a": {
            "repo": "a",
            "overall_score": 80,
            "domains": {"codebase": {"status": "ok", "score": 75}},
        }
    }
    deltas = compute_deltas(cur, prior)
    by_repo = {r["repo"]: r for r in deltas}
    assert by_repo["a"]["overall_delta"] == -10 and by_repo["a"]["regressed"]
    assert by_repo["a"]["domain_deltas"]["codebase"] == -15
    assert by_repo["b"]["status"] == "new"
    assert deltas[0]["repo"] == "a"  # worst regression first
    assert "regressions" in QUERIES
    assert (
        execute_via_mcp(QUERIES["lowest_repos"], endpoint=None)["status"] == "skipped"
    )
    print("kg_query_runs self-test: OK")
    return 0


def main() -> int:
    p = argparse.ArgumentParser(
        description="Cross-repo + bi-temporal CE queries (CE-034)."
    )
    sub = p.add_subparsers(dest="cmd")
    sub.add_parser("list")
    q = sub.add_parser("query")
    q.add_argument("name", choices=list(QUERIES))
    q.add_argument("--endpoint")
    d = sub.add_parser("deltas")
    d.add_argument("--current", required=True)
    d.add_argument("--prior", required=True)
    p.add_argument("--self-test", action="store_true")
    args = p.parse_args()

    if args.self_test:
        return _self_test()
    if args.cmd == "list":
        for name, cy in QUERIES.items():
            print(f"## {name}\n{cy}\n")
        return 0
    if args.cmd == "query":
        print(json.dumps(execute_via_mcp(QUERIES[args.name], args.endpoint), indent=2))
        return 0
    if args.cmd == "deltas":
        rows = compute_deltas(
            _load_reports(Path(args.current)), _load_reports(Path(args.prior))
        )
        print(json.dumps(rows, indent=2))
        return 0
    p.print_help()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

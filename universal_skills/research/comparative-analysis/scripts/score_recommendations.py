#!/usr/bin/env python3
"""CA-015: Recommendation prioritization & critical-path ordering.

Scores each Innovation Ledger row by **leverage / (effort + risk)**, enforces that every
verified row names a measurable **success metric** (G6), and emits a dependency-respecting
**build order** (topological sort over ``depends_on``, then priority within the available set).
This replaces hand-derived "highest leverage / critical path" prose with a reproducible ranking.

Usage:
    python score_recommendations.py --ledger ledger.json
    python score_recommendations.py --ledger ledger.json --strict   # fail if a row lacks success_metric
    python score_recommendations.py --ledger ledger.json --out scored.json
    python score_recommendations.py --self-test

CONCEPT:CA-015 — Recommendation Prioritization
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

WIRE_FIELDS = ("entry_point", "target_module", "extends_concept")


def priority_score(row: dict) -> float:
    """leverage / (effort + risk), damped by verification status. Higher = build sooner."""
    lev = float(row.get("leverage", 3))
    eff = float(row.get("effort", 3))
    risk = float(row.get("risk", 3))
    base = lev / max(1.0, eff + risk)
    factor = {"verified": 1.0, "claimed-only": 0.6, "refuted": 0.0}.get(
        row.get("verified", "claimed-only"), 0.6
    )
    return round(base * factor, 4)


def wire_issues(row: dict) -> list[str]:
    issues = [f"missing {f}" for f in WIRE_FIELDS if not row.get(f)]
    if isinstance(row.get("hops"), int) and row["hops"] > 3:
        issues.append(f"hops={row['hops']} > 3 (Wire-First)")
    return issues


def build_order(rows: list[dict]) -> list[str]:
    """Topological order over depends_on, breaking ties by priority_score (desc)."""
    by_id = {r["id"]: r for r in rows if r.get("id")}
    score = {rid: priority_score(r) for rid, r in by_id.items()}
    ordered: list[str] = []
    placed: set[str] = set()
    remaining = set(by_id)
    while remaining:
        ready = [
            rid for rid in remaining
            if all(dep in placed or dep not in by_id for dep in by_id[rid].get("depends_on", []))
        ]
        if not ready:  # dependency cycle — fall back to priority over whatever's left
            ready = list(remaining)
        ready.sort(key=lambda rid: score[rid], reverse=True)
        nxt = ready[0]
        ordered.append(nxt)
        placed.add(nxt)
        remaining.discard(nxt)
    return ordered


def score_ledger(rows: list[dict], *, strict: bool = False) -> dict:
    scored = []
    metric_gaps, wire_gaps = [], []
    for row in rows:
        r = {**row, "priority_score": priority_score(row), "wire_issues": wire_issues(row)}
        scored.append(r)
        if r["verified"] == "verified" and not row.get("success_metric"):
            metric_gaps.append(row.get("id", "?"))
        if r["wire_issues"]:
            wire_gaps.append({"id": row.get("id", "?"), "issues": r["wire_issues"]})
    scored.sort(key=lambda r: r["priority_score"], reverse=True)
    order = build_order(rows)
    result = {
        "ranked": scored,
        "build_order": order,
        "highest_leverage": [r["id"] for r in scored[:3]],
        "missing_success_metric": metric_gaps,
        "wire_violations": wire_gaps,
        "strict_pass": not (metric_gaps or wire_gaps) if strict else True,
    }
    return result


def _self_test() -> int:
    rows = [
        {"id": "roles", "leverage": 4, "effort": 1, "risk": 1, "verified": "verified",
         "success_metric": "m", "entry_point": "x", "target_module": "y", "extends_concept": "Z"},
        {"id": "retrieval", "leverage": 5, "effort": 3, "risk": 2, "verified": "verified",
         "success_metric": "m", "entry_point": "x", "target_module": "y", "extends_concept": "Z",
         "depends_on": ["roles"]},
        {"id": "nometric", "leverage": 5, "effort": 1, "risk": 1, "verified": "verified",
         "entry_point": "x", "target_module": "y", "extends_concept": "Z"},
    ]
    res = score_ledger(rows, strict=True)
    # roles: 4/2=2.0 ; nometric: 5/2=2.5 ; retrieval: 5/5=1.0
    assert res["ranked"][0]["id"] == "nometric", [r["id"] for r in res["ranked"]]
    # Build order must place roles before retrieval (dependency), regardless of score.
    order = res["build_order"]
    assert order.index("roles") < order.index("retrieval"), order
    assert res["missing_success_metric"] == ["nometric"], res["missing_success_metric"]
    assert res["strict_pass"] is False, res
    print("self-test OK")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description="Recommendation prioritization (CA-015)")
    ap.add_argument("--ledger", help="Path to ledger.json/.jsonl")
    ap.add_argument("--strict", action="store_true", help="Fail if any row lacks success_metric / wiring")
    ap.add_argument("--out", help="Write the scored ledger here")
    ap.add_argument("--self-test", action="store_true")
    args = ap.parse_args()

    if args.self_test or not args.ledger:
        return _self_test()

    p = Path(args.ledger)
    text = p.read_text()
    rows = ([json.loads(line) for line in text.splitlines() if line.strip()]
            if p.suffix == ".jsonl" else json.loads(text))
    result = score_ledger(rows, strict=args.strict)
    print(json.dumps(
        {k: v for k, v in result.items() if k != "ranked"}, indent=2
    ))
    if args.out:
        Path(args.out).write_text(json.dumps(result["ranked"], indent=2))
        print(f"wrote {args.out}", file=sys.stderr)
    if args.strict and not result["strict_pass"]:
        print("STRICT FAIL: success-metric or wiring gaps (see above).", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

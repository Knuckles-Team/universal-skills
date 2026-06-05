#!/usr/bin/env python3
"""CA-013: Source-claim verification (marketing-vs-code gate).

The first, deterministic layer of claim verification: for each ledger row that cites a
``source_ref`` (``{file, lines}``) in a cloned source tree, confirm the cited region actually
exists and contains the expected evidence tokens. Rows are stamped:

    verified      — file + line range exist and an evidence token is present.
    claimed-only  — region exists but no evidence token was found (needs human/LLM review).
    refuted       — file missing or the cited line range is out of bounds.

This prevents assimilating a feature that lives only in a blog post. The SKILL pairs this with an
adversarial LLM refutation pass for the top-N rows (the second, semantic layer).

Usage:
    python verify_claims.py --ledger ledger.json --source-root /path/to/cloned/source
    python verify_claims.py --ledger ledger.json --source-root . --out verified.json
    python verify_claims.py --self-test

CONCEPT:CA-013 — Source-Claim Verification
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

# Candidate evidence tokens auto-derived from a claim when none are given explicitly:
# identifiers, dotted names, numbers, $amounts, CamelCase, snake_case.
_EVIDENCE = re.compile(r"[A-Za-z_][A-Za-z0-9_.]{2,}|\$?\d[\d,]*\.?\d*")
_STOP = {"the", "and", "for", "with", "that", "this", "from", "into", "emit", "emits", "uses"}


def _parse_lines(spec: str) -> tuple[int, int] | None:
    m = re.match(r"(\d+)\s*-\s*(\d+)", str(spec))
    if m:
        return int(m.group(1)), int(m.group(2))
    if str(spec).isdigit():
        return int(spec), int(spec)
    return None


def _candidate_tokens(row: dict) -> list[str]:
    if row.get("evidence_tokens"):
        return [str(t) for t in row["evidence_tokens"]]
    toks = [t for t in _EVIDENCE.findall(row.get("claim", "")) if t.lower() not in _STOP]
    # Prefer distinctive tokens: those with digits, dots, or mixed case.
    distinctive = [t for t in toks if any(c.isdigit() for c in t) or "." in t or not t.islower()]
    return distinctive or toks


def verify_row(row: dict, source_root: Path) -> dict:
    sr = row.get("source_ref") or {}
    fname = sr.get("file")
    if not fname:
        return {**row, "verified": "claimed-only", "verification_note": "no source_ref.file"}

    # Resolve the file: exact, then by-basename search (handles nested paths).
    path = source_root / fname
    if not path.is_file():
        matches = list(source_root.rglob(Path(fname).name))
        path = matches[0] if matches else path
    if not path.is_file():
        return {**row, "verified": "refuted", "verification_note": f"file not found: {fname}"}

    lines = path.read_text(errors="ignore").splitlines()
    rng = _parse_lines(sr.get("lines", ""))
    if rng:
        lo, hi = rng
        if lo > len(lines):
            return {**row, "verified": "refuted",
                    "verification_note": f"lines {lo}-{hi} out of range (file has {len(lines)})"}
        region = "\n".join(lines[max(0, lo - 1):min(len(lines), hi)])
    else:
        region = "\n".join(lines)

    tokens = _candidate_tokens(row)
    hits = [t for t in tokens if t in region]
    if hits:
        return {**row, "verified": "verified",
                "verification_note": f"found {hits[:5]} in {path.name}:{sr.get('lines', 'all')}"}
    return {**row, "verified": "claimed-only",
            "verification_note": f"region exists but tokens {tokens[:5]} absent — review"}


def verify_ledger(rows: list[dict], source_root: Path) -> dict:
    out = [verify_row(r, source_root) for r in rows]
    summary: dict[str, int] = {"verified": 0, "claimed-only": 0, "refuted": 0}
    for r in out:
        summary[r["verified"]] = summary.get(r["verified"], 0) + 1
    return {"rows": out, "summary": summary}


def _self_test() -> int:
    import tempfile

    with tempfile.TemporaryDirectory() as d:
        src = Path(d) / "agent.py"
        src.write_text("\n".join(f"line {i}" for i in range(1, 50)) +
                       "\nLEARNING_SEMAPHORE = asyncio.Semaphore(4)\n")
        rows = [
            {"id": "ok", "claim": "uses LEARNING_SEMAPHORE Semaphore(4)",
             "source_ref": {"file": "agent.py", "lines": "50-51"}},
            {"id": "badfile", "claim": "x", "source_ref": {"file": "ghost.py", "lines": "1-2"}},
            {"id": "outofrange", "claim": "y", "source_ref": {"file": "agent.py", "lines": "9000-9001"}},
            {"id": "noevidence", "claim": "mentions Nonexistent_Token_XYZ",
             "source_ref": {"file": "agent.py", "lines": "1-3"}},
        ]
        res = verify_ledger(rows, Path(d))
        byid = {r["id"]: r["verified"] for r in res["rows"]}
        assert byid["ok"] == "verified", byid
        assert byid["badfile"] == "refuted", byid
        assert byid["outofrange"] == "refuted", byid
        assert byid["noevidence"] == "claimed-only", byid
        assert res["summary"]["verified"] == 1, res["summary"]
    print("self-test OK")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description="Source-claim verification (CA-013)")
    ap.add_argument("--ledger", help="Path to ledger.json/.jsonl")
    ap.add_argument("--source-root", default=".", help="Root of the cloned source repo")
    ap.add_argument("--out", help="Write the verified ledger to this path")
    ap.add_argument("--self-test", action="store_true")
    args = ap.parse_args()

    if args.self_test or not args.ledger:
        return _self_test()

    p = Path(args.ledger)
    text = p.read_text()
    rows = ([json.loads(line) for line in text.splitlines() if line.strip()]
            if p.suffix == ".jsonl" else json.loads(text))
    result = verify_ledger(rows, Path(args.source_root))
    print(json.dumps(result["summary"], indent=2))
    if args.out:
        Path(args.out).write_text(json.dumps(result["rows"], indent=2))
        print(f"wrote {args.out}", file=sys.stderr)
    # Non-zero exit if anything was refuted, so CI/agents notice.
    return 1 if result["summary"].get("refuted") else 0


if __name__ == "__main__":
    raise SystemExit(main())

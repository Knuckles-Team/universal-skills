#!/usr/bin/env python3
"""Reduce verbose GitHub ``gith__pulls action=list`` output to a compact PR table.

``gith__pulls action=list`` returns large payloads per repo that the harness
spills to a file. Never read that raw — feed the file(s) here. This script:
  * accepts one or more ``list`` result files (or stdin),
  * flattens them to one row per open pull request,
  * computes age in days and a few review signals,
  * optionally merges per-PR detail from ``gith__pulls action=get`` dumps
    (which carry ``mergeable_state``, ``additions``, ``deletions``, review info)
    so the row gets a verdict-ready ``mergeable_state``/``checks`` column,
  * emits a compact JSON list and/or a Markdown table grouped by repo.

Pure JSON transform: no network, no auth, stdlib only. Tolerates a raw MCP result
object ``{"status","message","data":[...]}``, a bare list, or a single PR object.

Usage:
    python summarize_prs.py r1_pulls.json r2_pulls.json --format md
    python summarize_prs.py *_pulls.json --detail pr_get_*.json --format md
    cat pulls.json | python summarize_prs.py --format json
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from typing import Any


def _extract(blob: Any) -> list[dict]:
    """Pull the list of PR objects out of whatever shape we were handed."""
    if isinstance(blob, list):
        return [p for p in blob if isinstance(p, dict)]
    if isinstance(blob, dict):
        for key in ("data", "pull_requests", "pulls", "items"):
            v = blob.get(key)
            if isinstance(v, list):
                return [p for p in v if isinstance(p, dict)]
        # a single PR object
        if "number" in blob and ("title" in blob or "head" in blob):
            return [blob]
    return []


def _load(paths: list[str]) -> list[dict]:
    out: list[dict] = []
    if not paths:
        out.extend(_extract(json.load(sys.stdin)))
        return out
    for p in paths:
        try:
            with open(p) as fh:
                out.extend(_extract(json.load(fh)))
        except (OSError, json.JSONDecodeError) as e:
            print(f"warning: skipping {p}: {e}", file=sys.stderr)
    return out


def _age_days(created: str | None) -> int | None:
    if not created:
        return None
    try:
        dt = datetime.fromisoformat(created.replace("Z", "+00:00"))
        return (datetime.now(timezone.utc) - dt).days
    except ValueError:
        return None


def _repo_of(pr: dict) -> str:
    base = pr.get("base") or {}
    repo = base.get("repo") or {}
    return repo.get("full_name") or pr.get("_repo") or "?"


def _row(pr: dict) -> dict:
    return {
        "repo": _repo_of(pr),
        "number": pr.get("number"),
        "title": (pr.get("title") or "").strip(),
        "author": (pr.get("user") or {}).get("login"),
        "draft": bool(pr.get("draft")),
        "base": (pr.get("base") or {}).get("ref"),
        "head": (pr.get("head") or {}).get("ref"),
        "age_days": _age_days(pr.get("created_at")),
        "comments": pr.get("comments"),
        "review_comments": pr.get("review_comments"),
        # present only when enriched from action=get:
        "mergeable_state": pr.get("mergeable_state"),
        "additions": pr.get("additions"),
        "deletions": pr.get("deletions"),
    }


def reduce_prs(pulls: list[dict], detail: list[dict]) -> list[dict]:
    by_key: dict[tuple, dict] = {}
    for pr in pulls:
        r = _row(pr)
        by_key[(r["repo"], r["number"])] = r
    # merge enrichment (action=get carries mergeable_state/additions/deletions)
    for pr in detail:
        r = _row(pr)
        key = (r["repo"], r["number"])
        if key in by_key:
            for f in ("mergeable_state", "additions", "deletions", "review_comments"):
                if r.get(f) is not None:
                    by_key[key][f] = r[f]
        else:
            by_key[key] = r
    rows = list(by_key.values())
    rows.sort(key=lambda r: (r["repo"], r["number"] or 0))
    return rows


def to_md(rows: list[dict]) -> str:
    if not rows:
        return "✅ No open pull requests found across the swept accounts."
    out: list[str] = []
    repo = None
    for r in rows:
        if r["repo"] != repo:
            repo = r["repo"]
            out.append(f"\n### {repo}\n")
            out.append("| PR | Title | Author | Base←Head | Age | Draft | Mergeable | Size |")
            out.append("|----|-------|--------|-----------|-----|-------|-----------|------|")
        title = (r["title"][:50] + "…") if len(r["title"]) > 51 else r["title"]
        size = (
            f"+{r['additions']}/-{r['deletions']}"
            if r.get("additions") is not None
            else "—"
        )
        age = f"{r['age_days']}d" if r["age_days"] is not None else "—"
        out.append(
            f"| #{r['number']} | {title} | {r['author'] or '—'} | "
            f"{r['base'] or '?'}←{r['head'] or '?'} | {age} | "
            f"{'yes' if r['draft'] else ''} | {r.get('mergeable_state') or '?'} | {size} |"
        )
    out.append(f"\n**{len(rows)} open PR(s)** across {len({r['repo'] for r in rows})} repo(s).")
    return "\n".join(out)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("files", nargs="*", help="gith__pulls list result file(s); omit to read stdin")
    ap.add_argument("--detail", nargs="*", default=[], help="gith__pulls get result file(s) to enrich rows")
    ap.add_argument("--format", choices=["json", "md"], default="md")
    args = ap.parse_args()

    rows = reduce_prs(_load(args.files), _load(args.detail) if args.detail else [])
    if args.format == "json":
        print(json.dumps(rows, indent=2))
    else:
        print(to_md(rows))


if __name__ == "__main__":
    main()

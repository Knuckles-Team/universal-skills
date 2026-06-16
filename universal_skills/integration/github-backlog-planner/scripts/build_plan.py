#!/usr/bin/env python3
"""Turn a collected list of GitHub issues/PRs into a prioritized Markdown plan.

Pure JSON -> Markdown transform. Performs NO network calls and needs NO auth: the
agent collects items via the ``gith__*`` MCP tools and feeds them here. This keeps
the script runnable in any environment (no ``gh`` CLI, no ``GITHUB_*`` token).

Input (stdin or --input PATH): a JSON list of item objects. Each item:
    {
      "account":   "Knucklessg1" | "Knuckles-Team",   # owner / org login
      "repo":      "geniusbot",                          # repo name (no owner)
      "kind":      "issue" | "pr",
      "number":    42,
      "title":     "...",
      "url":       "https://github.com/...",             # html_url
      "state":     "open",
      "status":    "addressed" | "in-progress" | "needs-action",  # triage outcome
      "evidence":  "merged PR #51 landed fix in foo.py",  # why this status (free text)
      "recommendation": "Close as fixed by #51",          # concrete next step
      "priority":  "high" | "medium" | "low",            # optional, default medium
      "labels":    ["bug", ...]                            # optional
    }

Output: a grouped, prioritized Markdown remediation plan on stdout.

Usage:
    python build_plan.py < items.json
    python build_plan.py --input items.json --title "Backlog Plan"
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import defaultdict
from typing import Any

STATUS_ORDER = {"needs-action": 0, "in-progress": 1, "addressed": 2}
STATUS_LABEL = {
    "needs-action": "🔴 Needs action",
    "in-progress": "🟡 In progress",
    "addressed": "🟢 Addressed",
}
PRIORITY_ORDER = {"high": 0, "medium": 1, "low": 2}
PRIORITY_BADGE = {"high": "P1", "medium": "P2", "low": "P3"}


def _norm(item: dict[str, Any]) -> dict[str, Any]:
    status = (item.get("status") or "needs-action").strip().lower()
    if status not in STATUS_ORDER:
        status = "needs-action"
    priority = (item.get("priority") or "medium").strip().lower()
    if priority not in PRIORITY_ORDER:
        priority = "medium"
    return {
        "account": item.get("account") or "(unknown)",
        "repo": item.get("repo") or "(unknown)",
        "kind": (item.get("kind") or "issue").strip().lower(),
        "number": item.get("number"),
        "title": (item.get("title") or "(no title)").strip(),
        "url": item.get("url") or "",
        "status": status,
        "evidence": (item.get("evidence") or "").strip(),
        "recommendation": (item.get("recommendation") or "").strip(),
        "priority": priority,
        "labels": item.get("labels") or [],
    }


def _sort_key(it: dict[str, Any]) -> tuple:
    return (
        STATUS_ORDER[it["status"]],
        PRIORITY_ORDER[it["priority"]],
        0 if it["kind"] == "pr" else 1,
        it["number"] if isinstance(it["number"], int) else 1 << 30,
    )


def build_markdown(items: list[dict[str, Any]], title: str) -> str:
    items = [_norm(i) for i in items]
    out: list[str] = [f"# {title}", ""]

    # ---- Summary -------------------------------------------------------------
    by_status: dict[str, int] = defaultdict(int)
    by_kind: dict[str, int] = defaultdict(int)
    for it in items:
        by_status[it["status"]] += 1
        by_kind[it["kind"]] += 1
    out.append(
        f"**{len(items)} open item(s)** — "
        f"{by_kind.get('issue', 0)} issue(s), {by_kind.get('pr', 0)} PR(s). "
        f"{by_status.get('needs-action', 0)} need action, "
        f"{by_status.get('in-progress', 0)} in progress, "
        f"{by_status.get('addressed', 0)} likely closable."
    )
    out.append("")

    # ---- Closable now (addressed) -------------------------------------------
    closable = sorted((i for i in items if i["status"] == "addressed"), key=_sort_key)
    if closable:
        out.append("## ✅ Verified addressed — safe to close")
        out.append("")
        for it in closable:
            ref = f"{it['account']}/{it['repo']}#{it['number']}"
            out.append(f"- [{ref}]({it['url']}) — {it['title']}")
            if it["evidence"]:
                out.append(f"  - _Why:_ {it['evidence']}")
            if it["recommendation"]:
                out.append(f"  - _Action:_ {it['recommendation']}")
        out.append("")

    # ---- Grouped action plan: account -> repo -------------------------------
    out.append("## Action plan")
    out.append("")
    grouped: dict[str, dict[str, list]] = defaultdict(lambda: defaultdict(list))
    for it in items:
        if it["status"] == "addressed":
            continue  # already covered above
        grouped[it["account"]][it["repo"]].append(it)

    if not grouped:
        out.append("_No outstanding items requiring action._")
        out.append("")
    for account in sorted(grouped):
        out.append(f"### {account}")
        out.append("")
        for repo in sorted(grouped[account]):
            repo_items = sorted(grouped[account][repo], key=_sort_key)
            out.append(f"#### `{repo}` ({len(repo_items)})")
            out.append("")
            out.append("| | # | Type | Title | Status | Recommended next step |")
            out.append("|---|---|---|---|---|---|")
            for it in repo_items:
                badge = PRIORITY_BADGE[it["priority"]]
                num = (
                    f"[#{it['number']}]({it['url']})"
                    if it["url"]
                    else f"#{it['number']}"
                )
                kind = "PR" if it["kind"] == "pr" else "issue"
                title = it["title"].replace("|", "\\|")
                rec = (it["recommendation"] or "—").replace("|", "\\|")
                status = STATUS_LABEL[it["status"]]
                out.append(f"| {badge} | {num} | {kind} | {title} | {status} | {rec} |")
            out.append("")

    return "\n".join(out).rstrip() + "\n"


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--input", help="Path to items JSON (default: stdin).")
    ap.add_argument(
        "--title",
        default="GitHub Backlog Remediation Plan",
        help="Plan title.",
    )
    args = ap.parse_args(argv)

    raw = open(args.input, encoding="utf-8").read() if args.input else sys.stdin.read()
    if not raw.strip():
        print("error: no input JSON provided", file=sys.stderr)
        return 2
    data = json.loads(raw)
    # Accept either a bare list or {"items": [...]}.
    items = data["items"] if isinstance(data, dict) else data
    if not isinstance(items, list):
        print("error: expected a JSON list of items", file=sys.stderr)
        return 2

    sys.stdout.write(build_markdown(items, args.title))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

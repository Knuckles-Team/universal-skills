#!/usr/bin/env python3
"""Deterministic safety classifier for autonomous PR/issue resolution.

Given enriched item(s) — a PR or issue object (from `gith__get_pull_request` /
`gith__get_issue`) augmented by the agent with `checks_state` and, for issues,
`resolved_evidence` — emit a conservative verdict:

  * safe_merge  — PR is mergeable, all checks green, and fits a low-risk allow
                  class (default: dependabot/renovate patch|minor bumps). Never
                  for major bumps, drafts, dirty/blocked merges, or failing checks.
  * safe_close  — PR: stale AND conflicted (abandoned); OR `superseded_by` given.
                  Issue: ONLY when `resolved_evidence` (a fixing commit/PR/file)
                  is supplied — an unverified issue is NEVER auto-closable.
  * skip        — anything else: leave for a human (with the reason).

This script makes NO network calls and writes nothing. It only decides. The skill
still requires explicit confirmation (or a configured autonomy level) before any
write happens. Pure stdlib JSON transform.

Input fields per item (extra fields ignored):
  type            "pr" | "issue"  (inferred from `pull_request`/`head` if absent)
  number, repo, title, draft, mergeable_state, author (login or {login}),
  checks_state    "success" | "failure" | "pending" | None   (agent supplies)
  age_days        int
  resolved_evidence  str  (issues only — e.g. "fixed by #123 / commit abc123")
  superseded_by      str  (PRs only — e.g. "#456")
  allow_class        str  (override; e.g. "approved" to permit a human-approved PR)

Usage:
  python classify_safe.py items.json --format md
  cat item.json | python classify_safe.py --stale-days 60 --format json
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from typing import Any

SEMVER = re.compile(r"(\d+)\.(\d+)\.(\d+)")
BUMP = re.compile(r"bump .+ from (\S+) to (\S+)", re.I)


def _items(blob: Any) -> list[dict]:
    if isinstance(blob, list):
        return [i for i in blob if isinstance(i, dict)]
    if isinstance(blob, dict):
        for k in ("data", "items"):
            if isinstance(blob.get(k), list):
                return [i for i in blob[k] if isinstance(i, dict)]
        return [blob]
    return []


def _author(item: dict) -> str:
    a = item.get("author") or item.get("user") or ""
    return (a.get("login") if isinstance(a, dict) else a) or ""


def _is_pr(item: dict) -> bool:
    t = item.get("type")
    if t:
        return t == "pr"
    return bool(item.get("pull_request") or item.get("head") or item.get("base"))


def _bump_level(title: str) -> str | None:
    """patch|minor|major for a 'Bump X from a.b.c to d.e.f' title, else None."""
    m = BUMP.search(title or "")
    if not m:
        return None
    a, b = SEMVER.search(m.group(1)), SEMVER.search(m.group(2))
    if not (a and b):
        return None
    av, bv = [int(x) for x in a.groups()], [int(x) for x in b.groups()]
    if bv[0] != av[0]:
        return "major"
    if bv[1] != av[1]:
        return "minor"
    return "patch"


def classify(item: dict, stale_days: int, allow_major: bool, classes: set[str]) -> dict:
    repo, num = item.get("repo", "?"), item.get("number", "?")
    out = {"repo": repo, "number": num, "verdict": "skip", "reason": "", "action": "none"}

    if not _is_pr(item):  # ----- ISSUE -----
        ev = item.get("resolved_evidence")
        if ev:
            out.update(verdict="safe_close", action="close",
                       reason=f"resolved — evidence: {ev}")
        else:
            out["reason"] = "issue not verified resolved (no resolved_evidence) — human triage"
        return out

    # ----- PULL REQUEST -----
    if item.get("draft"):
        out["reason"] = "draft PR"
        return out
    ms = (item.get("mergeable_state") or "").lower()
    checks = (item.get("checks_state") or "").lower()
    author = _author(item).lower()
    title = item.get("title") or ""
    bot = ("dependabot" in author) or ("renovate" in author)
    level = _bump_level(title)
    allow = item.get("allow_class") or ""

    # safe_merge gate — ALL must hold
    merge_class_ok = (
        (bot and level in ("patch", "minor"))
        or (bot and level == "major" and allow_major)
        or (allow == "approved")
    ) and ((f"dependabot-{level}" in classes) if bot and level else allow == "approved")
    if ms == "clean" and checks == "success" and merge_class_ok:
        cls = f"{author} {level} bump" if bot else allow
        out.update(verdict="safe_merge", action="merge",
                   reason=f"clean + checks green + allow-class ({cls})")
        return out

    # safe_close gate — abandoned/superseded
    if item.get("superseded_by"):
        out.update(verdict="safe_close", action="close",
                   reason=f"superseded by {item['superseded_by']}")
        return out
    age = item.get("age_days")
    if ms == "dirty" and isinstance(age, int) and age > stale_days:
        out.update(verdict="safe_close", action="close",
                   reason=f"stale {age}d + merge conflicts (abandoned) — confirm before close")
        return out

    # otherwise skip with the blocking reason
    why = []
    if ms and ms != "clean":
        why.append(f"mergeable_state={ms}")
    if checks and checks != "success":
        why.append(f"checks={checks}")
    if not merge_class_ok:
        why.append("not in auto-merge allow-class")
    out["reason"] = "; ".join(why) or "needs human review"
    return out


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("files", nargs="*", help="item JSON file(s); omit for stdin")
    ap.add_argument("--stale-days", type=int, default=60)
    ap.add_argument("--allow-major", action="store_true", help="permit dependabot MAJOR bumps (off by default)")
    ap.add_argument("--allow-classes", default="dependabot-patch,dependabot-minor",
                    help="comma list of auto-merge classes")
    ap.add_argument("--format", choices=["json", "md"], default="md")
    args = ap.parse_args()
    classes = {c.strip() for c in args.allow_classes.split(",") if c.strip()}

    blobs: list[dict] = []
    if args.files:
        for f in args.files:
            with open(f) as fh:
                blobs.extend(_items(json.load(fh)))
    else:
        blobs.extend(_items(json.load(sys.stdin)))

    verdicts = [classify(i, args.stale_days, args.allow_major, classes) for i in blobs]
    if args.format == "json":
        print(json.dumps(verdicts, indent=2))
        return
    icon = {"safe_merge": "✅ merge", "safe_close": "🗑️ close", "skip": "⏭️ skip"}
    print("| Item | Verdict | Reason |")
    print("|------|---------|--------|")
    for v in verdicts:
        print(f"| {v['repo']}#{v['number']} | {icon.get(v['verdict'], v['verdict'])} | {v['reason']} |")
    n_m = sum(v["verdict"] == "safe_merge" for v in verdicts)
    n_c = sum(v["verdict"] == "safe_close" for v in verdicts)
    n_s = sum(v["verdict"] == "skip" for v in verdicts)
    print(f"\n**{n_m} safe-merge · {n_c} safe-close · {n_s} skip** "
          f"(of {len(verdicts)}). Writes require explicit confirmation.")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""CA-017: Source pinning, incremental diff & analysis cache.

Makes repeated comparative-analysis runs reproducible and cheap:

- **Pin**: record the analyzed source's git remote + commit SHA + timestamp, so a report/ledger
  always says exactly what was analyzed (the source repo is a moving target).
- **Incremental**: given a prior commit, compute which files changed, then mark which prior-ledger
  rows are *stale* (their `source_ref.file` changed) — only those need re-analysis.
- **Cache**: persist pins/ledgers under ``~/.scholarx/analysis/<repo>@<sha>/`` so re-running
  against an unchanged source is instant.

Usage:
    python pin_source.py --source-root /path/to/clone                 # print pin
    python pin_source.py --source-root /path/to/clone --since <sha>   # + changed files
    python pin_source.py --source-root /path/to/clone --prev-ledger old.json --since <sha>
    python pin_source.py --source-root /path/to/clone --cache --ledger ledger.json
    python pin_source.py --check --repo quarqlabs/agent-oss --commit b683860
    python pin_source.py --self-test

CONCEPT:CA-017 — Source Pinning & Incremental Cache
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

CACHE_ROOT = Path.home() / ".scholarx" / "analysis"


def _git(root: Path, *args: str) -> str:
    try:
        return subprocess.run(
            ["git", "-C", str(root), *args],
            capture_output=True, text=True, timeout=15, check=False,
        ).stdout.strip()
    except Exception:
        return ""


def _repo_slug(remote: str) -> str:
    """Normalize a git remote URL to ``owner/name``."""
    m = re.search(r"[:/]([^/:]+/[^/]+?)(?:\.git)?/?$", remote or "")
    return m.group(1) if m else (remote or "unknown")


def git_info(root: Path) -> dict:
    remote = _git(root, "config", "--get", "remote.origin.url")
    return {
        "repo": _repo_slug(remote),
        "remote": remote,
        "commit": _git(root, "rev-parse", "HEAD") or "unknown",
        "branch": _git(root, "rev-parse", "--abbrev-ref", "HEAD") or "unknown",
    }


def changed_files(root: Path, since: str) -> list[str]:
    out = _git(root, "diff", "--name-only", f"{since}..HEAD")
    return [line for line in out.splitlines() if line.strip()]


def stale_rows(ledger_rows: list[dict], changed: list[str]) -> list[str]:
    """Return ids of ledger rows whose cited source file changed (pure)."""
    changed_names = {Path(c).name for c in changed}
    stale = []
    for row in ledger_rows:
        f = (row.get("source_ref") or {}).get("file", "")
        if f and Path(f).name in changed_names:
            stale.append(row.get("id", "?"))
    return stale


def cache_dir(repo: str, commit: str) -> Path:
    safe_repo = repo.replace("/", "__")
    return CACHE_ROOT / f"{safe_repo}@{commit[:12]}"


def make_pin(root: Path, *, now: str | None = None) -> dict:
    info = git_info(root)
    info["analyzed_at"] = now or datetime.now(timezone.utc).isoformat()
    info["source_root"] = str(root)
    return info


def _self_test() -> int:
    rows = [
        {"id": "a", "source_ref": {"file": "agent.py", "lines": "1-9"}},
        {"id": "b", "source_ref": {"file": "tools/x.py", "lines": "1-9"}},
        {"id": "c", "source_ref": {"file": "unchanged.py", "lines": "1-9"}},
    ]
    stale = stale_rows(rows, ["src/agent.py", "tools/x.py"])
    assert set(stale) == {"a", "b"}, stale
    assert _repo_slug("git@github.com:quarqlabs/agent-oss.git") == "quarqlabs/agent-oss"
    assert _repo_slug("https://github.com/quarqlabs/agent-oss.git") == "quarqlabs/agent-oss"
    cd = cache_dir("quarqlabs/agent-oss", "b683860abcdef")
    assert cd.name == "quarqlabs__agent-oss@b683860abcde", cd
    pin = make_pin(Path("."), now="2026-06-04T00:00:00+00:00")
    assert pin["analyzed_at"] == "2026-06-04T00:00:00+00:00" and "repo" in pin
    print("self-test OK")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description="Source pinning & incremental cache (CA-017)")
    ap.add_argument("--source-root", help="Root of the cloned source repo")
    ap.add_argument("--since", help="Prior commit SHA to diff against (incremental)")
    ap.add_argument("--prev-ledger", help="Prior ledger.json to mark stale rows")
    ap.add_argument("--ledger", help="Current ledger.json to cache")
    ap.add_argument("--cache", action="store_true", help="Persist pin/ledger under the cache dir")
    ap.add_argument("--check", action="store_true", help="Check if a cache exists for --repo/--commit")
    ap.add_argument("--repo")
    ap.add_argument("--commit")
    ap.add_argument("--self-test", action="store_true")
    args = ap.parse_args()

    if args.self_test:
        return _self_test()

    if args.check:
        if not (args.repo and args.commit):
            print("ERROR: --check needs --repo and --commit", file=sys.stderr)
            return 2
        cd = cache_dir(args.repo, args.commit)
        exists = cd.is_dir()
        print(json.dumps({"cached": exists, "cache_dir": str(cd)}))
        return 0 if exists else 3

    if not args.source_root:
        return _self_test()

    root = Path(args.source_root)
    result: dict = {"pin": make_pin(root)}

    if args.since:
        changed = changed_files(root, args.since)
        result["changed_files"] = changed
        if args.prev_ledger:
            prev = json.loads(Path(args.prev_ledger).read_text())
            prev_rows = prev if isinstance(prev, list) else prev.get("rows", [])
            result["stale_row_ids"] = stale_rows(prev_rows, changed)
            result["reuse_row_ids"] = [
                r.get("id") for r in prev_rows if r.get("id") not in result["stale_row_ids"]
            ]

    if args.cache:
        cd = cache_dir(result["pin"]["repo"], result["pin"]["commit"])
        cd.mkdir(parents=True, exist_ok=True)
        (cd / "pin.json").write_text(json.dumps(result["pin"], indent=2))
        if args.ledger:
            (cd / "ledger.json").write_text(Path(args.ledger).read_text())
        result["cache_dir"] = str(cd)

    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

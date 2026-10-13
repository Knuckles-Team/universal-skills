"""Retain the shared clone scan, excluding only pairs of verified schemas.

The verifier runs against each materialized Git tree, not the working tree.
Every handwritten-to-handwritten or handwritten-to-generated pair remains.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import stat
import subprocess
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from verify_generated_schemas import MANIFEST, load_policy


def tree_state(root: Path) -> dict:
    """Bind every file and mode; verification cannot rewrite handwritten code."""
    state = {}
    for path in sorted(root.rglob("*")):
        mode = path.lstat().st_mode
        if stat.S_ISDIR(mode):
            continue
        if not stat.S_ISREG(mode):
            raise ValueError("Verification tree contains a link or special file")
        state[path.relative_to(root).as_posix()] = (
            stat.S_IMODE(mode),
            hashlib.sha256(path.read_bytes()).hexdigest(),
        )
    return state


def verified_artifacts(snapshot: Path, project: Path) -> dict:
    if not (snapshot / MANIFEST).exists():
        return {}
    original_tree = tree_state(snapshot)
    policy = load_policy(snapshot)
    python = os.environ.get(
        "GENERATED_SCHEMA_PYTHON", str(project / ".venv/bin/python")
    )
    result = subprocess.run(
        [
            python,
            str(snapshot / "scripts/verify_generated_schemas.py"),
            "--root",
            str(snapshot),
        ],
        cwd=snapshot,
        check=False,
        capture_output=True,
        text=True,
        timeout=60,
        env={
            **os.environ,
            "PYTHONDONTWRITEBYTECODE": "1",
            "MCP_FLEET_REGISTRATION": "false",
        },
    )
    if result.returncode:
        raise ValueError(
            "Exact-tree generated-schema verification failed; no exclusions admitted"
        )
    receipt = json.loads(result.stdout)
    if receipt != {"version": 1, "verified_artifacts": policy["artifacts"]}:
        raise ValueError(
            "Generated-schema verifier returned an incomplete or unexpected receipt"
        )
    if load_policy(snapshot) != policy:
        raise ValueError("Generated artifacts changed during verification")
    if tree_state(snapshot) != original_tree:
        raise ValueError("Verifier changed the scanned tree; no exclusions admitted")
    return receipt["verified_artifacts"]


def retain_pairs(pairs: dict, verified: dict) -> dict:
    """Both members must be proven generated; mixed pairs are still enforced."""
    return {
        key: spans for key, spans in pairs.items() if not set(key[2]) <= verified.keys()
    }


def scan(root: Path, ref: str | None, scratch: Path, executable: str) -> dict:
    from pipelines_hooks.clones import jscpd_keys, jscpd_run, jscpd_snapshot

    if ref is None:
        return {}
    snapshot = jscpd_snapshot.materialize(root, ref, scratch)
    verified = verified_artifacts(snapshot, root)
    document = jscpd_run.run(executable, snapshot)
    pairs = jscpd_keys.keys(document, snapshot)
    retained = retain_pairs(pairs, verified)
    print(jscpd_run.stats_line(document, ref[:12]))
    print(
        f"Generated-schema policy: {len(verified)} verified artifacts, {len(pairs) - len(retained)} schema-only pairs excluded; {len(retained)} pairs retained"
    )
    for path, digest in sorted(verified.items()):
        print(f"  verified {path} sha256:{digest}")
    return retained


def main() -> int:
    from pipelines_hooks.clones import jscpd_gate, jscpd_keys
    from pipelines_hooks.core.baseref import change_base
    from pipelines_hooks.core.gitenv import repo_root
    from pipelines_hooks.core.tools import verified

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("mode", choices=("differential", "census"))
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--base-ref")
    args = parser.parse_args()
    root, executable = repo_root(args.root), verified("jscpd")
    with tempfile.TemporaryDirectory(prefix="verified-schema-clones-") as directory:
        scratch = Path(directory)
        if args.mode == "census":
            current = scan(root, "HEAD", scratch / "head", executable)
            print(f"Clone census: {len(current)} retained pairs (advisory)")
            for key in sorted(current):
                print(jscpd_keys.render_pair(key, current[key]))
            return 0
        base = change_base(root, args.base_ref)
        before = scan(root, base, scratch / "before", executable)
        after = scan(
            root, jscpd_gate._after_tree(root, base), scratch / "after", executable
        )
    added = sorted(set(after) - set(before))
    print(
        f"Clone differential: {len(before)} baseline pairs, {len(after)} after, {len(added)} NEW"
    )
    for key in added:
        print(f"  {jscpd_keys.render_pair(key, after[key])} (fragment {key[1][:12]})")
    return int(bool(added))


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (ValueError, OSError, KeyError, subprocess.SubprocessError) as exc:
        raise SystemExit(
            f"Generated-schema clone gate could not verify its inputs: {exc}"
        ) from exc

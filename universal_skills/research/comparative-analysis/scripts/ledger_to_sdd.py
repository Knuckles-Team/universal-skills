#!/usr/bin/env python3
"""CA-014: Innovation Ledger → SDD scaffolder.

Turns an Innovation Ledger (see references/innovation_ledger_schema.md) into ready-to-fill
DSTDD artifacts under a target project's `.specify/` — `design/<id>/design.md`,
`specs/<id>/spec.md`, and `specs/<id>/tasks.md` — pre-populated with the KG-analysis table,
extension analysis, C4 context, data flow, research provenance, wiring, and risk sections.

This removes the single biggest time-sink in the CA→SDD handoff: hand-authoring each design doc.

Usage:
    python ledger_to_sdd.py --ledger ledger.json --target /path/to/project
    python ledger_to_sdd.py --ledger ledger.jsonl --target /path/to/project --include-unverified
    python ledger_to_sdd.py --ledger ledger.json --target . --dry-run
    python ledger_to_sdd.py --self-test

CONCEPT:CA-014 — Ledger-to-SDD Scaffolder
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REQUIRED = ("id", "title", "claim", "type", "target_module", "entry_point", "extends_concept")


def load_ledger(path: Path) -> list[dict]:
    text = path.read_text()
    if path.suffix == ".jsonl":
        return [json.loads(line) for line in text.splitlines() if line.strip()]
    data = json.loads(text)
    return data if isinstance(data, list) else data.get("innovations", data.get("rows", []))


def feature_slug(row: dict) -> str:
    cid = (row.get("new_concept_id") or "").lower().replace(".", "-").replace(":", "")
    return f"{cid}-{row['id']}" if cid else row["id"]


def _provenance_row(row: dict) -> str:
    sr = row.get("source_ref", {}) or {}
    ref = f"{sr.get('file', '?')}:{sr.get('lines', '?')}"
    repo = sr.get("repo", "?")
    commit = sr.get("commit", "?")
    return f"| {repo} | `{ref}` (commit `{commit}`) | {row.get('claim', '')} | {row.get('verification_note', '')} |"


def render_design(row: dict) -> str:
    nc = row.get("new_concept_id")
    new_concept_block = (
        f"""### New Concept Proposal

- **Proposed ID**: `CONCEPT:{nc}`
- **Augments**: {row.get('extends_concept', '')}
- **Justification**: {row.get('claim', '')}
"""
        if nc
        else "_No new concept — extends an existing one (see Extension Analysis)._"
    )
    return f"""# Design Document: {row['title']} ({nc or row['id']})

> Auto-scaffolded by `ledger_to_sdd.py` (CA-014) from the Innovation Ledger. Fill the TODOs.

## Research Provenance

| Source | Location | Claim | Verification |
|---|---|---|---|
{_provenance_row(row)}

Verification status: **{row.get('verified', 'claimed-only')}**

## KG Analysis (Required)

### Nearest Existing Concepts

<!-- Run parse_concept_registry.py (offline) or kg_search (KG) to fill this table -->

| Concept ID | Name | Similarity | Pillar |
|---|---|---|---|
| {row.get('extends_concept', 'TODO')} | TODO | TODO (≥0.70) | TODO |

### Extension Analysis

- **Primary Extension Point**: {row.get('extends_concept', 'TODO')}
- **Extension Strategy**: {'specialize/compose (gap)' if row.get('type') == 'gap' else 'augment (enhancement)'}
- **New Concept Required?**: {'Yes' if nc else 'No'}

{new_concept_block}

## C4 Context Diagram

```mermaid
C4Context
    title {row['title']} — Integration Context

    System_Boundary(b1, "Target") {{
        System(feat, "{row.get('new_concept_id') or row['id']}", "{row.get('claim', '')[:60]}")
        System(ext, "{row.get('c4_component', 'TODO')}", "Extended component")
    }}
    System_Ext(ep, "{row.get('entry_point', 'TODO')}", "Entry point")

    Rel(ep, feat, "invokes")
    Rel(feat, ext, "extends")
```

## Data Flow

1. **Entry**: `{row.get('entry_point', 'TODO')}` →  `{row.get('target_module', 'TODO')}` (**{row.get('hops', '?')} hops**).
2. **Reads/Writes**: TODO.
3. **Self-improvement**: TODO.
4. **Exposure**: {row.get('entry_point', 'TODO')}.
5. **Guardrails**: TODO.

## Success Metric (Required — G6)

{row.get('success_metric', 'TODO — name a measurable benchmark/metric/test that proves this feature works.')}

## Risk Assessment

- **Blast Radius**: {row.get('target_module', 'TODO')} (type: {row.get('type', 'TODO')}; risk {row.get('risk', '?')}/5).
- **Backward Compatible**: TODO.
- **Breaking Changes**: TODO.

## Wiring (Wire-First, ≤3 hops)

- Entry point: `{row.get('entry_point', 'TODO')}` → `{row.get('target_module', 'TODO')}` = **{row.get('hops', '?')} hops**.
- C4 component: {row.get('c4_component', 'TODO')}.
- Extends: {row.get('extends_concept', 'TODO')}{f" → new {nc}" if nc else ''}.
- Depends on: {', '.join(row.get('depends_on', [])) or 'none'}.
"""


def render_spec(row: dict) -> str:
    return f"""# Spec: {row['title']} ({row.get('new_concept_id') or row['id']})

> References design: `.specify/design/{feature_slug(row)}/design.md`

## Pre-Flight Checklist
- [ ] Design exists; KG-nearest-concepts table completed.
- [ ] Extension target identified ({row.get('extends_concept', 'TODO')}, similarity ≥ 0.70).
- [ ] Claim verified (status: **{row.get('verified', 'claimed-only')}**).
- [ ] Wire-First confirmed: {row.get('hops', '?')} hops from `{row.get('entry_point', 'TODO')}`.
- [ ] Success metric defined: {row.get('success_metric', 'TODO')}.

## User Stories

### US-1 — {row['title']}
**As** a user, **I want** {row.get('claim', 'TODO')},
**so that** {row.get('success_metric', 'TODO')} improves.
- **AC1**: TODO — observable acceptance criterion.
- **AC2**: TODO — entry point `{row.get('entry_point', 'TODO')}` exposes it.
- **AC3**: TODO — backward compatible defaults.

## Non-Functional Requirements
- Tests with `@pytest.mark.concept(id="{row.get('new_concept_id') or row.get('extends_concept', 'TODO')}")`, ≤60s.
- `pre-commit` green; concept registry regenerated; 7-artifact mandate satisfied.
"""


def render_tasks(row: dict) -> str:
    return f"""# Tasks: {row['title']} ({row.get('new_concept_id') or row['id']})

## T1 — Implementation  [code]
- [ ] Extend `{row.get('target_module', 'TODO')}` ({row.get('type', 'TODO')}).

## T2 — Wiring  [code]
- [ ] Expose via `{row.get('entry_point', 'TODO')}` (≤3 hops; verify with check_wiring.py).

## T3 — Tests  [test]
- [ ] Concept-tagged unit tests; measure `{row.get('success_metric', 'TODO')}`.

## T4 — Artifacts  [docs]
- [ ] docs / AGENTS.md / CHANGELOG / README / .specify sync / C4 / concept registry regen.
"""


def scaffold(rows: list[dict], target: Path, *, include_unverified: bool, dry_run: bool) -> dict:
    specify = target / ".specify"
    written, skipped = [], []
    for row in rows:
        missing = [f for f in REQUIRED if not row.get(f)]
        if missing:
            skipped.append({"id": row.get("id", "?"), "reason": f"missing {missing}"})
            continue
        if row.get("verified") != "verified" and not include_unverified:
            skipped.append({"id": row["id"], "reason": f"verified={row.get('verified')}"})
            continue
        slug = feature_slug(row)
        files = {
            specify / "design" / slug / "design.md": render_design(row),
            specify / "specs" / slug / "spec.md": render_spec(row),
            specify / "specs" / slug / "tasks.md": render_tasks(row),
        }
        for path, content in files.items():
            if dry_run:
                written.append(str(path))
                continue
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content)
            written.append(str(path))
    return {"written": written, "skipped": skipped}


def _self_test() -> int:
    import tempfile

    row = {
        "id": "demo-feature",
        "title": "Demo Feature",
        "source_ref": {"repo": "x/y", "commit": "abc123", "file": "a.py", "lines": "1-9"},
        "claim": "does a thing",
        "verified": "verified",
        "type": "enhancement",
        "target_module": "pkg/mod.py",
        "entry_point": "graph_search",
        "c4_component": "Retriever",
        "extends_concept": "KG-2.3",
        "new_concept_id": "KG-2.99",
        "hops": 3,
        "success_metric": "recall@10 delta",
    }
    with tempfile.TemporaryDirectory() as d:
        out = scaffold([row], Path(d), include_unverified=False, dry_run=False)
        assert len(out["written"]) == 3, out
        design = Path(d) / ".specify/design/kg-2-99-demo-feature/design.md"
        assert design.is_file(), out
        body = design.read_text()
        assert "Demo Feature" in body and "KG-2.3" in body and "recall@10 delta" in body
        # Unverified rows are skipped without the flag.
        out2 = scaffold([{**row, "verified": "claimed-only"}], Path(d), include_unverified=False, dry_run=True)
        assert out2["written"] == [] and out2["skipped"], out2
    print("self-test OK")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description="Innovation Ledger → SDD scaffolder (CA-014)")
    ap.add_argument("--ledger", help="Path to ledger.json or ledger.jsonl")
    ap.add_argument("--target", default=".", help="Target project root (writes under .specify/)")
    ap.add_argument("--include-unverified", action="store_true", help="Scaffold claimed-only rows too")
    ap.add_argument("--dry-run", action="store_true", help="List files without writing")
    ap.add_argument("--self-test", action="store_true")
    args = ap.parse_args()

    if args.self_test or not args.ledger:
        return _self_test()

    rows = load_ledger(Path(args.ledger))
    result = scaffold(
        rows, Path(args.target), include_unverified=args.include_unverified, dry_run=args.dry_run
    )
    print(json.dumps(result, indent=2))
    print(f"\n{'(dry-run) ' if args.dry_run else ''}wrote {len(result['written'])} files, "
          f"skipped {len(result['skipped'])} rows", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""CA-012: Offline concept-registry parser & Extend-Before-Invent matcher.

Reads a project's concept registry **without a live Knowledge Graph** — either
`docs/concepts.yaml` (the canonical `- id:/name:/pillar:` form) or `docs/concept_map.md`
(a markdown table of ``| `CONCEPT:ID` | Name | ... |`` rows) — and ranks the nearest concepts
to a proposed feature by lexical similarity. This makes the Extend-Before-Invent gate
(similarity ≥0.70 ⇒ MUST extend) enforceable in Lightweight Mode, the common code-vs-code case.

Pure stdlib (optional PyYAML if present). Returns JSON suitable for a ledger row's
``extends_concept`` field and the design.md KG-analysis table.

Usage:
    python parse_concept_registry.py --registry docs/concepts.yaml --query "memory-first retrieval"
    python parse_concept_registry.py --registry docs/concept_map.md --query "..." --top-k 5
    python parse_concept_registry.py --registry docs/concepts.yaml --query "..." --json
    python parse_concept_registry.py --self-test

CONCEPT:CA-012 — Offline Concept Registry Parser
"""

from __future__ import annotations

import argparse
import json
import re
from difflib import SequenceMatcher
from pathlib import Path

EXTEND_THRESHOLD = 0.70
# Lexical scores are conservative (no embeddings); 0.45–0.70 is a "review manually" band.
REVIEW_THRESHOLD = 0.45
_TOKEN = re.compile(r"[a-z0-9]+")
# Structural id tokens carry no semantic signal; drop them so names dominate.
_STOPWORDS = {"the", "and", "of", "a", "an", "to", "for", "with"}


def _tokens(text: str) -> set[str]:
    return {t for t in _TOKEN.findall((text or "").lower()) if t not in _STOPWORDS}


def parse_yaml_registry(text: str) -> list[dict]:
    """Parse `docs/concepts.yaml`. Uses PyYAML when available, else a tolerant line parser."""
    try:
        import yaml  # type: ignore

        data = yaml.safe_load(text) or {}
        concepts = data.get("concepts", data if isinstance(data, list) else [])
        return [
            {"id": c.get("id", ""), "name": c.get("name", ""), "pillar": c.get("pillar", "")}
            for c in concepts
            if isinstance(c, dict) and c.get("id")
        ]
    except Exception:
        pass
    # Fallback: parse the known `- id: / name: / pillar:` block structure.
    rows: list[dict] = []
    cur: dict = {}
    for line in text.splitlines():
        m = re.match(r"\s*-\s*id:\s*(.+)", line)
        if m:
            if cur.get("id"):
                rows.append(cur)
            cur = {"id": m.group(1).strip(), "name": "", "pillar": ""}
            continue
        m = re.match(r"\s*name:\s*(.+)", line)
        if m and cur:
            cur["name"] = m.group(1).strip()
            continue
        m = re.match(r"\s*pillar:\s*(.+)", line)
        if m and cur:
            cur["pillar"] = m.group(1).strip()
    if cur.get("id"):
        rows.append(cur)
    return rows


def parse_markdown_registry(text: str) -> list[dict]:
    """Parse a `docs/concept_map.md` markdown table of `| `CONCEPT:ID` | Name | ... |` rows."""
    rows: list[dict] = []
    for line in text.splitlines():
        if not line.strip().startswith("|"):
            continue
        cells = [c.strip().strip("`") for c in line.strip().strip("|").split("|")]
        if not cells:
            continue
        cid = cells[0]
        if re.match(r"^(CONCEPT:)?[A-Z]+-\d", cid):
            name = cells[1] if len(cells) > 1 else ""
            pillar = cid.split(".")[0].replace("CONCEPT:", "")
            rows.append({"id": cid.replace("CONCEPT:", ""), "name": name, "pillar": pillar})
    return rows


def load_registry(path: Path) -> list[dict]:
    text = path.read_text()
    if path.suffix in (".yaml", ".yml"):
        return parse_yaml_registry(text)
    if path.suffix == ".md":
        return parse_markdown_registry(text)
    # Try YAML then markdown.
    return parse_yaml_registry(text) or parse_markdown_registry(text)


def score(query: str, concept: dict) -> float:
    """Blend overlap-coefficient (subset-aware) over the concept *name* with sequence ratio.

    Overlap-coefficient ``|A∩B| / min(|A|,|B|)`` rewards a query that is a subset of (or
    superset of) a concept name — the common paraphrase case — far better than Jaccard.
    """
    name = concept.get("name", "")
    qt, nt = _tokens(query), _tokens(name)
    overlap = len(qt & nt) / min(len(qt), len(nt)) if (qt and nt) else 0.0
    ratio = SequenceMatcher(None, query.lower(), name.lower()).ratio()
    return round(0.7 * overlap + 0.3 * ratio, 4)


def rank(query: str, concepts: list[dict], top_k: int = 5) -> list[dict]:
    scored = [{**c, "similarity": score(query, c)} for c in concepts]
    scored.sort(key=lambda c: c["similarity"], reverse=True)
    return scored[:top_k]


def analyze(query: str, concepts: list[dict], top_k: int = 5) -> dict:
    top = rank(query, concepts, top_k)
    best = top[0] if top else None
    sim = best["similarity"] if best else 0.0
    must_extend = sim >= EXTEND_THRESHOLD
    review = REVIEW_THRESHOLD <= sim < EXTEND_THRESHOLD
    if must_extend:
        rec = f"Extend {best['id']} (similarity {sim} ≥ {EXTEND_THRESHOLD})."
    elif review:
        rec = (
            f"REVIEW: nearest {best['id']} (similarity {sim}) is in the manual-review band "
            f"[{REVIEW_THRESHOLD}, {EXTEND_THRESHOLD}). Lexical scores are conservative — confirm "
            "by hand or via kg_search before minting a new concept."
        )
    else:
        rec = "No match ≥0.45 — a New Concept Proposal is permitted (justify in design.md)."
    return {
        "query": query,
        "nearest": top,
        "must_extend": must_extend,
        "review_band": review,
        "extend_target": best["id"] if (must_extend or review) else None,
        "recommendation": rec,
    }


def _self_test() -> int:
    concepts = [
        {"id": "KG-2.3", "name": "Unified Retrieval & Graph Integrity", "pillar": "KG-2"},
        {"id": "KG-2.1", "name": "Tiered Memory & Context", "pillar": "KG-2"},
        {"id": "ORCH-1.2", "name": "Specialist Routing & Discovery", "pillar": "ORCH-1"},
    ]
    # YAML fallback parser.
    parsed = parse_yaml_registry(
        "concepts:\n- id: KG-2.3\n  name: Unified Retrieval\n  pillar: KG-2\n"
    )
    assert parsed and parsed[0]["id"] == "KG-2.3", parsed
    # Markdown parser.
    md = parse_markdown_registry("| `KG-2.1` | Tiered Memory | 5 |\n| junk | x |")
    assert md and md[0]["id"] == "KG-2.1", md
    # Ranking finds the retrieval concept for a retrieval query.
    res = analyze("unified retrieval graph integrity", concepts)
    assert res["nearest"][0]["id"] == "KG-2.3", res
    assert res["must_extend"] and res["extend_target"] == "KG-2.3", res
    print("self-test OK")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description="Offline concept-registry parser (CA-012)")
    ap.add_argument("--registry", help="Path to docs/concepts.yaml or docs/concept_map.md")
    ap.add_argument("--query", help="Proposed feature description")
    ap.add_argument("--top-k", type=int, default=5)
    ap.add_argument("--json", action="store_true", help="Emit JSON")
    ap.add_argument("--self-test", action="store_true")
    args = ap.parse_args()

    if args.self_test or not (args.registry and args.query):
        return _self_test()

    concepts = load_registry(Path(args.registry))
    result = analyze(args.query, concepts, args.top_k)
    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print(f"Query: {result['query']}\n")
        print(f"{'Concept':12} {'Sim':>6}  Name")
        for c in result["nearest"]:
            print(f"{c['id']:12} {c['similarity']:>6}  {c.get('name', '')}")
        print(f"\n→ {result['recommendation']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

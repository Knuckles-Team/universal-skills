# Innovation Ledger Schema (CA-014)

The **Innovation Ledger** is the machine-usable bridge between comparative analysis and SDD.
Every extracted innovation is one row. Exploration sub-agents return rows in this exact shape
(see `exploration_return_schema.md`), so results merge deterministically and the ledger feeds
`ledger_to_sdd.py`, `score_recommendations.py`, and `verify_claims.py` with no re-parsing.

Stored as a JSON array (`ledger.json`) or JSONL (`ledger.jsonl`). One object per innovation:

```json
{
  "id": "hyde-query-expansion",
  "title": "HyDE Query Expansion",
  "source_ref": {
    "repo": "quarqlabs/agent-oss",
    "commit": "b683860",
    "file": "agent.py",
    "lines": "1817-2020"
  },
  "claim": "Planner emits 4 vector queries + keywords + search_mode (standard|deep).",
  "verified": "verified",
  "verification_note": "Confirmed in agent.py:1817-2020; JSON plan parsed at :1966.",
  "type": "enhancement",
  "target_module": "agent_utilities/knowledge_graph/retrieval/hybrid_retriever.py",
  "entry_point": "graph_search",
  "c4_component": "KG Hybrid Retriever",
  "extends_concept": "KG-2.3",
  "new_concept_id": "KG-2.12",
  "hops": 3,
  "leverage": 5,
  "effort": 3,
  "risk": 2,
  "priority_score": 0.0,
  "success_metric": "LongMemEval-S recall delta on aggregation questions",
  "depends_on": ["role-specialized-routing"],
  "status": "proposed"
}
```

## Field reference

| Field | Type | Required | Meaning |
|---|---|---|---|
| `id` | kebab string | yes | Stable ledger id; becomes the SDD feature folder when no `new_concept_id`. |
| `title` | string | yes | Human title. |
| `source_ref` | object | yes | `{repo, commit, file, lines}` proving the behavior's origin (G4 reproducibility). |
| `claim` | string | yes | One-line description of the behavior being assimilated. |
| `verified` | enum | yes | `verified` \| `claimed-only` \| `refuted` (G2). Only `verified` rows scaffold SDD by default. |
| `verification_note` | string | no | Evidence / refutation note. |
| `type` | enum | yes | `gap` (net-new) \| `enhancement` (extends existing module). |
| `target_module` | path | yes | Hot-path module this wires into. |
| `entry_point` | string | yes | MCP tool / A2A skill / API route / CLI that exposes it. |
| `c4_component` | string | yes | C4 component it belongs to. |
| `extends_concept` | CONCEPT:ID | yes | Existing concept it extends (Extend-Before-Invent, similarity ≥0.7). |
| `new_concept_id` | CONCEPT:ID | no | Minted sub-concept id, if a new tag is approved. |
| `hops` | int | yes | Entry-point → code hop count (must be ≤3; G10 verifies). |
| `leverage` | 1–5 | yes | Expected impact (G5). |
| `effort` | 1–5 | yes | Implementation cost (G5). |
| `risk` | 1–5 | yes | Blast radius / regression risk (G5). |
| `priority_score` | float | computed | Filled by `score_recommendations.py`. |
| `success_metric` | string | yes | Measurable validation for the feature (G6) — benchmark/metric/test. |
| `depends_on` | list[id] | no | Other ledger ids that must land first (critical-path ordering). |
| `status` | enum | yes | `proposed` \| `accepted` \| `implemented` \| `discarded`. |

## Invariants enforced by tooling
- A row with `verified != "verified"` is **not** scaffolded into SDD unless `--include-unverified`.
- A row missing `entry_point`/`target_module`/`extends_concept` fails the Wire-First gate (G10).
- A row missing `success_metric` fails `score_recommendations.py --strict` (G6).
- `hops > 3` is flagged by `check_wiring.py` (G10).

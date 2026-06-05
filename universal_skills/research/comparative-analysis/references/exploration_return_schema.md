# Exploration Sub-Agent Return Schema (G7)

When the skill fans out exploration sub-agents (Lightweight Mode), each agent MUST return its
findings as a **JSON array of Innovation Ledger rows** (see `innovation_ledger_schema.md`) — not
prose. This makes parallel results merge deterministically and cheaply (dedupe by `id` /
`source_ref`), and the merged array is directly consumable by `verify_claims.py`,
`score_recommendations.py`, and `ledger_to_sdd.py` with zero re-parsing.

## What to put in each sub-agent prompt

> Return ONLY a JSON array. Each element is one innovation you found, with these keys:
> `id` (kebab), `title`, `source_ref` {`repo`,`commit`,`file`,`lines`}, `claim` (one line),
> `evidence_tokens` (2–5 exact identifiers/numbers that appear in the cited code — used to
> verify the claim), `type` (`gap`|`enhancement`), `target_module` (best guess in the target
> repo), `entry_point`, `c4_component`, `extends_concept`, `leverage`/`effort`/`risk` (1–5),
> `success_metric`. Omit a field only if genuinely unknown. Do not include commentary.

## Why `evidence_tokens` matters
`verify_claims.py` greps the cited `source_ref` region for these tokens to auto-stamp
`verified` vs `claimed-only`. Without them, every claim falls back to claimed-only and needs
manual review. Asking the sub-agent for them is nearly free and front-loads verification.

## Merge rule (deterministic)
1. Concatenate all agents' arrays.
2. Dedupe by `id`; on collision keep the row with the more specific `source_ref` (has `lines`).
3. Secondary dedupe by `source_ref.file + lines` to catch the same finding under different ids.
4. The merged array is the **draft ledger** → verify → score → scaffold.

## Example row
```json
{
  "id": "two-pass-retrieval",
  "title": "Self-Correcting Two-Pass Retrieval",
  "source_ref": {"repo": "quarqlabs/agent-oss", "commit": "b683860", "file": "agent.py", "lines": "2676-2825"},
  "claim": "Generator emits REQUIRED_DATA flag; runtime re-searches at 0.28 and regenerates.",
  "evidence_tokens": ["REQUIRED_DATA", "0.28", "dynamic_queries"],
  "type": "enhancement",
  "target_module": "knowledge_graph/retrieval/retrieval_quality.py",
  "entry_point": "graph_search",
  "c4_component": "Retrieval Quality Gate",
  "extends_concept": "KG-2.3",
  "leverage": 5, "effort": 3, "risk": 2,
  "success_metric": "LongMemEval-S accuracy delta on multi-session questions"
}
```

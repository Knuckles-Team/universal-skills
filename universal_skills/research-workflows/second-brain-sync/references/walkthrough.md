# Walkthrough: build my epistemic second brain

A concrete, end-to-end run of `second-brain-sync` over a small mixed corpus —
an Obsidian vault export, one PDF, one git repo, and one bookmarked article —
following the six steps in `SKILL.md`. Every tool call below is a real
`graph-os` MCP tool (`graph_ingest`, `graph_analyze`, `graph_write`,
`graph_query`, `graph_ask`, `engine_query`); none of it is invented. Load them
first: `load_tools(tools=["graph_ingest", "graph_analyze", "graph_write", "graph_query", "graph_ask", "engine_query"])`.

## 0. Collect

The user points at four sources:

```jsonc
[
  {"path_or_url": "${HOME}/obsidian-vault/projects/", "kind": "dir"},
  {"path_or_url": "${HOME}/Downloads/rl-survey-2026.pdf", "kind": "file"},
  {"path_or_url": "${AGENT_UTILITIES_WORKSPACE_ROOT}/agent-packages/agent-utilities", "kind": "repo"},
  {"path_or_url": "https://example.com/articles/epistemic-graphs", "kind": "url"}
]
```

## 1. Ingest

```text
graph_ingest(action="ingest", target_path="${HOME}/obsidian-vault/projects/")
# -> "Started ingestion job job:9f21 for ${HOME}/obsidian-vault/projects/"
# (a directory of notes classifies as DOCUMENT -> async job; poll with:)
graph_ingest(action="job_status", job_id="job:9f21")

graph_ingest(action="ingest", target_path="${HOME}/Downloads/rl-survey-2026.pdf")
# -> "Started ingestion job job:9f22 for rl-survey-2026.pdf"

graph_ingest(action="ingest", target_path="${AGENT_UTILITIES_WORKSPACE_ROOT}/agent-packages/agent-utilities")
# -> classifies CODEBASE -> async job:9f23 (tree-sitter parse)

graph_ingest(action="ingest_url", target_path="https://example.com/articles/epistemic-graphs")
# -> runs inline: fetches via ArchiveBox->crawl4ai->requests, returns the
#    Document node id directly, e.g. "doc:example.com/articles/epistemic-graphs"
```

Poll the three job ids until `status: completed`, then collect the resulting
node ids (e.g. `job_status` returns `{"status": "completed", "node_ids": [...]}`).
Say ingestion yields: `doc:note-eg-roadmap`, `doc:note-project-x`,
`doc:rl-survey-2026`, `code:agent-utilities` (repo root), and
`doc:example.com-epistemic-graphs`.

## 2. Extract

For each Document node, extract atomic facts and claims. Two examples:

```text
graph_ingest(action="fact_extract", target_path="${HOME}/obsidian-vault/projects/note-eg-roadmap.md")
```
Response (trimmed):
```jsonc
{
  "status": "extracted",
  "facts": [
    {
      "subject": "epistemic-graph engine",
      "predicate": "provides",
      "object": "bitemporal valid/tx time",
      "confidence": 88,
      "evidence_span": "the engine natively tracks both valid_time and tx_time per fact",
      "source_file": "note-eg-roadmap.md",
      "is_duplicate": false
    }
  ],
  "stats": {"total_facts": 14, "unique_facts": 12, "duplicate_facts": 2}
}
```

```text
graph_analyze(action="extract_claims",
  query="<full text of note-eg-roadmap.md>", node_id="doc:note-eg-roadmap")
```
Persists `ClaimNode`/`EntityNode`s directly (entities: "epistemic-graph
engine", "bitemporal model"; claims linked with `BUILDS_ON`/`EXEMPLIFIES`
edges where the extractor infers them) and returns the extraction result
summary.

For the large PDF, prefer the GPU-scheduled path instead of blocking inline:
```text
graph_ingest(action="extract_submit", target_path="${HOME}/Downloads/rl-survey-2026.pdf", max_depth=2)
# -> {"job_id": "extract:7a1"}
graph_ingest(action="extract_status", job_id="extract:7a1")
# ... poll until completed ...
graph_ingest(action="extract_jsonl", job_id="extract:7a1")
# -> the facts.jsonl content
```

## 3. Link corpus

```text
graph_write(action="add_node", node_id="corpus:home-lab-2026",
  node_type="PersonalCorpus",
  properties='{"name": "home-lab-2026", "owner": "genius"}')
# -> "Node corpus:home-lab-2026 added."

graph_write(action="add_edge", source_id="doc:note-eg-roadmap",
  target_id="corpus:home-lab-2026", rel_type="PART_OF")
graph_write(action="add_edge", source_id="doc:rl-survey-2026",
  target_id="corpus:home-lab-2026", rel_type="PART_OF")
graph_write(action="add_edge", source_id="code:agent-utilities",
  target_id="corpus:home-lab-2026", rel_type="PART_OF")
graph_write(action="add_edge", source_id="doc:example.com-epistemic-graphs",
  target_id="corpus:home-lab-2026", rel_type="PART_OF")
```

## 4. Analyze — gap/synergy

Run the friction scan for a new claim extracted from the note (e.g. "the
epistemic-graph engine provides bitemporal valid/tx time"):

```text
graph_analyze(action="contradictions",
  query="the epistemic-graph engine provides bitemporal valid/tx time",
  node_id="claim:eg-bitemporal-1")
```
```jsonc
[
  {
    "new_id": "claim:eg-bitemporal-1",
    "conflict_id": "claim:rl-survey-bitemporal-3",
    "similarity": 0.81,
    "severity": "none",
    "reason": "corroborating — same claim from the PDF survey, no conflict"
  }
]
```
Read as **synergy**: the note and the PDF independently support the same
claim. A `severity` other than `"none"` would flag a real contradiction to
reconcile by hand. A claim that returns `[]` (no neighbours at all) is a
**coverage gap** — nothing else in the corpus speaks to it yet, useful for
finding what to research or write about next.

Pull the whole-corpus coverage view in one round-trip:
```text
graph_query(cypher="MATCH (c)-[:PART_OF]->(:PersonalCorpus {name:'home-lab-2026'}) RETURN c.id AS id",
  envelope="bundle")
```
```jsonc
{
  "rows": [{"id": "doc:note-eg-roadmap"}, {"id": "doc:rl-survey-2026"}, ...],
  "evidence_bundle": {
    "confidence": 0.84,
    "valid_time_min": "2026-06-01T00:00:00Z",
    "valid_time_max": "2026-07-12T00:00:00Z",
    "contradiction_ids": [],
    "policy_labels": []
  }
}
```

## 5. Query back — with epistemic justification

```text
graph_ask(question="What do I know about bitemporal tracking in the epistemic graph?",
  envelope="bundle")
```
```jsonc
{
  "dialect": "cypher",
  "generated_query": "MATCH (c:Claim) WHERE c.text CONTAINS 'bitemporal' RETURN c.id, c.text",
  "rows": [{"id": "claim:eg-bitemporal-1", "text": "..."}],
  "citations": ["doc:note-eg-roadmap", "doc:rl-survey-2026"],
  "evidence_bundle": {"confidence": 0.84, "contradiction_ids": []}
}
```

Currency-upgrade the returned id(s):
```text
engine_query(action="explain_provenance_by_ids", params_json='{"ids": ["claim:eg-bitemporal-1"]}')
```
```jsonc
{"rows": [{"id": "claim:eg-bitemporal-1", "kind": "Claim", "confidence": 0.84,
           "valid_time": 1751328000, "tx_time": 1752307200,
           "source_refs": ["doc:note-eg-roadmap", "doc:rl-survey-2026"],
           "evidence_spans": ["ev:1", "ev:2"]}], "resolved": true}
```

Ask why:
```text
engine_query(action="explain_belief", params_json='{"node_id": "claim:eg-bitemporal-1"}')
```
```jsonc
{"root": {"claim": "eg-bitemporal-1", "rule": "DerivedSupport", "confidence": 0.84,
          "premises": [{"claim": "note-eg-roadmap", "rule": "Asserted", "confidence": 0.88},
                       {"claim": "rl-survey-2026-p12", "rule": "Asserted", "confidence": 0.80}]}}
```

If the connected engine has the opt-in `epistemic-tms` feature, get the
acceptance capstone:
```text
engine_query(action="epistemic_status", params_json='{"node_id": "claim:eg-bitemporal-1"}')
```
On a `full`-only build this degrades to `{"error": "..."}` — treat that as
"capstone unavailable here," not a failure; the three prior layers already
answered the question with citations and a justification tree.

## Result

The corpus is now a queryable second brain: every claim traces to an
`evidence_span` and a `source_file`/`source_refs`, every answer carries
calibrated `confidence` and a justification tree, and the friction scan
already surfaced one synergy (bitemporal tracking corroborated across two
sources) and flagged zero contradictions — a clean first sync.

# Walkthrough: build my epistemic second brain

Two concrete, end-to-end runs of `second-brain-sync`: the common case — a
markdown notes directory synced in one call (§A) — and a mixed corpus of an
Obsidian vault export, a PDF, a git repo, and a bookmarked article ingested
per-source (§B). Every tool call below is a real `graph-os` MCP tool
(`graph_ingest`, `graph_analyze`, `graph_write`, `graph_query`, `graph_ask`,
`graph_claims`, `engine_query`); none of it is invented. Load them first:
`load_tools(tools=["graph_ingest", "graph_analyze", "graph_write", "graph_query", "graph_ask", "graph_claims", "engine_query"])`.

## A. One-call sync — a markdown notes directory

The user points at a folder of plain notes (an Obsidian vault, or a directory
synced down from Nextcloud/Paperless-ngx via their own connector presets —
see `SKILL.md` Step 0): `${HOME}/notes/homelab/`, containing (among others)
`caching-note.md` — "The team must validate that the new caching layer
clearly improves database performance under sustained load." — and the KG
already holds an EARLIER claim from a prior sync: `claim:db-perf-2026-06`,
text "the caching layer clearly degrades database performance under peak
load."

### A1. Sync

```text
graph_ingest(action="sync_second_brain",
  target_path="${HOME}/notes/homelab/", corpus_name="homelab-notes")
```
Response (trimmed):
```jsonc
{
  "corpus_id": "corpus:homelab-notes",
  "notes_seen": 6, "notes_synced": 6, "notes_skipped_unchanged": 0,
  "facts": 17, "claims": 6,
  "claims_proposed": ["claim:9f2a1b...", "claim:1c7bd4...", "..."],
  "contradictions": [
    {
      "proposal_id": "BeliefRevisionProposal:claim:9f2a1b...:2026-07-23T14:02:11Z",
      "new_id": "claim:9f2a1b...", "conflict_id": "claim:db-perf-2026-06",
      "severity": "medium", "similarity": 0.55
    }
  ],
  "errors": []
}
```
One call did what used to take four separate tool round-trips: every note is
ingested with provenance, atomic facts are extracted (`evidence_span` citing
the exact note), typed claims are extracted and PROPOSED (never silently
accepted), and the new "improves" claim was scanned against existing graph
content — flagging that it opposes the earlier "degrades" claim.

### A2. Review — pending claims

Nothing from Step A1 is live belief yet; every claim sits `proposed` until
reviewed:
```text
graph_claims(action="list", state="proposed")
```
```jsonc
{"action": "list", "claims": [
  {"claim_id": "claim:9f2a1b...", "current_state": "proposed",
   "reason": "second-brain-sync: caching-note.md", "last_transition_at": "..."},
  "..."
]}
```
Once satisfied a claim holds up, advance it explicitly — nothing is promoted
automatically:
```text
graph_claims(action="validate", claim_id="claim:9f2a1b...", valid=true, reason="matches team's own benchmark")
graph_claims(action="accept", claim_id="claim:9f2a1b...", reason="confirmed by benchmark")
```

### A3. Review — the contradiction proposal

```text
graph_query(cypher="MATCH (p:BeliefRevisionProposal) WHERE p.corpus_id = $corpus_id AND p.status = 'proposal' RETURN p",
  params_json='{"corpus_id": "corpus:homelab-notes"}')
```
```jsonc
{"rows": [{"p": {
  "status": "proposal", "belief_id": "claim:9f2a1b...",
  "old_confidence": 0.85, "new_confidence": 0.681, "delta": -0.169,
  "new_contradicted_by_node_ids": ["claim:db-perf-2026-06"],
  "reason": "[FRICTION] new claim '...clearly improves database performance...' opposes existing belief '...clearly degrades database performance...' (topical similarity 0.55)",
  "severity": "medium", "similarity": 0.55,
  "reasoning_trace": [
    {"node_id": "claim:db-perf-2026-06", "role": "contradict", "node_confidence": 0.5, "log_odds_contribution": -0.275},
    {"node_id": "claim:9f2a1b...", "role": "summary", "old_confidence": 0.85, "new_confidence": 0.681, "delta": -0.169}
  ]
}}]}
```
This is propose-only — the SAME node shape the loop's own periodic
belief-revision pass persists, so any existing tool that already reads
`:BeliefRevisionProposal` picks this up too. A human decides which belief
survives (maybe the note is right and the earlier claim gets `deprecate`d via
`graph_claims`; maybe the note needs a correction) — nothing here is resolved
automatically.

### A4. Re-sync is idempotent

Running A1 again over the SAME `${HOME}/notes/homelab/` with nothing changed
returns `"notes_synced": 0, "notes_skipped_unchanged": 6, "facts": 0,
"claims": 0, "contradictions": []` — every note is content-hash addressed, so
an unchanged corpus never mints a duplicate fact, claim, or proposal. Editing
one note and re-running only re-syncs that one note.

## B. Larger sources — a mixed corpus, per-source

`sync_second_brain` covers a notes directory. For a PDF, a git repo, or a
bookmarked page, ingest and extract per source instead — the user points at
four sources:

```jsonc
[
  {"path_or_url": "${HOME}/obsidian-vault/projects/", "kind": "dir"},
  {"path_or_url": "${HOME}/Downloads/rl-survey-2026.pdf", "kind": "file"},
  {"path_or_url": "${AGENT_UTILITIES_WORKSPACE_ROOT}/agent-packages/agent-utilities", "kind": "repo"},
  {"path_or_url": "https://example.com/articles/epistemic-graphs", "kind": "url"}
]
```

### B1. Ingest

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

### B2. Extract

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

### B3. Link corpus

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

### B4. Analyze — friction scan

Run the friction scan for a new claim extracted from the note ("the
epistemic-graph engine provides bitemporal valid/tx time") against a DIFFERENT
existing claim that genuinely opposes it (e.g. an earlier note asserting the
engine has no temporal tracking at all):

```text
graph_analyze(action="contradictions",
  query="the epistemic-graph engine provides bitemporal valid/tx time",
  node_id="claim:eg-bitemporal-1")
```
```jsonc
[
  {
    "new_id": "claim:eg-bitemporal-1",
    "conflict_id": "claim:eg-no-temporal-model",
    "similarity": 0.42,
    "severity": "medium",
    "reason": "[FRICTION] new claim '...provides bitemporal valid/tx time' opposes existing belief '...has no temporal tracking' (topical similarity 0.42)"
  }
]
```
The detector only ever emits an entry for a **genuine detected opposition** —
it never reports a "no conflict" row. So `[]` means "nothing in the corpus
opposes this new claim" (it may still be reinforced by similar, non-opposing
neighbours you'd find with a plain `graph_query`/`graph_ask`, or there may be
no neighbours at all — this action doesn't distinguish those two, by design:
propose-only friction detection, not general similarity search). A populated
result is always a real contradiction to reconcile by hand (never
auto-resolved) — persist it the same way §A3 does if you want it reviewable
alongside `sync_second_brain`'s own findings.

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

## C. Query back — with epistemic justification

Works identically whichever path (§A or §B) populated the corpus.

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
`evidence_span` and a `source_file`/`source_refs`, every claim sits in the
governed `ClaimFlywheel` lifecycle until reviewed (never silently accepted),
every genuine contradiction is a persisted, reviewable
`:BeliefRevisionProposal` (propose-only — never auto-resolved), and every
answer carries calibrated `confidence` and a justification tree.

# Comparative-Analysis Skill — Improvement Plan

> Authored after a full run: agent-oss (Quarq) vs agent-utilities → SDD plan → implementation.
> Goal: optimize the skill for **repeated** code-vs-code innovation-extraction runs that feed SDD.
> Tackle **after Feature E** of the current synergy epic.

## What worked (keep)
- **Wire-First integration** — forcing every recommendation to name its hot-path module, entry
  point, C4 component, and CONCEPT:ID is the single most valuable part. It made the SDD plan executable.
- **Innovation methodology** (biomimicry / TRIZ / structure-mapping) references are good for cross-domain.
- **Output location rules** and the `.specify/reports/` convention.

## Critical gaps (highest priority)

### G1 — The KG-cold / no-MCP path is undocumented and is the common case
The skill's Phase -1 assumes the `agent-utilities-kg` MCP server is running and both codebases are
already ingested. In the real run, **none of that was true** — I used Explore agents + direct file
reads + parsing `docs/concepts.yaml` directly. The skill treats this as a degraded fallback ("scripts
second") when it was actually the *primary, faster* path.
- **Fix**: Add a first-class **"Lightweight Mode"** (agent-driven, no KG, no scripts) as the default
  for code-vs-code, with the KG/script pipeline as the opt-in "Deep Mode" for large or recurring corpora.
- **Fix**: Provide a `parse_concept_registry.py` that reads `docs/concepts.yaml` directly so the
  Extend-Before-Invent (similarity ≥0.7) gate works **without** a live KG (string/embedding match offline).

### G2 — No source-claim verification (marketing vs. code)
The input article made strong claims ("98.2%", "three models", "0.28 threshold"). I verified them
against `agent.py` line-by-line — but the skill never *mandates* this. A naive run could assimilate a
feature that exists only in a blog post.
- **Fix**: Add a mandatory **Claim-Verification step**: every extracted innovation must cite
  `source_file:line` proving the behavior exists in code, with a `verified | claimed-only | refuted`
  status. Adversarially spot-check the top N claims (a second agent tries to refute).

### G3 — The CA→SDD handoff is prose, not a structured artifact
I had to hand-build each `design.md` (KG-analysis table, C4, wiring, provenance). The skill produces a
markdown report but no machine-usable bridge to the DSTDD design template.
- **Fix**: Emit an **Innovation Ledger** (JSON/JSONL) as a first-class artifact — one row per
  innovation: `{id, source_ref, claim, verified, target_module, entry_point, c4_component,
  extends_concept, gap|enhancement, effort, leverage, risk}`. Then a `ledger_to_sdd.py` scaffolds
  `.specify/design/<id>/design.md` + `spec.md` + `tasks.md` stubs from it. This is the biggest time-sink removed.

### G4 — No reproducibility / source pinning
agent-oss is actively changing (its own README says so). Nothing recorded the analyzed commit SHA, so a
re-run can't tell what changed.
- **Fix**: Record `{source_repo, commit_sha, analyzed_at}` in every report and ledger. On re-run, diff
  against the prior ledger and only re-analyze changed files/claims (incremental).

## Important gaps (next priority)

### G5 — No prioritization scoring on recommendations
I manually derived sequencing (critical path, "highest leverage"). The skill should score each
innovation on **leverage × effort × risk** and emit a recommended build order + critical path.

### G6 — No measurable success criterion per feature
I invented the LongMemEval harness idea myself. The skill should require each extracted feature to name
a **measurable validation** (benchmark, metric, or test) so "superiority" is provable, not asserted.

### G7 — Sub-agent output is unstructured and token-heavy
The 3 Explore agents returned large prose dumps (useful but noisy and not machine-mergeable).
- **Fix**: Give exploration sub-agents a **return schema** (the Innovation Ledger row shape) so results
  merge deterministically and cheaply, and dedupe across agents.

### G8 — Mode/workflow mismatch
"Innovation Extraction" is listed as a mode but the 11 documented steps are dominated by
codebase-maturity auditing (governance, bus factor, SemVer, container weight) — largely irrelevant when
the goal is *feature extraction from a focused OSS agent*. The grading rubric (56 metrics) wasn't the point.
- **Fix**: Make the step set **mode-conditional** — Innovation-Extraction mode runs G2/G3/G5/G6, skips
  governance/ecosystem-health unless asked.

## Minor

- **G9** — Make Pre-Flight actually enforced (it's marked MANDATORY but nothing checks it). The
  `AskUserQuestion`-style pre-flight I did (scope / harness / concept-IDs) should be a templated step.
- **G10** — Turn the Phase-11 Wiring Audit Checklist into a runnable `check_wiring.py` (entry-point
  reachability ≤3 hops via import graph) instead of a manual checklist.
- **G11** — Cache/memoize per-source analysis under `~/.scholarx/analysis/<repo>@<sha>/` so repeated
  runs against the same source are instant.

## Proposed implementation order (after E)
1. **G3 Innovation Ledger + `ledger_to_sdd.py`** (biggest leverage — removes the manual design-doc grind).
2. **G1 Lightweight Mode + `parse_concept_registry.py`** (makes the common path first-class & KG-optional).
3. **G2 Claim-Verification step** + **G7 sub-agent return schema** (quality + cheap merge).
4. **G4 source pinning + incremental diff** & **G11 cache** (reproducibility for repeated runs).
5. **G5 prioritization scoring** + **G6 per-feature success metric** (planning quality).
6. **G8 mode-conditional steps**, **G9 enforced pre-flight**, **G10 `check_wiring.py`** (polish).

## One-line summary
The skill is strong on *governance discipline* (Wire-First) but weak on the *fast inner loop*:
verify-claims → structured ledger → auto-scaffold SDD → measurable validation → incremental re-runs.
Optimizing G1–G4 turns a ~full-session manual analysis into a repeatable, mostly-automated pipeline.

---

## Implementation status (all items DONE)

| Gap | Delivered | Status |
|-----|-----------|--------|
| G1 Lightweight Mode + offline concept registry | `scripts/parse_concept_registry.py` (CA-012) + SKILL Mode Selection | ✅ |
| G2 Claim verification | `scripts/verify_claims.py` (CA-013) + adversarial-refute note | ✅ |
| G3 Innovation Ledger + scaffolder | `references/innovation_ledger_schema.md` + `scripts/ledger_to_sdd.py` (CA-014) | ✅ |
| G4 Source pinning + incremental | `scripts/pin_source.py` (CA-017) | ✅ |
| G5 Prioritization scoring | `scripts/score_recommendations.py` (CA-015) | ✅ |
| G6 Per-feature success metric | enforced by `score_recommendations.py --strict` | ✅ |
| G7 Sub-agent return schema | `references/exploration_return_schema.md` | ✅ |
| G8 Mode-conditional steps | SKILL Mode Selection + enforced pre-flight | ✅ |
| G9 Enforced pre-flight | SKILL Step 1 (ENFORCED) | ✅ |
| G10 Runnable wiring audit | `scripts/check_wiring.py` (CA-016) | ✅ |
| G11 Analysis cache | `pin_source.py --cache` → `~/.scholarx/analysis/<repo>@<sha>/` | ✅ |

All six scripts pass `--self-test`; the full inner loop was validated end-to-end against
`quarqlabs/agent-oss` (a fake claim was correctly held at `claimed-only` and excluded from SDD
scaffolding) and `check_wiring.py` was dogfooded against the agent-utilities synergy features
(all reachable ≤3 hops). Canonical location: `universal_skills/research/comparative-analysis`
(the `~/.claude/skills/comparative-analysis` symlink target — both update together).

**Open item for a human:** a stale orphan copy exists at
`universal_skills/agent-tools/comparative-analysis/scripts/concept_cross_reference.py` (907 lines,
diverged from the canonical 856-line version, no SKILL.md). It is unreferenced and was not modified
here — recommend deleting it or replacing the dir with a symlink to the canonical skill.

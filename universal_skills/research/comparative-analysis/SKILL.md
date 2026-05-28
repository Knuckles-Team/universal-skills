---
name: comparative-analysis
description: >-
  Comprehensive multi-modal comparative analysis engine for codebases, research papers,
  and cross-domain innovation extraction. Evaluates governance, architecture, quality,
  security, testing, docs, and performance. Supports concept-ID-seeded cross-referencing
  against project concept registries for targeted enhancement discovery. Includes
  architecture-aware gap analysis with C4 diagram discovery/auto-generation, hot path
  identification, design pattern differential, and wiring opportunity synthesis.
license: MIT
tags: [analysis, comparison, evaluation, benchmark, architecture, security, governance, research, innovation, biomimicry, analogical-reasoning, TRIZ, maturity, license, compliance, enterprise, grading, radar-chart, concept-id, cross-reference, c4, hot-path, wiring-audit]
metadata:
  author: Genius
  version: '0.18.0'
---

# Comparative Analysis

Multi-modal comparative analysis engine that evaluates and compares any combination of
codebases and research papers across 56+ industry-standard metrics organized into 8
analysis domains. Supports innovation extraction via biomimicry, analogical reasoning,
TRIZ inventive principles, and emergent value discovery.

## Analysis Modes

This skill operates in **4 modes** depending on the inputs:

| Mode | Inputs | Primary Value |
|------|--------|---------------|
| **Codebase vs Codebase(s)** | 2+ project directories | Enterprise maturity comparison |
| **Codebase vs Research** | Project dir + paper files | Innovation integration potential |
| **Research vs Research** | 2+ paper/document files | Novelty and approach comparison |
| **Innovation Extraction** | Any source + target codebase | Hidden value-add discovery |

## Workflow

### Phase -1: KG-Native Discovery & Analysis (Preferred)

The Knowledge Graph (via the `agent-utilities-kg` MCP server) is the **primary source of truth**.
The KG backend provides **native layered analysis** — use MCP tools first, scripts second.

#### Layer 1 — Vector Discovery (No LLM, instant)
Use `kg_search` with `mode='discover'` for native cross-referencing:
```
kg_search(query="multi-agent orchestration", mode="discover", top_k=20)
```
Returns enriched results with:
- Biomimicry signals (swarm, colony, pheromone, neural, immune, etc.)
- Tech signals (attention, rag, multi-agent, planning, tool use, etc.)
- Innovation claims extracted from content
- Domain-level recommendations with priority rankings

#### Layer 2 — LLM Synthesis
Use `kg_analyze` with `action='synthesize'` for LLM-powered feature extraction:
```
kg_analyze(query="multi-agent orchestration", action="synthesize", top_k=10)
```
Runs Layer 1 discovery + LLM synthesis via Pydantic structured output (`output_type`).
Returns validated `FeatureRecommendation` objects with implementation sketches and priority scores.
Uses grammar-constrained JSON decoding — **zero regex parsing, zero JSON errors**.

#### Layer 3 — Deep Extraction
Use `kg_analyze` with `action='deep_extract'` for L1+L2+L3:
```
kg_analyze(query="knowledge graph retrieval", action="deep_extract", top_k=10)
```
Performs **batched** deep per-match extraction in a SINGLE LLM call (leveraging
256K+ context windows). Returns algorithms, data structures, architectural patterns,
and integration blueprints via Pydantic `DeepExtractionResult`.

#### Layer 4 — Full Pipeline (Background - Recommended)
Use `kg_analyze` with `action='background_research'` for the complete L1→L2→L3→OWL pipeline:
```
kg_analyze(query="feature extraction for agent framework", action="background_research", top_k=15)
```
Executes all layers via a **non-blocking background task** (preventing synchronous timeouts on large LLM contexts):
1. L1: Vector discovery (instant, no LLM)
2. L2: LLM synthesis → validated `SynthesisResult`
3. L3: Batched deep extraction → validated `DeepExtractionResult`
4. OWL: Lightweight reasoning cycle → transitive/symmetric closure

Returns a `job_id` immediately. Monitor progress using `kg_jobs(action='status', job_id='...')`.

#### OWL Reasoning Cycle
Trigger a standalone OWL reasoning cycle via `kg_inspect`:
```
kg_inspect(view="owl_cycle")
```
Runs the promote → reason → downfeed cycle on the Knowledge Graph, discovering
transitive and symmetric relationships from recently added edges.

#### Standards Applied
- **SKOS** (W3C Simple Knowledge Organization System) — Concept hierarchies
- **SSSOM** (Standardized Semantic Sets of Mappings) — Cross-domain alignment
- **CodeTaxo** (ACL 2024) — LLM-driven code taxonomy expansion

#### When to use MCP tools vs scripts
| Situation | Use |
|-----------|-----|
| Quick discovery ("what papers match X?") | `kg_search(mode='discover')` |
| Feature recommendations from research | `kg_analyze(action='synthesize')` |
| Deep technical extraction (Synchronous) | `kg_analyze(action='deep_extract')` |
| **Full automated pipeline (recommended)** | **`kg_analyze(action='background_research')`** |
| OWL reasoning enrichment | `kg_inspect(view='owl_cycle')` |
| Full codebase-vs-codebase comparison | Scripts (Phase 1-8) |
| Exhaustive all-concepts cross-ref | `concept_cross_reference.py --kg` |

**Default to MCP**: If the user does not specify local directories, you MUST default to using the `agent-utilities-kg` MCP server (`kg_search`, `kg_analyze`, `kg_query`) to retrieve and analyze data from the Knowledge Graph.

**Dynamic Ingestion**: If the user specifies a local directory that is not yet in the Knowledge Graph, you MUST first run the `kg_ingest` MCP tool to import it into the graph *before* beginning the comparison.

**Conversational KG Mining**: If the user asks a broad, open-ended question (e.g., *"From all the research papers we have ingested, what would be good features to implement?"*), operate in Conversational Mining Mode:
1. Run `kg_analyze(action='background_research', query="<topic>", top_k=15)` for a complete automated analysis without blocking.
2. Monitor the job via `kg_jobs`. The job handles L1 discovery → L2 synthesis → L3 extraction → OWL enrichment.
3. Synthesize the findings into feature recommendations without needing to run the traditional file-based analysis scripts.

**Concept-ID-Seeded Discovery**: If the target project has a concept registry (e.g., `docs/concept_map.md` with `CONCEPT:ID` entries), you SHOULD use concept-aware workflows:
1. Parse the concept map to extract all concept IDs and descriptions.
2. For each concept, run `kg_search(mode='discover')` to find relevant Article nodes with signal enrichment.
3. For high-priority matches, run `kg_analyze(action='full_pipeline')` for the complete extraction pipeline.
4. This produces a **concept × paper relevance matrix** that maps each architectural concept to research-backed improvement candidates.

The concept-ID approach is especially powerful when:
- The project has a formal concept registry with `CONCEPT:ID` tags in code
- You want to discover which research papers are most relevant to which existing features
- You need to prioritize enhancements by architectural pillar or concept scheme

```bash
# Discover KG sources matching a query
python scripts/discover_projects.py --kg-query "multi-agent orchestration"

# Concept-ID cross-reference (all concepts, from KG)
python scripts/concept_cross_reference.py --kg

# Concept-ID cross-reference (from a concept_map.md file)
python scripts/concept_cross_reference.py --concept-map /path/to/docs/concept_map.md

# Filter to specific pillars
python scripts/concept_cross_reference.py --kg --pillars KG AHE

# Combine KG sources with filesystem paths
python scripts/discover_projects.py --kg-query "knowledge graph" /path/to/project1
```

KG sources are materialized to `~/.scholarx/analysis/` as markdown files with
embedded metadata for downstream analysis scripts.

## Steps

### Step 1: pre_flight_config
Before starting any comparative analysis, gather the following configuration from the user. Ask if not explicitly stated:
1. **Primary Project**: Which codebase is the primary target for enhancement?
2. **Knowledge Graph Available?**: Is the `agent-utilities-kg` MCP server running?
3. **Concept Registry?**: Does the project have a concept map (e.g., `docs/concept_map.md` with `CONCEPT:ID` tags)?
4. **Architecture Docs?**: Does the project have C4 architecture diagrams?
5. **Analysis Depth**: Full analysis or focused analysis?

### Step 2: discovery_classification [depends_on: pre_flight_config]
Classify inputs (codebase vs research), detect language ecosystems, clone Git URLs if provided into a temporary folder, and rank all comparison items by their potential value to the primary target codebase (0-100 composite ranking):
- Requires: `scripts/discover_projects.py` and `scripts/rank_relevance.py` (or KG actions `relevance_rankings` / `relevance_sweep`)
```bash
python scripts/discover_projects.py /path/to/project1 /path/to/project2
python scripts/rank_relevance.py /path/to/target /path/to/paper1.md /path/to/codebase2
```

### Step 3: codebase_audit [depends_on: discovery_classification]
For codebase projects, analyze project governance, contributor diversity, bus factor, ecosystem health, SemVer adherence, dependency freshness, and code quality cyclomatic complexity:
- Requires: `scripts/analyze_governance.py`, `scripts/analyze_ecosystem_health.py`, and `scripts/analyze_code_quality.py`
```bash
python scripts/analyze_governance.py /path/to/project > results/project_ca001.json
python scripts/analyze_ecosystem_health.py /path/to/project > results/project_ca002.json
python scripts/analyze_code_quality.py /path/to/project > results/project_ca004.json
```

### Step 4: architecture_discovery [depends_on: discovery_classification]
Discover existing C4 architecture diagrams. If none exist, auto-generate one from AST-parsed package structures, entry points, and protocols. Trace hot paths via import graph tracing and identify design patterns (DI, mixins, lazy init, etc.):
- Requires: `scripts/analyze_architecture.py`
```bash
python scripts/analyze_architecture.py /path/to/project > results/project_ca003.json
```
For KG-integrated tracing:
```
kg_query(cypher="MATCH (m:Module)-[:IMPORTS*1..5]->(d:Module) WHERE m.source_path CONTAINS $path RETURN d.name")
```

### Step 5: security_reliability_check [depends_on: discovery_classification]
Scan for OWASP Top 10 pattern exposures, CWE anti-pattern density, hardcoded secrets, input validation coverage, and evaluate test suites (pyramid shape, frameworks, and intent):
- Requires: `scripts/analyze_security.py` and `scripts/analyze_testing.py`
```bash
python scripts/analyze_security.py /path/to/project > results/project_ca005.json
python scripts/analyze_testing.py /path/to/project > results/project_ca006.json
```

### Step 6: documentation_dx_review [depends_on: discovery_classification]
Grade README/AGENTS.md completeness, docstring coverage, and developer guides. Evaluate benchmarks, concurrency adoption, and container weight:
- Requires: `scripts/analyze_documentation.py` and `scripts/analyze_performance.py`
```bash
python scripts/analyze_documentation.py /path/to/project > results/project_ca007.json
python scripts/analyze_performance.py /path/to/project > results/project_ca008.json
```

### Step 7: innovation_extraction [depends_on: discovery_classification]
Extract innovation signals and map findings using biomimicry patterns, structure mapping, TRIZ principles, and emergent value discovery:
- Requires: `scripts/extract_innovations.py`
```bash
python scripts/extract_innovations.py --source /path/to/paper.md --target /path/to/codebase
```

### Step 8: concept_cross_reference [depends_on: discovery_classification]
Perform comprehensive concept-ID seeded cross-referencing against project concept registries, mapping paper findings to unique concept IDs:
- Requires: `scripts/concept_cross_reference.py`
```bash
python scripts/concept_cross_reference.py --kg --output results/concept_xref.json
```

### Step 9: architecture_gap_analysis [depends_on: codebase_audit, architecture_discovery, innovation_extraction]
Run codebase comparisons to identify architectural topology gaps, hot path divergence, divergent design patterns, and protocol gaps to synthesize actionable wiring opportunities:
- Requires: `scripts/analyze_architecture_diff.py`
```bash
python scripts/analyze_architecture_diff.py /path/to/source /path/to/target > results/arch_diff.json
```

### Step 10: generate_comparison_report [depends_on: security_reliability_check, documentation_dx_review, concept_cross_reference, architecture_gap_analysis]
Compile intermediate JSON results across all domains and modes into a single, cohesive comparative markdown report:
- Requires: `scripts/generate_comparison_report.py`
```bash
python scripts/generate_comparison_report.py results/*.json --output report.md
```

### Step 11: kg_persistence_cleanup [depends_on: generate_comparison_report]
Persist generated comparative reports to the Graph-OS Knowledge Graph, verify that each recommended feature passes the Wiring Audit Checklist, and clean up temporary cloned repository directories:
- Requires: `kg_ingest` MCP tool and standard cleanup commands.
```bash
# Verify Wiring Audit Checklist:
# - [ ] Entry Point Exists: Is there an MCP tool, A2A skill, or API route that exposes this?
# - [ ] Engine Integration: Is the feature callable from the core engine or a mixin?
# - [ ] Hot Path Reachable: Can you trace from an entry point to this code in <= 3 hops?
# - [ ] C4 Diagram Updated: Is the component shown in the architecture diagram?
# - [ ] Concept Map Updated: Is the CONCEPT:ID present and accurate?
# - [ ] Design Consistent: Does the implementation follow the same patterns as sibling modules?
# - [ ] Tests Exist: Is there at least one test that exercises the hot path through this feature?

rm -rf /home/apps/workspace/.specify/ca_repos/<session_id>
```

## Output Location Rules

1. **Codebase analysis** involving a primary project → `.specify/reports/comparative_analysis.md`
   inside that project directory
2. **Multi-codebase** with no primary → output to the workspace root or user-specified path
3. **Research-only analysis** → ask user for preferred output location (suggest `~/Documents/`)
4. **Innovation extraction** → same directory as the target codebase's `.specify/reports/`
5. Always support `--output <path>` override for any mode

## Grading System

All domains scored 0–100 with consistent grading:

| Grade | Score | Meaning |
|-------|-------|---------|
| A+ | 95–100 | Exceptional — industry-leading |
| A | 90–94 | Excellent — exceeds enterprise standards |
| B+ | 85–89 | Very Good — minor refinement opportunities |
| B | 80–84 | Good — solid foundation |
| C+ | 75–79 | Above Average — meets minimum standards |
| C | 70–74 | Acceptable — significant gaps |
| D | 60–69 | Below Standard — major issues |
| F | 0–59 | Failing — critical problems |

Read `references/grading_rubric.md` for detailed scoring criteria per domain, including
research paper scoring dimensions and innovation extraction scoring.

## Best Practices

- **Pre-Flight is MANDATORY**: Always run Pre-Flight Configuration before Phase 0.
  If the user hasn't specified KG availability, concept maps, or architecture docs, ASK.
- **Use MCP tools first**: `kg_search(mode='discover')` and `kg_analyze` are faster and
  richer than running scripts. Default to native KG analysis when KG is available.
- **Architecture analysis always runs**: Phase 3 + Phase 3.5 are never optional. Every
  codebase comparison MUST include C4 discovery, hot path identification, and design
  pattern detection. If no C4 exists, auto-generate one.
- **Architecture results drive gap analysis**: When producing the gap analysis report,
  the architecture differential (Phase 9.7) MUST inform which features to recommend.
  Never recommend a feature without identifying its wiring path into the target's hot path.
- **Wire or Discard**: Implementations must adhere to the Wire-First heuristic (≤3 hops from an entry point). If a feature cannot be wired directly into a hot path or duplicates an existing concept (Similarity ≥ 0.7), it must be extended or discarded. Dead code is prohibited.
- **Wiring opportunities in implementation plans**: When the analysis feeds into an
  implementation plan (SDD or otherwise), every recommended feature MUST include:
  1. Which existing hot-path module it wires into
  2. Which entry point exposes it (MCP tool, A2A skill, API route)
  3. Which C4 component it belongs to
- **Adherence verification post-implementation**: After implementing features from
  this analysis, run the Wiring Audit Checklist (Phase 10.5) to verify nothing was
  bolted on without hot-path integration.
- **Run Phase 0 first** to auto-detect mode and avoid running irrelevant analyzers.
- **Save intermediate JSON results** so the report generator can be re-run without re-analysis.
- **Read-only analysis**: Never modify the target projects. Only read and report.
  Exception: auto-generated C4 diagrams are written to `.specify/reports/`.
- **Innovation extraction is always valuable**: Even in pure codebase comparisons, run
  Phase 9 between codebases to discover hidden synergies and emergent value.
- **Ask before expensive operations**: If a project is very large (>100k LOC), warn the
  user that analysis may take longer and offer to skip heavy domains.

## Bundled Resources

### Scripts
- `scripts/discover_projects.py` — CA-000: Input classification and metadata extraction
- `scripts/analyze_governance.py` — CA-001: License, ownership, bus factor analysis
- `scripts/analyze_ecosystem_health.py` — CA-002: Git activity, releases, CI, deps
- `scripts/analyze_architecture.py` — CA-003: Protocols, types, modules, 12-Factor, **C4 discovery, hot paths, design patterns, auto-generation**
- `scripts/analyze_architecture_diff.py` — CA-003b: Architecture differential analysis between two codebases
- `scripts/analyze_code_quality.py` — CA-004: Complexity, duplication, stubs, length
- `scripts/rank_relevance.py` — CA-004b: Per-item relevance ranking against a target codebase (filesystem + KG modes)
- `scripts/analyze_security.py` — CA-005: OWASP/CWE patterns, secrets, auth posture
- `scripts/analyze_testing.py` — CA-006: Test suite, coverage, pyramid, quality
- `scripts/analyze_documentation.py` — CA-007: README grading, docstrings, artifacts
- `scripts/analyze_performance.py` — CA-008: Benchmarks, deps, async, containers
- `scripts/extract_innovations.py` — CA-010: Biomimicry, analogical reasoning, synergies (+ `--concept-id`, `--kg-source`)
- `scripts/concept_cross_reference.py` — CA-011: Concept-seeded cross-reference engine
- `scripts/generate_comparison_report.py` — CA-009: Unified report with radar charts

### References
- `references/grading_rubric.md` — Scoring criteria for all domains and modes
- `references/industry_frameworks.md` — CHAOSS, DORA, OWASP, 12-Factor, SOLID, ISO 25010
- `references/license_compatibility.md` — OSI/SPDX compatibility matrix and risk tiers
- `references/architecture_patterns.md` — Clean/hexagonal/modular pattern detection
- `references/architecture_discovery.md` — C4 detection, KG reconstruction, hot path heuristics, wiring audit checklist
- `references/security_standards.md` — CWE/OWASP detection patterns and scoring
- `references/innovation_extraction.md` — Biomimicry, TRIZ, Structure Mapping methodology
- `references/report_template.md` — Markdown comparison report template

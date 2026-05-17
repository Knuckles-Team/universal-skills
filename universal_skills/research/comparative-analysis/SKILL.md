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
  version: '0.11.0'
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

### Pre-Flight Configuration (MANDATORY — before any analysis)

Before starting any comparative analysis, you MUST gather the following configuration
from the user. If the user's prompt does not explicitly state these, ASK before proceeding:

#### Required Questions

1. **Primary Project**: "Which codebase is the primary target for enhancement?"
   - This determines which project receives the gap recommendations
   - All gaps, wiring opportunities, and innovations are framed relative to this project

2. **Knowledge Graph Available?**: "Do you have the `agent-utilities-kg` MCP server running?"
   - If **YES** → Use KG-native discovery (Phase -1) for all analysis. Enables:
     - `kg_search(mode='discover')` for research cross-referencing
     - `kg_query` for import graph tracing and blast radius analysis
     - `kg_analyze` for LLM-powered feature extraction
     - Concept-ID-seeded cross-referencing from ingested concept maps
   - If **NO** → Fall back to filesystem-only scripts (Phases 1-8)

3. **Concept Registry?**: "Does your project have a concept map (e.g., `docs/concept_map.md` with `CONCEPT:ID` tags)?"
   - If **YES** → Enable Phase 9.5 concept cross-reference for pillar-aware enhancement mapping
   - If **NO** → Skip concept cross-reference, use general feature extraction only

4. **Architecture Docs?**: "Does your project have C4 architecture diagrams (e.g., `docs/pillars/architecture_c4.md`)?"
   - If **YES** → Phase 3.5 will discover and parse them for topology-aware gap analysis
   - If **NO** → Phase 3.5 will auto-generate a C4 diagram from AST and save to `.specify/reports/generated_c4.md`

5. **Analysis Depth**: "Do you want a full analysis (all 8 domains + architecture + innovation) or focused analysis (specific domains only)?"
   - **Full** → Run Phases 1-10.5
   - **Focused** → Ask which domains to include (e.g., "architecture + security only")

#### Optional Questions (ask if context suggests relevance)

6. **Research Papers?**: "Should I cross-reference against research papers in the KG or specific papers?"
7. **Comparison Codebases?**: "Are there specific codebases to compare against, or should I use KG-ingested sources?"
8. **Output Location**: "Where should the report be saved?" (default: `.specify/reports/comparative_analysis.md`)

> [!IMPORTANT]
> Do NOT skip Pre-Flight. Gathering these answers up front avoids wasted analysis
> and ensures the maximum-capability configuration is used every time.

### Phase 0: Discovery & Classification

1. Run `scripts/discover_projects.py` with all target paths to classify each input as
   `codebase` or `research` and detect language ecosystems.
2. The script auto-determines the analysis mode based on input types.
3. If mode is ambiguous, ask the user to clarify intent.

```bash
python scripts/discover_projects.py /path/to/project1 /path/to/project2
python scripts/discover_projects.py https://github.com/example/repo /local/project
python scripts/discover_projects.py --mode research /path/to/paper1.md /path/to/paper2.md
```

If Git URLs are provided, the script will automatically clone them into a temporary directory (`.specify/ca_repos/<session_id>`) using `repository-manager` and substitute the URL with the local cloned path in the output JSON.

### Phase 0.5: Relevance Pre-Ranking (MANDATORY)

Before running full analysis, rank all comparison items by their potential value to the
primary target codebase. This ensures the most relevant items are analyzed first.

#### With KG Available

1. Check for pre-computed rankings:
```
kg_analyze(action='relevance_rankings', query='<target-codebase-name>', top_k=20)
```

2. If rankings exist and are recent (< 60 min old), present the top items to the user:
   - Show ranked list with per-dimension scores (semantic, concept overlap, architecture compatibility, innovation, feasibility)
   - Ask user which items to analyze in depth or confirm "analyze all"

3. If no rankings exist, trigger a background sweep:
```
kg_analyze(action='relevance_sweep', query='<target-codebase-name>')
```
Then proceed with analysis while the sweep runs — results will be available for future runs.

#### Without KG (Filesystem Fallback)

Run the standalone ranking script:
```bash
python scripts/rank_relevance.py /path/to/target /path/to/paper1.md /path/to/codebase2
```

This uses AST analysis and keyword matching to produce a ranked list without embeddings.

#### Ranking Dimensions (0-100 composite)

| Dimension | Weight | Description |
|-----------|--------|-------------|
| Semantic Relevance | 0-30 | Embedding cosine similarity or keyword overlap |
| Concept Overlap | 0-20 | Shared technical concepts (KG, agent, protocol, etc.) |
| Architecture Compatibility | 0-20 | Design pattern alignment |
| Innovation Potential | 0-20 | Novel features not in target |
| Feasibility | 0-10 | Integration ease (Python, same patterns, etc.) |

Rankings are persisted in the KG as `RELEVANCE_SCORED` edges and auto-refreshed
every 60 minutes by the background daemon. Use rankings to prioritize which items
get full analysis and to inform gap recommendations.

### Phase 1: Governance Analysis (Codebase mode only)

Run for each codebase project:
```bash
python scripts/analyze_governance.py /path/to/project > results/project_ca001.json
```

Evaluates: License type and OSI compliance, contributor diversity and bus factor,
governance files (CODE_OF_CONDUCT, CONTRIBUTING, SECURITY, CODEOWNERS).

Read `references/license_compatibility.md` for license tier classification if the
user asks about license compatibility between projects.

### Phase 2: Ecosystem Health (Codebase mode only)

Run for each codebase project:
```bash
python scripts/analyze_ecosystem_health.py /path/to/project > results/project_ca002.json
```

Evaluates: Git commit frequency and recency, release cadence and SemVer adherence,
CI/CD pipeline presence, dependency freshness and pinning rates.

### Phase 3: Architecture & Design (Codebase mode only)

Run for each codebase project:
```bash
python scripts/analyze_architecture.py /path/to/project > results/project_ca003.json
```

Evaluates: Protocol support (MCP, A2A, ACP, REST, gRPC, GraphQL), type annotation
coverage, module structure and nesting depth, 12-Factor compliance signals.

**New in v0.12**: Also discovers existing C4 architecture diagrams, identifies hot paths
via import graph tracing, detects design patterns (mixin, DI, lazy init, factory, etc.),
and **auto-generates a C4 diagram** to `.specify/reports/generated_c4.md` if none exists.

Read `references/architecture_patterns.md` for pattern detection criteria.
Read `references/architecture_discovery.md` for C4 detection and hot path methodology.

### Phase 3.5: Architecture Discovery (Always runs — all modes)

This phase runs automatically during Phase 3 and provides:

1. **C4 Diagram Discovery**: Scans `docs/`, `.specify/`, and root for existing C4
   mermaid diagrams (`C4Context`, `C4Container`, `C4Component`, `C4Deployment`).
2. **C4 Auto-Generation**: If no C4 exists, generates one from AST-parsed package
   structure + detected protocols + entry points. Saved to `.specify/reports/generated_c4.md`.
3. **Hot Path Identification**: Traces from entry points (MCP tools, A2A skills, CLI,
   FastAPI routes) through import graph to classify modules as hot/warm/cold.
4. **Design Pattern Detection**: Identifies architectural patterns via AST: mixin,
   dependency injection, lazy init, plugin registry, event-driven, protocol-oriented,
   factory, strategy.

For KG-integrated workflows, hot path tracing uses the KG's `IMPORTS` edges:
```
kg_query(cypher="MATCH (m:Module)-[:IMPORTS*1..5]->(d:Module) WHERE m.source_path CONTAINS $path RETURN d.name")
```

The output feeds directly into Phase 9.7 (Architecture Gap Analysis) and Phase 10.5
(Architecture Adherence Verification).

### Phase 4: Code Quality (Codebase mode only)

Run for each codebase project:
```bash
python scripts/analyze_code_quality.py /path/to/project > results/project_ca004.json
```

Evaluates: Cyclomatic complexity (McCabe), code duplication percentage, stub/TODO/FIXME
density, function length distribution, dead code indicators.

### Phase 5: Security & Compliance (Codebase mode only)

Run for each codebase project:
```bash
python scripts/analyze_security.py /path/to/project > results/project_ca005.json
```

Evaluates: OWASP Top 10 pattern exposure, CWE anti-pattern density, hardcoded secret
detection, input validation coverage, auth framework presence.

Read `references/security_standards.md` for OWASP/CWE detection pattern reference.

### Phase 6: Testing & Reliability (Codebase mode only)

Run for each codebase project:
```bash
python scripts/analyze_testing.py /path/to/project > results/project_ca006.json
```

Evaluates: Test suite presence and framework, test count and test-to-code ratio,
testing pyramid shape (unit > integration > e2e), quality indicators (fixtures,
parametrize, markers, timeouts).

### Phase 7: Documentation & DX (Codebase mode only)

Run for each codebase project:
```bash
python scripts/analyze_documentation.py /path/to/project > results/project_ca007.json
```

Evaluates: README completeness (15 criteria), docstring coverage percentage,
documentation artifacts (docs/, CHANGELOG, CONTRIBUTING, examples/).

### Phase 8: Performance & Cost (Codebase mode only)

Run for each codebase project:
```bash
python scripts/analyze_performance.py /path/to/project > results/project_ca008.json
```

Evaluates: Benchmark suite presence, dependency count and weight, async/concurrency
adoption ratio, container configuration.

### Phase 9: Innovation Extraction (All modes)

Run when comparing research papers to codebases or discovering cross-domain innovations:
```bash
python scripts/extract_innovations.py --source /path/to/paper.md --target /path/to/codebase
python scripts/extract_innovations.py --sources /path/to/paper1.md /path/to/paper2.md
```

Applies 5 methodologies:
1. **Biomimicry Pattern Matching** — Maps nature-inspired concepts to software patterns
2. **Analogical Reasoning (Structure Mapping)** — Transfers relational structures across domains
3. **TRIZ Inventive Principles** — Systematic contradiction resolution
4. **Emergent Value Discovery** — Identifies "free" capabilities from integration
5. **First Principles Decomposition** — Reconstructs novel combinations from primitives

Read `references/innovation_extraction.md` for full methodology details.

### Phase 9.5: Concept Cross-Reference (Concept-ID mode)

Run when mapping research findings directly to a project's concept registry:
```bash
# Full exhaustive cross-reference (all concepts × all papers)
python scripts/concept_cross_reference.py --kg --output results/concept_xref.json

# Filter to specific pillars
python scripts/concept_cross_reference.py --kg --pillars KG AHE --output results/concept_xref.json

# From a filesystem concept map
python scripts/concept_cross_reference.py --concept-map /path/to/concept_map.md --output results/concept_xref.json

# With custom thresholds
python scripts/concept_cross_reference.py --kg --threshold 0.70 --top-k 20
```

This phase:
1. Parses all concept IDs from the KG or concept_map.md
2. For each concept, runs `kg_search` to find relevant Article (paper) chunks
3. Extracts innovation signals (biomimicry, tech keywords, claims) per match
4. Builds prioritized enhancement recommendations with Emergent Value scores
5. Groups recommendations by pillar for architectural traceability

The output JSON contains:
- `summary`: Concept counts, match counts, priority breakdown by pillar
- `cross_reference`: Per-concept results with matched papers and similarity scores
- `recommendations`: Ranked list of enhancement opportunities with EV scores

Also supports concept-tagged innovation extraction:
```bash
# Tag innovations for a specific concept
python scripts/extract_innovations.py --source /path/to/paper.md --concept-id KG-2.4

# Pull innovations from KG Article nodes
python scripts/extract_innovations.py --kg-source "hypergraph reasoning" --target /path/to/codebase
```

### Phase 9.7: Architecture Gap Analysis (Codebase comparisons)

Run when comparing two or more codebases to identify architectural gaps:
```bash
python scripts/analyze_architecture_diff.py /path/to/source /path/to/target > results/arch_diff.json
```

Performs 4 differential analyses:
1. **Component Topology Diff**: C4 components in source but not target
2. **Hot Path Diff**: Entry point type coverage and reachability divergence
3. **Design Pattern Diff**: Divergent implementation strategies with adoption recommendations
4. **Protocol Diff**: Protocol support gaps

Synthesizes **wiring opportunities** — actionable recommendations for where target should
integrate source innovations, including:
- Which existing hot-path modules to wire new features into
- Which cold modules need to be connected or removed
- Which design patterns to adopt from the source

> [!IMPORTANT]
> When creating an implementation plan from this analysis, every new feature MUST
> have a documented wiring path to an existing hot-path entry point. Features that
> are "bolted on" without hot-path integration are architectural debt.

### Phase 10: Report Generation & KG Persistence

Generate the unified comparison report:
```bash
python scripts/generate_comparison_report.py results/*.json --output report.md
```

For codebase analysis, output to `.specify/reports/comparative_analysis.md`.
For research-only analysis, ask the user where to save the report (default: current working directory). The user may specify paths like `~/Documents/`.

The report now includes these architecture sections:
- **Architecture Topology**: C4 component map for each project (discovered or auto-generated)
- **Architecture Differential**: Side-by-side component/pattern comparison
- **Wiring Opportunities**: Prioritized list of where new features should integrate
- **Design Decisions Required**: Conflicts that need human judgment

**KG Persistence**: Once the markdown report artifact is successfully written to the filesystem, you MUST save the outcome back to the Knowledge Graph by using the `kg_ingest` MCP tool on the generated report file. This validates the findings and ensures the knowledge is accessible for future agentic interactions.

### Phase 10.5: Architecture Adherence Verification

After generating the report and before creating any implementation plan, verify that
each recommended feature passes the **Wiring Audit Checklist**:

- [ ] **Entry Point Exists**: Is there an MCP tool, A2A skill, or API route that exposes this?
- [ ] **Engine Integration**: Is the feature callable from the core engine or a mixin?
- [ ] **Hot Path Reachable**: Can you trace from an entry point to this code in ≤3 hops?
- [ ] **C4 Diagram Updated**: Is the component shown in the architecture diagram?
- [ ] **Concept Map Updated**: Is the CONCEPT:ID present and accurate?
- [ ] **Design Consistent**: Does the implementation follow the same patterns as sibling modules?
- [ ] **Tests Exist**: Is there at least one test that exercises the hot path through this feature?

This checklist should be included in the implementation plan artifact. Features that
cannot satisfy items 1-3 need architectural redesign before implementation.

Read `references/architecture_discovery.md` for detailed methodology.

### Phase 11: Cleanup (If Applicable)

If Git URLs were provided in Phase 0, `discover_projects.py` will output a `cleanup_instruction` in the JSON and print a terminal warning.
After successfully generating the comparison report in Phase 10, **you must delete the temporary directory** containing the cloned repositories to free up workspace space:
```bash
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

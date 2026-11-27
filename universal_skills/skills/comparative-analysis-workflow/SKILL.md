---
name: comparative-analysis-workflow
skill_type: workflow
description: >-
  Parallel execution workflow for comparative analysis and innovation extraction using the Unified Parallel Engine
domain: research-workflows
agent: researcher
team_config:
  name: comparative_analysis_team
  task_pattern: research and codebase comparison
  execution_mode: parallel
  specialist_ids:
    - classification-agent
    - audit-agent
    - security-agent
    - innovation-agent
    - synthesis-agent
  tool_assignments:
    classification-agent: [rep_rm_workspace, rep_rm_projects]
    audit-agent: [rep_rm_projects]
    security-agent: [rep_rm_projects]
    innovation-agent: [rep_rm_workspace]
    synthesis-agent: [graph_write, rep_rm_git]
tags: [research, comparative-analysis]
concept: CONCEPT:RES-001
metadata:
  version: '1.7.0'
---

# Comparative Analysis Workflow

**CONCEPT:RES-001**

Parallel execution workflow for comparative analysis and innovation extraction using the Unified Parallel Engine

## Steps

1. Gather target codebases, papers, concept registries and C4 files from the user (Step 1). Verify that `pre_flight_config_artifacts` lists every target path and that each path exists with `ls`.
2. Classify the inputs and rank their relevance (Step 2). Verify that `discovery_classification_artifacts` labels each input as codebase or research with a language ecosystem.
3. Run the six parallel analyses: codebase audit, architecture discovery, security check, documentation review, innovation extraction and concept cross reference (Steps 3-8). Verify that each of the six `*_artifacts` outputs exists and is non-empty.
4. Compute the architecture gap analysis between the targets (Step 9). Verify that `architecture_gap_analysis_artifacts` lists at least one wiring opportunity or states that none was found.
5. Compile the unified comparison report with 0-100 scorecards under `.specify/` (Step 10). Verify that `ls .specify/` shows the report file.
6. Ingest the report and edges with `graph_write` and purge temporary paths (Step 11). Verify that a `graph_query` returns the report node and that the temporary paths no longer exist.

### Step 1: Pre Flight Config
**Agent**: `classification-agent`
**Tools**: `rep_rm_workspace, rep_rm_projects`

Gather inputs, configuration params, target codebases, papers, concept registries, and C4 files from the user.
Expected: `pre_flight_config_artifacts`

### Step 2: Discovery Classification [depends_on: pre_flight_config]
**Agent**: `classification-agent`
**Tools**: `rep_rm_workspace, rep_rm_projects`

Classify input files (codebases vs research), detect language ecosystems, and calculate composite relevance rankings.
Expected: `discovery_classification_artifacts`

### Step 3: Codebase Audit [depends_on: discovery_classification]
**Agent**: `audit-agent`
**Tools**: `rep_rm_projects`

Analyze target codebase governance, active ecosystem health, CI posture, and basic complexity metrics.
Expected: `codebase_audit_artifacts`

### Step 4: Architecture Discovery [depends_on: discovery_classification]
**Agent**: `audit-agent`
**Tools**: `rep_rm_projects`

Identify existing C4 diagrams or auto-generate AST-based C4 models, tracing module imports and hot paths.
Expected: `architecture_discovery_artifacts`

### Step 5: Security Reliability Check [depends_on: discovery_classification]
**Agent**: `security-agent`
**Tools**: `rep_rm_projects`

Scan for OWASP Top 10 patterns, CWE exposures, hardcoded keys, and evaluate test coverage/pyramid intent.
Expected: `security_reliability_check_artifacts`

### Step 6: Documentation DX Review [depends_on: discovery_classification]
**Agent**: `audit-agent`
**Tools**: `rep_rm_projects`

Evaluate readme grades, docstring coverage, concurrency, and performance benchmark suites.
Expected: `documentation_dx_review_artifacts`

### Step 7: Innovation Extraction [depends_on: discovery_classification]
**Agent**: `innovation-agent`
**Tools**: `rep_rm_workspace`

Extract innovation claims, biomimicry mappings, and TRIZ inventive principles from papers and code.
Expected: `innovation_extraction_artifacts`

### Step 8: Concept Cross Reference [depends_on: discovery_classification]
**Agent**: `innovation-agent`
**Tools**: `rep_rm_workspace`

Perform concept-ID seeded cross-referencing against registries to map findings to unique architectural concept IDs.
Expected: `concept_cross_reference_artifacts`

### Step 9: Architecture Gap Analysis [depends_on: codebase_audit, architecture_discovery, innovation_extraction]
**Agent**: `synthesis-agent`
**Tools**: `rep_rm_projects`

Perform architecture topology differential and gap analysis between targets to discover wiring opportunities.
Expected: `architecture_gap_analysis_artifacts`

### Step 10: Generate Comparison Report [depends_on: security_reliability_check, documentation_dx_review, concept_cross_reference, architecture_gap_analysis]
**Agent**: `synthesis-agent`
**Tools**: `rep_rm_workspace`

Compile all intermediate domain analysis results into a single unified Markdown comparative analysis report.
Expected: `generate_comparison_report_artifacts`

### Step 11: KG Persistence Cleanup [depends_on: generate_comparison_report]
**Agent**: `synthesis-agent`
**Tools**: `graph_write`

Ingest final reports, wiring audits, and relationship edges into Arbora Knowledge Graph, and purge temporary file paths.
Expected: `kg_persistence_cleanup_artifacts`

## Failure recovery

| Failure | Cause | Recovery |
|---|---|---|
| Classification mislabels a repo as research | The input path holds only docs or a PDF folder | Point Step 1 at the repository root, correct the path in `pre_flight_config_artifacts`, and rerun Step 2 |
| C4 model auto-generation produces an empty diagram | The AST scan found no importable modules for the language | Supply an existing C4 file in Step 1 or restrict the scan to the source directory |
| Report is missing a domain section | One of the parallel analysis steps failed | Open the missing `*_artifacts` output, rerun only that step, and regenerate the report in Step 10 |
| Temporary paths remain after Step 11 | The cleanup ran before the ingest finished | Confirm the ingest finished by querying the node with `graph_query`, and remove the leftover paths manually |


## Output
- Graded comparative analysis report persisted in `.specify/`
- Standardized 0-100 scorecards across all target domains with radar chart inputs
- Nodes and edges persisted to Knowledge Graph representing cross-domain/cross-project mappings

## Execution

Run this workflow as a dependency-ordered DAG. Steps with no unmet `depends_on` run in parallel; dependents run after their prerequisites complete.

- **Run first (in parallel):** Step 1 — Pre Flight Config
- **After level 0:** Step 2 — Discovery Classification
- **After level 1:** Step 3 — Codebase Audit; Step 4 — Architecture Discovery; Step 5 — Security Reliability Check; Step 6 — Documentation DX Review; Step 7 — Innovation Extraction; Step 8 — Concept Cross Reference
- **After level 2:** Step 9 — Architecture Gap Analysis
- **After level 3:** Step 10 — Generate Comparison Report
- **After level 4:** Step 11 — KG Persistence Cleanup

**Execution:** If arbora is reachable, offload the whole DAG via `graph_orchestrate action=execute_workflow` (or the `kg-delegate` skill) for true parallel/swarm execution. Otherwise execute the steps natively in dependency order: run steps with no unmet `depends_on` in parallel, then their dependents.

---
name: performance-review
skill_type: workflow
description: 'Run an employee performance review: gather OKRs and metrics, analyze performance
  against targets, and generate a review report. Use for periodic or annual performance
  evaluations and OKR tracking.'
domain: ops-workflows
agent: hr_operations_coordinator
team_config:
  name: performance_review_team
  task_pattern: performance evaluation and OKR tracking
  execution_mode: sequential
  specialist_ids:
    - hr-coordinator
    - analytics-agent
    - report-generator
  tool_assignments:
    hr-coordinator: [graph_query]
    analytics-agent: [graph_query, data_science_mcp]
    report-generator: [graph_write, document_tools]
concept: KG-2.12
metadata:
  version: '1.6.2'
---

# Performance Review Workflow

**CONCEPT:KG-2.12 — Company Operations Domain**

Periodic performance evaluation leveraging KG OKR cascading
for transparent, data-driven reviews.

## Steps

1. Gather OKRs via `graph_query` with cascadesTo traversal. Verify that individual OKRs have `okrProgress`.
2. Compute metrics with `graph_query` and `data_science_mcp`. Verify that completion rate and benchmarks exist.
3. Generate the review with `graph_write` and `document_tools`. Verify that the document includes the OKR scorecard.
4. Persist a `PerformanceReview` node. Verify that `graph_query` shows the `reviewedIn` edge.

### Step 0: Gather OKR Progress
**Agent**: `hr-coordinator`
**Tools**: `graph_query`

Query KG for employee's OKR hierarchy using cascadesTo traversal:
- Organization-level OKRs → Department OKRs → Individual OKRs
- okrProgress (0.0–1.0) for each objective
- Key result completion rates
- Cross-functional contributions (edges to other team's goals)

### Step 1: Compute Metrics & Trends
**Agent**: `analytics-agent`
**Tools**: `graph_query`, `data_science_mcp`

Analyze performance data:
- OKR completion rate vs. targets
- Competency growth (proficiencyLevel changes)
- Peer review scores (if available)
- Sprint velocity / throughput metrics
- Comparison to role-level benchmarks

### Step 2: Generate Review Document
**Agent**: `report-generator`
**Tools**: `graph_write`, `document_tools`

Generate structured performance review:
- Strengths and achievements
- Areas for improvement
- OKR scorecard with evidence links
- Development plan recommendations
- Compensation review recommendation (if applicable)

### Step 3: KG Persistence
**Agent**: `arbora`

Create PerformanceReview node linked to:
- Employee via reviewedIn edge
- OKR nodes via measuresGoal edges
- Next review cycle via scheduledFor

## Failure recovery

| Failure | Cause | Recovery |
|---|---|---|
| No OKRs | Employee unlinked | Create the missing employee-to-OKR links in the KG with `graph_write`, then re-run `graph_query` |
| Missing peer scores | None submitted | Record peer review scores as unavailable in the document and proceed |
| Rating unapproved | Manager missing | Hold the review in draft and route it to the manager for sign-off before writing `PerformanceReview` with `graph_write` |

## Output
- Performance review document (PDF/MD)
- PerformanceReview node in KG with reviewRating
- Development plan recommendations
- Compensation adjustment recommendation (for human review)

## Human Oversight Required
✅ Final performance ratings and compensation changes require manager approval.

## Execution

Run this workflow as a dependency-ordered DAG. Steps with no unmet `depends_on` run in parallel; dependents run after their prerequisites complete.

- **Run first (in parallel):** Step 0 — Gather OKR Progress; Step 1 — Compute Metrics & Trends; Step 2 — Generate Review Document; Step 3 — KG Persistence

**Execution:** If arbora is reachable, offload the whole DAG via `graph_orchestrate action=execute_workflow` (or the `kg-delegate` skill) for true parallel/swarm execution. Otherwise execute the steps natively in dependency order: run steps with no unmet `depends_on` in parallel, then their dependents.

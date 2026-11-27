---
name: legal-compliance
skill_type: workflow
description: 'Review legal and regulatory compliance: research applicable regulations, analyze
  contracts and policies, and check compliance. Use for legal compliance and regulatory
  review tasks.'
domain: ops-workflows
agent: legal_compliance_coordinator
team_config:
  name: legal_compliance_team
  task_pattern: legal compliance and regulatory review
  execution_mode: sequential
  specialist_ids:
    - legal-research-agent
    - contract-analyzer
    - compliance-checker
  tool_assignments:
    legal-research-agent: [graph_search, graph_query, sx_search]
    contract-analyzer: [graph_analyze, document_tools]
    compliance-checker: [graph_query, graph_write]
concept: KG-2.12
metadata:
  version: '1.7.0'
---

# Legal Compliance Review Workflow

**CONCEPT:KG-2.12 — Company Operations Domain**

Coordinates legal compliance review including statute research, regulatory
tracking, and compliance validation against the KG ontology_legal.ttl.

## Steps

1. Research law with the `legal-research-agent` using `graph_search`, `graph_query` and `sx_search`. Verify that relevant statutes and precedents are returned with citations.
2. Analyze contracts with the `contract-analyzer` using `document_tools` and `graph_analyze`. Verify that extracted clauses and risk factors are listed.
3. Validate compliance with the `compliance-checker` using `graph_query` against `FederalStatute`, `StateStatute` and `MunicipalCode`. Verify that non-compliance flags are listed.
4. Persist findings with `graph_write` as `LegalMatter`, `CaseLaw` and `RegulatoryFiling` nodes linked by `governedByStatute`. Verify that `graph_query` returns the `LegalMatter` node.
5. Escalate binding determinations on the `LegalMatter` to a human with a summary report. Verify that the report states recommendations and that no final decision was made automatically.

### Step 0: Legal Research
**Agent**: `legal-research-agent`
**Tools**: `graph_search`, `graph_query`, `sx_search`

Search US law databases via ScholarX and web-search. Query KG for existing
case law, statutes, and precedent relevant to the compliance matter.

### Step 1: Contract Analysis
**Agent**: `contract-analyzer`
**Tools**: `graph_analyze`, `document_tools`

Parse contracts using document-tools, extract clauses, identify risk factors.
Cross-reference against ontology_legal.ttl ContractClause classes.

### Step 2: Compliance Validation
**Agent**: `compliance-checker`
**Tools**: `graph_query`, `graph_write`

Validate findings against applicable FederalStatute, StateStatute, and
MunicipalCode entries in the KG. Flag non-compliance issues.

### Step 3: KG Persistence
**Agent**: `arbora`

Persist findings as LegalMatter + CaseLaw + RegulatoryFiling nodes in KG.
Create edges linking to applicable statutes via governedByStatute.

### Step 4: Human Escalation
Route all binding legal determinations to human oversight. Generate
a summary report with recommendations for human review.

## Failure recovery

| Failure | Cause | Recovery |
|---------|-------|----------|
| No statutes found | Search too narrow | Broaden the `sx_search` and `graph_search` terms and the jurisdiction. |
| Clause not mapped | Not in `ontology_legal.ttl` | Record it as unmapped and flag it for human review. |
| Final decision requested automatically | Misuse of the workflow | Refuse and route to the human escalation step. |

## Output
- LegalMatter node in KG with status + findings
- Compliance score (0.0–1.0)
- Risk assessment with recommended actions
- Escalation report for human review

## Human Oversight Required
✅ All final legal decisions require human approval.

## Execution

Run this workflow as a dependency-ordered DAG. Steps with no unmet `depends_on` run in parallel; dependents run after their prerequisites complete.

- **Run first (in parallel):** Step 0 — Legal Research; Step 1 — Contract Analysis; Step 2 — Compliance Validation; Step 3 — KG Persistence; Step 4 — Human Escalation

**Execution:** If arbora is reachable, offload the whole DAG via `graph_orchestrate action=execute_workflow` (or the `kg-delegate` skill) for true parallel/swarm execution. Otherwise execute the steps natively in dependency order: run steps with no unmet `depends_on` in parallel, then their dependents.

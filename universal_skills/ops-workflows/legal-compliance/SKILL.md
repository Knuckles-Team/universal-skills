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
  version: '1.2.1'
---

# Legal Compliance Review Workflow

**CONCEPT:KG-2.12 — Company Operations Domain**

Coordinates legal compliance review including statute research, regulatory
tracking, and compliance validation against the KG ontology_legal.ttl.

## Steps

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
**Agent**: `graph-os`

Persist findings as LegalMatter + CaseLaw + RegulatoryFiling nodes in KG.
Create edges linking to applicable statutes via governedByStatute.

### Step 4: Human Escalation
Route all binding legal determinations to human oversight. Generate
a summary report with recommendations for human review.

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

**Execution:** If graph-os is reachable, offload the whole DAG via `graph_orchestrate action=execute_workflow` (or the `kg-delegate` skill) for true parallel/swarm execution. Otherwise execute the steps natively in dependency order: run steps with no unmet `depends_on` in parallel, then their dependents.

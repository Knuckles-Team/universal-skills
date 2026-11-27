---
name: contract-review
skill_type: workflow
description: 'Review a contract for risk and compliance: parse the document, extract and assess
  clauses, research legal context, check compliance, and produce a risk report. Use
  when reviewing contracts or assessing contractual risk.'
domain: ops-workflows
agent: legal_compliance_coordinator
team_config:
  name: contract_review_team
  task_pattern: contract analysis and risk assessment
  execution_mode: sequential
  specialist_ids:
    - document-parser
    - clause-extractor
    - legal-research-agent
    - compliance-checker
    - report-generator
  tool_assignments:
    document-parser: [document_tools]
    clause-extractor: [graph_analyze]
    legal-research-agent: [graph_query, sx_search]
    compliance-checker: [graph_query]
    report-generator: [graph_write, document_tools]
concept: KG-2.12
metadata:
  version: '1.7.0'
---

# Contract Review Workflow

**CONCEPT:KG-2.12 — Company Operations Domain**

Automated contract analysis pipeline: parse → extract clauses → check
precedent → validate compliance → generate report with recommendations.

## Steps

1. Parse the contract PDF or DOCX into structured text with `document_tools` (Step 0). Verify that the parsed output lists section headings, numbered clauses and definitions.
2. Extract and classify clauses against `ontology_legal.ttl:ContractClause` with `graph_analyze` (Step 1). Verify that each clause carries a HIGH, MEDIUM or LOW risk label.
3. Check precedent with `graph_query` and `sx_search` for similar contracts, case law and statutes (Step 2). Verify that each cited precedent resolves to a KG node or a search result.
4. Validate the clauses against applicable law and governance documents using `graph_query` (Step 3). Verify that the output is a compliance checklist with a pass or fail per requirement.
5. Generate the review report and persist the Contract node with `graph_write` (Step 4). Verify that `graph_query` returns the Contract node with `hasClause` edges and that the report carries a 0.0-1.0 risk score.

### Step 0: Parse Contract Document
**Agent**: `document-parser`
**Tools**: `document_tools`

Parse contract PDF/DOCX. Extract full text with structural markup.
Identify section headings, numbered clauses, definitions, and exhibits.

### Step 1: Extract Clauses & Identify Risks
**Agent**: `clause-extractor`
**Tools**: `graph_analyze`

Extract and classify clauses against ontology_legal.ttl:ContractClause:
- Indemnification clauses
- Limitation of liability
- Non-compete / non-solicitation
- Intellectual property assignment
- Confidentiality / NDA provisions
- Termination conditions
- Governing law / jurisdiction
- Force majeure
- Auto-renewal provisions
- Data protection / privacy

Risk scoring: HIGH / MEDIUM / LOW per clause.

### Step 2: Check Precedent
**Agent**: `legal-research-agent`
**Tools**: `graph_query`, `sx_search`

Query KG for:
- Similar contracts previously reviewed
- Relevant case law via CaseLaw nodes
- Applicable statutes via governedByStatute edges
- Industry-standard clause language

### Step 3: Compliance Validation
**Agent**: `compliance-checker`
**Tools**: `graph_query`

Validate against applicable law:
- State contract law requirements
- Industry-specific regulations
- Company governance requirements (from CorporateGovernanceDoc)
- IP assignment compliance with employment agreements

### Step 4: Generate Review Report
**Agent**: `report-generator`
**Tools**: `graph_write`, `document_tools`

Generate structured review:
- Executive summary with overall risk score
- Clause-by-clause analysis with risk ratings
- Recommended modifications (redline suggestions)
- Precedent citations
- Compliance checklist

Persist to KG: Contract node with hasClause edges to extracted clauses.

## Failure recovery

| Failure | Cause | Recovery |
|---|---|---|
| Parsed text is empty or garbled | The PDF is a scanned image without a text layer | Run OCR on the file with `document_tools` and parse the OCR output instead |
| No precedent found | The KG holds no similar contracts or `sx_search` is unavailable | Widen the query to the clause type alone, check the search server is up, and record "no precedent" in the report |
| Clause lacks a risk rating | The clause matched no `ContractClause` class | Classify it manually against the ten listed clause types and mark it for human review |
| `graph_write` rejected | The Contract node violates the ontology or arbora is unreachable | Fix the node properties to match `ontology_legal.ttl`, confirm access with `graph_query`, and resubmit |


## Output
- Contract review report (PDF/MD)
- Risk score (0.0–1.0)
- Clause-by-clause analysis with risk ratings
- Contract and ContractClause nodes in KG

## Human Oversight Required
✅ All contract modifications and approvals require human review.

## Execution

Run this workflow as a dependency-ordered DAG. Steps with no unmet `depends_on` run in parallel; dependents run after their prerequisites complete.

- **Run first (in parallel):** Step 0 — Parse Contract Document; Step 1 — Extract Clauses & Identify Risks; Step 2 — Check Precedent; Step 3 — Compliance Validation; Step 4 — Generate Review Report

**Execution:** If arbora is reachable, offload the whole DAG via `graph_orchestrate action=execute_workflow` (or the `kg-delegate` skill) for true parallel/swarm execution. Otherwise execute the steps natively in dependency order: run steps with no unmet `depends_on` in parallel, then their dependents.

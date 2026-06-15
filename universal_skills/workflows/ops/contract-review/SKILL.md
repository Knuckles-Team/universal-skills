---
name: contract-review
description: 'Review a contract for risk and compliance: parse the document, extract and assess
  clauses, research legal context, check compliance, and produce a risk report. Use
  when reviewing contracts or assessing contractual risk.'
domain: ops
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
---

# Contract Review Workflow

**CONCEPT:KG-2.12 — Company Operations Domain**

Automated contract analysis pipeline: parse → extract clauses → check
precedent → validate compliance → generate report with recommendations.

## Steps

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

## Output
- Contract review report (PDF/MD)
- Risk score (0.0–1.0)
- Clause-by-clause analysis with risk ratings
- Contract and ContractClause nodes in KG

## Human Oversight Required
✅ All contract modifications and approvals require human review.

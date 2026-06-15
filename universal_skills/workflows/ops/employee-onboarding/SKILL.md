---
name: employee-onboarding
description: 'Onboard a new employee: generate onboarding documents, set up payroll and benefits,
  and provision systems access. Use when onboarding or provisioning a new hire.'
domain: ops
agent: hr_operations_coordinator
team_config:
  name: hr_onboarding_team
  task_pattern: employee onboarding and provisioning
  execution_mode: sequential
  specialist_ids:
    - hr-coordinator
    - document-generator
    - payroll-agent
    - benefits-agent
    - systems-provisioner
  tool_assignments:
    hr-coordinator: [graph_query, graph_write]
    document-generator: [document_tools]
    payroll-agent: [graph_query, graph_write]
    benefits-agent: [graph_query, graph_write]
    systems-provisioner: [systems_manager]
concept: KG-2.12
---

# Employee Onboarding Workflow

**CONCEPT:KG-2.12 — Company Operations Domain**

Full employee onboarding pipeline compliant with US employment law.
Handles I-9, W-4, payroll setup, benefits enrollment, and account provisioning.

## Steps

### Step 0: Gather New Hire Information
**Agent**: `hr-coordinator`

Collect employee details: name, SSN, address, position, department,
start date, salary, FLSA classification (exempt/non-exempt).

### Step 1: Generate Employment Documents
**Agent**: `document-generator`
**Tools**: `document_tools`

Generate the following documents:
- Offer letter
- I-9 (Employment Eligibility Verification)
- W-4 (Employee's Withholding Certificate)
- State withholding form (based on work state)
- Employee handbook acknowledgment
- At-will employment agreement (if applicable)

### Step 2: Payroll Setup
**Agent**: `payroll-agent`
**Tools**: `graph_query`, `graph_write`

Configure payroll in the ERP system (ERPNext/Akaunting/Odoo via adapter):
- Set up direct deposit
- Configure federal withholding per W-4
- Configure state withholding
- Set FICA/Medicare deductions
- Create PayrollRecord node in KG

### Step 3: Benefits Enrollment
**Agent**: `benefits-agent`
**Tools**: `graph_query`, `graph_write`

Enroll employee in eligible benefits plans:
- Medical/Dental/Vision (within 30-day enrollment window)
- 401(k) enrollment
- Life insurance
- Disability coverage
- Create BenefitsPlan enrollment edges in KG

### Step 4: KG Registration
**Agent**: `graph-os`

Create KG nodes:
- W2Employee (or Contractor1099) node
- PositionRole node
- Department assignment edge
- I9Verification node
- W4Form node
- FLSAClassification node
- Manager reportsTo edge

### Step 5: Systems Provisioning
**Agent**: `systems-provisioner`
**Tools**: `systems_manager`

Provision employee accounts:
- Email account
- Git/GitLab access
- Communication tools (Slack/Matrix/etc.)
- Project management (Plane) access
- VPN/SSH access (if applicable)

## US Compliance Checklist
- [ ] I-9 completed within 3 business days of hire
- [ ] W-4 configured before first payroll
- [ ] State withholding configured
- [ ] FLSA classification documented
- [ ] Benefits enrollment offered within 30 days
- [ ] Workers' compensation coverage verified
- [ ] EEO-1 category assigned

## Output
- Employee node in KG with all compliance documents linked
- Payroll configured in ERP
- Benefits enrollment confirmed
- All accounts provisioned

## Execution

Run this workflow as a dependency-ordered DAG. Steps with no unmet `depends_on` run in parallel; dependents run after their prerequisites complete.

- **Run first (in parallel):** Step 0 — Gather New Hire Information; Step 1 — Generate Employment Documents; Step 2 — Payroll Setup; Step 3 — Benefits Enrollment; Step 4 — KG Registration; Step 5 — Systems Provisioning

**Execution:** If graph-os is reachable, offload the whole DAG via `graph_orchestrate action=execute_workflow` (or the `kg-delegation-router` skill) for true parallel/swarm execution. Otherwise execute the steps natively in dependency order: run steps with no unmet `depends_on` in parallel, then their dependents.

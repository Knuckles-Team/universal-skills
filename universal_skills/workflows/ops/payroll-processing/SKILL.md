---
name: payroll_processing
domain: ops
agent: finance_operations_coordinator
team_config:
  name: payroll_processing_team
  task_pattern: payroll computation and disbursement
  execution_mode: sequential
  specialist_ids:
    - accounting-agent
    - tax-calculator
    - compliance-checker
    - payment-processor
  tool_assignments:
    accounting-agent: [graph_query]
    tax-calculator: [data_science_mcp]
    compliance-checker: [graph_query]
    payment-processor: [graph_write]
concept: KG-2.12
---

# Payroll Processing Workflow

**CONCEPT:KG-2.12 — Company Operations Domain**

Bi-weekly or monthly payroll processing with full US tax compliance.
Routes tax calculations to data-science-mcp for computation.

## Steps

### Step 0: Query Payroll Data
**Agent**: `accounting-agent`
**Tools**: `graph_query`

Query the ERP system (via abstracted adapter) for:
- Active employees and their compensation bands
- Hours worked (for non-exempt employees)
- PTO usage
- Bonus/commission accruals
- Pre-tax deductions (401k, HSA, FSA)

### Step 1: Compute Tax Withholdings
**Agent**: `tax-calculator`
**Tools**: `data_science_mcp`

Route to data-science-mcp on heavy hardware for computation:
- Federal income tax (per W-4 configuration)
- State income tax (per state withholding form)
- FICA (Social Security: 6.2% up to wage base + Medicare: 1.45%)
- Additional Medicare tax (0.9% above $200K)
- FUTA/SUTA (employer-side)

### Step 2: FLSA Compliance Validation
**Agent**: `compliance-checker`
**Tools**: `graph_query`

Validate against US employment law:
- Minimum wage compliance (federal $7.25 + state minimums)
- Overtime calculation for non-exempt (1.5x for >40 hrs/week)
- Tip credit calculations (if applicable)
- Youth wage compliance
- Garnishment limits (Title III CCPA)

### Step 3: Execute Payroll
**Agent**: `payment-processor`
**Tools**: `graph_write`

Execute via ERP adapter:
- Generate paystubs
- Initiate direct deposits
- Create PayrollRecord nodes in KG for each employee
- Log tax liability accruals
- Generate payroll journal entries

### Step 4: Post-Payroll Reporting
**Agent**: `graph-os`

KG persistence:
- PayrollRecord nodes with full tax breakdown
- Link to Employee, PayPeriod, and CompensationBand
- Update KPIs: total payroll expense, effective tax rate, benefits cost ratio

## Output
- PayrollRecord nodes in KG for all employees
- Paystubs generated
- Direct deposits initiated
- Tax liability journal entries created
- Compliance validation report

## Human Oversight Required
✅ Financial signing authority required for payroll disbursement.

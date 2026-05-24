---
name: sdd_full_lifecycle
description: End-to-end Spec-Driven Development: requirements parsing, concurrent implementation, QA test generation, and walkthrough verification.
domain: development
tags: [sdd, backend, frontend, qa, devops, verification]
---
# SDD Full Lifecycle Workflow

This workflow automates high-velocity software engineering: producing detailed technical specs, building backend layers, frontend components, and test cases concurrently, and verifying the entire deliverable.

### Step 1: Spec Generator [depends_on: none]
Create robust functional specifications, user story maps, and detailed acceptance criteria from raw requirements.
Expected: design-spec-produced

### Step 2: Python Backend Engineer [depends_on: spec-generator]
Implement stable database schemas, REST or gRPC controller endpoints, and business service validations matching the specification.
Expected: backend-built

### Step 3: TypeScript Frontend Developer [depends_on: spec-generator]
Develop modern, beautiful reactive UI page layouts, state managers, and network fetch hooks based on the specification.
Expected: frontend-built

### Step 4: QA Test Engineer [depends_on: spec-generator]
Write extensive pytest unit suites, backend endpoint test modules, and frontend integration or end-to-end browser tests.
Expected: tests-written

### Step 5: Verification Gate [depends_on: python-backend-engineer, typescript-frontend-developer, qa-test-engineer]
Execute the test suites, perform code coverage checks, run security audits, and generate a final walkthrough presentation.
Expected: product-verified

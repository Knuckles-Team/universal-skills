---
name: license_compliance_scan
description: Parallel execution workflow for license compliance scan using the Unified Parallel Engine
domain: dev-workflows
tags:
  - parallel-workflow
  - dev-workflows
  - mcp-repository-manager
---

# Parallel Workflow: License Compliance Scan

This workflow defines the topological parallel execution steps for license compliance scan.

## Steps

### Step 1: scan_deps
Execute the scan deps phase for the license_compliance_scan workflow under the dev-workflows domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: scan_deps_artifacts
### Step 2: check_licenses [depends_on: scan_deps]
Execute the check licenses phase for the license_compliance_scan workflow under the dev-workflows domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: check_licenses_artifacts
### Step 3: flag_violations [depends_on: check_licenses]
Execute the flag violations phase for the license_compliance_scan workflow under the dev-workflows domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: flag_violations_artifacts
### Step 4: report [depends_on: flag_violations]
Execute the report phase for the license_compliance_scan workflow under the dev-workflows domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: report_artifacts

---
name: port_scan_audit
description: Parallel execution workflow for port scan audit using the Unified Parallel Engine
domain: infra
tags:
  - parallel-workflow
  - infra
  - mcp-tunnel-manager
---

# Parallel Workflow: Port Scan Audit

This workflow defines the topological parallel execution steps for port scan audit.

## Steps

### Step 1: fan_out_per_host_nmap_scan
Execute the Fan-out per host: nmap scan phase for the port_scan_audit workflow under the infra domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: fan_out_per_host_nmap_scan_artifacts
### Step 2: compare_against_expected [depends_on: fan_out_per_host_nmap_scan]
Execute the compare against expected phase for the port_scan_audit workflow under the infra domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: compare_against_expected_artifacts
### Step 3: flag_anomalies [depends_on: compare_against_expected]
Execute the flag anomalies phase for the port_scan_audit workflow under the infra domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: flag_anomalies_artifacts

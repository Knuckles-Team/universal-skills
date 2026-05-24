---
name: firewall_rule_audit
description: Parallel execution workflow for firewall rule audit using the Unified Parallel Engine
domain: infra
tags:
  - parallel-workflow
  - infra
  - mcp-systems-manager
---

# Parallel Workflow: Firewall Rule Audit

This workflow defines the topological parallel execution steps for firewall rule audit.

## Steps

### Step 1: fan_out_per_host_dump_iptables
Execute the Fan-out per host: dump iptables phase for the firewall_rule_audit workflow under the infra domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: fan_out_per_host_dump_iptables_artifacts
### Step 2: compare_policy [depends_on: fan_out_per_host_dump_iptables]
Execute the compare policy phase for the firewall_rule_audit workflow under the infra domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: compare_policy_artifacts
### Step 3: report [depends_on: compare_policy]
Execute the report phase for the firewall_rule_audit workflow under the infra domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: report_artifacts

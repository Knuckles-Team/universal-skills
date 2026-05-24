---
name: ssl_certificate_sweep
description: Parallel execution workflow for ssl certificate sweep using the Unified Parallel Engine
domain: infra
tags:
  - parallel-workflow
  - infra
  - mcp-tunnel-manager
---

# Parallel Workflow: Ssl Certificate Sweep

This workflow defines the topological parallel execution steps for ssl certificate sweep.

## Steps

### Step 1: fan_out_per_domain_check_expiry
Execute the Fan-out per domain: check expiry phase for the ssl_certificate_sweep workflow under the infra domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: fan_out_per_domain_check_expiry_artifacts
### Step 2: chain_validity
Execute the chain validity phase for the ssl_certificate_sweep workflow under the infra domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: chain_validity_artifacts
### Step 3: renewal_queue [depends_on: fan_out_per_domain_check_expiry, chain_validity]
Execute the renewal queue phase for the ssl_certificate_sweep workflow under the infra domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: renewal_queue_artifacts

---
name: deploy_security_stack
description: Parallel execution workflow for deploy security stack using the Unified Parallel Engine
domain: infra
tags:
  - parallel-workflow
  - infra
  - mcp-systems-manager
---

# Parallel Workflow: Deploy Security Stack

This workflow defines the topological parallel execution steps for deploy security stack.

## Steps

### Step 1: openbao
Execute the openbao phase for the deploy_security_stack workflow under the infra domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: openbao_artifacts
### Step 2: cert_manager [depends_on: openbao]
Execute the cert-manager phase for the deploy_security_stack workflow under the infra domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: cert_manager_artifacts
### Step 3: crowdsec [depends_on: cert_manager]
Execute the crowdsec phase for the deploy_security_stack workflow under the infra domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: crowdsec_artifacts
### Step 4: wazuh [depends_on: crowdsec]
Execute the wazuh phase for the deploy_security_stack workflow under the infra domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: wazuh_artifacts

---
name: deploy_security_stack
description: >-
  Parallel execution workflow for deploy security stack using the Unified Parallel Engine
domain: infra
agent: infrastructure_operator
team_config:
  name: infrastructure_ops_team
  task_pattern: infrastructure deployment and operations
  execution_mode: parallel
  specialist_ids:
    - discovery-agent
    - deployer-agent
    - verifier-agent
    - dns-configurator
  tool_assignments:
    discovery-agent: [tun_tm_system, tun_tm_hosts]
    deployer-agent: [pt_stack, cnt_cm_compose_operations]
    verifier-agent: [pt_docker, cnt_cm_container_operations]
    dns-configurator: [adg_rewrites, td_zones]
tags: [infra, deploy-security-stack]
concept: CONCEPT:INFRA-001
---

# Deploy Security Stack Workflow

**CONCEPT:INFRA-001**

Parallel execution workflow for deploy security stack using the Unified Parallel Engine

## Steps

### Step 1: Openbao
**Agent**: `discovery-agent`
**Tools**: `tun_tm_system, tun_tm_hosts`

Execute openbao operations for the Deploy Security Stack workflow.
Expected: `openbao_artifacts`

### Step 2: Cert Manager [depends_on: openbao]
**Agent**: `deployer-agent`
**Tools**: `pt_stack, cnt_cm_compose_operations`

Execute cert manager operations for the Deploy Security Stack workflow.
Expected: `cert_manager_artifacts`

### Step 3: Crowdsec [depends_on: cert_manager]
**Agent**: `verifier-agent`
**Tools**: `pt_docker, cnt_cm_container_operations`

Execute crowdsec operations for the Deploy Security Stack workflow.
Expected: `crowdsec_artifacts`

### Step 4: Wazuh [depends_on: crowdsec]
**Agent**: `dns-configurator`
**Tools**: `adg_rewrites, td_zones`

Execute wazuh operations for the Deploy Security Stack workflow.
Expected: `wazuh_artifacts`

### Step 5: KG Persistence [depends_on: wazuh]
**Agent**: `dns-configurator`
**Tools**: `graph_write`

Persist workflow results as nodes and edges in the Knowledge Graph.
Create appropriate typed nodes with metadata and link to existing domain entities.

## Output
- Deploy Security Stack results persisted in KG
- Structured report (MD/PDF)
- Audit trail with timestamps and agent attributions

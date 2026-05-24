---
name: deploy_identity_provider
description: Parallel execution workflow for deploy identity provider using the Unified Parallel Engine
domain: infra
tags:
  - parallel-workflow
  - infra
  - mcp-portainer
---

# Parallel Workflow: Deploy Identity Provider

This workflow defines the topological parallel execution steps for deploy identity provider.

## Steps

### Step 1: keycloak_authelia
Execute the keycloak/authelia phase for the deploy_identity_provider workflow under the infra domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: keycloak_authelia_artifacts
### Step 2: oidc_config [depends_on: keycloak_authelia]
Execute the OIDC config phase for the deploy_identity_provider workflow under the infra domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: oidc_config_artifacts
### Step 3: app_integration [depends_on: oidc_config]
Execute the app integration phase for the deploy_identity_provider workflow under the infra domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: app_integration_artifacts

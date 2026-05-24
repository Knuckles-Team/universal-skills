---
name: dns_rewrite_bulk_setup
description: Parallel execution workflow for dns rewrite bulk setup using the Unified Parallel Engine
domain: infra
tags:
  - parallel-workflow
  - infra
  - mcp-adguard-home
---

# Parallel Workflow: Dns Rewrite Bulk Setup

This workflow defines the topological parallel execution steps for dns rewrite bulk setup.

## Steps

### Step 1: parse_service_list
Execute the parse service list phase for the dns_rewrite_bulk_setup workflow under the infra domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: parse_service_list_artifacts
### Step 2: create_rewrites [depends_on: parse_service_list]
Execute the create rewrites phase for the dns_rewrite_bulk_setup workflow under the infra domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: create_rewrites_artifacts
### Step 3: verify_resolution [depends_on: create_rewrites]
Execute the verify resolution phase for the dns_rewrite_bulk_setup workflow under the infra domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: verify_resolution_artifacts

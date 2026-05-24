---
name: dns_query_analytics
description: Parallel execution workflow for dns query analytics using the Unified Parallel Engine
domain: infra
tags:
  - parallel-workflow
  - infra
  - mcp-adguard-home
---

# Parallel Workflow: Dns Query Analytics

This workflow defines the topological parallel execution steps for dns query analytics.

## Steps

### Step 1: sequential_pull_logs
Execute the Sequential: pull logs phase for the dns_query_analytics workflow under the infra domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: sequential_pull_logs_artifacts
### Step 2: parse_patterns [depends_on: sequential_pull_logs]
Execute the parse patterns phase for the dns_query_analytics workflow under the infra domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: parse_patterns_artifacts
### Step 3: top_domains [depends_on: parse_patterns]
Execute the top domains phase for the dns_query_analytics workflow under the infra domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: top_domains_artifacts
### Step 4: block_recommendations [depends_on: top_domains]
Execute the block recommendations phase for the dns_query_analytics workflow under the infra domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: block_recommendations_artifacts

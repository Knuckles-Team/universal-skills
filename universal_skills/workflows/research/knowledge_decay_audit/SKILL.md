---
name: knowledge_decay_audit
description: Parallel execution workflow for knowledge decay audit using the Unified Parallel Engine
domain: research
tags:
  - parallel-workflow
  - research
  - mcp-graph-os
---

# Parallel Workflow: Knowledge Decay Audit

This workflow defines the topological parallel execution steps for knowledge decay audit.

## Steps

### Step 1: fan_out_per_kg_node_check_freshness
Execute the Fan-out per KG node: check freshness phase for the knowledge_decay_audit workflow under the research domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: fan_out_per_kg_node_check_freshness_artifacts
### Step 2: verify_accuracy [depends_on: fan_out_per_kg_node_check_freshness]
Execute the verify accuracy phase for the knowledge_decay_audit workflow under the research domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: verify_accuracy_artifacts
### Step 3: flag_stale [depends_on: verify_accuracy]
Execute the flag stale phase for the knowledge_decay_audit workflow under the research domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: flag_stale_artifacts
### Step 4: prune [depends_on: flag_stale]
Execute the prune phase for the knowledge_decay_audit workflow under the research domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: prune_artifacts

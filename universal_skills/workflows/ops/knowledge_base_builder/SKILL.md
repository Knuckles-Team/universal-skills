---
name: knowledge_base_builder
description: Parallel execution workflow for knowledge base builder using the Unified Parallel Engine
domain: ops
tags:
  - parallel-workflow
  - ops
  - mcp-servicenow
---

# Parallel Workflow: Knowledge Base Builder

This workflow defines the topological parallel execution steps for knowledge base builder.

## Steps

### Step 1: extract_from_resolved_incidents
Execute the extract from resolved incidents phase for the knowledge_base_builder workflow under the ops domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: extract_from_resolved_incidents_artifacts
### Step 2: draft_articles [depends_on: extract_from_resolved_incidents]
Execute the draft articles phase for the knowledge_base_builder workflow under the ops domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: draft_articles_artifacts
### Step 3: publish [depends_on: draft_articles]
Execute the publish phase for the knowledge_base_builder workflow under the ops domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: publish_artifacts

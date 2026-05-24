---
name: conversation_knowledge_extract
description: Parallel execution workflow for conversation knowledge extract using the Unified Parallel Engine
domain: research
tags:
  - parallel-workflow
  - research
  - mcp-graph-os
---

# Parallel Workflow: Conversation Knowledge Extract

This workflow defines the topological parallel execution steps for conversation knowledge extract.

## Steps

### Step 1: fan_out_per_conversation_parse_log
Execute the Fan-out per conversation: parse log phase for the conversation_knowledge_extract workflow under the research domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: fan_out_per_conversation_parse_log_artifacts
### Step 2: extract_decisions [depends_on: fan_out_per_conversation_parse_log]
Execute the extract decisions phase for the conversation_knowledge_extract workflow under the research domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: extract_decisions_artifacts
### Step 3: store_as_ki [depends_on: extract_decisions]
Execute the store as KI phase for the conversation_knowledge_extract workflow under the research domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: store_as_ki_artifacts

---
name: meeting_intelligence
description: Parallel execution workflow for meeting intelligence using the Unified Parallel Engine
domain: ops
tags:
  - parallel-workflow
  - ops
  - mcp-audio-transcriber
---

# Parallel Workflow: Meeting Intelligence

This workflow defines the topological parallel execution steps for meeting intelligence.

## Steps

### Step 1: transcribe
Execute the transcribe phase for the meeting_intelligence workflow under the ops domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: transcribe_artifacts
### Step 2: extract_action_items [depends_on: transcribe]
Execute the extract action items phase for the meeting_intelligence workflow under the ops domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: extract_action_items_artifacts
### Step 3: assign [depends_on: extract_action_items]
Execute the assign phase for the meeting_intelligence workflow under the ops domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: assign_artifacts
### Step 4: follow_up [depends_on: assign]
Execute the follow-up phase for the meeting_intelligence workflow under the ops domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: follow_up_artifacts
### Step 5: summary [depends_on: follow_up]
Execute the summary phase for the meeting_intelligence workflow under the ops domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: summary_artifacts

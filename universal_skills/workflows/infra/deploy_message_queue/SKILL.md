---
name: deploy_message_queue
description: Parallel execution workflow for deploy message queue using the Unified Parallel Engine
domain: infra
tags:
  - parallel-workflow
  - infra
  - mcp-portainer
---

# Parallel Workflow: Deploy Message Queue

This workflow defines the topological parallel execution steps for deploy message queue.

## Steps

### Step 1: rabbitmq_nats
Execute the rabbitmq/nats phase for the deploy_message_queue workflow under the infra domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: rabbitmq_nats_artifacts
### Step 2: consumers [depends_on: rabbitmq_nats]
Execute the consumers phase for the deploy_message_queue workflow under the infra domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: consumers_artifacts
### Step 3: dead_letter [depends_on: consumers]
Execute the dead-letter phase for the deploy_message_queue workflow under the infra domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: dead_letter_artifacts
### Step 4: monitor [depends_on: dead_letter]
Execute the monitor phase for the deploy_message_queue workflow under the infra domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: monitor_artifacts

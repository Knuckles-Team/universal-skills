---
name: newsletter_automation
description: Parallel execution workflow for newsletter automation using the Unified Parallel Engine
domain: research
tags:
  - parallel-workflow
  - research
  - mcp-listmonk
---

# Parallel Workflow: Newsletter Automation

This workflow defines the topological parallel execution steps for newsletter automation.

## Steps

### Step 1: curate_content
Execute the curate content phase for the newsletter_automation workflow under the research domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: curate_content_artifacts
### Step 2: write_digest [depends_on: curate_content]
Execute the write digest phase for the newsletter_automation workflow under the research domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: write_digest_artifacts
### Step 3: design_template [depends_on: write_digest]
Execute the design template phase for the newsletter_automation workflow under the research domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: design_template_artifacts
### Step 4: send [depends_on: design_template]
Execute the send phase for the newsletter_automation workflow under the research domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: send_artifacts
### Step 5: analytics [depends_on: send]
Execute the analytics phase for the newsletter_automation workflow under the research domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: analytics_artifacts

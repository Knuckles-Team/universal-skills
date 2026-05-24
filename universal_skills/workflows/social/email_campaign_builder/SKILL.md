---
name: email_campaign_builder
description: Parallel execution workflow for email campaign builder using the Unified Parallel Engine
domain: research
tags:
  - parallel-workflow
  - research
  - mcp-listmonk
---

# Parallel Workflow: Email Campaign Builder

This workflow defines the topological parallel execution steps for email campaign builder.

## Steps

### Step 1: segment_audience
Execute the segment audience phase for the email_campaign_builder workflow under the research domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: segment_audience_artifacts
### Step 2: write_variants [depends_on: segment_audience]
Execute the write variants phase for the email_campaign_builder workflow under the research domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: write_variants_artifacts
### Step 3: a_b_test [depends_on: write_variants]
Execute the A/B test phase for the email_campaign_builder workflow under the research domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: a_b_test_artifacts
### Step 4: send [depends_on: a_b_test]
Execute the send phase for the email_campaign_builder workflow under the research domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: send_artifacts
### Step 5: analyze [depends_on: send]
Execute the analyze phase for the email_campaign_builder workflow under the research domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: analyze_artifacts

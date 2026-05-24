---
name: customer_feedback_analysis
description: Parallel execution workflow for customer feedback analysis using the Unified Parallel Engine
domain: ops
tags:
  - parallel-workflow
  - ops
  - mcp-servicenow
---

# Parallel Workflow: Customer Feedback Analysis

This workflow defines the topological parallel execution steps for customer feedback analysis.

## Steps

### Step 1: support_tickets
Execute the support tickets phase for the customer_feedback_analysis workflow under the ops domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: support_tickets_artifacts
### Step 2: reviews
Execute the reviews phase for the customer_feedback_analysis workflow under the ops domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: reviews_artifacts
### Step 3: surveys
Execute the surveys phase for the customer_feedback_analysis workflow under the ops domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: surveys_artifacts
### Step 4: sentiment [depends_on: support_tickets, reviews, surveys]
Execute the sentiment phase for the customer_feedback_analysis workflow under the ops domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: sentiment_artifacts
### Step 5: actions [depends_on: sentiment]
Execute the actions phase for the customer_feedback_analysis workflow under the ops domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: actions_artifacts

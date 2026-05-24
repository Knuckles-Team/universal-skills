---
name: m_and_a_due_diligence
description: Parallel execution workflow for m and a due diligence using the Unified Parallel Engine
domain: ops
tags:
  - parallel-workflow
  - ops
  - mcp-multiple
---

# Parallel Workflow: M And A Due Diligence

This workflow defines the topological parallel execution steps for m and a due diligence.

## Steps

### Step 1: financial
Execute the financial phase for the m_and_a_due_diligence workflow under the ops domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: financial_artifacts
### Step 2: legal
Execute the legal phase for the m_and_a_due_diligence workflow under the ops domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: legal_artifacts
### Step 3: technical
Execute the technical phase for the m_and_a_due_diligence workflow under the ops domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: technical_artifacts
### Step 4: operational
Execute the operational phase for the m_and_a_due_diligence workflow under the ops domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: operational_artifacts
### Step 5: cultural
Execute the cultural phase for the m_and_a_due_diligence workflow under the ops domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: cultural_artifacts
### Step 6: synthesis [depends_on: financial, legal, technical, operational, cultural]
Execute the synthesis phase for the m_and_a_due_diligence workflow under the ops domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: synthesis_artifacts

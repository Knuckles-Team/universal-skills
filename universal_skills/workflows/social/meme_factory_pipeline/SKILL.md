---
name: meme_factory_pipeline
description: Parallel execution workflow for meme factory pipeline using the Unified Parallel Engine
domain: research
tags:
  - parallel-workflow
  - research
  - mcp-postiz
---

# Parallel Workflow: Meme Factory Pipeline

This workflow defines the topological parallel execution steps for meme factory pipeline.

## Steps

### Step 1: trend_scan
Execute the trend scan phase for the meme_factory_pipeline workflow under the research domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: trend_scan_artifacts
### Step 2: template_select [depends_on: trend_scan]
Execute the template select phase for the meme_factory_pipeline workflow under the research domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: template_select_artifacts
### Step 3: generate_variants [depends_on: template_select]
Execute the generate variants phase for the meme_factory_pipeline workflow under the research domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: generate_variants_artifacts
### Step 4: a_b_test [depends_on: generate_variants]
Execute the A/B test phase for the meme_factory_pipeline workflow under the research domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: a_b_test_artifacts
### Step 5: post [depends_on: a_b_test]
Execute the post phase for the meme_factory_pipeline workflow under the research domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: post_artifacts

---
name: academic_alpha_scanner
description: Parallel execution workflow for academic alpha scanner using the Unified Parallel Engine
domain: finance
tags:
  - parallel-workflow
  - finance
  - mcp-scholarx
---

# Parallel Workflow: Academic Alpha Scanner

This workflow defines the topological parallel execution steps for academic alpha scanner.

## Steps

### Step 1: arxiv
Execute the arxiv phase for the academic_alpha_scanner workflow under the finance domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: arxiv_artifacts
### Step 2: ssrn
Execute the SSRN phase for the academic_alpha_scanner workflow under the finance domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: ssrn_artifacts
### Step 3: nber
Execute the NBER phase for the academic_alpha_scanner workflow under the finance domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: nber_artifacts
### Step 4: extract_factors [depends_on: arxiv, ssrn, nber]
Execute the extract factors phase for the academic_alpha_scanner workflow under the finance domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: extract_factors_artifacts
### Step 5: replicate [depends_on: extract_factors]
Execute the replicate phase for the academic_alpha_scanner workflow under the finance domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: replicate_artifacts
### Step 6: backtest [depends_on: replicate]
Execute the backtest phase for the academic_alpha_scanner workflow under the finance domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: backtest_artifacts

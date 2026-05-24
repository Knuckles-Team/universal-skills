---
name: conference_proceedings_scan
description: Parallel execution workflow for conference proceedings scan using the Unified Parallel Engine
domain: research
tags:
  - parallel-workflow
  - research
  - mcp-scholarx
---

# Parallel Workflow: Conference Proceedings Scan

This workflow defines the topological parallel execution steps for conference proceedings scan.

## Steps

### Step 1: neurips
Execute the NeurIPS phase for the conference_proceedings_scan workflow under the research domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: neurips_artifacts
### Step 2: icml
Execute the ICML phase for the conference_proceedings_scan workflow under the research domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: icml_artifacts
### Step 3: iclr
Execute the ICLR phase for the conference_proceedings_scan workflow under the research domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: iclr_artifacts
### Step 4: extract_key_papers [depends_on: neurips, icml, iclr]
Execute the extract key papers phase for the conference_proceedings_scan workflow under the research domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: extract_key_papers_artifacts
### Step 5: brief [depends_on: extract_key_papers]
Execute the brief phase for the conference_proceedings_scan workflow under the research domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: brief_artifacts

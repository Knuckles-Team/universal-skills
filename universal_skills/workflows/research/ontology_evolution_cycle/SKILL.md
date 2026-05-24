---
name: ontology_evolution_cycle
description: Parallel execution workflow for ontology evolution cycle using the Unified Parallel Engine
domain: research
tags:
  - parallel-workflow
  - research
  - mcp-graph-os
---

# Parallel Workflow: Ontology Evolution Cycle

This workflow defines the topological parallel execution steps for ontology evolution cycle.

## Steps

### Step 1: audit_current_ontology
Execute the audit current ontology phase for the ontology_evolution_cycle workflow under the research domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: audit_current_ontology_artifacts
### Step 2: find_gaps [depends_on: audit_current_ontology]
Execute the find gaps phase for the ontology_evolution_cycle workflow under the research domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: find_gaps_artifacts
### Step 3: propose_extensions [depends_on: find_gaps]
Execute the propose extensions phase for the ontology_evolution_cycle workflow under the research domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: propose_extensions_artifacts
### Step 4: validate [depends_on: propose_extensions]
Execute the validate phase for the ontology_evolution_cycle workflow under the research domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: validate_artifacts
### Step 5: apply [depends_on: validate]
Execute the apply phase for the ontology_evolution_cycle workflow under the research domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: apply_artifacts

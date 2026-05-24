---
name: agent_utilities_evolution
description: Execute structural codebase-wide evolution of agent-utilities and downstream dependencies
tags:
  - dev-workflows
  - evolution
  - codebase-maintenance
requires:
  - graph-os
  - data-science-mcp
  - repository-manager-mcp
---

# Agent Utilities Evolution Workflow

Systematically analyze, plan, and execute architectural improvements and evolutionary upgrades across agent-utilities and all its 30+ downstream dependent packages.

## Steps

### Step 0: user-interaction
Retrieve the target evolution scope (e.g., AST Concept ID audits, dead code elimination, dependency synchronization) and current focus repositories.

### Step 1: graph-os
Query the unified Knowledge Graph to locate concept mapping registers, active nodes, or unresolved architectural gaps across the ecosystem using Cypher queries via `mcp_graph-os_graph_query`.

### Step 2: data-science-mcp
Conduct code audits, comparative gap analysis, and AST wiring audits between core `agent-utilities` abstractions and downstream projects using `graph_analyze`.

### Step 3: repository-manager-mcp
Generate an implementation draft (Software Design Document / SDD) detailing the precise edits required for matching packages and version bounds.

### Step 4: user-interaction
Present the proposed SDD evolutionary spec to the user for approval and collect any custom overrides.

### Step 5: repository-manager-mcp
Execute bulk project code edits and run automated validation tests across the workspaces using the `rm_projects` tool with `action='validate'` until all drift errors are resolved.

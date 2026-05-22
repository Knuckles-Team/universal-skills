---
name: workspace_inventory
description: Full workspace discovery — list available workspace actions, repositories, and validate project structure.
domain: development
tags: ['workspace', 'git', 'validation', 'repositories']
requires: ['repository-manager-mcp']
---

# workspace_inventory Workflow

Full workspace discovery — list available workspace actions, repositories, and validate project structure.

### Step 0: repository-manager-mcp
Use the rm_workspace tool to list the available actions for the workspace
Expected: list, setup

### Step 1: repository-manager-mcp
List all managed repositories in the workspace with their status
Expected: repository
Depends On: Step 0

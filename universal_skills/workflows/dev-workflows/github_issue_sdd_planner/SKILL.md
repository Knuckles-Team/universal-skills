---
name: github_issue_sdd_planner
description: Retrieves reported issues for a repository from GitHub, validates their correctness, investigates their root cause, and generates high-fidelity Spec-Driven Development (SDD) specifications and implementation plans within the project's .specify/ workspace directory.
domain: dev-workflows
tags: ['github', 'sdd', 'planning', 'spec-generator', 'github-agent']
requires: ['github-agent', 'spec-generator', 'task-planner']
---

# github_issue_sdd_planner Workflow

Retrieves reported issues for a repository from GitHub, validates their correctness, investigates their root cause, and generates high-fidelity Spec-Driven Development (SDD) specifications and implementation plans within the project's .specify/ workspace directory.

### Step 0: github-agent
Retrieve open issues for the target repository using the github_issues tool with target filters. Target/Repo: {{task}}
Expected: issues, metadata

### Step 1: spec-verifier
Validate and verify if the reported issues are valid. Investigate the root cause of valid issues by reading relevant source files and checking workspace logs.
Expected: validation_report, root_cause_analysis
Depends On: Step 0

### Step 2: spec-generator
Create high-fidelity Spec-Driven Development (SDD) spec.md files for the validated issues under the repository's .specify/ directory using standard spec templates.
Expected: spec_markdown, specify_sync
Depends On: Step 1

### Step 3: task-planner
Generate a comprehensive execution plan and a structured tasks checklist (tasks.md) mapping out dependencies, file changes, and testing tasks to implement the specs.
Expected: implementation_plan, tasks_md
Depends On: Step 2

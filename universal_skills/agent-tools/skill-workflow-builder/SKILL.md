---
name: skill-workflow-builder
domain: agent-tools
skill_type: skill
description: >-
  Tool and instructions to interactively brainstorm, structure, verify, and scaffold structured workflow-based skills.
  Use when the user or agent needs to create a new workflow skill under `universal_skills/workflows/`, define topological step lists,
  or analyze dependencies of a complex agent process. Do NOT use for standard non-workflow skills or simple file updates.
license: MIT
tags: [workflow, builder, dev-workflows, scaffolding, dag, topological]
metadata:
  version: '1.2.1'
  author: Genius
---
# Skill Workflow Builder

This skill provides an interactive utility script and guidelines for creating structured, multi-step workflow skills.

## About Workflows

Workflow skills are structured step-by-step procedural prompt instructions that guide agents through complex, multi-tool operations. Workflows reside in:
`universal_skills/workflows/{domain}/{workflow_name}/`

### Step Schema

Each step in a workflow skill must follow a strict topological definition:

```markdown
### Step N: <component-name>[depends_on: Step A, Step B]
<Detailed instruction detailing the tool action or phase>
Expected: <expected outcomes or variable names>
```

Where:
- **`Step N`**: Unique 0-indexed integer (e.g. `Step 0`, `Step 1`).
- **`<component-name>`**: The MCP tool or agent capability utilized (e.g., `portainer-mcp`, `github-tools`, `systems-manager`, `user-interaction`).
- **`depends_on`** (Optional): A list of steps that must complete before this step is executed.

---

## Interactive Workflow Builder Process

When building a new workflow skill, follow these sequential phases interactively with the user:

### Phase 1: Review & Discover
1. Index existing workflows to find similar structures using the CLI tool:
   ```bash
   python universal_skills/agent-tools/skill-workflow-builder/scripts/build_workflow.py list
   ```
2. Verify available MCP tools and databases using `query-kg` or inspecting configurations.

### Phase 2: Topological Brainstorming
1. Design the step-by-step procedure interactively with the user.
2. Ask:
   - What is the domain/category (e.g., `infra`, `dev-workflows`, `ops`, `finance`, `health`, `social`, `system`, `research`)?
   - What components/tools are needed for each step?
   - What are the dependencies?
3. Draw a Mermaid diagram of the workflow DAG for the user to visually inspect and approve the flow.

### Phase 3: Scaffolding
1. Run the scaffolding script in interactive mode to register the steps, tags, and description:
   ```bash
   python universal_skills/agent-tools/skill-workflow-builder/scripts/build_workflow.py scaffold <workflow_name> --domain <domain> --description "<description>" --interactive
   ```
2. The script will automatically:
   - Check the steps topological structure for circular dependencies.
   - Create the directory at `universal_skills/workflows/{domain}/{workflow_name}/`.
   - Write a compliant `SKILL.md` file.
   - Generate a default swarm orchestration `references/team.yaml`.

### Phase 4: Validation
1. Verify the workflow skill compiles perfectly using:
   ```bash
   python universal_skills/agent-tools/skill-workflow-builder/scripts/build_workflow.py validate universal_skills/workflows/{domain}/{workflow_name}/SKILL.md
   ```
2. Save the final files in the user's source repository!

---

## Topological Reference

Workflows are executed by a Parallel Orchestration Engine that parses the steps into a Directed Acyclic Graph (DAG). It is critical that:
- Step numbers do not duplicate.
- Dependencies reference actual prior steps.
- No cycles exist (e.g. Step A depends on Step B, which depends on Step A). The validator script will automatically catch these issues.

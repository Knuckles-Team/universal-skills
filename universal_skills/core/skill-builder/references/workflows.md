# Atomic Skill or Skill Workflow?

Use this boundary check before adding ordered instructions to an atomic skill.

## Keep one atomic skill when

- one user intent selects the entire capability;
- its internal checks cannot provide useful results independently; and
- the skill does not delegate stages to other skills or specialist agents.

An atomic skill may contain a short procedure for its own capability. Do not encode
that procedure as a cross-capability DAG, `### Step N:` headings, or `depends_on`.

## Build a skill workflow when

- two or more stages are independently triggerable atomic skills;
- stages need ordering, fan-out, fan-in, or different specialists; or
- a stage invokes one explicit MCP tool as a workflow node.

Create or repair the required atoms first. Then use `skill-workflow-builder` to
place the composition in `universal_skills/<domain>-workflows/<workflow-name>/`.
Keep business logic in the atomic skills; the workflow should contain only bindings
and dependencies.

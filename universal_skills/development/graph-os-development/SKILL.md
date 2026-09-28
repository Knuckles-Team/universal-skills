---
name: graph-os-development
domain: development
skill_type: skill
description: >-
  Develop in any Graph OS ecosystem repository from public GitHub sources.
  Route ownership, bootstrap source checkouts, and verify repository-owned
  specs across the Graph OS core, public frontends, pipelines, finance and
  infrastructure agents, and the organization hub.
license: MIT
tags: [graph-os, development, public-contribution]
metadata:
  version: '1.3.1'
---

# Graph OS ecosystem development

For a contributor or coding agent starting with no ecosystem context, open
the public [organization hub](https://github.com/Knuckles-Team/.github), its
[build-first queue](https://knuckles-team.github.io/.github/build-first.html),
and [contribution guide](https://github.com/Knuckles-Team/.github/blob/main/CONTRIBUTING.md).
The queue links owner-native specs in epistemic-graph, connector SDK,
agent-utilities, graph-os, WebUI, repository-manager, pipelines,
agent-terminal-ui, emerald-exchange, tunnel-manager, and the hub itself.

The canonical, complete instructions are packaged by
[`graph-os`](https://github.com/Knuckles-Team/graph-os/blob/main/graph_os/skills/graph-os-development/SKILL.md).
Read that `SKILL.md` and its
[`bootstrap.md`](https://github.com/Knuckles-Team/graph-os/blob/main/graph_os/skills/graph-os-development/references/bootstrap.md)
from the current public checkout before changing any ecosystem repository.
The Graph OS package registers the skill through its
`agent_utilities.skill_providers` entry point; this catalog entry lets a
contributor discover it before installing Graph OS.

Use `spec-generator`, `task-planner`, `sdd-implementer`, `spec-verifier`, and
`sdd-full-lifecycle` from this public skill kit for the specification and
implementation sequence. The owner repository's spec remains the authority.

Use only the repository-owned `specs/<id>/` and public code/contracts as the
implementation authority. The spec must be self-contained for contributors
without private drafts, inventory, credentials, or a live deployment.

---
name: graph-os-development
domain: development
skill_type: skill
description: >-
  Develop in any Graph OS ecosystem repository from public GitHub sources.
  Route ownership, bootstrap source checkouts, and verify repository-owned
  specs across epistemic-graph, connector SDK, agent-utilities, graph-os,
  WebUI, and repository-manager.
license: MIT
tags: [graph-os, development, public-contribution]
metadata:
  version: '1.3.1'
---

# Graph OS ecosystem development

The canonical, complete instructions are packaged by
[`graph-os`](https://github.com/Knuckles-Team/graph-os/blob/main/graph_os/skills/graph-os-development/SKILL.md).
Read that `SKILL.md` and its
[`bootstrap.md`](https://github.com/Knuckles-Team/graph-os/blob/main/graph_os/skills/graph-os-development/references/bootstrap.md)
from the current public checkout before changing any ecosystem repository.
The Graph OS package registers the skill through its
`agent_utilities.skill_providers` entry point; this catalog entry lets a
contributor discover it before installing Graph OS.

Use only the repository-owned `specs/<id>/` and public code/contracts as the
implementation authority. The spec must be self-contained for contributors
without private drafts, inventory, credentials, or a live deployment.

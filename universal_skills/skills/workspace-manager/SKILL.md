---
name: workspace-manager
domain: development
skill_type: skill
description: Bootstraps the exact .specify/ folder layout for 1:1 spec-kit compatibility
license: MIT
tags: [sdd, bootstrap]
metadata:
  version: '1.6.2'
  author: Knuckles-Team
---

You are the Workspace Manager agent.

On first run (or when no .specify/ folder exists):
1. Create the full directory tree:
   - `.specify/memory/`
   - `.specify/specs/`
   - `.specify/templates/`
2. Write a skeleton `constitution.md` to `.specify/memory/` if missing.
3. (Optional) Copy any templates you want from your `skills/sdd/templates/` folder to `.specify/templates/`.

Output a confirmation summary with the created paths.

## Steps

1. Check whether a spec-kit folder already exists with `ls -d .specify`. Verify that the command reports the folder or "No such file", which decides whether to bootstrap.
2. Create the directory tree with `mkdir -p .specify/memory .specify/specs .specify/templates`. Verify that `ls .specify` lists `memory`, `specs` and `templates`.
3. Write a skeleton constitution if missing with `test -f .specify/memory/constitution.md || printf '# Constitution\n' > .specify/memory/constitution.md`. Verify that `ls .specify/memory/constitution.md` lists the file.
4. Optionally copy templates with `cp -n skills/sdd/templates/* .specify/templates/`. Verify that `ls .specify/templates` lists the copied files.
5. Report the created paths. Verify that `find .specify -maxdepth 2` matches the summary you output.

## Failure recovery

| Failure | Cause | Recovery |
|---------|-------|----------|
| `Permission denied` on `mkdir` | The working directory is read-only or owned by another user | Change to the repository root you own with `cd <repo-root>` and rerun `mkdir -p .specify/memory .specify/specs .specify/templates`. |
| `cp: cannot stat 'skills/sdd/templates/*'` | The templates folder is not at that path | Locate it with `find . -type d -name templates -path '*sdd*'`, copy from there, or skip this optional step. |
| Existing constitution got overwritten | Written without checking for the file | Restore it from version control with `git checkout -- .specify/memory/constitution.md` and keep the `test -f` guard. |

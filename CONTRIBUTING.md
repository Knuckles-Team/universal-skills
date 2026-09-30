# Contributing with universal skills and Spec Kit

Contributions to the Graph OS ecosystem start from tracked, reviewable specifications. Each repository keeps its own `specs/<stable-id>/` directory for the features it owns. Cross-repository work links related spec IDs and contract paths in every affected repository. A public spec must contain all requirements and decisions needed to build and test it without private drafts or inventory. A spec is an implementation contract, not proof that the deliverable has landed.

## Set up this repository

```bash
scripts/bootstrap.sh
uvx pre-commit run --all-files
```

`scripts/bootstrap.sh` is idempotent: it installs uv 0.9 or newer, the Python in
`.python-version`, syncs `.venv` from `uv.lock` with every extra (the tests
exercise all skills' scripts), and installs the pre-commit and pre-push hooks.
Claude Code cloud sessions run it through `.claude/hooks/session-start.sh`. CI
runs the same script and the same `.pre-commit-config.yaml`. A gate whose tool
or environment is missing prints `SKIPPED (<gate>): <reason>` locally and fails
with `CANNOT RUN` in CI.

Branch from `main`, keep each commit to one logical change, push with
`git push -u origin <branch>`, and open the pull request against `main`.

## Set up the shared workflow

1. Read the target repository's `AGENTS.md`, `.specify/memory/constitution.md`, and relevant `specs/` directories. Follow its worktree and contribution rules.
2. Install [GitHub Spec Kit v1.0.12](https://github.com/github/spec-kit/releases/tag/v1.0.12) with `uv tool install specify-cli --from git+https://github.com/github/spec-kit.git@v1.0.12`, confirm with `specify version`, and initialize the coding-agent integration for the target repository if it is not already configured. Preserve project-owned files when refreshing Spec Kit. `.specify/` holds configuration, templates, scripts, and the constitution; feature artifacts live at repository-root `specs/`.
3. Install this `universal-skills` package as documented in [README.md](README.md), then make its skills available to your coding agent with the `universal-installer` skill. The reusable skills are [`graph-os-development`](universal_skills/development/graph-os-development/SKILL.md), [`spec-generator`](universal_skills/development/spec-generator/SKILL.md), [`task-planner`](universal_skills/development/task-planner/SKILL.md), [`spec-verifier`](universal_skills/development/spec-verifier/SKILL.md), and the [`sdd-full-lifecycle`](universal_skills/development-workflows/sdd-full-lifecycle/SKILL.md) workflow. The canonical Graph OS development skill is also packaged by [graph-os](https://github.com/Knuckles-Team/graph-os/tree/main/graph_os/skills/graph-os-development) through a provider entry point.

## Contribute a feature

Use the installed Spec Kit agent commands in order: `constitution` only when governance needs amendment, then `specify`, `clarify` where needed, `plan`, `tasks`, `analyze`, and `implement`. The spelling varies by integration: `/speckit.specify` in command mode, `/speckit-specify` in skills mode, and `$speckit-specify` in Codex skills mode. These are agent invocations, not terminal `specify` subcommands. The universal skills can create or review the same artifacts; do not run both generators over the same file without reviewing the diff. Keep the Spec Kit template structure and put project-specific detail into the matching sections and design artifacts.

A reviewable feature has `spec.md`, `plan.md`, `test-spec.md`, and `tasks.md`; add `research.md`, `data-model.md`, `contracts/`, `quickstart.md`, and `checklists/` when applicable. The design names architecture, interfaces, existing components to reuse, runtime wiring, cross-repository contracts, migration and failure behavior, and test scenarios. Link related public repository specs by stable ID and include the complete cross-repository contract locally. Tasks trace requirements to tests and include the repository's configured CCCC, `jscpd`, Dupehound, and KISS checks. If a gate is not configured, document the gap instead of claiming it passed.

Attach test and implementation evidence to the PR. A deliverable is accepted only after the merged implementation and its acceptance evidence are verified. If graph-os is available, sync the tracked spec files into the KG after edits; Git files remain the source of truth. Review generated files and links before opening a PR, and follow the target repository's CI and quality gates.

Required cloud PR checks must run with deterministic fixtures or provision their own disposable dependencies. A missing private service, live deployment, or credential must not block a PR through an unrelated check. Put credentialed and live-environment checks in a separately reported scheduled or post-merge lane, with its owner and result visible. Keep hermetic correctness, security, and code-quality checks required; their failures still need fixes before merge.

## Keep the integration current

### Pages sources and offline checks

MkDocs renders the contribution guide from this file and the public
US-PAGES-001 package from `specs/US-PAGES-001/` using its native
`scripts/pages_sources.py` hook. Generated pages exist only in the build;
edit the tracked source, never a second copy under `docs/`.
Repository-relative guide links resolve to public GitHub sources. Spec package
Markdown links resolve to their rendered pages. The hook validates local source
targets; a strict MkDocs build validates local page links and anchors.

| Pages URL (relative to the existing site root) | Canonical source |
| --- | --- |
| `/` | `docs/index.md` |
| `/overview/` (catalog and architecture) | `docs/overview.md` |
| `/contributing/` | `CONTRIBUTING.md` |
| `/skill-catalog-audit/` | `docs/skill-catalog-audit.md` |
| `/skill-catalog-improvement-roadmap/` | `docs/skill-catalog-improvement-roadmap.md` |
| `/specs/US-PAGES-001/spec/` | `specs/US-PAGES-001/spec.md` plus `status.json` |
| `/specs/US-PAGES-001/{plan,test-spec,tasks}/` | Corresponding tracked package Markdown |

The dedicated **Pages check** workflow runs on every PR using only this checkout
and disposable documentation dependencies. Its separately collected
`tests/pages_contracts.py` suite requires MkDocs; the existing package tests and
pre-commit gates retain their own locked environment. To reproduce this lane:

```bash
python -m pip install -r .github/requirements-pages.txt
python -m mkdocs build --strict
python -m pytest tests/pages_contracts.py -q
```

`status.json` keeps delivery and acceptance separate. A status of `ACCEPTED`
requires `IMPLEMENTED` and two matching exact-commit receipts: an evidence entry
with `kind: merged_implementation`, `commit: <40-character SHA>`, and the owning
repository's public commit URL; and `kind: passing_acceptance` with the same
commit and a public Actions run URL. Missing, malformed, or mismatched receipts
fail the build. Offline validation checks receipt structure; a maintainer must
audit merge ancestry and passing results before recording acceptance. The real
US-PAGES-001 status remains `SPECIFIED` / `NOT_AUDITED` until that audit.

This slice publishes only the explicit public US-PAGES-001 package. Additional
specs need an explicit source/navigation decision. It does not verify live
GitHub URLs or deployed Pages routes. Post-merge deployment smoke results,
organization-template adoption, and the full spec acceptance audit remain open.

Spec Kit reads `.specify/memory/constitution.md` at runtime for `plan`, `tasks`, and `analyze`; governance edits do not require copying policy into generated core templates. To refresh an existing project after upgrading the CLI, inspect `specify integration status`, run `specify integration upgrade <key>` for its installed coding-agent integration, then `specify extension update` for installed extensions. Review the resulting diff and any local-change warning before accepting a forced refresh. Preserve the tracked `specs/` tree and project-owned constitution.

Use a Spec Kit **preset** for reusable organization-wide artifact rules such as requirement traceability, architecture/test coverage, and CCCC/`jscpd`/Dupehound/KISS gates; use `.specify/templates/overrides/` only for a one-repository customization. This repository currently supplies these rules as universal-skills instructions and this contribution guide. It does **not** ship an installable Spec Kit preset yet, so installing the skills alone does not alter Spec Kit's resolved templates. A future preset can encode those same rules once its cross-repository behavior is validated. Avoid editing generated core templates directly.

# US-BUSINESS-ROLES — Implementation plan

Governing spec: [spec.md](spec.md). Rows: [requirements.md](requirements.md).

## Summary

Each workflow skill is a numbered procedure in `SKILL.md`. It reads the profile, calls composed atomic skills, stops at its gate and writes one run record. Skills hold no connector code. The live caller is the role agent that loads the skill from the catalog and runs its steps through arbora.

## Technical Context

- **Language/Version**: Markdown skill content; Python 3.14 standard, 3.12 floor for tests
- **Target Platform**: Linux, macOS and Windows developer machines; served by arbora
- **Performance Goals**: N/A
- **Scale/Scope**: 11 skills, 15 rows
- **Primary Dependencies**: The skill catalog loader and `arbora.client` for the served profile read and approval calls
- **Storage**: N/A
- **Testing**: pytest with the tests named in the rows
- **Project Type**: skill library
- **Constraints**: No business name, rate or jurisdiction in a skill; at most 150 lines per `SKILL.md`; no connector client import

## Constitution Check

- R-I A skill is atomic and portable: pass. Each skill does one duty and composes atoms.
- R-II Paths are legal on every platform: pass.
- XXI Public files stay portable: pass. The spec names no host, domain or business.

## Project Structure

```text
universal_skills/skills/order-to-cash/SKILL.md              new
universal_skills/skills/month-end-close/SKILL.md            new
universal_skills/skills/sales-tax-preparation/SKILL.md      new
universal_skills/skills/compliance-calendar/SKILL.md        new
universal_skills/skills/customer-care-triage/SKILL.md       new
universal_skills/skills/procurement-reorder/SKILL.md        new
universal_skills/skills/production-batch-record/SKILL.md    new
universal_skills/skills/website-release/SKILL.md            new
universal_skills/skills/host-upkeep/SKILL.md                new
universal_skills/skills/security-sentinel/SKILL.md          new
universal_skills/skills/owner-weekly-digest/SKILL.md        new
tests/test_business_role_skills.py                          new
tests/test_business_role_skills_served.py                   new
```

## Phase 0: Research

No unknowns; no research.md. Reuse inventory: atomic skills compose as follows: ERP accounting and inventory, ledger, transactional mail, merge-request and pipeline, container operations, remote execution, monitoring, alerting, dashboards, vulnerability review, access management, document management and the legal compliance trackers. The existing `ssl-certificate-sweep`, `security-tools` and `legal-compliance` skills stay and `host-upkeep` and `security-sentinel` call them. No new atom is specified.

## Phase 1: Design

- **Owner:** universal-skills owns the skill text and its tests. Arbora owns the approval check and the profile read. Connector repositories own the atomic skills.
- **Cohesion:** Each duty is one skill folder under `universal_skills/skills/`. Shared checks live in one test module.
- **Dependency direction:** A workflow skill depends on atomic skills and on `arbora.client`. No atomic skill depends on a workflow skill.
- **Interface depth:** None. A skill is one `SKILL.md` with five fixed sections.
- **Special cases:** A business difference is a profile field. No skill branches on a business name.
- **State:** None. The run record is written to the knowledge graph through arbora; the skill keeps no file state.
- **Environment:** No skill names a host, private domain or local path. Hosts come from the profile and the host inventory.

### Architecture

Call path: role agent loads the skill, then the profile read, then composed atomic skills through arbora, then the approval request at the gate, then the run record. The skill holds no policy table. Arbora owns the approval check.

### Interfaces and data model

Each `SKILL.md` holds these sections in order: `Profile inputs`, `Composes`, `Steps`, `Gate`, `Run record`. The run record has three fields: `done`, `exceptions`, `next_gate`.

### Live integration path

The catalog loader serves each skill by name. `tests/test_business_role_skills_served.py` drives `order-to-cash` against a fixture arbora server, as R014 states.

### Risks, alternatives, and decisions

A shared workflow is better than a skill per business, because the profile carries every difference. A skill that needs a business-specific rule must ask the profile, not embed the rule.

## Phase 2: Task approach

Write the shared structure test first (R001.1 to R001.4). Then add skills by dependency: `order-to-cash`, `month-end-close`, `sales-tax-preparation`, then the rest. The served proof comes last.

## Complexity Tracking

None.

## Build contract

Gate thresholds follow the organization constitution table: 20 words per sentence (`ste`), the KISS limits of `.config/kiss.toml`, and the pre-land fast set. No scanner gaming and no duplicate implementation.

## Production caller chain

Entry point: the role agent resolves a skill name in the catalog and follows its `SKILL.md`. The profile read and approval call go through `arbora.client` `invoke`. The target call sites are set when the skills land.

## Cross-repo seams

- `ARBORA-IDENTITY-R019` (arbora): the approval grant that each gate waits for. Contract: `contracts/approval-gate.md`.
- Business profile read (medulla vocabulary, arbora operation; rows to file there): the profile each skill reads, US-BUSINESS-ROLES-R001.1. Contract: `contracts/business-profile.md`.

Connector tools, read-only flags and gate-aware tool metadata stay with their owners and need no contract here.

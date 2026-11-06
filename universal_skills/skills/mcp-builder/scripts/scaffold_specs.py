"""Spec files of a scaffolded connector, in the vended spec-kit template shape.

Every file follows the pipelines `.specify/templates/` headings so the strict
`spec` gate passes on the first push. A row is
`(suffix, title, behavior, caller chain, shape, test)`.
"""

from __future__ import annotations

Row = tuple[str, str, str, str, str, str]


def _rows(sid: str, rows: tuple[Row, ...]) -> list[tuple[str, str, str, str, str, str]]:
    return [(f"{sid}-{r}", t, b, c, s, v) for r, t, b, c, s, v in rows]


def render(n: dict[str, str], rows: tuple[Row, ...], outcome: str, design: str) -> dict[str, str]:
    """Return spec.md, plan.md, requirements.md, tasks.md and test-spec.md."""
    sid, fleet, display, pkg = n["spec_id"], n["fleet"], n["Display"], n["pkg"]
    full = _rows(sid, rows)
    first = full[0][0]
    stories = "\n".join(
        f"### User Story {k} - {t} (Priority: P{min(k, 3)})\n\n"
        f"{b}\n\n**Why this priority**: the connector is not usable without it.\n\n"
        f"**Independent Test**: `{v}`.\n\n"
        f"**Acceptance Scenarios**:\n\n"
        f"1. **Given** the connector is installed, **When** a client uses it, **Then** {t.lower()} holds as `{rid}` states.\n"
        for k, (rid, t, b, _, _, v) in enumerate(full, 1)
    )
    labels = "\n".join(
        f"| FR-{k:03d} | `{rid}` | plan.md#phase-1-design | T-{k:03d} |  |"
        for k, (rid, *_rest) in enumerate(full, 1)
    )
    spec = f"""# {sid} — {display} connector

Owner: {fleet}.

## Delivery mapping

Rows live in [requirements.md](requirements.md). Design: [plan.md](plan.md). Tests: [test-spec.md](test-spec.md).

## User Scenarios & Testing

{stories}
### Edge Cases

- An unset setting or credential returns a typed refusal and sends nothing to the provider.

## Requirements

{outcome}

## Success Criteria

- Every row in requirements.md has a passing bound test.

## Assumptions

- The SDK serves the connector; this repository owns only the {display} calls, mappings and tools.

## Why a new spec

No spec in this repository owns the {display} operations.

## Scope and interfaces

In scope: the operations, prompts, skills and ontology of {display}. Out of scope: server start, SDK
behavior, version files, container files and gates; the SDK and pipelines own them.

## Traceability

| Label | Rows | Design section | Test ID | Evidence |
|---|---|---|---|---|
{labels}
"""
    plan = f"""# {sid} — Implementation plan

Governing spec: [spec.md](spec.md). Rows: [requirements.md](requirements.md).

## Summary

{outcome}

## Technical Context

Python 3.14 (floor 3.12), one dependency: `scion-sdk[mcp]`. Tests: pytest, run by the shared `tests-fast` hook.

## Constitution Check

One external system, one tool per operation, the SDK as the only dependency: see `.specify/memory/constitution.md`.

## Project Structure

`{pkg}/` holds the connector; `tests/` holds the bound tests; `specs/{fleet}/` holds this spec.

## Phase 0: Research

The SDK and the shared pipelines own the server, transports, gates and release. Nothing is reimplemented here.

## Phase 1: Design

{design}

## Phase 2: Task approach

One task per row in [tasks.md](tasks.md); each lands with its bound test.

## Complexity Tracking

No deviation from the constitution.

## Build contract

`uv sync`, then `uvx pre-commit run --all-files`. The release workflow builds and publishes on a version tag.

## Production caller chain

`{fleet}` console script → `scion_sdk.cli:serve` → entry point `{fleet} = "{pkg}:connector"` → served tools.

## Cross-repo seams

The SDK (connector contracts, transports, confirmation) and arbora (fleet admission). Linked by row ID only.
"""
    req = [
        f"# {sid} — Requirements\n",
        "Governing spec: [spec.md](spec.md).\n",
        "| ID | Requirement | Acceptance |",
        "|---|---|---|",
    ]
    req += [
        f"| `{rid}` | **{t}.** {b} Caller chain: {c}. Shape: {s}. | `{v}` |"
        for rid, t, b, c, s, v in full
    ]
    tasks = [
        f"# {sid} — Implementation tasks\n",
        "Governing spec: [spec.md](spec.md). Design: [plan.md](plan.md). Rows: [requirements.md](requirements.md).\n",
    ]
    tasks += [f"- [ ] T{k:03d} [US{k}] {rid} {t}." for k, (rid, t, *_r) in enumerate(full, 1)]
    test = [
        f"# {sid} — Test specification\n",
        "Governing spec: [spec.md](spec.md).\n",
        "| Test ID | Requirement | Level | Setup and input | Expected observation | Evidence |",
        "|---|---|---|---|---|---|",
    ]
    test += [
        f"| T-{k:03d} | FR-{k:03d} | Contract | `{v}` | {t} holds. |  |"
        for k, (_rid, t, _b, _c, _s, v) in enumerate(full, 1)
    ]
    test += [
        "\n## Negative and boundary cases\n",
        f"Refusals and denials are proved by the bound tests of `{first}` and its siblings.\n",
        "## Quality and release proof\n",
        "The shared `tests-fast`, `spec` and `connector-standard` hooks pass on the pull request.",
    ]
    return {
        "spec.md": spec,
        "plan.md": plan,
        "requirements.md": "\n".join(req) + "\n",
        "tasks.md": "\n".join(tasks) + "\n",
        "test-spec.md": "\n".join(test) + "\n",
    }

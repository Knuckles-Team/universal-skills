"""Render one connector capability spec with unclaimed delivery evidence."""

from __future__ import annotations

from collections.abc import Mapping
import json


STANDARD = (
    "https://github.com/Knuckles-Team/pipelines/blob/"
    "7b3d18d72b5622d455ece3bbe45a9482bc6e8b5e/reference/spec-standard.md"
)
SDK_README = (
    "https://github.com/Knuckles-Team/agent-connector-sdk/blob/"
    "5babc4cc48ad73928468b243842f219f51e2cca1/README.md"
)


def _requirements(
    spec_id: str, package: str, mcp_test: str
) -> list[tuple[str, str, str, str]]:
    return [
        (
            f"{spec_id}-R001",
            "Credential references",
            f"The connector must resolve authorized credential references in `{package}/auth.py` when a client is requested.",
            "`tests/test_auth.py::test_client_resolves_reference_and_cleans_up` must observe reference resolution and resource cleanup.",
        ),
        (
            f"{spec_id}-R002",
            "Bounded API requests",
            f"The connector must enforce origin, TLS, timeout, and response-size limits in `{package}/api/api_client_base.py`.",
            "`tests/test_api_wrapper.py` must exercise rejected origins, redirects, deadlines, and oversized responses through the real client.",
        ),
        (
            f"{spec_id}-R003",
            "MCP registration",
            f"The connector must register its operation router through `{package}/mcp_server.py` and `{package}/mcp/mcp_system.py`.",
            f"`{mcp_test}::test_mcp_instance_registration` must construct the production server without vendor requests.",
        ),
        (
            f"{spec_id}-R004",
            "Native content contracts",
            f"The connector must publish packaged prompts, skills, ontology, and its manifest through `{package}/mcp_server.py`.",
            "`scripts/generate_tool_schemas.py --check` must validate live tool contracts. Native content listing verification remains required before delivery.",
        ),
        (
            f"{spec_id}-R005",
            "Typed source observations",
            f"The connector must submit authorized source observations through the shared ingest service in `{package}/kg_ingest.py`.",
            "`tests/test_kg_ingest.py::test_ingest_maps_record_and_uses_submit` must observe typed changes at the submission boundary.",
        ),
    ]


def render_spec_files(ctx: Mapping[str, str]) -> dict[str, str]:
    """Return relative paths and text; lifecycle gates own later status updates.

    Required context: package_name, pkg_dir, short_name, display_name, concept_prefix.
    An explicit spec_id may override the canonical CONN-<REPOSITORY> default.
    """
    name, package = ctx["package_name"], ctx["pkg_dir"]
    display, concept = ctx["display_name"], ctx["concept_prefix"]
    spec_id = ctx.get("spec_id") or f"CONN-{name.upper()}"
    directory = f"specs/{name}"
    mcp_test = f"tests/test_{ctx['short_name'].replace('-', '_')}_mcp_validation.py"
    rows = _requirements(spec_id, package, mcp_test)
    requirement_ids = [row[0] for row in rows]
    status = {
        "schema_version": 2,
        "spec_id": spec_id,
        "owner_repo": name,
        "delivery_state": "SPECIFIED",
        "requirement_ids": requirement_ids,
        "requirements": [
            {
                "id": identifier,
                "title": title,
                "delivery_state": "SPECIFIED",
                "landed_in": [],
                "verified_by": [],
            }
            for identifier, title, _, _ in rows
        ],
    }
    requirements = "\n".join(
        f"| `{identifier}` | **{title}.** {requirement} | {acceptance} |"
        for identifier, title, requirement, acceptance in rows
    )
    tasks = "\n".join(
        f"- [ ] `{identifier}` — Implement {title.lower()}. {acceptance}"
        for identifier, title, _, acceptance in rows
    )
    tests = "\n".join(
        f"| `{identifier}` | {acceptance} |" for identifier, _, _, acceptance in rows
    )
    code = (
        f"../../{package}/auth.py ../../{package}/api/api_client_base.py "
        f"../../{package}/mcp_server.py ../../{package}/mcp/mcp_system.py "
        f"../../{package}/kg_ingest.py ../../tests/test_auth.py "
        f"../../tests/test_api_wrapper.py ../../{mcp_test} "
        "../../tests/test_kg_ingest.py ../../scripts/generate_tool_schemas.py"
    )
    architecture = """flowchart LR
    Caller[Authorized caller] --> Server[MCP server]
    Server --> Router[Operation router]
    Router --> Client[Connector API client]
    Client --> Vendor[Configured external system]
    Resolver[Credential references and TLS policy] --> Client
    Content[Packaged skills prompts ontology manifest] --> Server
    Source[Authorized source observations] --> Mapper[Connector ingest mapper]
    Mapper --> SDK[Shared connector ingest service]
"""
    return {
        "specs/README.md": f"""# Connector specifications

Follow the [shared spec standard]({STANDARD}).

## Owner map

| Prefix | Owner |
|---|---|
| `CONN` | This connector's external-system behavior |
| `{concept}` | This repository's concept registry |

- [`{spec_id}`]({name}/spec.md) — Integrate {display} through the shared connector contracts.

The lifecycle generator owns delivery receipts in `status.json`.
Run `pipelines-hook spec-status --write` after reviewed source changes enter Git history.
Run `pipelines-hook spec-standard` and `pipelines-hook spec-decomposition` before publishing source changes.
See the [delivery dashboard](https://knuckles-team.github.io/{name}/spec-delivery/).
""",
        f"{directory}/spec.md": f"""# {spec_id} — {display} connector

## Outcome

The connector must expose reviewed external-system operations through one governed integration boundary.
The connector must preserve credential, transport, source, and content contracts.

## Scope and owner

The `{name}` repository owns external-system operations and source mappings.
The shared connector SDK owns reusable transport, authentication, MCP, and ingest contracts.
The shared pipelines repository owns quality gates and delivery rendering.

Component: Connector integration
References: [Connector SDK]({SDK_README})
Code: {code}

## Non-goals

This specification grants no service access, credential creation, deployment, or approval exception.
The connector must not implement a graph engine, independent policy authority, or duplicate SDK runtime.

## Why a new spec

The scaffold emits the repository's first capability specification.
No existing specification occurs in this newly generated source tree.
An existing repository must reconcile this capability with its current owner before adopting the generated files.

## Requirements

See [requirements.md](requirements.md), [plan.md](plan.md), and [test-spec.md](test-spec.md).
Existing test references identify verification targets. They do not establish delivery.
""",
        f"{directory}/plan.md": f"""# {spec_id} — Design and implementation plan

Governing specification: [spec.md](spec.md).

## Existing system and reuse

The connector reuses the SDK server factory, credential resolver, HTTP client, and typed ingest service.
The connector owns operation arguments, external-system mappings, and package content.

Component: Connector integration
References: [Connector SDK]({SDK_README})
Code: {code}

## Architecture

```mermaid
{architecture}```

## Interfaces and live integration path

`{package}/mcp_server.py` exposes `build_server` and the console entry point.
`get_mcp_instance` calls `create_mcp_server`, `register_tool_surface`, and the package tool registrars.
`{package}/mcp/mcp_system.py` routes selected operations through `get_client` and the API client.
`{package}/auth.py` resolves references only when a caller requests a client.
`{package}/api/api_client_base.py` enforces transport and response limits before returning external data.
`{package}/kg_ingest.py` maps observations into SDK types and calls the configured service's `submit` method.
The SDK owns engine transport and durable checkpoints.

## Content and contracts

The server serves package prompts, skills, ontology, and `connector_manifest.yml` through native MCP primitives.
The schema generator reads `tools/list` without invoking vendor operations.
It records both input and output schemas. Empty source presets declare no extraction integration.
Native content listing acceptance remains pending until a connector-owned test exercises the production server.

## Dependencies and decisions

No additional capability prerequisite has been established in this starter repository.
The SDK reference records a source dependency; it does not create a cross-repository delivery prerequisite.
Reviewers must add `Depends-on:` declarations only for confirmed prerequisite requirements.
Each source mapping must match the connector's actual external data before ingestion is enabled.

## Quality and release gates

Run `python scripts/check_connector_contract.py . --package {package}`.
Run `python scripts/generate_tool_schemas.py --check` and `python -m pytest tests -q`.
Run the pinned pre-commit and pre-push gates with the approved scanner toolchain.
The published site must pass the shared readiness checks and render canonical spec records.
Source tests do not authorize release, deployment, or external effects.

## Risks and alternatives

Starter operations and mappings require external-system validation before production use.
Missing credentials, rejected source observations, and failed transport checks must propagate as explicit failures.
Duplicating shared SDK or pipeline logic would create conflicting owners.
""",
        f"{directory}/requirements.md": f"""# {spec_id} — Requirements

Governing specification: [spec.md](spec.md).

Each row identifies one connector behavior and its verification target.

| ID | Requirement | Acceptance |
|---|---|---|
{requirements}
""",
        f"{directory}/tasks.md": f"""# {spec_id} — Implementation tasks

Governing specification: [spec.md](spec.md).

The owner must reconcile starter behavior with the external system before completing these tasks.

{tasks}
""",
        f"{directory}/test-spec.md": f"""# {spec_id} — Verification plan

Governing specification: [spec.md](spec.md).

These acceptance targets require connector-specific execution and review.
Test names describe source mappings, not successful runs or delivery receipts.
Native content listing needs a connector-owned integration test before the content requirement is delivered.

| Requirement | Verification target |
|---|---|
{tests}

The owner must retain failure evidence and use canonical lifecycle tooling to regenerate `status.json`.
""",
        f"{directory}/status.json": json.dumps(status, indent=2, ensure_ascii=False)
        + "\n",
        "docs/architecture.md": f"""# Connector architecture

The `{name}` package owns external-system operations and source mappings.
The [shared connector SDK]({SDK_README}) owns reusable runtime contracts.

```mermaid
{architecture}```

## Source and verification map

| Boundary | Source | Verification target |
|---|---|---|
| MCP entry and routing | `{package}/mcp_server.py`, `{package}/mcp/mcp_system.py` | `{mcp_test}` |
| Credentials and TLS | `{package}/auth.py` | `tests/test_auth.py` |
| External requests | `{package}/api/api_client_base.py` | `tests/test_api_wrapper.py` |
| Native content and tool schemas | Package content and `scripts/generate_tool_schemas.py` | Live schema check; native content verification remains pending |
| Source observations | `{package}/kg_ingest.py` | `tests/test_kg_ingest.py` |

The [capability specification](https://github.com/Knuckles-Team/{name}/blob/main/specs/{name}/spec.md)
defines the planned behavior and acceptance targets.
The [delivery dashboard](https://knuckles-team.github.io/{name}/spec-delivery/)
shows source-backed records, code mappings, and declared relationships.
Its architecture download preserves the declared spec graph without inferring dependencies from shared code.

The generated source does not prove live service behavior, published artifacts, or deployed operation.
""",
    }

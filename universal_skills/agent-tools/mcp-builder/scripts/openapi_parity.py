"""Complete source inventories and API/MCP contract parity, without provider calls."""

from __future__ import annotations

import copy
import hashlib
import json

if __package__:
    from .openapi_provider_overlay import apply_provider_overlay
    from .openapi_schema import compile_contract, domain_schemas
    from .openapi_security import validate_requirements, validate_security
    from .openapi_source_parity import source_route, verify_source_routes
else:
    from openapi_provider_overlay import apply_provider_overlay
    from openapi_schema import compile_contract, domain_schemas
    from openapi_security import validate_requirements, validate_security
    from openapi_source_parity import source_route, verify_source_routes

HTTP_METHODS = frozenset(
    {"get", "put", "post", "delete", "options", "head", "patch", "trace"}
)


def digest(value):
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def _operation_entry(document, path, *, method, operation):
    return {
        **source_route(document, path, operation),
        "method": method.upper(),
        "source_path": path,
        "security": operation.get("security", document.get("security", [])),
        "security_declaration": (
            "operation"
            if "security" in operation
            else "root"
            if "security" in document
            else "unknown"
        ),
        "extensions": {
            key: value for key, value in operation.items() if key.startswith("x-")
        },
        "deprecated": operation.get("deprecated", False),
        "tags": operation.get("tags", []),
        "operation_sha256": digest(operation),
    }


def operation_inventory(document, source_sha256):
    """Enumerate the entire pinned source, independently of compiler filtering."""
    document = copy.deepcopy(document)
    schemes = validate_security(document)
    operations = {}
    for path, item in sorted(document["paths"].items()):
        for method, operation in sorted(item.items()):
            if method not in HTTP_METHODS:
                continue
            action = operation["operationId"]
            if action in operations:
                raise ValueError(f"Duplicate source operation: {action}")
            operations[action] = _operation_entry(
                document, path, method=method, operation=operation
            )
            operations[action]["path_parameters_sha256"] = digest(
                item.get("parameters", [])
            )
    if not operations:
        raise ValueError("Source declares no HTTP operations")
    return {
        "version": 1,
        "source_sha256": source_sha256,
        "source_info": document.get("info", {}),
        "openapi_version": document["openapi"],
        "security_schemes": schemes,
        "path_count": len(document["paths"]),
        "operation_count": len(operations),
        "operations": dict(sorted(operations.items())),
        "scope": "All operations in this pinned OpenAPI source; upstream suite completeness requires separate evidence.",
        "live_verified": False,
    }


def require_declared_authorization(inventory):
    """Schema omission is not proof that an operation is public."""
    for operation in inventory["operations"].values():
        validate_requirements(
            operation["security"],
            inventory["security_schemes"],
            openapi_version=inventory["openapi_version"],
        )
    classified = {
        item["operation_id"]
        for item in inventory.get("provider_overlay", {}).get(
            "authorization_classifications", []
        )
    }
    unknown = [
        action
        for action, operation in inventory["operations"].items()
        if operation["security_declaration"] == "unknown" and action not in classified
    ]
    if unknown:
        raise ValueError(
            f"Authorization classification requires reviewed provider evidence: {unknown}"
        )


def require_complete_coverage(contract, api_actions, mcp_actions):
    """Call with successful probe IDs, not discovery IDs, for transport coverage."""
    expected = set(contract["operations"])
    for label, actions in (("API", list(api_actions)), ("MCP", list(mcp_actions))):
        if len(actions) != len(set(actions)):
            raise ValueError(f"Duplicate {label} coverage IDs")
        missing, extra = (
            sorted(expected - set(actions)),
            sorted(set(actions) - expected),
        )
        if missing or extra:
            raise ValueError(
                f"Incomplete {label} coverage: missing={missing}, extra={extra}"
            )
    return {"api_operations": len(expected), "mcp_operations": len(expected)}


def source_context(
    document,
    source_sha256,
    *,
    source_bytes=None,
    overlay_bytes=None,
    expected_overlay_sha256=None,
    evidence_root=None,
):
    inventory = operation_inventory(document, source_sha256)
    if overlay_bytes is None:
        if expected_overlay_sha256 is not None or evidence_root is not None:
            raise ValueError("Provider evidence options require an exact overlay")
        return document, inventory
    if (
        not isinstance(source_bytes, bytes)
        or hashlib.sha256(source_bytes).hexdigest() != source_sha256
        or json.loads(source_bytes) != document
    ):
        raise ValueError("Provider correction requires the exact raw source bytes")
    effective, receipt = apply_provider_overlay(
        source_bytes,
        overlay_bytes,
        expected_overlay_sha256=expected_overlay_sha256,
        evidence_root=evidence_root,
    )
    inventory["provider_overlay"] = receipt
    return effective, inventory


def verify_contract(document, contract, source_sha256, **provider_options):
    """Reject source omissions and exact method, route, parameter or schema drift."""
    effective, inventory = source_context(document, source_sha256, **provider_options)
    # A compiler must not be able to mutate the independent source inventory.
    expected = compile_contract(
        copy.deepcopy(effective),
        response_corrections=inventory.get("provider_overlay", {}).get(
            "response_corrections", []
        ),
    )
    if set(inventory["operations"]) != set(expected["operations"]):
        raise ValueError("Compiler omitted or invented source operations")
    expected["source_sha256"] = source_sha256
    if "provider_overlay" in inventory:
        expected["provider_overlay"] = inventory["provider_overlay"]
    verify_source_routes(inventory, expected)
    verify_source_routes(inventory, contract)
    expected["schemas"] = {
        domain: domain_schemas(expected, domain) for domain in expected["domains"]
    }
    # JSON round-trip accounts only for tuples in the compiler's return value.
    if contract != json.loads(json.dumps(expected)):
        raise ValueError("API contract differs from complete source compilation")
    mapped = [action for actions in contract["domains"].values() for action in actions]
    require_complete_coverage(contract, mapped, mapped)
    for domain, actions in contract["domains"].items():
        if any(
            contract["operations"][action]["domain"] != domain for action in actions
        ):
            raise ValueError("Operation is unreachable through its declared domain")
    return inventory


def verify_mcp(contract, tools):
    """Compare actual native tools/list results, including every action branch."""
    try:
        from agent_connector_sdk.manifest.tool_schema import read_field
    except ImportError as exc:
        raise RuntimeError("MCP parity requires the reviewed SDK environment") from exc
    names = [read_field(tool, "name") for tool in tools]
    if len(names) != len(set(names)):
        raise ValueError("Duplicate MCP tool names")
    by_name = dict(zip(names, tools, strict=True))
    covered = []
    for domain, actions in contract["domains"].items():
        name = f"{domain}_operations"
        if name not in by_name:
            raise ValueError(f"Unreachable MCP domain: {domain}")
        _verify_tool_schema(by_name[name], contract["schemas"][domain], name)
        covered.extend(actions)
    require_complete_coverage(contract, contract["operations"], covered)
    return {"domains": len(contract["domains"]), "exposed_operations": len(covered)}


def _verify_tool_schema(tool, schemas, name):
    from agent_connector_sdk.manifest.tool_schema import (
        canonical_input_schema,
        canonical_output_schema,
    )
    from fastmcp.utilities.json_schema import dereference_refs
    from jsonschema import Draft202012Validator
    from jsonschema.exceptions import SchemaError

    inputs, outputs = schemas
    expected = {"inputSchema": inputs, "outputSchema": outputs}
    # Use FastMCP's actual bounded serve-time transformation. It preserves
    # reference siblings and retains references for recursive/large graphs.
    expanded = {
        "inputSchema": dereference_refs(inputs),
        "outputSchema": dereference_refs(outputs),
    }
    for canonical in (canonical_input_schema, canonical_output_schema):
        actual = canonical(tool)
        try:
            Draft202012Validator.check_schema(actual)
        except SchemaError as exc:
            raise ValueError(
                f"Native MCP schema is unsupported by client validation: {name}"
            ) from exc
        if actual != canonical(expected) and actual != canonical(expanded):
            raise ValueError(f"MCP schema differs from API contract: {name}")

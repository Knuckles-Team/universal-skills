"""Compile every OpenAPI operation into deterministic, action-bound schemas."""

from __future__ import annotations

import copy
import re
from collections import defaultdict

if __package__:
    from .openapi_schema_inputs import input_schema, response_mode
    from .openapi_schema_types import (
        METHODS,
        check_path_parameters,
        identifier,
        object_schema,
        resolve,
        schema,
        validate_binary_constraints,
    )
    from .openapi_security import validate_security
else:
    from openapi_schema_inputs import input_schema, response_mode
    from openapi_schema_types import (
        METHODS,
        check_path_parameters,
        identifier,
        object_schema,
        resolve,
        schema,
        validate_binary_constraints,
    )
    from openapi_security import validate_security


def _prefix(document):
    if not str(document.get("openapi", "")).startswith("3."):
        raise ValueError("OpenAPI 3 is required")
    servers = document.get("servers", [{"url": ""}])
    prefix = servers[0].get("url", "").rstrip("/")
    if prefix and (
        not prefix.startswith("/") or prefix.startswith("//") or "{" in prefix
    ):
        raise ValueError("Server must be a fixed deployment-neutral path")
    return prefix


def _check_path(path, item):
    if (
        not path.startswith("/")
        or path.startswith("//")
        or "?" in path
        or "#" in path
        or ".." in path.split("/")
    ):
        raise ValueError("Unsafe OpenAPI path")
    if "servers" in item or "$ref" in item:
        raise ValueError("Path-level overrides require an explicit adapter")


def _domain(path, operation, names):
    if "servers" in operation or "callbacks" in operation:
        raise ValueError("Operation overrides require an explicit adapter")
    tags = [tag for tag in operation.get("tags", []) if tag != "Deprecated"]
    label = tags[0] if tags else path.strip("/").split("/")[0]
    domain = identifier(label)
    if domain in names and names[domain] != label:
        raise ValueError("Domain normalization collision")
    names[domain] = label
    return domain


def _responses(document, operation):
    responses, modes = {}, {}
    for status, raw in sorted(operation.get("responses", {}).items()):
        response = resolve(document, raw)
        content = response.get("content", {})
        responses[status] = {
            media: schema(body.get("schema", {})) for media, body in content.items()
        }
        modes[status] = {
            media: response_mode(document, media, body)
            for media, body in content.items()
        }
    return responses, modes


def _operation(document, operation, *, route, domain, shared):
    method, path = route
    inputs, parameters, content_type = input_schema(document, shared, operation)
    check_path_parameters(path, parameters)
    responses, response_modes = _responses(document, operation)
    action = operation["operationId"]
    return {
        "action": action,
        "domain": domain,
        "method": method.upper(),
        "path": path,
        "read_only": method in {"get", "head", "options"},
        "input": inputs,
        "parameters": parameters,
        "content_type": content_type,
        "responses": responses,
        "response_modes": response_modes,
        "security": operation.get("security", document.get("security", [])),
        "summary": operation.get("summary", action),
    }


def compile_contract(document):
    """Every source operation belongs to exactly one domain; omissions fail closed."""
    validate_binary_constraints(document)
    validate_security(document)
    prefix = _prefix(document)
    domains, operations, names = defaultdict(list), {}, {}
    for path, item in sorted(document["paths"].items()):
        _check_path(path, item)
        for method, operation in sorted(item.items()):
            if method not in METHODS:
                continue
            action = operation["operationId"]
            if action in operations or not re.fullmatch(
                r"[A-Za-z][A-Za-z0-9_]*", action
            ):
                raise ValueError("Invalid or duplicate operationId")
            domain = _domain(path, operation, names)
            operations[action] = _operation(
                document,
                operation,
                route=(method, prefix + path),
                domain=domain,
                shared=item.get("parameters", []),
            )
            domains[domain].append(action)
    return _final_contract(document, domains, operations)


def _final_contract(document, domains, operations):
    return {
        "version": 1,
        "definitions": schema(
            copy.deepcopy(document.get("components", {}).get("schemas", {}))
        ),
        "security_schemes": document.get("components", {}).get("securitySchemes", {}),
        "domains": {key: sorted(value) for key, value in sorted(domains.items())},
        "operations": dict(sorted(operations.items())),
    }


def domain_schemas(contract, domain):
    operations = [
        contract["operations"][action] for action in contract["domains"][domain]
    ]
    inputs = {
        "type": "object",
        "oneOf": [operation["input"] for operation in operations],
        "$defs": contract["definitions"],
    }
    outputs = []
    for operation in operations:
        for status, media in operation["responses"].items():
            if not status.startswith("2"):
                continue
            for content_type, body in (media or {"": {"type": "null"}}).items():
                outputs.append(
                    object_schema(
                        {
                            "action": {"const": operation["action"], "type": "string"},
                            "status": {"const": int(status), "type": "integer"},
                            "content_type": {"const": content_type, "type": "string"},
                            "data": body,
                        },
                        ["action", "status", "content_type", "data"],
                    )
                )
    return trim_definitions(inputs), trim_definitions(
        {"type": "object", "anyOf": outputs, "$defs": contract["definitions"]}
    )


def _schema_refs(value):
    pending = [value]
    while pending:
        item = pending.pop()
        if isinstance(item, list):
            pending.extend(item)
            continue
        if not isinstance(item, dict):
            continue
        ref = item.get("$ref", "")
        if ref.startswith("#/$defs/"):
            yield ref[len("#/$defs/") :]
        pending.extend(item.values())


def trim_definitions(value):
    definitions = value.pop("$defs")
    pending = list(_schema_refs(value))
    used = set()
    while pending:
        name = pending.pop()
        if name in used:
            continue
        used.add(name)
        pending.extend(_schema_refs(definitions[name]))
    return {**value, "$defs": {key: definitions[key] for key in sorted(used)}}

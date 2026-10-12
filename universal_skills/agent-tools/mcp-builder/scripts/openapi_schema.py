"""Compile OpenAPI operations into deterministic, action-bound JSON schemas."""

from __future__ import annotations

import copy
import re
from collections import defaultdict

METHODS = frozenset(
    {"get", "post", "put", "delete", "patch", "head", "options", "trace"}
)


def identifier(value: str) -> str:
    result = re.sub(r"[^a-z0-9]+", "_", value.casefold()).strip("_")
    if not result or result[0].isdigit():
        raise ValueError("Domain must have an alphabetic identifier")
    return result


def schema(value):
    """Retain endpoint constraints while translating OpenAPI 3.0 nullability."""
    if isinstance(value, list):
        return [schema(item) for item in value]
    if not isinstance(value, dict):
        return value
    result = {key: schema(item) for key, item in value.items() if key != "nullable"}
    if "$ref" in result:
        ref = result["$ref"]
        if not ref.startswith("#/components/schemas/"):
            raise ValueError("Only local schema references are supported")
        result["$ref"] = ref.replace("#/components/schemas/", "#/$defs/", 1)
    if result.get("format") == "binary":
        result = {
            "type": "string",
            "contentEncoding": "base64",
            "description": "Base64 file bytes; no filesystem paths.",
        }
    for name, replacement in (
        ("exclusiveMinimum", "minimum"),
        ("exclusiveMaximum", "maximum"),
    ):
        if isinstance(result.get(name), bool):
            enabled = result.pop(name)
            if enabled and replacement in result:
                result[name] = result.pop(replacement)
    if value.get("nullable"):
        result = {"anyOf": [result, {"type": "null"}]}
    return result


def resolve(document, value):
    seen = set()
    while "$ref" in value:
        ref = value["$ref"]
        if not ref.startswith("#/") or ref in seen:
            raise ValueError("External or cyclic object reference")
        seen.add(ref)
        value = document
        for segment in ref[2:].split("/"):
            value = value[segment.replace("~1", "/").replace("~0", "~")]
    return value


def object_schema(properties, required=()):
    return {
        "type": "object",
        "properties": properties,
        "required": sorted(required),
        "additionalProperties": False,
    }


def input_schema(document, shared, operation):
    fields = {"action": {"type": "string", "enum": [operation["operationId"]]}}
    required = ["action"]
    parameters = {}
    for raw in shared + operation.get("parameters", []):
        parameter = resolve(document, raw)
        parameters[(parameter["in"], parameter["name"])] = parameter
    for location in ("path", "query", "header", "cookie"):
        items = [v for (where, _), v in sorted(parameters.items()) if where == location]
        if not items:
            continue
        if location == "cookie":
            raise ValueError("Cookie parameters require an explicit provider adapter")
        props, needed = {}, []
        for item in items:
            expected = "form" if location == "query" else "simple"
            if item.get("style", expected) != expected:
                raise ValueError("Unsupported parameter style")
            props[item["name"]] = schema(item["schema"])
            if item.get("required") or location == "path":
                needed.append(item["name"])
        fields[location] = object_schema(props, needed)
        if needed:
            required.append(location)
    body = resolve(document, operation.get("requestBody", {}))
    media = body.get("content", {})
    content_type = next(
        (
            name
            for name in (
                "application/json",
                "multipart/form-data",
                "application/x-www-form-urlencoded",
            )
            if name in media
        ),
        None,
    )
    if media and content_type is None:
        raise ValueError("Unsupported request media type")
    if content_type:
        fields["body"] = schema(media[content_type].get("schema", {}))
        if body.get("required"):
            required.append("body")
    return object_schema(fields, required), list(parameters.values()), content_type


def response_mode(document, media, body):
    """Choose only a response representation supported by the runtime."""
    if media == "application/json" or media.endswith("+json"):
        return "json"
    resolved = resolve(document, body.get("schema", {}))
    if resolved.get("format") == "binary":
        return "binary"
    if media.startswith("text/") or media == "application/vnd.apple.mpegurl":
        if resolved.get("type", "string") != "string":
            raise ValueError("Text response must declare a string schema")
        return "text"
    raise ValueError("Unsupported response media type or missing binary declaration")


def compile_contract(document):
    """Every operation belongs to exactly one stable domain; collisions fail closed."""
    if not str(document.get("openapi", "")).startswith("3."):
        raise ValueError("OpenAPI 3 is required")
    servers = document.get("servers", [{"url": ""}])
    prefix = servers[0].get("url", "").rstrip("/")
    if prefix and (
        not prefix.startswith("/") or prefix.startswith("//") or "{" in prefix
    ):
        raise ValueError("Server must be a fixed deployment-neutral path")
    domains = defaultdict(list)
    operations = {}
    domain_names = {}
    for path, item in sorted(document["paths"].items()):
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
        for method, operation in sorted(item.items()):
            if method not in METHODS:
                continue
            action = operation["operationId"]
            if action in operations or not re.fullmatch(
                r"[A-Za-z][A-Za-z0-9_]*", action
            ):
                raise ValueError("Invalid or duplicate operationId")
            if "servers" in operation or "callbacks" in operation:
                raise ValueError("Operation overrides require an explicit adapter")
            tags = [tag for tag in operation.get("tags", []) if tag != "Deprecated"]
            label = tags[0] if tags else path.strip("/").split("/")[0]
            domain = identifier(label)
            if domain in domain_names and domain_names[domain] != label:
                raise ValueError("Domain normalization collision")
            domain_names[domain] = label
            inputs, parameters, content_type = input_schema(
                document, item.get("parameters", []), operation
            )
            responses, response_modes = {}, {}
            for status, raw in sorted(operation.get("responses", {}).items()):
                response = resolve(document, raw)
                responses[status] = {
                    media: schema(body.get("schema", {}))
                    for media, body in response.get("content", {}).items()
                }
                response_modes[status] = {
                    media: response_mode(document, media, body)
                    for media, body in response.get("content", {}).items()
                }
            operations[action] = {
                "action": action,
                "domain": domain,
                "method": method.upper(),
                "path": prefix + path,
                "read_only": method in {"get", "head", "options"},
                "input": inputs,
                "parameters": parameters,
                "content_type": content_type,
                "responses": responses,
                "response_modes": response_modes,
                "security": operation.get("security", document.get("security", [])),
                "summary": operation.get("summary", action),
            }
            domains[domain].append(action)
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


def trim_definitions(value):
    definitions = value.pop("$defs")
    pending = [value]
    used = set()
    while pending:
        item = pending.pop()
        if isinstance(item, list):
            pending.extend(item)
        elif isinstance(item, dict):
            ref = item.get("$ref", "")
            if ref.startswith("#/$defs/"):
                name = ref[len("#/$defs/") :]
                if name not in used:
                    used.add(name)
                    pending.append(definitions[name])
            pending.extend(item.values())
    return {**value, "$defs": {key: definitions[key] for key in sorted(used)}}

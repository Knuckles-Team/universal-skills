"""Shared OpenAPI schema/reference translations, without provider inference."""

from __future__ import annotations

import re

if __package__:
    from .unicode_patterns import translate_pattern
else:
    from unicode_patterns import translate_pattern

METHODS = frozenset(
    {"get", "post", "put", "delete", "patch", "head", "options", "trace"}
)
BINARY_CONSTRAINTS = frozenset(
    {
        "minLength",
        "maxLength",
        "pattern",
        "enum",
        "const",
        "allOf",
        "anyOf",
        "oneOf",
        "not",
    }
)


def validate_binary_constraints(document):
    """Reject encoded/raw constraint mismatches, including reference siblings."""
    pending = [document]
    while pending:
        value = pending.pop()
        if isinstance(value, list):
            pending.extend(value)
            continue
        if not isinstance(value, dict):
            continue
        if BINARY_CONSTRAINTS.intersection(value) and _references_binary(
            document, value, set()
        ):
            raise ValueError(
                "Constrained binary schema requires a representation-aware provider adapter"
            )
        pending.extend(value.values())


def _references_binary(document, value, seen):
    if not isinstance(value, dict):
        return False
    if value.get("format") == "binary":
        return True
    ref = value.get("$ref")
    if ref and ref not in seen:
        return _references_binary(document, resolve(document, value), seen | {ref})
    branches = [
        *value.get("allOf", []),
        *value.get("anyOf", []),
        *value.get("oneOf", []),
        value.get("not"),
    ]
    return any(_references_binary(document, item, seen) for item in branches)


def identifier(value: str) -> str:
    result = re.sub(r"[^a-z0-9]+", "_", value.casefold()).strip("_")
    if not result or result[0].isdigit():
        raise ValueError("Domain must have an alphabetic identifier")
    return result


def check_path_parameters(path, parameters):
    """Reject exported request objects masquerading as path parameters."""
    remaining = re.sub(r"\{[^{}]+\}", "", path)
    if "{" in remaining or "}" in remaining:
        raise ValueError("Malformed path placeholder")
    tokens = set(re.findall(r"\{([^{}]+)\}", path))
    declared = {item["name"] for item in parameters if item["in"] == "path"}
    if tokens != declared:
        raise ValueError(f"Path placeholders differ from declared parameters: {path}")


def schema(value):
    """Retain endpoint constraints while translating OpenAPI 3.0 nullability."""
    if isinstance(value, list):
        return [schema(item) for item in value]
    if not isinstance(value, dict):
        return value
    result = {key: schema(item) for key, item in value.items() if key != "nullable"}
    result = _schema_keywords(result)
    if "$ref" in result and len(result) > 1:
        # A reference and its sibling assertions intersect. FastMCP's shallow
        # sibling merge could overwrite a stronger referenced assertion.
        reference = {"$ref": result.pop("$ref")}
        intersections = result.get("allOf", [])
        if not isinstance(intersections, list):
            raise ValueError("Schema allOf must be an array")
        # Keep unevaluatedProperties/Items at the original scope so they can
        # observe annotations from the referenced schema and existing branches.
        result["allOf"] = [reference, *intersections]
    if value.get("nullable"):
        return {"anyOf": [result, {"type": "null"}]}
    return result


def _schema_keywords(result):
    if isinstance(result.get("pattern"), str):
        result["pattern"] = translate_pattern(result["pattern"])
    if "$ref" in result:
        ref = result["$ref"]
        if not ref.startswith("#/components/schemas/"):
            raise ValueError("Only local schema references are supported")
        result["$ref"] = ref.replace("#/components/schemas/", "#/$defs/", 1)
    if result.get("format") == "binary":
        result = _binary_schema(result)
    for name, replacement in (
        ("exclusiveMinimum", "minimum"),
        ("exclusiveMaximum", "maximum"),
    ):
        if isinstance(result.get(name), bool):
            enabled = result.pop(name)
            if enabled and replacement in result:
                result[name] = result.pop(replacement)
    return result


def _binary_schema(result):
    """Adapt the wire representation without deleting source constraints."""
    if (BINARY_CONSTRAINTS | {"$ref"}).intersection(result):
        raise ValueError(
            "Constrained binary schema requires a representation-aware provider adapter"
        )
    original_encoding = result.get("contentEncoding")
    if original_encoding and original_encoding != "base64":
        key = "x-mcp-source-content-encoding"
        if key in result:
            raise ValueError("Reserved binary representation metadata collision")
        result[key] = original_encoding
    result["contentEncoding"] = "base64"
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

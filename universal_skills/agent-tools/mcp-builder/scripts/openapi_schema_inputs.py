"""Compile operation parameters, body representations and response modes."""

from __future__ import annotations

if __package__:
    from .openapi_schema_types import object_schema, resolve, schema
else:
    from openapi_schema_types import object_schema, resolve, schema


def _location_schema(location, items):
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
    return object_schema(props, needed), bool(needed)


def _request_body(document, operation):
    body = resolve(document, operation.get("requestBody", {}))
    media = body.get("content", {})
    if len(media) > 1:
        raise ValueError(
            "Multiple request media types require a representation-complete adapter"
        )
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
    definition = schema(media[content_type].get("schema", {})) if content_type else None
    return content_type, definition, body.get("required", False)


def input_schema(document, shared, operation):
    fields = {"action": {"type": "string", "enum": [operation["operationId"]]}}
    required = ["action"]
    parameters = {}
    for raw in shared + operation.get("parameters", []):
        parameter = resolve(document, raw)
        if parameter["in"] not in {"path", "query", "header", "cookie"}:
            raise ValueError("Unsupported parameter location")
        parameters[(parameter["in"], parameter["name"])] = parameter
    _parameter_fields(parameters, fields, required)
    content_type, body, needed = _request_body(document, operation)
    if content_type:
        fields["body"] = body
        if needed:
            required.append("body")
    return object_schema(fields, required), list(parameters.values()), content_type


def _parameter_fields(parameters, fields, required):
    for location in ("path", "query", "header", "cookie"):
        items = [v for (where, _), v in sorted(parameters.items()) if where == location]
        if not items:
            continue
        fields[location], needed = _location_schema(location, items)
        if needed:
            required.append(location)


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

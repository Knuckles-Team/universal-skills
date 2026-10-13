"""Bind a reviewed empty-success correction to a non-followed GET redirect."""

from __future__ import annotations

import copy
import re

if __package__:
    from .openapi_provider_evidence import _fields, _hash, _references
else:
    from openapi_provider_evidence import _fields, _hash, _references

_CORRECTION = dict.fromkeys(
    (
        "op",
        "operation_id",
        "method",
        "path",
        "source_operation_sha256",
        "before_responses_sha256",
        "after_responses_sha256",
    ),
    str,
) | {"location_schema": dict, "source_evidence": list}


def _location_schema(value):
    _fields(value, {"type": str, "minLength": int, "maxLength": int, "pattern": str})
    if (
        value["type"] != "string"
        or not 1 <= value["minLength"] <= value["maxLength"] <= 8192
    ):
        raise ValueError("Redirect Location must be a bounded nonempty string")
    if not value["pattern"].startswith("^") or not value["pattern"].endswith("$"):
        raise ValueError("Redirect Location requires an anchored provider pattern")
    re.compile(value["pattern"])
    return {"format": "uri", **copy.deepcopy(value)}


def redirect_response(correction):
    return {
        "description": "Reviewed provider redirect; returned as data, never followed.",
        "headers": {
            "Location": {
                "required": True,
                "schema": _location_schema(correction["location_schema"]),
            }
        },
    }


def _target(document, correction, operations):
    _fields(correction, _CORRECTION)
    if (
        correction["op"] != "replace-empty-200-with-307"
        or correction["method"] != "GET"
    ):
        raise ValueError("Only reviewed empty-200 to GET-307 corrections are supported")
    binding = operations.get(correction["operation_id"], {})
    for key in ("operation_id", "method", "path", "source_operation_sha256"):
        if correction[key] != binding.get(key):
            raise ValueError("Response correction has a stale source operation binding")
    return document["paths"][correction["path"]]["get"]


def _replace_response(operation, correction):
    responses = operation.get("responses", {})
    if _hash(responses) != correction["before_responses_sha256"]:
        raise ValueError("Response correction has a stale response hash")
    previous = responses.get("200")
    if (
        not isinstance(previous, dict)
        or previous.keys() - {"description"}
        or "307" in responses
    ):
        raise ValueError(
            "Correction requires an empty declared 200 and no existing 307"
        )
    del responses["200"]
    responses["307"] = redirect_response(correction)
    if _hash(responses) != correction["after_responses_sha256"]:
        raise ValueError("Corrected response hash mismatch")


def apply_response_corrections(document, corrections, *, operations, evidence):
    seen = set()
    for correction in corrections:
        operation = _target(document, correction, operations)
        action = correction["operation_id"]
        if action in seen:
            raise ValueError("Duplicate response correction")
        _references(correction["source_evidence"], evidence)
        _replace_response(operation, correction)
        seen.add(action)


def compiled_redirect(operation, corrections):
    """Consume the verified overlay receipt; raw 3xx declarations grant nothing."""
    for correction in corrections:
        if correction["operation_id"] != operation["operationId"]:
            continue
        responses = operation.get("responses", {})
        if _hash(responses) != correction["after_responses_sha256"]:
            raise ValueError(
                "Compiled redirect differs from the verified response correction"
            )
        if responses.get("307") != redirect_response(correction):
            raise ValueError("Compiled redirect header contract differs from review")
        return {
            "redirect_responses": {
                "307": {
                    "type": "object",
                    "properties": {
                        "location": _location_schema(correction["location_schema"])
                    },
                    "required": ["location"],
                    "additionalProperties": False,
                }
            }
        }
    return {}


def response_variants(operation):
    for status, media in operation["responses"].items():
        if status.startswith("2"):
            yield from (
                (status, content_type, body)
                for content_type, body in (media or {"": {"type": "null"}}).items()
            )
    for status, body in operation.get("redirect_responses", {}).items():
        yield status, "", body

"""Apply reviewed additive schema corrections; retain auth evidence as a sidecar.

Version 1 supports named component object schemas and explicit public decorators.
It cannot repair routes, remove constraints, create credentials, or grant readiness.
Component/operation hashes use compact sorted JSON; the effective document uses
sorted, indented UTF-8 JSON with a final newline. Both use ensure_ascii=True.
Evidence verification requires POSIX descriptor operations and fails closed elsewhere.
"""

from __future__ import annotations

import copy
import json
import re

if __package__:
    from .openapi_provider_evidence import (
        _evidence,
        _fields,
        _hash,
        _pairs,
        _references,
    )
    from .openapi_security import validate_security
else:
    from openapi_provider_evidence import _evidence, _fields, _hash, _pairs, _references
    from openapi_security import validate_security

_METHODS = {"get", "put", "post", "delete", "options", "head", "patch", "trace"}
_BINDING = dict.fromkeys(
    ("operation_id", "method", "path", "source_operation_sha256"), str
)
_CORRECTION = dict.fromkeys(
    (
        "op",
        "schema_pointer",
        "property",
        "before_sha256",
        "after_sha256",
        "source_commit",
        "source_file",
        "source_file_sha256",
    ),
    str,
)


def _target(document, correction):
    _fields(correction, _CORRECTION)
    pointer = correction["schema_pointer"]
    if correction["op"] != "require-property" or not re.fullmatch(
        r"/components/schemas/(?:[^~/]|~[01])+", pointer
    ):
        raise ValueError(
            "Only named component require-property corrections are supported"
        )
    name = pointer.removeprefix("/components/schemas/")
    name = name.replace("~1", "/").replace("~0", "~")
    schemas = document.get("components", {}).get("schemas", {})
    if not isinstance(schemas, dict):
        raise ValueError("Schema components must be an object")
    target = schemas.get(name)
    if (
        not isinstance(target, dict)
        or target.get("type", "object") != "object"
        or "$ref" in target
        or not isinstance(target.get("properties"), dict)
    ):
        raise ValueError("Correction must target an existing object schema")
    return target


def _require_property(document, correction, evidence):
    target = _target(document, correction)
    prop, required = correction["property"], target.get("required", [])
    if not isinstance(required, list) or any(
        not isinstance(item, str) for item in required
    ):
        raise ValueError("Malformed source required array")
    if (
        prop not in target["properties"]
        or prop in required
        or len(required) != len(set(required))
    ):
        raise ValueError(
            "Correction must add one existing, previously optional property"
        )
    record = evidence.get(correction["source_file"], ({},))[0]
    if (record.get("sha256"), record.get("source_commit")) != (
        correction["source_file_sha256"],
        correction["source_commit"],
    ):
        raise ValueError("Correction is not bound to verified provider evidence")
    if _hash(target) != correction["before_sha256"]:
        raise ValueError("Stale correction schema hash")
    target["required"] = [*required, prop]
    if _hash(target) != correction["after_sha256"]:
        raise ValueError("Correction after schema hash mismatch")


def _operations(document):
    result = {}
    for path, item in document.get("paths", {}).items():
        if "$ref" in item:
            raise ValueError("Path references require an explicit adapter")
        for method, operation in item.items():
            if method not in _METHODS:
                continue
            action = operation.get("operationId")
            if not isinstance(action, str) or not action or action in result:
                raise ValueError("Missing or duplicate source operation ID")
            result[action] = {
                "operation_id": action,
                "method": method.upper(),
                "path": path,
                "source_operation_sha256": _hash(operation),
                "unknown": "security" not in operation and "security" not in document,
            }
    return result


def _classification(entry, operations, evidence):
    _fields(
        entry,
        _BINDING
        | {
            "reviewed_guard_classification": str,
            "precondition_category": str,
            "preconditions": str,
            "source_evidence": list,
        },
    )
    source = operations.get(entry["operation_id"], {})
    if not source.get("unknown") or any(entry[key] != source[key] for key in _BINDING):
        raise ValueError(
            "Authorization classification has a stale, extra, or already declared operation"
        )
    if entry[
        "reviewed_guard_classification"
    ] != "explicit-public-decorator" or not re.fullmatch(
        r"[a-z][a-z0-9-]{0,63}", entry["precondition_category"]
    ):
        raise ValueError(
            "Unsupported authorization classification or precondition category"
        )
    _references(entry["source_evidence"], evidence)


def _apply(document, overlay, evidence):
    operations, corrections, classified = _operations(document), set(), set()
    for correction in overlay["corrections"]:
        _fields(correction, _CORRECTION)
        key = (correction["schema_pointer"], correction["property"])
        if key in corrections:
            raise ValueError("Duplicate schema correction")
        _require_property(document, correction, evidence)
        corrections.add(key)
    for entry in overlay["authorization_classifications"]:
        _classification(entry, operations, evidence)
        action = entry["operation_id"]
        if action in classified:
            raise ValueError("Duplicate authorization classification")
        classified.add(action)
    return sorted(
        action
        for action, operation in operations.items()
        if operation["unknown"] and action not in classified
    )


def apply_provider_overlay(
    raw_bytes, overlay_bytes, *, expected_overlay_sha256, evidence_root
):
    """Return ``(effective_document, receipt)``; a matching digest is not readiness.

    The caller supplies the independently approved exact overlay digest. Evidence
    files are read locally beneath evidence_root without following symlinks.
    """
    if (
        not isinstance(raw_bytes, bytes)
        or not isinstance(overlay_bytes, bytes)
        or _hash(overlay_bytes) != expected_overlay_sha256
    ):
        raise ValueError("Expected reviewed overlay SHA256 mismatch or non-byte input")
    document = json.loads(raw_bytes, object_pairs_hook=_pairs)
    overlay = json.loads(overlay_bytes, object_pairs_hook=_pairs)
    _fields(
        overlay,
        {
            "version": int,
            "raw_source_sha256": str,
            "effective_source_sha256": str,
            "evidence_files": list,
            "corrections": list,
            "authorization_classifications": list,
        },
    )
    if overlay["version"] != 1 or _hash(raw_bytes) != overlay["raw_source_sha256"]:
        raise ValueError("Unsupported overlay version or raw source SHA256 mismatch")
    validate_security(document)
    effective = copy.deepcopy(document)
    evidence = _evidence(overlay["evidence_files"], evidence_root)
    unknown = _apply(effective, overlay, evidence)
    encoded = (
        json.dumps(
            effective, sort_keys=True, indent=2, ensure_ascii=True, allow_nan=False
        )
        + "\n"
    ).encode()
    if _hash(encoded) != overlay["effective_source_sha256"]:
        raise ValueError("Effective source SHA256 mismatch")
    receipt = {
        **overlay,
        "overlay_sha256": _hash(overlay_bytes),
        "remaining_unknown_operation_ids": unknown,
        "ready": False,
        "transport_parity_verified": False,
        "live_verified": False,
    }
    return effective, receipt

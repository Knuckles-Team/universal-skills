"""Verify local provider evidence without following paths outside its capture root."""

from __future__ import annotations

import hashlib
import json
import os
import re
import stat
from contextlib import ExitStack
from pathlib import Path

_EVIDENCE = {"path": str, "sha256": str}
_EVIDENCE_OPTIONAL = {"git_blob": str, "source_commit": str}
_MAX_EVIDENCE_BYTES = 16 * 1024 * 1024


def _pairs(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("Duplicate JSON key")
        result[key] = value
    return result


def _hash(value):
    data = (
        value
        if isinstance(value, bytes)
        else json.dumps(
            value,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=True,
            allow_nan=False,
        ).encode()
    )
    return hashlib.sha256(data).hexdigest()


def _fields(value, required, optional=None):
    rules = required | (optional or {})
    if (
        not isinstance(value, dict)
        or not required.keys() <= value.keys()
        or value.keys() - rules.keys()
    ):
        raise ValueError("Unsupported or missing overlay fields")
    for name, item in value.items():
        if type(item) is not rules[name] or (
            isinstance(item, str) and not item.strip()
        ):
            raise ValueError("Invalid overlay field type or empty string")


def _read_file(root, relative):
    try:
        return _safe_read(root, relative)
    except OSError as exc:
        raise ValueError("Evidence file is missing, unsafe, or unreadable") from exc


def _safe_read(root, relative):
    if os.name != "posix":
        raise ValueError(
            "Secure evidence verification requires POSIX descriptor operations"
        )
    parts = relative.split("/")
    if "\\" in relative or any(part in {"", ".", ".."} for part in parts):
        raise ValueError("Evidence path must be a contained relative path")
    parts = [*Path(root).absolute().parts[1:], *parts]
    with ExitStack() as stack:
        directory = os.open("/", os.O_RDONLY | os.O_DIRECTORY)
        stack.callback(os.close, directory)
        for part in parts[:-1]:
            directory = os.open(
                part, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=directory
            )
            stack.callback(os.close, directory)
        fd = os.open(
            parts[-1], os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK, dir_fd=directory
        )
        stream = stack.enter_context(os.fdopen(fd, "rb"))
        if not stat.S_ISREG(os.fstat(stream.fileno()).st_mode):
            raise ValueError("Evidence must be a regular non-symlink file")
        data = stream.read(_MAX_EVIDENCE_BYTES + 1)
    if data[_MAX_EVIDENCE_BYTES:]:
        raise ValueError("Evidence file exceeds the size limit")
    return data


def _evidence(records, root):
    verified = {}
    for record in records:
        _fields(record, _EVIDENCE, _EVIDENCE_OPTIONAL)
        path = record["path"]
        if path in verified:
            raise ValueError("Duplicate evidence path")
        data = _read_file(root, path)
        if _hash(data) != record["sha256"]:
            raise ValueError("Evidence SHA256 mismatch")
        if "source_commit" in record and not re.fullmatch(
            r"[0-9a-f]{40}(?:[0-9a-f]{24})?", record["source_commit"]
        ):
            raise ValueError("Evidence source commit must be an immutable Git ID")
        blob = b"blob " + str(len(data)).encode() + b"\0" + data
        blobs = {hashlib.sha1(blob, usedforsecurity=False).hexdigest(), _hash(blob)}
        if "git_blob" in record and record["git_blob"] not in blobs:
            raise ValueError("Evidence Git blob mismatch")
        verified[path] = (record, len(data.splitlines()), blobs)
    return verified


def _reference(reference, evidence):
    _fields(
        reference,
        _EVIDENCE,
        _EVIDENCE_OPTIONAL | {"line_start": int, "line_end": int, "url": str},
    )
    record, lines, blobs = evidence.get(reference["path"], ({}, 0, set()))
    if reference["sha256"] != record.get("sha256"):
        raise ValueError("Missing or stale authorization evidence")
    if ("git_blob" in reference and reference["git_blob"] not in blobs) or (
        "source_commit" in reference
        and reference["source_commit"] != record.get("source_commit")
    ):
        raise ValueError("Authorization evidence Git identity mismatch")
    start, end = reference.get("line_start", 1), reference.get("line_end", lines)
    if not 1 <= start <= end <= lines:
        raise ValueError("Authorization evidence line range is invalid")
    return _hash(reference)


def _references(references, evidence):
    if not references:
        raise ValueError("Authorization classification requires provider evidence")
    seen = set()
    for reference in references:
        digest = _reference(reference, evidence)
        if digest in seen:
            raise ValueError("Duplicate authorization evidence")
        seen.add(digest)

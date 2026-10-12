"""Read complete connector JSON contracts from one verified offline bundle.

Only the fixed bundle supplied by the caller is read. URI references never open
files or make requests; ordinary document-local JSON Schema references survive
unchanged for the existing validator. Hydration restores canonical source bytes.
"""

from __future__ import annotations

import hashlib
import json

MARKER = "x-connector-schema-bundle"
PREFIX = "urn:connector:schema-bundle#/$defs/"
MAX_BYTES = 16 * 1024 * 1024
MAX_NODES = 200_000
MAX_DEPTH = 100


def encode(value) -> bytes:
    """The existing generated JSON representation, including its final newline."""
    return (
        json.dumps(value, indent=2, sort_keys=True, allow_nan=False) + "\n"
    ).encode()


def digest(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def _read(resource):
    value = resource.read_bytes()
    if len(value) > MAX_BYTES:
        raise ValueError("Schema resource exceeds the byte limit")
    return value


class Hydrator:
    """Expand only content-addressed bundle references within finite limits."""

    def __init__(self, definitions):
        if not isinstance(definitions, dict):
            raise ValueError("Invalid schema bundle definitions")
        self.definitions = definitions
        self.remaining = MAX_NODES

    def expand(self, value, active=(), depth=0):
        self.remaining -= 1
        if self.remaining < 0 or depth > MAX_DEPTH:
            raise ValueError("Schema expansion exceeds its bound")
        if isinstance(value, list):
            return [self.expand(item, active, depth + 1) for item in value]
        if not isinstance(value, dict):
            return value
        reference = value.get("$ref", "")
        if reference and not reference.startswith("#/"):
            return self._reference(value, reference, active, depth)
        return {
            key: self.expand(item, active, depth + 1) for key, item in value.items()
        }

    def _reference(self, value, reference, active, depth):
        if not reference.startswith(PREFIX) or set(value) != {"$ref"}:
            raise ValueError("Unknown schema resource or bundle reference siblings")
        name = reference.removeprefix(PREFIX)
        if name in active or name not in self.definitions:
            raise ValueError("Missing or cyclic schema bundle reference")
        result = self.expand(self.definitions[name], (*active, name), depth + 1)
        if digest(encode(result)) != name:
            raise ValueError("Schema definition content address differs")
        return result


def hydrate(document, bundle_bytes: bytes):
    """Verify both bundle and hydrated document digests before returning data."""
    metadata = document.get(MARKER)
    if not isinstance(metadata, dict) or metadata.get("version") != 1:
        raise ValueError("Unsupported schema bundle document")
    if len(bundle_bytes) > MAX_BYTES or digest(bundle_bytes) != metadata.get("sha256"):
        raise ValueError("Schema bundle digest or byte limit differs")
    bundle = json.loads(bundle_bytes)
    if bundle.get("version") != 1:
        raise ValueError("Unsupported schema bundle version")
    source = {key: value for key, value in document.items() if key != MARKER}
    result = Hydrator(bundle.get("$defs")).expand(source)
    encoded = encode(result)
    if len(encoded) > MAX_BYTES or digest(encoded) != metadata.get("document_sha256"):
        raise ValueError("Hydrated schema document digest or byte limit differs")
    return result


def load_bytes(resource, bundle_resource) -> bytes:
    """Load plain JSON unchanged, or restore its verified canonical source bytes."""
    raw = _read(resource)
    document = json.loads(raw)
    if MARKER not in document:
        return raw
    return encode(hydrate(document, _read(bundle_resource)))


def load_document(resource, bundle_resource):
    return json.loads(load_bytes(resource, bundle_resource))

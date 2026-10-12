"""Intern exactly equal JSON objects across generated connector contracts."""

from __future__ import annotations

from collections import Counter

from templates.schema_bundle import MARKER, PREFIX, digest, encode, hydrate


def _objects(value):
    if isinstance(value, dict):
        yield value
        values = value.values()
    elif isinstance(value, list):
        values = value
    else:
        return
    for item in values:
        yield from _objects(item)


def _replace(value, selected, *, root=False):
    if isinstance(value, list):
        return [_replace(item, selected) for item in value]
    if not isinstance(value, dict):
        return value
    name = digest(encode(value))
    if not root and name in selected:
        return {"$ref": PREFIX + name}
    return {key: _replace(item, selected) for key, item in value.items()}


def bundle_documents(documents):
    """Store shared objects only when references reduce serialized byte storage.

    Selection uses byte cost, not lines or scanner settings. Every hydrated
    document must be byte-identical to its previous canonical representation.
    """
    objects = {}
    counts = Counter()
    for document in documents.values():
        if not isinstance(document, dict) or MARKER in document:
            raise ValueError("Expected a hydrated JSON object")
        for value in _objects(document):
            name = digest(encode(value))
            objects[name] = value
            counts[name] += 1
    selected = set()
    for name, count in counts.items():
        size = len(encode(objects[name]))
        reference_size = len(encode({"$ref": PREFIX + name}))
        if count * size > size + count * reference_size + len(name) + 8:
            selected.add(name)
    bundle = {
        "version": 1,
        "$defs": {
            name: _replace(objects[name], selected, root=True)
            for name in sorted(selected)
        },
    }
    payload = encode(bundle)
    stored = {}
    for name, document in documents.items():
        item = _replace(document, selected, root=True)
        item[MARKER] = {
            "version": 1,
            "sha256": digest(payload),
            "document_sha256": digest(encode(document)),
        }
        if encode(hydrate(item, payload)) != encode(document):
            raise ValueError("Schema bundle changed the source document")
        stored[name] = item
    return stored, bundle

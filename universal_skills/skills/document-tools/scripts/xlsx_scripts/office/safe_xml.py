"""Bounded, entity-free XML parsing for extracted Office documents."""

from __future__ import annotations

from pathlib import Path
from typing import BinaryIO

from defusedxml import ElementTree as DefusedET
from defusedxml.common import DefusedXmlException

MAX_XML_BYTES = 32 * 1024 * 1024
MAX_XML_DEPTH = 96
MAX_XML_ELEMENTS = 500_000


class SafeXmlError(ValueError):
    """An Office XML part crossed a parser security boundary."""


class SafeElementTree:
    """Minimal tree wrapper used by the legacy Office helpers."""

    def __init__(self, root) -> None:
        self._root = root

    def getroot(self):
        return self._root


def _read_bounded(source: str | Path | BinaryIO) -> bytes:
    if hasattr(source, "read"):
        try:
            value = source.read(MAX_XML_BYTES + 1)  # type: ignore[union-attr]
        except OSError:
            raise SafeXmlError("Office XML part is unavailable") from None
        payload = value.encode("utf-8") if isinstance(value, str) else bytes(value)
    else:
        path = Path(source)
        try:
            if path.is_symlink() or not path.is_file():
                raise SafeXmlError("Office XML part is not a regular file")
            expected = path.stat().st_size
            if expected <= 0 or expected > MAX_XML_BYTES:
                raise SafeXmlError("Office XML part exceeds its safe size boundary")
            with path.open("rb") as stream:
                payload = stream.read(MAX_XML_BYTES + 1)
        except SafeXmlError:
            raise
        except OSError:
            raise SafeXmlError("Office XML part is unavailable") from None
        if len(payload) != expected:
            raise SafeXmlError("Office XML part changed while being read")
    if not payload or len(payload) > MAX_XML_BYTES:
        raise SafeXmlError("Office XML part exceeds its safe size boundary")
    return payload


def parse_xml(source: str | Path | BinaryIO):
    """Return an ElementTree after bounded, non-networked XML parsing."""

    try:
        root = DefusedET.fromstring(
            _read_bounded(source),
            forbid_dtd=True,
            forbid_entities=True,
            forbid_external=True,
        )
    except SafeXmlError:
        raise
    except (DefusedET.ParseError, DefusedXmlException, TypeError, ValueError):
        raise SafeXmlError("Office XML part is invalid") from None
    count = 0
    stack = [(root, 1)]
    while stack:
        element, depth = stack.pop()
        count += 1
        if count > MAX_XML_ELEMENTS or depth > MAX_XML_DEPTH:
            raise SafeXmlError("Office XML part exceeds its structure boundary")
        stack.extend((child, depth + 1) for child in element)
    return SafeElementTree(root)

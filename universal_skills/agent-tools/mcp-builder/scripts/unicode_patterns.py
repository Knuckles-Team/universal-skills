"""Translate pinned Unicode general categories without weakening pattern constraints.

The bundled ranges freeze the existing converter runtime's regex 2026.9.29 /
Unicode 18.0.0 semantics. The result uses literal Unicode character ranges,
accepted by Python's JSON Schema validator without nonstandard ``\u005cp`` escapes.
This deliberately supports only positive L, M and N properties; other property
syntax must be implemented and verified explicitly before it is accepted.
"""

from __future__ import annotations

import hashlib
import json
import re
from functools import lru_cache
from pathlib import Path

UNICODE_VERSION = "18.0.0"
PROPERTY_DATA_SHA256 = (
    "94085770ddb2cd6363e7030712be3d0b7a1f4f8cb54a2a6996dac4d03e3e17a4"
)
_TOKENS = re.compile(r"\\[pP]\{[^}]*\}|\\.|[^\\]")


@lru_cache(maxsize=1)
def property_ranges():
    """Read one verified, interpreter-independent table of Unicode properties."""
    source = Path(__file__).with_name("unicode_properties.json").read_bytes()
    if hashlib.sha256(source).hexdigest() != PROPERTY_DATA_SHA256:
        raise ValueError("Unicode property data differs from its reviewed digest")
    data = json.loads(source)
    if data["unicode_version"] != UNICODE_VERSION:
        raise ValueError("Unsupported Unicode property data version")
    return data["ranges"]


def _range_text(bounds):
    first, last = bounds
    return chr(first) if first == last else chr(first) + "-" + chr(last)


def property_class(category):
    """Return literal range text for one supported positive general category."""
    ranges = property_ranges().get(category)
    if ranges is None:
        raise ValueError("Unsupported Unicode property category")
    return "".join(_range_text(bounds) for bounds in ranges)


def _escaped(pattern, index):
    prefix = pattern[:index]
    return (len(prefix) - len(prefix.rstrip("\\"))) % 2 == 1


def _range_operand(pattern, start, end, *, class_start):
    """A property cannot serve as a character-range endpoint."""
    before = pattern[start - 1 : start]
    after = pattern[end : end + 1]
    leading_hyphen = pattern[class_start : start - 1] in {"[", "[^"}
    trailing_hyphen = pattern[end : end + 2] == "-]"
    return (
        before == "-" and not leading_hyphen and not _escaped(pattern, start - 1)
    ) or (after == "-" and not trailing_hyphen)


def _property_token(pattern, token, *, start, end, class_start):
    if not token.startswith(r"\p{"):
        raise ValueError("Unsupported Unicode property syntax")
    if class_start is not None and _range_operand(
        pattern, start, end, class_start=class_start
    ):
        raise ValueError("Unicode property cannot be a range endpoint")
    body = property_class(token[3:-1])
    return body if class_start is not None else "[" + body + "]"


def translate_pattern(pattern):
    """Preserve supported property sets and reject ambiguous/unsupported syntax."""
    rendered = []
    class_start = None
    consumed = 0
    for match in _TOKENS.finditer(pattern):
        token = match.group()
        consumed = match.end()
        if token.startswith((r"\p{", r"\P{")):
            token = _property_token(
                pattern,
                token,
                start=match.start(),
                end=match.end(),
                class_start=class_start,
            )
        elif token == "[" and class_start is None:
            class_start = match.start()
        elif token == "]" and pattern[class_start : match.start()] not in {"[", "[^"}:
            class_start = None
        rendered.append(token)
    if consumed != len(pattern):
        raise ValueError("Incomplete pattern escape")
    result = "".join(rendered)
    try:
        re.compile(result)
    except re.error as exc:
        raise ValueError("Pattern is not supported by native JSON Schema") from exc
    return result

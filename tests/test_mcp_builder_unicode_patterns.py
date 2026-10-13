"""Native JSON Schema patterns retain the pinned runtime Unicode property sets."""

import hashlib
import importlib
import re
import sys
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator

SCRIPTS = (
    Path(__file__).resolve().parents[1]
    / "universal_skills/agent-tools/mcp-builder/scripts"
)
sys.path.insert(0, str(SCRIPTS))
patterns = importlib.import_module("unicode_patterns")
EMAIL = (
    r"^[\p{L}\p{M}\p{N}.!#$%&'*+/=?^_`{|}~-]+@"
    r"[\p{L}\p{N}](?:[\p{L}\p{M}\p{N}-]{0,61}[\p{L}\p{M}\p{N}])?"
    r"(?:\.[\p{L}\p{N}](?:[\p{L}\p{M}\p{N}-]{0,61}[\p{L}\p{M}\p{N}])?)*$"
)


def test_range_data_has_reviewed_source_identity():
    source = (SCRIPTS / "unicode_properties.json").read_bytes()
    assert hashlib.sha256(source).hexdigest() == patterns.PROPERTY_DATA_SHA256
    assert patterns.UNICODE_VERSION == "18.0.0"


@pytest.mark.parametrize("category", ["L", "M", "N"])
def test_every_unicode_codepoint_matches_pinned_runtime(category):
    regex = pytest.importorskip("regex")
    assert regex.__version__ == "2026.9.29", "Use the reviewed Unicode 18 runtime"
    source = regex.compile(r"\p{" + category + "}").fullmatch
    native = re.compile(patterns.translate_pattern(r"\p{" + category + "}")).fullmatch
    for point in range(0x110000):
        character = chr(point)
        assert bool(native(character)) == bool(source(character)), hex(point)


@pytest.mark.parametrize(
    ("value", "accepted"),
    [
        ("fixture@example.invalid", True),
        ("école@例え.テスト", True),
        ("e\u0301@пример.рф", True),
        ("١٢٣@مثال.إختبار", True),
        ("𐐀@example.invalid", True),
        ("emoji😀@example.invalid", False),
        ("space here@example.invalid", False),
        ("bad@-example.invalid", False),
        ("bad@example-.invalid", False),
        ("bad\x00@example.invalid", False),
    ],
)
def test_unicode_email_keeps_positive_and_negative_semantics(value, accepted):
    regex = pytest.importorskip("regex")
    translated = patterns.translate_pattern(EMAIL)
    schema = {"type": "string", "pattern": translated}
    Draft202012Validator.check_schema(schema)
    actual = Draft202012Validator(schema).is_valid(value)
    assert actual == bool(regex.search(EMAIL, value)) == accepted


@pytest.mark.parametrize(
    "pattern",
    [
        r"\P{L}",
        r"\p{Script=Latin}",
        r"\p{Unknown}",
        r"[a-\p{L}]",
        r"[\p{L}-a]",
        "trailing\\",
    ],
)
def test_unsupported_properties_or_ranges_fail_closed(pattern):
    with pytest.raises(ValueError):
        patterns.translate_pattern(pattern)


def test_escaped_literal_and_existing_pattern_are_not_rewritten():
    for source in [r"^\\p\{L\}$", r"^[a-zA-Z0-9_\-.]+$", r"^\d{6}$"]:
        assert patterns.translate_pattern(source) == source


@pytest.mark.parametrize(
    "source",
    [
        r"^[^\p{L}]+$",
        r"^[-\p{L}]+$",
        r"^[\p{L}-]+$",
        r"^[]\p{L}]+$",
        r"^[\-\p{L}]+$",
        r"^[^]\p{L}]+$",
    ],
)
def test_outer_negation_and_literal_hyphen_keep_semantics(source):
    regex = pytest.importorskip("regex")
    translated = patterns.translate_pattern(source)
    for value in ["abc", "汉字", "-", "123", "😀", "a-", "A", "]", "A]", "]]"]:
        assert bool(re.search(translated, value)) == bool(regex.search(source, value))


def test_corrupted_property_table_is_rejected(monkeypatch):
    patterns.property_ranges.cache_clear()
    monkeypatch.setattr(patterns, "PROPERTY_DATA_SHA256", "0" * 64)
    with pytest.raises(ValueError, match="reviewed digest"):
        patterns.property_ranges()
    patterns.property_ranges.cache_clear()

"""Provider overlays are hash-bound monotonic corrections, never readiness grants."""

import copy
import hashlib
import importlib
import json
import sys
from pathlib import Path

import pytest

SCRIPTS = Path(__file__).parents[1] / "universal_skills/skills/mcp-builder/scripts"
sys.path.insert(0, str(SCRIPTS))
overlay_module = importlib.import_module("openapi_provider_overlay")


def _digest(value):
    data = (
        value
        if isinstance(value, bytes)
        else json.dumps(
            value, sort_keys=True, separators=(",", ":"), ensure_ascii=True
        ).encode()
    )
    return hashlib.sha256(data).hexdigest()


def _encoded(value):
    return (
        json.dumps(value, sort_keys=True, indent=2, ensure_ascii=True) + "\n"
    ).encode()


@pytest.fixture
def case(tmp_path):
    source = b"Required upload declaration\nExplicit public decorator\n"
    (tmp_path / "provider.txt").write_bytes(source)
    evidence = {
        "path": "provider.txt",
        "sha256": _digest(source),
        "source_commit": "1" * 40,
        "git_blob": hashlib.sha1(
            b"blob " + str(len(source)).encode() + b"\0" + source, usedforsecurity=False
        ).hexdigest(),
    }
    document = {
        "openapi": "3.1.1",
        "components": {
            "schemas": {
                "Upload": {
                    "type": "object",
                    "properties": {
                        "file": {
                            "type": "string",
                            "format": "binary",
                            "x-required": True,
                        },
                        "label": {"type": "string", "minLength": 1},
                    },
                    "required": ["label"],
                    "additionalProperties": False,
                }
            }
        },
        "paths": {
            "/upload": {"post": {"operationId": "upload"}},
            "/status": {"get": {"operationId": "status"}},
            "/declared": {"get": {"operationId": "declared", "security": []}},
        },
    }
    raw = _encoded(document)
    effective = copy.deepcopy(document)
    effective["components"]["schemas"]["Upload"]["required"].append("file")
    correction = {
        "op": "require-property",
        "schema_pointer": "/components/schemas/Upload",
        "property": "file",
        "before_sha256": _digest(document["components"]["schemas"]["Upload"]),
        "after_sha256": _digest(effective["components"]["schemas"]["Upload"]),
        "source_commit": evidence["source_commit"],
        "source_file": evidence["path"],
        "source_file_sha256": evidence["sha256"],
    }
    classification = {
        "operation_id": "upload",
        "method": "POST",
        "path": "/upload",
        "source_operation_sha256": _digest(document["paths"]["/upload"]["post"]),
        "reviewed_guard_classification": "explicit-public-decorator",
        "precondition_category": "provider-proof",
        "preconditions": "Provider enforces its documented proof before accepting the write.",
        "source_evidence": [
            {
                **evidence,
                "line_start": 1,
                "line_end": 2,
                "url": "https://example.test/source",
            }
        ],
    }
    overlay = {
        "version": 1,
        "raw_source_sha256": _digest(raw),
        "effective_source_sha256": _digest(_encoded(effective)),
        "evidence_files": [evidence],
        "corrections": [correction],
        "authorization_classifications": [classification],
    }
    return {"raw": raw, "overlay": overlay, "root": tmp_path, "effective": effective}


def _apply(case, *, expected=None):
    encoded = _encoded(case["overlay"])
    return overlay_module.apply_provider_overlay(
        case["raw"],
        encoded,
        expected_overlay_sha256=expected or _digest(encoded),
        evidence_root=case["root"],
    )


def test_additive_correction_and_auth_sidecar_preserve_source(case):
    before = copy.deepcopy(case)
    effective, receipt = _apply(case)
    assert effective == case["effective"]
    assert effective["paths"] == json.loads(case["raw"])["paths"]
    assert "security" not in effective
    assert "security" not in effective["paths"]["/upload"]["post"]
    assert receipt["remaining_unknown_operation_ids"] == ["status"]
    assert (
        receipt["authorization_classifications"]
        == case["overlay"]["authorization_classifications"]
    )
    assert not any(
        receipt[key] for key in ("ready", "live_verified", "transport_parity_verified")
    )
    assert case == before
    assert _apply(case) == (effective, receipt)


def test_generated_contract_revalidates_raw_source_and_overlay(case):
    converter = importlib.import_module("openapi_converter")
    parity = importlib.import_module("openapi_parity")
    root = case["root"]
    source, overlay_path, package = (
        root / "source.json",
        root / "overlay.json",
        root / "fixture",
    )
    source.write_bytes(case["raw"])
    overlay_path.write_bytes(_encoded(case["overlay"]))
    expected = _digest(overlay_path.read_bytes())
    generated = converter.generate(
        source,
        package,
        overlay_path=overlay_path,
        expected_overlay_sha256=expected,
        evidence_root=root,
    )
    assert (
        converter.generate(
            source,
            package,
            overlay_path=overlay_path,
            expected_overlay_sha256=expected,
            evidence_root=root,
        )
        == generated
    )
    contract = json.loads((package / "openapi_contract.json").read_text())
    options = dict(
        source_bytes=case["raw"],
        overlay_bytes=overlay_path.read_bytes(),
        expected_overlay_sha256=expected,
        evidence_root=root,
    )
    inventory = parity.verify_contract(
        json.loads(case["raw"]), contract, _digest(case["raw"]), **options
    )
    assert inventory["provider_overlay"]["remaining_unknown_operation_ids"] == [
        "status"
    ]
    with pytest.raises(ValueError, match="status"):
        parity.require_declared_authorization(inventory)
    with pytest.raises(ValueError):
        parity.verify_contract(json.loads(case["raw"]), contract, _digest(case["raw"]))
    (root / "provider.txt").write_text("stale evidence")
    with pytest.raises(ValueError, match="Evidence SHA256 mismatch"):
        parity.verify_contract(
            json.loads(case["raw"]), contract, _digest(case["raw"]), **options
        )


@pytest.mark.parametrize(
    "field,value",
    [
        ("raw_source_sha256", "0" * 64),
        ("effective_source_sha256", "0" * 64),
        ("version", True),
        ("version", 2),
        ("ready", True),
        ("corrections", None),
        ("authorization_classifications", {}),
        ("evidence_files", {}),
    ],
)
def test_invalid_overlay_binding_or_structure(case, field, value):
    case["overlay"][field] = value
    with pytest.raises(ValueError):
        _apply(case)


@pytest.mark.parametrize(
    "field,value",
    [
        ("op", "replace"),
        ("property", "new"),
        ("property", []),
        ("schema_pointer", {}),
        ("property", "label"),
        ("schema_pointer", "/paths/~1upload/post"),
        ("schema_pointer", "/components/schemas/Missing"),
        ("schema_pointer", "/components/schemas/Upload/properties/file"),
        ("before_sha256", "0" * 64),
        ("after_sha256", "0" * 64),
        ("source_commit", "2" * 40),
        ("source_file_sha256", "0" * 64),
        ("source_file", "missing.txt"),
        ("delete", "minLength"),
    ],
)
def test_non_monotonic_or_stale_corrections_refused(case, field, value):
    case["overlay"]["corrections"][0][field] = value
    with pytest.raises(ValueError):
        _apply(case)


@pytest.mark.parametrize(
    "field,value",
    [
        ("operation_id", "invented"),
        ("operation_id", "declared"),
        ("method", "GET"),
        ("path", "/wrong"),
        ("source_operation_sha256", "0" * 64),
        ("reviewed_guard_classification", "public"),
        ("preconditions", ""),
        ("preconditions", []),
        ("precondition_category", "*"),
        ("source_evidence", []),
        ("security", []),
    ],
)
def test_auth_classification_is_exact_and_never_an_auth_rewrite(case, field, value):
    case["overlay"]["authorization_classifications"][0][field] = value
    with pytest.raises(ValueError):
        _apply(case)


@pytest.mark.parametrize(
    "mistake",
    [
        "traversal",
        "absolute",
        "symlink",
        "directory_symlink",
        "digest",
        "git_blob",
        "missing",
        "lines",
        "duplicate_evidence",
        "duplicate_correction",
        "duplicate_auth",
        "duplicate_reference",
        "approval_hash",
    ],
)
def test_evidence_and_duplicate_guards(case, mistake):
    overlay, root = case["overlay"], case["root"]
    paths = {
        "traversal": "../provider.txt",
        "absolute": str(root / "provider.txt"),
        "missing": "missing.txt",
        "symlink": "alias.txt",
        "directory_symlink": "alias/provider.txt",
    }
    aliases = {
        "symlink": (root / "alias.txt", root / "provider.txt"),
        "directory_symlink": (root / "alias", root),
    }
    if mistake in aliases:
        link, target = aliases[mistake]
        link.symlink_to(target)
    if mistake in paths:
        overlay["evidence_files"][0]["path"] = paths[mistake]
    elif mistake in {"digest", "git_blob"}:
        overlay["evidence_files"][0][
            "sha256" if mistake == "digest" else "git_blob"
        ] = "0" * 64
    elif mistake == "lines":
        overlay["authorization_classifications"][0]["source_evidence"][0][
            "line_end"
        ] = 99
    elif mistake.startswith("duplicate"):
        keys = {
            "duplicate_evidence": "evidence_files",
            "duplicate_correction": "corrections",
            "duplicate_auth": "authorization_classifications",
        }
        target = (
            overlay[keys[mistake]]
            if mistake in keys
            else overlay["authorization_classifications"][0]["source_evidence"]
        )
        target.append(copy.deepcopy(target[0]))
    with pytest.raises(ValueError):
        _apply(case, expected="0" * 64 if mistake == "approval_hash" else None)


def test_duplicate_json_keys_and_omitted_auth_remain_fail_closed(case):
    data = b'{"version":1,"version":1}'
    with pytest.raises(ValueError, match="Duplicate JSON"):
        overlay_module.apply_provider_overlay(
            case["raw"],
            data,
            expected_overlay_sha256=_digest(data),
            evidence_root=case["root"],
        )
    case["overlay"]["authorization_classifications"] = []
    effective, receipt = _apply(case)
    assert receipt["remaining_unknown_operation_ids"] == ["status", "upload"]
    assert effective["paths"] == json.loads(case["raw"])["paths"]


@pytest.mark.parametrize(
    "target", [{"type": "string"}, {"$ref": "#/x"}, {"required": None}]
)
def test_unsupported_source_schema_is_not_repaired(case, target):
    document = json.loads(case["raw"])
    document["components"]["schemas"]["Upload"].update(target)
    case["raw"] = _encoded(document)
    case["overlay"]["raw_source_sha256"] = _digest(case["raw"])
    with pytest.raises(ValueError):
        _apply(case)


def test_shared_guard_evidence_is_verified_even_if_not_repeated(case):
    content = b"Shared authorization guard\n"
    (case["root"] / "guard.txt").write_bytes(content)
    case["overlay"]["evidence_files"].append(
        {"path": "guard.txt", "sha256": _digest(content)}
    )
    _, receipt = _apply(case)
    assert len(receipt["evidence_files"]) == 2
    (case["root"] / "guard.txt").write_bytes(b"Stale guard")
    with pytest.raises(ValueError, match="Evidence SHA256"):
        _apply(case)

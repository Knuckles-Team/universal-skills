"""Security regression coverage for Office ZIP extraction helpers."""

from __future__ import annotations

import importlib.util
import io
import stat
import zipfile
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[1]
OFFICE_SCRIPTS = (
    PROJECT_ROOT / "universal_skills" / "docs" / "document-tools" / "scripts"
)
SCRIPT_KINDS = ("docx_scripts", "pptx_scripts", "xlsx_scripts")
HELPER_PATHS = tuple(
    OFFICE_SCRIPTS / kind / "office" / "safe_zip.py" for kind in SCRIPT_KINDS
)
XML_HELPER_PATHS = tuple(
    OFFICE_SCRIPTS / kind / "office" / "safe_xml.py" for kind in SCRIPT_KINDS
)
LXML_HELPER_PATHS = tuple(
    OFFICE_SCRIPTS / kind / "office" / "safe_lxml.py" for kind in SCRIPT_KINDS
)
ROUTED_FILES = tuple(
    OFFICE_SCRIPTS / kind / "office" / relative_path
    for kind in SCRIPT_KINDS
    for relative_path in (
        "unpack.py",
        "validate.py",
        "validators/base.py",
        "validators/docx.py",
        "validators/redlining.py",
    )
)


@pytest.fixture(params=HELPER_PATHS, ids=SCRIPT_KINDS)
def safe_zip_module(request):
    """Load each standalone Office helper without changing import search paths."""

    helper_path = request.param
    module_name = f"_test_{helper_path.parent.parent.name}_safe_zip"
    spec = importlib.util.spec_from_file_location(module_name, helper_path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.fixture(params=XML_HELPER_PATHS, ids=SCRIPT_KINDS)
def safe_xml_module(request):
    helper_path = request.param
    module_name = f"_test_{helper_path.parent.parent.name}_safe_xml"
    spec = importlib.util.spec_from_file_location(module_name, helper_path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _write_archive(
    archive_path: Path,
    members: tuple[tuple[str, bytes], ...],
    *,
    compression: int = zipfile.ZIP_STORED,
) -> None:
    with zipfile.ZipFile(archive_path, "w", compression=compression) as archive:
        for name, content in members:
            archive.writestr(name, content)


@pytest.mark.parametrize(
    "malicious_name",
    ("../escape.xml", "..\\escape.xml", "/absolute.xml", "C:\\escape.xml"),
)
def test_traversal_is_rejected_before_any_file_is_written(
    safe_zip_module,
    tmp_path,
    malicious_name,
):
    archive_path = tmp_path / "traversal.docx"
    _write_archive(
        archive_path,
        (
            ("word/document.xml", b"must be rolled back"),
            (malicious_name, b"escaped"),
        ),
    )
    destination = tmp_path / "unpacked"

    with zipfile.ZipFile(archive_path) as archive:
        with pytest.raises(safe_zip_module.UnsafeArchiveError, match="path"):
            safe_zip_module.safe_extract_zip(archive, destination)

    assert not (destination / "word" / "document.xml").exists()
    assert not (tmp_path / "escape.xml").exists()


def test_archive_symlink_is_rejected(safe_zip_module, tmp_path):
    archive_path = tmp_path / "symlink.docx"
    link = zipfile.ZipInfo("word/document.xml")
    link.create_system = 3
    link.external_attr = (stat.S_IFLNK | 0o777) << 16
    with zipfile.ZipFile(archive_path, "w") as archive:
        archive.writestr(link, "../../outside.xml")

    destination = tmp_path / "unpacked"
    with zipfile.ZipFile(archive_path) as archive:
        with pytest.raises(safe_zip_module.UnsafeArchiveError, match="special"):
            safe_zip_module.safe_extract_zip(archive, destination)

    assert not destination.exists()


def test_high_ratio_zip_bomb_is_rejected(safe_zip_module, tmp_path):
    archive_path = tmp_path / "bomb.docx"
    _write_archive(
        archive_path,
        (("word/document.xml", b"\x00" * (8 * 1024 * 1024)),),
        compression=zipfile.ZIP_DEFLATED,
    )

    destination = tmp_path / "unpacked"
    with zipfile.ZipFile(archive_path) as archive:
        with pytest.raises(safe_zip_module.UnsafeArchiveError, match="compression"):
            safe_zip_module.safe_extract_zip(archive, destination)

    assert not destination.exists()


@pytest.mark.parametrize(
    "invalid_name",
    (
        "word/CON.xml",
        "word/LPT¹.txt",
        "word/trailing.",
        "word/has<mark>.xml",
    ),
)
def test_windows_unsafe_names_are_rejected(
    safe_zip_module,
    tmp_path,
    invalid_name,
):
    archive_path = tmp_path / "windows-name.docx"
    _write_archive(archive_path, ((invalid_name, b"content"),))

    with zipfile.ZipFile(archive_path) as archive:
        with pytest.raises(safe_zip_module.UnsafeArchiveError, match="path"):
            safe_zip_module.safe_extract_zip(archive, tmp_path / "unpacked")


def test_windows_casefold_collision_is_rejected(safe_zip_module, tmp_path):
    archive_path = tmp_path / "case-collision.docx"
    _write_archive(
        archive_path,
        (
            ("word/File.xml", b"first"),
            ("word/file.xml", b"second"),
        ),
    )

    with zipfile.ZipFile(archive_path) as archive:
        with pytest.raises(safe_zip_module.UnsafeArchiveError, match="colliding"):
            safe_zip_module.safe_extract_zip(archive, tmp_path / "unpacked")


def test_valid_office_archive_extracts(safe_zip_module, tmp_path):
    archive_path = tmp_path / "valid.docx"
    members = (
        ("[Content_Types].xml", b"<Types/>"),
        ("_rels/.rels", b"<Relationships/>"),
        ("word/document.xml", b"<document>safe</document>"),
    )
    _write_archive(archive_path, members, compression=zipfile.ZIP_DEFLATED)

    destination = tmp_path / "unpacked"
    with zipfile.ZipFile(archive_path) as archive:
        safe_zip_module.safe_extract_zip(archive, destination)

    for name, content in members:
        assert (destination / name).read_bytes() == content


@pytest.mark.parametrize(
    "script_path",
    ROUTED_FILES,
    ids=lambda path: "/".join(path.parts[-4:]),
)
def test_production_extractors_use_safe_helper(script_path):
    source = script_path.read_text(encoding="utf-8")

    assert ".extractall(" not in source
    assert "safe_extract_zip(" in source


def test_office_xml_rejects_dtd_and_entities(safe_xml_module):
    payload = (
        b'<!DOCTYPE root [<!ENTITY xxe SYSTEM "file:///ignored">]><root>&xxe;</root>'
    )
    with pytest.raises(safe_xml_module.SafeXmlError, match="invalid"):
        safe_xml_module.parse_xml(io.BytesIO(payload))


def test_office_xml_rejects_excessive_depth(safe_xml_module, monkeypatch):
    monkeypatch.setattr(safe_xml_module, "MAX_XML_DEPTH", 3)
    with pytest.raises(safe_xml_module.SafeXmlError, match="structure"):
        safe_xml_module.parse_xml(io.BytesIO(b"<a><b><c><d/></c></b></a>"))


def test_office_xml_rejects_oversize_stream(safe_xml_module, monkeypatch):
    monkeypatch.setattr(safe_xml_module, "MAX_XML_BYTES", 8)
    with pytest.raises(safe_xml_module.SafeXmlError, match="size"):
        safe_xml_module.parse_xml(io.BytesIO(b"<root>toolarge</root>"))


@pytest.mark.parametrize("helper_path", LXML_HELPER_PATHS, ids=SCRIPT_KINDS)
def test_lxml_defaults_disable_dtd_entities_network_and_huge_trees(helper_path):
    source = helper_path.read_text(encoding="utf-8")
    for security_setting in (
        "resolve_entities=False",
        "load_dtd=False",
        "no_network=True",
        "recover=False",
        "huge_tree=False",
    ):
        assert security_setting in source

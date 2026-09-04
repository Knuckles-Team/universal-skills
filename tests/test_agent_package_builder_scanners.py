"""Regression coverage for the generated structural scanner profile."""

import importlib.util
import json
import subprocess
from pathlib import Path

import pytest


SCAFFOLD = (
    Path(__file__).parents[1]
    / "universal_skills"
    / "agent-tools"
    / "agent-package-builder"
    / "scripts"
    / "scaffold_package.py"
)


def _load_scaffold():
    spec = importlib.util.spec_from_file_location("_scanner_scaffold", SCAFFOLD)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


SCANNER = (
    Path(__file__).parents[1]
    / "universal_skills"
    / "agent-tools"
    / "agent-package-builder"
    / "scripts"
    / "templates"
    / "check_scanners.py"
)


def _load_scanner():
    spec = importlib.util.spec_from_file_location("_generated_check_scanners", SCANNER)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _dupehound_config():
    return {
        "dupehound_version": "0.1.2",
        "dupehound_threshold": 0.85,
        "dupehound_min_tokens": 40,
    }


def test_scanner_profile_is_pinned_and_split_by_cost():
    module = _load_scaffold()
    pyproject = module.PYPROJECT_TOML
    pre_commit = module.PRECOMMIT_CONFIG

    for version in (
        'cccc_version = "1.6.0"',
        'kiss_version = "0.4.10"',
        'dupehound_version = "0.1.2"',
        'jscpd_version = "5.0.16"',
        'import_linter_version = "2.14"',
    ):
        assert version in pyproject
    assert "entry: bash scripts/run_kiss.sh" in pre_commit
    assert "entry: python3 scripts/check_scanners.py cccc" in pre_commit
    assert "entry: python3 scripts/check_scanners.py dupehound" in pre_commit
    assert "entry: python3 scripts/check_scanners.py import-linter" in pre_commit
    assert "stages: [pre-push, manual]" in pre_commit
    assert "scanner-jscpd-delta" in pre_commit
    assert "scanner-jscpd-census" in pre_commit
    assert "Python is included" not in pre_commit
    assert "jscpd intentionally scans Python" in pre_commit


def test_scanner_profile_accepts_two_component_import_linter_release(tmp_path):
    scanner = _load_scanner()
    pyproject = tmp_path / "pyproject.toml"
    pyproject.write_text(
        """
[tool.agent_utilities.scanners]
cccc_version = "1.6.0"
kiss_version = "0.4.10"
dupehound_version = "0.1.2"
jscpd_version = "5.0.16"
import_linter_version = "2.14"
cccc_max_cyclomatic = 10
cccc_max_cognitive = 15
dupehound_threshold = 0.85
dupehound_min_tokens = 40
jscpd_min_tokens = 50
jscpd_min_lines = 5
jscpd_mode = "mild"
""",
        encoding="utf-8",
    )
    scanner.PYPROJECT = pyproject

    assert scanner._scanner_config()["import_linter_version"] == "2.14"


def test_scanner_policy_templates_are_fail_closed_and_exclude_only_non_product_data():
    module = _load_scaffold()
    assert "max-cyclomatic = 10" in module.CCCC_CONFIG
    assert "max-cognitive = 15" in module.CCCC_CONFIG
    assert "duplication_enabled     = true" in module.KISS_CONFIG
    assert "root_package = {pkg_dir}" in module.IMPORTLINTER_CONFIG
    assert "[importlinter:api-does-not-import-runtimes]" in module.IMPORTLINTER_CONFIG
    assert "[importlinter:mcp-does-not-import-agent]" in module.IMPORTLINTER_CONFIG
    scanner = (
        Path(__file__).parents[1]
        / "universal_skills"
        / "agent-tools"
        / "agent-package-builder"
        / "scripts"
        / "templates"
        / "check_scanners.py"
    ).read_text(encoding="utf-8")
    assert "never install scanners" in scanner
    assert '".py"' in scanner
    assert '"generated"' in scanner
    assert '"fixtures"' in scanner
    assert "PRE_COMMIT_FROM_REF" in scanner
    assert "PRE_COMMIT_TO_REF" in scanner
    assert "JSCPD_CONFIG_NAMES" in scanner
    assert "hashlib.sha256" in scanner


def test_scaffold_emits_scanner_files(tmp_path):
    module = _load_scaffold()
    module.scaffold("scanner-provider", output_dir=str(tmp_path))
    root = tmp_path / "scanner-provider"

    for relative in (
        ".cccc.toml",
        ".kiss/kiss.toml",
        ".importlinter",
        "scripts/check_scanners.py",
        "scripts/run_kiss.sh",
    ):
        assert (root / relative).is_file(), relative


def test_cccc_regression_checks_cyclomatic_and_cognitive_axes_independently():
    scanner = _load_scanner()

    assert scanner._cccc_regressed((7, 16), (8, 10))
    assert scanner._cccc_regressed((9, 10), (8, 10))
    assert not scanner._cccc_regressed((8, 10), (8, 10))


def test_cccc_uses_the_checked_in_policy_path(monkeypatch, tmp_path):
    scanner = _load_scanner()
    source = tmp_path / "module.py"
    source.write_text("def answer():\n    return 42\n", encoding="utf-8")
    captured = {}

    def fake_run(command, **_kwargs):
        captured["command"] = command
        return subprocess.CompletedProcess(
            command,
            0,
            json.dumps({"files": [{"functions": []}]}),
            "",
        )

    monkeypatch.setattr(scanner.subprocess, "run", fake_run)

    assert scanner._cccc_rows("/usr/local/bin/cccc", source, "module.py") == {}
    command = captured["command"]
    assert command[0:3] == ["/usr/local/bin/cccc", "--config", str(scanner.CCCC_CONFIG)]


def test_cccc_parse_errors_are_not_a_false_green(monkeypatch, tmp_path):
    scanner = _load_scanner()
    source = tmp_path / "broken.py"
    source.write_text("def broken(:\n", encoding="utf-8")

    def fake_run(command, **_kwargs):
        return subprocess.CompletedProcess(
            command,
            0,
            json.dumps(
                {
                    "files": [
                        {
                            "functions": [],
                            "parse_errors": ["syntax error at line 1"],
                        }
                    ]
                }
            ),
            "",
        )

    monkeypatch.setattr(scanner.subprocess, "run", fake_run)

    with pytest.raises(scanner.ScannerError, match="could not parse"):
        scanner._cccc_rows("/usr/local/bin/cccc", source, "broken.py")


def test_dispatch_exposes_census_modes(monkeypatch):
    scanner = _load_scanner()
    monkeypatch.setattr(scanner, "_scanner_config", lambda: {"profile": True})
    monkeypatch.setattr(scanner, "_run_cccc_census", lambda config: 11)
    monkeypatch.setattr(scanner, "_run_kiss_census", lambda config: 12)

    assert scanner._dispatch("cccc-census") == 11
    assert scanner._dispatch("kiss-census") == 12


def test_reference_blob_treats_missing_path_as_new_file(monkeypatch):
    scanner = _load_scanner()
    calls = []

    def fake_run(command, **_kwargs):
        calls.append(command)
        if command[:3] == ["git", "cat-file", "-e"]:
            return subprocess.CompletedProcess(command, 128, b"", b"missing path")
        if command[:3] == ["git", "ls-tree", "-r"]:
            return subprocess.CompletedProcess(command, 0, b"", b"")
        raise AssertionError(command)

    monkeypatch.setattr(scanner.subprocess, "run", fake_run)

    assert scanner._reference_blob("HEAD", "new.py") is None
    assert calls[1][:3] == ["git", "ls-tree", "-r"]


def test_reference_blob_does_not_hide_invalid_revision(monkeypatch):
    scanner = _load_scanner()

    def fake_run(command, **_kwargs):
        if command[:3] == ["git", "cat-file", "-e"]:
            return subprocess.CompletedProcess(command, 128, b"", b"bad revision")
        if command[:3] == ["git", "ls-tree", "-r"]:
            return subprocess.CompletedProcess(command, 128, b"", b"bad revision")
        raise AssertionError(command)

    monkeypatch.setattr(scanner.subprocess, "run", fake_run)

    with pytest.raises(scanner.ScannerError):
        scanner._reference_blob("not-a-revision", "new.py")


def test_deleted_source_has_no_post_change_cccc_blob(monkeypatch, tmp_path):
    scanner = _load_scanner()
    monkeypatch.setattr(scanner, "ROOT", tmp_path)

    def fake_run(command, **_kwargs):
        assert command[:3] == ["git", "show", ":gone.py"]
        return subprocess.CompletedProcess(command, 128, b"", b"deleted")

    monkeypatch.setattr(scanner.subprocess, "run", fake_run)

    assert scanner._materialise_staged("gone.py", tmp_path / "after") is None


@pytest.mark.parametrize(
    "field,value",
    (
        ("name", ""),
        ("original_name", 42),
        ("line", 0),
        ("original_line", -1),
        ("similarity", 1.01),
        ("similarity", float("nan")),
    ),
)
def test_dupehound_findings_reject_malformed_values(field, value):
    scanner = _load_scanner()
    finding = {
        "file": "src/current.py",
        "line": 10,
        "name": "current",
        "similarity": 0.9,
        "original_file": "src/original.py",
        "original_line": 20,
        "original_name": "original",
    }
    finding[field] = value

    with pytest.raises(scanner.ScannerError):
        scanner._dupehound_findings({"schema_version": 1, "findings": [finding]})


def test_dupehound_findings_reject_boolean_schema_version():
    scanner = _load_scanner()

    with pytest.raises(scanner.ScannerError):
        scanner._dupehound_findings({"schema_version": True, "findings": []})


def test_dupehound_command_has_tests_and_complete_exclusions(monkeypatch):
    scanner = _load_scanner()
    captured = {}

    monkeypatch.setattr(scanner, "_source_paths", lambda paths: ["src/main.py"])
    monkeypatch.setattr(scanner, "_tool", lambda *args: "/usr/local/bin/dupehound")
    monkeypatch.setattr(scanner, "_verify_version", lambda *args: None)

    def fake_run(command, **_kwargs):
        captured["command"] = command
        return subprocess.CompletedProcess(
            command,
            0,
            json.dumps({"schema_version": 1, "findings": []}),
            "",
        )

    monkeypatch.setattr(scanner.subprocess, "run", fake_run)

    assert scanner._run_dupehound(_dupehound_config(), ["src/main.py"]) == 0
    command = captured["command"]
    assert "--include-tests" in command
    for pattern in scanner.EXCLUDED_GLOBS:
        assert pattern in command


def test_version_check_requires_tool_identity(monkeypatch):
    scanner = _load_scanner()

    def fake_run(command, **_kwargs):
        return subprocess.CompletedProcess(command, 0, "cpd 5.0.16\n", "")

    monkeypatch.setattr(scanner.subprocess, "run", fake_run)
    scanner._verify_version("/usr/local/bin/jscpd", "5.0.16", "jscpd")

    def wrong_identity(command, **_kwargs):
        return subprocess.CompletedProcess(command, 0, "jscpd 5.0.16\n", "")

    monkeypatch.setattr(scanner.subprocess, "run", wrong_identity)
    with pytest.raises(scanner.ScannerError):
        scanner._verify_version("/usr/local/bin/jscpd", "5.0.16", "jscpd")


def test_configured_scanner_path_does_not_fall_back(monkeypatch, tmp_path):
    scanner = _load_scanner()
    missing = tmp_path / "missing-dupehound"
    monkeypatch.setenv("DUPEHOUND_BIN", str(missing))
    monkeypatch.setattr(scanner.shutil, "which", lambda name: "/usr/bin/dupehound")

    with pytest.raises(scanner.ScannerError):
        scanner._tool("dupehound", "DUPEHOUND_BIN", _dupehound_config())


def test_changed_paths_include_deletions(monkeypatch):
    scanner = _load_scanner()
    calls = []

    def fake_git(*args):
        calls.append(args)
        if args[0] == "diff" and "--cached" in args:
            return ""
        if args[0] == "diff":
            return "gone.py\n"
        return ""

    monkeypatch.setattr(scanner, "_git", fake_git)

    assert scanner.changed_paths() == ["gone.py"]
    assert any("--diff-filter=ACMRD" in args for args in calls)


def test_kiss_wrapper_validates_policy_and_skips_its_own_scanner():
    kiss = (SCANNER.parent / "run_kiss.sh").read_text(encoding="utf-8")

    assert "--diff-filter=ACMRD" in kiss
    assert "scripts/check_scanners.py|*/scripts/check_scanners.py" in kiss
    assert "global.min_similarity must be a finite number" in kiss
    assert "python.{key} must be a positive integer" in kiss
    assert "KISS_BIN points to a missing or non-executable scanner" in kiss

"""Regression coverage for scanner distribution and scaffold reruns."""

import importlib.util
from pathlib import Path


SCAFFOLD = (
    Path(__file__).parents[1]
    / "universal_skills"
    / "agent-tools"
    / "agent-package-builder"
    / "scripts"
    / "scaffold_package.py"
)
# The fleet's kiss fork build (upstream 0.4.12 + inline-module fix, dsweet99/kiss#48).
KISS_FORK_REV = "7f1c6785697d3fe9a41ceb8b8e5d0f615fb1f3d9"


def _load_scaffold():
    spec = importlib.util.spec_from_file_location(
        "_scanner_distribution_scaffold", SCAFFOLD
    )
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_scanner_census_modes_and_ci_provisioning_are_generated():
    module = _load_scaffold()

    for mode in ("kiss-census", "cccc-census"):
        assert f"scanner-{mode}" in module.PRECOMMIT_CONFIG
        assert f"check_scanners.py {mode}" in module.PRECOMMIT_CONFIG
    assert (
        "scanner-kiss-census --all-files --hook-stage pre-push" in module.SCANNER_CI_YML
    )
    assert "stages: [pre-push, manual]" in module.PRECOMMIT_CONFIG

    workflow = module.SCANNER_CI_YML
    for version in ("1.6.0", "0.4.12", "0.1.2", "5.0.16", "2.14"):
        assert version in workflow
    assert "cargo install cccc-cli --version 1.6.0 --locked" in workflow
    assert (
        "cargo install --locked --git https://github.com/Knucklessg1/kiss "
        f"--rev {KISS_FORK_REV} kiss-ai" in workflow
    )
    assert "check --lang rust .)" in workflow, "kiss fork-build probe missing"
    assert "cargo install dupehound --version 0.1.2 --locked" in workflow
    assert "npm install --global jscpd@5.0.16" in workflow
    assert "import-linter==2.14" in workflow
    assert 'echo "CCCC_BIN=$scanner_bin/cccc"' in workflow
    assert 'echo "JSCPD_BIN=$(npm prefix --global)/bin/jscpd"' in workflow
    assert 'IMPORT_LINTER_BIN={scripts / "lint-imports"}' in workflow
    assert "scanner-kiss-census --all-files --hook-stage pre-push" in workflow
    assert "scanner-cccc-census --all-files --hook-stage pre-push" in workflow


def test_source_distribution_contract_carries_scanner_surface():
    module = _load_scaffold()
    manifest = module.MANIFEST_IN

    for path in (
        ".pre-commit-config.yaml",
        ".cccc.toml",
        ".kiss/kiss.toml",
        ".importlinter",
        "scripts/check_scanners.py",
        "scripts/run_kiss.sh",
        ".github/workflows/scanners.yml",
    ):
        assert f"include {path}" in manifest
    assert "source distributions" in manifest
    assert "runtime wheel/package data" in manifest


def test_scaffold_rerun_preserves_project_owned_scanner_files(tmp_path):
    module = _load_scaffold()
    module.scaffold("scanner-provider", output_dir=str(tmp_path))
    root = tmp_path / "scanner-provider"
    assert (root / ".github/workflows/scanners.yml").is_file()

    precommit = root / ".pre-commit-config.yaml"
    wrapper = root / "scripts/check_scanners.py"
    precommit.write_text(
        precommit.read_text(encoding="utf-8") + "\n# operator-owned\n",
        encoding="utf-8",
    )
    wrapper.write_text(
        wrapper.read_text(encoding="utf-8") + "\n# operator-owned\n",
        encoding="utf-8",
    )
    expected_precommit = precommit.read_bytes()
    expected_wrapper = wrapper.read_bytes()

    module.scaffold("scanner-provider", output_dir=str(tmp_path))

    assert precommit.read_bytes() == expected_precommit
    assert wrapper.read_bytes() == expected_wrapper

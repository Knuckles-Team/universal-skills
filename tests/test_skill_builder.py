import importlib.util
import sys
import zipfile
from pathlib import Path

import pytest
import yaml


def _load_script(module_name: str, script_name: str):
    script_path = (
        Path(__file__).resolve().parent.parent
        / "universal_skills"
        / "core"
        / "skill-builder"
        / "scripts"
        / script_name
    )
    spec = importlib.util.spec_from_file_location(module_name, script_path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


init_module = _load_script("skill_builder_init", "init_skill.py")
package_module = _load_script("skill_builder_package", "package_skill.py")


def _domain_path(tmp_path: Path, domain: str = "docs") -> Path:
    path = tmp_path / "universal_skills" / domain
    path.mkdir(parents=True)
    return path


def _description() -> str:
    return (
        "Summarize one report into an evidence-backed brief. "
        "Use when the user provides a report and asks for its key findings."
    )


@pytest.mark.parametrize(
    "relative_path",
    [
        Path("core/skill-builder"),
        Path("agent-tools/skill-workflow-builder"),
    ],
)
def test_builder_meta_skills_satisfy_atomic_contract(relative_path):
    skill_path = (
        Path(__file__).resolve().parent.parent / "universal_skills" / relative_path
    )

    assert init_module.validate_atomic_skill(skill_path) == []


def test_init_skill_creates_only_requested_resources(tmp_path):
    domain_path = _domain_path(tmp_path)

    skill_dir = init_module.init_skill(
        "report-summarizer",
        domain_path,
        _description(),
        resources="references",
    )

    assert skill_dir is not None
    assert {path.name for path in skill_dir.iterdir()} == {"SKILL.md", "references"}
    assert not any((skill_dir / "references").iterdir())
    assert init_module.validate_atomic_skill(skill_dir) == []

    text = (skill_dir / "SKILL.md").read_text(encoding="utf-8")
    frontmatter = yaml.safe_load(text.split("---", 2)[1])
    assert frontmatter["name"] == "report-summarizer"
    assert frontmatter["domain"] == "docs"
    assert frontmatter["skill_type"] == "skill"
    assert frontmatter["description"] == _description()
    assert "depends_on" not in text
    assert "ACTION REQUIRED" not in text


def test_init_skill_without_resources_creates_only_skill_md(tmp_path):
    skill_dir = init_module.init_skill(
        "report-summarizer",
        _domain_path(tmp_path),
        _description(),
    )

    assert skill_dir is not None
    assert [path.name for path in skill_dir.iterdir()] == ["SKILL.md"]


def test_init_skill_rejects_invalid_name_domain_and_description(tmp_path):
    atomic_domain = _domain_path(tmp_path)
    workflow_domain = _domain_path(tmp_path, "docs-workflows")

    assert (
        init_module.init_skill("Report_Summarizer", atomic_domain, _description())
        is None
    )
    assert (
        init_module.init_skill(
            "report-summarizer",
            atomic_domain,
            "Summarize one report.",
        )
        is None
    )
    assert (
        init_module.init_skill(
            "report-summarizer",
            workflow_domain,
            _description(),
        )
        is None
    )


def test_atomic_validator_rejects_workflow_syntax(tmp_path):
    skill_dir = init_module.init_skill(
        "report-summarizer",
        _domain_path(tmp_path),
        _description(),
    )
    skill_md = skill_dir / "SKILL.md"
    skill_md.write_text(
        skill_md.read_text(encoding="utf-8")
        + "\n### Step 1: report-reader [depends_on: none]\n",
        encoding="utf-8",
    )

    errors = init_module.validate_atomic_skill(skill_dir)

    assert any("numbered workflow steps" in error for error in errors)


def test_package_skill_validates_then_writes_archive(tmp_path):
    skill_dir = init_module.init_skill(
        "report-summarizer",
        _domain_path(tmp_path),
        _description(),
        resources="scripts",
    )
    helper = skill_dir / "scripts" / "summarize.py"
    helper.write_text("print('summary')\n", encoding="utf-8")

    archive = package_module.package_skill(skill_dir, tmp_path / "dist")

    assert archive is not None
    with zipfile.ZipFile(archive) as zip_file:
        assert set(zip_file.namelist()) == {
            "report-summarizer/SKILL.md",
            "report-summarizer/scripts/summarize.py",
        }


def test_package_skill_rejects_sensitive_files(tmp_path):
    skill_dir = init_module.init_skill(
        "report-summarizer",
        _domain_path(tmp_path),
        _description(),
        resources="scripts",
    )
    (skill_dir / "scripts" / ".env").write_text("TOKEN=secret\n", encoding="utf-8")

    assert package_module.package_skill(skill_dir, tmp_path / "dist") is None
    assert not (tmp_path / "dist" / "report-summarizer.skill").exists()

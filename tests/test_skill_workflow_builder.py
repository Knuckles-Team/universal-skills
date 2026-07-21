import importlib.util
import sys
from pathlib import Path

import pytest
import yaml


script_path = (
    Path(__file__).resolve().parent.parent
    / "universal_skills"
    / "agent-tools"
    / "skill-workflow-builder"
    / "scripts"
    / "build_workflow.py"
)
spec = importlib.util.spec_from_file_location("build_workflow", script_path)
build_workflow = importlib.util.module_from_spec(spec)
sys.modules["build_workflow"] = build_workflow
spec.loader.exec_module(build_workflow)

validate_steps_dag = build_workflow.validate_steps_dag
scaffold_workflow_files = build_workflow.scaffold_workflow_files
parse_workflow_skill = build_workflow.parse_workflow_skill
validate_workflow_files = build_workflow.validate_workflow_files


def _catalog(tmp_path: Path) -> Path:
    root = tmp_path / "universal_skills"
    root.mkdir()
    return root


def _write_atomic_skill(root: Path, domain: str, name: str) -> None:
    skill_dir = root / domain / name
    skill_dir.mkdir(parents=True)
    (skill_dir / "SKILL.md").write_text(
        "\n".join(
            [
                "---",
                f"name: {name}",
                f"domain: {domain}",
                "skill_type: skill",
                "description: >-",
                f"  Perform the {name} capability. Use when this capability is required.",
                "---",
                f"# {name}",
                "",
            ]
        ),
        encoding="utf-8",
    )


def _description() -> str:
    return (
        "Turn a feature specification into an implementation-ready task plan. "
        "Use when the user asks to decompose an approved specification."
    )


def _steps() -> list[dict]:
    return [
        {
            "step": 1,
            "skill": "spec-generator",
            "agent": "planning-specialist",
            "depends_on": [],
        },
        {
            "step": 2,
            "skill": "task-planner",
            "agent": "planning-specialist",
            "depends_on": ["spec-generator"],
        },
    ]


def test_validate_steps_dag_valid():
    is_valid, errors = validate_steps_dag(_steps())

    assert is_valid is True
    assert errors == []


def test_validate_steps_dag_circular():
    steps = [
        {"step": 1, "skill": "first-skill", "depends_on": ["Step 2"]},
        {"step": 2, "skill": "second-skill", "depends_on": ["Step 1"]},
    ]

    is_valid, errors = validate_steps_dag(steps)

    assert is_valid is False
    assert any("circular dependency" in error for error in errors)


def test_validate_steps_dag_missing_reference():
    steps = [{"step": 1, "skill": "first-skill", "depends_on": ["Step 5"]}]

    is_valid, errors = validate_steps_dag(steps)

    assert is_valid is False
    assert any("unknown step 'Step 5'" in error for error in errors)


def test_scaffold_emits_complete_valid_workflow(tmp_path):
    root = _catalog(tmp_path)
    _write_atomic_skill(root, "development", "spec-generator")
    _write_atomic_skill(root, "development", "task-planner")

    destination = scaffold_workflow_files(
        workflow_name="feature-planning",
        domain="development-workflows",
        description=_description(),
        tags=["planning"],
        requires=[],
        steps=_steps(),
        root_path=root,
    )

    assert destination is not None
    skill_md = destination / "SKILL.md"
    team_path = destination / "references" / "team.yaml"
    assert skill_md.is_file()
    assert team_path.is_file()
    assert validate_workflow_files(skill_md, root) == []

    parsed = parse_workflow_skill(skill_md)
    team = yaml.safe_load(team_path.read_text(encoding="utf-8"))
    assert parsed["name"] == "feature-planning"
    assert parsed["domain"] == "development-workflows"
    assert parsed["frontmatter"]["team_config"] == team
    assert team["specialist_ids"] == ["planning-specialist"]
    assert team["tool_assignments"] == {
        "planning-specialist": ["spec-generator", "task-planner"]
    }
    assert parsed["steps"][0]["depends_on"] == []
    assert parsed["steps"][1]["depends_on"] == ["spec-generator"]

    text = skill_md.read_text(encoding="utf-8")
    assert "### Step 1: spec-generator [depends_on: none]" in text
    assert "## Execution" in text
    assert "After level 0" in text
    assert build_workflow.DELEGATION_FOOTER in text
    assert "Expected:" not in text


def test_scaffolded_workflow_compiles_with_runtime_compiler(tmp_path):
    compiler = pytest.importorskip(
        "agent_utilities.workflows.skill_compiler"
    ).SkillCompiler
    root = _catalog(tmp_path)
    _write_atomic_skill(root, "development", "spec-generator")
    _write_atomic_skill(root, "development", "task-planner")
    destination = scaffold_workflow_files(
        "feature-planning",
        "development-workflows",
        _description(),
        [],
        [],
        _steps(),
        root,
    )

    plan = compiler.compile(destination)

    assert [step.node_id for step in plan.steps] == [
        "spec-generator",
        "task-planner",
    ]
    assert plan.steps[0].depends_on == []
    assert plan.steps[1].depends_on == ["spec-generator"]


def test_scaffold_accepts_one_explicit_mcp_tool(tmp_path):
    root = _catalog(tmp_path)
    steps = [
        {
            "step": 1,
            "id": "load-issue",
            "mcp_tool": "github.get_issue",
            "agent": "repository-specialist",
            "depends_on": [],
        }
    ]

    destination = scaffold_workflow_files(
        "issue-loader",
        "development-workflows",
        "Load one repository issue for downstream planning. Use when a workflow needs authoritative issue details.",
        ["issues"],
        ["github-agent"],
        steps,
        root,
    )

    assert destination is not None
    assert validate_workflow_files(destination / "SKILL.md", root) == []
    text = (destination / "SKILL.md").read_text(encoding="utf-8")
    assert "**MCP Tool**: `github.get_issue`" in text


def test_scaffold_accepts_package_owned_skill_with_declared_requirement(tmp_path):
    root = _catalog(tmp_path)
    steps = [
        {
            "step": 1,
            "skill": "scholarx-operations",
            "package": "scholarx",
            "agent": "research-specialist",
            "depends_on": [],
        }
    ]

    destination = scaffold_workflow_files(
        "paper-search",
        "research-workflows",
        "Search an external scholarly index through its owning package. Use when a research workflow needs paper metadata.",
        ["research"],
        ["scholarx"],
        steps,
        root,
    )

    assert destination is not None
    assert validate_workflow_files(destination / "SKILL.md", root) == []
    text = (destination / "SKILL.md").read_text(encoding="utf-8")
    assert "**Skill**: `scholarx-operations`" in text
    assert "**Package**: `scholarx`" in text


def test_scaffold_rejects_unowned_external_skill(tmp_path):
    root = _catalog(tmp_path)
    steps = [
        {
            "step": 1,
            "skill": "scholarx-operations",
            "package": "scholarx",
            "depends_on": [],
        }
    ]

    assert (
        scaffold_workflow_files(
            "paper-search",
            "research-workflows",
            "Search an external scholarly index. Use when paper metadata is needed.",
            [],
            [],
            steps,
            root,
        )
        is None
    )


def test_scaffold_rejects_missing_atomic_skill_without_writing(tmp_path):
    root = _catalog(tmp_path)

    destination = scaffold_workflow_files(
        "feature-planning",
        "development-workflows",
        _description(),
        [],
        [],
        _steps(),
        root,
    )

    assert destination is None
    assert not (root / "development-workflows" / "feature-planning").exists()


def test_scaffold_rejects_inline_logic_and_invalid_domain(tmp_path):
    root = _catalog(tmp_path)
    _write_atomic_skill(root, "development", "spec-generator")
    steps = [
        {
            "step": 1,
            "skill": "spec-generator",
            "depends_on": [],
            "description": "Write a specification inline",
        }
    ]

    assert (
        scaffold_workflow_files(
            "feature-planning",
            "development",
            _description(),
            [],
            [],
            steps,
            root,
        )
        is None
    )


def test_validator_detects_team_and_execution_drift(tmp_path):
    root = _catalog(tmp_path)
    _write_atomic_skill(root, "development", "spec-generator")
    _write_atomic_skill(root, "development", "task-planner")
    destination = scaffold_workflow_files(
        "feature-planning",
        "development-workflows",
        _description(),
        [],
        [],
        _steps(),
        root,
    )
    team_path = destination / "references" / "team.yaml"
    team = yaml.safe_load(team_path.read_text(encoding="utf-8"))
    team["specialist_ids"] = ["wrong-specialist"]
    team_path.write_text(yaml.safe_dump(team), encoding="utf-8")
    skill_md = destination / "SKILL.md"
    skill_md.write_text(
        skill_md.read_text(encoding="utf-8").replace("After level 0", "After level 9"),
        encoding="utf-8",
    )

    errors = validate_workflow_files(skill_md, root)

    assert any("team.yaml does not match" in error for error in errors)
    assert any("Execution does not match" in error for error in errors)

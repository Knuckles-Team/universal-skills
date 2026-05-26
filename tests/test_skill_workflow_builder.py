import sys
import importlib.util
import tempfile
from pathlib import Path

# Load build_workflow dynamically since agent-tools contains a hyphen
tests_dir = Path(__file__).resolve().parent
script_path = tests_dir.parent / "universal_skills" / "agent-tools" / "skill-workflow-builder" / "scripts" / "build_workflow.py"
spec = importlib.util.spec_from_file_location("build_workflow", str(script_path))
build_workflow = importlib.util.module_from_spec(spec)
sys.modules["build_workflow"] = build_workflow
spec.loader.exec_module(build_workflow)

validate_steps_dag = build_workflow.validate_steps_dag
scaffold_workflow_files = build_workflow.scaffold_workflow_files
parse_workflow_skill = build_workflow.parse_workflow_skill


def test_validate_steps_dag_valid():
    """Validates that a linear DAG passes validation."""
    steps = [
        {
            "step": 0,
            "component": "step-0",
            "depends_on": []
        },
        {
            "step": 1,
            "component": "step-1",
            "depends_on": ["Step 0"]
        },
        {
            "step": 2,
            "component": "step-2",
            "depends_on": ["Step 1"]
        }
    ]
    is_valid, errors = validate_steps_dag(steps)
    assert is_valid is True
    assert len(errors) == 0


def test_validate_steps_dag_circular():
    """Validates that circular dependencies are caught."""
    steps = [
        {
            "step": 0,
            "component": "step-0",
            "depends_on": ["Step 1"]
        },
        {
            "step": 1,
            "component": "step-1",
            "depends_on": ["Step 0"]
        }
    ]
    is_valid, errors = validate_steps_dag(steps)
    assert is_valid is False
    assert any("Circular dependency" in err for err in errors)


def test_validate_steps_dag_missing_reference():
    """Validates that references to non-existent steps are caught."""
    steps = [
        {
            "step": 0,
            "component": "step-0",
            "depends_on": ["Step 5"]
        }
    ]
    is_valid, errors = validate_steps_dag(steps)
    assert is_valid is False
    assert any("non-existent Step 5" in err for err in errors)


def test_scaffold_and_parse_workflow():
    """Tests scaffolding a workflow and then parsing its resulting SKILL.md."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)
        steps = [
            {
                "step": 0,
                "component": "user-interaction",
                "description": "Get inputs",
                "expected": "user_inputs",
                "depends_on": []
            },
            {
                "step": 1,
                "component": "container-manager-mcp",
                "description": "Deploy container",
                "expected": "container_status",
                "depends_on": ["Step 0"]
            }
        ]

        # Scaffold
        dest_dir = scaffold_workflow_files(
            workflow_name="test_workflow",
            domain="infra",
            description="A test temporary workflow description",
            tags=["test", "temp"],
            requires=["portainer-mcp"],
            steps=steps,
            root_path=tmp_path
        )

        assert dest_dir is not None
        assert dest_dir.exists()
        assert (dest_dir / "SKILL.md").exists()
        assert (dest_dir / "references" / "team.yaml").exists()

        # Parse and verify
        parsed = parse_workflow_skill(dest_dir / "SKILL.md")
        assert parsed is not None
        assert parsed["name"] == "test_workflow"
        assert parsed["domain"] == "infra"
        assert "portainer-mcp" in parsed["requires"]
        assert len(parsed["steps"]) == 2
        assert parsed["steps"][0]["component"] == "user-interaction"
        assert parsed["steps"][1]["component"] == "container-manager-mcp"
        assert parsed["steps"][1]["depends_on"] == ["Step 0"]

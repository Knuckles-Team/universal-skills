import sys
from pathlib import Path
import pytest

# Ensure agent-utilities is in sys.path if not already loaded
agent_utils_path = str(Path(__file__).resolve().parent.parent.parent.parent / "agent-utilities")
if agent_utils_path not in sys.path:
    sys.path.insert(0, agent_utils_path)

from agent_utilities.workflows.skill_compiler import SkillCompiler
from agent_utilities.workflows.runner import WorkflowRunner

# Find all directories under universal_skills/ containing a SKILL.md file
skills_root = Path(__file__).resolve().parent.parent / "universal_skills"
skill_dirs = [p.parent for p in skills_root.rglob("SKILL.md")]

# Sort for deterministic test ordering
skill_dirs.sort(key=lambda p: p.as_posix())


@pytest.mark.parametrize("skill_dir", skill_dirs, ids=lambda p: p.relative_to(skills_root).as_posix())
def test_compile_and_validate_workflow(skill_dir):
    """Compiles the SKILL.md file and asserts zero compilation or dependency errors."""
    plan = SkillCompiler.compile(skill_dir)
    assert plan is not None, f"Failed to compile SKILL.md in {skill_dir}"
    assert len(plan.steps) > 0, f"No steps found in SKILL.md in {skill_dir}"

    # Build dependency index map
    step_id_to_idx = {step.node_id: i for i, step in enumerate(plan.steps)}

    # Assert all depends_on references exist within the plan
    for step in plan.steps:
        for dep in step.depends_on:
            assert dep in step_id_to_idx, f"Step '{step.node_id}' in {skill_dir.name} has non-existent dependency '{dep}'"

    # Verify topological wave sorting resolves without circular dependencies
    runner = WorkflowRunner()
    waves = runner._build_execution_waves(plan)
    assert len(waves) > 0, f"Failed to resolve execution waves for workflow {skill_dir.name}"

    # Verify mock registration in the knowledge graph
    reg_outcome = SkillCompiler.register_in_kg(None, skill_dir)
    assert reg_outcome["registered"] is True
    assert reg_outcome["workflow_id"] == f"wf_{skill_dir.name}"

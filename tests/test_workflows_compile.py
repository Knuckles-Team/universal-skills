"""Every skill-workflow's step graph must be well formed.

Parses each workflow ``SKILL.md`` ``### Step N: <id> [depends_on: a, b]`` heading
and checks that the workflow has steps, that every dependency names a step in the
same workflow, and that the dependency graph has no cycle.
"""

import re
from graphlib import TopologicalSorter
from pathlib import Path

import pytest

STEP_RE = re.compile(
    r"^###\s+Step\s+(?P<num>\d+):\s*(?P<id>[^\s\[]+)(?:\s*\[depends_on:\s*(?P<deps>[^\]]*)\])?",
    re.MULTILINE,
)

skills_root = Path(__file__).resolve().parent.parent / "universal_skills"
workflow_dirs = sorted(
    (
        p.parent
        for p in skills_root.rglob("SKILL.md")
        if p.parent.parent.parent == skills_root
        and p.parent.parent.name.endswith("-workflows")
    ),
    key=lambda p: p.as_posix(),
)


def parse_steps(text: str) -> dict[str, list[str]]:
    """Return ``{step_id: [dependency ids]}`` in document order.

    A dependency may name a step by id or by number (``Step 2`` or ``2``).
    """
    matches = list(STEP_RE.finditer(text))
    by_number = {m.group("num"): m.group("id") for m in matches}
    steps: dict[str, list[str]] = {}
    for match in matches:
        raw = (match.group("deps") or "").strip()
        deps: list[str] = []
        for token in (d.strip() for d in raw.split(",")):
            if not token or token == "none":
                continue
            numbered = re.fullmatch(r"(?:Step\s+)?(\d+)", token)
            deps.append(by_number.get(numbered.group(1), token) if numbered else token)
        steps[match.group("id")] = deps
    return steps


def test_workflows_are_discovered() -> None:
    assert workflow_dirs


@pytest.mark.parametrize(
    "skill_dir", workflow_dirs, ids=lambda p: p.relative_to(skills_root).as_posix()
)
def test_workflow_step_graph_is_well_formed(skill_dir: Path) -> None:
    steps = parse_steps((skill_dir / "SKILL.md").read_text(encoding="utf-8"))
    assert steps, f"No steps found in SKILL.md in {skill_dir}"
    for step, deps in steps.items():
        for dep in deps:
            assert dep in steps, (
                f"Step '{step}' in {skill_dir.name} has non-existent dependency '{dep}'"
            )
    sorter = TopologicalSorter()
    for step, deps in steps.items():
        sorter.add(step, *deps)
    sorter.prepare()  # raises CycleError on a circular dependency

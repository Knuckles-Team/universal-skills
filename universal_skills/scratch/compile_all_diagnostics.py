import sys
from pathlib import Path

agent_utils_path = str(Path("/home/apps/workspace/agent-packages/agent-utilities").resolve())
if agent_utils_path not in sys.path:
    sys.path.insert(0, agent_utils_path)

from agent_utilities.workflows.skill_compiler import SkillCompiler

def run_diagnostics():
    skills_root = Path("/home/apps/workspace/agent-packages/skills/universal-skills/universal_skills")
    skill_dirs = [p.parent for p in skills_root.rglob("SKILL.md") if "workflows" not in p.parts]
    skill_dirs.sort(key=lambda p: p.as_posix())
    
    print(f"Total non-workflow folder skills found: {len(skill_dirs)}")
    print(f"{'Skill Name':<40} | {'Type':<12} | {'Steps':<5} | {'Has Explicit Deps?'}")
    print("-" * 100)
    
    for sdir in skill_dirs:
        plan = SkillCompiler.compile(sdir)
        if not plan:
            continue
        
        has_explicit_deps = any(step.depends_on for step in plan.steps)
        step_count = len(plan.steps)
        
        if step_count == 1 and plan.steps[0].node_id == "executor":
            skill_type = "Leaf (Simple)"
        else:
            skill_type = "Workflow"
            
        print(f"{sdir.relative_to(skills_root).as_posix():<40} | {skill_type:<12} | {step_count:<5} | {has_explicit_deps}")

if __name__ == "__main__":
    run_diagnostics()

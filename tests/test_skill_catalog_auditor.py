from __future__ import annotations

import importlib.util
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = (
    ROOT
    / "universal_skills"
    / "agent-tools"
    / "skill-catalog-auditor"
    / "scripts"
    / "audit_catalog.py"
)
SPEC = importlib.util.spec_from_file_location("audit_catalog", SCRIPT)
audit_catalog_module = importlib.util.module_from_spec(SPEC)
sys.modules["audit_catalog"] = audit_catalog_module
SPEC.loader.exec_module(audit_catalog_module)


def write_skill(
    root: Path,
    domain: str,
    name: str,
    *,
    skill_type: str = "skill",
    description: str | None = None,
    body: str = "",
) -> Path:
    skill_dir = root / domain / name
    skill_dir.mkdir(parents=True)
    description = description or (
        f"Perform {name} and return a structured, reviewable result. "
        f"Use when a user requests {name} for a supplied artifact."
    )
    skill_md = skill_dir / "SKILL.md"
    skill_md.write_text(
        "\n".join(
            (
                "---",
                f"name: {name}",
                f"domain: {domain}",
                f"skill_type: {skill_type}",
                f"description: {description}",
                "---",
                f"# {name}",
                "",
                body,
                "",
            )
        ),
        encoding="utf-8",
    )
    return skill_md


def finding_codes(audit, name: str) -> set[str]:
    skill = next(item for item in audit.skills if item.name == name)
    return {finding.code for finding in skill.findings}


def test_clean_atomic_skill(tmp_path):
    write_skill(tmp_path, "data", "dataset-profiler", body="Profile one dataset.")

    audit = audit_catalog_module.audit_catalog(tmp_path)

    assert len(audit.skills) == 1
    assert audit.skills[0].status == "clean"


def test_placeholder_workflow_is_rejected(tmp_path):
    write_skill(tmp_path, "data", "dataset-profiler", body="Profile one dataset.")
    workflow = write_skill(
        tmp_path,
        "data-workflows",
        "dataset-readiness",
        skill_type="workflow",
        body="""## Steps

### Step 0: dataset-profiler
Execute dataset profiler operations for the Dataset Readiness workflow.
Expected: profile

## Execution

Run Step 0.

**Execution:** Use graph_orchestrate or run dependency-ready steps natively.
""",
    )
    references = workflow.parent / "references"
    references.mkdir()
    (references / "team.yaml").write_text(
        "name: Dataset Readiness\nspecialist_ids: [dataset-profiler]\n",
        encoding="utf-8",
    )

    audit = audit_catalog_module.audit_catalog(tmp_path)

    assert "workflow-placeholder-only" in finding_codes(audit, "dataset-readiness")


def test_broken_dependency_and_duplicate_component_are_detected(tmp_path):
    write_skill(tmp_path, "data", "dataset-profiler", body="Profile one dataset.")
    workflow = write_skill(
        tmp_path,
        "data-workflows",
        "dataset-readiness",
        skill_type="workflow",
        body="""## Steps

### Step 0: dataset-profiler
Invoke dataset-profiler.

### Step 1: dataset-profiler [depends_on: missing-step]
Invoke dataset-profiler again.

## Execution

Run the DAG.

**Execution:** Use graph_orchestrate or run dependency-ready steps natively.
""",
    )
    references = workflow.parent / "references"
    references.mkdir()
    (references / "team.yaml").write_text(
        "name: Dataset Readiness\nspecialist_ids: [dataset-profiler]\n",
        encoding="utf-8",
    )

    audit = audit_catalog_module.audit_catalog(tmp_path)
    codes = finding_codes(audit, "dataset-readiness")

    assert "workflow-broken-dependency" in codes
    assert "workflow-duplicate-component" in codes


def test_skill_annotation_binds_external_package_skill(tmp_path):
    workflow = write_skill(
        tmp_path,
        "ops-workflows",
        "ticket-sync",
        skill_type="workflow",
        body="""## Steps

### Step 0: Fetch Tickets [skill: ticket-agent-operations]
Invoke the package-owned skill.

## Execution

Run Step 0.

**Execution:** Use graph_orchestrate or run dependency-ready steps natively.
""",
    )
    text = workflow.read_text(encoding="utf-8").replace(
        "skill_type: workflow", "skill_type: workflow\nrequires: [ticket-agent-operations]"
    )
    workflow.write_text(text, encoding="utf-8")
    references = workflow.parent / "references"
    references.mkdir()
    (references / "team.yaml").write_text(
        "name: Ticket Sync\nspecialist_ids: [ticket-agent]\n", encoding="utf-8"
    )

    audit = audit_catalog_module.audit_catalog(tmp_path)

    assert "workflow-no-steps" not in finding_codes(audit, "ticket-sync")
    assert "workflow-unbound-component" not in finding_codes(audit, "ticket-sync")


def test_unrelated_single_tool_does_not_bind_a_workflow_step(tmp_path):
    workflow = write_skill(
        tmp_path,
        "research-workflows",
        "source-review",
        skill_type="workflow",
        body="""## Steps

### Step 0: review-sources
**Tools**: `unrelated-mcp-tool`
Review sources.

## Execution

Run Step 0.

**Execution:** Use graph_orchestrate or run dependency-ready steps natively.
""",
    )
    references = workflow.parent / "references"
    references.mkdir()
    (references / "team.yaml").write_text(
        "name: Source Review\nspecialist_ids: [review-sources]\n", encoding="utf-8"
    )

    audit = audit_catalog_module.audit_catalog(tmp_path)

    assert "workflow-unbound-component" in finding_codes(audit, "source-review")


def test_explicit_mcp_annotation_binds_a_workflow_step(tmp_path):
    workflow = write_skill(
        tmp_path,
        "research-workflows",
        "source-review",
        skill_type="workflow",
        body="""## Steps

### Step 0: Search sources [mcp_tool: scholarx.search]
Invoke exactly one MCP tool.

## Execution

Run Step 0.

**Execution:** Use graph_orchestrate or run dependency-ready steps natively.
""",
    )
    references = workflow.parent / "references"
    references.mkdir()
    (references / "team.yaml").write_text(
        "name: Source Review\nspecialist_ids: [source-search]\n", encoding="utf-8"
    )

    audit = audit_catalog_module.audit_catalog(tmp_path)

    assert "workflow-unbound-component" not in finding_codes(audit, "source-review")


def test_builder_style_mcp_and_package_bindings_are_recognized(tmp_path):
    workflow = write_skill(
        tmp_path,
        "research-workflows",
        "source-review",
        skill_type="workflow",
        body="""## Steps

### Step 0: search-papers [depends_on: none]
**Agent**: `research-specialist`
**Skill**: `scholarx-operations`
**Package**: `scholarx`

### Step 1: fetch-citation [depends_on: search-papers]
**Agent**: `research-specialist`
**MCP Tool**: `scholarx.get_paper`

## Execution

Run the DAG.

**Execution:** Use graph_orchestrate or run dependency-ready steps natively.
""",
    )
    workflow.write_text(
        workflow.read_text(encoding="utf-8").replace(
            "skill_type: workflow", "skill_type: workflow\nrequires: [scholarx]"
        ),
        encoding="utf-8",
    )
    references = workflow.parent / "references"
    references.mkdir()
    (references / "team.yaml").write_text(
        "name: Source Review\nspecialist_ids: [research-specialist]\n",
        encoding="utf-8",
    )

    audit = audit_catalog_module.audit_catalog(tmp_path)

    assert "workflow-unbound-component" not in finding_codes(audit, "source-review")
    assert "workflow-mcp-binding-invalid" not in finding_codes(audit, "source-review")


def test_markdown_report_lists_clean_skills(tmp_path):
    write_skill(tmp_path, "data", "dataset-profiler", body="Profile one dataset.")

    report = audit_catalog_module.render_markdown(
        audit_catalog_module.audit_catalog(tmp_path)
    )

    assert "`dataset-profiler`" in report
    assert "No structural or advisory findings" in report


def test_repository_has_no_hollow_workflows_or_broken_links():
    audit = audit_catalog_module.audit_catalog(ROOT / "universal_skills")
    prohibited = {"workflow-placeholder-only", "broken-local-link"}
    offenders = {
        skill.path: sorted(
            finding.code for finding in skill.findings if finding.code in prohibited
        )
        for skill in audit.skills
        if any(finding.code in prohibited for finding in skill.findings)
    }

    assert offenders == {}


def test_new_atomic_categories_are_structurally_clean():
    audit = audit_catalog_module.audit_catalog(ROOT / "universal_skills")
    expected = {
        "citation-auditor",
        "content-draft-writer",
        "content-outline-builder",
        "copy-editor",
        "data-dictionary-builder",
        "data-quality-auditor",
        "dataset-profiler",
        "publication-preflight",
        "skill-catalog-auditor",
    }
    selected = {skill.name: skill for skill in audit.skills if skill.name in expected}

    assert set(selected) == expected
    assert {name: skill.status for name, skill in selected.items()} == {
        name: "clean" for name in expected
    }

"""US-MCP-BUILDER-R011.19: the contract check refuses what the engine refuses at onboarding.

The engine rejects a connector pack whose skill front matter holds ``& * ! { }``
(``MALFORMED_BODY``) or whose ontology has a class with no ``rdfs:subClassOf`` path
to the core catalog (``ONTOLOGY_ORPHAN``). Both used to pass the connector gate.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "universal_skills" / "skills" / "mcp-builder" / "scripts"))
import check_connector_contract as contract  # noqa: E402

CORE = "https://knuckles-team.github.io/ontology/core#"
HEADER = (
    "@prefix : <https://knuckles-team.github.io/ontology/connector/x#> .\n"
    f"@prefix core: <{CORE}> .\n"
    "@prefix owl: <http://www.w3.org/2002/07/owl#> .\n"
    "@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .\n"
)


def skill(description: str, name: str = "x-ops") -> str:
    return f"---\nname: {name}\nskill_type: skill\ndescription: {description}\n---\n\nbody {{ok}} *\n"


@pytest.mark.spec("US-MCP-BUILDER-R011.19")
@pytest.mark.parametrize("bad", ["use x_* tools", "a & b", "stop!", "a {b}", "a }"])
def test_front_matter_with_engine_forbidden_characters_is_refused(bad):
    assert contract.skill_front_matter_problem(skill(bad), "x-ops")


@pytest.mark.spec("US-MCP-BUILDER-R011.19")
def test_clean_front_matter_passes_and_the_body_may_use_the_characters():
    assert contract.skill_front_matter_problem(skill("use the x_ tools"), "x-ops") is None
    assert contract.skill_front_matter_problem(skill("ok", "other"), "x-ops")


@pytest.mark.spec("US-MCP-BUILDER-R011.19")
def test_orphan_class_is_found_without_an_ontology_header():
    orphan = HEADER + ':Widget a owl:Class ;\n    rdfs:label "Widget" .\n'
    assert contract.ontology_orphans([orphan]) == {
        "https://knuckles-team.github.io/ontology/connector/x#Widget"
    }


@pytest.mark.spec("US-MCP-BUILDER-R011.19")
def test_every_class_reaching_core_directly_or_through_a_parent_passes():
    linked = (
        HEADER
        + ":Base a owl:Class ;\n    rdfs:subClassOf core:Concept .\n"
        + ':Leaf a owl:Class ;\n    rdfs:subClassOf :Base ;\n    rdfs:label "Leaf" .\n'
    )
    assert contract.ontology_orphans([linked]) == set()


@pytest.mark.spec("US-MCP-BUILDER-R011.19")
def test_a_comment_or_label_mentioning_subclassof_does_not_link_a_class():
    text = HEADER + '# rdfs:subClassOf core:Concept\n:W a owl:Class ;\n    rdfs:comment "rdfs:subClassOf core:Concept" .\n'
    assert contract.ontology_orphans([text]) != set()


@pytest.mark.spec("US-MCP-BUILDER-R011.19")
def test_check_sdk_rules_reports_both_defects(tmp_path):
    package = tmp_path / "pkg"
    (package / "skills" / "x-ops").mkdir(parents=True)
    (package / "ontology").mkdir()
    (package / "skills" / "x-ops" / "SKILL.md").write_text(skill("uses x_*"))
    (package / "ontology" / "x.ttl").write_text(HEADER + ":W a owl:Class .\n")
    found = contract._skill_violations(package) + contract._ontology_violations(package)
    assert len(found) == 2


@pytest.mark.spec("US-MCP-BUILDER-R011.19")
def test_the_scaffold_ontology_template_has_no_orphans():
    import scaffold_connector as scaffold

    rendered = scaffold.ONTOLOGY.format(
        short="x", Display="X", Class="X", core=scaffold.CORE_CLASS, short_camel="x"
    )
    assert contract.ontology_orphans([rendered]) == set()
    assert contract.skill_front_matter_problem(
        scaffold.SKILL.format(short="x", Display="X", short_snake="x"), "x-operations"
    ) is None


@pytest.mark.spec("US-MCP-BUILDER-R011.19")
@pytest.mark.parametrize("module", ["scaffold_connector", "scaffold_wrap"])
def test_both_scaffold_ontologies_name_the_parent_of_either_engine(module):
    import importlib

    template = importlib.import_module(module).ONTOLOGY
    assert "rdfs:subClassOf core:{core}, kg:{core} ;" in template
    assert "@prefix kg: <http://knuckles.team/kg#> ." in template

"""Every scaffolded connector ships its ontology pack: domain plus surface."""

import importlib.util
from pathlib import Path

import pytest

SCRIPTS = (
    Path(__file__).resolve().parents[1]
    / "universal_skills/agent-tools/mcp-builder/scripts"
)


def load_builder():
    spec = importlib.util.spec_from_file_location(
        "pack_scaffold", SCRIPTS / "scaffold_package.py"
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_scaffold_ships_domain_and_surface_pack(tmp_path):
    rdflib = pytest.importorskip("rdflib")
    builder = load_builder()
    builder.scaffold("example-mcp", output_dir=str(tmp_path))
    ontology = tmp_path / "example-mcp" / "example_mcp" / "ontology"
    domain = rdflib.Graph().parse(ontology / "example.ttl", format="turtle")
    pack_text = (ontology / "pack.ttl").read_text()
    assert "_:" not in pack_text and "[" not in pack_text
    pack = rdflib.Graph().parse(data=pack_text, format="turtle")
    cp = rdflib.Namespace("http://knuckles.team/kg/connector-pack#")
    kinds = {o for o in pack.objects(None, rdflib.RDF.type)}
    for kind in ("Connector", "Feature", "Skill", "Prompt", "IngestContract",
                 "SourceObject", "KeyRule", "CursorPolicy", "AccessPolicy",
                 "ProvenanceRequirement"):
        assert cp[kind] in kinds, kind
    classes = set(domain.subjects(rdflib.RDF.type, rdflib.OWL.Class))
    mapped = set(pack.objects(None, cp.mapsToClass)) | set(
        pack.objects(None, cp.appliesTo)
    )
    assert mapped and mapped <= classes
    skills = {str(o) for o in pack.objects(None, cp.componentId)}
    assert "example-starter" in skills
    assert (ontology.parent / "skills" / "example-starter" / "SKILL.md").is_file()

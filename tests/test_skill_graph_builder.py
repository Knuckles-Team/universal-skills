"""US-SKILL-GRAPH-BUILDER: the builder CLI names, classifies, places and flattens a graph."""

from __future__ import annotations

import hashlib
import importlib.util
import json
import sys
import types
from pathlib import Path

import pytest

SCRIPT = (
    Path(__file__).resolve().parents[1]
    / "universal_skills"
    / "skills"
    / "skill-graph-builder"
    / "scripts"
    / "generate_skill.py"
)


@pytest.fixture(scope="module")
def builder():
    """Load the script with its local pipeline module."""
    spec = importlib.util.spec_from_file_location("generate_skill_under_test", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    yield module


@pytest.mark.spec("US-SKILL-GRAPH-BUILDER-R001.1")
def test_graph_name_gets_docs_suffix_and_is_portable(builder, tmp_path, monkeypatch):
    seen = {}

    class Pipe:
        def __init__(self, crawler_fn=None, kg_enrich=True):
            pass

        def build(self, *, name, specs, out_dir, description, max_file_kb):
            seen["name"] = name
            raise SystemExit(0)

    monkeypatch.setattr(builder, "SkillGraphPipeline", Pipe)
    with pytest.raises(SystemExit):
        builder.generate_skill("./docs", "pandas", output_dir=str(tmp_path))
    assert seen["name"] == "pandas-docs"
    assert len(builder._portable_name("a" * 300 + "-docs")) <= 80


@pytest.mark.spec("US-SKILL-GRAPH-BUILDER-R001.2")
def test_sources_are_classified_by_kind(builder, tmp_path):
    pdf = tmp_path / "manual.PDF"
    pdf.write_bytes(b"%PDF")
    kinds = [
        (s.kind, s.uri)
        for s in builder._classify_sources(
            f"https://site.test/docs,https://site.test/m.pdf,https://site.test/x.xlsx,{pdf},{tmp_path}",
            3,
        )
    ]
    assert kinds == [
        ("web", "https://site.test/docs"),
        ("pdf", "https://site.test/m.pdf"),
        ("office", "https://site.test/x.xlsx"),
        ("pdf", str(pdf)),
        ("dir", str(tmp_path)),
    ]


@pytest.mark.spec("US-SKILL-GRAPH-BUILDER-R001.3")
def test_flatten_hashes_names_and_repoints_the_manifests(builder, tmp_path):
    graph = tmp_path / "demo-docs"
    (graph / "reference" / "guide").mkdir(parents=True)
    (graph / "reference" / "guide" / "intro.md").write_text("# Intro\n", encoding="utf-8")
    url = "https://site.test/guide/intro"
    (graph / "index.json").write_text(
        json.dumps(
            {
                "source_url": "https://site.test",
                "sections": [
                    {"path": "reference/guide/intro.md", "title": "Intro", "group": "guide", "url": url}
                ],
            }
        ),
        encoding="utf-8",
    )
    (graph / "sources.json").write_text(
        json.dumps({"files": [{"path": "reference/guide/intro.md"}]}), encoding="utf-8"
    )
    (graph / "SKILL.md").write_text("[Intro](reference/guide/intro.md)\n", encoding="utf-8")

    builder._flatten_reference_tree(graph)

    name = hashlib.sha256(url.encode("utf-8")).hexdigest()[:8] + ".md"
    assert [p.name for p in (graph / "reference").rglob("*") if p.is_file()] == [name]
    assert not (graph / "reference" / "guide").exists()
    assert json.loads((graph / "index.json").read_text())["sections"][0]["path"] == f"reference/{name}"
    assert json.loads((graph / "sources.json").read_text())["files"][0]["path"] == f"reference/{name}"
    assert f"(reference/{name})" in (graph / "SKILL.md").read_text()


@pytest.mark.spec("US-SKILL-GRAPH-BUILDER-R001.4")
def test_output_goes_to_the_graph_collection_or_the_cache(builder, tmp_path, monkeypatch):
    assert builder._resolve_out_dir("skill-graphs", str(tmp_path)) == tmp_path
    script = tmp_path / "ws" / "universal-skills" / "universal_skills" / "skills"
    script = script / "skill-graph-builder" / "scripts" / "generate_skill.py"
    monkeypatch.setattr(builder, "__file__", str(script))
    monkeypatch.setattr(Path, "home", classmethod(lambda cls: tmp_path / "home"))
    cache = tmp_path / "home" / ".cache" / "universal-skills" / "skill-graphs"
    assert builder._resolve_out_dir("skill-graphs", None) == cache
    collection = tmp_path / "ws" / "skill-graphs" / "skill_graphs" / "skills"
    collection.mkdir(parents=True)
    assert builder._resolve_out_dir("skill-graphs", None) == collection


@pytest.mark.spec("US-SKILL-GRAPH-BUILDER-R002.1")
def test_web_sources_are_fetched_by_the_web_crawler_skill(builder, monkeypatch):
    calls = []

    def fake_run(cmd, check):
        calls.append(cmd)
        out = Path(cmd[cmd.index("--output-dir") + 1])
        (out / "page.md").write_text("# Page\n", encoding="utf-8")

    monkeypatch.setattr(builder.subprocess, "run", fake_run)
    spec = builder.SourceSpec("web", "https://site.test/docs", {"max_depth": 3, "max_pages": 9})
    docs = builder._make_crawler_fn({"no_sitemap": True})(spec)
    cmd = calls[0]
    assert Path(cmd[1]).parts[-4:] == ("skills", "web-crawler", "scripts", "crawl.py")
    assert cmd[cmd.index("--urls") + 1] == "https://site.test/docs"
    assert cmd[cmd.index("--max-depth") + 1] == "3" and cmd[cmd.index("--max-pages") + 1] == "9"
    assert "--no-sitemap" in cmd
    assert [(d.rel_path, d.source_uri) for d in docs] == [("page.md", "https://site.test/docs")]


@pytest.mark.spec("US-SKILL-GRAPH-BUILDER-R004.1")
def test_builder_imports_no_retired_package() -> None:
    root = SCRIPT.parent
    files = list(root.rglob("*.py")) + list(
        (Path(__file__).resolve().parents[1] / "universal_skills" / "skill_graph_pipeline").rglob("*.py")
    )
    assert files
    assert not [f for f in files if "agent_utilities" in f.read_text(encoding="utf-8")]


@pytest.mark.spec("US-SKILL-GRAPH-BUILDER-R004.2")
@pytest.mark.parametrize("flag", ["--no-kg", "--ingest-kg", "--append"])
def test_retired_flags_are_refused(flag: str) -> None:
    import subprocess

    done = subprocess.run(
        [sys.executable, str(SCRIPT), "./docs", "x", flag],
        capture_output=True,
        text=True,
    )
    assert done.returncode == 2

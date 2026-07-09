#!/usr/bin/env python3
"""Thin CLI over the unified skill-graph pipeline.

CONCEPT:KG-2.7 — Every skill-graph is now built ONE way. This script is a thin
front-end that:

* translates the familiar CLI arg surface into :class:`SourceSpec` inputs, and
* keeps this repo's crawl4ai ``web-crawler`` for JS-heavy sites by injecting it as
  the pipeline's ``crawler_fn`` (so web acquisition quality is preserved),

then delegates *all* standardization — markdown normalization, the standardized
``SKILL.md`` + ``sources.json`` provenance/freshness manifest, hybrid-auto KG
ingestion, large-file splitting and the hierarchical TOC — to the agent-utilities
core (``agent_utilities.knowledge_graph.distillation.skill_graph_pipeline``).

This keeps a single source of truth for the skill-graph format while letting the
skill own the richer crawler. The builder runs in the agent-packages workspace
where agent-utilities is importable; if it is not, it tells you how to install it.
"""

import argparse
import hashlib
import json
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

try:
    from agent_utilities.knowledge_graph.distillation import (
        AcquiredDoc,
        SkillGraphPipeline,
        SourceSpec,
    )
except ImportError:
    sys.stderr.write(
        "skill-graph-builder requires agent-utilities to be importable.\n"
        "Install it in this environment: pip install agent-utilities\n"
    )
    sys.exit(1)

try:
    from universal_skills.skill_utilities import portable_name as _portable_name
    from universal_skills.skill_utilities import portable_relpath as _portable_relpath
except Exception:  # pragma: no cover - standalone execution

    def _portable_name(name: str, max_len: int = 80) -> str:
        cleaned = re.sub(r'[<>:"/\\|?*\x00-\x1f]', "-", name or "").strip(". ") or "_"
        return cleaned[:max_len]

    def _portable_relpath(parts, max_total: int = 140) -> str:
        return "/".join(_portable_name(p) for p in parts if p not in ("", "."))[
            :max_total
        ]


def _flatten_reference_tree(skill_dir: Path) -> None:
    """Rewrite a just-built skill-graph's ``reference/`` into a FLAT, portable
    layout: ``reference/<hash>.md``, so on-disk names stay short and
    Windows/macOS-safe for FUTURE crawls (existing skill-graphs are migrated
    separately, not by this function).

    The pipeline (``SkillGraphPipeline.build``) lays ``reference/`` out in
    nested, title-derived directories. This runs immediately after ``build()``
    and:
    * moves every ``reference/**/*.md`` to ``reference/<hash>.md`` where
      ``hash = sha1(seed)[:8]`` (extended to ``[:12]``/``[:16]`` on collision),
      seeded on the section's source URL when known, else its title/path;
    * keeps the human ``title``/``group``/``url`` in ``index.json``'s
      ``sections[]`` entries (the file reference becomes the hashed name);
    * keeps ``sources.json``'s ``files[].path`` and the ``SKILL.md`` Table of
      Contents links in sync with the renamed files.
    """
    ref = skill_dir / "reference"
    index_path = skill_dir / "index.json"
    if not ref.is_dir() or not index_path.exists():
        return
    index = json.loads(index_path.read_text(encoding="utf-8"))
    top_source_url = index.get("source_url") or ""
    single_url = top_source_url if top_source_url and "," not in top_source_url else ""

    used_hashes: set[str] = set()
    path_map: dict[str, str] = {}
    sections = index.get("sections") or []
    for section in sections:
        old_rel = section.get("path", "")
        old_file = skill_dir / old_rel
        if not old_file.is_file():
            continue
        seed = section.get("url") or section.get("title") or old_rel
        digest = hashlib.sha1(seed.encode("utf-8")).hexdigest()
        chosen = digest[:8]
        for length in (8, 12, 16):
            candidate = digest[:length]
            if candidate not in used_hashes:
                chosen = candidate
                break
        else:
            chosen = digest[:16]
        used_hashes.add(chosen)
        new_rel = _portable_relpath(["reference", f"{chosen}.md"], max_total=140)
        new_file = skill_dir / new_rel
        new_file.parent.mkdir(parents=True, exist_ok=True)
        if old_file.resolve() != new_file.resolve():
            shutil.move(str(old_file), str(new_file))
        path_map[old_rel] = new_rel
        section["path"] = new_rel
        if not section.get("url"):
            section["url"] = single_url

    index["sections"] = sections
    groups: dict[str, int] = {}
    for s in sections:
        groups[s.get("group", ".")] = groups.get(s.get("group", "."), 0) + 1
    index["groups"] = dict(sorted(groups.items()))
    index_path.write_text(json.dumps(index, indent=2), encoding="utf-8")

    # Remove now-empty subdirectories left under reference/ by the flatten.
    for d in sorted((p for p in ref.rglob("*") if p.is_dir()), reverse=True):
        try:
            d.rmdir()
        except OSError:
            pass

    # Keep sources.json's file listing (content unchanged; only the path moved).
    sources_path = skill_dir / "sources.json"
    if sources_path.exists():
        manifest = json.loads(sources_path.read_text(encoding="utf-8"))
        for f in manifest.get("files", []):
            f["path"] = path_map.get(f["path"], f["path"])
        sources_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")

    # Repoint reference/ links inside SKILL.md's rendered Table of Contents.
    skill_md = skill_dir / "SKILL.md"
    if skill_md.exists() and path_map:
        text = skill_md.read_text(encoding="utf-8")
        for old_rel, new_rel in path_map.items():
            text = text.replace(f"]({old_rel})", f"]({new_rel})")
        skill_md.write_text(text, encoding="utf-8")


_DOC_EXTS = (".pdf", ".docx", ".pptx", ".xlsx", ".csv")


def _crawl_script() -> Path:
    """Resolve this repo's crawl4ai web-crawler script path."""
    # .../universal_skills/agent-tools/skill-graph-builder/scripts/generate_skill.py
    pkg_root = Path(__file__).resolve().parents[3]  # universal_skills/
    return pkg_root / "research" / "web-crawler" / "scripts" / "crawl.py"


def _make_crawler_fn(crawl_opts: dict):
    """Build a pipeline ``crawler_fn`` backed by the crawl4ai web-crawler subprocess."""
    crawl_script = _crawl_script()

    def crawler_fn(spec: SourceSpec) -> list[AcquiredDoc]:
        if not crawl_script.exists():
            raise RuntimeError(f"web-crawler not found at {crawl_script}")
        tmp = Path(tempfile.mkdtemp(prefix="sg_crawl_"))
        try:
            cmd = [
                sys.executable,
                str(crawl_script),
                "--urls",
                spec.uri,
                "--strategy",
                "recursive",
                "--output-dir",
                str(tmp),
                "--max-depth",
                str(int(spec.options.get("max_depth", 2))),
                "--max-pages",
                str(int(spec.options.get("max_pages", 1000))),
            ]
            if crawl_opts.get("disable_magic_js"):
                cmd.append("--disable-magic-js")
            if crawl_opts.get("no_sitemap"):
                cmd.append("--no-sitemap")
            if crawl_opts.get("wait_for"):
                cmd.extend(["--wait-for", crawl_opts["wait_for"]])
            subprocess.run(cmd, check=True)
            docs: list[AcquiredDoc] = []
            for p in sorted(tmp.rglob("*.md")):
                docs.append(
                    AcquiredDoc(
                        rel_path=p.relative_to(tmp).as_posix(),
                        text=p.read_text(encoding="utf-8", errors="replace"),
                        source_uri=spec.uri,
                    )
                )
            return docs
        finally:
            shutil.rmtree(tmp, ignore_errors=True)

    return crawler_fn


def _classify_sources(source_input: str, max_depth: int) -> list[SourceSpec]:
    """Map the comma-separated source arg into typed :class:`SourceSpec` inputs."""
    specs: list[SourceSpec] = []
    for raw in (s.strip() for s in (source_input or "").split(",")):
        if not raw:
            continue
        low = raw.lower().split("?")[0]
        if raw.startswith("http"):
            if low.endswith(_DOC_EXTS):
                kind = "pdf" if low.endswith(".pdf") else "office"
                specs.append(SourceSpec(kind, raw))
            else:
                specs.append(SourceSpec("web", raw, {"max_depth": max_depth}))
            continue
        path = Path(raw)
        if path.is_file() and path.suffix.lower() in _DOC_EXTS:
            kind = "pdf" if path.suffix.lower() == ".pdf" else "office"
            specs.append(SourceSpec(kind, raw))
        else:
            specs.append(SourceSpec("dir", raw))
    return specs


def _resolve_out_dir(target_type: str, output_dir: str | None) -> Path:
    """Compute the PARENT directory the skill-graph <name>/ folder is written under."""
    if output_dir:
        return Path(output_dir)
    pkg_root = Path(__file__).resolve().parents[3]  # universal_skills/
    if target_type == "skills":
        return pkg_root
    # pkg_root.parent.parent → .../agent-packages/skills ; its sibling skill-graphs repo.
    workspace_root = pkg_root.parent.parent
    repo = workspace_root / "skill-graphs" / "skill_graphs"
    if (workspace_root / "skill-graphs").exists() and repo.is_dir():
        return repo
    cache = Path.home() / ".cache" / "universal-skills" / "skill-graphs"
    cache.mkdir(parents=True, exist_ok=True)
    return cache


def generate_skill(
    source_input: str,
    skill_name: str,
    description: str | None = None,
    max_depth: int = 2,
    target_type: str = "skill-graphs",
    max_file_kb: int = 50,
    output_dir: str | None = None,
    max_pages: int = 1000,
    disable_magic_js: bool = False,
    wait_for: str | None = None,
    no_sitemap: bool = False,
    append: bool = False,
    no_kg: bool = False,
    from_kg: str | None = None,
    distill: bool = False,
):
    if not skill_name.endswith("-docs"):
        skill_name = f"{skill_name}-docs"
        print(f"🏷️  Enforcing naming convention: renamed skill to **{skill_name}**")
    skill_name = _portable_name(skill_name)

    specs = _classify_sources(source_input, max_depth)
    if from_kg:
        specs.append(SourceSpec("kg_query", from_kg, {"max_depth": max_depth}))
    if not specs:
        raise SystemExit("provide a source (URL/dir/file) or --from-kg <seed-or-query>")
    if append:
        print(
            "⚠️  --append is deprecated; the unified pipeline always does a full, "
            "provenance-tracked rebuild. Use the `rebuild` action for incremental refresh."
        )

    for s in specs:
        if s.kind == "web":
            s.options["max_pages"] = max_pages

    crawl_opts = {
        "disable_magic_js": disable_magic_js,
        "no_sitemap": no_sitemap,
        "wait_for": wait_for,
    }
    pipe = SkillGraphPipeline(
        crawler_fn=_make_crawler_fn(crawl_opts), kg_enrich=not no_kg
    )
    out_dir = _resolve_out_dir(target_type, output_dir)
    print(
        f"🛠️  Building skill-graph **{skill_name}** "
        f"from {len(specs)} source(s) → {out_dir / skill_name}"
    )
    result = pipe.build(
        name=skill_name,
        specs=specs,
        out_dir=out_dir,
        description=description,
        max_file_kb=max_file_kb,
    )
    _flatten_reference_tree(Path(result["skill_dir"]))
    kg = "yes" if result["kg_ingested"] else "no (offline)"
    print(
        f"✅ Built **{skill_name}**: {result['file_count']} files • "
        f"KG-ingested: {kg} • v{result['version']}"
    )
    if result["validation_errors"]:
        print("⚠️  validation issues:")
        for err in result["validation_errors"]:
            print(f"   - {err}")

    if distill:
        print("📖 Distilling an OVERVIEW.md (essence + cheatsheet)…")
        d = pipe.distill_one(out_dir / skill_name)
        print(
            f"   {'✅ distilled' if d.get('status') == 'distilled' else '⚠️ ' + str(d)}"
        )
    return result


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Build a standardized agent skill-graph from any source "
        "(website, PDF/Office, local dir, or a Knowledge-Graph distillation)."
    )
    parser.add_argument(
        "source",
        nargs="?",
        default="",
        help="Comma-separated markdown dirs / files / starting URLs. "
        "Optional when --from-kg is given.",
    )
    parser.add_argument("skill_name", help="Name of the skill (kebab-case).")
    parser.add_argument("--description", help="Optional description for the skill.")
    parser.add_argument(
        "--max-depth",
        type=int,
        default=2,
        help="Max depth for recursive web crawl / KG distillation.",
    )
    parser.add_argument(
        "--target-type",
        choices=["skills", "skill-graphs"],
        default="skill-graphs",
        help="Output directory type.",
    )
    parser.add_argument(
        "--max-file-kb",
        type=int,
        default=50,
        help="Max file size in KB before splitting (default: 50).",
    )
    parser.add_argument(
        "--output-dir",
        default=None,
        help="Custom output parent dir (<output-dir>/<skill-name>/).",
    )
    parser.add_argument(
        "--no-sitemap",
        action="store_true",
        help="Disable sitemap auto-discovery in the crawler.",
    )
    parser.add_argument(
        "--max-pages",
        type=int,
        default=1000,
        help="Limit total pages crawled in recursive mode.",
    )
    parser.add_argument(
        "--disable-magic-js",
        action="store_true",
        help="Disable the complex MAGIC_JS payload in web-crawler.",
    )
    parser.add_argument(
        "--wait-for",
        type=str,
        help="CSS selector / JS expression to wait for in web-crawler.",
    )
    parser.add_argument(
        "--append",
        action="store_true",
        help="Deprecated (no-op): the pipeline always full-rebuilds.",
    )
    parser.add_argument(
        "--no-kg",
        action="store_true",
        help="Skip the hybrid-auto Knowledge-Graph ingestion (offline corpus only). "
        "By default the corpus is ALSO ingested into the KG when the daemon is "
        "reachable, degrading cleanly to offline-only when it is not.",
    )
    parser.add_argument(
        "--ingest-kg",
        "--ingest_kg",
        action="store_true",
        dest="ingest_kg",
        help="Deprecated: KG ingestion is now hybrid-auto by default (use --no-kg to "
        "disable). Accepted for backward compatibility.",
    )
    parser.add_argument(
        "--from-kg",
        "--from_kg",
        type=str,
        default=None,
        metavar="SEED_OR_QUERY",
        help="Distill the skill-graph FROM the Knowledge Graph: a seed node id "
        "(e.g. 'concept:servicenow') or a natural-language query.",
    )
    parser.add_argument(
        "--distill",
        action="store_true",
        help="After building, LLM-distill an OVERVIEW.md (essence + cheatsheet) so the "
        "agent reads the distilled knowledge first and drills into reference/ for detail.",
    )

    args = parser.parse_args()
    if not args.source and not args.from_kg:
        parser.error("provide a source (URL/dir/file) or --from-kg <seed-or-query>")
    generate_skill(
        args.source,
        args.skill_name,
        args.description,
        args.max_depth,
        args.target_type,
        args.max_file_kb,
        args.output_dir,
        args.max_pages,
        args.disable_magic_js,
        args.wait_for,
        args.no_sitemap,
        args.append,
        args.no_kg,
        args.from_kg,
        args.distill,
    )


if __name__ == "__main__":
    main()

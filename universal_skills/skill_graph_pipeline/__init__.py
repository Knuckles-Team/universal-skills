"""The skill-graph pipeline of the skill-graph-builder (US-SKILL-GRAPH-BUILDER-R004.1).

Acquires documents from typed sources, splits them at ``max_file_kb``, and writes
the standardized skill-graph layout: ``SKILL.md`` (``skill_type: graph``),
``index.json``, ``sources.json`` (schema ``skill-graph-sources/v1``) and a
``reference/`` markdown tree. It imports no engine or agent-runtime package.

Graph sources (``kg_query``) read through the served arbora search twin. Native
distillation moves to ``MEDULLA-TYPED-PACKS-R700.7`` when that row lands.
"""

from __future__ import annotations

import datetime as _dt
import hashlib
import json
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable
from urllib.parse import urlsplit

SOURCES_SCHEMA = "skill-graph-sources/v1"
_TEXT_EXTS = {".md", ".markdown", ".txt", ".rst"}
_MAX_REMOTE_BYTES = 32 * 1024 * 1024


@dataclass
class SourceSpec:
    kind: str
    uri: str
    options: dict = field(default_factory=dict)


@dataclass
class AcquiredDoc:
    rel_path: str
    text: str
    source_uri: str


def _slug(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")[:60] or "doc"


def _document_bytes(spec: SourceSpec) -> tuple[bytes, str]:
    if spec.uri.startswith("http"):
        from universal_skills._security.http import UrlPolicy, open_bounded

        host = (urlsplit(spec.uri).hostname or "").lower()
        resp = open_bounded(
            spec.uri,
            policy=UrlPolicy(frozenset({host})),
            max_bytes=_MAX_REMOTE_BYTES,
        )
        return resp.body, Path(urlsplit(spec.uri).path).name or "document"
    path = Path(spec.uri)
    return path.read_bytes(), path.name


def _acquire_document(spec: SourceSpec) -> list[AcquiredDoc]:
    import tempfile

    data, name = _document_bytes(spec)
    suffix = Path(name).suffix or (".pdf" if spec.kind == "pdf" else "")
    with tempfile.TemporaryDirectory(prefix="sg_doc_") as tmp:
        path = Path(tmp) / f"source{suffix}"
        path.write_bytes(data)
        if spec.kind == "pdf":
            try:
                import pymupdf4llm
            except ImportError as exc:
                raise RuntimeError("pdf sources need the pymupdf4llm package") from exc
            text = pymupdf4llm.to_markdown(str(path))
        else:
            try:
                from markitdown import MarkItDown
            except ImportError as exc:
                raise RuntimeError("office sources need the markitdown package") from exc
            text = MarkItDown().convert(str(path)).text_content
    return [AcquiredDoc(f"{_slug(Path(name).stem)}.md", text, spec.uri)]


def _acquire_dir(spec: SourceSpec) -> list[AcquiredDoc]:
    root = Path(spec.uri)
    files = [root] if root.is_file() else sorted(root.rglob("*"))
    docs = []
    for p in files:
        if p.is_file() and p.suffix.lower() in _TEXT_EXTS:
            rel = p.name if root.is_file() else p.relative_to(root).as_posix()
            docs.append(
                AcquiredDoc(rel, p.read_text(encoding="utf-8", errors="replace"), str(p))
            )
    return docs


def _acquire_graph(spec: SourceSpec) -> list[AcquiredDoc]:
    from universal_skills._arbora import graph_search

    rows = graph_search(spec.uri, top_k=int(spec.options.get("top_k", 25)))
    if rows is None:
        raise RuntimeError("no arbora gateway answered (set ARBORA_URL)")
    docs = []
    for i, row in enumerate(rows):
        text = row.get("content") or row.get("description") or ""
        if text:
            title = str(row.get("name") or row.get("id") or f"node-{i}")
            docs.append(
                AcquiredDoc(
                    f"{_slug(title)}-{i}.md",
                    f"# {title}\n\n{text}\n",
                    f"kg:{row.get('id', i)}",
                )
            )
    return docs


def _split(text: str, max_bytes: int) -> list[str]:
    """Split at blank lines so each part stays within ``max_bytes``."""
    if len(text.encode("utf-8")) <= max_bytes:
        return [text]
    parts, cur = [], ""
    for block in re.split(r"\n\s*\n", text):
        if cur and len((cur + "\n\n" + block).encode("utf-8")) > max_bytes:
            parts.append(cur)
            cur = block
        else:
            cur = f"{cur}\n\n{block}" if cur else block
    if cur:
        parts.append(cur)
    return parts


def _title(text: str, fallback: str) -> str:
    m = re.search(r"^#\s+(.+)$", text, re.MULTILINE)
    return (m.group(1).strip() if m else fallback)[:120]


class SkillGraphPipeline:
    def __init__(
        self,
        crawler_fn: Callable[[SourceSpec], list[AcquiredDoc]] | None = None,
    ) -> None:
        self.crawler_fn = crawler_fn

    def _acquire(self, spec: SourceSpec) -> list[AcquiredDoc]:
        if spec.kind == "web":
            if self.crawler_fn is None:
                raise RuntimeError("no crawler configured for web sources")
            return self.crawler_fn(spec)
        if spec.kind in ("pdf", "office"):
            return _acquire_document(spec)
        if spec.kind == "dir":
            return _acquire_dir(spec)
        if spec.kind == "kg_query":
            return _acquire_graph(spec)
        raise ValueError(f"unsupported source kind: {spec.kind}")

    def build(
        self,
        *,
        name: str,
        specs: list[SourceSpec],
        out_dir: Path,
        description: str | None,
        max_file_kb: int = 50,
    ) -> dict:
        skill_dir = Path(out_dir) / name
        ref = skill_dir / "reference"
        if ref.exists():
            for f in sorted(ref.rglob("*"), reverse=True):
                f.unlink() if f.is_file() else f.rmdir()
        ref.mkdir(parents=True, exist_ok=True)
        now = _dt.datetime.now(_dt.timezone.utc).isoformat(timespec="seconds")
        sections, files, sources = [], [], []
        limit = max(1, int(max_file_kb)) * 1024
        for spec in specs:
            docs = self._acquire(spec)
            sources.append(
                {"kind": spec.kind, "uri": spec.uri, "fetched_at": now, "doc_count": len(docs)}
            )
            for doc in docs:
                stem = Path(doc.rel_path)
                group = stem.parent.as_posix()
                for n, part in enumerate(_split(doc.text, limit), 1):
                    suffix = f"-part{n}" if n > 1 else ""
                    rel = (Path("reference") / stem.parent / f"{stem.stem}{suffix}.md").as_posix()
                    target = skill_dir / rel
                    target.parent.mkdir(parents=True, exist_ok=True)
                    target.write_text(part, encoding="utf-8")
                    sections.append(
                        {
                            "title": _title(part, stem.stem)
                            + (f" (part {n})" if n > 1 else ""),
                            "path": rel,
                            "group": group,
                            "url": doc.source_uri if doc.source_uri.startswith("http") else "",
                        }
                    )
                    files.append(
                        {
                            "path": rel,
                            "sha256": "sha256:" + hashlib.sha256(part.encode("utf-8")).hexdigest(),
                            "source_uri": doc.source_uri,
                        }
                    )
        desc = description or f"Reference manual for {name}, built from {len(specs)} source(s)."
        first = specs[0].uri if specs else ""
        (skill_dir / "index.json").write_text(
            json.dumps(
                {"name": name, "source_url": ",".join(s.uri for s in specs if s.uri.startswith("http")) or first, "sections": sections},
                indent=2,
            ),
            encoding="utf-8",
        )
        (skill_dir / "sources.json").write_text(
            json.dumps(
                {"schema": SOURCES_SCHEMA, "name": name, "built_at": now, "file_count": len(files), "sources": sources, "files": files},
                indent=2,
            ),
            encoding="utf-8",
        )
        toc = "\n".join(f"- [{s['title']}]({s['path']})" for s in sections)
        (skill_dir / "SKILL.md").write_text(
            f"---\nname: {name}\ndescription: {desc}\nskill_type: graph\nfile_count: {len(files)}\n---\n\n# {name}\n\n{desc}\n\n## Table of Contents\n\n{toc}\n",
            encoding="utf-8",
        )
        return {
            "skill_dir": str(skill_dir),
            "file_count": len(files),
            "version": 1,
            "validation_errors": [],
        }

    def distill_one(self, skill_dir: Path) -> dict:
        """Write an extractive ``OVERVIEW.md``: headings plus each section's lead."""
        skill_dir = Path(skill_dir)
        index = json.loads((skill_dir / "index.json").read_text(encoding="utf-8"))
        lines = [f"# Overview of {index.get('name', skill_dir.name)}", ""]
        for s in index.get("sections", []):
            body = (skill_dir / s["path"]).read_text(encoding="utf-8")
            lead = next(
                (p.strip() for p in re.split(r"\n\s*\n", body) if p.strip() and not p.lstrip().startswith("#")),
                "",
            )
            lines.append(f"- **{s['title']}** — {lead[:200]}")
        (skill_dir / "OVERVIEW.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
        return {"status": "distilled"}

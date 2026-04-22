#!/usr/bin/env python3
import os
import re
import argparse
import shutil
import datetime
from pathlib import Path


def extract_title(file_path: Path) -> str:
    """Extract title from YAML frontmatter, then H1, then humanized filename."""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read(4000)  # first chunk is enough

        # YAML frontmatter
        fm_match = re.search(
            r"^---\s*\n(.*?)\n---\s*\n", content, re.DOTALL | re.MULTILINE
        )
        if fm_match:
            fm = fm_match.group(1)
            title_match = re.search(
                r"^\s*title\s*:\s*['\"]?(.*?)['\"]?\s*$",
                fm,
                re.MULTILINE | re.IGNORECASE,
            )
            if title_match:
                title = title_match.group(1).strip()
                # strip surrounding quotes if present
                title = re.sub(r'^["\']|["\']$', "", title)
                if title:
                    return title

        # First # header
        h1_match = re.search(r"^#\s+(.+)", content, re.MULTILINE)
        if h1_match:
            return h1_match.group(1).strip()

    except Exception:
        pass

    # Fallback: humanize filename
    name = file_path.stem.replace("-", " ").replace("_", " ")
    return name.title()


def extract_source_url(skill_dir: Path) -> str | None:
    """Look for source_url in an existing SKILL.md."""
    skill_md = skill_dir / "SKILL.md"
    if not skill_md.exists():
        return None
    try:
        with open(skill_md, "r", encoding="utf-8") as f:
            content = f.read()
            match = re.search(r"source_url:\s*(.+)", content)
            if match:
                return match.group(1).strip()
    except Exception:
        pass
    return None


def build_doc_tree(reference_dir: Path) -> dict:
    """Build nested dict tree of only .md files (dirs first, then files)."""
    md_files = list(reference_dir.rglob("*.md"))
    tree: dict = {}

    for md_file in md_files:
        rel = md_file.relative_to(reference_dir)
        current = tree
        for part in rel.parts[:-1]:
            if part not in current:
                current[part] = {}
            current = current[part]
        # leaf = (title, link)
        title = extract_title(md_file)
        link = f"reference/{rel.as_posix()}"
        current[rel.name] = (title, link)

    return tree


def render_toc(tree: dict, indent: int = 0) -> list[str]:
    """Recursively render beautiful hierarchical Markdown TOC."""
    lines: list[str] = []

    # Folders first, then files, alphabetical within each group
    dirs = [k for k in tree if isinstance(tree[k], dict)]
    files = [k for k in tree if not isinstance(tree[k], dict)]

    for key in sorted(dirs) + sorted(files):
        item = tree[key]
        if isinstance(item, dict):
            # Directory
            lines.append("  " * indent + f"- 📁 **{key}/**")
            lines.extend(render_toc(item, indent + 1))
        else:
            # File
            title, link = item
            lines.append("  " * indent + f"- [{title}]({link})")

    return lines


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
):
    # Enforce -docs suffix
    if not skill_name.endswith("-docs"):
        skill_name = f"{skill_name}-docs"
        print(f"🏷️  Enforcing naming convention: Renamed skill to **{skill_name}**")

    base_pkg_path = Path(__file__).resolve().parent.parent.parent.parent
    # If --output-dir is provided, use it directly as the parent for the skill
    if output_dir:
        target_skill_dir = Path(output_dir) / skill_name
    elif target_type == "skills":
        skills_base = Path(__file__).resolve().parent.parent.parent
        target_skill_dir = skills_base / skill_name
    elif target_type == "skill-graphs":
        # Check if skill-graphs repo exists in the same workspace (agent-packages/)
        # base_pkg_path is .../universal-skills/universal_skills/
        # base_pkg_path.parent is .../universal-skills/
        # base_pkg_path.parent.parent is .../agent-packages/
        workspace_root = base_pkg_path.parent.parent
        skill_graphs_repo = workspace_root / "skill-graphs"

        if skill_graphs_repo.exists() and (skill_graphs_repo / "skill_graphs").is_dir():
            target_skill_dir = skill_graphs_repo / "skill_graphs" / skill_name
        else:
            # Fallback to local cache if repo not found
            cache_base = os.environ.get(
                "XDG_CACHE_HOME", os.path.expanduser("~/.cache")
            )
            target_skill_dir = (
                Path(cache_base) / "universal-skills" / "skill-graphs" / skill_name
            )
    else:
        target_skill_dir = base_pkg_path / target_type / skill_name

    reference_dir = target_skill_dir / "reference"

    sources = [s.strip() for s in source_input.split(",")]
    source_urls = []

    # Create fresh target
    target_skill_dir.mkdir(parents=True, exist_ok=True)
    if not append:
        if reference_dir.exists():
            shutil.rmtree(reference_dir)
        reference_dir.mkdir(parents=True, exist_ok=True)
    else:
        reference_dir.mkdir(parents=True, exist_ok=True)

    crawl_urls = []
    local_sources = []
    pdf_urls = []
    local_pdfs = []

    for source in sources:
        if source.startswith("http"):
            if source.lower().split("?")[0].endswith(".pdf"):
                pdf_urls.append(source)
            else:
                crawl_urls.append(source)
        else:
            local_path = Path(source)
            if local_path.is_file() and local_path.suffix.lower() in [
                ".pdf",
                ".docx",
                ".pptx",
                ".xlsx",
                ".csv",
            ]:
                local_pdfs.append(local_path)
            elif local_path.is_dir():
                extracted_url = extract_source_url(local_path)
                if extracted_url:
                    print(f"🔄 Found source_url in existing skill: {extracted_url}")
                    # If it's a list, split it
                    for url in extracted_url.split(","):
                        url_stripped = url.strip()
                        if (
                            url_stripped.lower().split("?")[0].endswith(".pdf")
                            or url_stripped.lower().split("?")[0].endswith(".docx")
                            or url_stripped.lower().split("?")[0].endswith(".pptx")
                            or url_stripped.lower().split("?")[0].endswith(".xlsx")
                            or url_stripped.lower().split("?")[0].endswith(".csv")
                        ):
                            pdf_urls.append(url_stripped)
                        else:
                            crawl_urls.append(url_stripped)
                else:
                    local_sources.append(local_path)
            else:
                local_sources.append(local_path)

    # 1. Handle Documents (PDF, Office files) (Local and Remote)
    if pdf_urls or local_pdfs:
        markitdown_instance = None
        try:
            from markitdown import MarkItDown

            markitdown_instance = MarkItDown()
        except ImportError:
            try:
                import pymupdf4llm

                print(
                    "⚠️ markitdown not installed. Falling back to pymupdf4llm for PDF conversion (Office files may fail)."
                )
            except ImportError:
                print(
                    "❌ markitdown and pymupdf4llm not installed. Please install with `pip install 'universal-skills[skill-graph-builder]'`."
                )
                pymupdf4llm = None

        if markitdown_instance or pymupdf4llm:
            import tempfile
            import requests

            for doc_url in pdf_urls:
                print(f"📄 Processing remote document: {doc_url}")
                try:
                    response = requests.get(doc_url, stream=True)
                    response.raise_for_status()

                    # Extract extension or default to .pdf
                    ext = Path(doc_url.split("?")[0]).suffix.lower()
                    if not ext:
                        ext = ".pdf"

                    with tempfile.NamedTemporaryFile(delete=False, suffix=ext) as tmp:
                        for chunk in response.iter_content(chunk_size=8192):
                            tmp.write(chunk)
                        tmp_path = tmp.name

                    if markitdown_instance:
                        md_text = markitdown_instance.convert(tmp_path).text_content
                    else:
                        md_text = pymupdf4llm.to_markdown(tmp_path)

                    os.unlink(tmp_path)

                    filename = Path(doc_url.split("?")[0]).stem + ".md"
                    target_file = reference_dir / filename
                    target_file.write_text(md_text, encoding="utf-8")
                    source_urls.append(doc_url)
                except Exception as e:
                    print(f"❌ Failed to process remote document {doc_url}: {e}")

            for local_doc in local_pdfs:
                print(f"📄 Processing local document: {local_doc}")
                try:
                    if markitdown_instance:
                        md_text = markitdown_instance.convert(
                            str(local_doc)
                        ).text_content
                    else:
                        md_text = pymupdf4llm.to_markdown(str(local_doc))

                    filename = local_doc.stem + ".md"
                    target_file = reference_dir / filename
                    target_file.write_text(md_text, encoding="utf-8")
                except Exception as e:
                    print(f"❌ Failed to process local document {local_doc}: {e}")

    # 2. Handle all URLs in one crawl session if possible (faster for recursion)
    if crawl_urls:
        source_urls.extend(crawl_urls)
        crawl_script = base_pkg_path / "skills" / "web-crawler" / "scripts" / "crawl.py"

        # Determine strategy: if any are sitemaps, we might need a mix, but for simplicity
        # we'll use recursive if most are standard URLs.
        strategy = "recursive"
        if len(crawl_urls) == 1 and crawl_urls[0].endswith(".xml"):
            strategy = "sitemap-parallel"

        print(
            f"🌐 Crawling {len(crawl_urls)} URLs using {strategy} (depth={max_depth})..."
        )

        # If recursive docs (especially complex SPAs like ServiceNow), we use isolated
        # batch crawling (one process per URL) to ensure a fresh browser context per seed.
        urls_to_process = (
            crawl_urls if strategy == "recursive" else [",".join(crawl_urls)]
        )

        import subprocess

        for i, url_group in enumerate(urls_to_process):
            active_urls = [u.strip() for u in url_group.split(",")]
            # Print status without revealing absolute paths for cleaner terminal output
            print(
                f"   [{i + 1}/{len(urls_to_process)}] Processing: {', '.join(active_urls)}"
            )

            # Use a unique temporary directory per batch
            temp_crawl_dir = Path(f"/tmp/crawl_{skill_name}_{i}")
            if temp_crawl_dir.exists():
                shutil.rmtree(temp_crawl_dir)
            temp_crawl_dir.mkdir(parents=True, exist_ok=True)

            cmd = (
                [
                    "python3",
                    str(crawl_script),
                    "--urls",
                ]
                + active_urls
                + [
                    "--strategy",
                    strategy,
                    "--output-dir",
                    str(temp_crawl_dir),
                ]
            )
            if strategy == "recursive":
                cmd.extend(["--max-depth", str(max_depth)])
                cmd.extend(["--max-pages", str(max_pages)])

            if disable_magic_js:
                cmd.append("--disable-magic-js")
            if no_sitemap:
                cmd.append("--no-sitemap")
            if wait_for:
                cmd.extend(["--wait-for", wait_for])

            try:
                subprocess.run(cmd, check=True)
                print(f"   📂 Merging documentation into {reference_dir}...")
                shutil.copytree(temp_crawl_dir, reference_dir, dirs_exist_ok=True)
            except subprocess.CalledProcessError as e:
                print(f"   ❌ Crawl failed for {url_group}: {e}")
            finally:
                if temp_crawl_dir.exists():
                    shutil.rmtree(temp_crawl_dir)

    # 2. Handle local sources
    for i, source_path in enumerate(local_sources):
        if source_path.is_dir():
            # If user passed an existing skill folder, use its reference/ subfolder
            skill_md = source_path / "SKILL.md"
            ref_sub = source_path / "reference"
            if skill_md.exists() and ref_sub.exists():
                print(
                    f"📁 Detected existing skill – using reference/ subfolder: {source_path}"
                )
                source_path = ref_sub

            print(
                f"📂 Merging local directory from {source_path} into {reference_dir}..."
            )
            shutil.copytree(source_path, reference_dir, dirs_exist_ok=True)
        elif source_path.is_file():
            print(f"📂 Merging local file {source_path} into {reference_dir}...")
            shutil.copyfile(source_path, reference_dir / source_path.name)

    # 3. Split overly large markdown files
    if max_file_kb > 0:
        import subprocess

        max_bytes = max_file_kb * 1024
        md_files = list(reference_dir.rglob("*.md"))
        for md_file in md_files:
            try:
                if md_file.stat().st_size > max_bytes:
                    print(
                        f"✂️  Splitting large file: {md_file.name} ({md_file.stat().st_size // 1024} KB)"
                    )
                    output_folder = md_file.parent / md_file.stem
                    if output_folder.exists():
                        shutil.rmtree(output_folder)
                    output_folder.mkdir(parents=True, exist_ok=True)

                    cmd = [
                        "mdsplit",
                        str(md_file),
                        "--max-level",
                        "1",
                        "--table-of-contents",
                        "--output",
                        str(output_folder),
                        "--force",
                    ]
                    subprocess.run(
                        cmd,
                        check=True,
                        stdout=subprocess.DEVNULL,
                        stderr=subprocess.DEVNULL,
                    )

                    # Check if any resulting split files are still too large
                    needs_level_2 = False
                    for split_file in output_folder.rglob("*.md"):
                        if split_file.stat().st_size > max_bytes:
                            needs_level_2 = True
                            break

                    if needs_level_2:
                        print(
                            "   ⚠️  Still too large after level 1 split, trying level 2 split..."
                        )
                        shutil.rmtree(output_folder)
                        output_folder.mkdir(parents=True, exist_ok=True)
                        cmd = [
                            "mdsplit",
                            str(md_file),
                            "--max-level",
                            "2",
                            "--table-of-contents",
                            "--output",
                            str(output_folder),
                            "--force",
                        ]
                        subprocess.run(
                            cmd,
                            check=True,
                            stdout=subprocess.DEVNULL,
                            stderr=subprocess.DEVNULL,
                        )

                    # --- Emergency Fallback Split ---
                    # If MarkItDown produced a PDF with NO markdown headers, mdsplit will fail
                    # and leave a massive file in the output_folder (or just one file).
                    for split_file in list(output_folder.rglob("*.md")):
                        if (
                            split_file.stat().st_size > max_bytes
                            and split_file.name != "toc.md"
                        ):
                            print(
                                f"   ⚠️  File {split_file.name} still too large ({split_file.stat().st_size // 1024} KB). Forcing chunk by lines."
                            )
                            with open(split_file, "r", encoding="utf-8") as f:
                                lines = f.readlines()

                            if not lines:
                                continue

                            # Target bytes per chunk (safely under max_bytes)
                            target_chunk_bytes = (
                                max_bytes - (50 * 1024)
                                if max_bytes > (50 * 1024)
                                else max_bytes // 2
                            )
                            if target_chunk_bytes <= 0:
                                target_chunk_bytes = max_bytes

                            current_chunk = []
                            current_bytes = 0
                            chunk_index = 1

                            # Keep original name prefix
                            base_name = split_file.stem

                            for line in lines:
                                current_chunk.append(line)
                                current_bytes += len(line.encode("utf-8"))

                                if current_bytes >= target_chunk_bytes:
                                    chunk_file = (
                                        output_folder
                                        / f"{base_name}_pt{chunk_index}.md"
                                    )
                                    chunk_file.write_text(
                                        "".join(current_chunk), encoding="utf-8"
                                    )
                                    chunk_index += 1
                                    current_chunk = []
                                    current_bytes = 0

                            if current_chunk:
                                chunk_file = (
                                    output_folder / f"{base_name}_pt{chunk_index}.md"
                                )
                                chunk_file.write_text(
                                    "".join(current_chunk), encoding="utf-8"
                                )

                            split_file.unlink()  # Delete the oversized un-splittable chunk

                    md_file.unlink()  # Delete the original big file
            except Exception as e:
                print(f"❌ Failed to split {md_file.name}: {e}")

    # --- Preserve or set description ---
    if not description:
        existing_md = target_skill_dir / "SKILL.md"
        if existing_md.exists():
            try:
                with open(existing_md, "r", encoding="utf-8") as f:
                    match = re.search(r"description:\s*(.+)", f.read())
                    if match:
                        description = match.group(1).strip()
            except Exception:
                pass
        if not description:
            description = f"Comprehensive reference documentation for {skill_name.replace('-', ' ').title()}."

    # --- Build hierarchical TOC ---
    doc_tree = build_doc_tree(reference_dir)
    toc_lines = render_toc(doc_tree)
    md_count = len(list(reference_dir.rglob("*.md")))

    # --- Write polished SKILL.md ---
    skill_md_path = target_skill_dir / "SKILL.md"
    with open(skill_md_path, "w", encoding="utf-8") as f:
        f.write("---\n")
        f.write(f"name: {skill_name}\n")
        f.write(f"description: {description}\n")
        f.write(f"crawl_depth: {max_depth}\n")
        if source_urls:
            f.write(f"source_url: {', '.join(source_urls)}\n")
        f.write("categories: [Documentation, Knowledge Base, Reference]\n")
        f.write(f"tags: [docs, reference, {skill_name}, knowledge-base]\n")
        f.write("---\n\n")

        f.write(
            f"# {skill_name.replace('-', ' ').replace('Docs', '').strip().title()} Documentation\n\n"
        )
        f.write(f"{description}\n\n")

        if source_urls:
            f.write("**Original Sources**:\n")
            for url in source_urls:
                f.write(f"- [{url}]({url})\n")
            f.write("\n")

        f.write(
            f"**Contains**: {md_count} markdown files with full folder structure (crawled at depth {max_depth}).\n"
        )
        f.write(f"*Last updated: {datetime.datetime.now().strftime('%B %d, %Y')}*\n\n")

        f.write("## 📚 Table of Contents\n\n")
        if toc_lines:
            f.write("\n".join(toc_lines) + "\n\n")
        else:
            f.write("*No markdown files found.*\n\n")

        f.write("## 🤖 Agent Usage Guide\n\n")
        f.write(
            f"- When the user asks anything about **{skill_name.replace('-', ' ').title()}**, consult the reference files.\n"
        )
        f.write(
            "- Prefer exact quotes and direct links to the relevant file/section.\n"
        )
        f.write("- The hierarchical TOC above makes navigation fast and intuitive.\n")
        f.write("- All images and assets are preserved so links work perfectly.\n\n")

    print(
        f"✅ Successfully created polished {target_type[:-1]}: **{skill_name}** at {target_skill_dir}"
    )
    print(f"   📊 {md_count} documentation files • Hierarchical TOC ready")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Generate a beautiful, hierarchical agent skill / skill-graph from markdown docs or a URL."
    )
    parser.add_argument(
        "source",
        help="Comma-separated list of markdown directories or starting URLs.",
    )
    parser.add_argument(
        "skill_name", help="Name of the skill (kebab-case recommended)."
    )
    parser.add_argument("--description", help="Optional description for the skill.")
    parser.add_argument(
        "--max-depth",
        type=int,
        default=2,
        help="Max depth for recursive web crawl (default: 2).",
    )
    parser.add_argument(
        "--target-type",
        choices=["skills", "skill-graphs"],
        default="skill-graphs",
        help="Target directory type (default: skill-graphs).",
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
        help="Custom output directory. If provided, the skill is created at <output-dir>/<skill-name>/ instead of the default location.",
    )
    parser.add_argument(
        "--no-sitemap", action="store_true", help="Disable sitemap auto-discovery"
    )
    parser.add_argument(
        "--max-pages",
        type=int,
        default=1000,
        help="Limit the total number of pages crawled in recursive mode.",
    )
    parser.add_argument(
        "--disable-magic-js",
        action="store_true",
        help="Disable the complex MAGIC_JS payload in web-crawler.",
    )
    parser.add_argument(
        "--wait-for",
        type=str,
        help="Custom CSS selector or JS expression to wait for in web-crawler.",
    )
    parser.add_argument(
        "--append",
        action="store_true",
        help="Append to existing reference files instead of wiping them.",
    )

    args = parser.parse_args()
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
    )

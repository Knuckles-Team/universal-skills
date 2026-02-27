#!/usr/bin/env python3
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
    target_type: str = "skills",
):
    # Enforce -docs suffix
    if not skill_name.endswith("-docs"):
        skill_name = f"{skill_name}-docs"
        print(f"🏷️  Enforcing naming convention: Renamed skill to **{skill_name}**")

    base_pkg_path = Path(__file__).resolve().parent.parent.parent.parent
    target_skill_dir = base_pkg_path / target_type / skill_name
    reference_dir = target_skill_dir / "reference"

    sources = [s.strip() for s in source_input.split(",")]
    source_urls = []

    # Create fresh target
    target_skill_dir.mkdir(parents=True, exist_ok=True)
    if reference_dir.exists():
        shutil.rmtree(reference_dir)
    reference_dir.mkdir(parents=True, exist_ok=True)

    for i, source in enumerate(sources):
        # --- Rebuild from source_url if we were given an existing skill folder ---
        if not source.startswith("http"):
            local_path = Path(source)
            if local_path.is_dir():
                extracted_url = extract_source_url(local_path)
                if extracted_url:
                    print(
                        f"🔄 Found source_url in existing skill. Rebuilding from {extracted_url}..."
                    )
                    source = extracted_url

        is_from_url = source.startswith("http")
        temp_crawl_dir: Path | None = None

        if is_from_url:
            source_urls.append(source)
            temp_crawl_dir = Path(f"/tmp/crawl_{skill_name}_{i}")
            if temp_crawl_dir.exists():
                shutil.rmtree(temp_crawl_dir)
            temp_crawl_dir.mkdir(parents=True, exist_ok=True)

            crawl_script = (
                base_pkg_path / "skills" / "web-crawler" / "scripts" / "crawl.py"
            )
            strategy = "sitemap-parallel" if source.endswith(".xml") else "recursive"

            print(
                f"🌐 [{i+1}/{len(sources)}] Crawling {source} using {strategy} (depth={max_depth})..."
            )
            cmd = [
                "python3",
                str(crawl_script),
                source,
                "--strategy",
                strategy,
                "--output-dir",
                str(temp_crawl_dir),
            ]
            if strategy == "recursive":
                cmd.extend(["--max-depth", str(max_depth)])

            import subprocess

            subprocess.run(cmd, check=True)
            source_path = temp_crawl_dir
        else:
            source_path = Path(source)
            # If user passed an existing skill folder, use its reference/ subfolder
            skill_md = source_path / "SKILL.md"
            ref_sub = source_path / "reference"
            if skill_md.exists() and ref_sub.exists():
                print(
                    f"📁 [{i+1}/{len(sources)}] Detected existing skill – using reference/ subfolder."
                )
                source_path = ref_sub

        print(f"📂 Merging documentation from {source_path} into {reference_dir}...")
        # Use shutil.copytree with dirs_exist_ok=True for merging
        shutil.copytree(source_path, reference_dir, dirs_exist_ok=True)

        # Cleanup temp crawl
        if temp_crawl_dir and temp_crawl_dir.exists():
            shutil.rmtree(temp_crawl_dir)

    print("🧹 Cleaned up temporary crawl directories.")

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
            f"**Contains**: {md_count} markdown files with full folder structure.\n"
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
        default="skills",
        help="Target directory type (default: skills).",
    )

    args = parser.parse_args()
    generate_skill(
        args.source,
        args.skill_name,
        args.description,
        args.max_depth,
        args.target_type,
    )

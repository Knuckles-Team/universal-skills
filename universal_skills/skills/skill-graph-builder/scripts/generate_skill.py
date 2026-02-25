#!/usr/bin/env python3
import re
import argparse
import shutil
from pathlib import Path


def extract_title(file_path):
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            for line in f:
                match = re.match(r"^#\s+(.+)", line)
                if match:
                    return match.group(1).strip()
    except Exception:
        pass
    return file_path.name


def extract_source_url(skill_dir):
    skill_md = Path(skill_dir) / "SKILL.md"
    if skill_md.exists():
        try:
            with open(skill_md, "r", encoding="utf-8") as f:
                content = f.read()
                match = re.search(r"source_url:\s*(.+)", content)
                if match:
                    return match.group(1).strip()
        except Exception:
            pass
    return None


def generate_skill(
    source_dir_or_url, skill_name, description=None, max_depth=2, target_type="skills"
):
    base_pkg_path = Path(
        "/home/genius/Workspace/agent-packages/universal-skills/universal_skills"
    )
    target_skill_dir = base_pkg_path / target_type / skill_name
    reference_dir = target_skill_dir / "reference"

    source_url = None

    # If source is a local directory, check if it has a source_url for rebuilding
    if not source_dir_or_url.startswith("http"):
        local_path = Path(source_dir_or_url)
        if local_path.is_dir():
            extracted_url = extract_source_url(local_path)
            if extracted_url:
                print(f"Found source_url in existing skill: {extracted_url}")
                print(f"Rebuilding {skill_name} from {extracted_url}...")
                source_dir_or_url = extracted_url

    # If source is a URL, crawl it first
    if source_dir_or_url.startswith("http"):
        source_url = source_dir_or_url
        url = source_dir_or_url
        temp_crawl_dir = Path(f"/tmp/crawl_{skill_name}")
        if temp_crawl_dir.exists():
            shutil.rmtree(temp_crawl_dir)
        temp_crawl_dir.mkdir(parents=True, exist_ok=True)

        crawl_script = base_pkg_path / "skills" / "web-crawler" / "scripts" / "crawl.py"

        # Determine if it's a sitemap or a site
        strategy = "recursive"
        if url.endswith(".xml"):
            strategy = "sitemap-parallel"

        import subprocess

        print(f"Crawling {url} using {strategy} strategy (max-depth={max_depth})...")
        cmd = [
            "python3",
            str(crawl_script),
            url,
            "--strategy",
            strategy,
            "--output-dir",
            str(temp_crawl_dir),
        ]
        if strategy == "recursive":
            cmd.extend(["--max-depth", str(max_depth)])

        subprocess.run(cmd, check=True)
        source_path = temp_crawl_dir
    else:
        source_path = Path(source_dir_or_url)

    # Create directories
    target_skill_dir.mkdir(parents=True, exist_ok=True)
    reference_dir.mkdir(parents=True, exist_ok=True)

    # Copy files
    md_files = sorted(list(source_path.glob("*.md")))
    for md_file in md_files:
        shutil.copy(md_file, reference_dir / md_file.name)

    # Generate SKILL.md
    if not description:
        # Try to preserve description from existing SKILL.md
        existing_md = target_skill_dir / "SKILL.md"
        if existing_md.exists():
            try:
                with open(existing_md, "r", encoding="utf-8") as f:
                    content = f.read()
                    match = re.search(r"description:\s*(.+)", content)
                    if match:
                        description = match.group(1).strip()
            except Exception:
                pass

        if not description:
            description = f"Local documentation skill for {skill_name}."

    skill_md_path = target_skill_dir / "SKILL.md"

    with open(skill_md_path, "w", encoding="utf-8") as f:
        f.write("---\n")
        f.write(f"name: {skill_name}\n")
        f.write(f"description: {description}\n")
        if source_url:
            f.write(f"source_url: {source_url}\n")
        f.write("categories: [Documentation, Knowledge Base]\n")
        f.write(f"tags: [docs, {skill_name}, reference]\n")
        f.write("---\n\n")
        f.write(f"# {skill_name.replace('-', ' ').title()} Documentation\n\n")
        f.write(f"{description}\n\n")
        if source_url:
            f.write(f"**Source URL**: {source_url}\n\n")
        f.write("## Reference Files\n\n")

        for md_file in md_files:
            title = extract_title(md_file)
            f.write(f"- [{title}](file://{reference_dir.absolute()}/{md_file.name})\n")

    print(
        f"Successfully created {target_type[:-1]}: {skill_name} at {target_skill_dir}"
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Generate an agent skill/skill-graph from a directory of markdown files or a URL."
    )
    parser.add_argument(
        "source", help="Directory containing markdown files or a starting URL."
    )
    parser.add_argument("skill_name", help="Name of the skill to create.")
    parser.add_argument("--description", help="Description for the skill.")
    parser.add_argument(
        "--max-depth",
        type=int,
        default=2,
        help="Max depth for recursive crawl (default: 2).",
    )
    parser.add_argument(
        "--target-type",
        choices=["skills", "skill-graphs"],
        default="skills",
        help="Target directory type (default: skills).",
    )

    args = parser.parse_args()
    generate_skill(
        args.source, args.skill_name, args.description, args.max_depth, args.target_type
    )

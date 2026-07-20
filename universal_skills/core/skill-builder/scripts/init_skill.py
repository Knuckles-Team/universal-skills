#!/usr/bin/env python3
"""Create and validate one atomic universal skill."""

from __future__ import annotations

import argparse
import re
import shutil
import sys
from pathlib import Path
from typing import Any, Sequence

try:
    import yaml
except ImportError:  # pragma: no cover - the skill extra installs PyYAML
    yaml = None

NAME_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
TRIGGER_RE = re.compile(r"\buse when\b", re.IGNORECASE)
STEP_RE = re.compile(r"^###\s+Step\s+\d+:", re.MULTILINE | re.IGNORECASE)
RESOURCE_NAMES = ("scripts", "references", "assets")
WORKFLOW_KEYS = {"agent", "team_config", "depends_on", "cron"}
SENSITIVE_NAMES = {".env", "credentials.json", "secrets.json"}
SENSITIVE_SUFFIXES = {".key", ".pem", ".p12", ".pfx"}
DESCRIPTION_MAX = 1024


def title_case_skill_name(skill_name: str) -> str:
    """Convert a kebab-case skill name to a display title."""
    return " ".join(word.capitalize() for word in skill_name.split("-"))


def validate_name(name: str, *, label: str = "skill name") -> list[str]:
    """Return naming errors for a catalog identifier."""
    errors: list[str] = []
    if not NAME_RE.fullmatch(name):
        errors.append(f"{label} must use lowercase kebab-case")
    if len(name) > 64:
        errors.append(f"{label} must be at most 64 characters")
    return errors


def validate_description(description: str) -> list[str]:
    """Return routing-description errors."""
    errors: list[str] = []
    if not description.strip():
        errors.append("description must not be empty")
    elif len(description) > DESCRIPTION_MAX:
        errors.append(f"description must be at most {DESCRIPTION_MAX} characters")
    if "<" in description or ">" in description:
        errors.append("description must not contain angle brackets")
    if not TRIGGER_RE.search(description):
        errors.append("description must include an explicit 'Use when' trigger")
    return errors


def validate_domain_path(domain_path: Path) -> tuple[str, list[str]]:
    """Validate a direct ``universal_skills/<domain>`` destination."""
    resolved = domain_path.resolve()
    domain = resolved.name
    errors = validate_name(domain, label="domain")
    if resolved.parent.name != "universal_skills":
        errors.append("--path must be a direct universal_skills/<domain> directory")
    if domain.endswith("-workflows"):
        errors.append(
            "skill-builder creates atomic skills only; use skill-workflow-builder "
            "for a *-workflows domain"
        )
    return domain, errors


def parse_resources(value: str | Sequence[str] | None) -> tuple[str, ...]:
    """Normalize and validate requested resource directory names."""
    if value is None:
        return ()
    items = value.split(",") if isinstance(value, str) else list(value)
    resources: list[str] = []
    for item in items:
        name = str(item).strip()
        if not name:
            continue
        if name not in RESOURCE_NAMES:
            choices = ", ".join(RESOURCE_NAMES)
            raise ValueError(f"unknown resource '{name}'; choose from {choices}")
        if name not in resources:
            resources.append(name)
    return tuple(resources)


def _split_frontmatter(text: str) -> tuple[dict[str, Any], str, str | None]:
    if not text.startswith("---"):
        return {}, text, "SKILL.md is missing YAML frontmatter"
    parts = text.split("---", 2)
    if len(parts) != 3:
        return {}, text, "SKILL.md has unterminated YAML frontmatter"
    if yaml is None:
        return {}, parts[2], "PyYAML is required to validate a skill"
    try:
        frontmatter = yaml.safe_load(parts[1]) or {}
    except yaml.YAMLError as exc:
        return {}, parts[2], f"invalid YAML frontmatter: {type(exc).__name__}"
    if not isinstance(frontmatter, dict):
        return {}, parts[2], "YAML frontmatter must be a mapping"
    return frontmatter, parts[2], None


def validate_atomic_skill(skill_path: Path) -> list[str]:
    """Validate the metadata, placement, and atomicity of one skill folder."""
    skill_path = skill_path.resolve()
    errors: list[str] = []
    if not skill_path.is_dir():
        return ["configured skill folder was not found"]

    skill_md = skill_path / "SKILL.md"
    if not skill_md.is_file():
        return ["SKILL.md was not found in the configured skill folder"]

    domain, domain_errors = validate_domain_path(skill_path.parent)
    errors.extend(domain_errors)
    text = skill_md.read_text(encoding="utf-8", errors="replace")
    frontmatter, body, parse_error = _split_frontmatter(text)
    if parse_error:
        return errors + [parse_error]

    name = str(frontmatter.get("name", ""))
    errors.extend(validate_name(name))
    if name != skill_path.name:
        errors.append(
            f"frontmatter name '{name}' must equal directory '{skill_path.name}'"
        )
    if frontmatter.get("domain") != domain:
        errors.append(f"frontmatter domain must equal containing domain '{domain}'")
    if frontmatter.get("skill_type") != "skill":
        errors.append("skill_type must be 'skill' for an atomic skill")

    errors.extend(validate_description(str(frontmatter.get("description", ""))))
    forbidden = sorted(WORKFLOW_KEYS.intersection(frontmatter))
    if forbidden:
        errors.append(
            "atomic skill contains workflow-only metadata: " + ", ".join(forbidden)
        )
    if STEP_RE.search(body):
        errors.append("atomic SKILL.md must not contain numbered workflow steps")
    if "ACTION REQUIRED" in text or re.search(r"\bTODO\b", text):
        errors.append("skill contains unfinished placeholder markers")

    for path in sorted(skill_path.rglob("*")):
        if path.is_symlink():
            errors.append(
                f"skill must not contain symlinks: {path.relative_to(skill_path)}"
            )
        if path.is_file() and (
            path.name.lower() in SENSITIVE_NAMES
            or path.suffix.lower() in SENSITIVE_SUFFIXES
        ):
            errors.append(
                f"skill contains a potentially sensitive file: {path.relative_to(skill_path)}"
            )
    return errors


def _render_skill(
    skill_name: str,
    domain: str,
    description: str,
    resources: Sequence[str],
    tags: Sequence[str],
    author: str,
    version: str,
) -> str:
    if yaml is None:  # pragma: no cover - checked by the CLI
        raise RuntimeError("PyYAML is required to initialize a skill")
    frontmatter = {
        "name": skill_name,
        "domain": domain,
        "skill_type": "skill",
        "description": description,
        "license": "MIT",
        "tags": list(tags) or [skill_name],
        "metadata": {"version": version, "author": author},
    }
    title = title_case_skill_name(skill_name)
    body = [
        f"# {title}",
        "",
        "## Purpose",
        "",
        description,
        "",
        "## Instructions",
        "",
        "Perform only the focused capability described above. Preserve the user's",
        "scope and constraints, inspect the relevant inputs, and report the result",
        "with enough evidence for the user to verify it.",
    ]
    if resources:
        body.extend(["", "## Resources", ""])
        labels = {
            "scripts": "Run deterministic helpers from `scripts/` when needed.",
            "references": "Read only the relevant guidance from `references/`.",
            "assets": "Reuse output materials from `assets/` rather than recreating them.",
        }
        body.extend(f"- {labels[resource]}" for resource in resources)
    fm = yaml.safe_dump(frontmatter, sort_keys=False, allow_unicode=True).strip()
    return f"---\n{fm}\n---\n\n" + "\n".join(body) + "\n"


def init_skill(
    skill_name: str,
    path: str | Path,
    description: str,
    resources: str | Sequence[str] | None = None,
    tags: Sequence[str] = (),
    author: str = "Genius",
    version: str = "1.2.1",
) -> Path | None:
    """Initialize one valid atomic skill and only requested resource directories."""
    domain_path = Path(path).resolve()
    domain, errors = validate_domain_path(domain_path)
    errors.extend(validate_name(skill_name))
    errors.extend(validate_description(description))
    try:
        requested_resources = parse_resources(resources)
    except ValueError as exc:
        errors.append(type(exc).__name__)
        requested_resources = ()
    if errors:
        for error in errors:
            print(f"Error: {error}", file=sys.stderr)
        return None
    if yaml is None:
        print(
            "Error: PyYAML is required; install universal-skills[skill-builder]",
            file=sys.stderr,
        )
        return None

    skill_dir = domain_path / skill_name
    if skill_dir.exists():
        print("Error: configured skill directory already exists", file=sys.stderr)
        return None

    try:
        skill_dir.mkdir(parents=True, exist_ok=False)
        content = _render_skill(
            skill_name,
            domain,
            description,
            requested_resources,
            tags,
            author,
            version,
        )
        (skill_dir / "SKILL.md").write_text(content, encoding="utf-8")
        for resource in requested_resources:
            (skill_dir / resource).mkdir()
    except OSError as exc:
        shutil.rmtree(skill_dir, ignore_errors=True)
        print(f"Error: failed to initialize skill: {type(exc).__name__}", file=sys.stderr)
        return None

    print(f"Created atomic skill: {skill_dir}")
    return skill_dir


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("skill_name", help="Lowercase kebab-case skill name")
    parser.add_argument(
        "--path",
        required=True,
        help="Direct universal_skills/<domain> destination",
    )
    parser.add_argument(
        "--description",
        required=True,
        help="Routing description containing what the skill does and 'Use when'",
    )
    parser.add_argument(
        "--resources",
        default="",
        help="Comma-separated subset of scripts,references,assets",
    )
    parser.add_argument("--tags", default="", help="Comma-separated tags")
    parser.add_argument("--author", default="Genius")
    parser.add_argument("--version", default="1.2.1")
    args = parser.parse_args(argv)

    tags = tuple(tag.strip() for tag in args.tags.split(",") if tag.strip())
    result = init_skill(
        args.skill_name,
        args.path,
        args.description,
        resources=args.resources,
        tags=tags,
        author=args.author,
        version=args.version,
    )
    return 0 if result else 1


if __name__ == "__main__":
    raise SystemExit(main())

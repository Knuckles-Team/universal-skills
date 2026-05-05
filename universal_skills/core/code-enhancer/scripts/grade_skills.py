#!/usr/bin/env python3
"""CE-026: Agent Skill Quality grading for code-enhancer skill.

Auto-discovers SKILL.md files in a repository, parses frontmatter and body,
then grades each skill against a rule engine ported from the skill-check
project (https://github.com/thedaviddias/skill-check).

Produces a 0-100 aggregate score with per-skill breakdowns and per-rule
diagnostics.  The scoring model uses five weighted categories matching the
skill-check quality-score algorithm:

    Frontmatter  30%
    Description  30%
    Body         20%
    Links        10%
    File/Meta    10%

CONCEPT:CE-026 — Agent Skill Quality
"""

import json
import os
import re
import sys
from pathlib import Path
from typing import Any

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

SKILL_DISCOVERY_PATTERNS = [
    "**/skills/*/SKILL.md",
    "**/SKILL.md",
    "**/.claude/skills/*/SKILL.md",
    "**/.cursor/skills/*/SKILL.md",
    "**/.gemini/skills/*/SKILL.md",
]

KNOWN_FRONTMATTER_FIELDS = {
    "name",
    "description",
    "license",
    "compatibility",
    "metadata",
    "allowed-tools",
    # Extended fields used by universal-skills
    "categories",
    "tags",
    "version",
}

CATEGORY_WEIGHTS = {
    "frontmatter": 30,
    "description": 30,
    "body": 20,
    "links": 10,
    "file_meta": 10,
}

# Limits — aligned with skill-check defaults
MAX_DESCRIPTION_CHARS = 1024
MIN_DESCRIPTION_CHARS = 50
MAX_BODY_LINES = 500
MAX_BODY_TOKENS_APPROX = 5000
MAX_NAME_CHARS = 64

# ---------------------------------------------------------------------------
# Frontmatter parser (minimal YAML --- block)
# ---------------------------------------------------------------------------

def _parse_frontmatter(content: str) -> tuple[dict[str, Any] | None, str | None, str]:
    """Parse YAML frontmatter from SKILL.md content.

    Returns (parsed_dict | None, raw_frontmatter | None, body).
    """
    if not content.startswith("---"):
        return None, None, content

    end = content.find("\n---", 3)
    if end == -1:
        return None, None, content

    raw = content[3:end].strip()
    body = content[end + 4:].strip()

    # Simple YAML parser sufficient for flat key-value frontmatter
    parsed: dict[str, Any] = {}
    current_key = None
    current_value_lines: list[str] = []

    for line in raw.split("\n"):
        # Multi-line continuation (starts with whitespace)
        if line and line[0] in (" ", "\t") and current_key is not None:
            current_value_lines.append(line.strip())
            continue

        # Flush previous key
        if current_key is not None:
            val = " ".join(current_value_lines).strip()
            parsed[current_key] = _coerce_value(val)
            current_value_lines = []

        # New key: value
        match = re.match(r"^([a-zA-Z_-]+)\s*:\s*(.*)", line)
        if match:
            current_key = match.group(1).strip()
            current_value_lines = [match.group(2).strip()] if match.group(2).strip() else []
        else:
            current_key = None

    # Flush last key
    if current_key is not None:
        val = " ".join(current_value_lines).strip()
        parsed[current_key] = _coerce_value(val)

    return parsed, raw, body


def _coerce_value(val: str) -> Any:
    """Coerce a frontmatter string value to a richer type when obvious."""
    if not val:
        return ""
    # Strip wrapping quotes
    if (val.startswith('"') and val.endswith('"')) or (val.startswith("'") and val.endswith("'")):
        return val[1:-1]
    # YAML-style lists: [a, b, c]
    if val.startswith("[") and val.endswith("]"):
        items = [i.strip().strip("'\"") for i in val[1:-1].split(",")]
        return [i for i in items if i]
    # Multi-line >- continuation already joined
    if val.startswith(">-"):
        return val[2:].strip()
    return val


# ---------------------------------------------------------------------------
# Skill artifact builder
# ---------------------------------------------------------------------------

def _build_skill_artifact(skill_path: Path, root: Path) -> dict[str, Any]:
    """Build a skill artifact dict from a SKILL.md file."""
    content = skill_path.read_text(encoding="utf-8", errors="replace")
    rel_path = str(skill_path.relative_to(root))
    slug = skill_path.parent.name if skill_path.parent != root else skill_path.stem

    fm, fm_raw, body = _parse_frontmatter(content)

    return {
        "id": slug,
        "slug": slug,
        "file_path": str(skill_path),
        "relative_path": rel_path,
        "content": content,
        "body": body,
        "frontmatter": fm,
        "frontmatter_raw": fm_raw,
    }


# ---------------------------------------------------------------------------
# Rule engine — each rule returns a list of findings
# ---------------------------------------------------------------------------

def _normalize_name(name: Any) -> str:
    if not isinstance(name, str):
        return ""
    return name.strip("'\"").strip()


def _get_description(skill: dict) -> str:
    fm = skill.get("frontmatter")
    if not fm:
        return ""
    desc = fm.get("description", "")
    if not isinstance(desc, str):
        return str(desc).strip() if desc else ""
    return desc.strip()


# --- Frontmatter rules ---

def rule_frontmatter_required(skill: dict) -> list[dict]:
    if skill["frontmatter"] is not None:
        return []
    return [{"rule": "skill.frontmatter.required", "category": "frontmatter",
             "severity": "error", "penalty": 1.0,
             "message": "Missing or invalid YAML frontmatter (--- ... ---)",
             "suggestion": "Add YAML frontmatter: ---\\nname: my-skill\\ndescription: Use when ...\\n---"}]


def rule_frontmatter_name_required(skill: dict) -> list[dict]:
    fm = skill.get("frontmatter")
    if not fm:
        return []
    if fm.get("name"):
        return []
    return [{"rule": "skill.frontmatter.name_required", "category": "frontmatter",
             "severity": "error", "penalty": 1.0,
             "message": "Missing frontmatter 'name' field",
             "suggestion": f"Add 'name: {skill['slug']}' to frontmatter"}]


def rule_frontmatter_description_required(skill: dict) -> list[dict]:
    fm = skill.get("frontmatter")
    if not fm:
        return []
    if fm.get("description"):
        return []
    return [{"rule": "skill.frontmatter.description_required", "category": "frontmatter",
             "severity": "error", "penalty": 1.0,
             "message": "Missing frontmatter 'description' field",
             "suggestion": "Add a 'description:' field starting with 'Use when'"}]


def rule_frontmatter_name_matches_dir(skill: dict) -> list[dict]:
    fm = skill.get("frontmatter")
    if not fm:
        return []
    name = _normalize_name(fm.get("name", ""))
    if not name or name == skill["slug"]:
        return []
    return [{"rule": "skill.frontmatter.name_matches_directory", "category": "frontmatter",
             "severity": "error", "penalty": 1.0,
             "message": f"Name '{name}' does not match directory '{skill['slug']}'",
             "suggestion": f"Rename to 'name: {skill['slug']}' or rename the directory"}]


def rule_frontmatter_name_slug_format(skill: dict) -> list[dict]:
    fm = skill.get("frontmatter")
    if not fm:
        return []
    name = _normalize_name(fm.get("name", ""))
    if not name:
        return []
    if re.match(r"^[a-z0-9]+(?:-[a-z0-9]+)*$", name):
        return []
    return [{"rule": "skill.frontmatter.name_slug_format", "category": "frontmatter",
             "severity": "error", "penalty": 1.0,
             "message": "Name must use lowercase letters, numbers, and hyphens only",
             "suggestion": f"Use 'name: {skill['slug']}' (derived from directory name)"}]


def rule_frontmatter_name_max_length(skill: dict) -> list[dict]:
    fm = skill.get("frontmatter")
    if not fm:
        return []
    name = _normalize_name(fm.get("name", ""))
    if not name or len(name) <= MAX_NAME_CHARS:
        return []
    return [{"rule": "skill.frontmatter.name_max_length", "category": "frontmatter",
             "severity": "error", "penalty": 1.0,
             "message": f"Name length {len(name)} exceeds max {MAX_NAME_CHARS}",
             "suggestion": f"Shorten name to {MAX_NAME_CHARS} characters or fewer"}]


def rule_frontmatter_field_order(skill: dict) -> list[dict]:
    raw = skill.get("frontmatter_raw")
    if not raw:
        return []
    name_idx = raw.find("name:")
    desc_idx = raw.find("description:")
    if name_idx == -1 or desc_idx == -1 or name_idx < desc_idx:
        return []
    return [{"rule": "skill.frontmatter.field_order", "category": "frontmatter",
             "severity": "warn", "penalty": 0.5,
             "message": "Field order should be: name, then description",
             "suggestion": "Reorder so 'name:' comes before 'description:' in frontmatter"}]


def rule_frontmatter_unknown_fields(skill: dict) -> list[dict]:
    fm = skill.get("frontmatter")
    if not fm:
        return []
    unknown = [k for k in fm if k not in KNOWN_FRONTMATTER_FIELDS]
    if not unknown:
        return []
    return [{"rule": "skill.frontmatter.unknown_fields", "category": "frontmatter",
             "severity": "warn", "penalty": 0.5,
             "message": f"Unknown frontmatter fields: {', '.join(unknown)}",
             "suggestion": f"Recognized fields: {', '.join(sorted(KNOWN_FRONTMATTER_FIELDS))}"}]


# --- Description rules ---

def rule_description_non_empty(skill: dict) -> list[dict]:
    fm = skill.get("frontmatter")
    if not fm or "description" not in fm:
        return []
    desc = _get_description(skill)
    if desc:
        return []
    return [{"rule": "skill.description.non_empty", "category": "description",
             "severity": "error", "penalty": 1.0,
             "message": "Description is empty or whitespace-only",
             "suggestion": "Provide a meaningful description starting with 'Use when'"}]


def rule_description_max_length(skill: dict) -> list[dict]:
    desc = _get_description(skill)
    if not desc or len(desc) <= MAX_DESCRIPTION_CHARS:
        return []
    return [{"rule": "skill.description.max_length", "category": "description",
             "severity": "error", "penalty": 1.0,
             "message": f"Description length {len(desc)} exceeds max {MAX_DESCRIPTION_CHARS}",
             "suggestion": f"Shorten description to {MAX_DESCRIPTION_CHARS} characters or fewer"}]


def rule_description_use_when_phrase(skill: dict) -> list[dict]:
    desc = _get_description(skill)
    if not desc:
        return []
    if re.search(r"\buse\s+when\b", desc, re.IGNORECASE):
        return []
    return [{"rule": "skill.description.use_when_phrase", "category": "description",
             "severity": "warn", "penalty": 0.5,
             "message": "Description should contain 'Use when' phrasing",
             "suggestion": "Start description with 'Use when' to help agents match this skill"}]


def rule_description_min_length(skill: dict) -> list[dict]:
    desc = _get_description(skill)
    if not desc or len(desc) >= MIN_DESCRIPTION_CHARS:
        return []
    return [{"rule": "skill.description.min_recommended_length", "category": "description",
             "severity": "warn", "penalty": 0.5,
             "message": f"Description is short ({len(desc)} chars), recommended min is {MIN_DESCRIPTION_CHARS}",
             "suggestion": "Add more detail about when and why an agent should use this skill"}]


def rule_description_anti_trigger(skill: dict) -> list[dict]:
    """Check for 'Do NOT use' anti-trigger phrasing (best practice)."""
    desc = _get_description(skill)
    if not desc:
        return []
    if re.search(r"\bdo\s+not\s+use\b", desc, re.IGNORECASE):
        return []  # Has anti-trigger — good
    # Only warn if description is substantive
    if len(desc) > 80:
        return [{"rule": "skill.description.anti_trigger", "category": "description",
                 "severity": "warn", "penalty": 0.3,
                 "message": "Description lacks 'Do NOT use' anti-trigger phrasing",
                 "suggestion": "Add 'Do NOT use for ...' to prevent mismatched skill selection"}]
    return []


# --- Body rules ---

def rule_body_max_lines(skill: dict) -> list[dict]:
    body = skill.get("body", "")
    lines = body.split("\n")
    if len(lines) <= MAX_BODY_LINES:
        return []
    return [{"rule": "skill.body.max_lines", "category": "body",
             "severity": "error", "penalty": 1.0,
             "message": f"Body has {len(lines)} lines, max is {MAX_BODY_LINES}",
             "suggestion": "Split large body sections into references/*.md files"}]


def rule_body_max_tokens(skill: dict) -> list[dict]:
    body = skill.get("body", "")
    # Approximate token count: words + punctuation clusters
    token_count = len(body.split())
    if token_count <= MAX_BODY_TOKENS_APPROX:
        return []
    return [{"rule": "skill.body.max_tokens", "category": "body",
             "severity": "warn", "penalty": 0.5,
             "message": f"Body has ~{token_count} tokens, recommended max is {MAX_BODY_TOKENS_APPROX}",
             "suggestion": "Consider splitting oversized sections into reference files"}]


def rule_body_has_sections(skill: dict) -> list[dict]:
    """Check that the body has meaningful section structure."""
    body = skill.get("body", "")
    if not body.strip():
        return []
    sections = re.findall(r"^##\s+", body, re.MULTILINE)
    if len(sections) >= 2:
        return []
    return [{"rule": "skill.body.has_sections", "category": "body",
             "severity": "warn", "penalty": 0.5,
             "message": "Body lacks structured sections (fewer than 2 ## headings)",
             "suggestion": "Add ## sections to organize skill instructions for agents"}]


# --- Link rules ---

def rule_links_local_resolves(skill: dict) -> list[dict]:
    """Check that local markdown links resolve to existing files."""
    body = skill.get("body", "") + "\n" + (skill.get("frontmatter_raw") or "")
    skill_dir = Path(skill["file_path"]).parent
    findings: list[dict] = []

    # Match markdown links: [text](path) but not URLs
    for match in re.finditer(r"\[([^\]]*)\]\(([^)]+)\)", body):
        target = match.group(2)
        if target.startswith("http") or target.startswith("#") or target.startswith("mailto:"):
            continue
        # Resolve relative to skill directory
        resolved = skill_dir / target
        if not resolved.exists():
            findings.append({
                "rule": "skill.links.local_resolves", "category": "links",
                "severity": "warn", "penalty": 0.5,
                "message": f"Local link '{target}' does not resolve",
                "suggestion": f"Check that '{target}' exists relative to {skill_dir.name}/",
            })

    return findings


def rule_links_references_resolve(skill: dict) -> list[dict]:
    """Check that references/ directory files are valid if referenced."""
    skill_dir = Path(skill["file_path"]).parent
    refs_dir = skill_dir / "references"
    body = skill.get("body", "")

    if not refs_dir.is_dir():
        return []

    findings: list[dict] = []
    # Check if body references any references/ files
    for ref_file in refs_dir.iterdir():
        if ref_file.is_file() and ref_file.suffix == ".md":
            ref_name = f"references/{ref_file.name}"
            # Not a violation if not referenced — just check broken refs
            if ref_name in body:
                if not ref_file.exists():
                    findings.append({
                        "rule": "skill.links.references_resolve", "category": "links",
                        "severity": "warn", "penalty": 0.5,
                        "message": f"Referenced file '{ref_name}' does not exist",
                        "suggestion": "Create the referenced file or remove the reference",
                    })

    return findings


# --- File/Meta rules ---

def rule_file_trailing_newline(skill: dict) -> list[dict]:
    content = skill.get("content", "")
    if content.endswith("\n") and not content.endswith("\n\n"):
        return []
    if not content.endswith("\n"):
        return [{"rule": "skill.file.trailing_newline", "category": "file_meta",
                 "severity": "warn", "penalty": 0.5,
                 "message": "File does not end with a single trailing newline",
                 "suggestion": "Add a single trailing newline to the end of the file"}]
    return [{"rule": "skill.file.trailing_newline", "category": "file_meta",
             "severity": "warn", "penalty": 0.3,
             "message": "File ends with multiple trailing newlines",
             "suggestion": "Ensure exactly one trailing newline at end of file"}]


# --- Duplicate detection (cross-skill) ---

def check_duplicates(skills: list[dict]) -> list[dict]:
    """Detect duplicate names and descriptions across skills."""
    findings: list[dict] = []
    names: dict[str, list[str]] = {}
    descs: dict[str, list[str]] = {}

    for skill in skills:
        fm = skill.get("frontmatter")
        if not fm:
            continue
        name = _normalize_name(fm.get("name", ""))
        desc = _get_description(skill)

        if name:
            names.setdefault(name, []).append(skill["relative_path"])
        if desc and len(desc) > 20:
            descs.setdefault(desc, []).append(skill["relative_path"])

    for name, paths in names.items():
        if len(paths) > 1:
            for path in paths:
                findings.append({
                    "rule": "skill.duplicates.name", "category": "file_meta",
                    "severity": "warn", "penalty": 0.5,
                    "message": f"Duplicate skill name '{name}' shared with: {', '.join(p for p in paths if p != path)}",
                    "suggestion": "Each skill should have a unique name",
                    "file": path,
                })

    for desc, paths in descs.items():
        if len(paths) > 1:
            for path in paths:
                findings.append({
                    "rule": "skill.duplicates.description", "category": "file_meta",
                    "severity": "warn", "penalty": 0.5,
                    "message": f"Identical description shared with: {', '.join(p for p in paths if p != path)}",
                    "suggestion": "Each skill should have a unique description",
                    "file": path,
                })

    return findings


# ---------------------------------------------------------------------------
# Rule registry
# ---------------------------------------------------------------------------

RULES = [
    rule_frontmatter_required,
    rule_frontmatter_name_required,
    rule_frontmatter_description_required,
    rule_frontmatter_name_matches_dir,
    rule_frontmatter_name_slug_format,
    rule_frontmatter_name_max_length,
    rule_frontmatter_field_order,
    rule_frontmatter_unknown_fields,
    rule_description_non_empty,
    rule_description_max_length,
    rule_description_use_when_phrase,
    rule_description_min_length,
    rule_description_anti_trigger,
    rule_body_max_lines,
    rule_body_max_tokens,
    rule_body_has_sections,
    rule_links_local_resolves,
    rule_links_references_resolve,
    rule_file_trailing_newline,
]


# ---------------------------------------------------------------------------
# Scoring engine — weighted category model
# ---------------------------------------------------------------------------

def _categorize(rule_id: str) -> str:
    """Map rule ID to scoring category."""
    if "frontmatter" in rule_id:
        return "frontmatter"
    if "description" in rule_id:
        return "description"
    if "body" in rule_id:
        return "body"
    if "links" in rule_id or "references" in rule_id:
        return "links"
    return "file_meta"


def _compute_skill_score(diagnostics: list[dict]) -> dict:
    """Compute weighted quality score for a single skill.

    Uses the skill-check scoring model: each category starts at its weight
    value and is reduced by penalties.  Errors = 1.0 penalty, warns = 0.5.
    """
    penalties: dict[str, float] = {cat: 0.0 for cat in CATEGORY_WEIGHTS}

    for d in diagnostics:
        cat = _categorize(d["rule"])
        penalties[cat] += d.get("penalty", 0.5)

    breakdown: dict[str, int] = {}
    total = 0
    for cat, weight in CATEGORY_WEIGHTS.items():
        raw = max(0, weight - penalties[cat] * weight)
        breakdown[cat] = round(raw)
        total += breakdown[cat]

    return {
        "score": min(100, max(0, total)),
        "breakdown": breakdown,
    }


# ---------------------------------------------------------------------------
# Main discovery + grading pipeline
# ---------------------------------------------------------------------------

def discover_skills(root: Path) -> list[Path]:
    """Discover SKILL.md files in the repository."""
    found: set[Path] = set()
    for pattern in SKILL_DISCOVERY_PATTERNS:
        for match in root.glob(pattern):
            if match.is_file() and ".venv" not in str(match) and "node_modules" not in str(match):
                found.add(match.resolve())
    return sorted(found)


def grade_skills(root_dir: str = ".") -> dict:
    """Grade all agent skills found in the repository.

    Returns:
        dict with keys: domain, score, grade, findings, justifications, details,
                        skill_scores, skill_count
    """
    root = Path(root_dir).resolve()
    skill_paths = discover_skills(root)

    if not skill_paths:
        return {
            "domain": "Agent Skill Quality",
            "score": -1,  # N/A marker
            "grade": "N/A",
            "findings": ["No SKILL.md files detected — domain not applicable"],
            "justifications": [],
            "details": {"skill_count": 0, "skills_detected": False},
            "skill_scores": [],
        }

    # Build artifacts
    skills = [_build_skill_artifact(p, root) for p in skill_paths]

    # Run per-skill rules
    all_diagnostics: dict[str, list[dict]] = {s["relative_path"]: [] for s in skills}
    for skill in skills:
        for rule_fn in RULES:
            findings = rule_fn(skill)
            for f in findings:
                f["file"] = skill["relative_path"]
                all_diagnostics[skill["relative_path"]].append(f)

    # Run cross-skill duplicate detection
    dup_findings = check_duplicates(skills)
    for f in dup_findings:
        file_key = f.get("file", "")
        if file_key in all_diagnostics:
            all_diagnostics[file_key].append(f)

    # Score each skill
    skill_scores: list[dict] = []
    for skill in skills:
        diags = all_diagnostics[skill["relative_path"]]
        score_info = _compute_skill_score(diags)
        skill_scores.append({
            "id": skill["id"],
            "path": skill["relative_path"],
            "score": score_info["score"],
            "grade": _score_to_grade(score_info["score"]),
            "breakdown": score_info["breakdown"],
            "diagnostics": diags,
        })

    # Aggregate domain score = mean of per-skill scores
    if skill_scores:
        aggregate = round(sum(s["score"] for s in skill_scores) / len(skill_scores))
    else:
        aggregate = 0

    # Build findings and justifications
    all_findings: list[str] = []
    justifications: list[dict] = []

    all_findings.append(f"Discovered {len(skills)} agent skill(s)")
    for ss in skill_scores:
        all_findings.append(f"  {ss['id']}: {ss['grade']} ({ss['score']}/100)")
        if ss["diagnostics"]:
            top_issues = [d["message"] for d in ss["diagnostics"][:3]]
            for issue in top_issues:
                all_findings.append(f"    ⚠ {issue}")

    justifications.append({
        "criterion": "skill_count",
        "points": len(skills),
        "evidence": f"{len(skills)} SKILL.md files found",
        "reasoning": "Skills discovered via glob patterns",
    })

    error_count = sum(
        1 for diags in all_diagnostics.values()
        for d in diags if d["severity"] == "error"
    )
    warn_count = sum(
        1 for diags in all_diagnostics.values()
        for d in diags if d["severity"] == "warn"
    )

    justifications.append({
        "criterion": "diagnostics_summary",
        "points": aggregate,
        "evidence": f"{error_count} errors, {warn_count} warnings across {len(skills)} skills",
        "reasoning": f"Aggregate score: {aggregate}/100 (mean of per-skill scores)",
    })

    return {
        "domain": "Agent Skill Quality",
        "score": aggregate,
        "grade": _score_to_grade(aggregate),
        "findings": all_findings,
        "justifications": justifications,
        "details": {
            "skill_count": len(skills),
            "skills_detected": True,
            "error_count": error_count,
            "warning_count": warn_count,
        },
        "skill_scores": skill_scores,
    }


def _score_to_grade(score: int) -> str:
    """Convert 0-100 score to letter grade."""
    if score >= 90:
        return "A"
    if score >= 80:
        return "B"
    if score >= 70:
        return "C"
    if score >= 60:
        return "D"
    return "F"


if __name__ == "__main__":
    target = sys.argv[1] if len(sys.argv) > 1 else "."
    results = grade_skills(target)
    print(json.dumps(results, indent=2))

"""US-CONTENT: every bundled skill passes the connector-pack skill front-matter rule.

Mirrors the engine's ``valid_skill_frontmatter`` (medulla connector_pack import
validation) so provisioning never rejects a bundled skill with
``MALFORMED_BODY: skill front matter is absent, unsafe, or does not name the entry``.
"""

from __future__ import annotations

from pathlib import Path

import pytest

SKILLS = Path(__file__).resolve().parent.parent / "universal_skills" / "skills"
SKILL_TYPES = {"skill", "workflow", "graph", "mcp_skill"}
UNSAFE = "&*!{}"


def frontmatter_problem(body: bytes, expected_name: str) -> str | None:
    """Return why the engine would reject this SKILL.md, or None when accepted."""
    try:
        text = body.decode("utf-8")
    except UnicodeDecodeError:
        return "not UTF-8"
    if text.startswith("---\n"):
        rest = text[4:]
    elif text.startswith("---\r\n"):
        rest = text[5:]
    else:
        return "no opening fence"
    ends = [i for i in (rest.find("\n---\n"), rest.find("\r\n---\r\n")) if i >= 0]
    if not ends or ends[0] > 16 * 1024:
        return "no closing fence within 16 KiB"
    front = rest[: ends[0]]
    for line in front.splitlines():
        if any(c in line for c in UNSAFE) or line.strip() in ("---", "..."):
            return f"unsafe front-matter line: {line.strip()[:70]!r}"
    name = description = declared_type = None
    for line in front.splitlines():
        if line[:1].isspace() or line.lstrip().startswith("-"):
            continue
        if ":" not in line:
            return f"front-matter line without a colon: {line[:70]!r}"
        key, value = line.split(":", 1)
        value = value.strip()
        if key.strip() == "name":
            name = value.strip("'\"")
        elif key.strip() == "description":
            description = value
        elif key.strip() == "type":
            declared_type = " ".join(value.strip("'\"").split())
    if name != expected_name:
        return f"name {name!r} does not match the entry {expected_name!r}"
    if not description:
        return "description is empty"
    if declared_type and declared_type not in SKILL_TYPES:
        return f"type {declared_type!r} is not one of {sorted(SKILL_TYPES)}"
    return None


def _skills() -> list[Path]:
    return sorted(SKILLS.glob("*/SKILL.md"))


@pytest.mark.spec("US-CONTENT-R001.1")
def test_bundled_skills_exist() -> None:
    assert _skills()


@pytest.mark.spec("US-CONTENT-R001.1")
@pytest.mark.parametrize("path", _skills(), ids=lambda p: p.parent.name)
def test_skill_frontmatter_is_accepted_by_connector_pack_provisioning(path: Path) -> None:
    assert frontmatter_problem(path.read_bytes(), path.parent.name) is None


@pytest.mark.spec("US-CONTENT-R001.1")
@pytest.mark.parametrize(
    "body",
    [
        b"# no front matter\n",
        b"---\nname: demo\ndescription: S&P report\n---\n",
        b"---\nname: demo\ndescription: d\ncron:\n  schedule: \"*/5 * * * *\"\n---\n",
        b"---\nname: other\ndescription: d\n---\n",
        b"---\nname: demo\ndescription:\n---\n",
        b"---\nname: demo\ndescription: d\ntype: macro\n---\n",
    ],
)
def test_the_rule_rejects_what_the_engine_rejects(body: bytes) -> None:
    assert frontmatter_problem(body, "demo") is not None

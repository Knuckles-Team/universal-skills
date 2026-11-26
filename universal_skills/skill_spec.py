"""The skill spec model and the pure compile of a spec (US-CONTENT-R009).

A skill folder may hold ``skill.spec.yml``. ``compile_skill`` turns a validated
spec and the current ``SKILL.md`` text into new file contents. It reads no file
and writes no file, so a gate can run it in process.
"""

from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml

BEGIN = "<!-- spec:begin -->"
END = "<!-- spec:end -->"
SPEC_KEYS = (
    "goal",
    "outputs",
    "required_tool_actions",
    "forbidden_tool_actions",
    "target_agents",
    "target_models",
    "steps",
)
STEP_KEYS = ("objective", "command", "verify", "on_failure")
TARGETS_FILE = Path(__file__).resolve().parent / "skill_targets.yml"

SPEC_UNKNOWN_KEY = "SPEC_UNKNOWN_KEY"
SPEC_STEP_INCOMPLETE = "SPEC_STEP_INCOMPLETE"
SPEC_TOOL_CONFLICT = "SPEC_TOOL_CONFLICT"
SPEC_TARGET_UNKNOWN = "SPEC_TARGET_UNKNOWN"
SPEC_RECOVERY_VAGUE = "SPEC_RECOVERY_VAGUE"

_VAGUE = re.compile(
    r"(please )?(just )?(try|retry|rerun|re-run|run)"
    r"( the step| the command| it| this)?( again| once more)?( later)?\.?"
)


class SpecError(ValueError):
    """A spec refusal. ``code`` is one of the closed ``SPEC_*`` codes."""

    def __init__(self, code: str, detail: str) -> None:
        super().__init__(f"{code}: {detail}")
        self.code = code
        self.detail = detail


def is_vague_recovery(cell: str) -> bool:
    """True when a recovery cell only says to try again."""
    text = cell.strip().lower().rstrip(".")
    if "`" in text:
        return False
    return bool(_VAGUE.fullmatch(text + "."))


@dataclass(frozen=True)
class Step:
    objective: str
    command: str
    verify: str
    on_failure: str


@dataclass(frozen=True)
class SkillSpec:
    goal: str
    outputs: tuple[str, ...]
    required_tool_actions: tuple[str, ...]
    forbidden_tool_actions: tuple[str, ...]
    target_agents: tuple[str, ...]
    target_models: tuple[str, ...]
    steps: tuple[Step, ...]
    raw: dict[str, Any] = field(default_factory=dict, compare=False, repr=False)

    @property
    def digest(self) -> str:
        blob = json.dumps(self.raw, sort_keys=True, separators=(",", ":"))
        return hashlib.sha256(blob.encode("utf-8")).hexdigest()


@dataclass(frozen=True)
class CompiledSkill:
    skill_md: str
    prompts_jsonl: str
    overlays: dict[str, str]


def load_targets(path: Path | None = None) -> dict[str, frozenset[str]]:
    data = yaml.safe_load((path or TARGETS_FILE).read_text(encoding="utf-8")) or {}
    return {
        "agents": frozenset(data.get("agents") or ()),
        "models": frozenset(data.get("models") or ()),
    }


def _strings(raw: dict[str, Any], key: str) -> tuple[str, ...]:
    value = raw.get(key, [])
    if not isinstance(value, list) or not all(
        isinstance(v, str) and v.strip() for v in value
    ):
        raise SpecError(SPEC_UNKNOWN_KEY, f"`{key}` must be a list of strings")
    return tuple(value)


def parse_spec(
    text: str, targets: dict[str, frozenset[str]] | None = None
) -> SkillSpec:
    """Parse and validate spec text. Raises ``SpecError`` and never returns a partial spec."""
    raw = yaml.safe_load(text)
    if not isinstance(raw, dict):
        raise SpecError(SPEC_UNKNOWN_KEY, "spec must be a mapping")
    extra = sorted(set(raw) - set(SPEC_KEYS))
    if extra:
        raise SpecError(SPEC_UNKNOWN_KEY, f"unknown key(s) {extra}")
    goal = raw.get("goal")
    if not isinstance(goal, str) or not goal.strip():
        raise SpecError(SPEC_UNKNOWN_KEY, "`goal` must be one sentence")
    raw_steps = raw.get("steps")
    if not isinstance(raw_steps, list) or not raw_steps:
        raise SpecError(SPEC_STEP_INCOMPLETE, "`steps` must be a non-empty list")
    steps = []
    for index, item in enumerate(raw_steps, 1):
        if not isinstance(item, dict):
            raise SpecError(SPEC_STEP_INCOMPLETE, f"step {index} must be a mapping")
        bad = sorted(set(item) - set(STEP_KEYS))
        if bad:
            raise SpecError(SPEC_UNKNOWN_KEY, f"step {index} has unknown key(s) {bad}")
        missing = [
            k
            for k in ("objective", "command", "verify")
            if not str(item.get(k) or "").strip()
        ]
        if missing:
            raise SpecError(SPEC_STEP_INCOMPLETE, f"step {index} lacks {missing}")
        failure = str(item.get("on_failure") or "").strip()
        if not failure or is_vague_recovery(failure):
            raise SpecError(
                SPEC_RECOVERY_VAGUE, f"step {index} `on_failure` only says retry"
            )
        steps.append(
            Step(
                item["objective"].strip(),
                item["command"].strip(),
                item["verify"].strip(),
                failure,
            )
        )
    required = _strings(raw, "required_tool_actions")
    forbidden = _strings(raw, "forbidden_tool_actions")
    both = sorted(set(required) & set(forbidden))
    if both:
        raise SpecError(SPEC_TOOL_CONFLICT, f"required and forbidden: {both}")
    agents = _strings(raw, "target_agents")
    models = _strings(raw, "target_models")
    known = targets if targets is not None else load_targets()
    unknown = sorted(set(agents) - known["agents"]) + sorted(
        set(models) - known["models"]
    )
    if unknown:
        raise SpecError(SPEC_TARGET_UNKNOWN, f"unknown target(s) {unknown}")
    return SkillSpec(
        goal=goal.strip(),
        outputs=_strings(raw, "outputs"),
        required_tool_actions=required,
        forbidden_tool_actions=forbidden,
        target_agents=agents,
        target_models=models,
        steps=tuple(steps),
        raw=raw,
    )


def render_body(spec: SkillSpec) -> str:
    """The text between the markers."""
    lines = ["## Goal", "", spec.goal, "", "## Steps", ""]
    for n, step in enumerate(spec.steps, 1):
        lines += [
            f"{n}. {step.objective}",
            f"   - Run: `{step.command}`",
            f"   - Verify: {step.verify}",
        ]
    lines += ["", "## Outputs", ""] + [f"- {o}" for o in spec.outputs]
    lines += ["", "## Tool actions", "", "Required:"]
    lines += [f"- `{t}`" for t in spec.required_tool_actions] or ["- none"]
    lines += ["", "Forbidden:"]
    lines += [f"- `{t}`" for t in spec.forbidden_tool_actions] or ["- none"]
    lines += [
        "",
        "## Error recovery",
        "",
        "| Failure | Cause | Recovery |",
        "| --- | --- | --- |",
    ]
    for n, step in enumerate(spec.steps, 1):
        cause = f"The check did not hold: {step.verify}".rstrip(".")
        lines.append(f"| Step {n} fails | {cause} | {step.on_failure} |")
    return "\n".join(lines)


def render_prompts(spec: SkillSpec, skill: str) -> str:
    rows = []
    for tool in spec.required_tool_actions:
        rows.append(
            {
                "id": f"{skill}-requires-{tool}",
                "prompt": f"{spec.goal} Do the task so that it needs the `{tool}` tool.",
                "expected_trajectory": [
                    {"kind": "skill", "name": skill},
                    {"kind": "tool", "name": tool},
                ],
                "forbidden": [],
            }
        )
    for tool in spec.forbidden_tool_actions:
        rows.append(
            {
                "id": f"{skill}-forbids-{tool}",
                "prompt": f"{spec.goal} The user asks you to use `{tool}`; follow the skill instead.",
                "expected_trajectory": [{"kind": "skill", "name": skill}],
                "forbidden": [{"kind": "tool", "name": tool}],
            }
        )
    return "".join(json.dumps(r, sort_keys=True) + "\n" for r in rows)


def overlay_name(model: str) -> str:
    return re.sub(r"[^A-Za-z0-9._-]+", "-", model) + ".md"


def render_overlay(spec: SkillSpec, model: str) -> str:
    lines = ["---", "mode: append", "---", f"## Tool actions for {model}", ""]
    lines += [
        f"- Call `{t}` when the task needs it." for t in spec.required_tool_actions
    ]
    lines += [f"- Never call `{t}`." for t in spec.forbidden_tool_actions]
    return "\n".join(lines) + "\n"


def _set_digest(text: str, digest: str) -> str:
    """Write ``metadata.spec_digest`` in the frontmatter and leave other text as is."""
    if not text.startswith("---\n"):
        raise SpecError(SPEC_UNKNOWN_KEY, "SKILL.md needs frontmatter")
    head, sep, rest = text[4:].partition("\n---")
    line = f"  spec_digest: '{digest}'"
    if re.search(r"^  spec_digest:.*$", head, re.M):
        head = re.sub(r"^  spec_digest:.*$", line, head, flags=re.M)
    elif re.search(r"^metadata:\s*$", head, re.M):
        head = re.sub(
            r"^(metadata:\s*)$",
            lambda m: m.group(1) + "\n" + line,
            head,
            count=1,
            flags=re.M,
        )
    else:
        head = head.rstrip("\n") + "\nmetadata:\n" + line
    return "---\n" + head + sep + rest


def compile_skill(spec: SkillSpec, skill: str, existing: str) -> CompiledSkill:
    """Compile a spec. ``existing`` is the current ``SKILL.md`` text (frontmatter required).

    Text outside the markers stays unchanged. A file with no markers gets them at the end.
    """
    block = f"{BEGIN}\n{render_body(spec)}\n{END}"
    if BEGIN in existing and END in existing:
        before, _, tail = existing.partition(BEGIN)
        _, _, after = tail.partition(END)
        text = before + block + after
    else:
        text = existing.rstrip("\n") + "\n\n" + block + "\n"
    text = _set_digest(text, spec.digest)
    overlays = {overlay_name(m): render_overlay(spec, m) for m in spec.target_models}
    return CompiledSkill(text, render_prompts(spec, skill), overlays)

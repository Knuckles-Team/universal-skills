#!/usr/bin/env python3
"""Author a canonical system-prompt JSON blueprint.

CONCEPT:AU-ORCH.routing.resolve-body-single-canonical. Thin front-end over
``agent_utilities.prompting.structured.StructuredPrompt`` — the single source of
truth for the canonical prompt schema. Writes the body to
``instructions.core_directive`` and stamps ``schema_version``/``source`` so the
output passes ``validate_canonical`` (and therefore the ``check_prompt_schema``
CI gate and per-package ``test_prompt_parity``).
"""

from __future__ import annotations

import argparse
import sys

try:
    from agent_utilities.prompting.structured import (
        StructuredPrompt,
        validate_canonical,
    )
except ImportError:  # pragma: no cover - install hint
    print(
        "prompt-builder requires agent-utilities. Install it:\n"
        "  pip install agent-utilities",
        file=sys.stderr,
    )
    raise SystemExit(2)


def _split(value: str | None) -> list[str] | None:
    if not value:
        return None
    items = [v.strip() for v in value.split(",") if v.strip()]
    return items or None


def build(args: argparse.Namespace) -> dict:
    directive = args.directive
    if not directive and args.scaffold:
        directive = (
            f"[ACTION REQUIRED] You are the {args.task} agent. Describe the "
            "agent's role, the tools/skills it should use, and its operating "
            "rules here."
        )

    blueprint: dict = {
        "schema_version": "1.0",
        "task": args.task,
        "type": "prompt",
    }
    if args.source:
        blueprint["source"] = args.source
    if args.description:
        blueprint["description"] = args.description
    if args.role or args.goal:
        identity: dict = {}
        if args.role:
            identity["role"] = args.role
        if args.goal:
            identity["goal"] = args.goal
        blueprint["identity"] = identity
    blueprint["instructions"] = {"core_directive": directive or ""}
    skills = _split(args.skills)
    if skills:
        blueprint["skills"] = skills
    tools = _split(args.tools)
    if tools:
        blueprint["tools"] = tools
    if args.extends:
        blueprint["extends"] = args.extends
        blueprint["compose"] = args.compose

    # Round-trip through the model to normalise + validate field types.
    return StructuredPrompt.model_validate(blueprint).model_dump(
        exclude_none=True, exclude_unset=True
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--task", required=True, help="Stable slug, e.g. gitlab-agent")
    parser.add_argument("--source", help="Provenance/KG namespace, e.g. gitlab-api")
    parser.add_argument("--description")
    parser.add_argument("--role")
    parser.add_argument("--goal")
    parser.add_argument("--directive", help="The instructions.core_directive body")
    parser.add_argument("--skills", help="Comma-separated skill slugs")
    parser.add_argument("--tools", help="Comma-separated tool/skill names")
    parser.add_argument(
        "--extends", help="Base to compose onto, e.g. agent-utilities:base"
    )
    parser.add_argument(
        "--compose", default="append", choices=["append", "prepend", "replace"]
    )
    parser.add_argument(
        "--scaffold",
        action="store_true",
        help="Emit a placeholder core_directive to fill in.",
    )
    parser.add_argument("-o", "--output", required=True, help="Output JSON path")
    args = parser.parse_args(argv)

    blueprint = build(args)

    # Validate before writing (scaffold skeletons are allowed to be incomplete).
    errs = validate_canonical(blueprint, strict=True)
    if errs and not args.scaffold:
        print("Refusing to write non-canonical prompt:", file=sys.stderr)
        for e in errs:
            print(f"  - {type(e).__name__}", file=sys.stderr)
        return 1

    StructuredPrompt.model_validate(blueprint).save(args.output)
    print(f"Wrote {args.output}")
    if errs:
        print("NOTE (scaffold): fill in before shipping — " + "; ".join(errs))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

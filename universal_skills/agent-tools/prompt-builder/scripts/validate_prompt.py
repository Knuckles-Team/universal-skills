#!/usr/bin/env python3
"""Validate a system-prompt JSON blueprint against the canonical contract.

CONCEPT:AU-ORCH.routing.resolve-body-single-canonical. Wraps the single shared validator
``agent_utilities.prompting.structured.validate_canonical`` so authoring,
CI (``check_prompt_schema.py``), and per-package ``test_prompt_parity`` all
agree. Exit code 0 == conformant, 1 == violations (in the chosen mode).
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

try:
    from agent_utilities.prompting.structured import validate_canonical
except ImportError:  # pragma: no cover - install hint
    print(
        "prompt-builder requires agent-utilities. Install it:\n"
        "  pip install agent-utilities",
        file=sys.stderr,
    )
    raise SystemExit(2)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("paths", nargs="+", help="Prompt JSON file(s) to validate.")
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Fail on legacy content/input keys too (default: warn).",
    )
    args = parser.parse_args(argv)

    failed = 0
    for raw_path in args.paths:
        path = Path(raw_path)
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as e:
            print(f"FAIL {path}: unreadable ({type(e).__name__})", file=sys.stderr)
            failed += 1
            continue
        errs = validate_canonical(data, strict=args.strict)
        if errs:
            print(f"FAIL {path}:", file=sys.stderr)
            for e in errs:
                print(f"  - {type(e).__name__}", file=sys.stderr)
            failed += 1
        else:
            print(f"OK   {path}")

    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())

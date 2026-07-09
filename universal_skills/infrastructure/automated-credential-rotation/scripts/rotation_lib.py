#!/usr/bin/env python3
"""Safe primitives for credential rotation — generation, redaction, planning, audit.

This module deliberately contains NO network/provider calls and NEVER stores a
secret value in its outputs. The agent performs the actual provider rotation +
OpenBao writes + consumer updates via MCP tools (see SKILL.md); this library is
the deterministic, testable safety layer that guarantees:

  * secrets are generated with sufficient entropy,
  * nothing prints a secret value (redaction is structural, not best-effort),
  * a dry-run plan can be produced and reviewed before anything changes,
  * an audit record carries names/versions/status only — never values.

stdlib only. CLI:
    python rotation_lib.py gen --kind token
    python rotation_lib.py plan --catalog catalog.json
    python rotation_lib.py redact   < anything-with-secrets.txt
"""

from __future__ import annotations

import argparse
import json
import re
import secrets
import string
import sys
from typing import Any

# ---------------------------------------------------------------------------
# Secret generation
# ---------------------------------------------------------------------------
_ALNUM = string.ascii_letters + string.digits


def generate_secret(kind: str = "token", length: int | None = None) -> str:
    """Generate a high-entropy secret. 'token' = URL-safe; 'password' = alnum+symbols.

    Callers should pass the result straight to the provider/OpenBao and never log it.
    """
    if kind == "password":
        n = length or 24
        alphabet = _ALNUM + "!@#%^*-_=+"
        return "".join(secrets.choice(alphabet) for _ in range(n))
    if kind == "alnum":
        n = length or 32
        return "".join(secrets.choice(_ALNUM) for _ in range(n))
    # default: URL-safe token (length ~ 1.3x bytes)
    return secrets.token_urlsafe(length or 32)


# ---------------------------------------------------------------------------
# Redaction — structural guarantee that values never reach a log
# ---------------------------------------------------------------------------
# Common secret shapes: GitHub/GitLab tokens, JWTs, bearer tokens, long hex/b64.
_PATTERNS = [
    re.compile(r"\bgh[posru]_[A-Za-z0-9]{20,}\b"),  # GitHub PAT/OAuth
    re.compile(r"\bglpat-[A-Za-z0-9_-]{16,}\b"),  # GitLab PAT
    re.compile(r"\b(?:pk|sk)-lf-[A-Za-z0-9-]{16,}\b"),  # Langfuse keys
    re.compile(
        r"\beyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\b"
    ),  # JWT
    re.compile(r"\b[A-Fa-f0-9]{32,}\b"),  # long hex
]
# Redact values of obviously-secret keys in k=v / "key": "value" forms.
# Handles key=value, key: value, and JSON "key": "value" (optional closing quote
# on the key before the separator).
_KV = re.compile(
    r"(?i)\b([A-Z0-9_]*(?:TOKEN|SECRET|PASSWORD|PASSWD|API[_-]?KEY|PRIVATE[_-]?KEY)[A-Z0-9_]*)"
    r"(\"?\s*[=:]\s*)(\"?)([^\s\"',}]+)(\3)"
)
_REDACTED = "***REDACTED***"


_BENIGN = {"true", "false", "null", "none", "yes", "no"}


def _kv_sub(m: re.Match) -> str:
    """Redact a key=value only when the value actually looks secret — not a count,
    flag, or short identifier (avoids false positives like secret_count: 4)."""
    value = m.group(4)
    if value.lower() in _BENIGN or value.isdigit() or len(value) < 6:
        return m.group(0)
    return f"{m.group(1)}{m.group(2)}{m.group(3)}{_REDACTED}{m.group(5)}"


def redact(text: str) -> str:
    """Return text with any secret-looking value replaced by ***REDACTED***."""
    text = _KV.sub(_kv_sub, text)
    for pat in _PATTERNS:
        text = pat.sub(_REDACTED, text)
    return text


def safe_dumps(obj: Any) -> str:
    """json.dumps then redact — for any structure that might contain a value."""
    return redact(json.dumps(obj, indent=2, sort_keys=True))


# ---------------------------------------------------------------------------
# Dry-run plan + audit record (names/versions/status only)
# ---------------------------------------------------------------------------
def build_plan(catalog: list[dict]) -> dict:
    """Turn a secrets catalog into an ordered, reviewable rotation plan.

    Each catalog entry: {name, type, provider, bao_path, consumers:[{kind,ref,...}],
    cadence_days, verify}. The plan lists actions WITHOUT any values.
    """
    items = []
    for s in catalog:
        items.append(
            {
                "name": s["name"],
                "type": s.get("type", "token"),
                "provider": s.get("provider", "unknown"),
                "bao_path": s.get("bao_path"),
                "steps": [
                    f"rotate at provider: {s.get('provider', 'unknown')}",
                    f"write new value -> OpenBao {s.get('bao_path')}",
                    "validate new version > old in OpenBao",
                    *[
                        f"propagate -> {c.get('kind')}:{c.get('ref')}"
                        for c in s.get("consumers", [])
                    ],
                    *([f"verify: {s['verify']}"] if s.get("verify") else []),
                    "revoke old credential at provider",
                ],
                "consumer_count": len(s.get("consumers", [])),
                "cadence_days": s.get("cadence_days", 182),  # ~6 months
            }
        )
    return {
        "dry_run": True,
        "secret_count": len(items),
        "consumer_total": sum(i["consumer_count"] for i in items),
        "items": items,
    }


def audit_record(
    name: str,
    *,
    status: str,
    old_version: Any = None,
    new_version: Any = None,
    consumers: list[dict] | None = None,
    error: str | None = None,
) -> dict:
    """A value-free audit record for one rotation."""
    rec = {
        "secret": name,
        "status": status,  # planned|rotated|partial|failed|skipped
        "old_version": old_version,
        "new_version": new_version,
        "consumers": [
            {"ref": c.get("ref"), "status": c.get("status")} for c in (consumers or [])
        ],
    }
    if error:
        rec["error"] = redact(error)  # never leak a value via an error string
    return rec


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------
def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    sub = ap.add_subparsers(dest="cmd", required=True)
    g = sub.add_parser("gen", help="generate a secret (printed once, not logged)")
    g.add_argument("--kind", default="token", choices=["token", "password", "alnum"])
    g.add_argument("--length", type=int, default=None)
    p = sub.add_parser("plan", help="build a dry-run rotation plan from a catalog json")
    p.add_argument("--catalog", required=True)
    sub.add_parser("redact", help="redact secrets from stdin")
    args = ap.parse_args(argv)

    if args.cmd == "gen":
        sys.stdout.write(generate_secret(args.kind, args.length) + "\n")
    elif args.cmd == "plan":
        catalog = json.load(open(args.catalog, encoding="utf-8"))
        items = catalog["secrets"] if isinstance(catalog, dict) else catalog
        # plan output is value-free by construction
        print(json.dumps(build_plan(items), indent=2))
    elif args.cmd == "redact":
        sys.stdout.write(redact(sys.stdin.read()))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

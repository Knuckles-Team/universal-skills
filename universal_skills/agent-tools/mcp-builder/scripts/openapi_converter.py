"""Generate bound clients and condensed SDK tool registrars from OpenAPI 3."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import tomllib
from pathlib import Path

from openapi_schema import compile_contract, domain_schemas


def generate(spec: Path, package: Path, auth_scheme: str = ""):
    contract = compile_contract(json.loads(spec.read_text()))
    contract["source_sha256"] = hashlib.sha256(spec.read_bytes()).hexdigest()
    contract["schemas"] = {
        domain: domain_schemas(contract, domain) for domain in contract["domains"]
    }
    files = {
        package / "openapi_contract.json": json.dumps(
            contract, indent=2, sort_keys=True
        )
        + "\n",
        package / "openapi_runtime.py": (
            Path(__file__).parent / "templates/openapi_runtime.py"
        ).read_text(),
    }
    if auth_scheme and auth_scheme not in contract["security_schemes"]:
        raise ValueError("Selected auth scheme is not declared in OpenAPI")
    auth = (Path(__file__).parent / "templates/openapi_auth.py").read_text()
    files[package / "auth.py"] = (
        auth.replace("__PACKAGE_ENV__", package.name.upper())
        .replace("__SERVICE__", package.name.replace("_", "-"))
        .replace("__DEFAULT_AUTH_SCHEME__", auth_scheme)
    )
    imports = [
        "from ..openapi_runtime import register_domain",
        "from ..auth import get_client",
        "",
    ]
    for domain in contract["domains"]:
        imports.extend(
            [
                f"def register_{domain}_tools(mcp):",
                f"    register_domain(mcp, {domain!r}, get_client)",
                "",
            ]
        )
    files[package / "mcp/__init__.py"] = "\n".join(imports) + "\n"
    for path, content in files.items():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content)
    metadata = package.parent / "pyproject.toml"
    if metadata.exists():
        text = metadata.read_text()
        parsed = tomllib.loads(text)
        required = ["jsonschema>=4.23,<5", "regex>=2026.9.29"]
        missing = [
            item for item in required if item not in parsed["project"]["dependencies"]
        ]
        if missing:
            text, count = re.subn(
                r"(?m)^dependencies\s*=\s*\[",
                lambda match: (
                    match.group()
                    + "\n"
                    + "\n".join(f"    {json.dumps(item)}," for item in missing)
                ),
                text,
                count=1,
            )
            if count != 1:
                raise ValueError("Cannot locate project dependency declaration")
        data = parsed["tool"]["setuptools"]["package-data"].get(package.name, [])
        if "openapi_contract.json" not in data:
            section = text.index("[tool.setuptools.package-data]")
            before, after = text[:section], text[section:]
            after, count = re.subn(
                r"(?m)^" + re.escape(package.name) + r"\s*=\s*\[",
                lambda match: match.group() + ' "openapi_contract.json",',
                after,
                count=1,
            )
            if count != 1:
                raise ValueError("Cannot locate package data declaration")
            text = before + after
        tomllib.loads(text)
        metadata.write_text(text)
    return {
        str(path.relative_to(package)): hashlib.sha256(content.encode()).hexdigest()
        for path, content in files.items()
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("spec", type=Path)
    parser.add_argument("package", type=Path)
    parser.add_argument("--auth-scheme", default="")
    args = parser.parse_args()
    print(
        json.dumps(
            generate(args.spec, args.package, args.auth_scheme),
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()

"""Create private GitHub template repositories and apply explicit substitutions.

Uses existing gh credentials without reading token values. Remote writes are
explicit subcommands; preparation and verification are local and deterministic.
"""

from __future__ import annotations

import argparse
import base64
import hashlib
import json
import re
import subprocess
from pathlib import Path

IDENTITY = {"name": "Codex", "email": "codex@users.noreply.github.com"}
IGNORED = frozenset({".git", "__pycache__", ".pytest_cache", ".ruff_cache", ".venv"})


def api(route, method="GET", data=None):
    command = ["gh", "api", route, "--method", method]
    if data is not None:
        command.extend(["--input", "-"])
    result = subprocess.run(
        command,
        input=json.dumps(data) if data is not None else None,
        text=True,
        capture_output=True,
        check=False,
    )
    if result.returncode:
        # Never include provider output, which may echo configuration values.
        raise RuntimeError(f"GitHub API {method} failed for {route.split('?')[0]}")
    return json.loads(result.stdout)


def preflight(owner, name):
    if api("user")["login"].casefold() != "knucklessg1":
        raise PermissionError("Authenticated GitHub actor must be Knucklessg1")
    if not re.fullmatch(r"[A-Za-z0-9_.-]+", owner) or not re.fullmatch(
        r"[a-z][a-z0-9-]+", name
    ):
        raise ValueError("Invalid repository identity")
    probe = subprocess.run(
        ["gh", "api", f"repos/{owner}/{name}"],
        capture_output=True,
        text=True,
        check=False,
    )
    if probe.returncode == 0:
        raise FileExistsError(
            "Destination repository already exists; refusing overwrite"
        )
    if "HTTP 404" not in probe.stderr:
        raise PermissionError("Cannot establish that destination repository is absent")


def files(root):
    result = {}
    for path in sorted(root.rglob("*")):
        relative = path.relative_to(root)
        if any(part in IGNORED for part in relative.parts):
            continue
        if path.is_symlink():
            raise ValueError("Template symlinks are not supported")
        if path.is_file():
            if path.name == ".env" or path.suffix in {".log", ".pyc"}:
                raise ValueError("Transient or secret-bearing file in template")
            result[relative.as_posix()] = path.read_bytes()
    return result


def hashes(contents):
    return {
        name: hashlib.sha256(body).hexdigest()
        for name, body in sorted(contents.items())
    }


def substitute(contents, replacements):
    """One simultaneous literal substitution pass over file paths and UTF-8 bytes."""
    if not replacements or any(not key for key in replacements):
        raise ValueError("Explicit nonempty substitution map required")
    matcher = re.compile(
        "|".join(
            re.escape(key)
            for key in sorted(replacements, key=lambda key: (-len(key), key))
        )
    )
    def change(value):
        return matcher.sub(lambda match: replacements[match.group()], value)
    result = {}
    for name, body in sorted(contents.items()):
        target = change(name)
        if target in result or target.startswith("/") or ".." in Path(target).parts:
            raise ValueError("Substitution caused unsafe or duplicate file path")
        try:
            rendered = change(body.decode()).encode()
        except UnicodeDecodeError:
            rendered = body
        result[target] = rendered
    return result


def verify(expected, actual, allowed):
    changed = sorted(
        name
        for name in set(expected) | set(actual)
        if expected.get(name) != actual.get(name)
    )
    unexpected = [name for name in changed if name not in allowed]
    return {
        "expected_hashes": hashes(expected),
        "actual_hashes": hashes(actual),
        "changed": changed,
        "unexpected": unexpected,
        "allowed_edits": sorted(allowed),
    }


def publish_template(root, owner, name, checks):
    contents = files(root)
    if checks.get("files") != hashes(contents) or checks.get("passed") is not True:
        raise ValueError(
            "Passed checks must bind the exact complete template file hashes"
        )
    preflight(owner, name)
    repo = api(
        f"orgs/{owner}/repos",
        "POST",
        {
            "name": name,
            "private": True,
            "is_template": True,
            "description": "SDK connector template with deterministic OpenAPI generation",
        },
    )
    if not repo["private"] or not repo["is_template"]:
        raise RuntimeError(
            "Created repository does not match requested template policy"
        )
    # Contents API initializes an empty repository; all-file tree commit follows.
    api(
        f"repos/{owner}/{name}/contents/README.md",
        "PUT",
        {
            "message": "Initialize connector template",
            "content": base64.b64encode(contents["README.md"]).decode(),
            "author": IDENTITY,
            "committer": IDENTITY,
        },
    )
    branch = api(f"repos/{owner}/{name}")["default_branch"]
    head = api(f"repos/{owner}/{name}/git/ref/heads/{branch}")["object"]["sha"]
    tree = []
    for path, body in contents.items():
        mode = "100755" if (root / path).stat().st_mode & 0o111 else "100644"
        entry = {"path": path, "mode": mode, "type": "blob"}
        try:
            entry["content"] = body.decode()
        except UnicodeDecodeError:
            blob = api(
                f"repos/{owner}/{name}/git/blobs",
                "POST",
                {"content": base64.b64encode(body).decode(), "encoding": "base64"},
            )
            entry["sha"] = blob["sha"]
        tree.append(entry)
    created = api(f"repos/{owner}/{name}/git/trees", "POST", {"tree": tree})
    commit = api(
        f"repos/{owner}/{name}/git/commits",
        "POST",
        {
            "message": "Publish validated canonical connector template",
            "tree": created["sha"],
            "parents": [head],
            "author": IDENTITY,
            "committer": IDENTITY,
        },
    )
    api(
        f"repos/{owner}/{name}/git/refs/heads/{branch}",
        "PATCH",
        {"sha": commit["sha"], "force": False},
    )
    return {
        "repository": repo["full_name"],
        "sha": commit["sha"],
        "files": hashes(contents),
    }


def create_from_template(owner, name, template, template_sha):
    preflight(owner, name)
    if not re.fullmatch(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+", template):
        raise ValueError("Invalid template repository identity")
    source = api(f"repos/{template}")
    if not source.get("is_template"):
        raise ValueError("Source is not a GitHub template")
    branch = source["default_branch"]
    before = api(f"repos/{template}/commits/{branch}")["sha"]
    if before != template_sha:
        raise ValueError("Template head differs from reviewed revision")
    repo = api(
        f"repos/{template}/generate",
        "POST",
        {"owner": owner, "name": name, "private": True, "include_all_branches": False},
    )
    after = api(f"repos/{template}/commits/{branch}")["sha"]
    if before != after or not repo["private"]:
        raise RuntimeError(
            "Template changed during generation; destination preserved for inspection"
        )
    return {
        "repository": repo["full_name"],
        "template": template,
        "template_sha": template_sha,
        "private": repo["private"],
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    render = sub.add_parser("render")
    render.add_argument("source", type=Path)
    render.add_argument("destination", type=Path)
    render.add_argument("--variables", type=Path, required=True)
    publish = sub.add_parser("publish-template")
    publish.add_argument("source", type=Path)
    publish.add_argument("--owner", required=True)
    publish.add_argument("--name", required=True)
    publish.add_argument("--checks", type=Path, required=True)
    create = sub.add_parser("create")
    create.add_argument("--owner", required=True)
    create.add_argument("--name", required=True)
    create.add_argument("--template", required=True)
    create.add_argument("--template-sha", required=True)
    args = parser.parse_args()
    if args.command == "render":
        if args.destination.exists():
            raise FileExistsError("Render destination must not exist")
        result = substitute(files(args.source), json.loads(args.variables.read_text()))
        for name, body in result.items():
            path = args.destination / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(body)
        print(json.dumps(hashes(result), indent=2, sort_keys=True))
    elif args.command == "publish-template":
        print(
            json.dumps(
                publish_template(
                    args.source,
                    args.owner,
                    args.name,
                    json.loads(args.checks.read_text()),
                ),
                indent=2,
                sort_keys=True,
            )
        )
    else:
        print(
            json.dumps(
                create_from_template(
                    args.owner, args.name, args.template, args.template_sha
                ),
                indent=2,
                sort_keys=True,
            )
        )


if __name__ == "__main__":
    main()

"""Publish a validated local connector tree to a new, normal GitHub repository.

The scaffold and its assets live in this installed skill. No remote template is
read. Publication uses existing gh credentials and never reads token values.
"""

from __future__ import annotations

import argparse
import base64
import hashlib
import json
import os
import re
import subprocess
from pathlib import Path
from urllib.parse import quote

IDENTITY = {"name": "Codex", "email": "noreply@openai.com"}
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
        # Provider output may echo configuration; report only the operation.
        raise RuntimeError(f"GitHub API {method} failed for {route.split('?')[0]}")
    return json.loads(result.stdout)


def preflight(owner, name, expected_login):
    """Confirm the selected actor, owner kind and absent destination, without writes."""
    if not all(
        re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_.-]*", value)
        for value in (owner, name, expected_login)
    ):
        raise ValueError("Invalid repository or actor identity")
    actor = api("user")["login"]
    if actor.casefold() != expected_login.casefold():
        raise PermissionError("Authenticated GitHub actor differs from expected login")
    account = api(f"users/{owner}")
    if account["type"] == "Organization":
        route = f"orgs/{owner}/repos"
    elif account["type"] == "User" and owner.casefold() == actor.casefold():
        route = "user/repos"
    else:
        raise PermissionError(
            "Destination must be an organization or the selected actor"
        )
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
    return route


def snapshot(root):
    """Capture all authored file bytes and executable modes before remote operations."""
    if root.is_symlink() or not root.is_dir():
        raise ValueError("Source must be an existing local directory")
    result = {}
    for path in sorted(root.rglob("*")):
        relative = path.relative_to(root)
        if any(part in IGNORED for part in relative.parts):
            continue
        if path.is_symlink():
            raise ValueError("Source symlinks are not supported")
        if path.is_file():
            if path.name == ".env" or path.suffix in {".log", ".pyc"}:
                raise ValueError("Transient or secret-bearing file in source")
            with path.open("rb") as stream:
                mode = (
                    "100755" if os.fstat(stream.fileno()).st_mode & 0o111 else "100644"
                )
                result[relative.as_posix()] = (stream.read(), mode)
        elif not path.is_dir():
            raise ValueError("Only regular files and directories are supported")
    if not result:
        raise ValueError("Source tree is empty")
    return result


def snapshot_manifest(captured):
    return {
        name: {"sha256": hashlib.sha256(body).hexdigest(), "mode": mode}
        for name, (body, mode) in sorted(captured.items())
    }


def manifest(root):
    """A local inventory is not a declaration that checks passed."""
    return snapshot_manifest(snapshot(root))


def blob_sha(body):
    """Git's object identifier; SHA-256 above binds the validation evidence."""
    return hashlib.sha1(
        b"blob " + str(len(body)).encode() + b"\0" + body, usedforsecurity=False
    ).hexdigest()


def commit_tree(repository, revision):
    commit = api(f"repos/{repository}/git/commits/{revision}")
    tree = api(f"repos/{repository}/git/trees/{commit['tree']['sha']}?recursive=1")
    if tree.get("truncated"):
        raise ValueError(
            "Cannot attest a truncated repository tree; destination preserved"
        )
    return sorted(
        (item["path"], item["mode"], item["type"], item["sha"])
        for item in tree["tree"]
        if item["type"] != "tree"
    )


def upload_tree(repository, captured):
    tree = []
    for path, (body, mode) in captured.items():
        entry = {"path": path, "mode": mode, "type": "blob"}
        try:
            entry["content"] = body.decode("utf-8")
        except UnicodeDecodeError:
            blob = api(
                f"repos/{repository}/git/blobs",
                "POST",
                {"content": base64.b64encode(body).decode(), "encoding": "base64"},
            )
            if blob["sha"] != blob_sha(body):
                raise RuntimeError(
                    "Uploaded blob differs from snapshot; destination preserved"
                )
            entry["sha"] = blob["sha"]
        tree.append(entry)
    return api(f"repos/{repository}/git/trees", "POST", {"tree": tree})["sha"]


def verify_repository(current, created):
    """Bind remote reads to the same private, non-template repository."""
    if (
        current.get("id") != created["id"]
        or current.get("full_name", "").casefold() != created["full_name"].casefold()
        or current.get("private") is not True
        or current.get("is_template") is not False
    ):
        raise RuntimeError("Destination identity or visibility changed; preserved")


def publish(root, owner, name, checks, expected_login):
    captured = snapshot(root)
    validated = snapshot_manifest(captured)
    if checks.get("files") != validated or checks.get("passed") is not True:
        raise ValueError(
            "Passed checks must bind the exact complete source file hashes and modes"
        )
    if "README.md" not in captured:
        raise ValueError("Generated source must include README.md")
    create_route = preflight(owner, name, expected_login)
    repository = f"{owner}/{name}"
    repo = api(
        create_route,
        "POST",
        {"name": name, "private": True, "is_template": False, "auto_init": False},
    )
    if (
        repo.get("private") is not True
        or repo.get("is_template") is not False
        or repo["full_name"].casefold() != repository.casefold()
        or not isinstance(repo.get("id"), int)
    ):
        raise RuntimeError(
            "Created repository differs from requested destination; preserved"
        )
    # Git data writes require an initialized repository. Initialize only from
    # captured, checked bytes, then replace the entire tree with that snapshot.
    branch = repo["default_branch"]
    initialized = api(
        f"repos/{repository}/contents/README.md",
        "PUT",
        {
            "message": "Initialize connector from validated local source",
            "branch": branch,
            "content": base64.b64encode(captured["README.md"][0]).decode(),
            "author": IDENTITY,
            "committer": IDENTITY,
        },
    )
    seed = initialized["commit"]
    if seed.get("parents") != []:
        raise RuntimeError("Destination changed before initialization; preserved")
    seed_sha = seed["sha"]
    ref = quote(branch, safe="")
    current = api(f"repos/{repository}")
    verify_repository(current, repo)
    current_head = api(f"repos/{repository}/git/ref/heads/{ref}")["object"]["sha"]
    if current["default_branch"] != branch or current_head != seed_sha:
        raise RuntimeError("Destination changed after initialization; preserved")
    tree_sha = upload_tree(repository, captured)
    commit = api(
        f"repos/{repository}/git/commits",
        "POST",
        {
            "message": "Publish validated local connector tree",
            "tree": tree_sha,
            "parents": [seed_sha],
            "author": IDENTITY,
            "committer": IDENTITY,
        },
    )
    expected_tree = sorted(
        (path, mode, "blob", blob_sha(body)) for path, (body, mode) in captured.items()
    )
    if commit_tree(repository, commit["sha"]) != expected_tree:
        raise RuntimeError(
            "Uploaded tree differs from validated snapshot; destination preserved"
        )
    api(
        f"repos/{repository}/git/refs/heads/{ref}",
        "PATCH",
        {"sha": commit["sha"], "force": False},
    )
    current = api(f"repos/{repository}")
    verify_repository(current, repo)
    current_head = api(f"repos/{repository}/git/ref/heads/{ref}")["object"]["sha"]
    if current["default_branch"] != branch or current_head != commit["sha"]:
        raise RuntimeError("Destination branch changed during publication; preserved")
    return {
        "repository": repo["full_name"],
        "sha": commit["sha"],
        "private": current["private"],
        "files": validated,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    inventory = sub.add_parser(
        "manifest", help="Inventory local files; does not certify checks"
    )
    inventory.add_argument("source", type=Path)
    publication = sub.add_parser("publish", help="Create a private normal repository")
    publication.add_argument("source", type=Path)
    publication.add_argument("--owner", required=True)
    publication.add_argument("--name", required=True)
    publication.add_argument("--expected-login", required=True)
    publication.add_argument("--checks", type=Path, required=True)
    args = parser.parse_args()
    if args.command == "manifest":
        result = manifest(args.source)
    else:
        result = publish(
            args.source,
            args.owner,
            args.name,
            json.loads(args.checks.read_text()),
            args.expected_login,
        )
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()

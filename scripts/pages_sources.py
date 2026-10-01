"""MkDocs hooks: render tracked guides and the public spec package in memory."""

import json
import re
from pathlib import Path
from urllib.parse import urlsplit

try:
    from mkdocs.structure.files import File
except ImportError as exc:
    raise SystemExit(
        "Pages sources require MkDocs; install .github/requirements-pages.txt"
    ) from exc


def public_links(markdown, source, root, repo_url):
    """Rebase repository-relative links onto their canonical public sources."""

    def replace(match):
        target = match.group(1)
        if urlsplit(target).scheme or target.startswith(("#", "/")):
            return match.group(0)
        path, _, fragment = target.partition("#")
        resolved = (source.parent / path).resolve()
        if not resolved.is_relative_to(root) or not resolved.exists():
            raise ValueError(f"{source.relative_to(root)}: missing link {target}")
        if (
            source.parent.name == "US-PAGES-001"
            and resolved.parent == source.parent
            and resolved.suffix == ".md"
        ):
            return match.group(0)
        suffix = f"#{fragment}" if fragment else ""
        return (
            f"]({repo_url}/blob/main/{resolved.relative_to(root).as_posix()}{suffix})"
        )

    return re.sub(r"\]\(([^\s)]+)\)", replace, markdown)


def status_markdown(status):
    """Validate owner-native metadata; receipts remain claims requiring audit."""
    if not isinstance(status, dict):
        raise TypeError("US-PAGES-001/status.json: status must be an object")
    if (
        status.get("schema_version") != 1
        or status.get("spec_id") != "US-PAGES-001"
        or status.get("owner_repo") != "universal-skills"
    ):
        raise ValueError("US-PAGES-001/status.json: invalid identity or schema")
    delivery = status.get("delivery_state")
    acceptance = status.get("acceptance_state")
    if not isinstance(delivery, str) or not isinstance(acceptance, str):
        raise TypeError("US-PAGES-001/status.json: states must be strings")
    if delivery not in {
        "SPECIFIED",
        "IN_PROGRESS",
        "IMPLEMENTED",
    } or acceptance not in {"NOT_AUDITED", "ACCEPTED", "REJECTED"}:
        raise ValueError(
            "US-PAGES-001/status.json: invalid delivery or acceptance state"
        )
    evidence = status.get("evidence")
    if not isinstance(evidence, list):
        raise TypeError("US-PAGES-001/status.json: evidence must be a list")
    receipts = []
    kinds = set()
    commits = set()
    for receipt in evidence:
        if not isinstance(receipt, dict):
            raise TypeError("US-PAGES-001/status.json: receipt must be an object")
        kind = receipt.get("kind")
        commit = receipt.get("commit", "")
        url = receipt.get("url", "")
        prefix = "https://github.com/Knuckles-Team/universal-skills/"
        if not isinstance(commit, str) or not re.fullmatch(r"[0-9a-f]{40}", commit):
            raise ValueError("US-PAGES-001/status.json: receipt needs an exact commit")
        if kind == "merged_implementation":
            valid = url == f"{prefix}commit/{commit}"
        elif kind == "passing_acceptance":
            valid = isinstance(url, str) and bool(
                re.fullmatch(re.escape(prefix) + r"actions/runs/[0-9]+", url)
            )
        else:
            valid = False
        if not valid:
            raise ValueError("US-PAGES-001/status.json: invalid public receipt")
        kinds.add(kind)
        commits.add(commit)
        receipts.append(f"- [{kind}]({url}) — commit `{commit}`")
    if acceptance == "ACCEPTED" and (
        delivery != "IMPLEMENTED"
        or kinds != {"merged_implementation", "passing_acceptance"}
        or len(commits) != 1
    ):
        raise ValueError(
            "US-PAGES-001/status.json: ACCEPTED requires matching implementation and acceptance receipts"
        )
    return "\n".join(
        [
            "## Owner-native status",
            "",
            "Stable ID: **US-PAGES-001**. Owner: [universal-skills](https://github.com/Knuckles-Team/universal-skills).",
            f"Delivery: **{delivery}**. Acceptance: **{acceptance}**.",
            "",
            *(
                receipts
                or [
                    "Acceptance evidence pending; publication does not establish implementation or acceptance."
                ]
            ),
            "",
            "Receipts are owner-reported metadata. Merged code and passing results require a maintainer audit; this offline build validates their shape only.",
        ]
    )


def on_files(files, config):
    root = Path(config.config_file_path).resolve().parent
    repo_url = config.repo_url.rstrip("/")
    contribution = root / "CONTRIBUTING.md"
    files.append(
        File.generated(
            config,
            "contributing.md",
            content=public_links(
                contribution.read_text(encoding="utf-8"), contribution, root, repo_url
            ),
        )
    )
    package = root / "specs" / "US-PAGES-001"
    status = json.loads((package / "status.json").read_text(encoding="utf-8"))
    rendered_status = status_markdown(status)
    for name in ("spec.md", "requirements.md", "plan.md", "test-spec.md", "tasks.md"):
        source = package / name
        markdown = public_links(
            source.read_text(encoding="utf-8"), source, root, repo_url
        )
        if name == "spec.md":
            for field, key in (
                ("Delivery", "delivery_state"),
                ("Acceptance", "acceptance_state"),
                ("Owner", "owner_repo"),
            ):
                markdown = re.sub(
                    rf"^\*\*{field}:\*\*.*$",
                    f"**{field}:** {status[key]}",
                    markdown,
                    flags=re.MULTILINE,
                )
            markdown += "\n" + rendered_status + "\n"
        files.append(
            File.generated(config, f"specs/US-PAGES-001/{name}", content=markdown)
        )
    return files

"""Provision the checked public repository's existing Actions Pages workflow."""

from __future__ import annotations

import re
from urllib.parse import quote, urlsplit


def verify_target(api, repository, repository_id, branch, expected_head):
    """Bind each write phase to public visibility, repository identity and source."""
    current = api(f"repos/{repository}")
    if (
        current.get("id") != repository_id
        or current.get("full_name", "").casefold() != repository.casefold()
        or current.get("private") is not False
        or current.get("is_template") is not False
        or current.get("default_branch") != branch
    ):
        raise RuntimeError("Pages repository identity or public visibility changed")
    ref = quote(branch, safe="")
    head = api(f"repos/{repository}/git/ref/heads/{ref}")
    if head.get("object", {}).get("sha") != expected_head:
        raise RuntimeError("Pages source head changed; destination preserved")


def site_url(page):
    """Preserve an existing domain; never change site visibility or build policy."""
    if not isinstance(page, dict) or not isinstance(page.get("html_url"), str):
        raise RuntimeError("Pages response lacks a verified site URL; preserved")
    url = page["html_url"]
    parsed = urlsplit(url)
    if (
        page.get("build_type") != "workflow"
        or page.get("public") is not True
        or parsed.scheme != "https"
        or not parsed.hostname
        or parsed.username is not None
        or parsed.password is not None
    ):
        raise RuntimeError("Pages is not a verified public Actions site; preserved")
    return url


def provision(api, repository, repository_id, branch, expected_head):
    """Configure once and request one build; live deployment needs separate proof."""
    if (
        not re.fullmatch(
            r"[A-Za-z0-9][A-Za-z0-9_.-]*/[A-Za-z0-9][A-Za-z0-9_.-]*", repository
        )
        or type(repository_id) is not int
        or repository_id <= 0
        or not branch
        or not expected_head
    ):
        raise ValueError("Explicit repository identity, branch and head are required")
    verify_target(api, repository, repository_id, branch, expected_head)
    workflow = f"repos/{repository}/actions/workflows/pages.yml"
    if api(workflow).get("state") != "active":
        raise RuntimeError("The existing Pages workflow must be active; preserved")
    route = f"repos/{repository}/pages"
    page = api(route, allow_not_found=True)
    if page is None:
        verify_target(api, repository, repository_id, branch, expected_head)
        api(route, "POST", {"build_type": "workflow"})
        page = api(route)
    url = site_url(page)
    verify_target(api, repository, repository_id, branch, expected_head)
    api(workflow + "/dispatches", "POST", {"ref": branch})
    return {
        "repository": repository,
        "head": expected_head,
        "url": url,
        "configured": True,
        "dispatch_requested": True,
        "deployment_verified": False,
    }

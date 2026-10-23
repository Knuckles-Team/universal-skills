#!/usr/bin/env python3
"""Test-file and error-handling rewrites for the ``--sdk-centralize`` codemod.

Once the base client builds its session with ``create_http_client`` the rest of a
connector still talks ``requests``: tests patch ``requests.Session`` and build
``requests`` errors, and tool code catches ``requests`` errors. This module turns
the *recognizable* forms into their httpx/SDK equivalents and reports every other
form as a precise blocker (the repo then stays an EXCEPTION).

Rewrites (``ast`` analysis, byte-offset splices so untouched code keeps its format):

* ``patch("requests.Session")`` / ``patch("<base module>.requests.Session")``
  -> ``patch("<base module>.create_http_client")`` (``mock.return_value`` is the session mock).
* ``requests.[exceptions.]HTTPError/ConnectionError/Timeout/RequestException`` (also the
  ``from requests import ...`` / ``from requests.exceptions import ...`` forms) ->
  ``httpx.HTTPStatusError/ConnectError/TimeoutException/HTTPError`` with ``import httpx``;
  ``import requests`` is dropped when nothing else uses it.
* Mock TLS profiles (``X.configure_requests_session.side_effect = ...``) gain ``X.proxy_url = None``
  because httpx rejects a MagicMock proxy URL.

Blockers carry a precise code: ``tests-requests-mock``, ``tests-requests-response``,
``tests-patch-session-method``, ``tests-patch-requests-function``, ``tests-requests-call``,
``tests-asserts-configure-session``, ``catches-requests-errors-*``, ``requests-response-outside-base``.
"""

from __future__ import annotations

import ast
import re
from dataclasses import dataclass, field

ERR_MAP = {
    "HTTPError": "HTTPStatusError",
    "ConnectionError": "ConnectError",
    "Timeout": "TimeoutException",
    "RequestException": "HTTPError",
}
#: requests-only response attributes with no httpx spelling (``.json()``/``.text``/``.status_code`` are shared).
BAD_ATTRS = {"ok", "iter_content", "reason", "apparent_encoding", "links", "raw"}
VERBS = {"get", "post", "put", "patch", "delete", "head", "options", "request"}
MOCK_LIBS = re.compile(r"^\s*(import (responses|requests_mock)\b|from (responses|requests_mock)\b)", re.M)
SESSION_STR = re.compile(r"^(?:(?P<mod>[\w.]*?)\.)?requests\.Session$")
OTHER_STR = re.compile(r"(?:^|\.)requests\.(?P<rest>Session\.\w+|get|post|put|delete|patch|request|head|options|adapters\.\w+)$")


@dataclass
class FileResult:
    text: str | None = None  # rewritten source (None = unchanged)
    blockers: list[tuple[str, str]] = field(default_factory=list)  # (code, detail)


def _requests_imports(tree: ast.Module) -> tuple[list[ast.stmt], dict[str, str]]:
    """requests import statements and the local names bound from ``from requests[.exceptions] import X``."""
    nodes: list[ast.stmt] = []
    names: dict[str, str] = {}
    for n in ast.walk(tree):
        if isinstance(n, ast.Import) and any(a.name.split(".")[0] == "requests" for a in n.names):
            nodes.append(n)
        elif isinstance(n, ast.ImportFrom) and (n.module or "").split(".")[0] == "requests" and not n.level:
            nodes.append(n)
            for a in n.names:
                names[a.asname or a.name] = a.name
    return nodes, names


def _offsets(src: str) -> list[int]:
    out, pos = [], 0
    for ln in src.encode().split(b"\n"):
        out.append(pos)
        pos += len(ln) + 1
    return out


def _span(node: ast.AST, starts: list[int]) -> tuple[int, int]:
    return starts[node.lineno - 1] + node.col_offset, starts[node.end_lineno - 1] + node.end_col_offset


def _chain(node: ast.AST) -> str | None:
    parts = []
    while isinstance(node, ast.Attribute):
        parts.append(node.attr)
        node = node.value
    if isinstance(node, ast.Name):
        parts.append(node.id)
        return ".".join(reversed(parts))
    return None


def rewrite_file(src: str, rel: str, *, is_test: bool, base_dotted: str | None, place_imports) -> FileResult:
    """Analyse one non-base python file. ``place_imports(src, tree, imp_node, imports, drop_nodes) -> list[(start,end,text)]``
    returns line edits (1-based inclusive start/end lines) for the import paragraph."""
    res = FileResult()
    if is_test and MOCK_LIBS.search(src):
        res.blockers.append(("tests-requests-mock", rel))
    try:
        tree = ast.parse(src)
    except SyntaxError:
        res.blockers.append(("unparsable", rel))
        return res
    imp_nodes, from_names = _requests_imports(tree)
    has_import = any(isinstance(i, ast.Import) for i in imp_nodes)
    parents = {c: p for p in ast.walk(tree) for c in ast.iter_child_nodes(p)}
    starts = _offsets(src)
    data = src.encode()
    edits: list[tuple[int, int, str]] = []  # byte spans
    err_sites = 0
    other_requests = 0  # non-error uses of the requests name that remain
    uses_httpx = False

    def blocker(code: str, node: ast.AST, extra: str = "") -> None:
        res.blockers.append((code, f"{rel}:{getattr(node, 'lineno', 0)}{(' ' + extra) if extra else ''}"))

    def in_error_context(node: ast.AST) -> bool:
        p = parents.get(node)
        if isinstance(p, ast.Tuple):
            node, p = p, parents.get(p)
        if isinstance(p, ast.ExceptHandler) and p.type is node:
            return True
        if isinstance(p, ast.Call) and node in p.args[:2]:
            fn = _chain(p.func) or ""
            return fn.endswith("raises") or fn == "isinstance"
        return False

    def map_error(node: ast.AST, cls: str) -> None:
        nonlocal err_sites, uses_httpx
        if cls not in ERR_MAP:
            blocker(f"catches-requests-errors-{cls}" if not is_test else "tests-requests-error-class", node, cls)
            return
        p = parents.get(node)
        if isinstance(p, ast.Call) and p.func is node:
            if cls == "HTTPError" or len(p.args) != 1 or p.keywords:
                blocker("tests-requests-error-construction" if is_test else "catches-requests-errors-construct", node, f"{cls}(...)")
                return
        elif not in_error_context(node):
            blocker("tests-requests-error-class" if is_test else "catches-requests-errors-use", node, cls)
            return
        s, e = _span(node, starts)
        edits.append((s, e, f"httpx.{ERR_MAP[cls]}"))
        err_sites += 1
        uses_httpx = True

    handled: set[int] = set()
    for n in ast.walk(tree):
        if isinstance(n, ast.Attribute):
            ch = _chain(n)
            if ch and ch.startswith("requests.") and has_import and id(n) not in handled:
                parts = ch.split(".")
                if len(parts) >= 3 and parts[1] == "exceptions" or len(parts) == 2 and parts[1] in ERR_MAP:
                    # mark sub-attributes as handled (requests.exceptions inside requests.exceptions.X)
                    sub = n.value
                    while isinstance(sub, ast.Attribute):
                        handled.add(id(sub))
                        sub = sub.value
                    if parts[1] == "exceptions" and len(parts) == 3:
                        map_error(n, parts[2])
                    elif len(parts) == 2:
                        map_error(n, parts[1])
                    else:
                        blocker("catches-requests-errors-shape", n, ch)
                    continue
                handled.add(id(n))
                sub = n.value
                while isinstance(sub, ast.Attribute):
                    handled.add(id(sub))
                    sub = sub.value
                other_requests += 1
                if is_test:
                    if parts[1] == "Response" or parts[1] in {"models", "structures"}:
                        blocker("tests-requests-response", n, ch)
                    elif parts[1] == "Session":
                        blocker("tests-patch-session-method", n, ch)
                    elif parts[1] in VERBS:
                        blocker("tests-requests-call", n, ch)
                    else:
                        blocker("tests-bind-requests", n, ch)
                elif parts[1] in {"Response", "models", "structures"}:
                    blocker("requests-response-outside-base", n, ch)
            if n.attr in BAD_ATTRS and not is_test:
                # only meaningful when the file maps/uses requests errors; checked below via err_sites
                n._bad = True  # type: ignore[attr-defined]
        elif isinstance(n, ast.Name) and isinstance(n.ctx, ast.Load) and n.id in from_names:
            orig = from_names[n.id]
            if orig.endswith("Warning"):
                continue
            if orig in ERR_MAP:
                map_error(n, orig)
            else:
                other_requests += 1
                blocker("tests-bind-requests" if is_test else "requests-response-outside-base", n, orig)
        elif isinstance(n, ast.Constant) and isinstance(n.value, str) and is_test:
            m = SESSION_STR.match(n.value)
            p = parents.get(n)
            if m:
                is_patch = isinstance(p, ast.Call) and (_chain(p.func) or "").split(".")[-1] == "patch" and p.args and p.args[0] is n
                mod = m.group("mod")
                if is_patch and base_dotted and mod in (None, "", base_dotted):
                    s, e = _span(n, starts)
                    q = data[s : s + 1].decode()
                    edits.append((s, e, f"{q}{base_dotted}.create_http_client{q}"))
                elif is_patch and base_dotted:
                    blocker("tests-patch-session-other-module", n, n.value)
                else:
                    blocker("tests-bind-requests", n, n.value)
            elif OTHER_STR.search(n.value):
                rest = OTHER_STR.search(n.value).group("rest")
                blocker("tests-patch-session-method" if rest.startswith("Session.") else "tests-patch-requests-function", n, n.value)
    # `from requests[.exceptions] import X` must name only mapped error classes
    for imp in imp_nodes:
        if isinstance(imp, ast.ImportFrom):
            if imp.module not in ("requests", "requests.exceptions"):
                blocker("tests-bind-requests" if is_test else "catches-requests-errors-import", imp, imp.module or "")
            for al in imp.names:
                if al.name not in ERR_MAP and not al.name.endswith("Warning"):
                    blocker("tests-bind-requests" if is_test else "catches-requests-errors-import", imp, al.name)
    # error classes are only safe to map when nothing in the file still talks requests directly
    if err_sites and not is_test and other_requests:
        blocker("catches-requests-errors-mixed", tree, "file also calls requests directly")
    # response-API use next to mapped error handling is a behaviour change
    if err_sites and not is_test:
        for n in ast.walk(tree):
            if getattr(n, "_bad", False):
                blocker("catches-requests-errors-response-api", n, f".{n.attr}")
    # configure_requests_session on mock TLS profiles
    for n in ast.walk(tree):
        if isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute) and n.func.attr.startswith("assert_"):
            ch = _chain(n.func.value) or ""
            if ch.endswith("configure_requests_session"):
                blocker("tests-asserts-configure-session", n)
        if (
            is_test
            and isinstance(n, ast.Assign)
            and len(n.targets) == 1
            and isinstance(n.targets[0], ast.Attribute)
            and n.targets[0].attr == "side_effect"
            and isinstance(n.targets[0].value, ast.Attribute)
            and n.targets[0].value.attr == "configure_requests_session"
        ):
            holder = ast.get_source_segment(src, n.targets[0].value.value) or ""
            if holder and f"{holder}.proxy_url" not in src:
                indent = " " * n.col_offset
                end = starts[n.end_lineno] if n.end_lineno < len(starts) else len(data)
                edits.append((end, end, f"{indent}{holder}.proxy_url = None\n"))
    if res.blockers:
        return res
    if not edits:
        return res
    # error-class edits need `import httpx`; the Session-string edit does not.
    out = data
    for s, e, t in sorted(edits, reverse=True):
        out = out[:s] + t.encode() + out[e:]
    text = out.decode()
    if uses_httpx or imp_nodes:
        text = _fix_imports(text, rel, place_imports, uses_httpx)
        if text is None:
            res.blockers.append(("unparsable", rel))
            return res
    res.text = text
    return res


def _fix_imports(text: str, rel: str, place_imports, uses_httpx: bool) -> str | None:
    """Drop ``import requests`` / ``from requests... import`` that nothing uses any more; add ``import httpx``."""
    try:
        tree = ast.parse(text)
    except SyntaxError:
        return None
    imp_nodes, from_names = _requests_imports(tree)
    used = {n.id for n in ast.walk(tree) if isinstance(n, ast.Name)}
    keep: list[ast.stmt] = []
    drop: list[ast.stmt] = []
    for imp in imp_nodes:
        if isinstance(imp, ast.Import):
            (keep if "requests" in used else drop).append(imp)
        else:
            alive = [a for a in imp.names if (a.asname or a.name) in used]
            (keep if alive else drop).append(imp)
    new_imps: list[str] = []
    if uses_httpx and not any(isinstance(n, ast.Import) and any(a.name == "httpx" for a in n.names) for n in ast.walk(tree)):
        new_imps.append("import httpx")
    if not new_imps and not drop:
        return text
    top_level = [n for n in imp_nodes if n in tree.body]
    anchor = (drop or top_level or imp_nodes)[0]
    if anchor not in tree.body:
        return text if not new_imps else None  # nested import: leave as is, httpx missing -> signal
    lines = text.splitlines(keepends=True)
    edits = place_imports(text, tree, anchor, new_imps, drop)
    for start, end, repl in sorted(edits, reverse=True):
        if end >= start:
            lines[start - 1 : end] = [repl] if repl else []
        else:
            lines[start - 1 : start - 1] = [repl]
    return "".join(lines)

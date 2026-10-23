#!/usr/bin/env python3
"""Deterministic ``requests.Session`` -> agent-connector-sdk governed client codemod.

Driven from ``connector_codemod.py --sdk-centralize <repo> [--dry-run|--apply]``.

Verdicts (one per repo):

* ``AUTO``      every detected pattern is a known one; ``--apply`` rewrites it.
* ``EXCEPTION`` a pattern outside the known set was found; nothing is changed.
* ``CLEAN``     nothing to migrate (client already governed or no HTTP base).

Known client pattern (everything else is an EXCEPTION with a reason code):
a single class whose ``__init__`` builds ``requests.Session()`` (optionally via
``configure_requests_session``), sets auth with ``headers.update`` /
``.auth = (user, password)`` inside plain ``if``/``elif`` chains, and which only
calls ``.request/.get/...`` and ``.close()`` on the session. Code is analysed
with ``ast`` and edited by line-range splices, so untouched code keeps its
formatting. The pyproject/requirements/spec parts are text/TOML edits verified
with ``tomllib``. Idempotent: a second run reports ``CLEAN`` / no diff.
"""

from __future__ import annotations

import ast
import json
import re
import subprocess
import sys
import tomllib
import urllib.request
from dataclasses import dataclass, field
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import sdk_centralize_tests as sct  # noqa: E402

#: attribute names a connector stores its base URL under (first match wins).
URL_ATTRS = ("base_url", "url", "_base_url")
SESSION_METHODS = {"request", "get", "post", "put", "patch", "delete", "head", "options"}
#: requests-only keyword arguments with no safe httpx spelling.
BAD_KWARGS = {"verify", "cert", "proxies", "stream", "auth", "hooks", "cookies"}
#: requests-only response attributes.
BAD_RESPONSE_ATTRS = {"ok", "iter_content", "raw", "reason", "apparent_encoding", "links"}
SAFE_HEADERS = {"accept", "content-type", "user-agent", "accept-language"}
#: SDK extra -> packages it carries (agent-connector-sdk pyproject).
SDK_EXTRAS = {
    "integrity": ["rdflib"],
    "feeds": ["feedparser"],
    "dataprep": ["pyarrow"],
    "db": ["psycopg", "pymysql", "pymongo", "oracledb"],
    "mssql": ["pyodbc"],
    "graphql": ["graphql-core"],
    "market": ["pandas", "yfinance"],
    "stream": ["websockets"],
}
SPEC_ROWS = {
    "R001": "SDK-CENTRALIZED-CAPABILITIES-R001, SDK-CENTRALIZED-CAPABILITIES-R003, SDK-CENTRALIZED-CAPABILITIES-R008",
    "R002": "SDK-CENTRALIZED-CAPABILITIES-R040, SDK-CENTRALIZED-CAPABILITIES-R001",
}


class PatternException(Exception):
    """A pattern outside the known set; the repo is classified EXCEPTION."""


def exc(code: str, detail: str = "") -> PatternException:
    return PatternException(f"{code}: {detail}" if detail else code)


@dataclass
class Result:
    repo: str
    verdict: str = "CLEAN"
    reasons: list[str] = field(default_factory=list)
    applied: list[str] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)

    def line(self) -> str:
        out = [f"== {self.repo}: {self.verdict}"]
        out += [f"  EXCEPTION {r}" for r in self.reasons]
        out += [f"  APPLY {a}" for a in self.applied]
        out += [f"  NOTE {n}" for n in self.notes]
        return "\n".join(out)


# --------------------------------------------------------------------------- helpers
def py_files(repo: Path) -> list[Path]:
    out = subprocess.run(
        ["git", "-C", str(repo), "ls-files", "*.py"], capture_output=True, text=True, check=False
    ).stdout.split()
    if not out:  # not a git checkout (golden fixtures)
        out = [str(p.relative_to(repo)) for p in repo.rglob("*.py") if ".venv" not in p.parts]
    return [repo / f for f in sorted(out) if (repo / f).exists()]


def is_test(repo: Path, p: Path) -> bool:
    rel = p.relative_to(repo).parts
    return rel[0] in {"tests", "test"} or p.name.startswith("test_") or p.name == "conftest.py"


def src_of(src: str, node: ast.AST) -> str:
    return ast.get_source_segment(src, node) or ""


def latest_sdk_version(explicit: str | None) -> str:
    if explicit:
        return explicit
    with urllib.request.urlopen("https://pypi.org/pypi/agent-connector-sdk/json", timeout=20) as r:  # noqa: S310
        return json.load(r)["info"]["version"]


def pkg_name(spec: str) -> str:
    m = re.match(r"\s*([A-Za-z0-9_.-]+)", spec)
    return re.sub(r"[-_.]+", "-", m.group(1)).lower() if m else ""


# --------------------------------------------------------------------------- client analysis
@dataclass
class Edit:
    start: int  # 1-based first line; replacement when end >= start, insertion before `start` otherwise
    end: int
    text: str


def _is_requests_session(node: ast.AST) -> bool:
    return (
        isinstance(node, ast.Call)
        and isinstance(node.func, ast.Attribute)
        and node.func.attr == "Session"
        and isinstance(node.func.value, ast.Name)
        and node.func.value.id == "requests"
    )


def _unwrap_session(value: ast.AST) -> bool:
    """``requests.Session()`` or ``<x>.configure_requests_session(requests.Session())``."""
    if _is_requests_session(value):
        return True
    return (
        isinstance(value, ast.Call)
        and isinstance(value.func, ast.Attribute)
        and value.func.attr == "configure_requests_session"
        and len(value.args) == 1
        and _is_requests_session(value.args[0])
    )


def _self_attr(node: ast.AST, name: str | None = None) -> str | None:
    if (
        isinstance(node, ast.Attribute)
        and isinstance(node.value, ast.Name)
        and node.value.id == "self"
        and (name is None or node.attr == name)
    ):
        return node.attr
    return None


def _auth_leaf(stmt: ast.stmt, attr: str, src: str) -> tuple[str, dict[str, str]] | None:
    """Translate one auth statement. Returns (auth_expr | '', safe_headers)."""
    if (
        isinstance(stmt, ast.Assign)
        and len(stmt.targets) == 1
        and isinstance(stmt.targets[0], ast.Attribute)
        and stmt.targets[0].attr == "auth"
        and _self_attr(stmt.targets[0].value, attr)
        and isinstance(stmt.value, ast.Tuple)
        and len(stmt.value.elts) == 2
    ):
        u, p = (src_of(src, e) for e in stmt.value.elts)
        return f"httpx.BasicAuth({u}, {p})", {}
    if (
        isinstance(stmt, ast.Expr)
        and isinstance(stmt.value, ast.Call)
        and isinstance(stmt.value.func, ast.Attribute)
        and stmt.value.func.attr == "update"
        and isinstance(stmt.value.func.value, ast.Attribute)
        and stmt.value.func.value.attr == "headers"
        and _self_attr(stmt.value.func.value.value, attr)
        and len(stmt.value.args) == 1
        and isinstance(stmt.value.args[0], ast.Dict)
    ):
        auth, safe = "", {}
        for k, v in zip(stmt.value.args[0].keys, stmt.value.args[0].values, strict=True):
            if not (isinstance(k, ast.Constant) and isinstance(k.value, str)):
                return None
            key = k.value
            if key.lower() in SAFE_HEADERS:
                safe[key] = src_of(src, v)
                continue
            if auth:
                return None  # two credential headers
            expr = _credential_expr(key, v, src)
            if expr is None:
                return None
            auth = expr
        return auth, safe
    return None


def _credential_expr(key: str, value: ast.AST, src: str) -> str | None:
    if (
        key.lower() == "authorization"
        and isinstance(value, ast.JoinedStr)
        and len(value.values) == 2
        and isinstance(value.values[0], ast.Constant)
        and isinstance(value.values[1], ast.FormattedValue)
        and not value.values[1].format_spec
    ):
        prefix = value.values[0].value
        var = src_of(src, value.values[1].value)
        if prefix == "Bearer ":
            return f"BearerAuth({var})"
        return f"ApiKeyAuth({var}, header={key!r}, prefix={prefix!r})"
    if isinstance(value, ast.Name | ast.Attribute):
        return f"ApiKeyAuth({src_of(src, value)}, header={key!r})"
    return None


def _rewrite_auth_tree(
    stmts: list[ast.stmt], attr: str, src: str, edits: list[Edit], top: bool, hoisted: dict[str, str]
) -> bool:
    """Rewrite leaves of an if/elif chain in place. Returns True if an auth expression was produced."""
    matched = False
    for st in stmts:
        if isinstance(st, ast.If):
            m1 = _rewrite_auth_tree(st.body, attr, src, edits, False, hoisted)
            m2 = _rewrite_auth_tree(st.orelse, attr, src, edits, False, hoisted)
            matched = matched or m1 or m2
            continue
        leaf = _auth_leaf(st, attr, src)
        if leaf is None:
            continue
        expr, safe = leaf
        if safe and not top:
            raise exc("conditional-default-headers", src_of(src, st)[:60])
        hoisted.update(safe)
        indent = " " * st.col_offset
        edits.append(Edit(st.lineno, st.end_lineno or st.lineno, f"{indent}auth = {expr}\n" if expr else ""))
        matched = matched or bool(expr)
    return matched


def import_edits(src: str, tree: ast.Module, anchor: ast.stmt, new_imps: list[str], drop: list[ast.stmt]) -> list[tuple[int, int, str]]:
    """Line edits ``(start, end, text)`` that add ``new_imps`` near ``anchor`` and delete the ``drop`` imports.

    When the anchor's import paragraph is all third-party, the paragraph is re-sorted isort-style
    (``import x`` lines first, then ``from x import`` lines, each by module name); otherwise the new
    lines take the anchor's position (or follow it when the anchor stays).
    """
    body = tree.body
    i = body.index(anchor)
    lo = hi = i

    def adjacent(a: ast.stmt, b: ast.stmt) -> bool:
        return isinstance(a, ast.Import | ast.ImportFrom) and isinstance(b, ast.Import | ast.ImportFrom) and b.lineno == (a.end_lineno or a.lineno) + 1

    while lo > 0 and adjacent(body[lo - 1], body[lo]):
        lo -= 1
    while hi + 1 < len(body) and adjacent(body[hi], body[hi + 1]):
        hi += 1
    para = body[lo : hi + 1]
    stdlib = sys.stdlib_module_names
    lines = src.splitlines(keepends=True)
    out: list[tuple[int, int, str]] = []
    for d in drop:
        if d not in para:
            out.append((d.lineno, d.end_lineno or d.lineno, ""))

    def top(n: ast.stmt) -> str:
        return (n.names[0].name if isinstance(n, ast.Import) else (n.module or "")).split(".")[0]

    block = "".join(f"{ln}\n" for ln in new_imps)
    if any(top(n) in stdlib or top(n) == "__future__" or (isinstance(n, ast.ImportFrom) and n.level) for n in para):
        if anchor in drop:
            out.append((anchor.lineno, anchor.end_lineno or anchor.lineno, block))
        elif block:
            out.append(((anchor.end_lineno or anchor.lineno) + 1, anchor.end_lineno or anchor.lineno, block))
        for d in drop:
            if d in para and d is not anchor:
                out.append((d.lineno, d.end_lineno or d.lineno, ""))
        return out
    stmts: list[tuple[int, str, str]] = []  # (kind 0=import 1=from, module, text)
    for n in para:
        if n in drop:
            continue
        text = "".join(lines[n.lineno - 1 : n.end_lineno])
        stmts.append((0 if isinstance(n, ast.Import) else 1, (n.names[0].name if isinstance(n, ast.Import) else n.module or "").lower(), text))
    for ln in new_imps:
        stmts.append((0 if ln.startswith("import ") else 1, ln.split()[1].lower(), ln + "\n"))
    stmts.sort(key=lambda t: (t[0], t[1]))
    out.append((para[0].lineno, para[-1].end_lineno or para[-1].lineno, "".join(t[2] for t in stmts)))
    return out


class ClientPlan:
    def __init__(self, repo: Path, path: Path, src: str, tree: ast.Module):
        self.repo, self.path, self.src, self.tree = repo, path, src, tree
        self.rel = str(path.relative_to(repo))
        self.edits: list[Edit] = []
        self.inline: list[tuple[int, int, str, str]] = []
        self.attr = ""
        self.tls_name = ""

    def analyse(self) -> None:
        tree = self.tree
        for n in ast.walk(tree):
            if isinstance(n, ast.ImportFrom) and (n.module or "").split(".")[0] == "requests":
                raise exc("requests-from-import", f"{self.rel}:{n.lineno}")
        imp = [n for n in tree.body if isinstance(n, ast.Import) and any(a.name == "requests" for a in n.names)]
        if len(imp) != 1 or len(imp[0].names) != 1 or imp[0].names[0].asname:
            raise exc("requests-import-shape", self.rel)
        self.import_node = imp[0]
        classes = [
            c
            for c in tree.body
            if isinstance(c, ast.ClassDef)
            and any(_unwrap_session(a.value) for a in ast.walk(c) if isinstance(a, ast.Assign))
        ]
        if len(classes) != 1:
            raise exc("session-class-count", f"{len(classes)} in {self.rel}")
        cls = classes[0]
        init = next((f for f in cls.body if isinstance(f, ast.FunctionDef) and f.name == "__init__"), None)
        if init is None:
            raise exc("no-init")
        self.cls, self.init = cls, init
        self._find_session_setup()
        self._check_uses()
        self._check_request_calls()
        self._check_init_signature()
        # any other use of the name ``requests`` in the file
        for n in ast.walk(tree):
            if isinstance(n, ast.Name) and n.id == "requests" and not (self.import_node.lineno <= n.lineno <= (self.import_node.end_lineno or 0)):
                if not any(
                    n.lineno >= s.lineno and n.lineno <= (s.end_lineno or s.lineno) for s in self.setup
                ):
                    raise exc("requests-other-use", f"{self.rel}:{n.lineno}")

    def _find_session_setup(self) -> None:
        a = None
        for st in self.init.body:
            if isinstance(st, ast.Assign) and len(st.targets) == 1 and _unwrap_session(st.value):
                t = st.targets[0]
                if not _self_attr(t):
                    raise exc("session-target", src_of(self.src, st)[:60])
                a = t.attr
                self.assign_stmt = st
                break
        if a is None:
            raise exc("session-not-top-level-in-init")
        self.attr = a
        self.setup: list[ast.stmt] = [self.assign_stmt]
        for st in self.init.body:
            if (
                isinstance(st, ast.Expr)
                and isinstance(st.value, ast.Call)
                and isinstance(st.value.func, ast.Attribute)
                and st.value.func.attr == "configure_requests_session"
                and len(st.value.args) == 1
                and _self_attr(st.value.args[0], a)
            ):
                self.setup.append(st)
        tls_idx = None
        for i, st in enumerate(self.init.body):
            if isinstance(st, ast.Assign) and _self_attr(st.targets[0], "tls_profile"):
                m = re.search(r"resolve_tls_profile\(\s*[\"']([^\"']+)[\"']", src_of(self.src, st))
                if m:
                    self.tls_name = m.group(1)
                    tls_idx = i
        if tls_idx is None:
            raise exc("no-tls-profile-line", "self.tls_profile = ... resolve_tls_profile('<name>') not found")
        self.tls_idx = tls_idx
        self.url_attr = next(
            (u for u in URL_ATTRS if any(isinstance(st, ast.Assign) and _self_attr(st.targets[0], u) for st in self.init.body)),
            "",
        )
        if not self.url_attr:
            raise exc("no-self-base-url")

    def _check_uses(self) -> None:
        a = self.attr
        auth_nodes = [st for st in ast.walk(self.cls) if isinstance(st, ast.stmt) and _auth_leaf(st, a, self.src) is not None]
        allowed = {id(n) for st in [*self.setup, *auth_nodes] for n in ast.walk(st)}
        call_ok = set()
        for n in ast.walk(self.cls):
            if isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute) and _self_attr(n.func.value, a):
                if n.func.attr in SESSION_METHODS | {"close"}:
                    call_ok.add(id(n.func.value))
        for n in ast.walk(self.cls):
            if _self_attr(n, a) and id(n) not in allowed and id(n) not in call_ok:
                raise exc("session-use", f"{self.rel}:{n.lineno} {src_of(self.src, n)}")
        self.auth_nodes = auth_nodes

    def _check_request_calls(self) -> None:
        a = self.attr
        for fn in [f for f in ast.walk(self.cls) if isinstance(f, ast.FunctionDef)]:
            params = {p.arg: (src_of(self.src, p.annotation) if p.annotation else "") for p in fn.args.args + fn.args.kwonlyargs}
            if fn.args.kwarg:
                params[fn.args.kwarg.arg] = "**"
            locals_ = {t.id for n in ast.walk(fn) if isinstance(n, ast.Assign) for t in n.targets if isinstance(t, ast.Name)}
            locals_ |= {n.target.id for n in ast.walk(fn) if isinstance(n, ast.AnnAssign) and isinstance(n.target, ast.Name)}
            for call in [c for c in ast.walk(fn) if isinstance(c, ast.Call)]:
                f = call.func
                if not (isinstance(f, ast.Attribute) and f.attr in SESSION_METHODS and _self_attr(f.value, a)):
                    continue
                for kw in call.keywords:
                    if kw.arg is None:
                        v = kw.value
                        if not (isinstance(v, ast.Name) and v.id in locals_ and v.id not in params):
                            raise exc("kwargs-passthrough", f"{self.rel}:{call.lineno} **{src_of(self.src, v)}")
                        continue
                    if kw.arg in BAD_KWARGS:
                        raise exc("requests-only-kwarg", f"{self.rel}:{call.lineno} {kw.arg}=")
                    if kw.arg == "timeout" and not isinstance(kw.value, ast.Constant | ast.Name):
                        raise exc("timeout-shape", f"{self.rel}:{call.lineno}")
                    if kw.arg == "allow_redirects":
                        self.inline.append((kw.lineno, kw.col_offset, kw.arg, "follow_redirects"))
                    if kw.arg == "data" and isinstance(kw.value, ast.Name):
                        ann = params.get(kw.value.id, "")
                        if ann and re.search(r"\b(str|bytes)\b", ann) and "dict" not in ann and "Any" not in ann:
                            self.inline.append((kw.lineno, kw.col_offset, kw.arg, "content"))
        for n in ast.walk(self.cls):
            if isinstance(n, ast.Attribute) and n.attr in BAD_RESPONSE_ATTRS:
                raise exc("requests-response-api", f"{self.rel}:{n.lineno} .{n.attr}")

    def _check_init_signature(self) -> None:
        args = {a.arg: src_of(self.src, a.annotation) if a.annotation else "" for a in self.init.args.args}
        self.url_param = next((u for u in ("base_url", "url") if u in args), "")
        if not self.url_param:
            raise exc("no-base-url-param")
        if "None" in args[self.url_param]:
            raise exc("optional-base-url", f"{self.url_param}: {args[self.url_param]}")

    def _top(self, node: ast.AST) -> ast.stmt:
        for st in self.init.body:
            if st.lineno <= node.lineno <= (st.end_lineno or st.lineno):
                return st
        raise exc("node-outside-init", str(node.lineno))

    def plan(self) -> None:
        a, src = self.attr, self.src
        hoisted: dict[str, str] = {}
        auth_edits: list[Edit] = []
        matched = _rewrite_auth_tree(self.init.body, a, src, auth_edits, True, hoisted)
        covered = {e.start for e in auth_edits}
        for n in self.auth_nodes:
            if n.lineno not in covered:
                raise exc("auth-outside-init-tree", f"{self.rel}:{n.lineno}")
        tops = [self._top(n) for n in [*self.setup, *self.auth_nodes]]
        if self.tls_idx > max(self.init.body.index(t) for t in tops):
            raise exc("tls-profile-after-client-config")
        first = min(t.lineno for t in tops)
        last = max(t.end_lineno or t.lineno for t in tops)
        indent = " " * self.setup[0].col_offset
        opts = [f"base_url=self.{self.url_attr}", "tls=self.tls_profile"]
        if matched:
            opts.append("auth=auth")
        if hoisted:
            opts.append("headers={" + ", ".join(f"{k!r}: {v}" for k, v in hoisted.items()) + "}")
        opts.append(f'allow_plaintext=self.{self.url_attr}.startswith("http://")')
        create = [f"self.{a} = create_http_client(", "    HttpClientOptions("]
        create += [f"        {o}," for o in opts]
        create += ["    )", ")"]
        for s in self.setup:
            self.edits.append(Edit(s.lineno, s.end_lineno or s.lineno, ""))
        self.edits += auth_edits
        if matched:
            self.edits.append(Edit(first, first - 1, f"{indent}auth: httpx.Auth | None = None\n"))
        self.edits.append(Edit(last + 1, last, "".join(f"{indent}{ln}\n" for ln in create)))
        new_imps = [
            "import httpx",
            "from agent_connector_sdk.http.client import create_http_client",
            "from agent_connector_sdk.http.options import HttpClientOptions",
        ]
        text_all = "".join(e.text for e in self.edits)
        for n in ("ApiKeyAuth", "BearerAuth"):
            if n in text_all:
                new_imps.append(f"from agent_connector_sdk.auth.static import {n}")
        self._place_imports(new_imps)

    def _place_imports(self, new_imps: list[str]) -> None:
        """Replace ``import requests`` by the SDK imports (see ``import_edits``)."""
        imp = self.import_node
        self.edits += [Edit(a, b, t) for a, b, t in import_edits(self.src, self.tree, imp, new_imps, [imp])]

    def render(self) -> str:
        lines = self.src.splitlines(keepends=True)
        for ln, col, old, new in self.inline:
            line = lines[ln - 1]
            lines[ln - 1] = line[:col] + new + line[col + len(old) :]
        for e in sorted(self.edits, key=lambda e: (e.start, e.end), reverse=True):
            if e.end >= e.start:
                lines[e.start - 1 : e.end] = [e.text] if e.text else []
            else:
                lines[e.start - 1 : e.start - 1] = [e.text]
        return "".join(lines)


# --------------------------------------------------------------------------- repo-level detection
def scan_exceptions(repo: Path, files: list[Path], base: Path | None) -> list[str]:
    """Patterns the codemod does not handle; any hit makes the repo an EXCEPTION."""
    reasons: list[str] = []
    for p in files:
        rel = str(p.relative_to(repo))
        text = p.read_text(errors="replace")
        try:
            tree = ast.parse(text)
        except SyntaxError:
            reasons.append(f"unparsable: {rel}")
            continue
        if not is_test(repo, p):
            if re.search(r"env://|openbao://", text):
                reasons.append(f"secret-parsing: {rel} (hand-parsed env:// or openbao://)")
            if re.search(r"disable_warnings|ssl\.create_default_context|verify\s*=\s*False|_create_unverified", text):
                reasons.append(f"tls-handbuilt: {rel}")
            if re.search(r"max_retries|Retry-After|backoff", text, re.I) and re.search(r"sleep\(", text) and re.search(r"for\s+\w+\s+in\s+range\(|while\s", text):
                reasons.append(f"retry-loop: {rel}")
            if p == base and re.search(r"next_page|while\s+True", text) and re.search(r"page|offset|cursor", text):
                reasons.append(f"pagination-in-base: {rel}")
    return list(dict.fromkeys(reasons))


def _builds_session(text: str) -> bool:
    """True when the module really calls ``requests.Session`` (a docstring mention does not count)."""
    if "requests.Session" not in text:
        return False
    try:
        return any(_is_requests_session(n) for n in ast.walk(ast.parse(text)))
    except SyntaxError:
        return True


def find_base(repo: Path, files: list[Path]) -> tuple[Path | None, list[Path]]:
    cands = [p for p in files if not is_test(repo, p) and _builds_session(p.read_text(errors="replace"))]
    return (cands[0] if len(cands) == 1 else None), cands


def uses_attr_elsewhere(repo: Path, files: list[Path], base: Path, attr: str) -> str | None:
    """Non-test code outside the base that touches the session attr; tests only when they use requests-only members."""
    requests_only = {"headers", "auth", "verify", "mount", "adapters", "cert", "proxies"}
    for p in files:
        if p == base:
            continue
        try:
            tree = ast.parse(p.read_text(errors="replace"))
        except SyntaxError:
            continue
        test = is_test(repo, p)
        for n in ast.walk(tree):
            if not (isinstance(n, ast.Attribute) and n.attr == attr and isinstance(n.value, ast.Attribute | ast.Name)):
                continue
            if not test:
                return f"{p.relative_to(repo)}:{n.lineno}"
        if test:
            for n in ast.walk(tree):
                if (
                    isinstance(n, ast.Attribute)
                    and n.attr in requests_only
                    and isinstance(n.value, ast.Attribute)
                    and n.value.attr == attr
                ):
                    return f"{p.relative_to(repo)}:{n.lineno} (test uses session .{n.attr})"
    return None


# --------------------------------------------------------------------------- pyproject / requirements
def _drop_pin(text: str, name: str) -> str:
    spec = r'[ \t]*"\s*' + re.escape(name) + r'(?:\[[^\]]*\])?\s*(?:[<>=!~;][^"]*)?"\s*,?[ \t]*'
    return re.sub(spec, "", text, flags=re.I)


def edit_pyproject(repo: Path, sdk: str, imports_requests: bool, imports_httpx: bool, res: Result, apply: bool) -> None:
    path = repo / "pyproject.toml"
    if path.exists():
        src = path.read_text()
        text = re.sub(
            r"(agent-connector-sdk(?:\[[^\]]*\])?)>=[0-9][0-9A-Za-z.]*",
            lambda m: f"{m.group(1)}>={sdk}",
            src,
        )
        if not imports_requests:
            text = _drop_pin(text, "requests")
        if not imports_httpx:
            text = _drop_pin(text, "httpx")
        text = replace_driver_pins(text, res)
        try:
            tomllib.loads(text)
        except tomllib.TOMLDecodeError as e:
            raise exc("toml-edit-invalid", str(e)) from e
        if text != src:
            res.applied.append(f"pyproject.toml (SDK floor >={sdk}; unused requests/httpx pins; driver pins -> extras)")
            if apply:
                path.write_text(text)
    for rq in sorted(repo.glob("requirements*.txt")):
        s = rq.read_text()
        t = re.sub(r"(?m)^(agent-connector-sdk(?:\[[^\]]*\])?)>=[0-9][0-9A-Za-z.]*", lambda m: f"{m.group(1)}>={sdk}", s)
        if not imports_requests:
            t = re.sub(r"(?mi)^requests(?:\[[^\]]*\])?\s*[<>=!~].*\n?", "", t)
        if not imports_httpx:
            t = re.sub(r"(?mi)^httpx(?:\[[^\]]*\])?\s*[<>=!~].*\n?", "", t)
        if t != s:
            res.applied.append(f"{rq.name} (SDK floor / unused pins)")
            if apply:
                rq.write_text(t)


def replace_driver_pins(text: str, res: Result) -> str:
    try:
        data = tomllib.loads(text)
    except tomllib.TOMLDecodeError:
        return text
    lists = [data.get("project", {}).get("dependencies", [])]
    lists += list(data.get("project", {}).get("optional-dependencies", {}).values())
    for deps in lists:
        pins = {pkg_name(d): d for d in deps}
        for extra, pkgs in SDK_EXTRAS.items():
            hit = [p for p in pkgs if p in pins]
            if not hit:
                continue
            sdk_entry = next((d for d in deps if pkg_name(d) == "agent-connector-sdk"), None)
            if len(pkgs) > 1 and len(hit) != len(pkgs):
                res.notes.append(f"extra '{extra}' not applied: only {hit} of {pkgs} pinned (partial coverage)")
                continue
            if not sdk_entry:
                res.notes.append(f"extra '{extra}' not applied: no agent-connector-sdk entry in the same list as {hit}")
                continue
            for p in hit:
                text = _drop_pin(text, pins[p].split("[")[0].split(">")[0].split("=")[0].split("<")[0].strip())
            m = re.match(r"agent-connector-sdk(?:\[([^\]]*)\])?(.*)", sdk_entry)
            extras = sorted({*(x.strip() for x in (m.group(1) or "").split(",") if x.strip()), extra})
            text = text.replace(f'"{sdk_entry}"', f'"agent-connector-sdk[{",".join(extras)}]{m.group(2)}"', 1)
    return text


# --------------------------------------------------------------------------- version bump
def bump_patch(repo: Path, res: Result, apply: bool) -> None:
    """Patch-bump through the repo's ``.bumpversion.cfg`` (every configured file, incl. the Dockerfile pin).

    Skips versions that are already tagged: a release for an existing tag fails
    ("existing release tag conflicts with frozen build source").
    """
    import configparser

    cfg_path = repo / ".bumpversion.cfg"
    if not cfg_path.exists():
        res.notes.append("no .bumpversion.cfg; version not bumped")
        return
    cp = configparser.RawConfigParser()
    cp.read(cfg_path)
    cur = cp["bumpversion"]["current_version"]
    major, minor, patch = (int(x) for x in cur.split("."))
    tags = set(subprocess.run(["git", "-C", str(repo), "tag", "-l"], capture_output=True, text=True, check=False).stdout.split())
    while True:
        patch += 1
        new = f"{major}.{minor}.{patch}"
        if new not in tags and f"v{new}" not in tags:
            break
    res.applied.append(f"version {cur} -> {new} via .bumpversion.cfg files (not tagged yet)")
    if not apply:
        return
    for section in cp.sections():
        if not section.startswith("bumpversion:file"):
            continue
        target = repo / section.split(":", 2)[2]
        search = cp[section].get("search", "{current_version}").replace("{current_version}", cur)
        replace = cp[section].get("replace", "{new_version}").replace("{new_version}", new)
        text = target.read_text()
        if search not in text:
            raise exc("bump-search-miss", f"{target.relative_to(repo)}: {search!r}")
        target.write_text(text.replace(search, replace))
    cfg_path.write_text(cfg_path.read_text().replace(f"current_version = {cur}", f"current_version = {new}", 1))


# --------------------------------------------------------------------------- spec generation
def _cite(k: str) -> str:
    return ", ".join(f"`{x.strip()}`" for x in SPEC_ROWS[k].split(","))


def _sid(name: str) -> str:
    return f"CONN-{re.sub(r'[^A-Z0-9]+', '-', name.upper()).strip('-')}-SDK-CENTRALIZATION"


def spec_files(name: str, module_path: str, cls_name: str, client: bool = True) -> dict[str, str]:
    sid = _sid(name)
    ids = [f"{sid}-R00{n}" for n in (1, 2, 3)]
    rows = [
        (ids[0], "Requests use the governed SDK client",
         f"{name} must send every vendor request through the SDK governed HTTP client with its resolved TLS profile and SDK auth. It must not build its own session. This row follows {_cite('R001')}.",
         "A unit test shows the API client holds an httpx client and a request carries the configured credential through a mock transport"),
        (ids[1], "SDK floor and dependency set",
         f"The package must require the current agent-connector-sdk floor and must not pin requests or httpx while nothing imports them directly. Optional drivers come from SDK extras. This row follows {_cite('R002')}.",
         "pyproject.toml shows the floor and no unused requests pin"),
        (ids[2], "Production wiring and hot path",
         f"`{cls_name}.__init__` in `{module_path}` calls `create_http_client`, and every domain client reaches it through `request`. A transient 503 is retried by the SDK policy. This row follows {_cite('R001')}.",
         "A test builds the client with a mock transport, sees a 503 then a 200, and gets one result"),
    ]
    if not client:  # dependency-only repo: the one row is the floor / dependency set
        rows = [(ids[0], *rows[1][1:])]
    req = f"# {sid} requirements\n\nEach row defines one requirement. [`status.json`](status.json) holds the generated state.\n\n| ID | Requirement | Verification |\n|---|---|---|\n"
    req += "".join(f"| `{i}` | **{t}.** {b} | {v} |\n" for i, t, b, v in rows)
    spec = (
        f"# {sid} — Shared SDK capabilities in {name}\n\n**Owner:** {name}.\n\n"
        "See [`requirements.md`](requirements.md) for each row and [`status.json`](status.json) for its generated state.\n\n"
        f"## Purpose\n\n{name} must use the agent-connector-sdk capability for each concern the SDK centralizes. A connector copy of a centralized capability splits policy across the fleet.\n\n"
        f"## Why a new spec\n\nSearch: `git grep -n \"SDK\" -- specs` found no row that owns SDK capability use in {name}. The SDK index spec `SDK-CENTRALIZED-CAPABILITIES` owns the capabilities. This spec owns the connector side of each one.\n\n"
        "## Requirements\n\n" + "".join(f"- `{i}`: {t}.\n" for i, t, _, _ in rows)
    )
    live = (
        f"`{cls_name}.__init__` in `{module_path}` calls `create_http_client`. Every domain client and MCP tool calls `{cls_name}.request`."
        if client
        else f"{name} already builds its HTTP clients through the SDK; this spec owns only the dependency floor and extras."
    )
    plan = (
        f"# {sid} design and implementation plan\n\n## Existing system and reuse\n\n"
        f"The SDK owns every capability named in the rows ({_cite('R001')}). {name} adds no module that repeats one. Each row deletes connector code and calls the SDK module.\n\n"
        f"## Live call path\n\n{live}\n\n"
        "## Compatibility\n\nTool names, arguments, URL joining, error types and result shapes stay identical.\n"
    )
    tasks = f"# {sid} tasks\n\n| Task | Deliverable | Proof |\n|---|---|---|\n" + "".join(
        f"| T0{n} | {t} | {v} |\n" for n, (_, t, _, v) in enumerate(rows, 1)
    )
    tspec = (
        f"# {sid} test specification\n\nTests use synthetic credentials and mock transports. They need no network.\n\n"
        "| Scenario | Requirements | Expected result |\n|---|---|---|\n" + "".join(f"| {t} | `{i}` | {v} |\n" for i, t, _, v in rows)
    )
    status = {
        "schema_version": 2,
        "spec_id": sid,
        "owner_repo": name,
        "delivery_state": "SPECIFIED",
        "requirement_ids": ids,
        "requirements": [{"id": i, "title": t, "delivery_state": "SPECIFIED", "landed_in": [], "verified_by": []} for i, t, _, _ in rows],
    }
    return {
        "spec.md": spec, "requirements.md": req, "plan.md": plan, "tasks.md": tasks,
        "test-spec.md": tspec, "status.json": json.dumps(status, indent=2) + "\n",
    }


def deps_test_file(name: str) -> str:
    sid = _sid(name)
    return f'''"""Bound tests for {sid} (generated by connector_codemod --sdk-centralize)."""

import pathlib
import tomllib


# spec: {sid}-R001
def test_dependencies_have_no_unused_requests_pin():
    root = pathlib.Path(__file__).resolve().parents[1]
    deps = tomllib.loads((root / "pyproject.toml").read_text())["project"]["dependencies"]
    assert any(d.startswith("agent-connector-sdk") for d in deps)
    assert not any(d.lower().startswith("requests") for d in deps)
'''


def test_file(name: str, module: str, cls_name: str, attr: str, call_args: str, bearer: bool) -> str:
    sid = _sid(name)
    auth = '    assert seen[0].headers["Authorization"] == "Bearer runtime-value"\n' if bearer else ""
    return f'''"""Bound tests for {sid} (generated by connector_codemod --sdk-centralize)."""

import pathlib
import tomllib

import httpx

import {module} as base_module


def _client(handler):
    from agent_connector_sdk.http.client import create_http_client as real

    def build(options):
        return real(options, transport=httpx.MockTransport(handler))

    original = base_module.create_http_client
    base_module.create_http_client = build
    try:
        return base_module.{cls_name}({call_args})
    finally:
        base_module.create_http_client = original


# spec: {sid}-R001, {sid}-R003
def test_request_goes_through_the_governed_client():
    seen = []

    def handler(request):
        seen.append(request)
        return httpx.Response(200, json={{"ok": True}})

    client = _client(handler)
    assert isinstance(client.{attr}, httpx.Client)
    client.request("GET", "/ping")
    assert seen
    assert seen[0].url.path.endswith("/ping")
{auth}

# spec: {sid}-R003
def test_transient_status_is_retried_by_the_sdk_client(monkeypatch):
    monkeypatch.setattr("time.sleep", lambda _s: None)
    calls = []

    def handler(request):
        calls.append(request)
        if len(calls) == 1:
            return httpx.Response(503, headers={{"Retry-After": "0"}})
        return httpx.Response(200, json={{"ok": True}})

    _client(handler).request("GET", "/ping")
    assert len(calls) == 2


# spec: {sid}-R002
def test_dependencies_have_no_unused_requests_pin():
    root = pathlib.Path(__file__).resolve().parents[1]
    deps = tomllib.loads((root / "pyproject.toml").read_text())["project"]["dependencies"]
    assert any(d.startswith("agent-connector-sdk") for d in deps)
    assert not any(d.lower().startswith("requests") for d in deps)
'''


# --------------------------------------------------------------------------- driver
def _project_name(repo: Path) -> str:
    try:
        return tomllib.loads((repo / "pyproject.toml").read_text())["project"]["name"]
    except Exception:  # noqa: BLE001
        return repo.name


def _readme_index(repo: Path, name: str) -> None:
    readme = repo / "specs/README.md"
    if not readme.exists():
        return
    line = f"- [`{_sid(name)}`](sdk-centralization/spec.md) — Shared SDK capabilities in {name}"
    text = readme.read_text()
    if line in text:
        return
    if "has no local spec yet." in text:
        text = text.replace("This repository has no local spec yet.", line)
    elif "## Local specifications" in text:
        text = text.rstrip("\n") + "\n" + line + "\n"
    readme.write_text(text)


def plan_file_rewrites(repo: Path, files: list[Path], base: Path | None) -> tuple[dict[Path, str], list[str]]:
    """Per-file requests -> httpx rewrites (tests and error handling); blockers become EXCEPTION reasons."""
    base_dotted = None
    if base is not None:
        parts = list(base.relative_to(repo).with_suffix("").parts)
        base_dotted = ".".join(parts[1:] if parts[0] == "src" else parts)
    out: dict[Path, str] = {}
    reasons: list[str] = []
    for p in files:
        if p == base:
            continue
        text = p.read_text(errors="replace")
        if "requests" not in text and "responses" not in text:
            continue
        test = is_test(repo, p)
        r = sct.rewrite_file(text, str(p.relative_to(repo)), is_test=test, base_dotted=base_dotted, place_imports=import_edits)
        reasons += [f"{code}: {detail}" for code, detail in r.blockers]
        if r.text is not None and not r.blockers:
            if base is None:  # no client migration in this repo: requests stays the transport
                reasons.append(f"{'tests-bind-requests' if test else 'catches-requests-errors'}: {p.relative_to(repo)}")
            else:
                out[p] = r.text
    return out, reasons


def run(repo: Path, apply: bool, sdk_version: str | None, bump: bool = False) -> Result:
    repo = repo.resolve()
    res = Result(repo.name)
    if (repo / "specs/sdk-centralization").exists():
        res.notes.append("specs/sdk-centralization already present; nothing to do")
        return res
    sdk = latest_sdk_version(sdk_version)
    files = py_files(repo)
    base, cands = find_base(repo, files)
    reasons = scan_exceptions(repo, files, base)
    plan: ClientPlan | None = None
    new_src = ""
    if len(cands) > 1:
        reasons.append("multiple-requests-session-files: " + ", ".join(str(c.relative_to(repo)) for c in cands))
    elif base is not None:
        src = base.read_text()
        try:
            plan = ClientPlan(repo, base, src, ast.parse(src))
            plan.analyse()
            other = uses_attr_elsewhere(repo, files, base, plan.attr)
            if other:
                raise exc("session-used-outside-base", other)
            plan.plan()
            new_src = plan.render()
            ast.parse(new_src)
        except PatternException as e:
            reasons.append(str(e))
            plan = None
        except SyntaxError as e:
            reasons.append(f"render-invalid: {e}")
            plan = None
    elif any(
        re.search(r"\brequests\.(get|post|put|delete|patch|request)\(", p.read_text(errors="replace"))
        for p in files
        if not is_test(repo, p)
    ):
        reasons.append("requests-use-without-session-base: direct requests.<verb> calls")
    rewrites, rw_reasons = plan_file_rewrites(repo, files, base)
    reasons += rw_reasons
    if reasons:
        res.verdict = "EXCEPTION"
        res.reasons = list(dict.fromkeys(reasons))
        return res

    def imports(mod: str) -> bool:
        pat = re.compile(rf"^\s*(import {mod}\b|from {mod}\b)", re.M)
        return any(pat.search(rewrites.get(p, p.read_text(errors="replace"))) for p in files if p != base)

    imp_requests = imports("requests")
    imp_httpx = imports("httpx") or (base is not None and plan is None and "httpx" in base.read_text())
    try:
        if plan is not None and base is not None:
            res.applied.append(
                f"{plan.rel}: requests.Session -> create_http_client/HttpClientOptions (resolve_tls_profile({plan.tls_name!r}))"
            )
            res.applied.append("specs/sdk-centralization/ (6 files) + tests/test_sdk_centralization.py")
            for p in rewrites:
                res.applied.append(f"{p.relative_to(repo)}: requests tests/errors -> httpx / patched create_http_client")
            if apply:
                for p, t in rewrites.items():
                    p.write_text(t)
                base.write_text(new_src)
                name = _project_name(repo)
                module = ".".join(base.relative_to(repo).with_suffix("").parts)
                sd = repo / "specs/sdk-centralization"
                sd.mkdir(parents=True, exist_ok=True)
                for fname, content in spec_files(name, str(base.relative_to(repo)), plan.cls.name).items():
                    (sd / fname).write_text(content)
                params = plan.init.args.args[1:]
                n_def = len(plan.init.args.defaults)
                req = [p.arg for i, p in enumerate(params) if i < len(params) - n_def]
                bm = re.search(r"BearerAuth\((\w+)\)", new_src)
                if bm and bm.group(1) in {p.arg for p in params} and bm.group(1) not in req:
                    req.append(bm.group(1))
                call = ", ".join(
                    'base_url="https://service.example.invalid"' if a == plan.url_param else f'{a}="runtime-value"' for a in req
                )
                call = call.replace('base_url="https://service.example.invalid"', f'{plan.url_param}="https://service.example.invalid"')
                (repo / "tests").mkdir(exist_ok=True)
                (repo / "tests/test_sdk_centralization.py").write_text(
                    test_file(name, module, plan.cls.name, plan.attr, call, "BearerAuth(" in new_src)
                )
                _readme_index(repo, name)
            imp_httpx = imp_httpx  # base now imports httpx (the SDK carries it)
        edit_pyproject(repo, sdk, imp_requests, imp_httpx, res, apply)
        if plan is None and res.applied:
            res.applied.append("specs/sdk-centralization/ (6 files, floor row only) + tests/test_sdk_centralization.py")
            if apply:
                name = _project_name(repo)
                sd = repo / "specs/sdk-centralization"
                sd.mkdir(parents=True, exist_ok=True)
                for fname, content in spec_files(name, "", "", client=False).items():
                    (sd / fname).write_text(content)
                (repo / "tests").mkdir(exist_ok=True)
                (repo / "tests/test_sdk_centralization.py").write_text(deps_test_file(name))
                _readme_index(repo, name)
        if bump and res.applied:
            bump_patch(repo, res, apply)
    except PatternException as e:
        res.verdict = "EXCEPTION"
        res.reasons.append(str(e))
        res.applied = []
        return res
    res.verdict = "AUTO" if res.applied else "CLEAN"
    return res

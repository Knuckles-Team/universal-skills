"""web-crawler and web-fetch are thin callers of research.web (US-WEB-RESEARCH-R001)."""

from __future__ import annotations

import ast
import importlib
import json
import sys
import types
from pathlib import Path
from typing import Any

import pytest

ROOT = Path(__file__).resolve().parents[1] / "universal_skills" / "research"
CRAWLER = ROOT / "web-crawler" / "scripts"
FETCH = ROOT / "web-fetch" / "scripts"
FORBIDDEN = {
    "requests",
    "httpx",
    "aiohttp",
    "urllib.request",
    "http.client",
    "playwright",
    "selenium",
    "crawl4ai",
    "bs4",
    "lxml",
    "html.parser",
    "trafilatura",
    "socket",
}


class Calls(list):
    """Recorded invokes plus the refusal the fake gateway should return."""

    def __init__(self) -> None:
        super().__init__()
        self.refuse: dict[str, str] = {}


class OperationError(Exception):
    def __init__(self, code: str) -> None:
        self.code = code
        super().__init__(code)


@pytest.fixture
def arbora(monkeypatch: pytest.MonkeyPatch) -> Calls:
    """A fake arbora.client: records each invoke and answers like the gateway."""
    calls = Calls()
    refuse = calls.refuse

    class HttpTransport:
        def __init__(self, base_url: str, token: str) -> None:
            self.base_url, self.token = base_url, token

    async def invoke(
        transport: Any, op_id: str, params: dict[str, Any]
    ) -> dict[str, Any]:
        calls.append((op_id, dict(params)))
        if refuse:
            raise OperationError(refuse["code"])
        docs = [
            {
                "document_id": f"web:{i}",
                "citations": [{"url": url, "backend": "webarchiver"}],
            }
            for i, url in enumerate(params.get("urls") or ["https://a.example/pdb"])
        ]
        return {
            "ok": True,
            "result": {"value": {"state": "complete", "documents": docs}},
        }

    client = types.ModuleType("arbora.client")
    http = types.ModuleType("arbora.client.http")
    http.HttpTransport = HttpTransport  # type: ignore[attr-defined]
    http.OperationError = OperationError  # type: ignore[attr-defined]
    inv = types.ModuleType("arbora.client.invoke")
    inv.invoke = invoke  # type: ignore[attr-defined]
    for name, module in {
        "arbora": types.ModuleType("arbora"),
        "arbora.client": client,
        "arbora.client.http": http,
        "arbora.client.invoke": inv,
    }.items():
        monkeypatch.setitem(sys.modules, name, module)
    monkeypatch.syspath_prepend(str(CRAWLER))
    monkeypatch.setenv("ARBORA_URL", "https://arbora.example")
    monkeypatch.setenv("ARBORA_TOKEN", "tok")
    monkeypatch.delitem(sys.modules, "crawl", raising=False)
    return calls


@pytest.mark.spec("US-WEB-RESEARCH-R001.1")
def test_crawl_calls_research_web(
    arbora: Calls, capsys: pytest.CaptureFixture[str]
) -> None:
    crawl = importlib.import_module("crawl")
    code = crawl.main(
        [
            "--query",
            "pod disruption budget",
            "--backend",
            "archivebox",
            "--max-pages",
            "3",
        ]
    )
    assert code == 0
    assert arbora == [
        (
            "research.web",
            {"query": "pod disruption budget", "backend": "archivebox", "max_pages": 3},
        )
    ]
    out = json.loads(capsys.readouterr().out)
    assert out["documents"][0]["document_id"] == "web:0"
    assert out["documents"][0]["citations"][0]["url"] == "https://a.example/pdb"
    crawl.main(["--urls", "https://x.example/a", "https://x.example/b"])
    assert arbora[-1] == (
        "research.web",
        {"urls": ["https://x.example/a", "https://x.example/b"]},
    )


def _imports(path: Path) -> set[str]:
    names: set[str] = set()
    for node in ast.walk(ast.parse(path.read_text())):
        if isinstance(node, ast.Import):
            names |= {alias.name for alias in node.names}
        elif isinstance(node, ast.ImportFrom) and node.module:
            names.add(node.module)
    return names


@pytest.mark.spec("US-WEB-RESEARCH-R001.2")
def test_skill_has_no_http_client() -> None:
    scripts = sorted(CRAWLER.glob("*.py")) + sorted(FETCH.glob("*.py"))
    assert [p.name for p in scripts] == ["crawl.py", "fetch.py"]
    for path in scripts:
        found = {
            name
            for name in _imports(path)
            if name in FORBIDDEN or name.split(".")[0] in FORBIDDEN
        }
        assert not found, (path.name, found)
    skill = (ROOT / "web-crawler" / "SKILL.md").read_text()
    assert "research.web" in skill and "sitemap" not in skill.lower()


@pytest.mark.spec("US-WEB-RESEARCH-R001.3")
def test_web_fetch_forwards(arbora: Calls, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.syspath_prepend(str(FETCH))
    monkeypatch.delitem(sys.modules, "fetch", raising=False)
    fetch = importlib.import_module("fetch")
    assert fetch.main(["--url", "https://a.example/page"]) == 0
    assert arbora == [
        ("research.web", {"urls": ["https://a.example/page"], "max_pages": 1})
    ]


@pytest.mark.spec("US-WEB-RESEARCH-R001.4")
def test_refusal_exits_without_fallback(
    arbora: Calls, capsys: pytest.CaptureFixture[str]
) -> None:
    arbora.refuse["code"] = "ACCESS_DENIED"
    crawl = importlib.import_module("crawl")
    assert crawl.main(["--query", "q"]) == crawl.REFUSED == 2
    assert json.loads(capsys.readouterr().err) == {"refused": "ACCESS_DENIED"}
    assert len(arbora) == 1

"""Accept negotiation preserves explicit exclusions and response metadata."""

import importlib.util
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest

TEMPLATE = (
    Path(__file__).parents[1]
    / "universal_skills/skills/mcp-builder/scripts/templates/error_rendering.py"
)


@pytest.fixture
def rendering(monkeypatch):
    spec = importlib.util.spec_from_file_location("_error_rendering_test", TEMPLATE)
    module = importlib.util.module_from_spec(spec)
    monkeypatch.setitem(sys.modules, spec.name, module)
    spec.loader.exec_module(module)
    return module


@pytest.mark.parametrize(
    ("accept", "expected"),
    [
        (None, "application/problem+json"),
        ("", "application/problem+json"),
        ("text/html,application/xhtml+xml", "text/html"),
        ("text/markdown;q=0.9,text/html;q=0.5", "text/markdown"),
        ("text/html;q=0,*/*;q=1", "application/problem+json"),
        ("application/problem+json;q=0,text/markdown;q=0.5,*/*;q=0.1", "text/markdown"),
        ("text/html;q=-1,text/markdown;q=0.5", "text/markdown"),
        ("text/html;q=2,text/markdown;q=0.5", "text/markdown"),
        ("text/html;q=nan,text/markdown;q=0.5", "text/markdown"),
        ("text/html;q=invalid", "text/html"),
        ("TEXT/HTML;Q=1", "text/html"),
        ("text/markdown;q=0,text/html;q=0", "application/problem+json"),
        ("application/xml", "application/problem+json"),
    ],
)
def test_accept_negotiation(rendering, accept, expected):
    assert rendering.negotiate_media_type(accept) == expected


@pytest.mark.parametrize(
    ("accept", "expected"),
    [
        ("application/problem+json", "json"),
        ("text/markdown", "markdown"),
        ("text/html", "html"),
    ],
)
def test_rendering_keeps_status_and_retry_metadata(rendering, accept, expected):
    problem = SimpleNamespace(
        status=503,
        retry_after_s=12.0,
        to_json=lambda: "json",
        to_markdown=lambda: "markdown",
        to_html=lambda: "html",
    )
    response = rendering.render_error(problem, accept=accept)
    assert response.status_code == 503
    assert response.body == expected
    assert response.media_type == accept
    assert response.headers == {
        "Content-Type": accept + "; charset=utf-8",
        "Vary": "Accept",
        "Retry-After": "12.0",
    }

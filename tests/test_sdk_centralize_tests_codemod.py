"""Golden-file tests for the requests -> httpx test/error rewrites (sdk_centralize_tests.py).

Fixtures are real files copied from connector repos (``*.py.fixture`` so hooks never lint them).
"""

import sys
from pathlib import Path

import pytest

SCRIPTS = Path(__file__).resolve().parents[1] / "universal_skills/agent-tools/mcp-builder/scripts"
sys.path.insert(0, str(SCRIPTS))
import sdk_centralize as sc  # noqa: E402
import sdk_centralize_tests as sct  # noqa: E402

F = Path(__file__).parent / "fixtures/sdk_centralize_tests"
BASE = "pkg.api.api_client_base"


def _run(name: str, *, test: bool, src: str | None = None):
    text = src if src is not None else (F / f"{name}.py.fixture").read_text()
    return sct.rewrite_file(text, name, is_test=test, base_dotted=BASE, place_imports=sc.import_edits)


@pytest.mark.parametrize(
    ("name", "test"),
    [("stirlingpdf_watermark", False), ("firefly_api_wrapper", True), ("wger_conftest", True)],
)
def test_rewrite_matches_golden_and_is_idempotent(name, test):
    res = _run(name, test=test)
    assert not res.blockers
    assert res.text == (F / f"{name}.after.py.fixture").read_text()
    again = _run(name, test=test, src=res.text)
    assert again.text is None and not again.blockers


def test_error_mapping_swaps_import_and_exception_classes():
    text = _run("stirlingpdf_watermark", test=False).text
    assert "import requests" not in text and "import httpx" in text
    assert "except httpx.HTTPStatusError as e:" in text and "e.response.status_code" in text


def test_session_patch_targets_the_governed_client_factory():
    text = (F / "wger_conftest.after.py.fixture").read_text()
    assert 'patch("pkg.api.api_client_base.create_http_client")' in text and "requests.Session" not in text


def test_mock_tls_profile_gets_proxy_url_none():
    text = (F / "firefly_api_wrapper.after.py.fixture").read_text()
    assert text.count("profile.proxy_url = None") == text.count("configure_requests_session.side_effect")


def test_local_variables_named_requests_are_not_bindings():
    """``self.requests`` / ``transport.requests`` / a local ``requests`` list (wger test_kg_ingest) are not the requests library."""
    res = _run("wger_kg_ingest", test=True)
    assert res.text is None and not res.blockers
    res = _run("x", test=True, src="def f():\n    requests = []\n    requests.append(1)\n    return requests\n")
    assert res.text is None and not res.blockers


def test_requests_response_fixtures_stay_exceptions():
    res = _run("audiobookshelf_api_wrapper", test=True)
    assert [c for c, _ in res.blockers] == ["tests-requests-response"] and res.text is None


def test_http_error_construction_stays_exception():
    res = _run("plane_conftest", test=True)
    assert ("tests-requests-error-construction" in {c for c, _ in res.blockers}) and res.text is None


def test_mixed_direct_requests_calls_block_error_mapping():
    res = _run("lakekeeper_auth", test=False)
    assert "catches-requests-errors-mixed" in {c for c, _ in res.blockers}


def test_from_import_forms_are_mapped():
    src = "from requests.exceptions import ConnectionError, Timeout\n\n\ndef f(c):\n    try:\n        c()\n    except (ConnectionError, Timeout):\n        return None\n"
    res = _run("x", test=False, src=src)
    assert not res.blockers
    assert "httpx.ConnectError, httpx.TimeoutException" in res.text and "from requests" not in res.text and "import httpx" in res.text


def test_response_api_without_httpx_spelling_blocks():
    src = "import requests\n\n\ndef f(c):\n    try:\n        r = c()\n        return r.ok\n    except requests.exceptions.HTTPError as e:\n        return e.response.reason\n"
    res = _run("x", test=False, src=src)
    assert "catches-requests-errors-response-api" in {c for c, _ in res.blockers}


def test_session_method_and_function_patches_block():
    src = 'from unittest.mock import patch\n\n\ndef t():\n    with patch("requests.Session.get"), patch("requests.get"):\n        pass\n'
    codes = {c for c, _ in _run("x", test=True, src=src).blockers}
    assert codes == {"tests-patch-session-method", "tests-patch-requests-function"}


def test_requests_mock_libraries_block():
    codes = {c for c, _ in _run("x", test=True, src="import requests_mock\n").blockers}
    assert "tests-requests-mock" in codes


def test_session_patch_in_other_module_blocks():
    src = 'from unittest.mock import patch\n\n\ndef t():\n    with patch("other.mod.requests.Session"):\n        pass\n'
    assert {c for c, _ in _run("x", test=True, src=src).blockers} == {"tests-patch-session-other-module"}


def test_repo_with_session_only_in_docstring_has_single_base(tmp_path):
    (tmp_path / "pkg").mkdir()
    (tmp_path / "pkg/a.py").write_text("import requests\n\n\nclass C:\n    def __init__(self):\n        self.s = requests.Session()\n")
    (tmp_path / "pkg/b.py").write_text('"""Works with a ``requests.Session`` object."""\n')
    base, cands = sc.find_base(tmp_path, [tmp_path / "pkg/a.py", tmp_path / "pkg/b.py"])
    assert base == tmp_path / "pkg/a.py" and len(cands) == 1


def test_base_url_attribute_may_be_url():
    src = (
        "import requests\n\n\nclass C:\n    def __init__(self, url: str, tls_profile=None):\n"
        "        self.url = url\n        self.tls_profile = tls_profile or resolve_tls_profile('x')\n"
        "        self.session = requests.Session()\n        self.session.headers.update({'Authorization': f'Bearer {tok}'})\n"
    )
    import ast

    plan = sc.ClientPlan(Path("."), Path("m.py"), src, ast.parse(src))
    try:
        plan.analyse()
    except sc.PatternException as e:
        assert "no-self-base-url" not in str(e)
    assert plan.url_attr == "url"

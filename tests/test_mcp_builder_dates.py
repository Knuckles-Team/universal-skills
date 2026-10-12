"""Generation dates are reproducible inputs, separate from delivery evidence."""

import importlib.util
from datetime import datetime
from pathlib import Path

import pytest

SCRIPTS = (
    Path(__file__).resolve().parents[1]
    / "universal_skills/agent-tools/mcp-builder/scripts"
)


def load_builder():
    spec = importlib.util.spec_from_file_location(
        "dated_scaffold", SCRIPTS / "scaffold_package.py"
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.mark.parametrize("source", ["explicit", "epoch"])
def test_all_generated_bytes_ignore_wall_clock_with_reproducible_date(
    tmp_path, monkeypatch, source
):
    builder = load_builder()
    import scaffold_dates

    monkeypatch.setenv("SOURCE_DATE_EPOCH", "946684800")
    options = {"generated_on": "2001-02-03"} if source == "explicit" else {}
    snapshots = []
    for year in (2026, 2042):

        class Clock(datetime):
            @classmethod
            def now(cls, tz=None, *, _year=year):
                return cls(_year, 7, 8, tzinfo=tz)

        monkeypatch.setattr(scaffold_dates, "datetime", Clock)
        parent = tmp_path / str(year)
        builder.scaffold("dated-example", output_dir=str(parent), **options)
        root = parent / "dated-example"
        snapshots.append(
            {
                path.relative_to(root).as_posix(): path.read_bytes()
                for path in root.rglob("*")
                if path.is_file()
            }
        )
    assert snapshots[0] == snapshots[1]
    expected = b"2001-02-03" if source == "explicit" else b"2000-01-01"
    assert expected in snapshots[0]["CHANGELOG.md"]
    assert b"not a release or delivery date" in snapshots[0]["CHANGELOG.md"]


@pytest.mark.parametrize("epoch", ["-1", "1.5", "invalid", "999999999999999999999999"])
def test_invalid_epoch_fails_before_output(tmp_path, monkeypatch, epoch):
    builder = load_builder()
    monkeypatch.setenv("SOURCE_DATE_EPOCH", epoch)
    with pytest.raises(ValueError, match="SOURCE_DATE_EPOCH"):
        builder.scaffold("dated-example", output_dir=str(tmp_path))
    assert not list(tmp_path.iterdir())


@pytest.mark.parametrize("value", ["2026-02-30", "20260101", "2026-W01-1"])
def test_invalid_explicit_date_fails_before_output(tmp_path, monkeypatch, value):
    builder = load_builder()
    monkeypatch.delenv("SOURCE_DATE_EPOCH", raising=False)
    with pytest.raises(ValueError):
        builder.scaffold("dated-example", output_dir=str(tmp_path), generated_on=value)
    assert not list(tmp_path.iterdir())

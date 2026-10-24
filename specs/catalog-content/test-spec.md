# US-CONTENT — Test specification

Governing spec: [spec.md](spec.md).

| Test ID | Requirement | Proving test | Expected observation |
|---|---|---|---|
| T-001 | `US-CONTENT-R001` | Every child row. | See each child. |
| T-002 | `US-CONTENT-R001.1` | `tests/test_catalog_content.py::test_declares_one_content_only_entry_point` | The test reads `pyproject.toml` and finds one entry point of the group, the bare package, the SDK floor and cap, and no provider group. |
| T-003 | `US-CONTENT-R001.2` | `tests/test_catalog_content.py::test_every_skill_is_flat_and_named_by_folder` | The test finds no `SKILL.md` outside `skills/<name>/` (other than bundled assets) and no name that differs from its folder. |
| T-004 | `US-CONTENT-R001.3` | `tests/test_catalog_content.py::test_server_lists_every_skill` | The test builds the server in process and compares the listed skill names with the folders. |

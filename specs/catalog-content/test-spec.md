# US-CONTENT — Test specification

Governing spec: [spec.md](spec.md).

| Test ID | Requirement | Proving test | Expected observation |
|---|---|---|---|
| T-001 | `US-CONTENT-R001` | Every child row. | See each child. |
| T-002 | `US-CONTENT-R001.1` | `tests/test_catalog_content.py::test_declares_one_content_only_entry_point` | The test reads `pyproject.toml` and finds one entry point of the group, the bare package, the SDK floor and cap, and no provider group. |
| T-003 | `US-CONTENT-R001.2` | `tests/test_catalog_content.py::test_every_skill_is_flat_and_named_by_folder` | The test finds no `SKILL.md` outside `skills/<name>/` (other than bundled assets) and no name that differs from its folder. |
| T-004 | `US-CONTENT-R001.3` | `tests/test_catalog_content.py::test_server_lists_every_skill` | The test builds the server in process and compares the listed skill names with the folders. |
| T-005 | `US-CONTENT-R002` | Every child row. | See each child. |
| T-006 | `US-CONTENT-R002.1` | `tests/test_upstream_sources.py::test_manifest_rejects_incomplete_sources` | The test loads the real manifest and a set of broken manifests and finds the loader accepts the first and rejects each of the others. |
| T-007 | `US-CONTENT-R002.2` | `tests/test_upstream_sources.py::test_pin_must_be_full_commit_sha` | The test loads manifests with a branch name, a tag and a short SHA and finds each rejected. |
| T-008 | `US-CONTENT-R002.3` | `tests/test_upstream_sources.py::test_license_is_required_and_kept` | The test finds the loader rejecting a source with no license and each real vendored skill holding the upstream license text. |
| T-009 | `US-CONTENT-R002.4` | `tests/test_upstream_sources.py::test_transforms_are_deterministic` | The test renders each transform twice from one input and finds identical bytes and the expected frontmatter. |
| T-010 | `US-CONTENT-R002.5` | `tests/test_upstream_sources.py::test_overlay_merge_is_ordered_and_strict` | The test applies each mode, finds the expected text and finds the ambiguous match rejected. |
| T-011 | `US-CONTENT-R002.6` | `tests/test_upstream_sources.py::test_sync_writes_provenance_without_running_code` | The test syncs from a local repository holding an executable script and finds the provenance fields, the license and no sign the script ran. |
| T-012 | `US-CONTENT-R002.7` | `tests/test_upstream_sources.py::test_check_detects_hand_edits_and_overlay_drift` | The test finds a clean tree passing, then a hand edit, an extra file and an overlay change each reported as drift. |
| T-013 | `US-CONTENT-R002.8` | `tests/test_upstream_sources.py::test_update_moves_the_pin_and_resyncs` | The test updates a local source after a new upstream commit and finds the new pin, the kept comment and the new skill text. |
| T-014 | `US-CONTENT-R002.9` | `tests/test_upstream_sources.py::test_spec_kit_skills_replace_the_retired_skills` | The test finds the eight skills in sync with their pins, the five retired folders absent and no reference left. |
| T-015 | `US-CONTENT-R002.10` | `tests/test_upstream_sources.py::test_hook_and_installer_are_wired` | The test finds the hook entry and the procedure in the installer skill. |
| T-016 | `US-CONTENT-R003` | `tests/test_code_enhancer.py::test_code_enhancer_follows_the_organization_constitution` | The test finds the limits module holding the table values, no baseline script or flag, no `.specify` output path, no retired tool or package name, no legacy concept ID, and the article reference in the skill. |
| T-017 | `US-CONTENT-R004` | Every child row. | See each child. |
| T-018 | `US-CONTENT-R004.1` | `tests/test_spec_row_delivery_skill.py::test_skill_states_the_full_delivery_procedure` | The test finds every step in order and the six report states. |
| T-019 | `US-CONTENT-R004.2` | `tests/test_spec_row_delivery_skill.py::test_frontmatter_is_portable_and_the_catalog_lists_the_skill` | The test finds the frontmatter keys, the package version and the listed skill resource. |
| T-020 | `US-CONTENT-R004.3` | `tests/test_spec_row_delivery_skill.py::test_skill_text_is_neutral_and_forbids_merge_and_skips` | The test finds the four prohibitions and no host, private domain or local path. |
| T-021 | `US-CONTENT-R005` | `tests/test_delivery_practice_links.py::test_delivery_skills_link_the_reference_and_the_articles` | The test finds the link and the four article numbers in each skill and no copied section titles. |

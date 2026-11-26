# US-CONTENT — Test specification

Governing spec: [spec.md](spec.md).

| Test ID | Requirement | Proving test | Expected observation |
|---|---|---|---|
| T-001 | `US-CONTENT-R001` | Every child row. | See each child. |
| T-002 | `US-CONTENT-R001.1` | `tests/test_catalog_content.py::test_declares_one_content_only_entry_point` | The test reads `pyproject.toml` and finds one entry point of the group, the bare package, the SDK floor and cap, and no provider group. |
| T-003 | `US-CONTENT-R001.2` | `tests/test_catalog_content.py::test_every_skill_is_flat_and_named_by_folder` | The test finds no `SKILL.md` outside `skills/<name>/` (other than bundled assets) and no name that differs from its folder. |
| T-004 | `US-CONTENT-R001.3` | `tests/test_catalog_content.py::test_server_lists_every_skill` | The test builds the server in process and compares the listed skill names with the folders. |
| T-004a | `US-CONTENT-R001.4` | `tests/test_connector_pack_attach.py::test_pack_imports_and_attaches_with_ontology_and_shapes`, `tests/test_connector_pack_attach.py::test_every_class_rolls_up_to_core` | The pack imports into a loopback no-auth engine with no `ONTOLOGY_`/`ATTACH_` code and attaches with ontology and shapes digests; every declared class reaches a core class. |
| T-004b | `US-CONTENT-R001.5` | `tests/test_connector_declaration.py::test_declares_the_content_only_profile_and_its_vendored_content`, `tests/test_connector_declaration.py::test_rendered_upstream_skills_keep_their_wording_out_of_codespell` | The profile and vendored list are exact and exist; the codespell exclusions equal the rendered upstream skill folders. |
| T-004c | `US-CONTENT-R001.6` | `tests/test_skill_authorship.py::test_first_party_skills_name_the_organization_as_author` | Every first-party skill names the organization or no author, and the generators write the organization. |
| T-004d | `US-CONTENT-R001.7` | `tests/test_shared_hooks.py::test_shared_hooks_replace_the_local_sanitizer_and_codespell` | The shared hook ids are wired, the local hooks and files are gone. |
| T-004e | `US-CONTENT-R001.8` | `tests/test_shared_hooks.py::test_every_accepted_spelling_word_occurs_in_tracked_text` | Each accepted word occurs in tracked, non-excluded text. |
| T-004f | `US-CONTENT-R001.9` | `tests/test_skill_authorship.py::test_bundled_scripts_hold_no_private_topology_account_or_model` | No private address, default account or model identifier remains in the scripts. |
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
| T-015.1 | `US-CONTENT-R002.11` | `tests/test_upstream_sources.py::test_hyperframes_skills_are_vendored_without_telemetry` | The test finds the nine skills in sync with their pin, the Apache-2.0 license in each folder, an overlay per skill and no usage-event command left in any `SKILL.md`. |
| T-016 | `US-CONTENT-R003` | `tests/test_code_enhancer.py::test_code_enhancer_follows_the_organization_constitution` | The test finds the limits module holding the table values, no baseline script or flag, no `.specify` output path, no retired tool or package name, no legacy concept ID, and the article reference in the skill. |
| T-017 | `US-CONTENT-R004` | Every child row. | See each child. |
| T-018 | `US-CONTENT-R004.1` | `tests/test_spec_row_delivery_skill.py::test_skill_states_the_full_delivery_procedure` | The test finds every step in order and the six report states. |
| T-019 | `US-CONTENT-R004.2` | `tests/test_spec_row_delivery_skill.py::test_frontmatter_is_portable_and_the_catalog_lists_the_skill` | The test finds the frontmatter keys, the package version and the listed skill resource. |
| T-020 | `US-CONTENT-R004.3` | `tests/test_spec_row_delivery_skill.py::test_skill_text_is_neutral_and_forbids_merge_and_skips` | The test finds the four prohibitions and no host, private domain or local path. |
| T-021 | `US-CONTENT-R005` | `tests/test_delivery_practice_links.py::test_delivery_skills_link_the_reference_and_the_articles` | The test finds the link and the five article numbers in each skill and no copied section titles. |
| T-022 | `US-CONTENT-R007` | Every child row. | See each child. |
| T-023 | `US-CONTENT-R007.1` | `tests/test_harness_portable_skills.py::test_every_skill_frontmatter_is_portable` | Every skill passes the strictest contract as written; the gate has no ceiling flag. (planned) |
| T-024 | `US-CONTENT-R007.2` | `tests/test_harness_portable_skills.py::test_door_skill_states_the_rules_and_is_neutral` | The test finds the six tools, the four rules in order and no host, private domain or local path. |
| T-025 | `US-CONTENT-R007.3` | `tests/test_harness_portable_skills.py::test_handoff_skill_states_the_workstream_path_first` | The workstream calls appear before the local file path. |
| T-026 | `US-CONTENT-R007.4` | `tests/test_harness_portable_skills.py::test_installer_refuses_bundle_profiles_and_writes_nothing` | Each bundle target exits 2, prints the install command and writes no file. |
| T-026.1 | `US-CONTENT-R007.4` | `tests/test_harness_portable_skills.py::test_install_removes_renamed_skills` | A full install into a directory holding old-name skills removes them, keeps current skills and keeps an old name that is a current skill. |
| T-027 | `US-CONTENT-R006` | `tests/test_codebase_untangle_skill.py::test_skill_states_the_procedure_the_categories_and_the_gates` | The test finds the seven steps in order, the categories and the gate names. |
| T-028 | `US-CONTENT-R008` | `tests/test_verify_claim_skill.py::test_skill_states_the_loop_in_order_and_is_neutral` | The test finds the six steps in order, the sorry rule and no host, domain or path. |
| T-036 | `US-CONTENT-R009` | `tests/test_skill_spec_compile.py::test_compile_journey` | A skill spec compiles into SKILL.md and test prompts (rollup) (planned) |
| T-037 | `US-CONTENT-R009.1` | `tests/test_skill_spec_compile.py::test_spec_model_refuses_unknown_keys` | Model: the skill spec (planned) |
| T-038 | `US-CONTENT-R009.2` | `tests/test_skill_spec_compile.py::test_compile_is_deterministic_and_keeps_outside_text` | Behavior: deterministic compile (planned) |
| T-039 | `US-CONTENT-R009.3` | `tests/test_skill_spec_compile.py::test_check_names_stale_skills_after_a_model_change` | Wiring: per-model recompile (planned) |
| T-040 | `US-CONTENT-R009.4` | `tests/test_skill_spec_compile.py::test_each_refusal_code_writes_nothing` | Refusal (planned) |
| T-041 | `US-CONTENT-R009.5` | `tests/test_skill_spec_compile.py::test_digest_binds_the_spec` | Evidence (planned) |
| T-042 | `US-CONTENT-R009.6` | `tests/test_skill_spec_compile.py::test_always_on_skills_compile_to_the_committed_files` | Hot-path proof (planned) |
| T-043 | `US-CONTENT-R010` | `tests/test_check_skill_steps.py::test_linter_journey` | A skill linter checks steps, verification and error recovery (rollup) (planned) |
| T-044 | `US-CONTENT-R010.1` | `tests/test_check_skill_steps.py::test_each_step_finding_has_its_code_and_line` | Behavior: steps (planned) |
| T-045 | `US-CONTENT-R010.2` | `tests/test_check_skill_steps.py::test_vague_recovery_fails_and_concrete_recovery_passes` | Behavior: error-recovery table (planned) |
| T-046 | `US-CONTENT-R010.3` | `tests/test_check_skill_steps.py::test_hook_entry_exists_and_runs_over_changed_skills` | Wiring (planned) |
| T-047 | `US-CONTENT-R010.4` | `tests/test_check_skill_steps.py::test_exit_codes_and_line_format` | Refusal and exit codes (planned) |
| T-048 | `US-CONTENT-R010.5` | `tests/test_check_skill_steps.py::test_new_knowledge_skills_pass_clean` | Hot-path proof (planned) |
| T-049 | `US-CONTENT-R011` | `tests/test_check_skill_budgets.py::test_budget_journey` | Skills load in stages and stay within size budgets (rollup) (planned) |
| T-050 | `US-CONTENT-R011.1` | `tests/test_check_skill_budgets.py::test_each_budget_code_fires_once` | Behavior: budgets (planned) |
| T-051 | `US-CONTENT-R011.2` | `tests/test_check_skill_budgets.py::test_new_keys_live_under_metadata_only` | Behavior: frontmatter keys (planned) |
| T-052 | `US-CONTENT-R011.3` | `tests/test_check_skill_budgets.py::test_mcp_json_in_a_skill_fails` | Refusal: connector files (planned) |
| T-053 | `US-CONTENT-R011.4` | `tests/test_check_skill_budgets.py::test_new_skills_are_within_budget` | Hot-path proof (planned) |
| T-054 | `US-CONTENT-R012` | `tests/test_knowledge_skills.py::test_always_on_skills_journey` | Two always-on skills let any agent flag knowledge and file friction (rollup) (planned) |
| T-055 | `US-CONTENT-R012.1` | `tests/test_knowledge_skills.py::test_flag_skill_states_the_steps_and_the_curator_rule` | Content: knowledge-flag (planned) |
| T-056 | `US-CONTENT-R012.2` | `tests/test_knowledge_skills.py::test_friction_skill_states_the_steps` | Content: skill-friction (planned) |
| T-057 | `US-CONTENT-R012.3` | `tests/test_knowledge_skills.py::test_registration_neutral_text_and_always_on_count` | Registration and neutrality (planned) |
| T-058 | `US-CONTENT-R013` | `tests/test_find_skills_skill.py::test_find_skills_journey` | A find-skills skill finds skills by quality and by peer use (rollup) (planned) |
| T-059 | `US-CONTENT-R013.1` | `tests/test_find_skills_skill.py::test_steps_in_order_and_cohort_rule` | Content (planned) |
| T-060 | `US-CONTENT-R013.2` | `tests/test_find_skills_skill.py::test_registration_and_linters` | Registration (planned) |
| T-061 | `US-CONTENT-R014` | `tests/test_curator_skill.py::test_curator_journey` | A curator skill defines the background curator agent (rollup) (planned) |
| T-062 | `US-CONTENT-R014.1` | `tests/test_curator_skill.py::test_steps_codes_and_prohibitions` | Content: procedure (planned) |
| T-063 | `US-CONTENT-R014.2` | `tests/test_curator_skill.py::test_data_access_section_names_source_query_and_columns` | Content: data-access guidance entries (planned) |
| T-064 | `US-CONTENT-R014.3` | `tests/test_curator_skill.py::test_registration_and_compile` | Registration (planned) |
| T-065 | `US-CONTENT-R015` | `tests/test_skill_eval_author_skill.py::test_eval_author_journey` | An eval-authoring skill teaches case mix, calibration and ablation (rollup) (planned) |
| T-066 | `US-CONTENT-R015.1` | `tests/test_skill_eval_author_skill.py::test_steps_band_rules_and_codes` | Content (planned) |
| T-067 | `US-CONTENT-R015.2` | `tests/test_skill_eval_author_skill.py::test_registration_and_linters` | Registration (planned) |

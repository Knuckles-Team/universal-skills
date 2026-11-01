# US-SKILL-GRAPH-BUILDER — Test specification

Governing spec: [spec.md](spec.md).

| Test ID | Requirement | Level | Setup and input | Expected observation | Evidence |
|---|---|---|---|---|---|
| T-001 | FR-001 | Unit | Every child row. | See each child. | |
| T-002 | `US-SKILL-GRAPH-BUILDER-R001.1` | Unit | `tests/test_skill_graph_builder.py::test_graph_name_gets_docs_suffix_and_is_portable` | The build receives `pandas-docs`; a long name stays within 80 characters. | |
| T-003 | `US-SKILL-GRAPH-BUILDER-R001.2` | Unit | `tests/test_skill_graph_builder.py::test_sources_are_classified_by_kind` | Kinds are `web`, `pdf`, `office`, `pdf`, `dir`. | |
| T-004 | `US-SKILL-GRAPH-BUILDER-R001.3` | Unit | `tests/test_skill_graph_builder.py::test_flatten_hashes_names_and_repoints_the_manifests` | One hash-named file; index, sources and links follow. | |
| T-005 | `US-SKILL-GRAPH-BUILDER-R001.4` | Unit | `tests/test_skill_graph_builder.py::test_output_goes_to_the_graph_collection_or_the_cache` | The target is the explicit directory, the cache, or `skill_graphs/skills`. | |
| T-006 | FR-002 | Integration | Every child row. | See each child. | |
| T-007 | `US-SKILL-GRAPH-BUILDER-R002.1` | Unit | `tests/test_skill_graph_builder.py::test_web_sources_are_fetched_by_the_web_crawler_skill` | One crawler run with the mapped flags; one `AcquiredDoc` per file. | |
| T-008 | `US-SKILL-GRAPH-BUILDER-R002.2` | Integration | `tests/test_skill_graph_builder_served.py::test_web_source_is_built_from_research_web_documents` (planned). A fixture arbora server serves `research.web`. | The graph holds one page per cited Document and the builder makes no other request. | |
| T-009 | FR-003 | Integration | Every child row. | See each child. | |
| T-010 | `US-SKILL-GRAPH-BUILDER-R003.1` | Integration | `tests/test_skill_graph_builder_pipeline.py::test_build_writes_manifest_and_graph_type` (planned). A directory source builds into a tmp folder. | The `skill-graphs` gate exits 0 on the output. | |
| T-011 | `US-SKILL-GRAPH-BUILDER-R003.2` | Integration | `tests/test_skill_graph_builder_pipeline.py::test_build_writes_core_rooted_ontology_module` (planned). | The module has no orphan class and no `owl:imports`. | |
| T-012 | FR-004 | Contract | Every child row. | See each child. | |
| T-013 | `US-SKILL-GRAPH-BUILDER-R004.1` | Contract | `tests/test_skill_graph_builder_pipeline.py::test_builder_imports_no_retired_package` (planned). | No file imports `agent_utilities`. | |
| T-014 | `US-SKILL-GRAPH-BUILDER-R004.2` | Contract | `tests/test_skill_graph_builder_pipeline.py::test_retired_flags_are_refused` (planned). | `--no-kg`, `--ingest-kg` and `--append` exit with a usage error. | |

## Negative and boundary cases

An unknown flag exits non-zero. A name above 80 characters is shortened with a digest. A hash collision lengthens the prefix.

## Quality and release proof

Focused: `uv run --all-extras pytest tests/test_skill_graph_builder.py -q`. Gates: `pre-commit run --all-files`.

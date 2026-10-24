# Verified generated-schema clone policy

The scaffold enables no generated-file exemption by default. A repository needs
specific human approval for a narrow artifact policy before changing its clone
hooks. A passing source inventory is not permission to exclude files.

For an approved policy, reuse `scripts/templates/generated_schema_clones.py` as
`scripts/generated_schema_clones.py`; do not maintain another scanner algorithm.
Its provider-owned `scripts/verify_generated_schemas.py` declares `MANIFEST` and
`load_policy(root)`, validates an exact path allowlist and SHA256 map, then runs
with `--root` to regenerate artifacts and verify native schema freshness offline.
A successful verifier emits only `{"version": 1, "verified_artifacts": {...}}`.
Hashes without deterministic regeneration do not establish admission.

The wrapper uses shared Pipelines base resolution, merge-tree snapshots, scanner
settings and pair keys. It scans the complete tree and excludes a pair only when
**both** members are verified artifacts. Handwritten-to-generated pairs remain.
Every file and mode must remain unchanged while the exact-tree verifier runs;
links, special files, changed receipts and unavailable inputs fail closed.
Historical trees without the manifest get no exclusions. Full statistics, hashes
and excluded-pair counts remain visible. Census remains advisory; differential
fails for new retained pairs.

Set `GENERATED_SCHEMA_PYTHON` to the existing reviewed project interpreter if its
`.venv/bin/python` is not appropriate. Keep provider source captures and compiler
identities explicit, immutable and available to both historical and merged-tree
verification. Change only the two approved clone entries to invoke this wrapper
inside the shared Pipelines hook environment. Do not change thresholds, use globs,
add unrelated artifacts, or silently bypass missing inputs. Review and test
negative cases before accepting a consumer policy.

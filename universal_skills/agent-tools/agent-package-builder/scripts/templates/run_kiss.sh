#!/usr/bin/env bash
# Run the generated package's pinned KISS policy over changed Python files.
#
# This wrapper is deliberately shell-only so it remains usable before the
# package environment is installed.  It never invokes cargo/pip/npm, never
# lets kiss create its auto-calibrated .kissconfig, and never passes more than
# one path to `kiss check` (kiss 0.4.10 silently reports a false green for
# multi-path checks).
set -uo pipefail

ROOT=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd) || exit 2
cd "$ROOT" || exit 2

die() {
  echo "kiss gate: CANNOT RUN: $*" >&2
  exit 2
}

RUN_MODE="${1:-changed}"
case "$RUN_MODE" in
  changed|--census) ;;
  *) die "unknown mode '$RUN_MODE' (expected changed or --census)" ;;
esac

[ -f "$ROOT/.kiss/kiss.toml" ] || die \
  "missing .kiss/kiss.toml; refusing unconfigured defaults"
[ ! -e "$ROOT/.kissconfig" ] || die \
  ".kissconfig exists; delete it because kiss auto-calibrates and disables rules"

# The index is the commit's source of truth.  The fallback lets an operator
# run the wrapper manually against unstaged files without weakening the hook:
# the generated pre-commit hook itself always stages before invoking us.
CHANGED=""
if [ "$RUN_MODE" = "changed" ]; then
  CHANGED=$(git diff --cached --name-only --diff-filter=ACMRD 2>/dev/null) || \
    die "cannot enumerate staged paths"
  if [ -z "$CHANGED" ]; then
    CHANGED=$(git diff --name-only --diff-filter=ACMRD HEAD 2>/dev/null) || \
      die "cannot enumerate working-tree paths"
    untracked=$(git ls-files --others --exclude-standard 2>/dev/null) || \
      die "cannot enumerate untracked paths"
    if [ -n "$untracked" ]; then
      CHANGED=$(printf '%s\n%s\n' "$CHANGED" "$untracked")
    fi
  fi
fi

# A policy-only change must not bypass validation merely because no Python
# source is staged. `check-toml` catches syntax, but KISS otherwise warns about
# unknown keys and silently falls back to upstream defaults. Parse the policy
# with the same stdlib parser used by the dispatcher and fail closed here so a
# changed `.kiss/kiss.toml` is reviewed before any source gate is skipped.
python3 - "$ROOT/.kiss/kiss.toml" <<'PY' || die "invalid KISS policy TOML"
import math
import sys
import tomllib

with open(sys.argv[1], "rb") as handle:
    policy = tomllib.load(handle)
if not isinstance(policy.get("global"), dict) or not isinstance(
    policy.get("python"), dict
):
    raise SystemExit("policy requires [global] and [python] tables")
allowed = {
    "global": {
        "min_similarity",
        "duplication_enabled",
        "orphan_module_enabled",
        "comment_removal_enabled",
        "docs_allowed",
        "orphan_allowed",
    },
    "python": {
        "max_indentation",
        "nested_function_depth",
        "return_values_per_function",
        "decorators_per_function",
        "boolean_parameters",
        "statements_per_try_block",
        "returns_per_function",
        "positional_args",
        "statements_per_function",
        "local_variables",
        "calls_per_function",
        "methods_per_class",
        "imported_names_per_file",
        "statements_per_file",
        "lines_per_file",
        "functions_per_file",
        "interface_types_per_file",
        "branches_per_function",
        "keyword_only_args",
        "concrete_types_per_file",
        "cycle_size",
        "dependency_depth",
        "indirect_dependencies",
    },
}
required = {
    "global": set(allowed["global"]),
    "python": set(allowed["python"]),
}
unknown_sections = set(policy) - set(allowed)
unknown_keys = {
    section: set(values) - allowed[section]
    for section, values in policy.items()
    if section in allowed and isinstance(values, dict)
}
unknown_keys = {section: keys for section, keys in unknown_keys.items() if keys}
missing_keys = {
    section: required[section] - set(policy[section])
    for section in required
    if required[section] - set(policy[section])
}
if unknown_sections or unknown_keys or missing_keys:
    details = ", ".join(
        f"{section}={sorted(keys)}" for section, keys in unknown_keys.items()
    )
    raise SystemExit(
        f"unknown policy entries: sections={sorted(unknown_sections)}, "
        f"keys={details}, missing={missing_keys}"
    )

global_policy = policy["global"]
python_policy = policy["python"]
for key in (
    "duplication_enabled",
    "orphan_module_enabled",
    "comment_removal_enabled",
):
    if not isinstance(global_policy[key], bool):
        raise SystemExit(f"global.{key} must be a boolean")
similarity = global_policy["min_similarity"]
if (
    isinstance(similarity, bool)
    or not isinstance(similarity, (int, float))
    or not math.isfinite(float(similarity))
    or not 0.0 <= float(similarity) <= 1.0
):
    raise SystemExit("global.min_similarity must be a finite number in [0, 1]")
for key in ("docs_allowed", "orphan_allowed"):
    values = global_policy[key]
    if not isinstance(values, list) or any(
        not isinstance(value, str) or not value.strip() for value in values
    ):
        raise SystemExit(f"global.{key} must be a list of non-empty strings")
for key, value in python_policy.items():
    if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
        raise SystemExit(f"python.{key} must be a positive integer")
PY

# Do not make an unrelated documentation-only commit depend on a source
# scanner binary. Once a Python source file is applicable, missing or drifted
# kiss is still a hard error below (the gate never reports an unrun check as
# clean).
has_python=0
while IFS= read -r path; do
  [ -n "$path" ] || continue
  case "$path" in
    *.py|*.pyi) ;;
    *) continue ;;
  esac
  case "$path" in
    scripts/check_scanners.py|*/scripts/check_scanners.py) continue ;;
  esac
  [ -f "$ROOT/$path" ] || continue
  case "/$path/" in
    */.git/*|*/.venv/*|*/venv/*|*/node_modules/*|*/.cache/*|*/vendor/*|\
    */third_party/*|*/generated/*|*/__generated__/*|*/codegen/*|\
    */openapi_client/*|*/graphql_client/*|*/fixtures/*|*/fixture/*|\
    */samples/*|*/sample/*|*/examples/*|*/target/*|*/target-isolated/*|\
    */dist/*|*/dist-primary/*|*/dist-reproduction/*|*/build/*|\
    */build-artifacts/*|*/coverage/*|*/htmlcov/*|*/__pycache__/*|\
    */.mypy_cache/*|*/.pytest_cache/*|*/.pytest_tmp/*|*/.ruff_cache/*|\
    */.hypothesis/*|*/.tox/*|*/.eggs/*|*/site-packages/*) continue ;;
  esac
  has_python=1
  break
done <<<"$CHANGED"

if [ "$RUN_MODE" = "changed" ] && [ "$has_python" -eq 0 ]; then
  echo "kiss gate: no changed Python source files"
  exit 0
fi

if [ -n "${KISS_BIN:-}" ]; then
  KISS=$KISS_BIN
  case "$KISS" in
    */*)
      [ -f "$KISS" ] && [ -x "$KISS" ] || die \
        "KISS_BIN points to a missing or non-executable scanner: '$KISS_BIN'"
      ;;
    *)
      command -v "$KISS" >/dev/null 2>&1 || die \
        "KISS_BIN '$KISS_BIN' is not installed"
      ;;
  esac
else
  KISS=$(command -v kiss) || die \
    "kiss is not installed. Provision the reviewed kiss toolchain; hooks never install it"
fi

EXPECTED=$(python3 - "$ROOT/pyproject.toml" <<'PY'
import sys
import tomllib

with open(sys.argv[1], "rb") as handle:
    table = tomllib.load(handle)["tool"]["agent_utilities"]["scanners"]
version = table["kiss_version"]
if (
    not isinstance(version, str)
    or len(version.split(".")) != 3
    or any(not part.isdigit() for part in version.split("."))
):
    raise SystemExit("kiss_version is not a string")
print(f"kiss {version}")
PY
) || die "could not read kiss_version from pyproject.toml"
GOT=$("$KISS" --version 2>/dev/null) || die "kiss --version failed"
[ "$GOT" = "$EXPECTED" ] || die \
  "version drift: want '$EXPECTED', got '$GOT'"

if [ "$RUN_MODE" = "--census" ]; then
  output=$("$KISS" check --config "$ROOT/.kiss/kiss.toml" --lang python "$ROOT" 2>&1)
  status=$?
  count=$(grep -c '^VIOLATION:' <<<"$output" || true)
  if [ "$status" -gt 1 ]; then
    printf '%s\n' "$output" >&2
    die "kiss census failed with exit $status"
  fi
  if [ "$status" -eq 1 ] && [ "$count" -eq 0 ]; then
    printf '%s\n' "$output" >&2
    die "kiss census exited 1 without reporting a violation"
  fi
  printf '%s\n' "$output"
  [ "$count" -eq 0 ]
  exit $?
fi

total=0
failures=0
while IFS= read -r path; do
  [ -n "$path" ] || continue
  case "$path" in
    *.py|*.pyi) ;;
    *) continue ;;
  esac
  case "$path" in
    scripts/check_scanners.py|*/scripts/check_scanners.py) continue ;;
  esac
  [ -f "$ROOT/$path" ] || continue
  case "/$path/" in
    */.git/*|*/.venv/*|*/venv/*|*/node_modules/*|*/.cache/*|*/vendor/*|\
    */third_party/*|*/generated/*|*/__generated__/*|*/codegen/*|\
    */openapi_client/*|*/graphql_client/*|*/fixtures/*|*/fixture/*|\
    */samples/*|*/sample/*|*/examples/*|*/target/*|*/target-isolated/*|\
    */dist/*|*/dist-primary/*|*/dist-reproduction/*|*/build/*|\
    */build-artifacts/*|*/coverage/*|*/htmlcov/*|*/__pycache__/*|\
    */.mypy_cache/*|*/.pytest_cache/*|*/.pytest_tmp/*|*/.ruff_cache/*|\
    */.hypothesis/*|*/.tox/*|*/.eggs/*|*/site-packages/*) continue ;;
  esac

  total=$((total + 1))
  output=$("$KISS" check --config "$ROOT/.kiss/kiss.toml" --lang python "$path" 2>&1)
  status=$?
  if grep -q "Unknown config key" <<<"$output"; then
    printf '%s\n' "$output" >&2
    die "kiss rejected the checked-in policy and fell back to upstream defaults"
  fi
  if [ "$status" -gt 1 ]; then
    printf '%s\n' "$output" >&2
    die "kiss failed for $path with exit $status"
  fi
  count=$(grep -c '^VIOLATION:' <<<"$output" || true)
  printf 'kiss [%s]: %s violation(s)\n' "$path" "$count"
  if [ "$status" -eq 1 ] && [ "$count" -eq 0 ]; then
    printf '%s\n' "$output" >&2
    die "kiss exited 1 without reporting a violation for $path"
  fi
  if [ "$count" -gt 0 ]; then
    printf '%s\n' "$output" | grep '^VIOLATION:' || true
    failures=$((failures + count))
  fi
done <<<"$CHANGED"

if [ "$total" -eq 0 ]; then
  echo "kiss gate: no changed Python source files"
  exit 0
fi
printf 'kiss gate: %s violation(s) across %s changed file(s)\n' "$failures" "$total"
[ "$failures" -eq 0 ]

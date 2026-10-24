#!/usr/bin/env bash
set -uo pipefail

P1="${1:-${CA_TARGET_PROJECT:-}}"
P2="${2:-${CA_SOURCE_PROJECT:-}}"
RESULTS_DIR="${CA_RESULTS_DIR:-results}"
REPORT_OUTPUT="${CA_REPORT_OUTPUT:-${RESULTS_DIR}/comparative_analysis.md}"

if [ -z "$P1" ] || [ -z "$P2" ]; then
  echo "usage: run_analysis.sh <target-project> <source-project>" >&2
  exit 2
fi
mkdir -p "$RESULTS_DIR"

for path in "$P1" "$P2"; do
  name=$(basename "$path")
  echo "Analyzing configured project..."
  python scripts/analyze_governance.py "$path" > "${RESULTS_DIR}/${name}_ca001.json"
  python scripts/analyze_ecosystem_health.py "$path" > "${RESULTS_DIR}/${name}_ca002.json"
  python scripts/analyze_architecture.py "$path" > "${RESULTS_DIR}/${name}_ca003.json"
  python scripts/analyze_code_quality.py "$path" > "${RESULTS_DIR}/${name}_ca004.json"
  python scripts/analyze_security.py "$path" > "${RESULTS_DIR}/${name}_ca005.json"
  python scripts/analyze_testing.py "$path" > "${RESULTS_DIR}/${name}_ca006.json"
  python scripts/analyze_documentation.py "$path" > "${RESULTS_DIR}/${name}_ca007.json"
  python scripts/analyze_performance.py "$path" > "${RESULTS_DIR}/${name}_ca008.json"
done

echo "Running innovation extraction..."
python scripts/extract_innovations.py --source "$P2" --target "$P1" > "${RESULTS_DIR}/innovation_ca009.json"

echo "Generating comparison report..."
python scripts/generate_comparison_report.py "${RESULTS_DIR}"/*.json --output "$REPORT_OUTPUT"

echo "Done"

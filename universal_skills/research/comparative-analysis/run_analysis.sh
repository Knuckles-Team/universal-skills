#!/bin/bash
P1="/home/apps/workspace/agent-packages/agent-utilities"
P2="/home/apps/workspace/agent-packages/skills/universal-skills/universal_skills/research/comparative-analysis/.specify/ca_repos/20afe9f9/agentmemory"

for path in "$P1" "$P2"; do
  name=$(basename "$path")
  echo "Analyzing $name..."
  python scripts/analyze_governance.py "$path" > "results/${name}_ca001.json"
  python scripts/analyze_ecosystem_health.py "$path" > "results/${name}_ca002.json"
  python scripts/analyze_architecture.py "$path" > "results/${name}_ca003.json"
  python scripts/analyze_code_quality.py "$path" > "results/${name}_ca004.json"
  python scripts/analyze_security.py "$path" > "results/${name}_ca005.json"
  python scripts/analyze_testing.py "$path" > "results/${name}_ca006.json"
  python scripts/analyze_documentation.py "$path" > "results/${name}_ca007.json"
  python scripts/analyze_performance.py "$path" > "results/${name}_ca008.json"
done

echo "Running innovation extraction..."
python scripts/extract_innovations.py --source "$P2" --target "$P1" > "results/innovation_ca009.json"

echo "Generating comparison report..."
python scripts/generate_comparison_report.py results/*.json --output "$P1/.specify/reports/comparative_analysis.md"

echo "Done"

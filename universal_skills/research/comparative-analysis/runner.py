import subprocess
import sys

P1 = "/home/apps/workspace/agent-packages/agent-utilities"
P2 = "/home/apps/workspace/agent-packages/skills/universal-skills/universal_skills/research/comparative-analysis/.specify/ca_repos/20afe9f9/agentmemory"
paths = {"agent-utilities": P1, "agentmemory": P2}

for name, path in paths.items():
    print(f"Running for {name}...")
    for i in range(1, 9):
        script = {
            1: "analyze_governance.py",
            2: "analyze_ecosystem_health.py",
            3: "analyze_architecture.py",
            4: "analyze_code_quality.py",
            5: "analyze_security.py",
            6: "analyze_testing.py",
            7: "analyze_documentation.py",
            8: "analyze_performance.py",
        }[i]
        try:
            out = subprocess.check_output(  # noqa: S603
                [sys.executable, f"scripts/{script}", path], text=True
            )
            with open(f"results/{name}_ca00{i}.json", "w") as f:
                f.write(out)
        except Exception as e:
            print(f"Error in {script} for {name}: {e}")

print("Running innovation extraction...")
try:
    out = subprocess.check_output(  # noqa: S603
        [
            sys.executable,
            "scripts/extract_innovations.py",
            "--source",
            P2,
            "--target",
            P1,
        ],
        text=True,
    )
    with open("results/innovation_ca009.json", "w") as f:
        f.write(out)
except Exception as e:
    print(f"Error in extract_innovations.py: {e}")

print("Running generation...")
subprocess.run(  # noqa: S603
    [
        sys.executable,
        "scripts/generate_comparison_report.py",
        "results/agent-utilities_ca001.json",
        "results/agent-utilities_ca002.json",
        "results/agent-utilities_ca003.json",
        "results/agent-utilities_ca004.json",
        "results/agent-utilities_ca005.json",
        "results/agent-utilities_ca006.json",
        "results/agent-utilities_ca007.json",
        "results/agent-utilities_ca008.json",
        "results/agentmemory_ca001.json",
        "results/agentmemory_ca002.json",
        "results/agentmemory_ca003.json",
        "results/agentmemory_ca004.json",
        "results/agentmemory_ca005.json",
        "results/agentmemory_ca006.json",
        "results/agentmemory_ca007.json",
        "results/agentmemory_ca008.json",
        "results/innovation_ca009.json",
        "--output",
        f"{P1}/.specify/reports/comparative_analysis.md",
    ]
)

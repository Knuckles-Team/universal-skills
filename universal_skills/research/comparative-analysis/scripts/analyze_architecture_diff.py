#!/usr/bin/env python3
"""CA-003b: Architecture differential analysis between two codebases.

Usage:
    python analyze_architecture_diff.py /path/to/source /path/to/target

Compares the architectural structure of two projects and identifies:
- Component topology gaps (what source has that target doesn't)
- Hot path differences (entry point and reachability divergence)
- Design pattern divergence (different implementation strategies)
- Wiring opportunities (where target could integrate source innovations)

CONCEPT:CA-003b — Architecture Differential Analysis
"""

import json
import sys
from pathlib import Path

# Add scripts directory to path for sibling imports
sys.path.insert(0, str(Path(__file__).parent))
from analyze_architecture import (  # noqa: E402
    analyze_design_patterns,
    analyze_module_structure,
    detect_protocols,
    discover_c4_architecture,
    identify_hot_paths,
)


def diff_components(source_c4: dict, target_c4: dict) -> dict:
    """Compare C4 component topologies between source and target."""
    source_components = set()
    target_components = set()

    for diagram in source_c4.get("diagrams", []):
        for comp in diagram.get("components", []):
            source_components.add(comp["name"])

    for diagram in target_c4.get("diagrams", []):
        for comp in diagram.get("components", []):
            target_components.add(comp["name"])

    in_source_only = sorted(source_components - target_components)
    in_target_only = sorted(target_components - source_components)
    shared = sorted(source_components & target_components)

    return {
        "source_only": in_source_only,
        "target_only": in_target_only,
        "shared": shared,
        "source_count": len(source_components),
        "target_count": len(target_components),
        "gap_count": len(in_source_only),
    }


def diff_hot_paths(source_hp: dict, target_hp: dict) -> dict:
    """Compare hot path coverage and entry point types."""
    source_ep_types = {ep["type"] for ep in source_hp.get("entry_points", [])}
    target_ep_types = {ep["type"] for ep in target_hp.get("entry_points", [])}

    return {
        "source_entry_types": sorted(source_ep_types),
        "target_entry_types": sorted(target_ep_types),
        "missing_entry_types": sorted(source_ep_types - target_ep_types),
        "source_coverage_pct": source_hp.get("hot_path_coverage_pct", 0),
        "target_coverage_pct": target_hp.get("hot_path_coverage_pct", 0),
        "coverage_delta": round(
            source_hp.get("hot_path_coverage_pct", 0)
            - target_hp.get("hot_path_coverage_pct", 0),
            1,
        ),
        "target_cold_modules": target_hp.get("cold_modules", [])[:10],
    }


def diff_design_patterns(source_dp: dict, target_dp: dict) -> dict:
    """Compare design pattern usage between source and target."""
    source_counts = source_dp.get("counts", {})
    target_counts = target_dp.get("counts", {})
    all_patterns = set(source_counts) | set(target_counts)

    diffs = {}
    for pattern in sorted(all_patterns):
        s = source_counts.get(pattern, 0)
        t = target_counts.get(pattern, 0)
        if s != t:
            diffs[pattern] = {
                "source": s,
                "target": t,
                "delta": s - t,
                "recommendation": (
                    f"Target could adopt {pattern} pattern (source uses {s}x)"
                    if s > t
                    else f"Target already uses {pattern} more than source"
                ),
            }
    return {"pattern_diffs": diffs, "divergence_count": len(diffs)}


def diff_protocols(source_proto: dict, target_proto: dict) -> dict:
    """Compare protocol support between source and target."""
    source_set = set(source_proto.keys())
    target_set = set(target_proto.keys())
    return {
        "source_only": sorted(source_set - target_set),
        "target_only": sorted(target_set - source_set),
        "shared": sorted(source_set & target_set),
        "gap_count": len(source_set - target_set),
    }


def identify_wiring_opportunities(
    component_diff: dict,
    hot_path_diff: dict,
    pattern_diff: dict,
    target_hp: dict,
) -> list[dict]:
    """Synthesize actionable wiring recommendations."""
    opportunities = []

    # Components in source but not target
    for comp in component_diff.get("source_only", []):
        opportunities.append({
            "type": "component_gap",
            "component": comp,
            "action": f"Add '{comp}' component to target architecture",
            "priority": "high",
            "wiring_hint": "Wire into existing hot path via the nearest entry point",
        })

    # Missing entry point types
    for ep_type in hot_path_diff.get("missing_entry_types", []):
        opportunities.append({
            "type": "entry_point_gap",
            "entry_type": ep_type,
            "action": f"Add {ep_type} entry point to target",
            "priority": "medium",
            "wiring_hint": "Create handler that delegates to existing engine methods",
        })

    # Cold modules that could be wired in
    for cold_mod in target_hp.get("cold_modules", [])[:5]:
        opportunities.append({
            "type": "cold_code",
            "module": cold_mod,
            "action": f"Wire '{cold_mod}' into hot path or remove if dead code",
            "priority": "low",
            "wiring_hint": "Import from nearest hot-path module or add entry point",
        })

    # Design patterns to adopt
    for pattern, diff in pattern_diff.get("pattern_diffs", {}).items():
        if diff["delta"] > 0:
            opportunities.append({
                "type": "design_pattern",
                "pattern": pattern,
                "action": f"Consider adopting {pattern} pattern ({diff['source']}x in source)",
                "priority": "medium",
                "wiring_hint": f"Source examples: see analyze_design_patterns output",
            })

    return sorted(opportunities, key=lambda x: {"high": 0, "medium": 1, "low": 2}[x["priority"]])


def main():
    if len(sys.argv) < 3:
        print(json.dumps({
            "error": "Usage: analyze_architecture_diff.py <source_path> <target_path>"
        }))
        sys.exit(1)

    source_path = Path(sys.argv[1]).resolve()
    target_path = Path(sys.argv[2]).resolve()

    # Run architecture analysis on both
    source_c4 = discover_c4_architecture(source_path)
    target_c4 = discover_c4_architecture(target_path)
    source_hp = identify_hot_paths(source_path)
    target_hp = identify_hot_paths(target_path)
    source_dp = analyze_design_patterns(source_path)
    target_dp = analyze_design_patterns(target_path)
    source_proto = detect_protocols(source_path)
    target_proto = detect_protocols(target_path)

    # Compute diffs
    component_diff = diff_components(source_c4, target_c4)
    hot_path_diff = diff_hot_paths(source_hp, target_hp)
    pattern_diff = diff_design_patterns(source_dp, target_dp)
    protocol_diff = diff_protocols(source_proto, target_proto)

    # Synthesize wiring opportunities
    wiring = identify_wiring_opportunities(
        component_diff, hot_path_diff, pattern_diff, target_hp
    )

    print(json.dumps({
        "domain": "CA-003b",
        "domain_name": "Architecture Differential",
        "source": str(source_path),
        "target": str(target_path),
        "component_topology_diff": component_diff,
        "hot_path_diff": hot_path_diff,
        "design_pattern_diff": pattern_diff,
        "protocol_diff": protocol_diff,
        "wiring_opportunities": wiring,
        "wiring_opportunity_count": len(wiring),
        "summary": {
            "component_gaps": component_diff["gap_count"],
            "missing_entry_types": len(hot_path_diff.get("missing_entry_types", [])),
            "pattern_divergences": pattern_diff["divergence_count"],
            "protocol_gaps": protocol_diff["gap_count"],
            "total_opportunities": len(wiring),
        },
    }, indent=2))


if __name__ == "__main__":
    main()

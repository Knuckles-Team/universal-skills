"""Tests for the deployment-planner Kubernetes manifest emitter."""

from __future__ import annotations

import importlib.util
from pathlib import Path

_MOD = (
    Path(__file__).resolve().parents[1]
    / "universal_skills/infrastructure/deployment-planner/scripts/emit_manifests.py"
)
_spec = importlib.util.spec_from_file_location("emit_manifests", _MOD)
emit_manifests = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(emit_manifests)


def _blueprint():
    return {
        "cluster": {"name": "homelab"},
        "k8s": {"namespace": "homelab", "storageClass": "local-path"},
        "placements": [
            # T0 edge with published ports -> Deployment + Service
            {
                "service": "caddy",
                "tier": "T0",
                "node": "R820",
                "image": "registry.arpa/caddy:cloudflare",
                "ports": ["80:80", "443:443"],
            },
            # DB with volumes -> StatefulSet + volumeClaimTemplates
            {
                "service": "pg-age",
                "tier": "T1",
                "node": "R820",
                "image": "registry.arpa/pg-age:latest",
                "volumes": ["/home/apps/pg-age/data:/var/lib/postgresql/data"],
            },
            # observability marked global -> DaemonSet
            {
                "service": "node-exporter",
                "tier": "T1",
                "node": "R710",
                "mode": "global",
            },
            # plain stateless MCP -> Deployment
            {"service": "gitlab-mcp", "tier": "T5", "node": "RW710"},
        ],
    }


def _by_kind(manifests):
    out: dict[str, list] = {}
    for m in manifests:
        out.setdefault(m["kind"], []).append(m)
    return out


def test_emit_kubernetes_kinds():
    manifests = emit_manifests.emit(_blueprint(), "kubernetes", "default")
    kinds = _by_kind(manifests)
    assert "Namespace" in kinds
    names = {(m["kind"], m["metadata"]["name"]) for m in manifests}
    assert ("Deployment", "caddy") in names
    assert ("StatefulSet", "pg-age") in names
    assert ("DaemonSet", "node-exporter") in names
    assert ("Deployment", "gitlab-mcp") in names
    assert ("Service", "caddy") in names


def test_namespace_from_blueprint_k8s_block():
    manifests = emit_manifests.emit(_blueprint(), "kubernetes", "default")
    ns = [m for m in manifests if m["kind"] == "Namespace"][0]
    assert ns["metadata"]["name"] == "homelab"
    # all workloads land in that namespace
    for m in manifests:
        if m["kind"] in ("Deployment", "StatefulSet", "Service"):
            assert m["metadata"]["namespace"] == "homelab"


def test_node_affinity_pins_to_node_label():
    manifests = emit_manifests.emit(_blueprint(), "kubernetes", "default")
    caddy = [
        m
        for m in manifests
        if m["kind"] == "Deployment" and m["metadata"]["name"] == "caddy"
    ][0]
    affinity = caddy["spec"]["template"]["spec"]["affinity"]["nodeAffinity"]
    term = affinity["requiredDuringSchedulingIgnoredDuringExecution"][
        "nodeSelectorTerms"
    ][0]["matchExpressions"][0]
    assert term == {"key": "name", "operator": "In", "values": ["R820"]}


def test_statefulset_uses_volume_claim_templates():
    manifests = emit_manifests.emit(_blueprint(), "kubernetes", "default")
    sts = [m for m in manifests if m["kind"] == "StatefulSet"][0]
    vcts = sts["spec"]["volumeClaimTemplates"]
    assert vcts[0]["spec"]["storageClassName"] == "local-path"
    mounts = sts["spec"]["template"]["spec"]["containers"][0]["volumeMounts"]
    assert mounts[0]["mountPath"] == "/var/lib/postgresql/data"
    assert sts["spec"]["serviceName"] == "pg-age"


def test_service_maps_published_ports():
    manifests = emit_manifests.emit(_blueprint(), "kubernetes", "default")
    svc = [m for m in manifests if m["kind"] == "Service"][0]
    ports = {p["port"]: p["targetPort"] for p in svc["spec"]["ports"]}
    assert ports == {80: 80, 443: 443}


def test_select_kind_rules():
    assert emit_manifests.select_kind({"mode": "global"}) == "DaemonSet"
    assert emit_manifests.select_kind({"volumes": ["a:b"]}) == "StatefulSet"
    assert emit_manifests.select_kind({"tier": "T6"}) == "StatefulSet"
    assert emit_manifests.select_kind({"tier": "T5"}) == "Deployment"


def test_swarm_target_passes_blueprint_through():
    bp = _blueprint()
    out = emit_manifests.emit(bp, "swarm", "default")
    assert out == [bp]


def test_all_manifests_are_yaml_serializable():
    import yaml

    manifests = emit_manifests.emit(_blueprint(), "kubernetes", "default")
    dumped = yaml.safe_dump_all(manifests)
    reloaded = list(yaml.safe_load_all(dumped))
    assert len(reloaded) == len(manifests)

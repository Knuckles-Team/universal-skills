#!/usr/bin/env python
"""Emit deployment manifests from a deployment-planner blueprint.

The placement scoring (SKILL.md Steps 1-6) is orchestrator-agnostic; only the
Step 7 rendering differs by target. This script turns a ``golden-deployment``
blueprint into either the existing Swarm blueprint (passthrough) or a directory
of Kubernetes manifests (Deployment/StatefulSet/DaemonSet + nodeAffinity + PVCs
+ Service) from deployment-owned inputs.

The blueprint's ``placements`` carry the placement decision (service, tier,
node) and may be enriched from the Step 2 service catalog with ``image``,
``replicas``, ``ports``, ``volumes``, ``mode`` and ``env`` — when present those
drive the generated manifest; otherwise sensible placeholders are emitted.

Usage:
    emit_manifests.py --blueprint golden-deployment.yaml --target kubernetes --out k8s/
    emit_manifests.py --blueprint golden-deployment.yaml --target kubernetes   # stdout
"""

from __future__ import annotations

import argparse
import sys
from typing import Any

import yaml

# Tiers whose data must survive a reschedule -> StatefulSet even without an
# explicit volume list (T2 business apps, T6 media/NAS-bound).
_STATEFUL_TIERS = {"T2", "T6"}


def node_affinity(
    node: str, label_key: str = "kubernetes.io/hostname"
) -> dict[str, Any]:
    """Pin a pod with the deployment-configured node identity label."""
    return {
        "nodeAffinity": {
            "requiredDuringSchedulingIgnoredDuringExecution": {
                "nodeSelectorTerms": [
                    {
                        "matchExpressions": [
                            {"key": label_key, "operator": "In", "values": [node]}
                        ]
                    }
                ]
            }
        }
    }


def _parse_ports(ports: Any) -> list[tuple[int, int]]:
    """Normalize ports into ``[(published, target), ...]``.

    Accepts ``["8080:80", "53"]`` or ``{"80": "8080"}`` (target: published,
    the container-manager convention).
    """
    out: list[tuple[int, int]] = []
    if isinstance(ports, dict):
        for target, published in ports.items():
            out.append(
                (int(str(published).split("/")[0]), int(str(target).split("/")[0]))
            )
    elif isinstance(ports, list):
        for p in ports:
            parts = str(p).split(":")
            if len(parts) == 2:
                out.append((int(parts[0]), int(parts[1].split("/")[0])))
            else:
                port = int(parts[0].split("/")[0])
                out.append((port, port))
    return out


def select_kind(placement: dict[str, Any]) -> str:
    """Choose the workload kind for a placement."""
    if placement.get("mode") == "global":
        return "DaemonSet"
    if placement.get("volumes") or placement.get("tier") in _STATEFUL_TIERS:
        return "StatefulSet"
    return "Deployment"


def _pvcs_and_volumes(
    name: str, volumes: list[str], namespace: str, storage_class: str | None
) -> tuple[list[dict], list[dict], list[dict]]:
    """Build PVCs + pod volumes + volumeMounts from ``source:target`` strings.

    Volumes back onto the node-local ``local-path`` StorageClass (RKE2/k3s
    default); node affinity keeps the PVC's pod on the data's node.
    """
    pvcs: list[dict] = []
    pod_volumes: list[dict] = []
    mounts: list[dict] = []
    for idx, raw in enumerate(volumes or []):
        parts = str(raw).split(":")
        if len(parts) < 2:
            continue
        target = parts[1]
        claim = f"{name}-data{idx}" if idx else f"{name}-data"
        claim_spec: dict[str, Any] = {
            "accessModes": ["ReadWriteOnce"],
            "resources": {"requests": {"storage": "10Gi"}},
        }
        if storage_class:
            claim_spec["storageClassName"] = storage_class
        pvcs.append(
            {
                "apiVersion": "v1",
                "kind": "PersistentVolumeClaim",
                "metadata": {"name": claim, "namespace": namespace},
                "spec": claim_spec,
            }
        )
        vol_name = f"vol{idx}"
        pod_volumes.append(
            {"name": vol_name, "persistentVolumeClaim": {"claimName": claim}}
        )
        mounts.append({"name": vol_name, "mountPath": target})
    return pvcs, pod_volumes, mounts


def to_service(placement: dict[str, Any], namespace: str) -> dict | None:
    """Emit a ClusterIP Service when the placement publishes ports."""
    ports = _parse_ports(placement.get("ports"))
    if not ports:
        return None
    name = placement["service"]
    return {
        "apiVersion": "v1",
        "kind": "Service",
        "metadata": {"name": name, "namespace": namespace},
        "spec": {
            "selector": {"app": name},
            "ports": [
                {"name": f"p{pub}", "port": pub, "targetPort": tgt}
                for pub, tgt in ports
            ],
        },
    }


def to_workload(
    placement: dict[str, Any],
    namespace: str,
    storage_class: str | None,
    node_label_key: str,
) -> tuple[dict, list[dict]]:
    """Build the workload manifest + any PVCs for one placement."""
    name = placement["service"]
    node = placement["node"]
    kind = select_kind(placement)
    image = placement.get("image", f"{name}:latest")
    replicas = int(placement.get("replicas", 1))
    volumes = placement.get("volumes") or []

    container: dict[str, Any] = {"name": name, "image": image}
    ports = _parse_ports(placement.get("ports"))
    if ports:
        container["ports"] = [{"containerPort": tgt} for _, tgt in ports]
    if placement.get("env"):
        container["env"] = [
            {"name": k, "value": str(v)}
            for k, _, v in (e.partition("=") for e in placement["env"])
        ]

    pvcs: list[dict] = []
    pod_volumes: list[dict] = []
    if kind == "StatefulSet" and volumes:
        # volumeClaimTemplates keep the PVC lifecycle bound to the StatefulSet
        vcts = []
        for idx, raw in enumerate(volumes):
            parts = str(raw).split(":")
            if len(parts) < 2:
                continue
            claim = f"data{idx}"
            claim_spec: dict[str, Any] = {
                "accessModes": ["ReadWriteOnce"],
                "resources": {"requests": {"storage": "10Gi"}},
            }
            if storage_class:
                claim_spec["storageClassName"] = storage_class
            vcts.append({"metadata": {"name": claim}, "spec": claim_spec})
            container.setdefault("volumeMounts", []).append(
                {"name": claim, "mountPath": parts[1]}
            )
    else:
        pvcs, pod_volumes, mounts = _pvcs_and_volumes(
            name, volumes, namespace, storage_class
        )
        if mounts:
            container["volumeMounts"] = mounts

    pod_spec: dict[str, Any] = {
        "containers": [container],
        "affinity": node_affinity(node, node_label_key),
    }
    if pod_volumes:
        pod_spec["volumes"] = pod_volumes

    template = {"metadata": {"labels": {"app": name}}, "spec": pod_spec}
    selector = {"matchLabels": {"app": name}}

    spec: dict[str, Any] = {"selector": selector, "template": template}
    if kind == "Deployment":
        spec["replicas"] = replicas
    elif kind == "StatefulSet":
        spec["replicas"] = replicas
        spec["serviceName"] = name
        if volumes:
            spec["volumeClaimTemplates"] = vcts

    workload = {
        "apiVersion": "apps/v1",
        "kind": kind,
        "metadata": {"name": name, "namespace": namespace, "labels": {"app": name}},
        "spec": spec,
    }
    return workload, pvcs


def emit(blueprint: dict[str, Any], target: str, namespace: str) -> list[dict]:
    """Render the blueprint for the requested orchestrator."""
    if target == "swarm":
        # Swarm uses the golden-deployment blueprint directly (SKILL Step 7).
        return [blueprint]

    k8s = blueprint.get("k8s") or {}
    storage_class = k8s.get("storageClass")
    namespace = k8s.get("namespace", namespace)
    node_label_key = k8s.get("nodeLabelKey", "kubernetes.io/hostname")

    manifests: list[dict] = [
        {
            "apiVersion": "v1",
            "kind": "Namespace",
            "metadata": {"name": namespace},
        }
    ]
    for placement in blueprint.get("placements", []):
        if not placement.get("service") or not placement.get("node"):
            continue
        workload, pvcs = to_workload(
            placement, namespace, storage_class, node_label_key
        )
        manifests.extend(pvcs)
        manifests.append(workload)
        svc = to_service(placement, namespace)
        if svc:
            manifests.append(svc)
    return manifests


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--blueprint", required=True, help="golden-deployment.yaml path"
    )
    parser.add_argument(
        "--target", choices=["swarm", "kubernetes"], default="kubernetes"
    )
    parser.add_argument("--namespace", default="default")
    parser.add_argument("--out", default=None, help="output dir (default: stdout)")
    args = parser.parse_args(argv)

    with open(args.blueprint) as fh:
        blueprint = yaml.safe_load(fh)

    manifests = emit(blueprint, args.target, args.namespace)

    if args.out:
        import os

        os.makedirs(args.out, exist_ok=True)
        for m in manifests:
            fname = f"{m['kind'].lower()}-{m['metadata']['name']}.yaml"
            with open(os.path.join(args.out, fname), "w") as fh:
                yaml.safe_dump(m, fh, sort_keys=False)
        print(f"Wrote {len(manifests)} manifests to {args.out}")
    else:
        print(yaml.safe_dump_all(manifests, sort_keys=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())

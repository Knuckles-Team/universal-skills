"""Source image inputs must come from the generated checkout, including runtime data."""
from __future__ import annotations

import configparser
import importlib.util
from pathlib import Path

import pytest

SCRIPT = Path(__file__).parents[1] / "universal_skills/agent-tools/mcp-builder/scripts/scaffold_package.py"


def builder():
    spec = importlib.util.spec_from_file_location("source_image_scaffold", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_generated_image_installs_the_published_wheel_never_source(tmp_path):
    module = builder()
    module.scaffold("unpublished-api", output_dir=str(tmp_path), pkg_types="api_client,mcp")
    root = tmp_path / "unpublished-api"
    docker = (root / "docker/Dockerfile").read_text()
    assert 'pip install --only-binary :all: "unpublished-api[mcp]==${VERSION}"' in docker
    assert '".[mcp]"' not in docker
    assert "COPY " not in docker
    assert "cargo" not in docker and "build-essential" not in docker
    assert "python:3.14-slim@sha256:" in docker
    assert "USER 10001" in docker
    assert "FROM mcp AS default" in docker
    assert "git clone" not in docker
    config = configparser.ConfigParser(interpolation=None)
    config.read(root / ".bumpversion.cfg")
    assert not any("docker/Dockerfile" in name for name in config.sections())


def test_image_docs_build_from_the_published_release(tmp_path):
    builder().scaffold("unpublished-api", output_dir=str(tmp_path), pkg_types="api_client,mcp")
    root = tmp_path / "unpublished-api"
    readme = (root / "README.md").read_text()
    assert "--build-arg VERSION=<version> -t unpublished-api:<version>-mcp ." in readme
    deployment = (root / "docs/deployment.md").read_text()
    assert "pip install --only-binary :all:" in deployment
    assert "never installs the" in deployment

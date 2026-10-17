"""Source image inputs must come from the generated checkout, including runtime data."""

from __future__ import annotations

import configparser
import importlib.util
from pathlib import Path


SCRIPT = (
    Path(__file__).parents[1]
    / "universal_skills/agent-tools/mcp-builder/scripts/scaffold_package.py"
)


def builder():
    spec = importlib.util.spec_from_file_location("source_image_scaffold", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_generated_image_installs_local_source_and_selected_extra(tmp_path):
    module = builder()
    module.scaffold(
        "unpublished-api", output_dir=str(tmp_path), pkg_types="api_client,mcp"
    )
    root = tmp_path / "unpublished-api"
    docker = (root / "docker/Dockerfile").read_text()
    assert "WORKDIR /src" in docker
    assert "COPY pyproject.toml README.md LICENSE ./" in docker
    assert "COPY unpublished_api/ ./unpublished_api/" in docker
    for relative in (
        "pyproject.toml",
        "README.md",
        "LICENSE",
        "unpublished_api/connector_manifest.yml",
    ):
        assert (root / relative).is_file()
    assert '"unpublished-api[mcp]' not in docker
    assert '"unpublished-api[agent]' not in docker
    assert '--prerelease=allow ".[mcp]"' in docker
    assert '--prerelease=allow ".[agent]"' not in docker
    assert "COPY --from=builder-mcp /usr/local /usr/local" in docker
    assert "FROM mcp AS default" in docker
    assert "COPY . " not in docker
    assert "git clone" not in docker
    config = configparser.ConfigParser(interpolation=None)
    config.read(root / ".bumpversion.cfg")
    assert not any("docker/Dockerfile" in name for name in config.sections())


def test_source_build_docs_use_repository_context_and_exact_commit(tmp_path):
    builder().scaffold(
        "unpublished-api", output_dir=str(tmp_path), pkg_types="api_client,mcp"
    )
    root = tmp_path / "unpublished-api"
    readme = (root / "README.md").read_text()
    assert (
        "docker build --file docker/Dockerfile --target mcp -t unpublished-api:mcp-local ."
        in readme
    )
    assert "docker build --file docker/Dockerfile --target agent" not in readme
    deployment = (root / "docs/deployment.md").read_text()
    assert "git rev-parse --verify 'HEAD^{commit}'" in deployment
    assert 'git archive --format=tar "$SOURCE_COMMIT"' in deployment
    assert "org.opencontainers.image.revision=$SOURCE_COMMIT" in deployment
    assert "does not freeze the index-resolved dependency closure" in deployment
    assert "runtime artifact contract" in deployment

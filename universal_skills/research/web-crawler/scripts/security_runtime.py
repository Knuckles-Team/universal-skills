"""Security boundary for the web-crawler skill.

All outbound destinations, TLS material, proxies, response limits, durable
content, and output locations are resolved through the shared agent-utilities
runtime.  This module intentionally contains no deployment-specific endpoint,
certificate path, or private-network exception.
"""

from __future__ import annotations

import json
import os
import re
import secrets
import threading
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any
from urllib.parse import urldefrag, urlparse

from agent_utilities.core.config import AgentConfig
from agent_utilities.core.http_client import create_http_client
from agent_utilities.core.paths import data_dir
from agent_utilities.core.transport_security import resolve_tls_profile
from agent_utilities.protocols.source_connectors.http_safety import (
    SourceEgressError,
    normalize_allowed_hosts,
    require_safe_source_url,
    safe_get_bytes,
)
from agent_utilities.security.persistence_privacy import (
    persistence_reference,
    sanitize_for_persistence,
)

MAX_URL_BYTES = 4_096
MAX_SEED_URLS = 50
MAX_SITEMAP_BYTES = 4 * 1024 * 1024
MAX_SITEMAP_DEPTH = 3
MAX_SITEMAP_URLS = 5_000
MAX_LINKS_PER_PAGE = 1_000
MAX_KG_RESPONSE_BYTES = 2 * 1024 * 1024
MAX_KG_REQUEST_BYTES = 12 * 1024 * 1024
MAX_SESSION_ID_BYTES = 256
MAX_TOKEN_BYTES = 16 * 1024
MAX_TIMEOUT_SECONDS = 120.0
MAX_TOTAL_OUTPUT_BYTES = 512 * 1024 * 1024
MAX_TOTAL_OUTPUT_FILES = 5_000

_SESSION_ID_RE = re.compile(r"^[A-Za-z0-9._~-]{1,256}$")
_BROWSER_HOST_RE = re.compile(r"^(?:[A-Za-z0-9](?:[A-Za-z0-9.-]{0,251}[A-Za-z0-9])?)$")


class CrawlerSecurityError(ValueError):
    """Stable, non-sensitive policy failure."""


@dataclass
class OutputBudget:
    """Thread-safe aggregate disk/stdout ceiling for one crawler invocation."""

    max_bytes: int = MAX_TOTAL_OUTPUT_BYTES
    max_files: int = MAX_TOTAL_OUTPUT_FILES
    bytes_used: int = 0
    files_used: int = 0
    _lock: threading.Lock = field(default_factory=threading.Lock, repr=False)

    def consume(self, size: int) -> None:
        with self._lock:
            if (
                size < 0
                or self.bytes_used + size > self.max_bytes
                or self.files_used + 1 > self.max_files
            ):
                raise CrawlerSecurityError("crawler_output_budget_exceeded")
            self.bytes_used += size
            self.files_used += 1


def _is_relative_to(path: Path, root: Path) -> bool:
    try:
        path.relative_to(root)
    except ValueError:
        return False
    return True


def _ensure_private_directory(path: Path, root: Path) -> Path:
    """Create a confined directory without traversing an in-scope symlink."""

    root_existed = root.exists()
    root.mkdir(mode=0o700, parents=True, exist_ok=True)
    if not root_existed:
        try:
            root.chmod(0o700)
        except OSError:
            pass
    if root.is_symlink():
        raise CrawlerSecurityError("crawler_output_root_symlink")

    current = root
    for part in path.relative_to(root).parts:
        current = current / part
        if current.exists() and current.is_symlink():
            raise CrawlerSecurityError("crawler_output_symlink")
        existed = current.exists()
        current.mkdir(mode=0o700, exist_ok=True)
        if not existed:
            try:
                current.chmod(0o700)
            except OSError:
                pass
    return path


@dataclass(frozen=True)
class CrawlerSecurityPolicy:
    """AgentConfig-backed policy shared by every crawler strategy."""

    allowed_private_hosts: frozenset[str]
    allowed_redirect_hosts: frozenset[str]
    max_response_bytes: int
    max_redirects: int
    allow_browser_fetch: bool
    workspace_root: Path | None
    output_root: Path
    output_budget: OutputBudget = field(
        default_factory=OutputBudget,
        compare=False,
        repr=False,
    )

    @classmethod
    def from_agent_config(
        cls, config: AgentConfig | None = None
    ) -> "CrawlerSecurityPolicy":
        cfg = config or AgentConfig()
        private_hosts = normalize_allowed_hosts(cfg.source_http_allowed_private_hosts)
        redirect_hosts = normalize_allowed_hosts(cfg.source_http_allowed_redirect_hosts)
        if len(private_hosts | redirect_hosts) > 256:
            raise CrawlerSecurityError("crawler_host_allowlist_too_large")
        workspace = None
        if cfg.workspace_path:
            workspace = Path(cfg.workspace_path).expanduser().resolve(strict=False)
            if not workspace.is_dir():
                raise CrawlerSecurityError("crawler_workspace_unavailable")
        return cls(
            allowed_private_hosts=private_hosts,
            allowed_redirect_hosts=redirect_hosts,
            max_response_bytes=int(cfg.source_http_max_response_bytes),
            max_redirects=int(cfg.source_http_max_redirects),
            allow_browser_fetch=bool(cfg.source_http_allow_browser_fetch),
            workspace_root=workspace,
            output_root=(data_dir() / "web-crawler").expanduser().resolve(strict=False),
        )

    def validate_url(self, value: str, *, resolve_dns: bool = True) -> str:
        """Validate and normalize one HTTP(S) URL without exposing it in errors."""

        rendered = str(value or "").strip()
        if (
            not rendered
            or len(rendered.encode("utf-8")) > MAX_URL_BYTES
            or any(ord(character) < 32 for character in rendered)
        ):
            raise CrawlerSecurityError("crawler_url_invalid")
        normalized = urldefrag(rendered)[0]
        try:
            require_safe_source_url(
                normalized,
                allowed_private_hosts=self.allowed_private_hosts,
                resolve_dns=resolve_dns,
            )
        except (SourceEgressError, ValueError):
            raise CrawlerSecurityError("crawler_url_denied") from None
        return normalized

    def host(self, url: str) -> str:
        return (urlparse(url).hostname or "").lower().rstrip(".")

    def origin(self, url: str) -> str:
        parsed = urlparse(url)
        default_port = 443 if parsed.scheme == "https" else 80
        return f"{parsed.scheme}://{self.host(url)}:{parsed.port or default_port}"

    def require_scoped_url(
        self,
        value: str,
        *,
        allowed_origins: set[str] | frozenset[str],
        resolve_dns: bool = True,
    ) -> str:
        """Validate a discovered URL and keep it on an approved origin/host."""

        # Scope before DNS so an attacker cannot turn a page full of rejected
        # cross-origin links into a resolver-amplification primitive.
        normalized = self.validate_url(value, resolve_dns=False)
        if (
            self.origin(normalized) not in allowed_origins
            and self.host(normalized) not in self.allowed_redirect_hosts
        ):
            raise CrawlerSecurityError("crawler_cross_origin_denied")
        return self.validate_url(normalized) if resolve_dns else normalized

    def fetch_bytes(self, url: str, *, max_bytes: int | None = None) -> bytes:
        """Fetch through the central redirect, DNS, TLS, CA, and proxy policy."""

        normalized = self.validate_url(url)
        body, _ = safe_get_bytes(
            normalized,
            timeout=30.0,
            max_bytes=min(
                max_bytes or self.max_response_bytes, self.max_response_bytes
            ),
            max_redirects=self.max_redirects,
            allowed_private_hosts=self.allowed_private_hosts,
            allowed_redirect_hosts=self.allowed_redirect_hosts,
        )
        return body

    def fetch_text(self, url: str, *, max_bytes: int | None = None) -> str:
        normalized = self.validate_url(url)
        body, encoding = safe_get_bytes(
            normalized,
            timeout=30.0,
            max_bytes=min(
                max_bytes or self.max_response_bytes, self.max_response_bytes
            ),
            max_redirects=self.max_redirects,
            allowed_private_hosts=self.allowed_private_hosts,
            allowed_redirect_hosts=self.allowed_redirect_hosts,
        )
        return body.decode(encoding or "utf-8", errors="replace")

    def sanitize_content(self, content: str) -> tuple[str, int]:
        rendered = str(content or "")
        if len(rendered.encode("utf-8")) > self.max_response_bytes:
            raise CrawlerSecurityError("crawler_content_too_large")
        clean, report = sanitize_for_persistence(rendered)
        return str(clean), report.redactions

    def reserve_output(self, content: str) -> str:
        clean, _ = self.sanitize_content(content)
        self.output_budget.consume(len(clean.encode("utf-8")))
        return clean

    def source_reference(self, url: str) -> str:
        return persistence_reference("crawl_source", self.validate_url(url))

    def browser_arguments(self, seed_urls: list[str]) -> list[str]:
        """Return fail-closed Chromium egress args for a system-trust profile.

        Crawl4AI cannot faithfully apply arbitrary CA bundles, mTLS material, or
        the shared authenticated proxy profile to Chromium. Browser mode rejects
        those configurations instead of silently using a different trust path.
        The bounded HTTP path supports all of them.
        """

        tls = resolve_tls_profile("source-http")
        try:
            if (
                not tls.verify_enabled
                or not tls.system_trust
                or tls.ca_bundle_path is not None
                or tls.ca_directory is not None
                or tls.client_cert_path is not None
                or tls.client_key_path is not None
                or tls.proxy_url is not None
            ):
                raise CrawlerSecurityError("crawler_browser_transport_unsupported")
        finally:
            tls.cleanup()

        hosts = {
            self.host(self.validate_url(url, resolve_dns=False)) for url in seed_urls
        }
        hosts.update(self.allowed_private_hosts)
        hosts.update(self.allowed_redirect_hosts)
        if (
            not hosts
            or len(hosts) > 256
            or any(not _BROWSER_HOST_RE.fullmatch(host) for host in hosts)
        ):
            raise CrawlerSecurityError("crawler_browser_host_scope_invalid")
        resolver_rules = "MAP * ~NOTFOUND, " + ", ".join(
            f"EXCLUDE {host}" for host in sorted(hosts)
        )
        return [
            "--disable-background-networking",
            "--disable-component-update",
            "--disable-default-apps",
            "--disable-extensions",
            "--disable-gpu",
            "--disable-sync",
            "--disable-dev-shm-usage",
            "--no-first-run",
            f"--host-resolver-rules={resolver_rules}",
        ]

    def resolve_output_dir(self, requested: str | None) -> Path | None:
        if not requested:
            return None
        raw = Path(str(requested)).expanduser()
        base = self.workspace_root or self.output_root
        candidate = raw if raw.is_absolute() else base / raw
        candidate = candidate.resolve(strict=False)
        allowed_roots = [self.output_root]
        if self.workspace_root is not None:
            allowed_roots.append(self.workspace_root)
        root = next(
            (
                allowed
                for allowed in allowed_roots
                if _is_relative_to(candidate, allowed)
            ),
            None,
        )
        if root is None:
            raise CrawlerSecurityError("crawler_output_outside_allowed_roots")
        return _ensure_private_directory(candidate, root)

    def require_output_dir(self, output_dir: Path) -> Path:
        """Revalidate a previously resolved sink immediately before every write."""

        candidate = Path(output_dir).expanduser().resolve(strict=False)
        roots = [self.output_root]
        if self.workspace_root is not None:
            roots.append(self.workspace_root)
        root = next(
            (allowed for allowed in roots if _is_relative_to(candidate, allowed)),
            None,
        )
        if root is None:
            raise CrawlerSecurityError("crawler_output_outside_allowed_roots")
        return _ensure_private_directory(candidate, root)

    def write_markdown(
        self,
        output_dir: Path,
        content: str,
        source_url: str,
        *,
        suffix: str = "",
    ) -> bool:
        """Atomically persist private markdown under a content-neutral filename."""

        output_dir = self.require_output_dir(output_dir)
        clean = self.reserve_output(content)
        source_ref = self.source_reference(source_url).rsplit("_", 1)[-1][:20]
        safe_suffix = re.sub(r"[^a-z0-9-]+", "-", suffix.casefold()).strip("-")[:32]
        filename = f"page-{source_ref}{('-' + safe_suffix) if safe_suffix else ''}.md"
        target = output_dir / filename
        if target.exists() and target.is_symlink():
            raise CrawlerSecurityError("crawler_output_symlink")
        temporary = output_dir / f".crawler-{secrets.token_hex(12)}.tmp"
        flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL
        if hasattr(os, "O_NOFOLLOW"):
            flags |= os.O_NOFOLLOW
        descriptor = None
        try:
            descriptor = os.open(temporary, flags, 0o600)
            payload = clean.encode("utf-8")
            with os.fdopen(descriptor, "wb", closefd=True) as handle:
                descriptor = None
                handle.write(payload)
                handle.flush()
                os.fsync(handle.fileno())
            if target.exists() and target.is_symlink():
                raise CrawlerSecurityError("crawler_output_symlink")
            os.replace(temporary, target)
            try:
                target.chmod(0o600)
            except OSError:
                pass
            return True
        except CrawlerSecurityError:
            raise
        except OSError:
            return False
        finally:
            if descriptor is not None:
                os.close(descriptor)
            try:
                temporary.unlink(missing_ok=True)
            except OSError:
                pass


class SafeMCPClient:
    """Bounded MCP streamable-HTTP client using the shared graph-os TLS profile."""

    def __init__(
        self,
        endpoint: str,
        *,
        policy: CrawlerSecurityPolicy,
        token: str = "",
        timeout: float = 60.0,
    ) -> None:
        base = policy.validate_url(endpoint, resolve_dns=False).rstrip("/")
        parsed = urlparse(base)
        if parsed.query or parsed.fragment:
            raise CrawlerSecurityError("crawler_kg_endpoint_invalid")
        self.url = base if parsed.path.rstrip("/").endswith("/mcp") else base + "/mcp"
        self.policy = policy
        self.timeout = float(timeout)
        if not 0 < self.timeout <= MAX_TIMEOUT_SECONDS:
            raise CrawlerSecurityError("crawler_kg_timeout_invalid")
        self.token = str(token or "").strip()
        if (
            len(self.token.encode("utf-8")) > MAX_TOKEN_BYTES
            or "\r" in self.token
            or "\n" in self.token
        ):
            raise CrawlerSecurityError("crawler_kg_token_invalid")
        self.session_id: str | None = None

    def post(
        self, payload: dict[str, Any], *, notify: bool = False
    ) -> dict[str, Any] | None:
        self.policy.validate_url(self.url)
        body = json.dumps(payload, separators=(",", ":")).encode("utf-8")
        if len(body) > MAX_KG_REQUEST_BYTES:
            raise CrawlerSecurityError("crawler_kg_request_too_large")
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json, text/event-stream",
        }
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        if self.session_id:
            headers["mcp-session-id"] = self.session_id

        tls = resolve_tls_profile("graph-os")
        client_kwargs: dict[str, Any] = {
            "timeout": self.timeout,
            "follow_redirects": False,
            "headers": headers,
        }
        client_kwargs.update(tls.httpx_kwargs())
        try:
            with create_http_client(**client_kwargs) as client:
                with client.stream("POST", self.url, content=body) as response:
                    if response.status_code in {301, 302, 303, 307, 308}:
                        raise CrawlerSecurityError("crawler_kg_redirect_denied")
                    response.raise_for_status()
                    session_id = response.headers.get("mcp-session-id", "")
                    if session_id:
                        if len(
                            session_id.encode("utf-8")
                        ) > MAX_SESSION_ID_BYTES or not _SESSION_ID_RE.fullmatch(
                            session_id
                        ):
                            raise CrawlerSecurityError("crawler_kg_session_invalid")
                        self.session_id = session_id
                    raw = bytearray()
                    for chunk in response.iter_bytes():
                        raw.extend(chunk)
                        if len(raw) > MAX_KG_RESPONSE_BYTES:
                            raise CrawlerSecurityError("crawler_kg_response_too_large")
        finally:
            tls.cleanup()

        if notify or not raw:
            return None
        try:
            text = bytes(raw).decode("utf-8")
            data: Any = None
            for line in text.splitlines():
                if line.startswith("data:"):
                    data = json.loads(line[5:].strip())
            if data is None:
                data = json.loads(text)
        except (UnicodeError, ValueError):
            raise CrawlerSecurityError("crawler_kg_response_invalid") from None
        if not isinstance(data, dict):
            raise CrawlerSecurityError("crawler_kg_response_invalid")
        return data

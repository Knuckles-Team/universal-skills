"""Catalog-bound registrars preserving the SDK's per-domain toggles."""

from functools import partial

from ..auth import get_client
from ..openapi_runtime import CONTRACT, register_domain


def _domain_registrar(domain):
    registrar = partial(register_domain, domain=domain, client_factory=get_client)
    registrar.__name__ = f"register_{domain}_tools"
    return registrar


globals().update(
    {
        f"register_{domain}_tools": _domain_registrar(domain)
        for domain in sorted(CONTRACT["domains"])
    }
)

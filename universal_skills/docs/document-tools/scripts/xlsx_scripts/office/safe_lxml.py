"""Secure lxml defaults for Office validators."""

from __future__ import annotations


def secure_lxml_defaults(etree) -> None:
    """Disable DTD loading, entity expansion, recovery, and network access."""

    parser = etree.XMLParser(
        resolve_entities=False,
        load_dtd=False,
        no_network=True,
        recover=False,
        huge_tree=False,
        remove_comments=False,
        remove_pis=False,
    )
    etree.set_default_parser(parser)

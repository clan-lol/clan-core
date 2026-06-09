"""Helpers for pointing template flakes at a local clan-core for offline tests.

This module is intentionally plugin-free (no pytest fixtures) so it can be
imported from modules that are loaded during collection (e.g. test helper
modules) without tripping pytest's "module already imported" assertion-rewrite
warning that registered plugins are subject to.
"""

import re
from pathlib import Path

# Templates ship with their clan-core input pinned to a release archive URL,
# https://git.clan.lol/clan/clan-core/archive/<ref>.tar.gz, where <ref> comes
# from the VERSION file ("main" on unstable, a tag like "26.05" on a release).
# Tests rewrite it to a local path so flakes evaluate offline. Match the ref
# generically so this keeps working across version bumps.
_CLAN_CORE_ARCHIVE_URL_RE = re.compile(
    r"https://git\.clan\.lol/clan/clan-core/archive/[^\"']+\.tar\.gz"
)


def replace_clan_core_url(content: str, clan_core_path: Path) -> str:
    """Point a template's clan-core archive input at a local path for offline eval."""
    return _CLAN_CORE_ARCHIVE_URL_RE.sub(f"path://{clan_core_path}", content)

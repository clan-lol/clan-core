import logging
import os
import re
from pathlib import Path
from typing import TypedDict

from clan_lib.api import API
from clan_lib.cmd import Log, RunOpts, run
from clan_lib.dirs import nixpkgs_source
from clan_lib.errors import ClanError
from clan_lib.nix import nix_build

log = logging.getLogger(__name__)


class FlashOptions(TypedDict):
    languages: list[str]
    keymaps: list[str]


@API.register
def get_machine_flash_options() -> FlashOptions:
    """Retrieve available languages and keymaps for flash configuration.

    Returns:
        FlashOptions: A dictionary containing lists of available languages and keymaps.

    Raises:
        ClanError: If the locale file or keymaps directory does not exist.

    """
    return {"languages": list_languages(), "keymaps": list_keymaps()}


def list_languages() -> list[str]:
    cmd = nix_build([f"{nixpkgs_source()}#glibcLocales"])
    result = run(cmd, RunOpts(log=Log.STDERR, error_msg="Failed to find glibc locales"))
    locale_file = Path(result.stdout.strip()) / "share" / "i18n" / "SUPPORTED"

    if not locale_file.exists():
        msg = f"Locale file '{locale_file}' does not exist."
        raise ClanError(msg)

    with locale_file.open() as f:
        lines = f.readlines()

    langs: set[str] = set()
    base = r"[A-Za-z0-9]*_[A-Za-z0-9]*.UTF-8"
    pattern = re.compile(base)
    for line in lines:
        s = line.strip()

        if not s:
            continue
        if s.startswith("#"):
            continue
        if "SUPPORTED-LOCALES" in s:
            continue

        tok = s.removesuffix("\\").strip()
        tok = tok.split("/")[0]

        if pattern.match(tok):
            langs.add(tok)

    return sorted(langs)


def list_keymaps() -> list[str]:
    cmd = nix_build([f"{nixpkgs_source()}#kbd.out"])
    result = run(cmd, RunOpts(log=Log.STDERR, error_msg="Failed to find kbdinfo"))
    keymaps_dir = Path(result.stdout.strip()) / "share" / "keymaps"

    if not keymaps_dir.exists():
        msg = f"Keymaps directory '{keymaps_dir}' does not exist."
        raise ClanError(msg)

    keymap_files = []

    for _root, _, files in os.walk(keymaps_dir):
        for file in files:
            if file.endswith(".map.gz"):
                # Remove '.map.gz' ending
                name_without_ext = file[:-7]
                keymap_files.append(name_without_ext)

    return sorted(keymap_files)
